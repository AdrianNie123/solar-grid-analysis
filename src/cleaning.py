"""Cleaning and standardization for DGStats and CAISO data."""

import numpy as np
import pandas as pd

# NEM policy regime start dates by utility (IOU only)
NEM_REGIME_DATES = {
    "SDG&E": {"NEM2": pd.Timestamp("2016-01-01"), "NBT": pd.Timestamp("2023-04-15")},
    "PG&E": {"NEM2": pd.Timestamp("2016-12-01"), "NBT": pd.Timestamp("2023-04-15")},
    "SCE": {"NEM2": pd.Timestamp("2017-07-01"), "NBT": pd.Timestamp("2023-04-15")},
}


def standardize_zip(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.zfill(5)


def clean_dgstats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["zip_code"] = standardize_zip(df["zip_code"])

    # Drop non-CA ZIPs (CA ZCTAs start 900xx–961xx)
    ca_mask = df["zip_code"].str.match(r"^9[0-6]\d{3}$")
    df = df[ca_mask]

    # Size cleaning
    df["system_size_dc"] = pd.to_numeric(df["system_size_dc"], errors="coerce")
    df = df[df["system_size_dc"] > 0]

    # Outlier flag: >100 kW for residential
    df["size_outlier"] = df["system_size_dc"] > 100

    # Date fields
    df["app_approved_date"] = pd.to_datetime(df["app_approved_date"], errors="coerce")
    df = df[df["app_approved_date"].notna()]
    # Drop future dates beyond project scope
    df = df[df["app_approved_date"] <= "2023-12-31"]

    df["install_year"] = df["app_approved_date"].dt.year
    df["install_quarter"] = df["app_approved_date"].dt.to_period("Q").astype(str)

    # NEM policy regime flag per row
    df["nem_regime"] = df.apply(_assign_nem_regime, axis=1)

    # Q1 2023 pull-forward flag
    df["q1_2023_flag"] = (df["install_year"] == 2023) & (
        df["app_approved_date"] < "2023-04-15"
    )

    # Battery storage flag
    df["has_storage"] = df.get("battery_storage", pd.Series(False, index=df.index)).astype(bool)

    return df


def _assign_nem_regime(row: pd.Series) -> str:
    utility = row.get("utility", "")
    date = row.get("app_approved_date")
    if pd.isna(date):
        return "unknown"
    for iou, dates in NEM_REGIME_DATES.items():
        if iou.lower() in str(utility).lower():
            if date >= dates["NBT"]:
                return "NBT"
            elif date >= dates["NEM2"]:
                return "NEM2"
            else:
                return "NEM1"
    return "other"


def aggregate_dgstats_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Produce ZIP × year panel with cumulative BTM metrics."""
    df = df[~df["size_outlier"]].copy()
    df = df.sort_values(["zip_code", "app_approved_date"])

    annual = (
        df.groupby(["zip_code", "install_year"])
        .agg(
            annual_capacity_kw=("system_size_dc", "sum"),
            install_count=("application_id", "count"),
            storage_paired_count=("has_storage", "sum"),
        )
        .reset_index()
    )

    # Cumulative capacity by ZIP (running sum over years)
    annual = annual.sort_values(["zip_code", "install_year"])
    annual["btm_capacity_kw"] = annual.groupby("zip_code")["annual_capacity_kw"].cumsum()

    return annual
