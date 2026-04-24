from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

from .monitoring import PointEvaluation, evaluate_stream
from .timeseries import TimeseriesPoint


@dataclass(frozen=True)
class DriverSummary:
    batch_id: str
    anomaly_score: float
    top_drivers: list[dict[str, Any]]  # [{"variable": ..., "mean_abs_z": ..., "count": ...}, ...]
    critical_phase: str | None
    z_max: dict[str, Any] | None  # {"variable": ..., "abs_z": ..., "z": ..., "phase": ..., "t_pct": ...}


_BATCH_RE = re.compile(r"\bA_B\d{3}\b")


def infer_batch_id(user_input: str, default: str = "A_B003") -> str:
    m = _BATCH_RE.search(user_input or "")
    return m.group(0) if m else default


def mean_abs_z_by_variable(evals: Iterable[PointEvaluation]) -> list[dict[str, Any]]:
    sums: dict[str, float] = defaultdict(float)
    counts: Counter[str] = Counter()
    for e in evals:
        for var, z in e.z_scores.items():
            sums[var] += abs(float(z))
            counts[var] += 1

    rows: list[dict[str, Any]] = []
    for var, cnt in counts.items():
        if cnt <= 0:
            continue
        rows.append({"variable": var, "mean_abs_z": sums[var] / cnt, "count": int(cnt)})

    rows.sort(key=lambda r: float(r["mean_abs_z"]), reverse=True)
    return rows


def critical_phase_from_evals(evals: Iterable[PointEvaluation]) -> str | None:
    # "critical" here = phase with highest ratio of any-flag points
    phase_counts: Counter[str] = Counter()
    phase_flag_counts: Counter[str] = Counter()
    for e in evals:
        phase_counts[e.phase] += 1
        if any(e.flags.values()):
            phase_flag_counts[e.phase] += 1

    if not phase_counts:
        return None

    def ratio(ph: str) -> float:
        return phase_flag_counts[ph] / max(1, phase_counts[ph])

    return max(phase_counts.keys(), key=lambda ph: (ratio(ph), phase_flag_counts[ph], phase_counts[ph]))


def z_max_from_evals(evals: Iterable[PointEvaluation]) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    best_abs = -1.0
    for e in evals:
        for var, z in e.z_scores.items():
            az = abs(float(z))
            if az > best_abs:
                best_abs = az
                best = {"variable": var, "abs_z": az, "z": float(z), "phase": e.phase, "t_pct": float(e.t_pct)}
    return best


def analyze_batch_against_golden_profile(
    points: list[TimeseriesPoint],
    *,
    golden_profile: dict[str, Any],
    window_size: int = 5,
    t_pct_step: int = 5,
    z_threshold: float = 2.0,
) -> DriverSummary:
    if not points:
        return DriverSummary(
            batch_id="",
            anomaly_score=0.0,
            top_drivers=[],
            critical_phase=None,
            z_max=None,
        )

    evals = evaluate_stream(
        points,
        golden_profile=golden_profile,
        window_size=window_size,
        t_pct_step=t_pct_step,
        z_threshold=z_threshold,
        early_warning_min_vars=2,
        critical_phase_ratio=0.60,
    )

    drivers = mean_abs_z_by_variable(evals)
    anomaly_score = float(sum(d["mean_abs_z"] for d in drivers) / max(1, len(drivers))) if drivers else 0.0

    return DriverSummary(
        batch_id=points[0].batch_id,
        anomaly_score=anomaly_score,
        top_drivers=drivers,
        critical_phase=critical_phase_from_evals(evals),
        z_max=z_max_from_evals(evals),
    )

