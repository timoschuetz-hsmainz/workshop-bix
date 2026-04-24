from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BatchInfo:
    batch_id: str
    is_anomalous: int
    anomaly_type: str
    quality_pass: bool


def resolve_case_a_batches_path(repo_root: Path) -> Path:
    candidates = [
        repo_root / "challenges" / "caseA_batches.csv",
        repo_root / "challenges" / "challenge a" / "caseA_batches.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "Could not find caseA_batches.csv. Tried:\n- " + "\n- ".join(str(p) for p in candidates)
    )


def load_case_a_batches(csv_path: Path) -> dict[str, BatchInfo]:
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        cols = set(reader.fieldnames or [])

        required = {"batch_id", "is_anomalous", "anomaly_type", "quality_pass"}
        missing = sorted(required - cols)
        if missing:
            raise ValueError(f"caseA_batches.csv missing columns: {missing}")

        out: dict[str, BatchInfo] = {}
        for r in reader:
            batch_id = str(r.get("batch_id", "")).strip()
            if not batch_id:
                continue
            anomaly_type = str(r.get("anomaly_type", "")).strip()
            try:
                is_anomalous = int(str(r.get("is_anomalous", "0")).strip() or "0")
            except ValueError:
                is_anomalous = 0
            qp_raw = str(r.get("quality_pass", "")).strip().lower()
            quality_pass = qp_raw in {"1", "true", "t", "yes", "y"}
            out[batch_id] = BatchInfo(
                batch_id=batch_id,
                is_anomalous=is_anomalous,
                anomaly_type=anomaly_type,
                quality_pass=quality_pass,
            )

    return out

