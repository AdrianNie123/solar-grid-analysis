# California Solar Adoption & Grid Displacement Analysis

Does geographic clustering of residential behind-the-meter (BTM) solar in California (2015–2023) predict measurable changes in grid stress — faster net-load ramps, higher curtailment, more negative wholesale prices?

## Setup

```bash
conda env create -f environment.yml
conda activate solar_grid_analysis
```

## Data Sources

| Source | Access | Output |
|--------|--------|--------|
| CEC DGStats | Bulk CSV download | `data/raw/dgstats_raw.parquet` |
| CAISO OASIS | `gridstatus` Python package | `data/raw/caiso_hourly_raw.parquet` |
| NREL DeepSolar CA | Kaggle/GitHub CSV | `data/raw/deepsolar_ca_tracts.parquet` |
| Census ZIP–Tract crosswalk | Census API / IPUMS | `data/raw/zip_tract_xwalk.parquet` |
| Utility Territory GeoJSON | CEC shapefile | `data/external/utility_territories.geojson` |

## Notebook Pipeline

Run notebooks in order:

```
01_data_ingest.ipynb        → raw parquets
02_cleaning_qa.ipynb        → clean parquets + QC report
03_feature_engineering.ipynb → dgstats_panel, caiso_daily/monthly
04_panel_construction.ipynb  → panel_for_regression.parquet
05_eda.ipynb                 → EDA figures
06_regression_analysis.ipynb → 15 regression models
07_spatial_analysis.ipynb    → Moran's I, spatial lag, maps
08_timeseries_decomposition.ipynb → duck curve figures
09_visualizations.ipynb      → publication-ready figures
```

## Build the Book

```bash
jupyter-book build .
ghp-import -n -p -f output/_book/_build/html
```

## Scope Notes

- Residential NEM/NBT only (commercial and industrial excluded)
- IOU territories only: PG&E, SCE, SDG&E (LADWP, SMUD excluded)
- CAISO metrics are system-level, not distribution-level
