# NuuksioSparseTrails — re-simulation plan

Generated: 2026-05-28T18:15:32

## Recommendation

- **Re-run 04_rural simulations** if POI or ranger patrol WKT changed before publishing new KPIs.
- **R4 path fix** and **R1 rename** change settings identifiers; update external pipelines referencing `R1_Rural_RandomWaypoint`.
- Historical `output_metrics.csv` rows keep old R1 name until analysis is regenerated.

## Scope

- Affected settings files: **156** (12 base × 12 TP + variants).
- Traffic Profile blocks (`Events*`) not modified.

## Priority

1. R4 ParkRangers (MapRoute + patrol route)
2. R2 VillagesTrails (clusters on map)
3. R1, R3, R5 realistic SPMM
4. R6–R12 controls only if comparing before/after map fixes
