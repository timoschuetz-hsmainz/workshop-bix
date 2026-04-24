from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from math import floor
from typing import Any, Iterable

from .timeseries import TimeseriesPoint
from .dtw_alignment import align_observed_to_reference, build_reference_series


@dataclass(frozen=True)
class PointEvaluation:
    idx: int
    batch_id: str
    phase: str
    t_pct: float
    t_pct_bucket: int
    z_scores: dict[str, float]
    flags: dict[str, bool]  # variable -> outside?
    flagged_variables_window: list[str]
    early_warning: bool
    critical: bool


def _bucket_t_pct(t_pct: float, step_pct: int) -> int:
    return int(floor(float(t_pct) / step_pct) * step_pct)


def _index_golden_profile(profile: dict[str, Any]) -> dict[tuple[str, int, str], dict[str, float]]:
    idx: dict[tuple[str, int, str], dict[str, float]] = {}
    for r in profile.get("rows", []) or []:
        try:
            phase = str(r["phase"])
            t_bucket = int(r["t_pct_bucket"])
            var = str(r["variable"])
            idx[(phase, t_bucket, var)] = {
                "mean": float(r["mean"]),
                "std": float(r["std"]),
                "lower": float(r["lower"]),
                "upper": float(r["upper"]),
            }
        except Exception:  # noqa: BLE001
            continue
    return idx


def evaluate_stream(
    points: Iterable[TimeseriesPoint],
    *,
    golden_profile: dict[str, Any],
    window_size: int = 5,
    t_pct_step: int = 5,
    z_threshold: float = 2.0,
    early_warning_min_vars: int = 2,
    critical_phase_ratio: float = 0.60,
) -> list[PointEvaluation]:
    """
    Streaming evaluation:
    - per point: z = (x - mean) / std per variable (if std>0 and profile row exists)
    - flag: |z| > z_threshold
    - window aggregation: last N points, count variables with at least one flag in window
    - early warning: >= early_warning_min_vars variables outside in window
    - critical: within a phase, proportion of points with any-flag > critical_phase_ratio
    """
    if window_size <= 0:
        raise ValueError("window_size must be > 0")

    gp = _index_golden_profile(golden_profile)

    window: deque[set[str]] = deque(maxlen=window_size)  # each entry: set of vars flagged at that point
    phase_counts: Counter[str] = Counter()
    phase_flag_counts: Counter[str] = Counter()

    out: list[PointEvaluation] = []
    for i, p in enumerate(points):
        t_bucket = _bucket_t_pct(p.t_pct, t_pct_step)
        z_scores: dict[str, float] = {}
        flags: dict[str, bool] = {}

        flagged_vars_this_point: set[str] = set()
        for var, x in p.values.items():
            ref = gp.get((p.phase, t_bucket, var))
            if not ref:
                continue
            sd = float(ref["std"])
            if sd <= 0.0:
                continue
            mu = float(ref["mean"])
            z = (float(x) - mu) / sd
            z_scores[var] = z
            outside = z > z_threshold or z < -z_threshold
            flags[var] = outside
            if outside:
                flagged_vars_this_point.add(var)

        window.append(flagged_vars_this_point)
        flagged_vars_window: set[str] = set().union(*window) if window else set()
        flagged_list = sorted(flagged_vars_window)

        early_warning = len(flagged_vars_window) >= early_warning_min_vars

        phase_counts[p.phase] += 1
        if flagged_vars_this_point:
            phase_flag_counts[p.phase] += 1
        ratio = phase_flag_counts[p.phase] / max(1, phase_counts[p.phase])
        critical = ratio > critical_phase_ratio

        out.append(
            PointEvaluation(
                idx=i,
                batch_id=p.batch_id,
                phase=p.phase,
                t_pct=p.t_pct,
                t_pct_bucket=t_bucket,
                z_scores=z_scores,
                flags=flags,
                flagged_variables_window=flagged_list,
                early_warning=early_warning,
                critical=critical,
            )
        )

    return out


def evaluate_stream_dtw(
    points: list[TimeseriesPoint],
    *,
    golden_profile: dict[str, Any],
    variable_subset: list[str] | None = None,
    window_size: int = 5,
    t_pct_step: int = 5,
    z_threshold: float = 2.0,
    early_warning_min_vars: int = 2,
    critical_phase_ratio: float = 0.60,
) -> list[PointEvaluation]:
    """
    DTW-aligned streaming evaluation (per phase, per variable):
    - For each phase, align the observed sequence to the golden reference median using DTW.
    - Compute z-scores against the aligned reference mean/std at the mapped index.
    """
    if not points:
        return []
    if window_size <= 0:
        raise ValueError("window_size must be > 0")

    # Group indices by phase (preserve original order for output)
    idx_by_phase: dict[str, list[int]] = {}
    for i, p in enumerate(points):
        idx_by_phase.setdefault(p.phase, []).append(i)

    # Precompute DTW mappings per phase+variable based on temp_C-like median reference
    # We only align variables that exist in both observed points and golden profile.
    all_vars_in_points: set[str] = set().union(*(set(p.values.keys()) for p in points))
    if variable_subset is None:
        vars_to_use = sorted(all_vars_in_points)
    else:
        vars_to_use = [v for v in variable_subset if v in all_vars_in_points]

    ref_cache: dict[tuple[str, str], dict[str, list[float]]] = {}
    align_cache: dict[tuple[str, str], list[int]] = {}

    for phase, idxs in idx_by_phase.items():
        for var in vars_to_use:
            ref = build_reference_series(golden_profile, phase=phase, variable=var)
            if not ref["mean"]:
                continue
            obs = [float(points[i].values.get(var, float("nan"))) for i in idxs]
            obs_clean = [x for x in obs if x == x]  # filter NaN
            if not obs_clean:
                continue
            # DTW requires aligned sequences; if we have NaNs, fallback to ignoring DTW for those points later.
            # For simplicity: run DTW on the NaN-filtered sequence if NaNs are present.
            # Map back by index order: we only support no-NaN per phase+var for DTW alignment.
            if any(x != x for x in obs):
                continue

            try:
                alignment = align_observed_to_reference(ref["mean"], obs)
            except Exception:  # noqa: BLE001
                continue
            ref_cache[(phase, var)] = ref
            align_cache[(phase, var)] = alignment.obs_to_ref

    window: deque[set[str]] = deque(maxlen=window_size)
    phase_counts: Counter[str] = Counter()
    phase_flag_counts: Counter[str] = Counter()

    out: list[PointEvaluation] = []
    for i, p in enumerate(points):
        t_bucket = _bucket_t_pct(p.t_pct, t_pct_step)
        z_scores: dict[str, float] = {}
        flags: dict[str, bool] = {}
        flagged_vars_this_point: set[str] = set()

        # Determine this point's index within its phase
        phase_idxs = idx_by_phase.get(p.phase, [])
        try:
            j_in_phase = phase_idxs.index(i)
        except ValueError:
            j_in_phase = 0

        for var, x in p.values.items():
            ref = ref_cache.get((p.phase, var))
            obs_to_ref = align_cache.get((p.phase, var))
            if not ref or not obs_to_ref:
                continue
            k = obs_to_ref[min(j_in_phase, len(obs_to_ref) - 1)]
            sd = float(ref["std"][k])
            if sd <= 0.0:
                continue
            mu = float(ref["mean"][k])
            z = (float(x) - mu) / sd
            z_scores[var] = z
            outside = z > z_threshold or z < -z_threshold
            flags[var] = outside
            if outside:
                flagged_vars_this_point.add(var)

        window.append(flagged_vars_this_point)
        flagged_vars_window: set[str] = set().union(*window) if window else set()
        flagged_list = sorted(flagged_vars_window)

        early_warning = len(flagged_vars_window) >= early_warning_min_vars

        phase_counts[p.phase] += 1
        if flagged_vars_this_point:
            phase_flag_counts[p.phase] += 1
        ratio = phase_flag_counts[p.phase] / max(1, phase_counts[p.phase])
        critical = ratio > critical_phase_ratio

        out.append(
            PointEvaluation(
                idx=i,
                batch_id=p.batch_id,
                phase=p.phase,
                t_pct=p.t_pct,
                t_pct_bucket=t_bucket,
                z_scores=z_scores,
                flags=flags,
                flagged_variables_window=flagged_list,
                early_warning=early_warning,
                critical=critical,
            )
        )

    return out

