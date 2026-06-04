# Simulation time and warmup policy

Generated: 2026-05-24 10:28 UTC

- Rows: **720**
- CSV: `data/simulation_time_policy.csv`

## Global policy

- `warmup = 5% × endTime` (2160 s for 12 h runs)
- `analysis_cutoff = 90% × endTime` for message outcome metrics
- `Scenario.endTime = 43200` s is **sufficient** for connectivity-heavy scenarios (see `useful_time_ratio` ≈ 1)

## Spatial coverage linkage

Where `coverage_total < 12%`, prefer **worldSize crop** before extending endTime.

## Family notes

| family | note |
|--------|------|
| 01_urban | Low spatial % often map oversized, not short sim |
| 07_ | Stress lab — report separately |
| 04_rural | R1/R11 may need mobility fix not longer time |