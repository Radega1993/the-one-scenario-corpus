# World size occupancy calibration (pilot)

Per-map `MovementModel.worldSize` from sim road span + `occupancy_margin_m`.
Primary metric: **`coverage_road_cells_pct`**. Re-sim required before metrics match settings.

## Calibration table

| Map | margin (m) | worldSize | bbox/world cells | pilot scenario |
|-----|------------|-----------|------------------|----------------|
| HelsinkiDowntown | 20 | 1713×1459 | 1.000 | `U1_CBD_Commuting_HelsinkiDowntown__TP01_Baseline` |
| KumpulaCampus | 20 | 1148×1036 | 1.000 | `C1_Campus_ClassChange__TP01_Baseline` |
| ManhattanMidtownGrid | 20 | 2120×1986 | 1.000 | `V1_TaxiLow_ManhattanMidtownGridMidtownGrid__TP01_Baseline` |
| NuuksioSparseTrails | 20 | 2470×2565 | 1.000 | `R1_Rural_SparseSPMM__TP01_Baseline` |
| HelsinkiDisrupted | 20 | 1711×1874 | 1.000 | `D1_ShelterHotspots_EmergencyMobility__TP01_Baseline` |
| KallioCommunityCompact | 20 | 1124×1149 | 1.000 | `S2_WeakCommunities_HighMixing__TP01_Baseline` |

## Pilot acceptance

| Map | pilot | road % | world % | world≥0.85×road | mismatch | PASS |
|-----|-------|--------|---------|-----------------|----------|------|
| HelsinkiDowntown | `U1_CBD_Commuting_HelsinkiDowntown__TP01_Baseline` | 65.3 | 28.2 | no | no | FAIL |
| KumpulaCampus | `C1_Campus_ClassChange__TP01_Baseline` | 91.4 | 62.4 | no | no | FAIL |
| ManhattanMidtownGrid | `V1_TaxiLow_ManhattanMidtownGridMidtownGrid__TP01_Baseline` | 17.7 | 11.9 | no | no | FAIL |
| NuuksioSparseTrails | `R1_Rural_SparseSPMM__TP01_Baseline` | 96.9 | 18.2 | no | no | FAIL |
| HelsinkiDisrupted | `D1_ShelterHotspots_EmergencyMobility__TP01_Baseline` | 89.1 | 49.4 | no | no | FAIL |
| KallioCommunityCompact | `S2_WeakCommunities_HighMixing__TP01_Baseline` | 94.2 | 61.0 | no | no | FAIL |

## Notes

- Do not compare `coverage_world_pct` from pre-calibration simulation reports.
- Full corpus (540) re-sim is out of scope; scale after pilot PASS.
