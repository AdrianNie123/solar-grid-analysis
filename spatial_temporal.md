# Spatial and Temporal Dynamics: Adoption Clustering and Grid Stress Decoupling

## Research Question

Does geographic clustering of BTM solar adoption predict measurable differences in ZIP-level grid stress
metrics (net-load ramps, curtailment, negative LMPs)?

## Finding: No Strong Relationship

```{figure} output/figures/morans_scatter.png
:name: morans-scatter
:width: 100%

Regression residuals show weak spatial clustering (Moran's I ≈ 0.10, p < 0.05), indicating that
ZIP-level adoption patterns do not systematically predict ZIP-level grid stress.
```

Regression analysis of ZIP-level adoption density versus ZIP-specific ramp magnitude found
**r = 0.02** (essentially zero correlation). Moran's I test for spatial autocorrelation in regression
residuals was weak (I ≈ 0.10, p < 0.05), indicating that ZIP-level adoption patterns do not
systematically predict ZIP-level grid stress.

## Why?

Grid stress is a **system-wide phenomenon**, not a local one:

1. **Aggregate effect dominates:** When solar generation across all of California ramps down at sunset,
   CAISO sees a single system-level event. Whether that solar is concentrated in Riverside or spread
   across 100 ZIPs, the ramp magnitude is the same.

2. **Utility-scale solar drives the curve:** The majority of the duck-curve deepening is driven by
   utility-scale solar (Mojave Desert, Central Valley), not distributed BTM solar. Utility-scale
   penetration has grown much faster than BTM.

3. **System operations are aggregate-focused:** Grid operators forecast total system ramping need,
   dispatch generation across the entire interconnection, and manage curtailment system-wide. Local
   clustering does not affect this system-level optimization.

4. **Data granularity mismatch:** System-level CAISO metrics (net load, curtailment, LMP) do not vary
   by ZIP or even by utility territory. They are invariant across all ZIPs within the CAISO interconnection.

## Implications

This finding suggests two possibilities:

1. **Grid stress is driven by aggregate penetration, not clustering.** Whether solar is concentrated or
   dispersed, the system-level ramp is the same.

2. **Local distribution-network constraints may exist, but are invisible at system level.** Feeder-level
   voltage and frequency data (not publicly available) would be required to test whether local BTM
   clustering causes local hosting-capacity limits.

## Data & Methods

- **Data:** CEC DGStats (ZIP-level), CAISO OASIS (system-level)
- **Method:** ZIP-level fixed-effects panel regression; Moran's I spatial autocorrelation test
- **Sample:** ~800 ZIPs with ≥1 installation; 2015–2023; ~6,000 ZIP-year observations
- **Outcome variable:** Monthly mean hourly net-load ramp magnitude (MW/hour)
- **Predictor:** Lagged cumulative BTM capacity (kW) per ZIP
