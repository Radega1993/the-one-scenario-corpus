## Escenario S5 — S5_TwoLayer_StudentsStaff

### 1. Visión general

- **Scenario ID:** S5
- **Nombre:** S5_TwoLayer_StudentsStaff
- **Familia:** Social
- **Fichero settings:** `corpus_v1/06_social/S5_TwoLayer_StudentsStaff.settings`

**Objetivo**

Estructura de dos capas (estudiantes + staff). Patrones de movilidad y contacto distintos por capa; prueba el protocolo bajo grupos heterogéneos.

### 2. Configuración del escenario (features core)

Los valores siguientes provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 30000000 |  |
| aspect_ratio | 0.8333 |  |
| N | 75 |  |
| nrofHostGroups | 2 |  |
| speed_mean | 1.6 |  |
| wait_mean | 105 |  |
| mm_WDM | 0 |  |
| mm_RWP | 1 |  |
| mm_MapRoute | 0 |  |
| mm_Cluster | 0 |  |
| mm_Bus | 0 |  |
| mm_Linear | 0 |  |
| transmitRange | 11 |  |
| bufferSize | 50000000 |  |
| transmitSpeed | 2000000 |  |
| msgTtl | 10000 |  |
| event_interval_mean | 102.5 |  |
| event_size_mean | 57500 |  |
| nrof_event_generators | 1 |  |
| pattern_burst | 0 |  |
| pattern_hub_target | 0 |  |
| workDayLength | Not recorded | Not used in this scenario |
| ownCarProb | Not recorded | Not used in this scenario |
| clusterRange_mean | Not recorded | Mean cluster radius if ClusterMovement |

### 3. Modelo de movilidad

Los escenarios sociales usan modelos de movilidad que crean estructura comunitaria: ClusterMovement (S1, S6), RandomWaypoint con parámetros de mezcla (S2, S3, S4), o configuraciones de dos capas (S5).

**Implicación DTN**

Los escenarios sociales estresan **estructura comunitaria**, **nodos puente** y **patrones temporales** (periódicos vs aleatorios). La entrega depende de relays inter-comunidad; los protocolos deben explotar o tolerar contactos dispersos entre clusters.

### 4. Patrón de tráfico

MessageEventGenerator con intervalo y tamaño ajustados por escenario. Patrones uniformes o hub-target.

**Implicación DTN**

El tráfico interactúa con la estructura comunitaria: mensajes dentro de clusters se benefician de la densidad local; la entrega entre clusters requiere paciencia o explotación de puentes.

### 5. Comportamiento esperado de la red

- Oportunidades de contacto determinadas por estructura comunitaria y mezcla.
- Entrega sensible a presencia de puentes y TTL.
- Overhead puede aumentar con flooding en clusters locales densos.
- Latencia variable: baja dentro de clusters, alta entre particiones.

### 6. Rol en el corpus

Este escenario representa un **régimen de comunicación social** que contribuye diversidad en estructura comunitaria, mezcla y patrones temporales respecto a baselines Urban/Campus/Rural.

### 7. Características distintivas

- Configuración social con estructura explícita de comunidad o capas.
- Prueba el comportamiento del protocolo bajo mezcla estructurada vs aleatoria.
- Complementa otros escenarios Social con un lever distinto (tamaño de cluster, mezcla, periodicidad, capas).

### 8. Correlación con otros escenarios (core 23)

Usando el **espacio de 23 features core** (`analysis/data/correlation_pearson_core23.csv`):

- **Más similares (top 3):**
  - S2_WeakCommunities_HighMixing — r ≈ **0.89**
  - D7_HighLoad_TrafficStorm — r ≈ **0.88**
  - S4_RandomMixing_NoHotspots — r ≈ **0.72**
- **Más diferentes (top 3)** (menor |r|):
  - R2_VillagesTrails_ThreeClusters — r ≈ **0.00**
  - T5_VeryLongTtl_6to24h — r ≈ **0.00**
  - T10_HighRateLowSpeed_Congestion — r ≈ **0.02**

Correlaciones completas en `analysis/reports/correlation_core23_report.txt` y `analysis/data/correlation_pearson_core23.csv`.

**Interpretación**

Escenarios similares comparten levers estructurales (ClusterMovement, densidad, mezcla). Correlaciones cercanas a cero corresponden a escenarios gobernados por drivers ortogonales.

### 9. Asignación a cluster

En el **clustering Ward k=7** sobre el espacio core de 23 features (`cluster_assignments_core23.csv`), este escenario pertenece a:

- **Cluster 7**.

### 10. Salidas de simulación (opcional)

Si se han ejecutado simulaciones de routing y se extrajeron métricas (`analysis/data/output_metrics.csv`):

| Métrica | Valor |
|--------|-------|
| delivery_ratio | 0.0853 |
| latency_mean | 10002.4892 |
| overhead_ratio | 67.6757 |
| drop_ratio | 5.493087557603687 |

**Interpretación**

Los escenarios sociales muestran entrega variable según estructura comunitaria y disponibilidad de puentes; alta mezcla (S2) puede mejorar la entrega; clusters fuertes (S1, S6) pueden limitar el alcance entre clusters.
