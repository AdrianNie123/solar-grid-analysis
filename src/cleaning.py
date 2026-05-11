"""Cleaning and standardization for DGStats and CAISO data."""

import numpy as np
import pandas as pd

NEM_REGIME_DATES = {
    "SDG&E": {"NEM2": pd.Timestamp("2016-01-01"), "NBT": pd.Timestamp("2023-04-15")},
    "PG&E":  {"NEM2": pd.Timestamp("2016-12-01"), "NBT": pd.Timestamp("2023-04-15")},
    "SCE":   {"NEM2": pd.Timestamp("2017-07-01"), "NBT": pd.Timestamp("2023-04-15")},
}


def standardize_zip(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.zfill(5)


def clean_dgstats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["zip_code"] = standardize_zip(df["zip_code"])
    df = df[df["zip_code"].str.match(r"^9[0-6]\d{3}$")]

    df["system_size_dc"] = pd.to_numeric(df["system_size_dc"], errors="coerce")
    df = df[df["system_size_dc"] > 0]
    df["size_outlier"] = df["system_size_dc"] > 100

    if not pd.api.types.is_datetime64_any_dtype(df["app_approved_date"]):
        df["app_approved_date"] = pd.to_datetime(df["app_approved_date"], errors="coerce")
    df = df[df["app_approved_date"].notna()]
    df = df[df["app_approved_date"] <= pd.Timestamp("2023-12-31")]

    df["install_year"] = df["app_approved_date"].dt.year
    df["install_quarter"] = df["app_approved_date"].dt.to_period("Q").astype(str)

    df["nem_regime"] = _assign_nem_regime_vectorized(df)

    df["q1_2023_flag"] = (df["install_year"] == 2023) & (
        df["app_approved_date"] < pd.Timestamp("2023-04-15")
    )

    storage_col = df["battery_storage"] if "battery_storage" in df.columns else pd.Series(False, index=df.index)
    df["has_storage"] = storage_col.astype(bool)

    return df


def _assign_nem_regime_vectorized(df: pd.DataFrame) -> pd.Series:
    """Vectorized NEM regime assignment across all rows."""
    date = df["app_approved_date"]
    utility = df["utility"].fillna("").str.lower()

    conditions, choices = [], []
    for iou, dates in NEM_REGIME_DATES.items():
        mask = utility.str.contains(iou.lower(), regex=False)
        conditions.extend([mask & (date >= dates["NBT"]), mask & (date >= dates["NEM2"]), mask])
        choices.extend(["NBT", "NEM2", "NEM1"])

    return pd.Series(np.select(conditions, choices, default="other"), index=df.index)


def aggregate_dgstats_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Produce ZIP × year panel with cumulative BTM metrics."""
    annual = (
        df[~df["size_outlier"]]
        .groupby(["zip_code", "install_year"])
        .agg(
            annual_capacity_kw=("system_size_dc", "sum"),
            install_count=("application_id", "count"),
            storage_paired_count=("has_storage", "sum"),
        )
        .reset_index()
        .sort_values(["zip_code", "install_year"])
    )
    annual["btm_capacity_kw"] = annual.groupby("zip_code")["annual_capacity_kw"].cumsum()
    return annual
