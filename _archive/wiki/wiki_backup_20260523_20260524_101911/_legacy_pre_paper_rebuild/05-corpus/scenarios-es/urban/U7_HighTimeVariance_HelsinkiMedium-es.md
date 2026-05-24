## Escenario U7 — U7_HighTimeVariance_HelsinkiMedium

### 1. Visión general

- **Scenario ID:** U7
- **Nombre:** U7_HighTimeVariance_HelsinkiMedium
- **Familia:** Urban
- **Fichero settings:** `corpus_v1/01_urban/U7_HighTimeVariance_HelsinkiMedium.settings`

**Objetivo**

Alta varianza temporal en horarios de actividad. Dispersa picos mañana/tarde y diversifica el timing de contactos.

### 2. Configuración del escenario (features core)

Los valores siguientes provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 51590000 |  |
| aspect_ratio | 0.8701 |  |
| N | 81 |  |
| nrofHostGroups | 2 |  |
| speed_mean | 8.5 |  |
| wait_mean | 20 |  |
| mm_WDM | 1 |  |
| mm_RWP | 0 |  |
| mm_MapRoute | 0 |  |
| mm_Cluster | 0 |  |
| mm_Bus | 1 |  |
| mm_Linear | 0 |  |
| transmitRange | 11 |  |
| bufferSize | 48000000 |  |
| transmitSpeed | 1450000 |  |
| msgTtl | 3000 |  |
| event_interval_mean | 37 |  |
| event_size_mean | 100000 |  |
| nrof_event_generators | 1 |  |
| pattern_burst | 0 |  |
| pattern_hub_target | 0 |  |
| workDayLength | 29700 | Work day length (s) if WorkingDayMovement |
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
  - U6_OfficeWaitHeavyTail_HelsinkiMedium — r ≈ **0.97**
  - V4_CarOwnership_0_HelsinkiMedium — r ≈ **0.90**
  - U3_MicroMobility_HelsinkiMedium — r ≈ **0.84**
- **Más diferentes (top 3)** (menor |r|):
  - S1_StrongCommunities_SeparateClusters — r ≈ **0.01**
  - C6_EmergencyDrill_Evacuation — r ≈ **-0.02**
  - T10_HighRateLowSpeed_Congestion — r ≈ **-0.03**

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
| delivery_ratio | 0.1825 |
| latency_mean | 7816.6536 |
| overhead_ratio | 77.1086 |
| drop_ratio | 8.349282296650717 |

**Interpretación**

Los escenarios urbanos suelen mostrar entrega y overhead moderados; variantes dispersas (U5) o TTL corto (U7) estresan el comportamiento del protocolo bajo conectividad limitada.
