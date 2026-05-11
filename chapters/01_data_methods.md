# Chapter 1: Data & Methods

## Data Sources

### CEC DGStats
California's distributed generation interconnection database. Residential NEM and NBT applications, 2015–2023. ~600K records after sector and date filters.

### CAISO OASIS
Hourly system-level grid data via the `gridstatus` Python package. Variables: total demand, solar generation, wind generation, curtailment, locational marginal prices. ~78,840 hourly observations.

### NREL DeepSolar
Satellite-detected residential PV systems aggregated to Census tract. Used to cross-validate DGStats coverage and provide tract-level spatial controls.

### Census ZIP–Tract Crosswalk
HUD USPS ZIP-to-tract relationship file. Used to map tract-level DeepSolar data to ZCTAs and to assign ZIP codes to utility territories.

## Methods

### Panel Construction
ZIP × year × month panel with running cumulative BTM capacity (kW-DC) as the key treatment variable.

### Regression Specification

$$
Y_{it} = \beta_1 \log(\text{BTM}_{i,t-1}) + \beta_2 [\log(\text{BTM}_{i,t-1})]^2 + \gamma_i + \delta_t + \varepsilon_{it}
$$

Where:
- $Y_{it}$: grid stress outcome (ramp magnitude, curtailment days, negative-LMP hours)
- $\gamma_i$: ZIP fixed effects (absorb time-invariant geography)
- $\delta_t$: year fixed effects (absorb common time trends)
- SEs clustered at ZIP level

### Spatial Analysis
Moran's I test on model residuals using queen-contiguity weights. Spatial lag model fitted if $I$ is significant at $p < 0.05$.

## Policy Regime Flags

| Utility | NEM 2.0 Start | NBT Start |
|---------|--------------|-----------|
| SDG&E | 2016-01-01 | 2023-04-15 |
| PG&E | 2016-12-01 | 2023-04-15 |
| SCE | 2017-07-01 | 2023-04-15 |
