"""Spatial weight matrix construction and Moran's I testing."""

import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path

try:
    import libpysal
    import esda
except ImportError:
    libpysal = None  # type: ignore
    esda = None  # type: ignore

FIGURES_DIR = Path(__file__).parent.parent / "output" / "figures"


def build_queen_weights(gdf: gpd.GeoDataFrame, id_col: str = "zip_code"):
    """Build queen contiguity spatial weights."""
    if libpysal is None:
        raise ImportError("libpysal is required")
    w = libpysal.weights.Queen.from_dataframe(gdf, idVariable=id_col)
    w.transform = "r"  # row-standardize
    return w


def build_idw_weights(gdf: gpd.GeoDataFrame, bandwidth_km: float = 100, id_col: str = "zip_code"):
    """Build inverse-distance weights with a bandwidth cutoff."""
    if libpysal is None:
        raise ImportError("libpysal is required")
    coords = list(zip(gdf.geometry.centroid.x, gdf.geometry.centroid.y))
    w = libpysal.weights.DistanceBand.from_array(
        np.array(coords),
        threshold=bandwidth_km * 1000,  # convert km → m (assumes projected CRS)
        ids=gdf[id_col].tolist(),
    )
    w.transform = "r"
    return w


def morans_i(residuals: pd.Series, w, permutations: int = 999) -> dict:
    """Compute Moran's I with permutation inference."""
    if esda is None:
        raise ImportError("esda is required")
    mi = esda.Moran(residuals.values, w, permutations=permutations)
    return {
        "I": mi.I,
        "EI": mi.EI,
        "z_score": mi.z_norm,
        "p_value": mi.p_norm,
        "p_sim": mi.p_sim,
    }


def plot_morans_scatter(residuals: pd.Series, w, ax=None, save: bool = True):
    """Moran scatterplot: standardized residuals vs. spatial lag."""
    import matplotlib.pyplot as plt  # noqa: PLC0415

    z = (residuals - residuals.mean()) / residuals.std()
    lag_z = libpysal.weights.lag_spatial(w, z.values)

    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))

    ax.scatter(z, lag_z, alpha=0.4, s=12, color="steelblue")
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.axvline(0, color="gray", linewidth=0.8, linestyle="--")
    m, b = np.polyfit(z, lag_z, 1)
    x_line = np.linspace(z.min(), z.max(), 100)
    ax.plot(x_line, m * x_line + b, color="crimson", linewidth=1.5)
    ax.set_xlabel("Standardized residuals")
    ax.set_ylabel("Spatially lagged residuals")
    ax.set_title("Moran Scatterplot")

    if save:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        plt.savefig(FIGURES_DIR / "morans_scatter.png", dpi=300, bbox_inches="tight")
        plt.savefig(FIGURES_DIR / "morans_scatter.pdf", bbox_inches="tight")

    return fig, ax
