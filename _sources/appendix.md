# Appendix: Data Sources, Code, and Methodology

## Data Sources (Final)

| Source | Coverage | Granularity | Files Used |
|--------|----------|-------------|-----------|
| CEC DGStats | 1.8M+ residential NEM/NBT systems, 1999–present | Project-level, ZIP-geocoded | dgstats_panel.parquet |
| CAISO OASIS | Hourly system demand, fuel mix, LMPs, 2010–present | Hourly, system-level | caiso_hourly_merged.parquet |
| Census TIGER/Line | ZIP code boundaries (ZCTA5, 2020) | ZIP-level shapefile | ca_zcta.geojson |
| CEC Generation Report | Annual renewable generation by fuel, 2009–2024 | Annual, statewide | Total_System_Electric_Generation_2009-2024.xlsx |

## Code Repository

All code, notebooks, and data processing scripts are available at:
[GitHub URL—to be populated]

**Key modules:**
- `src/data_ingestion.py` — Data download and parsing
- `src/cleaning.py` — QC and standardization
- `src/feature_engineering.py` — Panel construction
- `src/plotting.py` — Figure generation

## Reproducibility

To reproduce this analysis:

```bash
# Create environment
conda env create -f environment.yml
conda activate solar_grid_analysis

# Run pipeline
jupyter notebook notebooks/01_data_ingest.ipynb
# ... run through 09_visualizations_final.ipynb

# Build Jupyter Book
jupyter-book build .
```

**Note:** Some data requires API queries (CAISO OASIS). Allow 1–2 hours for full data pipeline.

## Metrics & Definitions

**Net Load (MW):** Total demand minus utility-scale renewable generation (solar + wind + geo + biomass + hydro)

**Ramp Magnitude (MW/hour):** Absolute value of change in net load from hour *t* to hour *t+1*

**BTM Capacity (kW-DC):** Cumulative residential solar capacity per ZIP code, end-of-year

**Moran's I:** Spatial autocorrelation statistic; range [-1, 1]; I ≈ 0 indicates no spatial clustering

**NEM (Net Energy Metering):** California policy crediting solar customers for excess generation exported
to the grid. NEM 2.0 (2016–2023) credited at retail rates; NEM 3.0/NBT (2023+) credits at avoided cost.

**IOU (Investor-Owned Utility):** PG&E, SCE, SDG&E — the three large private utilities subject to CPUC
regulation and NEM policy. Covers ~75% of California electricity load.
