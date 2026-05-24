# Corpus v3 recommendation (executive summary)

Generated: 2026-05-20 11:03 UTC

## Executive summary

Corpus v2 (720 scenarios) was audited without modifying settings. Cross-metrics diagnosis shows:

- **HelsinkiMedium** dominates (>90% bases) → diversify via MAP02–MAP04 in v3.
- **MAP_UNDERUSED** on WDM urban scenarios is often structural (large `worldSize`); v3 should crop to roads bbox.
- **TP04_FewLarge** and storm/critical TTL profiles belong in **stress**, not main benchmark.
- **TP12** cross-group scenarios are valid **diagnostic** controls (zero delivery with contacts).

## P0 correction priority

| scenario_base | P0 scenario count |
|---------------|------------------:|
| `R1_Rural_RandomWaypoint` | 12 |
| `R11_SpeedExtremeLow` | 12 |
| `U3_MicroMobility_HelsinkiMedium` | 11 |
| `D6_ShortTtlCritical_5to10min` | 9 |
| `S1_StrongCommunities_SeparateClusters` | 9 |
| `C3_Hackathon_24h` | 7 |
| `D7_HighLoad_TrafficStorm` | 7 |
| `U1_CBD_Commuting_HelsinkiMedium` | 6 |
| `U4_CongestionHotspot_HelsinkiMedium` | 6 |
| `V4_CarOwnership_0_HelsinkiMedium` | 6 |
| `D5_UAVMule_FastRoute_HelsinkiMedium` | 5 |
| `T4_VeryShortTtl_5to10min` | 5 |
| `R7_SparseTinyBuffer` | 5 |
| `D1_ShelterHotspots_Clusters` | 5 |
| `R3_WildlifeTracking` | 5 |

## Map change candidates

`D5_UAVMule_FastRoute_HelsinkiMedium`, `U1_CBD_Commuting_HelsinkiMedium`, `U3_MicroMobility_HelsinkiMedium`, `U4_CongestionHotspot_HelsinkiMedium`, `V4_CarOwnership_0_HelsinkiMedium`


## Acceptance checklist

- [x] `settings_audit.csv` / `.md` for 720 scenarios
- [x] `scenario_diagnosis.csv` / `.md` with flags and priority
- [x] `corpus_v3_plan.csv` with `status=pending` (no settings copied)
- [x] Map profiles MAP01–MAP10 documented
- [x] Mobility and traffic review reports
- [x] `realism_rules.md` + `realism_thresholds.yaml`
- [ ] Full spatial metrics on 720 scenarios (requires re-sim with SpatialOccupancyReport; 98 grids available today)
- [ ] `corpus_v3/` settings generation (future work)

## Next steps

1. Build `scenarios/corpus_v3/` from `corpus_v3_plan.csv` (filter `benchmark_split=main`).
2. Apply map profiles (crop worldSize, swap WKT paths).
3. Re-run simulations and `diagnose_scenarios.py` to validate TP differentiation.
