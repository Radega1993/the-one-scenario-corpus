# Tiempo útil de simulación — informe metodológico

Generado: 2026-05-20 12:41 UTC

## 1. Fuentes de datos auditadas

| Fuente | Disponible en pipeline actual | Uso en este informe |
|--------|------------------------------|---------------------|
| `ConnectivityONEReport` | Sí (720/720 en corpus_v1 con Diego17 overrides) | **Principal** — traza `CONN up/down` |
| `MessageStatsReport` | Sí | No usado aquí (entrega, no exploración) |
| `ContactTimesReport` / `TotalEncountersReport` | Sí | Fallback posible; no necesario con traza ONE |
| Logs de posiciones (`MovementReport`, GPS) | **No** | Ocupación espacial vía **cobertura de pares** en grafo de contactos |

## 2. Definición de tiempo útil

En DTN, simular "hasta el infinito" haría converger muchas entregas; el `Scenario.endTime` debe ser **suficiente** para observar exploración de la red oportunista y un **cola de entrega**, sin ser arbitrariamente largo.

### Métricas derivadas de conectividad

| Métrica | Definición |
|---------|------------|
| `first_contact_time` | Primer evento `CONN … up` en la traza |
| `last_contact_time` | Último evento de la traza (up o down) |
| `total_encounters` | Número de eventos `CONN up` |
| `contact_time_per_min` | `total_encounters / (end_time / 60)` |
| `ratio_contact_nodes` | Grado medio normalizado en grafo de contactos (trace) |
| `pct_nodes_ever_contacted` | % de hosts configurados con ≥1 contacto |
| `time_to_Xpct_contact_nodes` | Primer instante en que X% de hosts han tenido su primer contacto |
| `pair_coverage_final_pct` | Pares únicos observados / pares posibles (proxy espacial) |
| `time_to_90pct_pair_coverage` | Instante en que se ha visto el 90% de pares que aparecerán |

### Tiempo útil recomendado

```
useful_time_recommendation = min(end_time, max(time_to_90pct_contact_nodes, last_contact_time))
```

- **`useful_time_ratio`** = `useful_time_recommendation / end_time`
- **`tail_time_ratio`** = `(end_time - useful_time_recommendation) / end_time` — cola reservada a entregas tardías / tráfico ya inyectado

Interpretación:
- **`tail_time_ratio` alto** (p. ej. >0.5): la simulación explora la red pronto y deja mucho margen para entrega (habitual en campus/urbano).
- **`late_exploration`**: el 90% de nodos no se ha contactado hasta >90% de `endTime` — el `endTime` puede ser corto para la movilidad.
- **`disconnected`**: sin eventos `CONN` — no hay tiempo útil oportunista (control negativo, p. ej. `R1`).

## 3. Clasificación por escenario base

| Clase | Criterio | Escenarios base (n) |
|-------|----------|---------------------|
| `disconnected` | `total_encounters = 0` | 4 |
| `marginal_connectivity` | `<15%` nodos contactados | 2 |
| `sufficient_activity` | ≥100 encuentros y ≥30% nodos | 29 |
| `late_exploration` | `t_90` > 90% `end_time` | 2 |
| `early_saturation_long_tail` | `t_90` < 40% `end_time` y cola >50% | 1 |
| `moderate_activity` | resto | 22 |

Bases `late_exploration`: `T2_FewHugeMsgs_LowRate`, `T6_UniformSources_RandomFromTo`.

### Escenarios desconectados o casi desconectados

- `R11_SpeedExtremeLow`
- `R1_Rural_RandomWaypoint`
- `U2_SparseSuburb_Manhattan`
- `U4_CongestionHotspot_Manhattan`

### Escenarios con actividad suficiente (muestra)

- `C1_Campus_ClassChange`: encounters=4219, pct_nodes=100.0%, useful_ratio=1.00
- `C2_ExamDay_LongStays`: encounters=842, pct_nodes=100.0%, useful_ratio=1.00
- `C3_Hackathon_24h`: encounters=550, pct_nodes=100.0%, useful_ratio=1.00
- `C4_Stadium_IngressEgress`: encounters=932, pct_nodes=100.0%, useful_ratio=1.00
- `C5_Library_Quiet`: encounters=229, pct_nodes=100.0%, useful_ratio=1.00
- `D1_ShelterHotspots_Clusters`: encounters=12476, pct_nodes=100.0%, useful_ratio=1.00
- `D2_PartitionedCity_MuleBridge`: encounters=1778, pct_nodes=100.0%, useful_ratio=1.00
- `D8_InfrastructureReturns_BackboneLinks`: encounters=3683, pct_nodes=100.0%, useful_ratio=1.00
- `R12_SpeedExtremeHigh`: encounters=1844, pct_nodes=100.0%, useful_ratio=1.00
- `R2_VillagesTrails_ThreeClusters`: encounters=271, pct_nodes=100.0%, useful_ratio=1.00
- `R9_ExtremeRange_200m`: encounters=594, pct_nodes=100.0%, useful_ratio=1.00
- `S1_StrongCommunities_SeparateClusters`: encounters=8089, pct_nodes=100.0%, useful_ratio=1.00
- `S2_WeakCommunities_HighMixing`: encounters=625, pct_nodes=100.0%, useful_ratio=1.00
- `S3_PeriodicMeetings_RegularRhythm`: encounters=112, pct_nodes=96.0%, useful_ratio=1.00
- `S5_TwoLayer_StudentsStaff`: encounters=308, pct_nodes=100.0%, useful_ratio=1.00
- … (+14 más en CSV)

## 4. Agregados (60 bases, deduplicado por movilidad)

- Media `useful_time_ratio`: **0.882** (mediana 0.994)
- Media `tail_time_ratio` (con contacto): **0.055**

**Nota:** la conectividad depende del escenario base (movilidad), no del perfil TP. En el CSV hay 720 filas (una por simulación); las métricas de contacto son **idénticas por base** salvo variación numérica entre corridas. Para el paper, reportar por **escenario base**.

## 5. Política metodológica propuesta (paper / tesis)

1. **Fijar `Scenario.endTime` por familia** (12 h estándar, ventanas cortas en C4/C6/T4…) como horizonte máximo.
2. **Declarar tiempo útil** como el intervalo `[first_contact_time, useful_time_recommendation]` en el que la red oportunista ha sido explorada al 90% de nodos participantes.
3. **Excluir o etiquetar** escenarios `disconnected` en agregados de protocolo (`R1` como control).
4. **Justificar duración:** mostrar que `tail_time_ratio` deja margen para entrega DTN (no cortar la simulación en el pico de exploración).
5. **No afirmar cobertura espacial real** sin logs GPS; citar `pair_coverage_final_pct` como proxy de diversidad de contactos.

## 6. Limitaciones

- Sin trazas de posición → no hay grid de ocupación real; solo proxy por pares de contacto.
- Contactos abiertos al final de la simulación no suman duración (sesgo conservador en `contact_time_sum`).
- El perfil de tráfico (TP) **no debería** alterar la movilidad; pequeñas diferencias entre corridas TP reflejan no-determinismo de ejecución, no diseño.
- `useful_time_recommendation` no sustituye análisis de entrega: un escenario puede tener cola larga y aun así TTL crítico (TP05).

## 7. Artefactos

- CSV: `data/useful_simulation_time_metrics.csv`
- Script: `compute_useful_simulation_time.py`
- Parser: `lib/connectivity_timeline.py`

## 8. Tabla resumen por escenario base

| Base | end_time | encounters | % nodos | t_90 (s) | useful_ratio | class |
|------|----------|------------|--------:|---------:|-------------:|-------|
| `C1_Campus_ClassChange` | 43200 | 4219 | 100.0 | 746 | 1.00 | sufficient_activity |
| `C2_ExamDay_LongStays` | 43200 | 842 | 100.0 | 2096 | 1.00 | sufficient_activity |
| `C3_Hackathon_24h` | 86400 | 550 | 100.0 | 9169 | 1.00 | sufficient_activity |
| `C4_Stadium_IngressEgress` | 10800 | 932 | 100.0 | 1307 | 1.00 | sufficient_activity |
| `C5_Library_Quiet` | 43200 | 229 | 100.0 | 7352 | 1.00 | sufficient_activity |
| `C6_EmergencyDrill_Evacuation` | 7200 | 3570 | 100.0 | 0 | 0.02 | early_saturation_long_tail |
| `D1_ShelterHotspots_Clusters` | 43200 | 12476 | 100.0 | 498 | 1.00 | sufficient_activity |
| `D2_PartitionedCity_MuleBridge` | 43200 | 1778 | 100.0 | 2296 | 1.00 | sufficient_activity |
| `D3_Aftershock_ErraticMobility` | 43200 | 46 | 79.6 | — | 1.00 | moderate_activity |
| `D4_MedicalTriage_TwoClasses` | 43200 | 66 | 86.0 | — | 0.99 | moderate_activity |
| `D5_UAVMule_FastRoute_HelsinkiMedium` | 43200 | 424 | 9.7 | — | 1.00 | marginal_connectivity |
| `D6_ShortTtlCritical_5to10min` | 14400 | 24 | 55.6 | — | 1.00 | moderate_activity |
| `D7_HighLoad_TrafficStorm` | 14400 | 37 | 67.1 | — | 0.98 | moderate_activity |
| `D8_InfrastructureReturns_BackboneLinks` | 43200 | 3683 | 100.0 | 1179 | 1.00 | sufficient_activity |
| `D9_Critical_1minTTL` | 43200 | 36 | 75.0 | — | 0.99 | moderate_activity |
| `R10_TinyRange_5m` | 43200 | 5 | 28.1 | — | 0.87 | moderate_activity |
| `R11_SpeedExtremeLow` | 43200 | 0 | 0.0 | — | 0.00 | disconnected |
| `R12_SpeedExtremeHigh` | 43200 | 1844 | 100.0 | 942 | 1.00 | sufficient_activity |
| `R1_Rural_RandomWaypoint` | 43200 | 0 | 0.0 | — | 0.00 | disconnected |
| `R2_VillagesTrails_ThreeClusters` | 43200 | 271 | 100.0 | 8344 | 1.00 | sufficient_activity |
| `R3_WildlifeTracking` | 43200 | 1 | 10.0 | — | 0.87 | marginal_connectivity |
| `R4_ParkRangers_HelsinkiMedium` | 43200 | 43 | 100.0 | 22628 | 0.95 | moderate_activity |
| `R5_MountainRescue` | 14400 | 3 | 19.2 | — | 0.79 | moderate_activity |
| `R6_SparseLongRange` | 43200 | 18 | 94.4 | 37343 | 0.87 | moderate_activity |
| `R7_SparseTinyBuffer` | 43200 | 14 | 47.4 | — | 0.96 | moderate_activity |
| `R8_IntermittentPower` | 43200 | 14 | 48.6 | — | 0.72 | moderate_activity |
| `R9_ExtremeRange_200m` | 43200 | 594 | 100.0 | 4070 | 1.00 | sufficient_activity |
| `S1_StrongCommunities_SeparateClusters` | 43200 | 8089 | 100.0 | 567 | 1.00 | sufficient_activity |
| `S2_WeakCommunities_HighMixing` | 43200 | 625 | 100.0 | 6389 | 1.00 | sufficient_activity |
| `S3_PeriodicMeetings_RegularRhythm` | 43200 | 112 | 96.0 | 20378 | 1.00 | sufficient_activity |
| `S4_RandomMixing_NoHotspots` | 43200 | 69 | 91.7 | 30042 | 0.99 | moderate_activity |
| `S5_TwoLayer_StudentsStaff` | 43200 | 308 | 100.0 | 11847 | 1.00 | sufficient_activity |
| `S6_FamilyGroups_SmallPersistent` | 43200 | 4120 | 100.0 | 1567 | 1.00 | sufficient_activity |
| `T10_HighRateLowSpeed_Congestion` | 43200 | 39 | 87.5 | — | 0.93 | moderate_activity |
| `T11_TTL_1min` | 43200 | 305 | 100.0 | 3770 | 0.99 | sufficient_activity |
| `T12_TTL_Infinite_Buffer200M` | 43200 | 35 | 83.3 | — | 0.97 | moderate_activity |
| `T13_Buffer_256k` | 43200 | 9 | 43.3 | — | 0.90 | moderate_activity |
| `T14_Buffer_200M` | 43200 | 110 | 100.0 | 16091 | 1.00 | sufficient_activity |
| `T15_TransmitSpeed_256k` | 43200 | 210 | 100.0 | 9043 | 1.00 | sufficient_activity |
| `T1_ManySmallMsgs_HighRate` | 43200 | 48 | 94.4 | 35799 | 0.87 | moderate_activity |
| `T2_FewHugeMsgs_LowRate` | 43200 | 50 | 93.3 | 40368 | 0.98 | late_exploration |
| `T3_MixedBimodal_SmallAndLarge` | 43200 | 41 | 88.9 | — | 0.98 | moderate_activity |
| `T4_VeryShortTtl_5to10min` | 28800 | 11 | 40.5 | — | 0.60 | moderate_activity |
| `T5_VeryLongTtl_6to24h` | 43200 | 60 | 92.5 | 36306 | 0.97 | moderate_activity |
| `T6_UniformSources_RandomFromTo` | 43200 | 33 | 90.5 | 40588 | 0.94 | late_exploration |
| `T7_TargetedToHubs_FewDestinations` | 43200 | 43 | 86.7 | — | 0.99 | moderate_activity |
| `T8_BurstTraffic_TimeWindows` | 43200 | 45 | 84.4 | — | 0.98 | moderate_activity |
| `T9_BufferStress_SmallBufferHighTraffic` | 43200 | 32 | 70.8 | — | 0.94 | moderate_activity |
| `U1_CBD_Commuting_HelsinkiMedium` | 43200 | 2116 | 85.2 | — | 0.88 | sufficient_activity |
| `U2_SparseSuburb_Manhattan` | 43200 | 0 | 0.0 | — | 0.00 | disconnected |
| `U3_MicroMobility_HelsinkiMedium` | 43200 | 7058 | 78.8 | — | 0.99 | sufficient_activity |
| `U4_CongestionHotspot_Manhattan` | 43200 | 0 | 0.0 | — | 0.00 | disconnected |
| `U5_WorkdayShort_HelsinkiMedium` | 43200 | 1218 | 80.2 | — | 1.00 | sufficient_activity |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium` | 43200 | 1291 | 70.4 | — | 1.00 | sufficient_activity |
| `U7_HighTimeVariance_HelsinkiMedium` | 43200 | 2371 | 76.5 | — | 1.00 | sufficient_activity |
| `V1_TaxiLow_HelsinkiMedium` | 43200 | 449 | 100.0 | 770 | 1.00 | sufficient_activity |
| `V2_TaxiHigh_HelsinkiMedium` | 43200 | 19748 | 100.0 | 73 | 1.00 | sufficient_activity |
| `V3_BusOnlyCarriers_HelsinkiMedium` | 43200 | 562 | 88.9 | — | 1.00 | sufficient_activity |
| `V4_CarOwnership_0_HelsinkiMedium` | 43200 | 3200 | 86.4 | — | 1.00 | sufficient_activity |
| `V5_CarOwnership_100_HelsinkiMedium` | 43200 | 2084 | 79.3 | — | 1.00 | sufficient_activity |