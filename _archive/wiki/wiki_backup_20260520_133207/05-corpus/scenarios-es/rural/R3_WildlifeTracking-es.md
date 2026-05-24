## Escenario R3 — R3_WildlifeTracking

### 1. Visión general

- **Scenario ID:** R3  
- **Nombre:** R3_WildlifeTracking  
- **Familia:** Rural  
- **Fichero settings:** `corpus_v1/04_rural/R3_WildlifeTracking.settings`

**Objetivo**

Nodos se mueven muy lento, TTL muy largo (los datos pueden esperar). Régimen fauna/trackers.

### 2. Configuración del escenario (features core)

Los valores siguientes provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 80000000 | Área total de simulación (m^2) |
| aspect_ratio | 0.8 | min(width,height)/max(width,height) |
| N | 20 | Nodos totales |
| nrofHostGroups | 1 | Número de host groups |
| speed_mean | 0.125 | Velocidad media configurada (m/s) |
| wait_mean | 1500 | Tiempo medio de pausa/espera (s) |
| mm_WDM | 0 | WorkingDayMovement activo (1/0) |
| mm_RWP | 1 | RandomWaypoint activo (1/0) |
| mm_MapRoute | 0 | MapRouteMovement activo (1/0) |
| mm_Cluster | 0 | ClusterMovement activo (1/0) |
| mm_Bus | 0 | BusMovement activo (1/0) |
| mm_Linear | 0 | LinearMovement activo (1/0) |
| transmitRange | 10 | Alcance de interfaz (m) |
| bufferSize | 50000000 | Node buffer (bytes) |
| transmitSpeed | 2000000 | Velocidad de interfaz (bytes/s) |
| msgTtl | 10080 | TTL de mensajes |
| event_interval_mean | 900 | Media del intervalo de Events1 |
| event_size_mean | 30000 | Tamaño medio de Events1 (bytes) |
| nrof_event_generators | 1 | Número de generadores de eventos |
| pattern_burst | 0 | Ventanas burst en tráfico (1/0) |
| pattern_hub_target | 0 | Patrón de tráfico hub-target (1/0) |
| workDayLength | Not recorded | No usado en este escenario |
| ownCarProb | Not recorded | No usado en este escenario |
| clusterRange_mean | Not recorded | Radio medio de cluster si hay ClusterMovement |

### 3. Modelo de movilidad

RandomWaypoint, velocidad muy baja (0.05–0.2 m/s), esperas largas, TTL 10080.

**Implicación DTN**

Los escenarios rurales fuerzan **tolerancia al retardo** y **conectividad dispersa**: los contactos son infrecuentes, la diversidad de caminos es limitada y domina store-carry-forward. Los levers de rango extremo (R6, R9) o velocidad extrema (R11, R12) alteran la dinámica de contactos.

### 4. Patrón de tráfico

El tráfico lo generan MessageEventGenerator(s) con parámetros ajustados a la narrativa rural (baja tasa para wildlife, cargas pequeñas para rescate, etc.).

**Implicación DTN**

Bajas tasas de contacto y TTL largo (p. ej. R3) favorecen la paciencia; TTL corto (R5) estresa la entrega time-critical. Estrés de buffer (R7) y potencia intermitente (R8) añaden restricciones de recursos.

### 5. Comportamiento de red esperado

- Contactos dispersos, alta dependencia de store-carry-forward.  
- Entrega sensible al rango, velocidad y buffer.  
- Overhead puede dispararse cuando flooding coincide con ventanas de contacto raras.  
- Latencia típicamente alta salvo que rango/velocidad sean extremos.

### 6. Rol dentro del corpus

Este escenario representa un **régimen de comunicación rural** que aporta diversidad en conectividad, estrés de recursos y tolerancia al retardo frente a baselines Urban/Campus/Disaster.

### 7. Características distintivas

- Configuración orientada a rural con parámetros dispersos o extremos.  
- Prueba el comportamiento del protocolo bajo baja conectividad y restricciones de recursos.  
- Complementa otros escenarios Rural con un lever distinto (rango, velocidad, buffer, TTL o estructura).

### 8. Correlación con otros escenarios (core 23)

Usando el espacio de **23 features core** (`analysis/data/correlation_pearson_core23.csv`):

- **Más similares (top 3):**
  - R11_SpeedExtremeLow — r ≈ **0.78**
  - C3_Hackathon_24h — r ≈ **0.69**
  - R10_TinyRange_5m — r ≈ **0.64**
- **Más diferentes (top 3)** (menor |r|):
  - T7_TargetedToHubs_FewDestinations — r ≈ **-0.00**
  - T11_TTL_1min — r ≈ **-0.00**
  - T3_MixedBimodal_SmallAndLarge — r ≈ **0.00**

Referencias: `analysis/reports/correlation_core23_report.txt` y `analysis/data/correlation_pearson_core23.csv`.

**Interpretación**

Los escenarios similares comparten las mismas palancas estructurales principales. Correlaciones cercanas a cero suelen corresponder a escenarios dominados por factores ortogonales.

### 9. Asignación de cluster

En el clustering Ward k=7 sobre el espacio core 23 (`cluster_assignments_core23.csv`), este escenario pertenece a:

- **Cluster 7**.

### 10. Outputs de simulación (opcional)

Si se han ejecutado simulaciones y extraído métricas (`analysis/data/output_metrics.csv`):

| Métrica | Valor |
|---------|-------|
| delivery_ratio | 0.0 |
| latency_mean |  |
| overhead_ratio |  |
| drop_ratio | 0.0 |

**Interpretación**

Estos outputs reflejan el régimen rural: la entrega depende de las oportunidades de contacto y del TTL; muchos escenarios rurales muestran baja entrega o muchos drops cuando la conectividad es dispersa o los deadlines son estrictos.
