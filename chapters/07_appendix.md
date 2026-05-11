# Appendix

## A. Data Dictionary

| Variable | Source | Units | Notes |
|----------|--------|-------|-------|
| `btm_capacity_kw` | CEC DGStats | kW-DC | Cumulative residential NEM/NBT capacity at EOY |
| `install_count` | CEC DGStats | count | Annual new interconnections per ZIP |
| `ramp_magnitude_mwh` | CAISO | MW | Mean absolute hourly net-load ramp |
| `curtailment_days_per_month` | CAISO | days | Days with curtailment_pct > 10% |
| `negative_lmp_hours_per_month` | CAISO | hours | Hours with system LMP < $0 |
| `log_btm_lag1` | Derived | — | log(btm_capacity_kw, 12-month lag) |
| `nem_regime` | Derived | categorical | NEM1 / NEM2 / NBT based on utility × date |
| `q1_2023_flag` | Derived | binary | Install in Q1 2023 (pre-NBT pull-forward) |

## B. Regression Output Template

Each model output CSV contains: `coef`, `se`, `t`, `pvalue`, `ci_lower`, `ci_upper` for each regressor.

## C. NEM Policy Timeline

- **NEM 1.0 → 2.0**: Grandfathered legacy rates replaced by time-of-use export rates. Reduced the NPV of solar by ~10–15%.
- **NEM 2.0 → NBT (2023)**: Dramatically reduced export compensation (~75% reduction for peak-hour exports). Created strong Q1 2023 pull-forward.
- **NBT Design**: Shift from volumetric to avoided-cost export rates; includes grid benefit charge.
