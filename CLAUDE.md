# Solar Grid Analysis — Claude Code Project Guide

## Research Question
Does geographic clustering of behind-the-meter (BTM) residential solar adoption in California (2015–2023) predict measurable changes in grid stress — specifically faster net-load ramps, higher curtailment rates, and more frequent negative wholesale prices?

## Project Goal
End-to-end spatial-econometric analysis deployed as a Jupyter Book on GitHub Pages. Audience: hiring managers evaluating quantitative/data science skills. Adrian Nie is the author.

---

## Tech Stack
- **Python 3.11** (via conda env `solar_grid_analysis`)
- **Data**: pandas, numpy, pyarrow (parquet)
- **Geo**: geopandas, pyogrio, libpysal, esda, spreg
- **Modeling**: statsmodels, linearmodels (PanelOLS), scikit-learn
- **Viz**: matplotlib, seaborn, plotly
- **CAISO data**: gridstatus (pip)
- **Book**: jupyter-book, ghp-import

Setup: `conda env create -f environment.yml && conda activate solar_grid_analysis`

---

## Directory Layout

```
solar_grid_analysis/
├── data/
│   ├── raw/                  ← source parquets + CSVs (gitignored)
│   │   ├── dgstats_raw.csv           MISSING — needs CEC DGStats bulk download
│   │   ├── dgstats_raw.parquet       produced by notebook 01
│   │   ├── caiso_hourly_raw.parquet  produced by notebook 01 (gridstatus API)
│   │   ├── deepsolar_ca_tracts.csv   ✅ in place
│   │   ├── zip_tract_xwalk.xlsx      ✅ in place (HUD Dec 2023)
│   │   └── caiso_shards/             monthly CAISO parquet cache
│   ├── processed/            ← intermediate parquets (gitignored)
│   └── external/
│       ├── tl_2020_us_zcta520.shp    ✅ in place (Census TIGER)
│       ├── utility_territories.*     MISSING — needs CPUC shapefile download
│       └── ca_zcta.geojson           produced when notebook 04 runs
├── notebooks/                ← 01–09 numbered analysis notebooks
├── src/                      ← Python utility modules (importable)
│   ├── data_ingestion.py
│   ├── cleaning.py
│   ├── feature_engineering.py
│   ├── regression_utils.py
│   ├── spatial_utils.py
│   └── plotting.py
├── output/
│   ├── figures/              ← PNG + PDF exports
│   └── tables/               ← regression CSV outputs
├── chapters/                 ← Jupyter Book narrative .md files
├── tests/                    ← pytest unit tests
├── _config.yml               ← Jupyter Book config
├── _toc.yml                  ← book table of contents
└── intro.md                  ← book landing page
```

---

## Data Sources & Status

| Source | File | Status | Notes |
|--------|------|--------|-------|
| CEC DGStats | `data/raw/dgstats_raw.csv` | **MISSING** | Search "CEC NEM Interconnection Data" on energy.ca.gov — bulk CSV download, one row per application |
| CAISO OASIS | fetched via `gridstatus` API | auto | Monthly batches 2015–2023, cached in `data/raw/caiso_shards/` |
| NREL DeepSolar | `data/raw/deepsolar_ca_tracts.csv` | ✅ | Full US dataset, filter to state='ca' in notebook 03 |
| HUD ZIP–Tract crosswalk | `data/raw/zip_tract_xwalk.xlsx` | ✅ | Dec 2023 vintage, has RES_RATIO weight column |
| Census TIGER ZCTA5 | `data/external/tl_2020_us_zcta520.shp` | ✅ | National 2020 file, filtered to CA ZCTAs in notebook 04 |
| Utility territories | `data/external/utility_territories.*` | **MISSING** | Search "CPUC electric utility service territory shapefile" |

---

## Notebook Pipeline (run in order)

| # | Notebook | Inputs | Key Output |
|---|----------|--------|------------|
| 01 | `01_data_ingest.ipynb` | raw CSVs + CAISO API | `data/raw/*.parquet` |
| 02 | `02_cleaning_qa.ipynb` | raw parquets | `data/processed/*_clean.parquet`, `qc_report.txt` |
| 03 | `03_feature_engineering.ipynb` | clean parquets | `dgstats_panel.parquet`, `caiso_daily/monthly.parquet` |
| 04 | `04_panel_construction.ipynb` | panel parquets + geo | `panel_for_regression.parquet` |
| 05 | `05_eda.ipynb` | panel | EDA figures |
| 06 | `06_regression_analysis.ipynb` | panel | 15 regression models, `output/tables/` |
| 07 | `07_spatial_analysis.ipynb` | residuals + W matrix | Moran's I, spatial lag model, choropleth |
| 08 | `08_timeseries_decomposition.ipynb` | CAISO hourly + cohorts | Duck curve figures × 3 |
| 09 | `09_visualizations.ipynb` | all above | 4 publication-ready figures |

---

## Regression Specification

**5 models × 3 outcomes = 15 total runs**

Outcomes: `ramp_magnitude_mwh`, `curtailment_days_per_month`, `negative_lmp_hours_per_month`

Baseline spec (Model 1):
```
Y_it = β₁·log(BTM_lag1) + β₂·[log(BTM_lag1)]² + γ_i (ZIP FE) + δ_t (year FE) + ε_it
```

All models use cluster-robust SEs by ZIP via `linearmodels.PanelOLS`.

Model variants:
- Model 2: + NEM regime interactions
- Model 3: stratified by adoption intensity quartile
- Model 4: + utility territory interactions
- Model 5: drop Q1 2023 (NBT pull-forward sensitivity)

---

## Key Domain Rules (burn these in)

**NEM policy regime dates:**
- SDG&E NEM 2.0: 2016-01-01 | NBT: 2023-04-15
- PG&E NEM 2.0: 2016-12-01 | NBT: 2023-04-15
- SCE NEM 2.0: 2017-07-01 | NBT: 2023-04-15

**Scope boundaries (never cross these):**
- Residential NEM/NBT only — no commercial, no industrial
- IOU territories only — PG&E, SCE, SDG&E (LADWP, SMUD excluded)
- CAISO grid metrics are system-level, not distribution-level — this is a known limitation, documented in Chapter 6

**Q1 2023 flag:** Installs before 2023-04-15 in year 2023 are flagged as potential NBT pull-forward. Model 5 drops these rows for sensitivity testing.

---

## Website Implementation (Jupyter Book → GitHub Pages)

The project is a Jupyter Book deployed to GitHub Pages. The site will contain:

**Navigation structure:**
1. Introduction — research question, motivation, scope
2. Chapter 1: Data & Methods — sources, panel construction, regression spec
3. Chapter 2: Exploratory Findings — adoption trends, grid-stress trends, correlation matrix
4. Chapter 3: Regression Results — 5 model tables, marginal effects plot
5. Chapter 4: Spatial Patterns — Moran's I, spatial lag model, residual choropleth
6. Chapter 5: Duck Curve Evolution — 2015/2018/2022 daily profiles
7. Chapter 6: Limitations & Discussion — scope caveats, identification challenges
8. Appendix: data dictionary, regression template

**Build & deploy:**
```bash
jupyter-book build .
ghp-import -n -p -f output/_book/_build/html
```

**Design intent:** Clean academic look, all figures at 300 DPI, labeled with source annotations. No interactive widgets in Phase 1 — static rendered notebook outputs only. Plotly charts (if used) should have static PNG fallbacks.

---

## Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Scaffolding — dirs, env, src modules, notebooks, tests | ✅ Done |
| 1 | Data ingestion + QC | Blocked: DGStats CSV + utility territory shapefile needed |
| 2 | Cleaning + feature engineering | Not started |
| 3 | EDA | Not started |
| 4 | Regression analysis | Not started |
| 5 | Spatial analysis | Not started |
| 6 | Time-series decomposition | Not started |
| 7 | Final visualizations | Not started |
| 8 | Jupyter Book build + deploy | Not started |

---

## Running Tests

```bash
cd solar_grid_analysis
conda activate solar_grid_analysis
pytest tests/ -v
```

Unit tests cover: ZIP standardization, DGStats cleaning, net-load computation, CAISO daily aggregation.
