## Escenario T5 — T5_VeryLongTtl_6to24h

### 1. Visión general

- **Scenario ID:** T5
- **Nombre:** T5_VeryLongTtl_6to24h
- **Familia:** Traffic
- **Fichero settings:** `corpus_v1/07_traffic/T5_VeryLongTtl_6to24h.settings`

**Objetivo**

TTL muy largo (6–24 h). Patience-friendly; permite cadenas largas de store-carry-forward.

### 2. Configuración del escenario (features core)

Los valores siguientes provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 24750000 |  |
| aspect_ratio | 0.8182 |  |
| N | 40 |  |
| nrofHostGroups | 1 |  |
| speed_mean | 0.85 |  |
| wait_mean | 180 |  |
| mm_WDM | 0 |  |
| mm_RWP | 1 |  |
| mm_MapRoute | 0 |  |
| mm_Cluster | 0 |  |
| mm_Bus | 0 |  |
| mm_Linear | 0 |  |
| transmitRange | 14 |  |
| bufferSize | 52000000 |  |
| transmitSpeed | 1750000 |  |
| msgTtl | 1440 |  |
| event_interval_mean | 260 |  |
| event_size_mean | 90000 |  |
| nrof_event_generators | 1 |  |
| pattern_burst | 0 |  |
| pattern_hub_target | 0 |  |
| workDayLength | Not recorded | Not used in this scenario |
| ownCarProb | Not recorded | Not used in this scenario |
| clusterRange_mean | Not recorded | Mean cluster radius if ClusterMovement |

### 3. Modelo de movilidad

Los escenarios Traffic usan movilidad RandomWaypoint compartida. El foco está en **levers de mensajes y recursos** (tamaño, tasa, TTL, buffer, velocidad de transmisión) más que en diversidad de movilidad.

**Implicación DTN**

Los escenarios Traffic estresan **gestión de buffer**, **sensibilidad a TTL**, **congestión** y **cuellos de botella de transferencia**. Misma movilidad entre escenarios aísla el comportamiento del protocolo bajo distintas carga y restricciones de recursos.

### 4. Patrón de tráfico

MessageEventGenerator(s) con intervalo, tamaño, TTL y patrón configurables (uniforme, burst, hub-target). Uno o dos generadores por escenario.

**Implicación DTN**

La tasa de eventos, tamaño y TTL interactúan: alta tasa + buffer pequeño (T9) causa drops; TTL corto (T4, T11) requiere entrega rápida; TTL largo (T5, T12) tolera paciencia.

### 5. Comportamiento esperado de la red

- Entrega sensible a TTL, buffer y velocidad de transmisión.
- Overhead puede aumentar con flooding o tráfico burst.
- Latencia variable: baja cuando recursos son amplios, alta bajo congestión o buffer pequeño.
- Drop ratio alto cuando buffer o TTL están estresados.

### 6. Rol en el corpus

Este escenario representa un **régimen de tráfico/recursos** que contribuye diversidad en tamaño de mensaje, tasa, TTL, buffer y velocidad de transmisión respecto a familias centradas en movilidad.

### 7. Características distintivas

- Configuración centrada en tráfico con movilidad compartida.
- Lever distinto (tamaño, tasa, TTL, buffer, velocidad de transmisión, patrón) por escenario.
- Complementa otras familias aislando efectos de tráfico y recursos.

### 8. Correlación con otros escenarios (core 23)

Usando el **espacio de 23 features core** (`analysis/data/correlation_pearson_core23.csv`):

- **Más similares (top 3):**
  - D3_Aftershock_ErraticMobility — r ≈ **0.79**
  - S3_PeriodicMeetings_RegularRhythm — r ≈ **0.75**
  - T11_TTL_1min — r ≈ **0.71**
- **Más diferentes (top 3)** (menor |r|):
  - S5_TwoLayer_StudentsStaff — r ≈ **0.00**
  - T3_MixedBimodal_SmallAndLarge — r ≈ **0.00**
  - S2_WeakCommunities_HighMixing — r ≈ **0.02**

Correlaciones completas en `analysis/reports/correlation_core23_report.txt` y `analysis/data/correlation_pearson_core23.csv`.

**Interpretación**

Escenarios similares comparten levers estructurales (tasa de eventos, tamaño, TTL, buffer). Correlaciones cercanas a cero corresponden a escenarios gobernados por drivers ortogonales.

### 9. Asignación a cluster

En el **clustering Ward k=7** sobre el espacio core de 23 features (`cluster_assignments_core23.csv`), este escenario pertenece a:

- **Cluster 7**.

### 10. Salidas de simulación (opcional)

Si se han ejecutado simulaciones de routing y se extrajeron métricas (`analysis/data/output_metrics.csv`):

| Métrica | Valor |
|--------|-------|
| delivery_ratio | 0.0932 |
| latency_mean | 24025.4 |
| overhead_ratio | 47.8 |
| drop_ratio | 0.0 |

**Interpretación**

Los escenarios Traffic muestran entrega variable según TTL, buffer y velocidad de transmisión; TTL corto o buffer pequeño suelen dar baja entrega o alta tasa de drops.
