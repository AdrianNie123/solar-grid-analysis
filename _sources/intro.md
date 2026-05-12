# California Solar Adoption & Grid Evolution: A Data-Driven Analysis

## Executive Summary

Between 2015 and 2023, California's behind-the-meter (BTM) residential solar capacity grew from
0.3 GW to 9.2 GW—a 30-fold increase. This growth was highly concentrated geographically, with
Southern California counties (Riverside, Kern, San Bernardino) leading adoption. Over the same period,
the California grid's net-load curve underwent a dramatic shift: midday electricity demand fell to
near-zero due to massive solar generation, while evening demand ramps steepened.

**Main finding:** While BTM adoption clustering is visible and policy-responsive, grid stress (measured
as net-load ramp magnitude) is a system-wide phenomenon insensitive to geographic concentration. This
suggests grid planning requires aggregate-level insights, not just distribution-network focus.

## What's Inside

This Jupyter Book contains:
1. **Data pipeline:** 7 reproducible notebooks covering ingestion, cleaning, and analysis
2. **6 publication-ready figures:** Adoption trajectories, duck curves, spatial diagnostics
3. **Narrative chapters:** Research findings, limitations, and future directions
4. **Full code:** GitHub repository with reproducible analysis

## For Different Audiences

**Hiring managers/recruiters:**
Start with [Where Solar Clustered](adoption.md) and [How the Grid Changed](grid_evolution.md).

**Researchers/analysts:**
Clone the repository, run the notebooks, and adapt for other geographies or time periods.

**Policy/utility stakeholders:**
Read [Spatial & Temporal Dynamics](spatial_temporal.md) for key insights on adoption clustering
and grid stress decoupling.

## Key Visualizations

Six publication-ready figures are produced by this analysis:

1. **Adoption Trajectory** — BTM capacity growth by utility (PG&E, SCE, SDG&E), 2015–2023
2. **Adoption Density Heatmap** — Geographic clustering across California ZIP codes
3. **Duck Curve Evolution** — Net-load shift from smooth hump to sharp canyon (2015 vs. 2023)
4. **Hourly Load Profiles** — Daily patterns across 2015, 2018, 2022
5. **Grid Stress Trends** — Net-load ramp magnitude, monthly series 2015–2023
6. **Spatial Diagnostics** — Moran's I scatterplot; weak spatial clustering (I ≈ 0.10)

## Navigation

Use the table of contents (left sidebar) to jump to specific chapters.

```{tableofcontents}
```
