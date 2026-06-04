# HelsinkiDisrupted — re-simulation plan

Generated: 2026-05-28T18:21:19

## Recommendation

- **Re-run 05_disaster simulations** if POI or disaster route WKT changed before publishing new KPIs.
- **D5 Group1 SPMM fix** changes civilian mobility model — re-run D5 and TP variants.

## Scope

- Affected settings files: **117** (9 base × 12 TP).
- Traffic Profile blocks (`Events*`) not modified.

## Priority

1. D5 UAVMule (MapRoute UAV + SPMM civilians)
2. D2 PartitionedCity (structural partition)
3. D1, D4, D8 narrative cluster scenarios
4. D6, D7, D9 controls only if comparing before/after map fixes