# California Solar Adoption & Grid Evolution: A Data-Driven Analysis (2015–2023)

## Overview

This project analyzes the spatial and temporal patterns of behind-the-meter (BTM) residential solar
adoption across California and its relationship to grid operations from 2015 to 2023.

**Key findings:**
- BTM solar capacity grew 30x (0.3 GW → 9.2 GW) in IOU territories, concentrated in Southern California
- The grid's net-load curve shifted dramatically: midday loads dropped to near-zero; evening ramps steepened
- Geographic clustering of adoption does NOT predict ZIP-level grid stress; grid stress is system-wide

## Why This Matters

California's energy transition is a case study in how rapid distributed solar adoption reshapes grid
operations. Understanding adoption patterns and their grid consequences informs utility planning,
policy design, and equity considerations.

## Data

- **CEC DGStats:** 1.8M+ residential solar installations, ZIP-level, 2015–2023
- **CAISO OASIS:** Hourly grid operations data (load, renewable generation), 2015–2023
- **Public:** All data sources are free and publicly available

## Key Visualizations

1. **Adoption Trajectory** — BTM capacity growth by utility (PG&E, SCE, SDG&E)
2. **Adoption Density Heatmap** — Geographic clustering, 2015–2023
3. **Duck Curve Evolution** — Net-load shift from smooth hump to sharp canyon
4. **Hourly Load Profiles** — Daily patterns across 2015, 2018, 2022
5. **Grid Stress Trends** — Net-load ramp magnitude, 2015–2023
6. **Spatial Diagnostics** — Moran's I scatterplot; weak spatial clustering

## Limitations

- **System-level granularity:** Analysis covers California-wide grid, not local distribution networks
- **IOU-only coverage:** ~75% of state load; municipal utilities excluded
- **No household consumption data:** Rebound effects, customer behavior not measured
- **2023 cutoff:** NEM 3.0 policy effects and post-2024 federal ITC changes beyond scope

## How to Use This Project

### For Hiring Managers / Recruiters
- **Read:** `grid_evolution.md` and `spatial_temporal.md` for the core findings
- **Browse:** Output figures (6 high-resolution PNGs in `output/figures/`)
- **Access:** Full Jupyter Book deployment (live HTML at [URL—to be populated])

### For Researchers / Analysts
- **Clone:** All code, notebooks, and data pipeline are reproducible
- **Adapt:** Modify for other states, other time periods, or different granularities
- **Extend:** See `limitations.md` for future research directions

### For Utility / Policy Stakeholders
- **Key message:** Adoption clustering is visible but doesn't predict local grid stress
- **Implication:** Grid planning requires system-wide perspective, not just distribution-network focus
- **Caveat:** Feeder-level analysis would be needed to test local hosting-capacity limits

## Technical Stack

- **Language:** Python 3.11
- **Key libraries:** pandas, statsmodels, geopandas, matplotlib, linearmodels, esda
- **Data format:** Parquet (efficient, column-compressed)
- **Notebooks:** Jupyter / Jupyter Book
- **Reproducibility:** Conda environment file included

## Timeline & Effort

- **Data assembly:** ~2 weeks (mostly API queries and caching)
- **Analysis & figures:** ~3 weeks (exploratory analysis, spatial regression, visualization)
- **Writing & documentation:** ~1 week
- **Total:** ~6 weeks part-time work

## Contact & Attribution

**Author:** Adrian Nie
**Institutions:** UC Berkeley (B.A. Economics + Data Science, 2023)
**Repository:** [GitHub URL]
**Documentation:** Jupyter Book at [URL]

---

## Quick Start

```bash
# Install
conda env create -f environment.yml
conda activate solar_grid_analysis

# Run notebooks in order
jupyter notebook

# Build Jupyter Book
jupyter-book build .

# Open output
open _build/html/index.html
```

---

## Notebook Pipeline

```
01_data_ingest.ipynb           → raw parquets
02_cleaning_qa.ipynb           → clean parquets + QC report
03_feature_engineering.ipynb   → dgstats_panel.parquet
04_panel_construction.ipynb    → panel aggregation
05_eda.ipynb                   → EDA figures
08_timeseries_decomposition.ipynb → time-series analysis
09_visualizations_final.ipynb  → 6 publication-ready figures
```

## Metrics & Definitions

See `appendix.md` for full technical details.
