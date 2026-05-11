"""Regression helpers: panel OLS, diagnostics, output formatting."""

import numpy as np
import pandas as pd
from pathlib import Path

try:
    from linearmodels.panel import PanelOLS, PooledOLS
except ImportError:
    PanelOLS = None  # type: ignore

try:
    from statsmodels.stats.outliers_influence import variance_inflation_factor
except ImportError:
    variance_inflation_factor = None  # type: ignore

OUTCOMES = ["ramp_magnitude_mwh", "curtailment_days_per_month", "negative_lmp_hours_per_month"]
TABLES_DIR = Path(__file__).parent.parent / "output" / "tables"


def _set_panel_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["time"] = pd.to_datetime(df[["year", "month"]].assign(day=1))
    return df.set_index(["zip_code", "time"])


def fit_model(
    df: pd.DataFrame,
    outcome: str,
    extra_regressors: list[str] | None = None,
    model_label: str = "model",
    drop_q1_2023: bool = False,
) -> dict:
    """Fit a two-way FE panel model for one outcome. Returns result dict."""
    if PanelOLS is None:
        raise ImportError("linearmodels is required for panel regression")

    if drop_q1_2023 and "q1_2023_flag" in df.columns:
        df = df[~df["q1_2023_flag"]]

    data = df.dropna(subset=["log_btm_lag1", "log_btm_lag1_sq", outcome])
    data = _set_panel_index(data)

    regressors = ["log_btm_lag1", "log_btm_lag1_sq"]
    if extra_regressors:
        regressors += extra_regressors

    model = PanelOLS(data[outcome], data[regressors], entity_effects=True, time_effects=True)
    result = model.fit(cov_type="clustered", cluster_entity=True)

    return {
        "label": model_label,
        "outcome": outcome,
        "result": result,
        "n_obs": result.nobs,
        "r2_within": result.rsquared,
    }


def vif(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    """Variance inflation factors for a set of columns."""
    if variance_inflation_factor is None:
        raise ImportError("statsmodels is required for VIF computation")

    X = df[cols].dropna().values
    vifs = {col: variance_inflation_factor(X, i) for i, col in enumerate(cols)}
    return pd.Series(vifs, name="VIF")


def save_result_table(result_dict: dict) -> Path:
    """Write regression summary to CSV in output/tables/."""
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    path = TABLES_DIR / f"{result_dict['label']}_{result_dict['outcome']}.csv"

    result = result_dict["result"]
    ci = result.conf_int()
    table = pd.DataFrame(
        {
            "coef": result.params,
            "se": result.std_errors,
            "t": result.tstats,
            "pvalue": result.pvalues,
            "ci_lower": ci["lower"],
            "ci_upper": ci["upper"],
        }
    )
    table.to_csv(path)
    return path
