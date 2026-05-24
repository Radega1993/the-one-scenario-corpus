# Mobility realism review

Per **scenario_base** (mobility from corpus_v1, unchanged in v2 except TP overlays).

## Summary by family

### `01_urban` (7 bases)

| base | movement | mean delivery | P0 count |
|------|----------|--------------:|---------:|
| `U1_CBD_Commuting_HelsinkiMedium` | `G1:BusMovement|G2:WorkingDayMovement` | 0.376 | 6 |
| `U2_SparseSuburb_HelsinkiMedium` | `G1:BusMovement|G2:WorkingDayMovement` | 0.261 | 1 |
| `U3_MicroMobility_HelsinkiMedium` | `G1:BusMovement|G2:WorkingDayMovement` | 0.206 | 11 |
| `U4_CongestionHotspot_HelsinkiMedium` | `G1:BusMovement|G2:WorkingDayMovement` | 0.290 | 6 |
| `U5_WorkdayShort_HelsinkiMedium` | `G1:BusMovement|G2:WorkingDayMovement` | 0.231 | 2 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium` | `G1:BusMovement|G2:WorkingDayMovement` | 0.264 | 3 |
| `U7_HighTimeVariance_HelsinkiMedium` | `G1:BusMovement|G2:WorkingDayMovement` | 0.356 | 4 |

### `02_campus` (6 bases)

| base | movement | mean delivery | P0 count |
|------|----------|--------------:|---------:|
| `C1_Campus_ClassChange` | `G1:RandomWaypoint` | 0.801 | 3 |
| `C2_ExamDay_LongStays` | `G1:RandomWaypoint` | 0.663 | 3 |
| `C3_Hackathon_24h` | `G1:RandomWaypoint` | 0.559 | 7 |
| `C4_Stadium_IngressEgress` | `G1:RandomWaypoint` | 0.691 | 2 |
| `C5_Library_Quiet` | `G1:RandomWaypoint` | 0.489 | 0 |
| `C6_EmergencyDrill_Evacuation` | `G1:LinearMovement` | 0.499 | 1 |

### `03_vehicles` (5 bases)

| base | movement | mean delivery | P0 count |
|------|----------|--------------:|---------:|
| `V1_TaxiLow_HelsinkiMedium` | `G1:MapRouteMovement` | 0.687 | 0 |
| `V2_TaxiHigh_HelsinkiMedium` | `G1:MapRouteMovement` | 0.883 | 4 |
| `V3_BusOnlyCarriers_HelsinkiMedium` | `G1:BusMovement|G2:BusMovement` | 0.257 | 0 |
| `V4_CarOwnership_0_HelsinkiMedium` | `G1:BusMovement|G2:WorkingDayMovement` | 0.372 | 6 |
| `V5_CarOwnership_100_HelsinkiMedium` | `G1:BusMovement|G2:WorkingDayMovement` | 0.293 | 0 |

### `04_rural` (12 bases)

| base | movement | mean delivery | P0 count |
|------|----------|--------------:|---------:|
| `R10_TinyRange_5m` | `G1:RandomWaypoint` | 0.011 | 3 |
| `R11_SpeedExtremeLow` | `G1:RandomWaypoint` | 0.000 | 12 |
| `R12_SpeedExtremeHigh` | `G1:RandomWaypoint` | 0.669 | 0 |
| `R1_Rural_RandomWaypoint` | `G1:RandomWaypoint` | 0.000 | 12 |
| `R2_VillagesTrails_ThreeClusters` | `G1:ClusterMovement|G2:ClusterMovement|G3:ClusterMovement` | 0.173 | 0 |
| `R3_WildlifeTracking` | `G1:RandomWaypoint` | 0.003 | 5 |
| `R4_ParkRangers_HelsinkiMedium` | `G1:MapRouteMovement` | 0.473 | 0 |
| `R5_MountainRescue` | `G1:RandomWaypoint` | 0.011 | 3 |
| `R6_SparseLongRange` | `G1:RandomWaypoint` | 0.052 | 0 |
| `R7_SparseTinyBuffer` | `G1:RandomWaypoint` | 0.005 | 5 |
| `R8_IntermittentPower` | `G1:RandomWaypoint` | 0.012 | 2 |
| `R9_ExtremeRange_200m` | `G1:RandomWaypoint` | 0.663 | 3 |

### `05_disaster` (9 bases)

| base | movement | mean delivery | P0 count |
|------|----------|--------------:|---------:|
| `D1_ShelterHotspots_Clusters` | `G1:ClusterMovement|G2:ClusterMovement|G3:ClusterMovement|G4:` | 0.272 | 5 |
| `D2_PartitionedCity_MuleBridge` | `G1:ClusterMovement|G2:ClusterMovement|G3:RandomWaypoint` | 0.355 | 2 |
| `D3_Aftershock_ErraticMobility` | `G1:RandomWaypoint` | 0.024 | 1 |
| `D4_MedicalTriage_TwoClasses` | `G1:RandomWaypoint|G2:RandomWaypoint` | 0.079 | 1 |
| `D5_UAVMule_FastRoute_HelsinkiMedium` | `G1:MapRouteMovement|G2:MapRouteMovement` | 0.006 | 5 |
| `D6_ShortTtlCritical_5to10min` | `G1:RandomWaypoint` | 0.005 | 9 |
| `D7_HighLoad_TrafficStorm` | `G1:RandomWaypoint` | 0.006 | 7 |
| `D8_InfrastructureReturns_BackboneLinks` | `G1:ClusterMovement|G2:ClusterMovement` | 0.363 | 3 |
| `D9_Critical_1minTTL` | `G1:RandomWaypoint` | 0.023 | 3 |

### `06_social` (6 bases)

| base | movement | mean delivery | P0 count |
|------|----------|--------------:|---------:|
| `S1_StrongCommunities_SeparateClusters` | `G1:ClusterMovement|G2:ClusterMovement|G3:ClusterMovement|G4:` | 0.182 | 9 |
| `S2_WeakCommunities_HighMixing` | `G1:RandomWaypoint` | 0.434 | 0 |
| `S3_PeriodicMeetings_RegularRhythm` | `G1:RandomWaypoint` | 0.119 | 1 |
| `S4_RandomMixing_NoHotspots` | `G1:RandomWaypoint` | 0.043 | 1 |
| `S5_TwoLayer_StudentsStaff` | `G1:RandomWaypoint|G2:RandomWaypoint` | 0.245 | 1 |
| `S6_FamilyGroups_SmallPersistent` | `G1:ClusterMovement|G2:ClusterMovement|G3:ClusterMovement|G4:` | 0.050 | 1 |

### `07_traffic` (15 bases)

| base | movement | mean delivery | P0 count |
|------|----------|--------------:|---------:|
| `T10_HighRateLowSpeed_Congestion` | `G1:RandomWaypoint` | 0.021 | 2 |
| `T11_TTL_1min` | `G1:RandomWaypoint` | 0.449 | 1 |
| `T12_TTL_Infinite_Buffer200M` | `G1:RandomWaypoint` | 0.032 | 2 |
| `T13_Buffer_256k` | `G1:RandomWaypoint` | 0.004 | 3 |
| `T14_Buffer_200M` | `G1:RandomWaypoint` | 0.149 | 1 |
| `T15_TransmitSpeed_256k` | `G1:RandomWaypoint` | 0.190 | 0 |
| `T1_ManySmallMsgs_HighRate` | `G1:RandomWaypoint` | 0.050 | 1 |
| `T2_FewHugeMsgs_LowRate` | `G1:RandomWaypoint` | 0.030 | 3 |
| `T3_MixedBimodal_SmallAndLarge` | `G1:RandomWaypoint` | 0.034 | 1 |
| `T4_VeryShortTtl_5to10min` | `G1:RandomWaypoint` | 0.003 | 5 |
| `T5_VeryLongTtl_6to24h` | `G1:RandomWaypoint` | 0.103 | 1 |
| `T6_UniformSources_RandomFromTo` | `G1:RandomWaypoint` | 0.029 | 1 |

## Findings

- **WorkingDayMovement + HelsinkiMedium** dominates urban/vehicle/disaster bases; spatial coverage ~8–10% of world is expected but flags **MAP_UNDERUSED** vs full grid.
- **Campus** bases use MapRoute/MovementSwitch; fewer map-dependency issues but **TP04_FewLarge** drives extreme overhead.
- **Rural RWP** bases are the main non-Helsinki mobility diversity in v1; recommend **MAP06** cropped synthetic worlds for v3 main benchmark.
- v3 should **decouple** mobility template, map profile, and TP overlay (see `corpus_v3_design.md`).
