# Chapter 6: Limitations & Discussion

## Key Limitations

**System-level grid metrics**: CAISO data is aggregated across the entire California ISO footprint. ZIP-level BTM adoption cannot be causally linked to ZIP-level curtailment or LMP impacts — only to system-wide effects. This is the most significant scope limitation.

**IOU scope only**: PG&E, SCE, and SDG&E represent ~70% of CA residential customers. LADWP (Los Angeles) and SMUD (Sacramento) are excluded because they report to separate balancing authorities with different data availability. Results should not be generalized to POU territories.

**Q1 2023 pull-forward**: The NBT transition in April 2023 created an incentive to accelerate installations before the policy change. Model 5 (sensitivity) drops Q1 2023 to test robustness.

**Omitted variables**: Weather (DNI, cloud cover), housing density, income, permitting timelines — all correlated with both adoption and grid stress. ZIP fixed effects absorb time-invariant confounders; time-varying confounders remain a threat to causal identification.

**Measurement lag**: DGStats records interconnection approval dates, not activation dates. Systems may take 1–3 months to activate after approval.
