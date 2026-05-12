# California Solar Adoption & Grid Evolution (2015–2023)
### A Data Visualization & Analytics Portfolio Project

---

## Overview

This project visualizes California's energy transition through the lens of distributed solar adoption and grid operations over a 9-year period (2015–2023).

**What it is:** A reproducible data pipeline that transforms public datasets into publication-quality visualizations telling the story of how rapidly deployed solar technology reshaped California's electricity grid.

**What it isn't:** A hypothesis-driven causal analysis. This is a visual narrative using real operational data to document changes in adoption patterns and grid behavior.

---

## The Story

### 1. Where Solar Clustered

Behind-the-meter residential solar adoption in California grew 30-fold between 2015 and 2023—from 0.3 GW to 9.2 GW across the state's three largest utilities. This growth was geographically concentrated in high-solar-potential suburban areas, particularly inland Southern California (Riverside, Kern, San Bernardino counties).

**Key visualization:** Adoption density heatmap (9-panel map, 2015–2023) + adoption trajectory by utility (stacked bar chart).

### 2. How the Grid Changed

Over the same period, the California grid's net-load curve underwent a dramatic transformation. In 2015, utility-scale solar generation peaked at ~2 GW, creating a modest midday dip. By 2023, peak solar generation hit ~13 GW, pushing midday net load to near-zero and creating a sharp evening demand ramp. This transition—from a gentle "duck curve" to a steep "canyon"—created new operational challenges for grid operators.

**Key visualization:** Duck curve evolution (2015 vs. 2023 stacked area) + hourly load profiles (2015, 2018, 2022) + net-load ramp magnitude time series.

### 3. System-Level Perspective

Both adoption and grid stress increased over the period, but they tell independent stories. Grid stress (measured as net-load ramp magnitude) is a system-wide phenomenon—the result of aggregate renewable generation, not geographic clustering. While adoption is concentrated, the grid responds to total generation, not location.

**Key visualization:** Moran's I scatterplot showing weak spatial clustering of grid-stress residuals.

---

## What You'll Find Here

### Live Jupyter Book

**[Read the full analysis →](https://adriannie123.github.io/solar-grid-analysis)**

The Jupyter Book includes:
- 8 chapters covering data ingestion, cleaning, exploration, and visualization
- 6 publication-ready figures embedded in narrative context
- 7 reproducible Jupyter notebooks showing the full analysis pipeline
- Clear captions explaining what each figure shows and why it matters

### Data Pipeline

- **Input:** 1.8M+ solar installations (CEC DGStats), 9 years of grid operations (CAISO OASIS), public Census geography
- **Processing:** 7 notebooks handling ingestion, QC, feature engineering, aggregation, and visualization
- **Output:** Parquet files, publication-quality PNG figures, Jupyter Book HTML

### Code Repository

All code is open-source and reproducible:

```bash
git clone https://github.com/AdrianNie123/solar-grid-analysis.git
cd solar-grid-analysis/solar_grid_analysis
conda env create -f environment.yml
conda activate solar_grid_analysis
jupyter notebook
```

Then open any notebook (01–05, 08–09) to see the analysis step-by-step.

---

## The 6 Key Visualizations

1. **Adoption Trajectory by Utility (2015–2023)**
   Stacked bar chart showing cumulative BTM capacity growth, colored by utility (PG&E, SCE, SDG&E). Shows the 2023 policy inflection (NEM 2.0 → NBT transition).

2. **Adoption Density Heatmap (9-panel map)**
   ZIP-level BTM capacity, one panel per year (2015–2023). Geographic clustering visible in darkest reds (Southern California). Shows persistent concentration in high-solar-potential suburbs.

3. **Duck Curve Evolution: 2015 vs. 2023**
   Stacked area chart comparing net-load curves. Shows solar generation (orange), wind (light blue), and net load (total). Visually demonstrates the shift from smooth curve to sharp canyon.

4. **Hourly Load Profiles (2015, 2018, 2022)**
   Three 24-hour profiles showing average daily patterns. Illustrates how solar's footprint grew and deepened the midday trough. Real CAISO metered data, not synthetic.

5. **Grid Stress: Net-Load Ramp Magnitude (Time Series)**
   Monthly mean hourly ramp (absolute change in net load). Shows increasing volatility, especially summer peaks. Quantifies the operational challenge of matching supply to demand.

6. **Spatial Diagnostics: Moran's I Scatterplot**
   Tests for spatial clustering in regression residuals. Shows weak autocorrelation (I ≈ 0.10). Validates that ZIP-level adoption doesn't predict ZIP-level grid stress.

---

## Data Sources

All data is public and free:

| Source | What | Coverage | Access |
|--------|------|----------|--------|
| CEC DGStats | Project-level residential solar installations | 1.8M+ systems, 1999–present, IOU territories | californiadgstats.ca.gov |
| CAISO OASIS | Hourly grid demand, renewable generation, prices | 2010–present, California-wide | oasis.caiso.com |
| CEC Generation Report | Annual renewable generation by fuel type | 2009–2024, statewide | energy.ca.gov |
| Census TIGER | ZIP code boundaries (ZCTA5) | 2020 vintage | census.gov |

---

## Why This Matters

California's energy transition is a natural experiment in rapid distributed solar adoption. Understanding the patterns—both geographic and temporal—has implications for:

- **Utility operations:** Grid operators must plan for system-wide ramping, not local clustering
- **Policy design:** Adoption incentives are effective but geographically concentrated
- **Infrastructure planning:** Distribution-network constraints may be local, but grid-wide stress is aggregate
- **Equity:** Solar adoption skews toward higher-income areas; renters and lower-income customers are underrepresented

This project doesn't answer all questions, but it documents the scale and shape of the transition with public data.

---

## Key Insights

- **BTM adoption clustering is real and persistent.** Southern California (Riverside, Kern, San Bernardino, Orange, San Diego counties) accounts for the majority of distributed solar installations.
- **The grid's net-load curve deepened dramatically.** Midday net load dropped by ~5 GW between 2015 and 2023 due to massive solar generation. Evening ramps steepened.
- **Both trends are policy-responsive.** The sharp adoption plateau in 2023 reflects the NEM 2.0 → NBT transition (April 15, 2023), which increased the solar payback period from ~6 years to ~12 years.
- **Grid stress is system-wide, not local.** Despite geographic clustering, ZIP-level adoption density does not predict ZIP-level ramp behavior. The grid responds to aggregate generation, not location.
- **System-level metrics obscure local constraints.** CAISO data measures system-wide stress, but distribution-network hosting-capacity limits (feeder voltage, frequency) are local. Local and system-wide effects may coexist.

---

## How to Use This Project

### For Hiring Managers / Data Professionals

- **Read:** Start with the [GitHub Pages summary](https://adriannie123.github.io/solar-grid-analysis) (5 min)
- **View:** Browse the 6 figures and captions (5 min)
- **Engage:** Skim a notebook to see the code quality (10 min)

What this demonstrates:
- ✅ Can access and wrangle multi-source public data
- ✅ Understands energy domain (NEM, duck curve, grid ops)
- ✅ Executes rigorous data pipelines (7 notebooks, 3K+ lines of code)
- ✅ Creates publication-quality visualizations
- ✅ Communicates findings clearly without overselling
- ✅ Honest about scope and data constraints

### For Researchers / Analysts

```bash
git clone https://github.com/AdrianNie123/solar-grid-analysis.git
cd solar-grid-analysis/solar_grid_analysis
conda env create -f environment.yml
conda activate solar_grid_analysis
# Run notebooks 01–05, 08–09 in order
```

All code is reproducible and well-commented.

### For Utility / Policy Stakeholders

- **Key message:** Adoption is geographically clustered; grid stress is system-wide
- **Implication:** Grid planning requires aggregate perspective, not just local focus
- **Data gap:** Feeder-level analysis would reveal local hosting-capacity limits

---

## What's Not Included

This project does not include:
- Causal inference or hypothesis testing
- Household-level consumption data or rebound effects
- Feeder-level distribution-network analysis
- Cost-benefit analysis or policy recommendations
- Machine learning or predictive modeling

This is intentional. The focus is visualization and documentation of observed patterns using public data.

---

## Future Research Directions

If extending this work, interesting questions include:

- **Local hosting-capacity analysis:** Feeder-level voltage/frequency data would reveal whether adoption clustering causes local grid stress
- **Consumption response:** Customer-level metering data would measure rebound effects and heterogeneity by income
- **Policy elasticity:** Exploit NEM transitions as natural experiments to test adoption sensitivity to rates
- **Equity distribution:** Detailed analysis of who adopts (income, race, tenure) and cost-shift implications
- **Forecasting:** Predict adoption trajectories under alternative policy scenarios (ITC levels, rate designs)

---

## Technical Stack

- **Language:** Python 3.11
- **Data processing:** pandas, geopandas, numpy
- **Analysis:** statsmodels, esda (spatial statistics)
- **Visualization:** matplotlib, seaborn, plotly
- **Notebooks:** Jupyter / Jupyter Book
- **Data format:** Parquet (efficient, columnar)
- **Deployment:** GitHub Pages + Jupyter Book

---

## Timeline & Effort

- **Data assembly:** 2 weeks (API queries, caching, merging)
- **Exploratory analysis:** 2 weeks (EDA, feature engineering, QC)
- **Visualization & narrative:** 1 week (figure creation, writing)
- **Deployment:** 1 week (GitHub Pages, Jupyter Book)
- **Total:** ~6 weeks part-time

---

## Repository Structure

```
solar_grid_analysis/
├── notebooks/
│   ├── 01_data_ingest.ipynb               # Data download & parsing
│   ├── 02_cleaning_qa.ipynb               # QC and cleaning
│   ├── 03_feature_engineering.ipynb       # Feature creation
│   ├── 04_panel_construction.ipynb        # Panel building
│   ├── 05_eda.ipynb                       # Exploratory analysis
│   ├── 08_timeseries_decomposition.ipynb  # Time-series viz
│   └── 09_visualizations_final.ipynb      # Final figures
├── src/
│   ├── data_ingestion.py
│   ├── cleaning.py
│   ├── feature_engineering.py
│   └── plotting.py
├── data/
│   ├── raw/                    # Raw input files
│   └── processed/              # Cleaned parquets
├── output/
│   └── figures/                # 6 PNG files
├── _config.yml                 # Jupyter Book config
├── _toc.yml                    # Table of contents
├── environment.yml             # Conda dependencies
└── README.md                   # This file
```

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/AdrianNie123/solar-grid-analysis.git
cd solar-grid-analysis/solar_grid_analysis

# Create environment
conda env create -f environment.yml
conda activate solar_grid_analysis

# Run notebooks (in order)
jupyter notebook notebooks/01_data_ingest.ipynb
# ... continue through 09_visualizations_final.ipynb

# Build Jupyter Book (optional; already deployed)
jupyter-book build .

# View locally
open _build/html/index.html
```

**Note:** Some data requires API queries (CAISO OASIS). The pipeline handles caching automatically—first run takes ~1–2 hours; subsequent runs are <5 minutes.

---

## Metrics & Key Definitions

| Term | Definition |
|------|-----------|
| **Net Load (MW)** | Total electricity demand minus utility-scale renewable generation (solar, wind, geothermal, biomass, hydro) |
| **Net-Load Ramp (MW/hour)** | Absolute hourly change in net load; measures operational challenge of matching supply to demand swings |
| **BTM Capacity (kW-DC)** | Cumulative residential solar capacity per ZIP code, rated at standard test conditions |
| **Duck Curve** | Net-load curve shape: smooth morning ramp-up, midday valley from solar, steep evening recovery |
| **Canyon Curve** | The evolved duck curve with extreme midday lows and sharp evening ramps (post-2020) |
| **Moran's I** | Spatial autocorrelation statistic; range [-1, 1], where I ≈ 0 indicates no spatial clustering |

---

## Contact & Attribution

**Author:** Adrian Nie  
**Background:** UC Berkeley (B.A. Economics + Data Science, 2023)  
**GitHub:** [@AdrianNie123](https://github.com/AdrianNie123)  
**Email:** adriannie21@gmail.com

---

## License

This project and all code are released under the MIT License. Data sources are public and free.

**Acknowledgments:**  
California Energy Commission (CEC) · California ISO (CAISO) · NREL · U.S. Census Bureau

---

## How to Cite

```
Nie, Adrian. (2026). California Solar Adoption & Grid Evolution (2015–2023):
A Data Visualization Portfolio. GitHub Repository.
https://github.com/AdrianNie123/solar-grid-analysis
```

---

*Last updated: May 2026 · Data current through: December 2023 (CEC DGStats) · January 2024 (CAISO OASIS)*
