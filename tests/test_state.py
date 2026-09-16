"""Pins qscreen_state (dedup key + sqlite-backed BatchState)."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from qscreen_state import (
    BatchState,
    STATUS_DONE,
    STATUS_ERROR,
    STATUS_IN_FLIGHT,
    STATUS_PENDING,
    STATUS_UPLOADED,
    dedup_key,
)


@pytest.fixture
def state(tmp_path: Path) -> BatchState:
    s = BatchState(tmp_path / "state.db")
    yield s
    s.close()


# ── dedup_key ────────────────────────────────────────────────────────────────


def test_dedup_key_is_stable_and_order_sensitive():
    a = dedup_key("QNBK", 2023, "FY", "sha256:aaa")
    b = dedup_key("QNBK", 2023, "FY", "sha256:aaa")
    assert a == b
    # Case-insensitive on ticker
    assert a == dedup_key("qnbk", 2023, "FY", "sha256:aaa")
    # Order matters
    assert a != dedup_key("QNBK", 2023, "FY", "sha256:bbb")
    assert a != dedup_key("QIBK", 2023, "FY", "sha256:aaa")
    assert a != dedup_key("QNBK", 2024, "FY", "sha256:aaa")
    assert a != dedup_key("QNBK", 2023, "Q1", "sha256:aaa")


def test_dedup_key_handles_missing_values():
    # Should not throw on None / empty values; produce a stable hex digest.
    a = dedup_key("", None, None, "")
    b = dedup_key("", None, None, "")
    assert a == b
    assert len(a) == 64                              # sha256 hex


# ── manifest lifecycle ───────────────────────────────────────────────────────


def test_start_manifest_inserts_and_resumes(state):
    state.start_manifest("m1", row_count=10)
    state.start_manifest("m1", row_count=12)         # idempotent
    s = state.manifest_summary("m1")
    assert s["row_count"] == 12                      # latest write wins
    assert s["finished_at"] is None


def test_start_then_finish_records_stats(state):
    state.start_manifest("m1", row_count=3)
    state.finish_manifest("m1", completed=2, errored=1)
    s = state.manifest_summary("m1")
    assert s["finished_at"] is not None
    assert s["completed"] == 2 and s["errored"] == 1


# ── row lifecycle ────────────────────────────────────────────────────────────


def test_ensure_row_is_idempotent(state):
    state.ensure_row("m1", 1, "dedup-a")
    state.ensure_row("m1", 1, "dedup-a")             # same row again
    state.ensure_row("m1", 1, "dedup-b")             # same row, different key — original kept
    rows = list(state.iter_rows("m1"))
    assert len(rows) == 1
    assert rows[0].dedup_key == "dedup-a"


def test_claim_row_transitions_pending_to_in_flight(state):
    state.ensure_row("m1", 1, "k")
    assert state.claim_row("m1", 1) is True
    assert state.get_row("m1", 1).status == STATUS_IN_FLIGHT


def test_claim_row_is_atomic(state):
    state.ensure_row("m1", 1, "k")
    state.claim_row("m1", 1)                          # worker A
    assert state.claim_row("m1", 1) is False         # worker B can't claim
    assert state.get_row("m1", 1).status == STATUS_IN_FLIGHT


def test_claim_row_can_reclaim_after_error(state):
    state.ensure_row("m1", 1, "k")
    state.claim_row("m1", 1)
    state.mark_error("m1", 1, error="boom")
    assert state.get_row("m1", 1).status == STATUS_ERROR
    assert state.claim_row("m1", 1) is True          # retry path


def test_mark_done_then_uploaded_progresses_statuses(state):
    state.ensure_row("m1", 1, "k")
    state.claim_row("m1", 1)
    state.mark_done("m1", 1, filing_id="QNBK_2023_FY_filing")
    assert state.get_row("m1", 1).status == STATUS_DONE
    state.mark_uploaded("m1", 1, filing_id="QNBK_2023_FY_filing")
    assert state.get_row("m1", 1).status == STATUS_UPLOADED
    assert state.get_row("m1", 1).uploaded_at is not None


def test_reset_in_flight_reclaims_crashed_rows(state):
    state.ensure_row("m1", 1, "k")
    state.claim_row("m1", 1)                          # worker A: claims then crashes
    n = state.reset_in_flight("m1")
    assert n == 1
    assert state.get_row("m1", 1).status == STATUS_PENDING


# ── pending_indices (the resume path) ──────────────────────────────────────


def test_pending_indices_returns_pending_and_error_only(state):
    state.ensure_row("m1", 1, "a")
    state.ensure_row("m1", 2, "b")
    state.ensure_row("m1", 3, "c")
    state.ensure_row("m1", 4, "d")
    state.claim_row("m1", 1)
    state.mark_done("m1", 1, filing_id="x")
    state.mark_uploaded("m1", 2, filing_id="y")
    state.claim_row("m1", 3)
    state.mark_error("m1", 3, error="boom")
    pending = state.pending_indices("m1")
    assert pending == [3, 4]


def test_pending_indices_ordered_by_row_index(state):
    state.ensure_row("m1", 1, "a")
    state.ensure_row("m1", 3, "c")
    state.ensure_row("m1", 2, "b")
    state.claim_row("m1", 1)
    state.mark_done("m1", 1, filing_id="x")
    assert state.pending_indices("m1") == [2, 3]


# ── cross-process concurrency safety ────────────────────────────────────────


def test_two_workers_cannot_claim_same_row(state):
    """Simulate two workers picking the same row by serial claims."""
    state.ensure_row("m1", 1, "k")
    a = state.claim_row("m1", 1)
    b = state.claim_row("m1", 1)
    assert a is True and b is False
    assert state.get_row("m1", 1).status == STATUS_IN_FLIGHT


# ── alternate state-db path via env ─────────────────────────────────────────


def test_state_db_overridable_via_constructor(tmp_path, monkeypatch):
    """The path is taken from the constructor, not the env (we don't want
    ambient state in tests)."""
    p = tmp_path / "x.db"
    s = BatchState(p)
    s.start_manifest("m", row_count=1)
    s.close()
    assert p.exists()
