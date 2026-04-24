from __future__ import annotations

import csv
from pathlib import Path
from pprint import pprint


def _resolve_csv_path() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [
        repo_root / "challenges" / "caseA_batches.csv",
        repo_root / "challenges" / "challenge a" / "caseA_batches.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "Could not find caseA_batches.csv. Tried:\n- "
        + "\n- ".join(str(p) for p in candidates)
    )


def main() -> None:
    csv_path = _resolve_csv_path()
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        columns = list(reader.fieldnames or [])
        rows = list(reader)

    print("df.columns.tolist():")
    print(columns)
    print()

    print("df.head(3):")
    pprint(rows[:3], width=120, sort_dicts=False)
    print()

    num_batches = len(rows)
    print("Anzahl Batches:")
    print(num_batches)
    print()

    num_anomalous = 0
    if "is_anomalous" in columns:
        for r in rows:
            try:
                num_anomalous += int(str(r.get("is_anomalous", "0")).strip() or "0")
            except ValueError:
                pass

    print("Anzahl anomale Batches:")
    print(num_anomalous)
    print()

    anomaly_types: list[str] = []
    if "anomaly_type" in columns:
        seen: set[str] = set()
        for r in rows:
            v = r.get("anomaly_type")
            if v is None:
                continue
            s = str(v).strip()
            if not s:
                continue
            if s not in seen:
                seen.add(s)
                anomaly_types.append(s)
        anomaly_types = sorted(anomaly_types)

    print("Vorkommende anomaly_type-Werte:")
    print(anomaly_types)


if __name__ == "__main__":
    main()
