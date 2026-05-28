# Tiempo útil de simulación — informe metodológico

Generado: 2026-05-28 07:55 UTC

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
| `disconnected` | `total_encounters = 0` | 0 |
| `marginal_connectivity` | `<15%` nodos contactados | 0 |
| `sufficient_activity` | ≥100 encuentros y ≥30% nodos | 43 |
| `late_exploration` | `t_90` > 90% `end_time` | 0 |
| `early_saturation_long_tail` | `t_90` < 40% `end_time` y cola >50% | 0 |
| `moderate_activity` | resto | 2 |

### Escenarios con actividad suficiente (muestra)

- `C1_Campus_ClassChange`: encounters=6037, pct_nodes=100.0%, useful_ratio=1.00
- `C2_ExamDay_LongStays`: encounters=1002, pct_nodes=100.0%, useful_ratio=1.00
- `C3_Hackathon_24h`: encounters=717, pct_nodes=100.0%, useful_ratio=1.00
- `C4_Stadium_IngressEgress`: encounters=2280, pct_nodes=100.0%, useful_ratio=1.00
- `C5_Library_Quiet`: encounters=279, pct_nodes=100.0%, useful_ratio=0.99
- `C6_EmergencyDrill_Evacuation`: encounters=5813, pct_nodes=100.0%, useful_ratio=1.00
- `D1_ShelterHotspots_Clusters`: encounters=49583, pct_nodes=100.0%, useful_ratio=1.00
- `D2_PartitionedCity_MuleBridge`: encounters=9553, pct_nodes=100.0%, useful_ratio=1.00
- `D3_Aftershock_ErraticMobility`: encounters=2693, pct_nodes=100.0%, useful_ratio=1.00
- `D4_MedicalTriage_TwoClasses`: encounters=2416, pct_nodes=100.0%, useful_ratio=1.00
- `D5_UAVMule_FastRoute_HelsinkiDisrupted`: encounters=49561, pct_nodes=100.0%, useful_ratio=1.00
- `D6_ShortTtlCritical_5to10min`: encounters=3665, pct_nodes=100.0%, useful_ratio=1.00
- `D7_HighLoad_TrafficStorm`: encounters=6397, pct_nodes=100.0%, useful_ratio=1.00
- `D8_InfrastructureReturns_BackboneLinks`: encounters=18822, pct_nodes=100.0%, useful_ratio=1.00
- `D9_Critical_1minTTL`: encounters=1870, pct_nodes=100.0%, useful_ratio=1.00
- … (+28 más en CSV)

## 4. Agregados (60 bases, deduplicado por movilidad)

- Media `useful_time_ratio`: **0.996** (mediana 1.000)
- Media `tail_time_ratio` (con contacto): **0.004**

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
| `C1_Campus_ClassChange` | 43200 | 6037 | 100.0 | 916 | 1.00 | sufficient_activity |
| `C2_ExamDay_LongStays` | 43200 | 1002 | 100.0 | 2512 | 1.00 | sufficient_activity |
| `C3_Hackathon_24h` | 86400 | 717 | 100.0 | 5388 | 1.00 | sufficient_activity |
| `C4_Stadium_IngressEgress` | 10800 | 2280 | 100.0 | 613 | 1.00 | sufficient_activity |
| `C5_Library_Quiet` | 43200 | 279 | 100.0 | 11901 | 0.99 | sufficient_activity |
| `C6_EmergencyDrill_Evacuation` | 7200 | 5813 | 100.0 | 156 | 1.00 | sufficient_activity |
| `D1_ShelterHotspots_Clusters` | 43200 | 49583 | 100.0 | 123 | 1.00 | sufficient_activity |
| `D2_PartitionedCity_MuleBridge` | 43200 | 9553 | 100.0 | 457 | 1.00 | sufficient_activity |
| `D3_Aftershock_ErraticMobility` | 43200 | 2693 | 100.0 | 1299 | 1.00 | sufficient_activity |
| `D4_MedicalTriage_TwoClasses` | 43200 | 2416 | 100.0 | 1360 | 1.00 | sufficient_activity |
| `D5_UAVMule_FastRoute_HelsinkiDisrupted` | 43200 | 49561 | 100.0 | 135 | 1.00 | sufficient_activity |
| `D6_ShortTtlCritical_5to10min` | 14400 | 3665 | 100.0 | 412 | 1.00 | sufficient_activity |
| `D7_HighLoad_TrafficStorm` | 14400 | 6397 | 100.0 | 309 | 1.00 | sufficient_activity |
| `D8_InfrastructureReturns_BackboneLinks` | 43200 | 18822 | 100.0 | 145 | 1.00 | sufficient_activity |
| `D9_Critical_1minTTL` | 43200 | 1870 | 100.0 | 1144 | 1.00 | sufficient_activity |
| `R10_TinyRange_5m` | 43200 | 678 | 100.0 | 2891 | 1.00 | sufficient_activity |
| `R11_SpeedExtremeLow` | 43200 | 1441 | 100.0 | 816 | 1.00 | sufficient_activity |
| `R12_SpeedExtremeHigh` | 43200 | 35026 | 100.0 | 120 | 1.00 | sufficient_activity |
| `R1_Rural_RandomWaypoint` | 43200 | 2037 | 100.0 | 648 | 1.00 | sufficient_activity |
| `R2_VillagesTrails_ThreeClusters` | 43200 | 697 | 100.0 | 2702 | 1.00 | sufficient_activity |
| `R3_WildlifeTracking` | 43200 | 92 | 100.0 | 10898 | 1.00 | moderate_activity |
| `R4_ParkRangers_NuuksioSparseTrails` | 43200 | 30 | 100.0 | 13381 | 0.98 | moderate_activity |
| `R5_MountainRescue` | 14400 | 314 | 100.0 | 1263 | 0.98 | sufficient_activity |
| `R6_SparseLongRange` | 43200 | 435 | 100.0 | 1283 | 1.00 | sufficient_activity |
| `R7_SparseTinyBuffer` | 43200 | 1835 | 100.0 | 1214 | 1.00 | sufficient_activity |
| `R8_IntermittentPower` | 43200 | 808 | 100.0 | 1261 | 0.92 | sufficient_activity |
| `R9_ExtremeRange_200m` | 43200 | 4118 | 100.0 | 357 | 1.00 | sufficient_activity |
| `S1_StrongCommunities_SeparateClusters` | 43200 | 111833 | 100.0 | 0 | 1.00 | sufficient_activity |
| `S2_WeakCommunities_HighMixing` | 43200 | 13234 | 100.0 | 319 | 1.00 | sufficient_activity |
| `S3_PeriodicMeetings_RegularRhythm` | 43200 | 2816 | 100.0 | 1109 | 1.00 | sufficient_activity |
| `S4_RandomMixing_NoHotspots` | 43200 | 3674 | 100.0 | 917 | 1.00 | sufficient_activity |
| `S5_TwoLayer_StudentsStaff` | 43200 | 18285 | 100.0 | 401 | 1.00 | sufficient_activity |
| `S6_FamilyGroups_SmallPersistent` | 43200 | 13700 | 100.0 | 338 | 1.00 | sufficient_activity |
| `U1_CBD_Commuting_HelsinkiDowntown` | 43200 | 5269 | 88.9 | — | 1.00 | sufficient_activity |
| `U2_SparseSuburb_HelsinkiDowntown` | 43200 | 870 | 75.0 | — | 1.00 | sufficient_activity |
| `U3_MicroMobility_HelsinkiDowntown` | 43200 | 12380 | 84.1 | — | 1.00 | sufficient_activity |
| `U4_CongestionHotspot_HelsinkiDowntown` | 43200 | 3442 | 79.0 | — | 0.99 | sufficient_activity |
| `U5_WorkdayShort_HelsinkiDowntown` | 43200 | 2144 | 74.1 | — | 1.00 | sufficient_activity |
| `U6_OfficeWaitHeavyTail_HelsinkiDowntown` | 43200 | 2474 | 75.3 | — | 1.00 | sufficient_activity |
| `U7_HighTimeVariance_HelsinkiDowntown` | 43200 | 3877 | 82.7 | — | 1.00 | sufficient_activity |
| `V1_TaxiLow_ManhattanMidtownGrid` | 43200 | 494 | 100.0 | 780 | 1.00 | sufficient_activity |
| `V2_TaxiHigh_ManhattanMidtownGrid` | 43200 | 25968 | 100.0 | 134 | 1.00 | sufficient_activity |
| `V3_BusOnlyCarriers_ManhattanMidtownGrid` | 43200 | 1034 | 100.0 | 1190 | 1.00 | sufficient_activity |
| `V4_CarOwnership_0_ManhattanMidtownGrid` | 43200 | 3753 | 86.4 | — | 0.99 | sufficient_activity |
| `V5_CarOwnership_100_ManhattanMidtownGrid` | 43200 | 2722 | 87.8 | — | 1.00 | sufficient_activity |