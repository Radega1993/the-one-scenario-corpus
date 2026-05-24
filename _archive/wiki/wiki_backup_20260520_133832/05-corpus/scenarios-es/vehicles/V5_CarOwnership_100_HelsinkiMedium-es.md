## Escenario V5 — V5_CarOwnership_100_HelsinkiMedium

### 1. Visión general

- **Scenario ID:** V5
- **Nombre:** V5_CarOwnership_100_HelsinkiMedium
- **Familia:** Vehicles
- **Fichero settings:** `corpus_v1/03_vehicles/V5_CarOwnership_100_HelsinkiMedium.settings`

**Objetivo**

Propiedad total de coche: todos los agentes usan coche. Altera patrones de contacto vs mezcla peatón/bus.

### 2. Configuración del escenario (features core)

Los valores siguientes provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 62160000 |  |
| aspect_ratio | 0.881 |  |
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
| transmitRange | 14 |  |
| bufferSize | 50000000 |  |
| transmitSpeed | 2000000 |  |
| msgTtl | 10000 |  |
| event_interval_mean | 30 |  |
| event_size_mean | 100000 |  |
| nrof_event_generators | 1 |  |
| pattern_burst | 0 |  |
| pattern_hub_target | 0 |  |
| workDayLength | 32400 | Work day length (s) if WorkingDayMovement |
| ownCarProb | 1 | Car ownership probability if WDM |
| clusterRange_mean | Not recorded | Mean cluster radius if ClusterMovement |

### 3. Modelo de movilidad

Los escenarios Vehicles usan MapRouteMovement (taxis), BusMovement (buses) o WorkingDayMovement con buses (V6, V7). Base mapa Helsinki.

**Implicación DTN**

Los escenarios vehiculares estresan **velocidad**, **estructura de rutas** y **densidad de portadores**. Taxis (V1, V2) proporcionan relays dispersos o densos; buses (V3) concentran tráfico en rutas; WDM+bus (V6, V7) mezclan movilidad peatonal y vehicular.

### 4. Patrón de tráfico

MessageEventGenerator con intervalo y tamaño ajustados por escenario. Fuente–destino uniforme.

**Implicación DTN**

La tasa de eventos y TTL interactúan con velocidad y densidad vehicular: portadores rápidos (V2) pueden mejorar la entrega; portadores dispersos (V1) requieren paciencia.

### 5. Comportamiento esperado de la red

- Oportunidades de contacto determinadas por densidad vehicular y solapamiento de rutas.
- Entrega sensible a número de portadores, velocidad y rango.
- Overhead típicamente menor que flooding peatonal cuando los portadores son pocos.
- Latencia variable: baja con portadores densos y rápidos, alta cuando son dispersos.

### 6. Rol en el corpus

Este escenario representa un **régimen de comunicación vehicular** que contribuye diversidad en velocidad, tipo de portador y densidad respecto a baselines Urban/Campus/Rural.

### 7. Características distintivas

- Configuración vehicular (taxis, buses o WDM con coches).
- Prueba el comportamiento del protocolo bajo relays vehiculares y movilidad basada en rutas.
- Complementa Urban (mapa Helsinki compartido) con levers de movilidad distintos.

### 8. Correlación con otros escenarios (core 23)

Usando el **espacio de 23 features core** (`analysis/data/correlation_pearson_core23.csv`):

- **Más similares (top 3):**
  - U1_CBD_Commuting_HelsinkiMedium — r ≈ **0.76**
  - U6_OfficeWaitHeavyTail_HelsinkiMedium — r ≈ **0.75**
  - V4_CarOwnership_0_HelsinkiMedium — r ≈ **0.75**
- **Más diferentes (top 3)** (menor |r|):
  - C6_EmergencyDrill_Evacuation — r ≈ **-0.01**
  - D5_UAVMule_FastRoute_HelsinkiMedium — r ≈ **0.03**
  - S1_StrongCommunities_SeparateClusters — r ≈ **0.04**

Correlaciones completas en `analysis/reports/correlation_core23_report.txt` y `analysis/data/correlation_pearson_core23.csv`.

**Interpretación**

Escenarios similares comparten levers estructurales (MapRoute, Bus, WDM, densidad). Correlaciones cercanas a cero corresponden a escenarios gobernados por drivers ortogonales.

### 9. Asignación a cluster

En el **clustering Ward k=7** sobre el espacio core de 23 features (`cluster_assignments_core23.csv`), este escenario pertenece a:

- **Cluster 1**.

### 10. Salidas de simulación (opcional)

Si se han ejecutado simulaciones de routing y se extrajeron métricas (`analysis/data/output_metrics.csv`):

| Métrica | Valor |
|--------|-------|
| delivery_ratio | 0.1442 |
| latency_mean | 8155.664 |
| overhead_ratio | 62.9716 |
| drop_ratio | 3.96514012303486 |

**Interpretación**

Los escenarios vehiculares muestran entrega variable: alta con taxis densos (V2), moderada con buses (V3), menor con taxis dispersos (V1) o variantes WDM (V6, V7).
