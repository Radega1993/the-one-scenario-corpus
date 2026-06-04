# Corpus v2 benchmark validation

Generated: 2026-05-27 09:42 UTC

## Executive summary

- **Corpus:** `corpus_v1` — **720** scenarios (60 bases × 12 TP)
- **Settings files:** 540
- **Manifest rows:** 540
- **Output metrics:** 720 rows
- **Spatial metrics:** 720 rows
- **Scenarios needing attention (non-ok, non-valido_extremo):** 275

### Validation status counts

| Status | Count |
|--------|------:|
| `configuracion_sospechosa` | 106 |
| `error_probable` | 168 |
| `ok` | 191 |
| `pendiente_revision` | 1 |
| `valido_extremo` | 104 |

## Completeness

| Check | Result |
|-------|--------|
| `.settings` in corpus_v1 | 540 |
| manifest.csv data rows | 540 |
| Scenario bases | 60 |
| Traffic profiles | 12 |
| output_metrics.csv | 720 |
| spatial_occupancy_metrics.csv | 720 |
| indirect_features_diego.csv | 720 |
| message_creation_time_summary.csv | 720 |
| useful_simulation_time_metrics.csv | 720 |
| Null delivery_ratio | 168 |
| Zero delivery_ratio | 34 |
| Zero total_encounters | 24 |

## Problem distribution

### By family

| family | ok | valido_extremo | pendiente_revision | configuracion_sospechosa | error_probable |
|--------|---:|---:|---:|---:|---:|
| `01_urban` | 0 | 0 | 0 | 0 | 84 |
| `02_campus` | 56 | 9 | 1 | 6 | 0 |
| `03_vehicles` | 0 | 0 | 0 | 0 | 60 |
| `04_rural` | 44 | 40 | 0 | 48 | 12 |
| `05_disaster` | 34 | 16 | 0 | 46 | 12 |
| `06_social` | 57 | 9 | 0 | 6 | 0 |
| `07_` | 0 | 30 | 0 | 0 | 0 |

### By traffic profile

| TP | ok | valido_extremo | pendiente_revision | configuracion_sospechosa | error_probable |
|----|---:|---:|---:|---:|---:|
| `TP01` | 18 | 17 | 0 | 11 | 14 |
| `TP02` | 18 | 3 | 0 | 10 | 14 |
| `TP03` | 20 | 2 | 0 | 9 | 14 |
| `TP04` | 12 | 13 | 0 | 6 | 14 |
| `TP05` | 16 | 13 | 0 | 2 | 14 |
| `TP06` | 17 | 2 | 0 | 12 | 14 |
| `TP07` | 18 | 2 | 0 | 11 | 14 |
| `TP08` | 13 | 2 | 0 | 16 | 14 |
| `TP09` | 11 | 12 | 0 | 8 | 14 |
| `TP10` | 17 | 21 | 0 | 8 | 14 |
| `TP11` | 18 | 8 | 0 | 5 | 14 |
| `TP12` | 13 | 9 | 1 | 8 | 14 |

### error_probable scenarios

- `U1_CBD_Commuting_HelsinkiDowntown__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `U1_CBD_Commuting_HelsinkiDowntown__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `U1_CBD_Commuting_HelsinkiDowntown__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `U1_CBD_Commuting_HelsinkiDowntown__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `U1_CBD_Commuting_HelsinkiDowntown__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `U1_CBD_Commuting_HelsinkiDowntown__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `U1_CBD_Commuting_HelsinkiDowntown__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `U1_CBD_Commuting_HelsinkiDowntown__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `U1_CBD_Commuting_HelsinkiDowntown__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `U1_CBD_Commuting_HelsinkiDowntown__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `U1_CBD_Commuting_HelsinkiDowntown__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `U1_CBD_Commuting_HelsinkiDowntown__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)
- `U2_SparseSuburb_HelsinkiDowntown__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `U2_SparseSuburb_HelsinkiDowntown__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `U2_SparseSuburb_HelsinkiDowntown__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `U2_SparseSuburb_HelsinkiDowntown__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `U2_SparseSuburb_HelsinkiDowntown__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `U2_SparseSuburb_HelsinkiDowntown__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `U2_SparseSuburb_HelsinkiDowntown__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `U2_SparseSuburb_HelsinkiDowntown__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `U2_SparseSuburb_HelsinkiDowntown__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `U2_SparseSuburb_HelsinkiDowntown__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `U2_SparseSuburb_HelsinkiDowntown__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `U2_SparseSuburb_HelsinkiDowntown__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)
- `U3_MicroMobility_HelsinkiDowntown__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `U3_MicroMobility_HelsinkiDowntown__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `U3_MicroMobility_HelsinkiDowntown__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `U3_MicroMobility_HelsinkiDowntown__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `U3_MicroMobility_HelsinkiDowntown__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `U3_MicroMobility_HelsinkiDowntown__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `U3_MicroMobility_HelsinkiDowntown__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `U3_MicroMobility_HelsinkiDowntown__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `U3_MicroMobility_HelsinkiDowntown__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `U3_MicroMobility_HelsinkiDowntown__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `U3_MicroMobility_HelsinkiDowntown__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `U3_MicroMobility_HelsinkiDowntown__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)
- `U4_CongestionHotspot_HelsinkiDowntown__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `U4_CongestionHotspot_HelsinkiDowntown__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `U4_CongestionHotspot_HelsinkiDowntown__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `U4_CongestionHotspot_HelsinkiDowntown__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `U4_CongestionHotspot_HelsinkiDowntown__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `U4_CongestionHotspot_HelsinkiDowntown__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `U4_CongestionHotspot_HelsinkiDowntown__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `U4_CongestionHotspot_HelsinkiDowntown__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `U4_CongestionHotspot_HelsinkiDowntown__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `U4_CongestionHotspot_HelsinkiDowntown__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `U4_CongestionHotspot_HelsinkiDowntown__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `U4_CongestionHotspot_HelsinkiDowntown__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)
- `U5_WorkdayShort_HelsinkiDowntown__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `U5_WorkdayShort_HelsinkiDowntown__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `U5_WorkdayShort_HelsinkiDowntown__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `U5_WorkdayShort_HelsinkiDowntown__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `U5_WorkdayShort_HelsinkiDowntown__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `U5_WorkdayShort_HelsinkiDowntown__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `U5_WorkdayShort_HelsinkiDowntown__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `U5_WorkdayShort_HelsinkiDowntown__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `U5_WorkdayShort_HelsinkiDowntown__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `U5_WorkdayShort_HelsinkiDowntown__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `U5_WorkdayShort_HelsinkiDowntown__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `U5_WorkdayShort_HelsinkiDowntown__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)
- `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `U6_OfficeWaitHeavyTail_HelsinkiDowntown__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)
- `U7_HighTimeVariance_HelsinkiDowntown__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `U7_HighTimeVariance_HelsinkiDowntown__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `U7_HighTimeVariance_HelsinkiDowntown__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `U7_HighTimeVariance_HelsinkiDowntown__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `U7_HighTimeVariance_HelsinkiDowntown__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `U7_HighTimeVariance_HelsinkiDowntown__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `U7_HighTimeVariance_HelsinkiDowntown__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `U7_HighTimeVariance_HelsinkiDowntown__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `U7_HighTimeVariance_HelsinkiDowntown__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `U7_HighTimeVariance_HelsinkiDowntown__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `U7_HighTimeVariance_HelsinkiDowntown__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `U7_HighTimeVariance_HelsinkiDowntown__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)
- `V1_TaxiLow_ManhattanMidtownGrid__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `V1_TaxiLow_ManhattanMidtownGrid__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `V1_TaxiLow_ManhattanMidtownGrid__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `V1_TaxiLow_ManhattanMidtownGrid__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `V1_TaxiLow_ManhattanMidtownGrid__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `V1_TaxiLow_ManhattanMidtownGrid__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `V1_TaxiLow_ManhattanMidtownGrid__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `V1_TaxiLow_ManhattanMidtownGrid__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `V1_TaxiLow_ManhattanMidtownGrid__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `V1_TaxiLow_ManhattanMidtownGrid__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `V1_TaxiLow_ManhattanMidtownGrid__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `V1_TaxiLow_ManhattanMidtownGrid__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)
- `V2_TaxiHigh_ManhattanMidtownGrid__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `V2_TaxiHigh_ManhattanMidtownGrid__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `V2_TaxiHigh_ManhattanMidtownGrid__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `V2_TaxiHigh_ManhattanMidtownGrid__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `V2_TaxiHigh_ManhattanMidtownGrid__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `V2_TaxiHigh_ManhattanMidtownGrid__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `V2_TaxiHigh_ManhattanMidtownGrid__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `V2_TaxiHigh_ManhattanMidtownGrid__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `V2_TaxiHigh_ManhattanMidtownGrid__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `V2_TaxiHigh_ManhattanMidtownGrid__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `V2_TaxiHigh_ManhattanMidtownGrid__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `V2_TaxiHigh_ManhattanMidtownGrid__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)
- `V3_BusOnlyCarriers_ManhattanMidtownGrid__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `V3_BusOnlyCarriers_ManhattanMidtownGrid__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `V3_BusOnlyCarriers_ManhattanMidtownGrid__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `V3_BusOnlyCarriers_ManhattanMidtownGrid__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `V3_BusOnlyCarriers_ManhattanMidtownGrid__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `V3_BusOnlyCarriers_ManhattanMidtownGrid__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `V3_BusOnlyCarriers_ManhattanMidtownGrid__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `V3_BusOnlyCarriers_ManhattanMidtownGrid__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `V3_BusOnlyCarriers_ManhattanMidtownGrid__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `V3_BusOnlyCarriers_ManhattanMidtownGrid__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `V3_BusOnlyCarriers_ManhattanMidtownGrid__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `V3_BusOnlyCarriers_ManhattanMidtownGrid__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)
- `V4_CarOwnership_0_ManhattanMidtownGrid__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `V4_CarOwnership_0_ManhattanMidtownGrid__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `V4_CarOwnership_0_ManhattanMidtownGrid__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `V4_CarOwnership_0_ManhattanMidtownGrid__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `V4_CarOwnership_0_ManhattanMidtownGrid__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `V4_CarOwnership_0_ManhattanMidtownGrid__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `V4_CarOwnership_0_ManhattanMidtownGrid__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `V4_CarOwnership_0_ManhattanMidtownGrid__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `V4_CarOwnership_0_ManhattanMidtownGrid__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `V4_CarOwnership_0_ManhattanMidtownGrid__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `V4_CarOwnership_0_ManhattanMidtownGrid__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `V4_CarOwnership_0_ManhattanMidtownGrid__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)
- `V5_CarOwnership_100_ManhattanMidtownGrid__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `V5_CarOwnership_100_ManhattanMidtownGrid__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `V5_CarOwnership_100_ManhattanMidtownGrid__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `V5_CarOwnership_100_ManhattanMidtownGrid__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `V5_CarOwnership_100_ManhattanMidtownGrid__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `V5_CarOwnership_100_ManhattanMidtownGrid__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `V5_CarOwnership_100_ManhattanMidtownGrid__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `V5_CarOwnership_100_ManhattanMidtownGrid__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `V5_CarOwnership_100_ManhattanMidtownGrid__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `V5_CarOwnership_100_ManhattanMidtownGrid__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `V5_CarOwnership_100_ManhattanMidtownGrid__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `V5_CarOwnership_100_ManhattanMidtownGrid__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)
- `R4_ParkRangers_NuuksioSparseTrails__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `R4_ParkRangers_NuuksioSparseTrails__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `R4_ParkRangers_NuuksioSparseTrails__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `R4_ParkRangers_NuuksioSparseTrails__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `R4_ParkRangers_NuuksioSparseTrails__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `R4_ParkRangers_NuuksioSparseTrails__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `R4_ParkRangers_NuuksioSparseTrails__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `R4_ParkRangers_NuuksioSparseTrails__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `R4_ParkRangers_NuuksioSparseTrails__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `R4_ParkRangers_NuuksioSparseTrails__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `R4_ParkRangers_NuuksioSparseTrails__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `R4_ParkRangers_NuuksioSparseTrails__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)
- `D5_UAVMule_FastRoute_HelsinkiDisrupted__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `D5_UAVMule_FastRoute_HelsinkiDisrupted__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `D5_UAVMule_FastRoute_HelsinkiDisrupted__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `D5_UAVMule_FastRoute_HelsinkiDisrupted__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `D5_UAVMule_FastRoute_HelsinkiDisrupted__TP05_CriticalTTL` — missing delivery_ratio (simulation report incomplete or absent)
- `D5_UAVMule_FastRoute_HelsinkiDisrupted__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `D5_UAVMule_FastRoute_HelsinkiDisrupted__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `D5_UAVMule_FastRoute_HelsinkiDisrupted__TP08_HubTarget` — missing delivery_ratio (simulation report incomplete or absent)
- `D5_UAVMule_FastRoute_HelsinkiDisrupted__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `D5_UAVMule_FastRoute_HelsinkiDisrupted__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `D5_UAVMule_FastRoute_HelsinkiDisrupted__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `D5_UAVMule_FastRoute_HelsinkiDisrupted__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)

## Methodological answers

### 1. Is corpus_v1 sufficiently complete to use as a benchmark?

**Yes for configuration/diversity benchmarking** — all 720 `.settings`, manifest rows, feature matrices, output metrics, spatial metrics, and auxiliary CSVs are present (720/720).

**Almost ready for routing protocol comparison** — two scenarios lack output metrics (`error_probable`, see CSV); message analysis window (policy B) is not yet enforced in the pipeline.

### 2. Which scenarios should be kept as valid extremes?

- **TP12** cross-group partition controls (`include_control`)
- **TP04 / TP05 / TP10** stress load and CriticalTTL tiers (`include_stress`)
- **R10 / R11** and disconnected bases with `ZERO_CONTACTS` (`include_control` / `document_as_extreme`)
- **07_** family (stress/control laboratory)
- **MAP_UNDERUSED** WDM scenarios (~8–10% world grid coverage on roads — not a simulation failure)

Count `valido_extremo`: **104** scenarios.

### 3. Which scenarios need review before the paper?

- **168** scenarios with missing outputs → re-simulate
- **106** suspicious configs (zero delivery with contacts, etc.)
- **1** pending revision (P0/P1 map, worldSize, latency window)
- Urban WDM **MAP_TOO_LARGE / MAP_UNDERUSED** — document in Methods, optional worldSize crop

### 4. Which problems do NOT block the paper?

- Diversity metrics frozen in `RESULTADOS_ACTUALES.md` (720 scenarios)
- Low spatial *world* coverage on map-based mobility (roads vs rectangle world)
- Stress-tier extremes reported separately from main claims
- 24 disconnected control scenarios (documented in tp_validation_report)

### 5. Which problems COULD block protocol comparison?

- **Message analysis window not implemented** — compare protocols only after policy B in pipeline
- **Missing output metrics** (2 scenarios) — exclude or re-simulate before ranking
- **Mixing P0 scenarios in main split** without stratification (use `manifest_revision.csv` benchmark_split)
- **TP05 zero-delivery** in aggregate main-tier ranking without stress tier separation

## Recommended splits

Align protocol runs with `corpus_v1/manifest_revision.csv`:

- **main:** TP01–TP08 on viable bases; exclude `error_probable` and `configuracion_sospechosa`
- **stress:** TP09–TP11, TP04–TP06 load, all `07_`
- **control:** TP12 partition, disconnected extremes

## Next steps

1. Re-simulate `S1_StrongCommunities_SeparateClusters__TP03_ManySmall` and `__TP11_ManyToOne`
2. Implement TTL-aware message window in `output_metrics` pipeline
3. Filter validation CSV when exporting paper tables (`validation_status == ok` for main tier)
4. Re-run after settings revision: `validate_corpus_benchmark.py`

## Artifacts

- Validation table: [`data/corpus_benchmark_validation.csv`](../data/corpus_benchmark_validation.csv)
- Diagnosis: [`data/scenario_diagnosis.csv`](../data/scenario_diagnosis.csv)
- TP validation: [`tp_validation_report.md`](tp_validation_report.md)
- Frozen diversity: [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)