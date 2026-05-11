"""Unit tests for src/feature_engineering.py"""

import pandas as pd
import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from feature_engineering import compute_net_load, compute_curtailment, aggregate_caiso_daily


def make_caiso(rows):
    df = pd.DataFrame(rows)
    df["interval_start_utc"] = pd.to_datetime(df["interval_start_utc"])
    return df


def test_compute_net_load_basic():
    df = make_caiso([
        {"interval_start_utc": "2020-06-01 12:00", "demand_mw": 30000.0, "solar_mw": 5000.0, "wind_mw": 2000.0},
        {"interval_start_utc": "2020-06-01 13:00", "demand_mw": 28000.0, "solar_mw": 4000.0, "wind_mw": 2000.0},
    ])
    result = compute_net_load(df)
    assert result.iloc[0]["net_load_mw"] == pytest.approx(23000.0)
    assert result.iloc[1]["net_load_mw"] == pytest.approx(22000.0)


def test_compute_net_load_ramp():
    df = make_caiso([
        {"interval_start_utc": "2020-06-01 10:00", "demand_mw": 30000.0, "solar_mw": 5000.0, "wind_mw": 0.0},
        {"interval_start_utc": "2020-06-01 11:00", "demand_mw": 32000.0, "solar_mw": 7000.0, "wind_mw": 0.0},
    ])
    result = compute_net_load(df)
    # net_load[0] = 25000, net_load[1] = 25000 → ramp = 0
    assert result.iloc[1]["ramp_mw"] == pytest.approx(0.0)


def test_compute_curtailment_flag():
    df = pd.DataFrame({
        "solar_mw": [1000.0, 500.0],
        "wind_mw": [500.0, 500.0],
        "curtailment_mw": [200.0, 10.0],
    })
    result = compute_curtailment(df)
    # Row 0: 200 / 1500 = 0.133 → >10%
    # Row 1: 10 / 1000 = 0.01 → <10%
    assert result.iloc[0]["curtailment_pct"] == pytest.approx(200 / 1500)
    assert result.iloc[1]["curtailment_pct"] == pytest.approx(10 / 1000)


def test_aggregate_caiso_daily_row_count():
    rows = []
    for h in range(24):
        rows.append({
            "interval_start_utc": f"2022-03-15 {h:02d}:00",
            "demand_mw": 25000.0,
            "solar_mw": 2000.0 if 6 <= h <= 19 else 0.0,
            "wind_mw": 1000.0,
        })
    df = make_caiso(rows)
    daily = aggregate_caiso_daily(df)
    assert len(daily) == 1
    assert daily.iloc[0]["ramp_magnitude_mwh"] >= 0
