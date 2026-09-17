"""qscreen_perf.py — per-stage performance tracking for the engine.

Pure stdlib (no ``prometheus_client`` / ``python-json-logger`` — those live in
``[dev]`` extras only). Holds:

* ``StageTimer`` — context manager that records (stage, duration_ms, metadata).
* ``PerfRecord`` — dataclass holding per-stage timings for one filing.
* ``aggregate(records)`` — returns ``{stage_name: {count, p50, p95, p99, max_ms}}``.
* ``emit_metrics(records)`` — Prometheus text-format output for one batch's records.
* ``check_regression(baseline, current, threshold)`` — flags p95 jumps ≥ threshold.

Used by ``qscreen_ingest.py`` (via the module-level ``log``), by the bench
(``qscreen_eval.py --timing``) and by the ``/metrics`` endpoint
(``qscreen_app.py``).
"""

from __future__ import annotations

import os
import time
from contextlib import AbstractContextManager, suppress
from dataclasses import dataclass, field
from typing import Any

# ── per-stage timing record ───────────────────────────────────────────────────


@dataclass
class StageSample:
    """One observation: a (stage_name, duration_ms, metadata) triple.

    ``metadata`` carries optional labels (mode, case, …) that can be attached
    later to Prometheus counters / gauges.
    """

    stage: str
    duration_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerfRecord:
    """All the stage samples recorded for one filing / run."""

    samples: list[StageSample] = field(default_factory=list)

    def add(self, stage: str, duration_ms: float, **meta: Any) -> None:
        self.samples.append(
            StageSample(stage=stage, duration_ms=float(duration_ms), metadata=dict(meta))
        )

    def durations(self, stage: str) -> list[float]:
        return [s.duration_ms for s in self.samples if s.stage == stage]

    def stage_names(self) -> list[str]:
        # Preserve insertion order; dedup keeps it stable.
        seen: set[str] = set()
        out: list[str] = []
        for s in self.samples:
            if s.stage not in seen:
                seen.add(s.stage)
                out.append(s.stage)
        return out


# ── StageTimer ────────────────────────────────────────────────────────────────


class _NoopTimer(AbstractContextManager):
    """Returned by ``stage_timer`` when timing is disabled — zero overhead."""

    def __enter__(self) -> _NoopTimer:
        return self

    def __exit__(self, *exc: Any) -> None:
        return None


class StageTimer(AbstractContextManager):
    """Context manager that records (stage, duration_ms, metadata) on a
    ``PerfRecord`` and logs entry/exit through the supplied logger.

    Usage:

        with StageTimer(logger, record, "extract", mode="basic") as t:
            ... do work ...
            t.meta["rows"] = 42    # optional extra metadata

    If ``record`` is None the timer becomes a no-op (zero overhead in
    benchmarks when the operator didn't pass ``--timing``).

    Logging contract:
      * INFO  on entry:  ``stage=<name> start``   (so the operator can grep)
      * DEBUG on exit:   ``stage=<name> duration_ms=<x> ...``
    """

    def __init__(
        self,
        logger: Any,
        record: PerfRecord | None,
        stage: str,
        log_on_entry: bool = True,
        **metadata: Any,
    ) -> None:
        self._logger = logger
        self._record = record
        self._stage = stage
        self._log_on_entry = log_on_entry
        self.metadata: dict[str, Any] = dict(metadata)
        self.duration_ms: float = 0.0
        self._t0: float = 0.0

    def __enter__(self) -> StageTimer:
        if self._record is None:
            return self
        self._t0 = time.perf_counter()
        if self._log_on_entry and self._logger is not None:
            with suppress(Exception):
                self._logger.info("stage=%s start", self._stage)
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self._record is None:
            return False
        self.duration_ms = (time.perf_counter() - self._t0) * 1000.0
        if self._logger is not None:
            with suppress(Exception):
                self._logger.debug(
                    "stage=%s duration_ms=%.3f metadata=%s%s",
                    self._stage,
                    self.duration_ms,
                    self.metadata,
                    " error" if exc_type else "",
                )
        # Carry forward useful metadata fields (mode, case, ...). Merging here
        # keeps the call site free of plumbing.
        merged = dict(self.metadata)
        if exc_type is not None:
            merged["error"] = exc_type.__name__
        self._record.add(self._stage, self.duration_ms, **merged)
        return False


def stage_timer(
    logger: Any, record: PerfRecord | None, stage: str, **metadata: Any
) -> AbstractContextManager:
    """Convenience factory. Returns a real ``StageTimer`` when ``record`` is
    truthy, otherwise a zero-overhead no-op context manager.

    Same call signature at the site regardless of whether timing is on, so
    the engine can be wired without an ``if`` at every stage.
    """
    if record is None:
        return _NoopTimer()
    return StageTimer(logger, record, stage, **metadata)


# ── aggregation (count / percentiles) ─────────────────────────────────────────


def _percentile(values: list[float], p: float) -> float:
    """Linear-interpolation percentile (same definition as numpy default).
    Returns 0.0 for an empty list."""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return float(s[0])
    # clamp p to [0, 100]
    if p < 0:
        p = 0.0
    if p > 100:
        p = 100.0
    k = (len(s) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return float(s[f])
    return float(s[f] + (s[c] - s[f]) * (k - f))


def aggregate(records: list[PerfRecord]) -> dict[str, dict[str, float]]:
    """Collapse a batch of ``PerfRecord`` into per-stage summary stats.

    Returns ``{stage_name: {count, p50_ms, p95_ms, p99_ms, max_ms, mean_ms}}``.
    ``p95_ms`` is what the regression check below compares against the baseline.
    """
    out: dict[str, dict[str, float]] = {}
    if not records:
        return out
    # Per-stage accumulation
    buckets: dict[str, list[float]] = {}
    for rec in records:
        for sample in rec.samples:
            buckets.setdefault(sample.stage, []).append(sample.duration_ms)
    for stage, values in buckets.items():
        out[stage] = {
            "count": float(len(values)),
            "p50_ms": round(_percentile(values, 50.0), 3),
            "p95_ms": round(_percentile(values, 95.0), 3),
            "p99_ms": round(_percentile(values, 99.0), 3),
            "max_ms": round(max(values), 3),
            "mean_ms": round(sum(values) / len(values), 3),
        }
    return out


# ── Prometheus exposition (text format v0.0.4) ────────────────────────────────


# Default histogram bucket edges for ``qscreen_extraction_duration_ms`` — kept
# identical to the request spec so a downstream collector parses them the
# same way regardless of how this codebase evolves.
DEFAULT_HIST_BUCKETS_MS: tuple[float, ...] = (
    50.0,
    100.0,
    250.0,
    500.0,
    1000.0,
    2500.0,
    5000.0,
    10000.0,
)


def _format_value(v: float) -> str:
    """Prometheus accepts ints and floats; we keep ints as ints so ``+Inf``
    renders as the conventional ``+Inf`` (not ``inf``)."""
    if v != v:  # NaN
        return "NaN"
    if v == float("inf"):
        return "+Inf"
    if v == float("-inf"):
        return "-Inf"
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    return repr(v)


def emit_metrics(
    records: list[PerfRecord], hist_buckets: tuple[float, ...] = DEFAULT_HIST_BUCKETS_MS
) -> str:
    """Render one batch's records as Prometheus text-format output (v0.0.4).

    Emitted metric families:
      * ``qscreen_perf_stage_duration_ms_count`` (per stage, no labels)
      * ``qscreen_perf_stage_duration_ms_sum``   (per stage, no labels)
      * ``qscreen_perf_stage_duration_ms_max``   (per stage, no labels)
      * ``qscreen_perf_stage_duration_ms_bucket{le="..."}`` (cumulative)

    The ``stage`` label is the same string the engine logged (e.g. ``extract``,
    ``pdf_to_pages``, ``gates.run``, …), so an operator can group them in a
    Prometheus query.
    """
    if not records:
        return ""

    # Per-stage buckets + sum + count, accumulated in a Prometheus-friendly shape.
    per_stage: dict[str, dict[str, float]] = {}
    for rec in records:
        for sample in rec.samples:
            slot = per_stage.setdefault(
                sample.stage,
                {"count": 0.0, "sum": 0.0, **{f"le_{b}": 0.0 for b in hist_buckets}, "le_inf": 0.0},
            )
            slot["count"] += 1.0
            slot["sum"] += sample.duration_ms
            placed = False
            for b in hist_buckets:
                if sample.duration_ms <= b:
                    slot[f"le_{b}"] += 1.0
                    placed = True
            if not placed:
                slot["le_inf"] += 1.0

    lines: list[str] = []
    for stage in sorted(per_stage.keys()):
        slot = per_stage[stage]
        metric = "qscreen_perf_stage_duration_ms"
        label = f'{{stage="{stage}"}}'
        lines.append(
            f"# HELP {metric} Per-stage wall time in milliseconds (from a single bench batch)."
        )
        lines.append(f"# TYPE {metric} histogram")
        # Buckets are cumulative: le="50" includes everything ≤50ms.
        for b in hist_buckets:
            count_le = slot[f"le_{b}"]
            bucket_label = f'{{stage="{stage}",le="{_format_value(b)}"}}'
            lines.append(f"{metric}_bucket{bucket_label} {int(count_le)}")
        # +Inf bucket = total count (everything falls into +Inf).
        inf_label = f'{{stage="{stage}",le="+Inf"}}'
        lines.append(f"{metric}_bucket{inf_label} {int(slot['count'])}")
        lines.append(f"{metric}_count{label} {int(slot['count'])}")
        # sum is a double in Prometheus but float in Python — emit as a float
        # so the histogram arithmetic in the collector is precise.
        lines.append(f"{metric}_sum{label} {_format_value(slot['sum'])}")
    return "\n".join(lines) + "\n"


# ── regression detection ─────────────────────────────────────────────────────


def check_regression(
    baseline: dict[str, dict[str, float]],
    current: dict[str, dict[str, float]],
    threshold: float = 0.20,
) -> list[str]:
    """Compare current per-stage aggregates against a baseline. Returns a
    list of human-readable warnings whenever ``current[stage].p95_ms`` is
    ``>= threshold`` (default 20 %) worse than the baseline's p95.

    A stage only present in baseline or only in current is flagged with a
    different message ("missing" vs "new stage") so the warning carries the
    right actionable hint.
    """
    warns: list[str] = []
    if not baseline:
        return warns
    if threshold < 0:
        threshold = 0.0

    for stage, base in baseline.items():
        cur = current.get(stage)
        if cur is None:
            warns.append(
                f"perf: stage '{stage}' missing from current run (was {int(base.get('count', 0))} samples in baseline)"
            )
            continue
        b_p95 = float(base.get("p95_ms") or 0.0)
        c_p95 = float(cur.get("p95_ms") or 0.0)
        # Avoid divide-by-zero — a stage that was zero-time in the baseline
        # is suspicious, but we still compute the relative jump so a real
        # regression (5ms → 50ms) is flagged.
        denom = b_p95 if b_p95 > 1e-9 else 1e-9
        delta_pct = (c_p95 - b_p95) / denom
        if delta_pct >= threshold:
            jump_pct = round(delta_pct * 100.0, 1)
            warns.append(
                f"perf: stage '{stage}' p95 regressed +{jump_pct}% "
                f"(baseline={b_p95:.1f}ms, current={c_p95:.1f}ms, threshold={int(threshold * 100)}%)"
            )

    for stage in current:
        if stage not in baseline:
            warns.append(
                f"perf: stage '{stage}' is new (not in baseline) — verify the new instrumentation"
            )
    return warns


# ── env helpers ───────────────────────────────────────────────────────────────


def is_timing_enabled() -> bool:
    """True if either ``--timing`` was passed to the bench or ``PERF_TIMING=1``
    is set in the environment. The bench checks this itself; the engine
    uses ``PERF_TIMING`` (set by the bench subprocess) so callers don't have
    to thread a flag through every code path."""
    return os.getenv("PERF_TIMING", "").strip() in ("1", "true", "TRUE", "yes", "YES")


def attach_to_args(args: Any, record: PerfRecord | None) -> None:
    """Stash a perf record on the engine's argparse Namespace so the various
    helper functions (``_apply_pre_flags``, ``pdf_to_pages``, …) can pick
    it up without changing their public signatures.

    The attribute is ``_perf_record`` and may be ``None`` when timing is off.
    """
    try:
        args._perf_record = record
    except Exception:
        # Some Namespace subclasses (or SimpleNamespace) are fully writable;
        # a frozen one is a programmer error here, so swallow.
        pass


def get_record(args: Any) -> PerfRecord | None:
    """Inverse of ``attach_to_args``. Returns ``None`` when timing is off or
    the attribute was never set."""
    if args is None:
        return None
    return getattr(args, "_perf_record", None)


# ── metric-sink hook ──────────────────────────────────────────────────────────
#
# ``qscreen_app`` (or any other observer) installs a callback on the engine's
# argparse Namespace at ``args._metric_sink``. The engine calls it at the
# natural observation points — filing processed, pre-flag warn, gate block —
# without Flask having to import any private engine state. The default is a
# silent no-op when the attribute is missing.


def attach_metric_sink(args: Any, sink: Any) -> None:
    """Install a metric callback on the engine's Namespace. The sink must
    accept a single ``(name: str, **labels)`` kwarg call (see
    ``qscreen_app._Metrics`` for the canonical implementation)."""
    with suppress(Exception):
        args._metric_sink = sink


def get_metric_sink(args: Any) -> Any:
    """Return the installed metric sink (or a no-op when none is set)."""
    sink = getattr(args, "_metric_sink", None)
    if sink is None:
        return _NULL_SINK
    return sink


def _null_sink(name: str, **labels: Any) -> None:
    return None


_NULL_SINK = _null_sink
