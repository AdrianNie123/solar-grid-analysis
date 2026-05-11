"""Publication-ready figure helpers."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

FIGURES_DIR = Path(__file__).parent.parent / "output" / "figures"
SOURCE_NOTE = "Sources: CEC DGStats, CAISO OASIS, NREL DeepSolar | IOU territories only"

UTILITY_COLORS = {"PG&E": "#1f77b4", "SCE": "#ff7f0e", "SDG&E": "#2ca02c"}


def _save(name: str, fig=None) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    f = fig or plt.gcf()
    f.savefig(FIGURES_DIR / f"{name}.png", dpi=300, bbox_inches="tight")
    f.savefig(FIGURES_DIR / f"{name}.pdf", bbox_inches="tight")


def duck_curve_evolution(hourly_2015, hourly_2023):
    """Figure 1: stacked area showing 2015 vs 2023 hourly net-load components."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, df, year in zip(axes, [hourly_2015, hourly_2023], [2015, 2023]):
        hours = df["hour"]
        ax.stackplot(
            hours,
            df["wind_mw"],
            df["solar_mw"],
            df["net_load_mw"],
            labels=["Wind", "Solar", "Net Load"],
            colors=["#aec7e8", "#ffbb78", "#1f77b4"],
            alpha=0.8,
        )
        ax.set_title(str(year))
        ax.set_xlabel("Hour of day")
        ax.xaxis.set_major_locator(mticker.MultipleLocator(4))
    axes[0].set_ylabel("MW")
    axes[0].legend(loc="upper right")
    fig.suptitle("Duck Curve Evolution: 2015 vs 2023 Average Day", fontsize=13)
    fig.text(0.5, -0.02, SOURCE_NOTE, ha="center", fontsize=8, color="gray")
    _save("duck_curve_evolution", fig)
    return fig


def adoption_density_heatmap(gdf, year_col: str = "year", capacity_col: str = "btm_capacity_kw"):
    """Figure 2: ZIP-level choropleth faceted by year."""
    import geopandas as gpd  # noqa: PLC0415

    years = sorted(gdf[year_col].unique())
    n = len(years)
    cols = 3
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    axes = axes.flatten()

    vmax = gdf[capacity_col].quantile(0.99)
    for ax, year in zip(axes, years):
        subset = gdf[gdf[year_col] == year]
        subset.plot(
            column=capacity_col,
            ax=ax,
            vmin=0,
            vmax=vmax,
            cmap="YlOrRd",
            legend=False,
            linewidth=0.2,
            edgecolor="white",
        )
        ax.set_title(str(year))
        ax.axis("off")
    for ax in axes[n:]:
        ax.set_visible(False)

    fig.suptitle("Cumulative BTM Capacity by ZIP (kW-DC)", fontsize=13)
    fig.text(0.5, -0.01, SOURCE_NOTE, ha="center", fontsize=8, color="gray")
    _save("adoption_density_heatmap", fig)
    return fig


def btm_vs_grid_scatter(df, outcome: str = "ramp_magnitude_mwh"):
    """Figure 4: log(BTM capacity) vs. grid stress outcome, colored by utility."""
    fig, ax = plt.subplots(figsize=(8, 5))
    for utility, color in UTILITY_COLORS.items():
        sub = df[df["utility"] == utility]
        ax.scatter(sub["log_btm_lag1"], sub[outcome], alpha=0.25, s=8, label=utility, color=color)

    ax.set_xlabel("log(Cumulative BTM Capacity, kW-DC)")
    outcome_label = outcome.replace("_", " ").title()
    ax.set_ylabel(outcome_label)
    ax.set_title(f"BTM Adoption vs. {outcome_label}")
    ax.legend()
    fig.text(0.5, -0.02, SOURCE_NOTE, ha="center", fontsize=8, color="gray")
    _save(f"btm_vs_{outcome}_scatter", fig)
    return fig
