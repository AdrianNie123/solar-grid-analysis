"""Feature engineering for CAISO hourly data and panel construction."""

import numpy as np
import pandas as pd

NIGHTTIME_HOURS = set(range(0, 6)) | set(range(20, 24))


def compute_net_load(df: pd.DataFrame) -> pd.DataFrame:
    """Add net_load_mw and hourly ramp_mw columns."""
    df = df.copy()
    df["net_load_mw"] = df["demand_mw"] - df["solar_mw"] - df["wind_mw"]
    df = df.sort_values("interval_start_utc")
    df["ramp_mw"] = df["net_load_mw"].diff(1).abs()
    return df


def compute_curtailment(df: pd.DataFrame) -> pd.DataFrame:
    """Add curtailment_pct; flag days with >10% curtailment."""
    df = df.copy()
    total_renewable = df["solar_mw"] + df["wind_mw"]
    # Avoid division by zero
    df["curtailment_pct"] = np.where(
        total_renewable > 0,
        df.get("curtailment_mw", 0) / total_renewable,
        0.0,
    )
    return df


def aggregate_caiso_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate hourly CAISO data to daily metrics."""
    df = compute_net_load(df)
    df = compute_curtailment(df)
    df["date"] = pd.to_datetime(df["interval_start_utc"]).dt.date
    df["negative_lmp"] = df.get("lmp", 0) < 0

    daily = (
        df.groupby("date")
        .agg(
            ramp_magnitude_mwh=("ramp_mw", "mean"),
            curtailment_flag=("curtailment_pct", lambda x: (x > 0.10).any()),
            negative_lmp_hours=("negative_lmp", "sum"),
            peak_net_load_mw=("net_load_mw", "max"),
            min_net_load_mw=("net_load_mw", "min"),
        )
        .reset_index()
    )
    return daily


def aggregate_caiso_monthly(daily: pd.DataFrame) -> pd.DataFrame:
    """Roll daily metrics up to monthly."""
    daily = daily.copy()
    daily["date"] = pd.to_datetime(daily["date"])
    daily["year"] = daily["date"].dt.year
    daily["month"] = daily["date"].dt.month

    monthly = (
        daily.groupby(["year", "month"])
        .agg(
            ramp_magnitude_mwh=("ramp_magnitude_mwh", "mean"),
            curtailment_days_per_month=("curtailment_flag", "sum"),
            negative_lmp_hours_per_month=("negative_lmp_hours", "sum"),
        )
        .reset_index()
    )
    return monthly


def build_panel(
    dgstats_panel: pd.DataFrame,
    caiso_monthly: pd.DataFrame,
    deepsolar_zip: pd.DataFrame,
    zip_utility_map: pd.DataFrame,
) -> pd.DataFrame:
    """Merge all sources into ZIP × year × month panel for regression."""
    # Expand DGStats to year-month by repeating annual values
    years = dgstats_panel["install_year"].unique()
    months = range(1, 13)
    idx = pd.MultiIndex.from_product(
        [dgstats_panel["zip_code"].unique(), years, list(months)],
        names=["zip_code", "year", "month"],
    )
    panel = pd.DataFrame(index=idx).reset_index()

    panel = panel.merge(dgstats_panel, on=["zip_code", "year"], how="left")
    panel["btm_capacity_kw"] = panel["btm_capacity_kw"].fillna(0)

    panel = panel.merge(caiso_monthly, on=["year", "month"], how="left")
    panel = panel.merge(deepsolar_zip, on="zip_code", how="left")
    panel = panel.merge(zip_utility_map, on="zip_code", how="left")

    # Log transforms and lags
    panel = panel.sort_values(["zip_code", "year", "month"])
    panel["btm_lag1"] = panel.groupby("zip_code")["btm_capacity_kw"].shift(12)
    panel["btm_lag2"] = panel.groupby("zip_code")["btm_capacity_kw"].shift(24)

    cap_lag1 = panel["btm_lag1"].clip(lower=1)
    panel["log_btm_lag1"] = np.log(cap_lag1)
    panel["log_btm_lag1_sq"] = panel["log_btm_lag1"] ** 2

    return panel
