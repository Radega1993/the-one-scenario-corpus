# Plan de revisión corpus_v2 (in-place)

Generado: 2026-05-20 11:08 UTC

> **Alcance:** propuesta de modificación sobre `scenarios/corpus_v2/` sin crear `corpus_v3`.
> Los artefactos `corpus_v3_*` quedan como histórico de auditoría.

## Resumen

- Filas tabla priorizada: **996** (de **720** escenarios)
- Bases: **60**
- Bases benchmark **main**: **40**
- Bases **stress**: **18**
- Bases **control**: **2**
- Cobertura espacial en diagnóstico: **98** escenarios con métricas (98 grids en `reports/`)

## Taxonomía de benchmark

| Split | Bases | TP típicos |
|-------|------:|------------|
| main | 40 | TP01–TP08 en bases viables |
| stress | 18 | TP04–06,09–11 + familia 07_traffic |
| control | 2 | TP12 + R1/R11 extremos |

## 1. Benchmark principal

Bases con movilidad viable; TP01–TP08 tras recorte de mapa donde aplique.

```
U1_CBD_Commuting_HelsinkiMedium, U2_SparseSuburb_HelsinkiMedium, U3_MicroMobility_HelsinkiMedium, U4_CongestionHotspot_HelsinkiMedium, U5_WorkdayShort_HelsinkiMedium, U6_OfficeWaitHeavyTail_HelsinkiMedium, U7_HighTimeVariance_HelsinkiMedium, C1_Campus_ClassChange, C2_ExamDay_LongStays, C3_Hackathon_24h, C4_Stadium_IngressEgress, C5_Library_Quiet, C6_EmergencyDrill_Evacuation, V1_TaxiLow_HelsinkiMedium, V2_TaxiHigh_HelsinkiMedium, V3_BusOnlyCarriers_HelsinkiMedium, V4_CarOwnership_0_HelsinkiMedium, V5_CarOwnership_100_HelsinkiMedium, R10_TinyRange_5m, R12_SpeedExtremeHigh, R2_VillagesTrails_ThreeClusters, R4_ParkRangers_HelsinkiMedium, R5_MountainRescue, R6_SparseLongRange, R9_ExtremeRange_200m …
```

## 2. Benchmark stress

```
R3_WildlifeTracking, R7_SparseTinyBuffer, R8_IntermittentPower, T10_HighRateLowSpeed_Congestion, T11_TTL_1min, T12_TTL_Infinite_Buffer200M, T13_Buffer_256k, T14_Buffer_200M, T15_TransmitSpeed_256k, T1_ManySmallMsgs_HighRate, T2_FewHugeMsgs_LowRate, T3_MixedBimodal_SmallAndLarge, T4_VeryShortTtl_5to10min, T5_VeryLongTtl_6to24h, T6_UniformSources_RandomFromTo, T7_TargetedToHubs_FewDestinations, T8_BurstTraffic_TimeWindows, T9_BufferStress_SmallBufferHighTraffic
```

## 3. Benchmark extremo / control

```
R11_SpeedExtremeLow, R1_Rural_RandomWaypoint
```

## 4. Cambiar mapa (worldSize / dataset)

| scenario_base | change_map |
|---------------|------------|
| `U1_CBD_Commuting_HelsinkiMedium` | recortar_worldSize |
| `U2_SparseSuburb_HelsinkiMedium` | recortar_worldSize|opcional_Manhattan |
| `U3_MicroMobility_HelsinkiMedium` | recortar_worldSize |
| `U4_CongestionHotspot_HelsinkiMedium` | recortar_worldSize|opcional_Manhattan |
| `U5_WorkdayShort_HelsinkiMedium` | recortar_worldSize |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium` | recortar_worldSize |
| `U7_HighTimeVariance_HelsinkiMedium` | recortar_worldSize |
| `V2_TaxiHigh_HelsinkiMedium` | recortar_worldSize |
| `V4_CarOwnership_0_HelsinkiMedium` | recortar_worldSize |
| `V5_CarOwnership_100_HelsinkiMedium` | recortar_worldSize |
| `D5_UAVMule_FastRoute_HelsinkiMedium` | recortar_worldSize |

## 5. Cambiar movilidad

| scenario_base |
|---------------|
| `R11_SpeedExtremeLow` |
| `R1_Rural_RandomWaypoint` |
| `D6_ShortTtlCritical_5to10min` |
| `D7_HighLoad_TrafficStorm` |
| `S1_StrongCommunities_SeparateClusters` |

## 6. Ajustar TP (overlay Events/msgTtl)

| scenario_base | change_tp |
|---------------|-----------|
| `U1_CBD_Commuting_HelsinkiMedium` | si_TP04_06 |
| `U2_SparseSuburb_HelsinkiMedium` | si_TP04_06 |
| `U3_MicroMobility_HelsinkiMedium` | si_TP04_06 |
| `U4_CongestionHotspot_HelsinkiMedium` | si_TP04_06 |
| `U5_WorkdayShort_HelsinkiMedium` | si_TP04_06 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium` | si_TP04_06 |
| `U7_HighTimeVariance_HelsinkiMedium` | si_TP04_06 |
| `C1_Campus_ClassChange` | si_TP04_06 |
| `C2_ExamDay_LongStays` | si_TP04_06 |
| `C3_Hackathon_24h` | si_TP04_06 |
| `C4_Stadium_IngressEgress` | si_TP04_06 |
| `C6_EmergencyDrill_Evacuation` | si_TP04_06 |
| `V2_TaxiHigh_HelsinkiMedium` | si_TP04_06 |
| `V4_CarOwnership_0_HelsinkiMedium` | si_TP04_06 |
| `R10_TinyRange_5m` | si |
| `R11_SpeedExtremeLow` | si |
| `R1_Rural_RandomWaypoint` | si |
| `R3_WildlifeTracking` | si |
| `R5_MountainRescue` | si |
| `R7_SparseTinyBuffer` | si |
| `R8_IntermittentPower` | si |
| `R9_ExtremeRange_200m` | si_TP04_06 |
| `D1_ShelterHotspots_Clusters` | si_TP04_06 |
| `D2_PartitionedCity_MuleBridge` | si_TP04_06 |
| `D3_Aftershock_ErraticMobility` | si |
| `D5_UAVMule_FastRoute_HelsinkiMedium` | si |
| `D6_ShortTtlCritical_5to10min` | si_TP04_06 |
| `D7_HighLoad_TrafficStorm` | si_TP04_06 |
| `D8_InfrastructureReturns_BackboneLinks` | si_TP04_06 |
| `D9_Critical_1minTTL` | si_TP04_06 |
| `S1_StrongCommunities_SeparateClusters` | si_TP04_06 |
| `S3_PeriodicMeetings_RegularRhythm` | si_TP04_06 |
| `S6_FamilyGroups_SmallPersistent` | si_TP04_06 |
| `T10_HighRateLowSpeed_Congestion` | si_TP04_06 |
| `T12_TTL_Infinite_Buffer200M` | si_TP04_06 |
| `T13_Buffer_256k` | si |
| `T3_MixedBimodal_SmallAndLarge` | si |
| `T4_VeryShortTtl_5to10min` | si |
| `T6_UniformSources_RandomFromTo` | si |
| `T8_BurstTraffic_TimeWindows` | si_TP04_06 |
| `T9_BufferStress_SmallBufferHighTraffic` | si |

## 7. Mantener sin cambios

| scenario_base |
|---------------|
| `C5_Library_Quiet` |
| `V1_TaxiLow_HelsinkiMedium` |
| `V3_BusOnlyCarriers_HelsinkiMedium` |
| `V5_CarOwnership_100_HelsinkiMedium` |
| `R12_SpeedExtremeHigh` |
| `R2_VillagesTrails_ThreeClusters` |
| `R4_ParkRangers_HelsinkiMedium` |
| `R6_SparseLongRange` |
| `D4_MedicalTriage_TwoClasses` |
| `S2_WeakCommunities_HighMixing` |
| `S4_RandomMixing_NoHotspots` |
| `S5_TwoLayer_StudentsStaff` |
| `T15_TransmitSpeed_256k` |

## Muestra tabla priorizada (P0)

| escenario | problema | evidencia | decision |
|-----------|----------|-----------|----------|
| `U4_CongestionHotspot_HelsinkiMedium__TP05_CriticalTTL` | ZERO_DELIVERY | delivery=0; overhead=na; drops=1.3435; encounters=1258; cov_… | modificar |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP05_CriticalTTL` | ZERO_DELIVERY | delivery=0; overhead=na; drops=1.3923; encounters=1291; cov_… | modificar |
| `R10_TinyRange_5m__TP02_LowLoad` | ZERO_DELIVERY | delivery=0; overhead=na; drops=0; encounters=5; std_base=0.0… | modificar |
| `R10_TinyRange_5m__TP04_FewLarge` | ZERO_DELIVERY | delivery=0; overhead=na; drops=0; encounters=5; std_base=0.0… | modificar |
| `R10_TinyRange_5m__TP05_CriticalTTL` | ZERO_DELIVERY | delivery=0; overhead=na; drops=0.9959; encounters=5; std_bas… | modificar |
| `R11_SpeedExtremeLow__TP01_Baseline` | ZERO_DELIVERY | delivery=0; overhead=na; drops=0; encounters=; std_base=0 | excluir |
| `R11_SpeedExtremeLow__TP02_LowLoad` | ZERO_DELIVERY | delivery=0; overhead=na; drops=0; encounters=; std_base=0 | excluir |
| `R11_SpeedExtremeLow__TP03_ManySmall` | ZERO_DELIVERY | delivery=0; overhead=na; drops=0; encounters=; std_base=0 | excluir |
| `R11_SpeedExtremeLow__TP04_FewLarge` | ZERO_DELIVERY | delivery=0; overhead=na; drops=0; encounters=; std_base=0 | excluir |
| `R11_SpeedExtremeLow__TP05_CriticalTTL` | ZERO_DELIVERY | delivery=0; overhead=na; drops=0.9959; encounters=; std_base… | excluir |
| `R11_SpeedExtremeLow__TP06_OneToMany` | ZERO_DELIVERY | delivery=0; overhead=na; drops=0.0794; encounters=; std_base… | excluir |
| `R11_SpeedExtremeLow__TP07_BurstWindow` | ZERO_DELIVERY | delivery=0; overhead=na; drops=0; encounters=; std_base=0 | excluir |
| `R11_SpeedExtremeLow__TP08_HubTarget` | ZERO_DELIVERY | delivery=0; overhead=na; drops=0; encounters=; std_base=0 | excluir |
| `R11_SpeedExtremeLow__TP09_Bimodal` | ZERO_DELIVERY | delivery=0; overhead=na; drops=0; encounters=; std_base=0 | excluir |
| `R11_SpeedExtremeLow__TP10_Storm` | ZERO_DELIVERY | delivery=0; overhead=na; drops=0.9186; encounters=; std_base… | excluir |

## Artefactos

- Tabla completa: `data/corpus_v2_revision_prioritized.csv`
- Resumen por base: `data/corpus_v2_revision_summary.csv`
- Diagnóstico fuente: `data/scenario_diagnosis.csv`

## Próximo paso (tras aprobación)

1. Aplicar cambios en `.settings` según `revision_action` / `change_*`.
2. Añadir `benchmark_split` a `manifest.csv` o sidecar `manifest_revision.csv`.
3. Re-simular y re-ejecutar `diagnose_scenarios.py` + este script.
