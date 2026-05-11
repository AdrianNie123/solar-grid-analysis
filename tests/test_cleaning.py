"""Unit tests for src/cleaning.py"""

import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from cleaning import standardize_zip, clean_dgstats, aggregate_dgstats_panel


def make_dgstats(rows):
    return pd.DataFrame(rows)


def test_standardize_zip_leading_zeros():
    s = pd.Series(["90210", "1234", "00501"])
    result = standardize_zip(s)
    assert list(result) == ["90210", "01234", "00501"]


def test_standardize_zip_strips_whitespace():
    s = pd.Series([" 90210 ", "94107"])
    assert list(standardize_zip(s)) == ["90210", "94107"]


def test_clean_dgstats_drops_non_ca_zip():
    df = make_dgstats([
        {"application_id": "1", "zip_code": "90210", "system_size_dc": 5.0,
         "app_approved_date": "2020-01-01", "utility": "SCE"},
        {"application_id": "2", "zip_code": "10001", "system_size_dc": 5.0,
         "app_approved_date": "2020-01-01", "utility": "SCE"},  # NYC zip
    ])
    result = clean_dgstats(df)
    assert len(result) == 1
    assert result.iloc[0]["zip_code"] == "90210"


def test_clean_dgstats_drops_zero_size():
    df = make_dgstats([
        {"application_id": "1", "zip_code": "94107", "system_size_dc": 0.0,
         "app_approved_date": "2020-01-01", "utility": "PG&E"},
        {"application_id": "2", "zip_code": "94107", "system_size_dc": 8.5,
         "app_approved_date": "2020-01-01", "utility": "PG&E"},
    ])
    result = clean_dgstats(df)
    assert len(result) == 1
    assert result.iloc[0]["system_size_dc"] == 8.5


def test_clean_dgstats_flags_size_outlier():
    df = make_dgstats([
        {"application_id": "1", "zip_code": "94107", "system_size_dc": 150.0,
         "app_approved_date": "2020-06-01", "utility": "PG&E"},
        {"application_id": "2", "zip_code": "94107", "system_size_dc": 8.5,
         "app_approved_date": "2020-06-01", "utility": "PG&E"},
    ])
    result = clean_dgstats(df)
    assert result[result["application_id"] == "1"]["size_outlier"].iloc[0] is True
    assert result[result["application_id"] == "2"]["size_outlier"].iloc[0] is False


def test_clean_dgstats_q1_2023_flag():
    df = make_dgstats([
        {"application_id": "1", "zip_code": "92101", "system_size_dc": 7.0,
         "app_approved_date": "2023-02-15", "utility": "SDG&E"},
        {"application_id": "2", "zip_code": "92101", "system_size_dc": 7.0,
         "app_approved_date": "2023-06-01", "utility": "SDG&E"},
    ])
    result = clean_dgstats(df)
    assert result[result["application_id"] == "1"]["q1_2023_flag"].iloc[0] is True
    assert result[result["application_id"] == "2"]["q1_2023_flag"].iloc[0] is False


def test_aggregate_dgstats_panel_cumulative():
    df = make_dgstats([
        {"application_id": "1", "zip_code": "94107", "system_size_dc": 5.0,
         "app_approved_date": "2019-03-01", "utility": "PG&E"},
        {"application_id": "2", "zip_code": "94107", "system_size_dc": 10.0,
         "app_approved_date": "2020-07-01", "utility": "PG&E"},
    ])
    clean = clean_dgstats(df)
    panel = aggregate_dgstats_panel(clean)
    panel = panel.sort_values("year").reset_index(drop=True)
    assert panel.iloc[0]["btm_capacity_kw"] == pytest.approx(5.0)
    assert panel.iloc[1]["btm_capacity_kw"] == pytest.approx(15.0)  # cumulative
