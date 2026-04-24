from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DtwAlignment:
    obs_to_ref: list[int]  # index j in observed -> index i in reference


def _tslearn_dtw_path(ref: list[float], obs: list[float]) -> list[tuple[int, int]]:
    # Imported lazily so the app still runs without tslearn installed.
    from tslearn.metrics import dtw_path  # type: ignore

    path, _dist = dtw_path(ref, obs)
    return [(int(i), int(j)) for (i, j) in path]


def align_observed_to_reference(
    reference: list[float],
    observed: list[float],
    *,
    method: str = "tslearn_dtw",
) -> DtwAlignment:
    """
    Returns an index mapping from each observed index j to a reference index i.
    If multiple DTW path cells hit the same j, we pick the median i (stable).
    """
    if not reference or not observed:
        return DtwAlignment(obs_to_ref=[0 for _ in observed])

    if method != "tslearn_dtw":
        raise ValueError(f"Unknown DTW method: {method}")

    path = _tslearn_dtw_path(reference, observed)

    hits: dict[int, list[int]] = {}
    for i, j in path:
        hits.setdefault(j, []).append(i)

    obs_to_ref: list[int] = []
    for j in range(len(observed)):
        is_ = sorted(hits.get(j, [min(len(reference) - 1, j)]))
        obs_to_ref.append(is_[len(is_) // 2])

    # Clamp for safety
    obs_to_ref = [max(0, min(len(reference) - 1, i)) for i in obs_to_ref]
    return DtwAlignment(obs_to_ref=obs_to_ref)


def build_reference_series(
    golden_profile: dict[str, Any],
    *,
    phase: str,
    variable: str,
) -> dict[str, list[float]]:
    """
    Extract reference series from golden_profile rows for a phase+variable.
    Returns dict with aligned arrays: buckets, mean, std, lower, upper.
    """
    rows = [r for r in (golden_profile.get("rows") or []) if str(r.get("phase")) == phase and str(r.get("variable")) == variable]
    rows.sort(key=lambda r: int(r.get("t_pct_bucket", 0)))
    return {
        "t_pct_bucket": [int(r["t_pct_bucket"]) for r in rows],
        "mean": [float(r["mean"]) for r in rows],
        "std": [float(r["std"]) for r in rows],
        "lower": [float(r["lower"]) for r in rows],
        "upper": [float(r["upper"]) for r in rows],
    }

