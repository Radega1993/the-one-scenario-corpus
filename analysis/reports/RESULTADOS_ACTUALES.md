# Resultados actuales del corpus (referencia única)

**Corpus:** 60 escenarios en `corpus_v1/`. 10 escenarios movidos a `corpus_dropped_v1/` (C6, V4, U2, V5, C5, U3, U4, U6, U10, V8) por alta correlación y redundancia narrativa.

---

## Por qué 24 features son CORE

La **referencia única** para diversidad y para el paper/tesis es el **espacio core de 24 features**. Justificación completa: [features_core_vs_extended.md](../docs/features_core_vs_extended.md).

**Criterios para que una feature esté en core:**
- Define de verdad el escenario (cambio científico si varía).
- Poca redundancia con otras del core (no misma variable latente).
- Interpretable y ligada a hipótesis de red (movilidad, contacto, tráfico, recursos).
- **Corpus-wide:** no sobrerrepresentar una sola familia (p. ej. WDM).

**Lista core (24):** world_area, aspect_ratio, N, nrofHostGroups, speed_mean, wait_mean, mm_WDM, mm_RWP, mm_MapRoute, mm_Cluster, mm_Bus, mm_Linear, transmitRange, bufferSize, transmitSpeed, msgTtl, event_interval_mean, event_size_mean, nrof_event_generators, pattern_burst, pattern_hub_target, workDayLength, ownCarProb, clusterRange_mean.

---

## Por qué otras features están descartadas o en EXTENDED

Los **settings que no se usan** y el motivo (identificadores, rutas, constantes, redundantes, detalle de implementación) están en [features_decision.md](../docs/features_decision.md).

Las **features extendidas (46 en total)** incluyen las 24 core más: density, pause_ratio, contact_rate_proxy, mm_ShortestPath, mm_External, event2_*, pattern_uniform, timeDiffSTD, nrOfOffices, nrOfMeetingSpots, officeWaitTime_mean, shoppingWaitTime_mean, etc. Se usan para análisis exploratorio y dashboard; **no** para el criterio de diversidad ni para los resultados principales. La razón de cada descarte (core vs extended) está en [features_core_vs_extended.md](../docs/features_core_vs_extended.md) §3 (redundancias, bloques WDM, density excluida del core, etc.).

---

## Métricas actuales (core 24)

| Métrica | Valor |
|--------|--------|
| Escenarios | 60 |
| Total pares | 1770 |
| **Pares con \|r\| ≥ 0.7** | **88 (5.0%)** |
| **max \|r\|** | **0.9708** (U11↔U12) |
| Distancia coseno mínima | 0.0295 |
| Silhouette (Ward k=7) | 0.3227 |

Espacio completo (46 features): 54 pares con |r| ≥ 0.7 (3.1%), max |r| = 0.9357.

Fuente: [correlation_core24_report.txt](correlation_core24_report.txt).

---

## Informes en este directorio (`reports/`)

Salidas del pipeline que aportan información a quien usa el proyecto:

| Informe | Contenido |
|---------|------------|
| [correlation_core24_report.txt](correlation_core24_report.txt) | Métricas y pares \|r\|≥0.7 en **core 24**. |
| [scenarios_to_diversify_core24.txt](scenarios_to_diversify_core24.txt) | Escenarios a diversificar (prioridad por core 24). |
| [features_report.md](features_report.md) / .txt | Lista de features y settings no usados. |
| [correlation_report.txt](correlation_report.txt) | Correlación en espacio 46. |
| [clustering_report.txt](clustering_report.txt) | Clusters Ward k=7. |
| [feature_feature_correlation_report.txt](feature_feature_correlation_report.txt) | Correlación 24×24 entre features. |
| [ablation_report.txt](ablation_report.txt) | Ablación 17 vs 24 vs 46. |
| [multiple_comparisons_report.txt](multiple_comparisons_report.txt) | FDR / Bonferroni. |

**Documentación (guías, metodología, planes de trabajo)** está en **[`analysis/docs/`](../docs/)**: justificación core 24 ([features_core_vs_extended.md](../docs/features_core_vs_extended.md)), settings descartados ([features_decision.md](../docs/features_decision.md)), plan de continuidad, guía de estado, mapas y variedad, análisis diversidad vs comportamiento.
