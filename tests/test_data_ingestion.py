"""Unit tests for src/data_ingestion.py — CEC monthly generation loader."""

import io
import sys
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from data_ingestion import load_cec_monthly_generation


def _make_cec_excel(tmp_path: Path) -> Path:
    """Write a minimal CEC-style Excel file to tmp_path/raw/cec/."""
    cec_dir = tmp_path / "raw" / "cec"
    cec_dir.mkdir(parents=True)

    rows = []
    for yr in range(2015, 2017):       # 2 years → 24 rows
        for mo in range(1, 13):
            rows.append({
                "Year": yr,
                "Month": mo,
                "Solar PV": float(mo * 100 + yr),
                "Wind": float(mo * 50 + yr),
                "Total": float(mo * 400 + yr),
            })
    df = pd.DataFrame(rows)

    out = cec_dir / "cec_test.xlsx"
    df.to_excel(out, index=False)
    return tmp_path


def test_load_cec_returns_correct_columns(tmp_path):
    data_dir = _make_cec_excel(tmp_path)
    result = load_cec_monthly_generation(data_dir)
    assert "year" in result.columns
    assert "month" in result.columns
    assert "solar_gwh" in result.columns
    assert "wind_gwh" in result.columns


def test_load_cec_returns_24_rows(tmp_path):
    data_dir = _make_cec_excel(tmp_path)
    result = load_cec_monthly_generation(data_dir)
    assert len(result) == 24


def test_load_cec_no_nulls(tmp_path):
    data_dir = _make_cec_excel(tmp_path)
    result = load_cec_monthly_generation(data_dir)
    assert result["solar_gwh"].isna().sum() == 0
    assert result["wind_gwh"].isna().sum() == 0


def test_load_cec_sorted_by_year_month(tmp_path):
    data_dir = _make_cec_excel(tmp_path)
    result = load_cec_monthly_generation(data_dir)
    assert list(result["year"]) == sorted(result["year"].tolist())


def test_load_cec_raises_if_no_files(tmp_path):
    (tmp_path / "raw" / "cec").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        load_cec_monthly_generation(tmp_path)


def test_load_cec_raises_if_no_solar_wind_columns(tmp_path):
    cec_dir = tmp_path / "raw" / "cec"
    cec_dir.mkdir(parents=True)
    df = pd.DataFrame({"Year": [2015], "Month": [1], "NaturalGas": [1000.0]})
    df.to_excel(cec_dir / "bad.xlsx", index=False)
    with pytest.raises(ValueError):
        load_cec_monthly_generation(tmp_path)
