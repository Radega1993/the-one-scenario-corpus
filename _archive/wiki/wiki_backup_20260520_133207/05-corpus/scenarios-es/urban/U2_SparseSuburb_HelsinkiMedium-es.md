## Escenario U2 — U2_SparseSuburb_HelsinkiMedium

### 1. Visión general

- **Scenario ID:** U2
- **Nombre:** U2_SparseSuburb_HelsinkiMedium
- **Familia:** Urban
- **Fichero settings:** `corpus_v1/01_urban/U2_SparseSuburb_HelsinkiMedium.settings`

**Objetivo**

Suburbio disperso: mundo grande, pocos puntos de interés, baja densidad. Prueba DTN bajo conectividad urbana diluida.

### 2. Configuración del escenario (features core)

Los valores siguientes provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 132000000 |  |
| aspect_ratio | 0.9167 |  |
| N | 36 |  |
| nrofHostGroups | 2 |  |
| speed_mean | 8.5 |  |
| wait_mean | 20 |  |
| mm_WDM | 1 |  |
| mm_RWP | 0 |  |
| mm_MapRoute | 0 |  |
| mm_Cluster | 0 |  |
| mm_Bus | 1 |  |
| mm_Linear | 0 |  |
| transmitRange | 12 |  |
| bufferSize | 50000000 |  |
| transmitSpeed | 2000000 |  |
| msgTtl | 10000 |  |
| event_interval_mean | 30 |  |
| event_size_mean | 100000 |  |
| nrof_event_generators | 1 |  |
| pattern_burst | 0 |  |
| pattern_hub_target | 0 |  |
| workDayLength | 28800 | Work day length (s) if WorkingDayMovement |
| ownCarProb | 0 | Car ownership probability if WDM |
| clusterRange_mean | Not recorded | Mean cluster radius if ClusterMovement |

### 3. Modelo de movilidad

WorkingDayMovement sobre mapa Helsinki con buses como portadores. La densidad urbana, clustering de oficinas y horarios de actividad varían según el lever del escenario.

**Implicación DTN**

Los escenarios urbanos estresan **frecuencia de contactos**, **estructura temporal** (picos de rush, duración de jornada) y **compartición de recursos** (buffer, velocidad de transmisión). Disperso (U5) vs denso (U7, U8) y jornada corta (U9) vs alta varianza (U12) crean regímenes de conectividad distintos.

### 4. Patrón de tráfico

MessageEventGenerator con intervalo y tamaño ajustados por escenario. Fuente–destino uniforme, un generador.

**Implicación DTN**

La tasa de eventos y TTL interactúan con la movilidad: TTL corto (U7) favorece relays rápidos; TTL largo (U5) tolera contactos dispersos. Buffer y velocidad de transmisión afectan la congestión bajo alta carga.

### 5. Comportamiento esperado de la red

- Oportunidades de contacto determinadas por clustering de oficinas, duración de jornada y varianza temporal.
- Entrega sensible a densidad, rango y TTL.
- Overhead aumenta con flooding en ventanas de contacto densas.
- Latencia típicamente moderada; escenarios dispersos muestran mayor retardo.

### 6. Rol en el corpus

Este escenario representa un **régimen de comunicación urbano** que contribuye diversidad en conectividad, estructura temporal y estrés de recursos respecto a baselines Campus/Rural/Disaster.

### 7. Características distintivas

- Configuración urbana con WorkingDayMovement y buses.
- Lever distinto (densidad, jornada, varianza temporal, rango, buffer) por escenario.
- Complementa otros escenarios Urban y Vehicles (mapa Helsinki compartido).

### 8. Correlación con otros escenarios (core 23)

Usando el **espacio de 23 features core** (`analysis/data/correlation_pearson_core23.csv`):

- **Más similares (top 3):**
  - U1_CBD_Commuting_HelsinkiMedium — r ≈ **0.81**
  - U6_OfficeWaitHeavyTail_HelsinkiMedium — r ≈ **0.76**
  - U7_HighTimeVariance_HelsinkiMedium — r ≈ **0.71**
- **Más diferentes (top 3)** (menor |r|):
  - R7_SparseTinyBuffer — r ≈ **0.00**
  - R2_VillagesTrails_ThreeClusters — r ≈ **0.01**
  - S6_FamilyGroups_SmallPersistent — r ≈ **-0.04**

Correlaciones completas en `analysis/reports/correlation_core23_report.txt` y `analysis/data/correlation_pearson_core23.csv`.

**Interpretación**

Escenarios similares comparten levers estructurales (WDM, densidad, rango, TTL). Correlaciones cercanas a cero corresponden a escenarios gobernados por drivers ortogonales.

### 9. Asignación a cluster

En el **clustering Ward k=7** sobre el espacio core de 23 features (`cluster_assignments_core23.csv`), este escenario pertenece a:

- **Cluster 1**.

### 10. Salidas de simulación (opcional)

Si se han ejecutado simulaciones de routing y se extrajeron métricas (`analysis/data/output_metrics.csv`):

| Métrica | Valor |
|--------|-------|
| delivery_ratio | 0.0769 |
| latency_mean | 930.125 |
| overhead_ratio | 30.0714 |
| drop_ratio | 0.0 |

**Interpretación**

Los escenarios urbanos suelen mostrar entrega y overhead moderados; variantes dispersas (U5) o TTL corto (U7) estresan el comportamiento del protocolo bajo conectividad limitada.
