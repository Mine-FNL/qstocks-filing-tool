"""Unit tests for qscreen_perf — the engine's per-stage timing primitives.

Plain pytest style. No real engine invocation; these exercise the perf
machinery itself (StageTimer, aggregate, check_regression, emit_metrics).
"""

from __future__ import annotations

import logging
import time

import pytest

import qscreen_perf as perf


def _sleep_ms(ms: float) -> None:
    time.sleep(ms / 1000.0)


def test_stage_timer_records_elapsed():
    """StageTimer writes (stage, duration_ms, metadata) to the PerfRecord."""
    log = logging.getLogger("qstock.test.perf")
    rec = perf.PerfRecord()
    with perf.StageTimer(log, rec, "extract", mode="basic") as t:
        _sleep_ms(5)
        t.metadata["rows"] = 42
    assert len(rec.samples) == 1
    s = rec.samples[0]
    assert s.stage == "extract"
    # 5 ms target + generous slack for CI jitter on a busy runner
    assert s.duration_ms >= 3.0, s.duration_ms
    assert s.metadata.get("mode") == "basic"
    assert s.metadata.get("rows") == 42


def test_aggregate_computes_percentiles():
    """aggregate() returns count / p50 / p95 / p99 / max_ms per stage."""
    # 20 records, each with one sample at value == 1ms .. 20ms
    recs = []
    for i in range(1, 21):
        rec = perf.PerfRecord()
        rec.add("extract", float(i))
        recs.append(rec)
    agg = perf.aggregate(recs)
    assert "extract" in agg
    s = agg["extract"]
    assert s["count"] == 20.0
    # percentile bounds for a known integer distribution
    assert 9.5 <= s["p50_ms"] <= 11.5
    assert 17.5 <= s["p95_ms"] <= 19.5
    assert 18.5 <= s["p99_ms"] <= 20.0
    assert s["max_ms"] == 20.0


def test_check_regression_flags_p95_jump_above_threshold():
    """p95 jump ≥ 20% is flagged; below threshold is silent."""
    baseline = {"extract": {"p95_ms": 100.0, "count": 10}}
    cur = {"extract": {"p95_ms": 150.0, "count": 10}}
    warns = perf.check_regression(baseline, cur, threshold=0.20)
    assert len(warns) == 1
    assert "p95 regressed" in warns[0]
    assert "extract" in warns[0]
    assert "+50.0%" in warns[0]


def test_check_regression_does_not_flag_within_threshold():
    """Within-threshold drift is silent (otherwise every release would warn)."""
    baseline = {"extract": {"p95_ms": 100.0, "count": 10}}
    cur = {"extract": {"p95_ms": 105.0, "count": 10}}
    warns = perf.check_regression(baseline, cur, threshold=0.20)
    assert warns == []


def test_emit_metrics_produces_valid_prometheus_format():
    """Output parses as Prometheus text exposition (HELP/TYPE/bucket/_count/_sum)."""
    rec = perf.PerfRecord()
    rec.add("extract", 12.0)
    rec.add("extract", 120.0)
    rec.add("pdf_to_pages", 8.0)
    text = perf.emit_metrics([rec])
    assert text.endswith("\n")
    # Two stages, so each HELP/TYPE line appears twice (one per stage).
    assert text.count("# TYPE qscreen_perf_stage_duration_ms histogram") == 2
    # Standard buckets are present in the bucket lines (Prometheus convention).
    for bucket in ("50", "100", "250", "500", "1000", "2500", "5000", "10000"):
        assert f'le="{bucket}"' in text, f'missing le="{bucket}"'
    # +Inf bucket must be emitted so a Prometheus client treats the histogram as total.
    assert 'le="+Inf"' in text
    # _count and _sum series are required for a histogram metric.
    assert "qscreen_perf_stage_duration_ms_count{" in text
    assert "qscreen_perf_stage_duration_ms_sum{" in text
    # Each stage's label set must be present.
    assert 'stage="extract"' in text
    assert 'stage="pdf_to_pages"' in text


if __name__ == "__main__":
    # Allow ``python -m tests.test_perf`` for ad-hoc debugging.
    raise SystemExit(pytest.main([__file__, "-v"]))
