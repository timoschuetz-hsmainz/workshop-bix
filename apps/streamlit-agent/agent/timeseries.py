from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TimeseriesPoint:
    batch_id: str
    t_pct: float
    phase: str
    values: dict[str, float]

    @property
    def temp_c(self) -> float:
        # Backwards-compatible convenience accessor for the common column name.
        return float(self.values.get("temp_C", float("nan")))


@dataclass(frozen=True)
class PhaseSegment:
    t_start: float
    t_end: float
    phase: str


def resolve_case_a_timeseries_path(repo_root: Path) -> Path:
    candidates = [
        repo_root / "challenges" / "caseA_timeseries.csv",
        repo_root / "challenges" / "challenge a" / "caseA_timeseries.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "Could not find caseA_timeseries.csv. Tried:\n- "
        + "\n- ".join(str(p) for p in candidates)
    )


def load_case_a_timeseries(csv_path: Path) -> list[TimeseriesPoint]:
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        cols = list(reader.fieldnames or [])
        colset = set(cols)

        required = {"batch_id", "t_pct", "phase"}
        missing = sorted(required - colset)
        if missing:
            raise ValueError(f"caseA_timeseries.csv missing columns: {missing}")

        non_value_cols = {"batch_id", "phase", "t_pct", "case"}
        value_cols = [c for c in cols if c not in non_value_cols]

        points: list[TimeseriesPoint] = []
        for r in reader:
            batch_id = str(r.get("batch_id", "")).strip()
            phase = str(r.get("phase", "")).strip()
            try:
                t_pct = float(str(r.get("t_pct", "")).strip())
            except ValueError:
                continue

            values: dict[str, float] = {}
            for c in value_cols:
                raw = r.get(c)
                if raw is None:
                    continue
                s = str(raw).strip()
                if not s:
                    continue
                try:
                    values[c] = float(s)
                except ValueError:
                    continue

            points.append(TimeseriesPoint(batch_id=batch_id, t_pct=t_pct, phase=phase, values=values))

    points.sort(key=lambda p: (p.batch_id, p.t_pct))
    return points


def phase_segments(points: Iterable[TimeseriesPoint]) -> list[PhaseSegment]:
    pts = list(points)
    if not pts:
        return []

    segs: list[PhaseSegment] = []
    cur_phase = pts[0].phase
    t_start = pts[0].t_pct
    t_end = pts[0].t_pct

    for p in pts[1:]:
        if p.phase != cur_phase:
            segs.append(PhaseSegment(t_start=t_start, t_end=t_end, phase=cur_phase))
            cur_phase = p.phase
            t_start = p.t_pct
            t_end = p.t_pct
        else:
            t_end = p.t_pct

    segs.append(PhaseSegment(t_start=t_start, t_end=t_end, phase=cur_phase))
    return segs

