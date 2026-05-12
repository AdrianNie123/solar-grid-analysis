# Limitations, Data Constraints, and Future Directions

## Data Granularity Constraints

This analysis is **system-level** in scope. We measure aggregate grid behavior (California-wide CAISO
interconnection) using system-level metrics (total net load, system LMP, system curtailment).

**This limits inference:**
- We **can** detect system-wide trends (duck curve deepening, increasing ramp magnitude)
- We **cannot** measure local distribution-network effects (feeder voltage, line losses, hosting capacity)
- We **cannot** determine whether local BTM clustering causes local grid stress

**To test local effects, we would need:**
- Feeder-level voltage and frequency data (not public)
- Distribution-network operator data (not public)
- Granular data requires utility data-sharing agreements and academic affiliation

## Coverage Limitations

This analysis covers **IOU territories only** (PG&E, SCE, SDG&E), representing ~75% of California's
electricity load. Municipal utilities (LADWP, SMUD, HECO) and rural cooperatives are excluded.

**Geographic bias:** IOU territories are predominantly urban and suburban. Rural and remote areas are
underrepresented.

## Data Currency

- **CEC DGStats:** Updated monthly with ~6-week lag. Latest data in this analysis: December 2023
- **CAISO OASIS:** Real-time data available; backfill to 2015 complete
- **Analysis window:** 2015–2023 (9 full years)
- **Policy context:** NEM transitions (1.0→2.0→3.0) and federal ITC phase-out (post-2025)
  are beyond this window

## Modeling Assumptions

1. **Behind-the-meter solar generation:** Estimated using installed capacity × NREL PVWatts
   profiles. Actual generation may vary due to soiling, temperature, shading, and inverter losses.
   Treated as typical-year performance.

2. **Income estimates (Tracking the Sun):** ZIP-level income is modeled using Census demographics
   and house-price imputations, not observed household income. Treat as proxy.

3. **System-level metrics as proxies for grid stress:** Net-load ramps are one metric; other valid
   metrics include frequency deviations, voltage swings, and transmission congestion. System-level
   metrics may not capture all grid challenges.

## What We Don't Know

1. **Do BTM adopters change their electricity consumption after installation?** (Rebound effect)
2. **Are solar adopters concentrated among high-income households, and does this exacerbate
   electricity affordability for renters and lower-income customers?** (Equity effects)
3. **What is the actual cost-shift from solar-inflected rate design?** (Contested; range: $1.5B–$8.5B/year)

## Future Research Directions

1. **Feeder-level analysis:** Obtain distribution-network data through utility partnerships to test
   local hosting-capacity constraints.

2. **Consumption response:** Access customer-level interval metering data (Green Button, utility
   data-sharing) to measure rebound effects and heterogeneity by income.

3. **Quasi-experimental design:** Leverage NEM policy transitions (2.0→3.0) as natural experiments
   to test adoption elasticity and distributional effects.

4. **Synthetic control or diff-in-diff:** Compare adoption trajectories in California (with NEM) versus
   other states (without NEM) to isolate policy effects.

5. **Agent-based modeling:** Build bottom-up models of residential adoption decisions to understand
   clustering and forecast future penetration under alternative policy regimes.
