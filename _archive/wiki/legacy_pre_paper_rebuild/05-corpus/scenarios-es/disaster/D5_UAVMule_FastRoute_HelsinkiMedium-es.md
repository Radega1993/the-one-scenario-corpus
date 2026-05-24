## Escenario D5 — D5_UAVMule_FastRoute_HelsinkiMedium

### 1. Visión general

- **Scenario ID:** D5  
- **Nombre:** D5_UAVMule_FastRoute_HelsinkiMedium  
- **Familia:** Disaster  
- **Fichero settings:** `corpus_v1/05_disaster/D5_UAVMule_FastRoute_HelsinkiMedium.settings`

**Objetivo**

Escenario disaster en mapa donde dos mules tipo UAV recorren rutas largas para relé de contactos dispersos.

### 2. Configuración del escenario (features core)

Los valores siguientes provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 63033600 | Área total de simulación (m^2) |
| aspect_ratio | 0.8933 | min(width,height)/max(width,height) |
| N | 62 | Nodos totales |
| nrofHostGroups | 2 | Número de host groups |
| speed_mean | 1.3 | Velocidad media configurada (m/s) |
| wait_mean | 65 | Tiempo medio de pausa/espera (s) |
| mm_WDM | 0 | WorkingDayMovement activo (1/0) |
| mm_RWP | 0 | RandomWaypoint activo (1/0) |
| mm_MapRoute | 1 | MapRouteMovement activo (1/0) |
| mm_Cluster | 0 | ClusterMovement activo (1/0) |
| mm_Bus | 0 | BusMovement activo (1/0) |
| mm_Linear | 0 | LinearMovement activo (1/0) |
| transmitRange | 10 | Alcance de interfaz (m) |
| bufferSize | 50000000 | Node buffer (bytes) |
| transmitSpeed | 2000000 | Velocidad de interfaz (bytes/s) |
| msgTtl | 10000 | TTL de mensajes |
| event_interval_mean | 112.5 | Media del intervalo de Events1 |
| event_size_mean | 65000 | Tamaño medio de Events1 (bytes) |
| nrof_event_generators | 1 | Número de generadores de eventos |
| pattern_burst | 0 | Ventanas burst en tráfico (1/0) |
| pattern_hub_target | 0 | Patrón de tráfico hub-target (1/0) |
| workDayLength | — | No usado en este escenario |
| ownCarProb | — | No usado en este escenario |
| clusterRange_mean | — | Radio medio de cluster si hay ClusterMovement |

### 3. Modelo de movilidad

- **World size:** `8400, 7504`  
- **Rango base de velocidad:** `Not recorded`  
- **Rango base de espera:** `Not recorded`

MapRouteMovement para todos, con subgrupo UAV de alta velocidad.

**Implicación DTN**

Este diseño de movilidad crea un régimen disaster de contacto restringido donde la conectividad depende de puentes temporales, clusters locales densos o relés oportunistas, más que de caminos estables extremo a extremo.

### 4. Patrón de tráfico

- `Events.nrof = 1`  
- `Events1.interval = 45, 180`  
- `Events1.size = 10k, 120k`  
- `Group.msgTtl = Not recorded`

El tráfico está configurado como carga de emergencia con parámetros de tiempo/tamaño alineados con esta narrativa disaster.

**Implicación DTN**

Con Epidemic routing, estos parámetros amplifican el compromiso entre urgencia y congestión: ventanas de contacto cortas pueden mejorar entregas rápidas, pero también aumentar redundancia o expiración cuando persisten las particiones.

### 5. Comportamiento de red esperado

- Las oportunidades de contacto son heterogéneas y dependen de la estructura de movilidad (clusters/particiones/rutas).  
- La entrega se limita cuando los puentes temporales son débiles o el TTL es muy corto.  
- El overhead crece rápido cuando flooding coincide con contactos locales densos.  
- La latencia puede ser bimodal: casi instantánea en islas locales, muy alta entre particiones.

### 6. Rol dentro del corpus

Este escenario representa un **régimen específico de comunicación disaster** dentro del corpus, aportando diversidad frente a baselines Urban/Campus/Social y complementando los demás escenarios Disaster con un estresor estructural diferenciado.

### 7. Características distintivas

- Configuración orientada a disaster con restricciones estructurales explícitas.  
- Acoplamiento movilidad/tráfico diseñado para forzar store-carry-forward.  
- Relevante para evaluar robustez bajo conectividad intermitente o interrumpida.

### 8. Correlación con otros escenarios (core 23)

Usando el espacio de **23 features core** (`analysis/data/correlation_pearson_core23.csv`):

- **Más similares (top 3):**
  - R4_ParkRangers_HelsinkiMedium — r ≈ **0.87**
  - V2_TaxiHigh_HelsinkiMedium — r ≈ **0.69**
  - V1_TaxiLow_HelsinkiMedium — r ≈ **0.68**
- **Más diferentes (top 3)** (menor |r|):
  - U6_OfficeWaitHeavyTail_HelsinkiMedium — r ≈ **0.00**
  - U3_MicroMobility_HelsinkiMedium — r ≈ **-0.00**
  - V4_CarOwnership_0_HelsinkiMedium — r ≈ **-0.01**

Referencias: `analysis/reports/correlation_core23_report.txt` y `analysis/data/correlation_pearson_core23.csv`.

**Interpretación**

Los escenarios más próximos comparten las mismas palancas estructurales principales (familia de movilidad, estructura de host groups y escala de tráfico), mientras que correlaciones cercanas a cero suelen corresponder a escenarios dominados por factores ortogonales (p. ej., rango/velocidad extremos, map routing o regímenes distintos de TTL/carga).

### 9. Asignación de cluster

En el clustering Ward k=7 sobre el espacio core 23 (`cluster_assignments_core23.csv`), este escenario pertenece a:

- **Cluster 3**.

### 10. Outputs de simulación (opcional)

Si se han ejecutado simulaciones y extraído métricas (`analysis/data/output_metrics.csv`):

| Métrica | Valor |
|---------|-------|
| delivery_ratio | 0.0052 |
| latency_mean | 366.75 |
| overhead_ratio | 36.5 |
| drop_ratio | 0.7242268041237113 |

**Interpretación**

Estos outputs son coherentes con las restricciones disaster del escenario: la entrega refleja disponibilidad de puentes y viabilidad del TTL; el overhead refleja presión de replicación en contactos locales; valores faltantes de latencia/overhead indican ausencia de entregas exitosas en la ejecución analizada.
