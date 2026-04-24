from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from math import floor
from pathlib import Path
from statistics import median, stdev
from typing import Any

from .batches import resolve_case_a_batches_path
from .timeseries import resolve_case_a_timeseries_path


@dataclass(frozen=True)
class GoldenProfileRow:
    phase: str
    t_pct_bucket: int
    variable: str
    mean: float  # median (robust center)
    std: float
    lower: float
    upper: float


def _bucket_t_pct(t_pct: float, step_pct: int) -> int:
    if step_pct <= 0:
        raise ValueError("step_pct must be > 0")
    return int(floor(float(t_pct) / step_pct) * step_pct)


def _is_trueish(v: Any) -> bool:
    if v is None:
        return False
    s = str(v).strip().lower()
    return s in {"1", "true", "t", "yes", "y"}


def build_case_a_golden_profile(
    repo_root: Path,
    *,
    t_pct_step: int = 5,
) -> dict[str, Any]:
    """
    Golden Profile for Case A.

    - "Good" batches: is_anomalous == 0 AND quality_pass == True
    - Merge with timeseries by batch_id
    - Group by phase and t_pct bucket (e.g. 5%-steps)
    - For each numeric variable, compute:
        - robust center: median (stored in output field "mean")
        - std (sample stdev; 0 if <2 points)
        - control limits: median ± 2*std

    Returns a JSON-serialisable dict: {"rows": [...], "meta": {...}}
    """
    batches_path = resolve_case_a_batches_path(repo_root)
    ts_path = resolve_case_a_timeseries_path(repo_root)

    good_batch_ids: set[str] = set()
    with batches_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("caseA_batches.csv has no header row")
        needed = {"batch_id", "is_anomalous", "quality_pass"}
        missing = sorted(needed - set(reader.fieldnames))
        if missing:
            raise ValueError(f"caseA_batches.csv missing columns: {missing}")

        for r in reader:
            batch_id = str(r.get("batch_id", "")).strip()
            if not batch_id:
                continue
            try:
                is_anomalous = int(str(r.get("is_anomalous", "0")).strip() or "0")
            except ValueError:
                is_anomalous = 0
            quality_pass = _is_trueish(r.get("quality_pass"))
            if is_anomalous == 0 and quality_pass:
                good_batch_ids.add(batch_id)

    with ts_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("caseA_timeseries.csv has no header row")

        cols = list(reader.fieldnames)
        required = {"batch_id", "phase", "t_pct"}
        missing = sorted(required - set(cols))
        if missing:
            raise ValueError(f"caseA_timeseries.csv missing columns: {missing}")

        non_value_cols = {"batch_id", "phase", "t_pct", "case"}
        candidate_value_cols = [c for c in cols if c not in non_value_cols]

        groups: dict[tuple[str, int, str], list[float]] = defaultdict(list)
        for r in reader:
            batch_id = str(r.get("batch_id", "")).strip()
            if batch_id not in good_batch_ids:
                continue

            phase = str(r.get("phase", "")).strip()
            try:
                t_pct = float(str(r.get("t_pct", "")).strip())
            except ValueError:
                continue
            t_bucket = _bucket_t_pct(t_pct, t_pct_step)

            for var in candidate_value_cols:
                raw = r.get(var)
                if raw is None:
                    continue
                s = str(raw).strip()
                if not s:
                    continue
                try:
                    val = float(s)
                except ValueError:
                    continue
                groups[(phase, t_bucket, var)].append(val)

    rows: list[GoldenProfileRow] = []
    for (phase, t_bucket, var), values in groups.items():
        if not values:
            continue
        m = float(median(values))
        sd = float(stdev(values)) if len(values) >= 2 else 0.0
        lower = m - 2.0 * sd
        upper = m + 2.0 * sd
        rows.append(
            GoldenProfileRow(
                phase=phase,
                t_pct_bucket=int(t_bucket),
                variable=str(var),
                mean=m,
                std=sd,
                lower=lower,
                upper=upper,
            )
        )

    rows.sort(key=lambda r: (r.phase, r.t_pct_bucket, r.variable))

    return {
        "meta": {
            "case": "A",
            "t_pct_step": int(t_pct_step),
            "num_good_batches": int(len(good_batch_ids)),
            "source_batches": str(batches_path),
            "source_timeseries": str(ts_path),
        },
        "rows": [
            {
                "phase": r.phase,
                "t_pct_bucket": r.t_pct_bucket,
                "variable": r.variable,
                "mean": r.mean,
                "std": r.std,
                "lower": r.lower,
                "upper": r.upper,
            }
            for r in rows
        ],
    }

