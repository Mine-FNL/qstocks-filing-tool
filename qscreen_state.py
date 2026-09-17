"""Resumable batch state — what we've already done, on disk.

Why this exists
---------------
Without it, every ``--manifest`` rerun hits every row. At 1000 filings
that means re-paying the LLM cost and rebuilding the same JSONs. Worse,
the live cron ``llm-ingest-monitor`` had to invent its own bookkeeping
to survive re-runs.

This module is the canonical on-disk state. ``BatchState`` is a small
SQLite cache — keyed by a content-addressed ``dedup_key`` — that records
which rows have been processed, what the resulting filing_id was, and
whether the upload succeeded.

Schema
------
    state.db
      manifests(manifest_id PK, started_at, finished_at, row_count,
                  completed_count, error_count)
      rows(manifest_id, row_index, dedup_key UNIQUE,
              status, filing_id, last_error, attempted_at, uploaded_at)

A row's ``status`` is one of:
    pending    -> not yet attempted
    in_flight  -> currently processing (set by the worker before extract)
    done       -> filing saved locally
    uploaded   -> done + successfully uploaded to the ingest endpoint
    error      -> saved with an error sidecar OR the extract raised

Dedup key
---------
    dedup_key = SHA256((symbol|fiscal_year|fiscal_period|content_sha256)
                       .upper().encode("utf-8")).hexdigest()
The server gets the same key as an ``If-None-Match`` request header so it
can short-circuit duplicates without charging us (see upload_filing).
"""

from __future__ import annotations

import contextlib
import hashlib
import sqlite3
import time
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

# Status values — fixed strings (avoids enum churn; readable from sqlite-shell).
STATUS_PENDING = "pending"
STATUS_IN_FLIGHT = "in_flight"
STATUS_DONE = "done"
STATUS_UPLOADED = "uploaded"
STATUS_ERROR = "error"


def _default_state_path() -> Path:
    """``~/.qstocks-filing-tool/state.db`` unless ``QSCREEN_STATE_DB`` overrides.

    Falls back to ``./.qscreen-state.db`` in the cwd if home is unset.
    """
    import os

    custom = os.getenv("QSCREEN_STATE_DB")
    if custom:
        return Path(custom)
    home = Path(os.path.expanduser("~"))
    if (home / ".qstocks-filing-tool").exists() or (home.parent and home.parent.exists()):
        target = home / ".qstocks-filing-tool" / "state.db"
        target.parent.mkdir(parents=True, exist_ok=True)
        return target
    return Path(".qscreen-state.db").resolve()


def dedup_key(
    symbol: str, fiscal_year: int | None, fiscal_period: str | None, content_sha256: str
) -> str:
    """Stable per-filing key. Order matters (drives the dedup contract)."""
    payload = f"{(symbol or '').upper()}|{fiscal_year or ''}|{fiscal_period or ''}|{content_sha256}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class RowState:
    row_index: int
    dedup_key: str
    status: str
    filing_id: str | None
    last_error: str | None
    attempted_at: float | None
    uploaded_at: float | None


class BatchState:
    """SQLite-backed state for a single batch run.

    One process owns one instance at a time. The connection is opened in
    ``check_same_thread=False`` so multiprocessing workers can use it
    safely when each gets its own connection (we open a fresh one per
    worker — the file is locked at the OS level for journaling).
    """

    def __init__(self, db_path: Path | str | None = None):
        self.path = Path(db_path) if db_path else _default_state_path()
        # Default isolation_level (deferred) + Python's smart transaction
        # handling — single-statement writes auto-commit, multi-statement
        # writes use the ``_tx()`` helper below which manages its own
        # BEGIN/COMMIT via ``executescript``.
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self) -> None:
        with self._tx() as c:
            c.executescript(
                """
                CREATE TABLE IF NOT EXISTS manifests (
                    manifest_id    TEXT PRIMARY KEY,
                    started_at     REAL NOT NULL,
                    finished_at    REAL,
                    row_count      INTEGER,
                    completed_count INTEGER DEFAULT 0,
                    error_count    INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS rows (
                    manifest_id   TEXT NOT NULL,
                    row_index     INTEGER NOT NULL,
                    dedup_key     TEXT NOT NULL,
                    status        TEXT NOT NULL,
                    filing_id     TEXT,
                    last_error    TEXT,
                    attempted_at  REAL,
                    uploaded_at   REAL,
                    PRIMARY KEY (manifest_id, row_index),
                    UNIQUE (manifest_id, dedup_key)
                );
                CREATE INDEX IF NOT EXISTS rows_by_status
                    ON rows(manifest_id, status);
                """
            )

    @contextlib.contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        """Atomic multi-statement transaction.

        Uses ``cursor.execute("BEGIN")`` so the txn is held across the
        context body. ``executescript`` is unsuitable here because Python's
        sqlite3 wrapper commits any pending txn before running the script,
        which would race with our own BEGIN/COMMIT.
        """
        cur = self._conn.cursor()
        cur.execute("BEGIN IMMEDIATE")
        try:
            yield cur
            self._conn.commit()
        except Exception:
            with contextlib.suppress(sqlite3.OperationalError):
                self._conn.rollback()
            raise
        finally:
            cur.close()

    def close(self) -> None:
        with contextlib.suppress(Exception):
            self._conn.close()

    # ── manifest lifecycle ────────────────────────────────────────────────────

    def start_manifest(self, manifest_id: str, row_count: int) -> None:
        with self._tx() as c:
            c.execute(
                "INSERT OR REPLACE INTO manifests "
                "(manifest_id, started_at, row_count, completed_count, error_count) "
                "VALUES (?, ?, ?, 0, 0)",
                (manifest_id, time.time(), row_count),
            )

    def finish_manifest(self, manifest_id: str, *, completed: int, errored: int) -> None:
        with self._tx() as c:
            c.execute(
                "UPDATE manifests SET finished_at = ?, completed_count = ?, error_count = ? "
                "WHERE manifest_id = ?",
                (time.time(), completed, errored, manifest_id),
            )

    def manifest_summary(self, manifest_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT manifest_id, started_at, finished_at, row_count, "
            "completed_count, error_count FROM manifests WHERE manifest_id = ?",
            (manifest_id,),
        ).fetchone()
        if not row:
            return None
        return {
            "manifest_id": row[0],
            "started_at": row[1],
            "finished_at": row[2],
            "row_count": row[3],
            "completed": row[4],
            "errored": row[5],
        }

    # ── row lifecycle ─────────────────────────────────────────────────────────

    def ensure_row(self, manifest_id: str, row_index: int, dedup_key_: str) -> RowState:
        """Insert a row in pending state if absent; return its current state.

        The unique-by-(manifest_id, dedup_key) constraint guards against a
        manifest CSV that lists the same filing twice — the second row
        becomes a no-op alias.
        """
        with self._tx() as c:
            row = c.execute(
                "SELECT row_index, dedup_key, status, filing_id, last_error, "
                "attempted_at, uploaded_at FROM rows WHERE manifest_id = ? AND row_index = ?",
                (manifest_id, row_index),
            ).fetchone()
            if row:
                return self._row(*row)
            c.execute(
                "INSERT INTO rows (manifest_id, row_index, dedup_key, status, "
                "filing_id, last_error, attempted_at, uploaded_at) "
                "VALUES (?, ?, ?, 'pending', NULL, NULL, NULL, NULL)",
                (manifest_id, row_index, dedup_key_),
            )
        return self.get_row(manifest_id, row_index)

    def claim_row(self, manifest_id: str, row_index: int) -> bool:
        """Atomically transition pending → in_flight.

        Used by the worker before it touches the file. Returns True iff
        this worker now owns the row; False if someone else got there.
        """
        with self._tx() as c:
            cur = c.execute(
                "UPDATE rows SET status = 'in_flight', attempted_at = ? "
                "WHERE manifest_id = ? AND row_index = ? AND status IN ('pending', 'error')",
                (time.time(), manifest_id, row_index),
            )
            return cur.rowcount > 0

    def mark_done(self, manifest_id: str, row_index: int, filing_id: str) -> None:
        with self._tx() as c:
            c.execute(
                "UPDATE rows SET status = 'done', filing_id = ?, last_error = NULL "
                "WHERE manifest_id = ? AND row_index = ?",
                (filing_id, manifest_id, row_index),
            )

    def mark_uploaded(self, manifest_id: str, row_index: int, filing_id: str) -> None:
        with self._tx() as c:
            c.execute(
                "UPDATE rows SET status = 'uploaded', uploaded_at = ?, filing_id = ?, "
                "last_error = NULL WHERE manifest_id = ? AND row_index = ?",
                (time.time(), filing_id, manifest_id, row_index),
            )

    def mark_error(self, manifest_id: str, row_index: int, error: str) -> None:
        with self._tx() as c:
            c.execute(
                "UPDATE rows SET status = 'error', last_error = ?, attempted_at = ? "
                "WHERE manifest_id = ? AND row_index = ?",
                (error[:500], time.time(), manifest_id, row_index),
            )

    def reset_in_flight(self, manifest_id: str) -> int:
        """Re-claim rows stuck in ``in_flight`` (a previous run crashed).

        Called at manifest start so a power-failure mid-batch doesn't leak
        "in_flight" rows forever. Returns the count reset.
        """
        with self._tx() as c:
            cur = c.execute(
                "UPDATE rows SET status = 'pending' WHERE manifest_id = ? AND status = 'in_flight'",
                (manifest_id,),
            )
            return cur.rowcount

    # ── read ──────────────────────────────────────────────────────────────────

    def get_row(self, manifest_id: str, row_index: int) -> RowState | None:
        row = self._conn.execute(
            "SELECT row_index, dedup_key, status, filing_id, last_error, "
            "attempted_at, uploaded_at FROM rows WHERE manifest_id = ? AND row_index = ?",
            (manifest_id, row_index),
        ).fetchone()
        if not row:
            return None
        return self._row(*row)

    def _row(self, ri, dk, st, fid, err, att, upl) -> RowState:
        return RowState(
            row_index=ri,
            dedup_key=dk,
            status=st,
            filing_id=fid,
            last_error=err,
            attempted_at=att,
            uploaded_at=upl,
        )

    def pending_indices(self, manifest_id: str) -> list[int]:
        """Row indices that are still ``pending`` or in ``error`` — the
        work remaining for a resume run.

        Ordered by ``row_index`` so the resumable run produces the same
        output order as the original run.
        """
        rows = self._conn.execute(
            "SELECT row_index FROM rows "
            "WHERE manifest_id = ? AND status IN ('pending', 'error') "
            "ORDER BY row_index",
            (manifest_id,),
        ).fetchall()
        return [r[0] for r in rows]

    def iter_rows(self, manifest_id: str) -> Iterable[RowState]:
        for r in self._conn.execute(
            "SELECT row_index, dedup_key, status, filing_id, last_error, "
            "attempted_at, uploaded_at FROM rows WHERE manifest_id = ? ORDER BY row_index",
            (manifest_id,),
        ):
            yield self._row(*r)


__all__ = [
    "STATUS_DONE",
    "STATUS_ERROR",
    "STATUS_IN_FLIGHT",
    "STATUS_PENDING",
    "STATUS_UPLOADED",
    "BatchState",
    "RowState",
    "dedup_key",
]
