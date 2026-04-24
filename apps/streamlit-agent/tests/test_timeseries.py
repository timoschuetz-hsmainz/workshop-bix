from __future__ import annotations

from agent.timeseries import TimeseriesPoint, phase_segments


def test_phase_segments_groups_consecutive_phases() -> None:
    points = [
        TimeseriesPoint(batch_id="A_B001", t_pct=0.0, temp_c=10.0, phase="heatup"),
        TimeseriesPoint(batch_id="A_B001", t_pct=10.0, temp_c=20.0, phase="heatup"),
        TimeseriesPoint(batch_id="A_B001", t_pct=20.0, temp_c=30.0, phase="hold"),
        TimeseriesPoint(batch_id="A_B001", t_pct=30.0, temp_c=40.0, phase="hold"),
        TimeseriesPoint(batch_id="A_B001", t_pct=40.0, temp_c=50.0, phase="cooldown"),
    ]

    segs = phase_segments(points)
    assert [(s.phase, s.t_start, s.t_end) for s in segs] == [
        ("heatup", 0.0, 10.0),
        ("hold", 20.0, 30.0),
        ("cooldown", 40.0, 40.0),
    ]

