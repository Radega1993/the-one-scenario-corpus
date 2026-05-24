## Escenario C1 — C1_Campus_ClassChange

### 1. Visión general

- **Scenario ID:** C1  
- **Nombre:** C1_Campus_ClassChange  
- **Familia:** Campus  
- **Fichero settings:** `corpus_v1/02_campus/C1_Campus_ClassChange.settings`

**Objetivo**

Este escenario modela **oleadas de cambio de clase en un campus**: los estudiantes se desplazan entre edificios cada ~50 minutos en un mapa relativamente pequeño, produciendo incrementos periódicos en las oportunidades de contacto. Sirve como baseline de campus con **movilidad RandomWaypoint en espacio libre** y un **único flujo de tráfico** cuyo intervalo está ajustado a los periodos de cambio de clase.

### 2. Configuración del escenario (features core)

Los valores siguientes provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 480000.0 | 800 m × 600 m (campus) |
| aspect_ratio | 0.75 | min(800,600)/max(800,600) |
| N | 60 | 60 nodos móviles |
| nrofHostGroups | 1 | Un único host group |
| speed_mean | 1.15 | Media de 0.8–1.5 m/s |
| wait_mean | 180.0 | Media de 60–300 s |
| mm_WDM | 0 | Sin WorkingDayMovement |
| mm_RWP | 1 | RandomWaypoint |
| mm_MapRoute | 0 | Sin rutas en mapa |
| mm_Cluster | 0 | Sin ClusterMovement |
| mm_Bus | 0 | Sin BusMovement |
| mm_Linear | 0 | Sin LinearMovement |
| transmitRange | 10.0 | Alcance corto tipo Bluetooth |
| bufferSize | 50,000,000.0 | Buffers de 50 MB |
| transmitSpeed | 2,000,000.0 | 2 MB/s |
| msgTtl | 10000.0 | TTL (unidades de simulación, ~2.8 h) |
| event_interval_mean | 3000.0 | ≈50 min entre mensajes (escala cambio de clase) |
| event_size_mean | 100000.0 | 100 kB |
| nrof_event_generators | 1 | Un flujo (Events1) |
| pattern_burst | 0 | Sin bursts explícitos por ventanas |
| pattern_hub_target | 0 | Sin destinos tipo hub |
| workDayLength | — | No aplica (no WDM) |
| ownCarProb | — | No aplica (no WDM/vehicular) |
| clusterRange_mean | — | No aplica (no ClusterMovement) |

### 3. Modelo de movilidad

C1 usa **RandomWaypoint** sobre un área 800×600 m:

- Los nodos se mueven libremente en espacio continuo entre puntos elegidos uniformemente.  
- Las velocidades se extraen entre **0.8 y 1.5 m/s**, aproximando caminata en un campus.  
- Los tiempos de espera entre movimientos están entre **60 y 300 s**, representando permanencias en aulas/estancias antes de ir a la siguiente clase.

Hay un único host group (`Group`/`Group1`) con 60 nodos homogéneos y sin mapa ni hotspots explícitos: la estructura espacial viene dada por `worldSize`.

**Implicación DTN**

Velocidades peatonales moderadas y pausas moderadas generan **contactos intermitentes** con diversidad de caminos limitada pero no trivial. El área pequeña aumenta la probabilidad de encuentro; al no haber restricciones por mapa, no aparecen cuellos de botella estructurales (los contactos emergen sobre todo de densidad y mezcla aleatoria).

### 4. Patrón de tráfico

El tráfico lo genera un único **MessageEventGenerator** (`Events1`):

- `Events.nrof = 1` y `Events1.class = MessageEventGenerator`.  
- **Intervalo**: `Events1.interval = 2900, 3100` → media ≈ **3000 s (~50 min)**, alineado con “Traffic waves every ~50 min (class change intervals)”.  
- **Tamaño**: `Events1.size = 50k, 150k` → media ≈ **100 kB**.  
- **Fuentes/destinos**: `Events1.hosts = 0, 60` y `Events1.prefix = M` (todos los nodos pueden participar; destinos aleatorios según los defaults del ONE).

Esto define un **flujo moderado y regular** alineado con el ritmo de cambio de clase, sin comportamiento hub-target ni flujos adicionales.

**Implicación DTN**

La tasa de tráfico está sincronizada con las olas de movilidad, así que **oportunidades de forwarding y carga ofrecida co-varían en el tiempo**. Esto suele crear ventanas periódicas “fáciles” para la entrega (durante picos de mezcla) separadas por periodos más tranquilos donde domina store-carry-forward.

### 5. Comportamiento de red esperado

- **Oportunidades de contacto periódicas:** mayor mezcla alrededor de cada cambio de clase.  
- **Entrega alta plausible con Epidemic:** densidad moderada + buffers grandes reducen drops.  
- **Overhead alto esperable:** el flooding replica agresivamente durante las olas de contacto, aumentando transmisiones redundantes.  
- **Latencia moderada:** muchos mensajes se entregan en la siguiente ola; mensajes creados justo después de una ola pueden esperar hasta el siguiente periodo de mezcla.

### 6. Rol dentro del corpus

Este escenario se incluye como **baseline de campus** con:

- densidad moderada (60 nodos en 800×600 m),
- dinámica periódica (ritmo ≈50 min),
- ausencia de estructura (sin rutas en mapa, sin clusters, sin WDM).

Se usa como referencia para comparar contra escenarios de campus más extremos o estructurados (p. ej. estancias largas en exámenes, hackathon, entradas/salidas de estadio).

### 7. Características distintivas

Aspectos que distinguen C1 dentro de la familia Campus:

- Baseline de campus con **RandomWaypoint en espacio libre**, sin mapa ni clusters.  
- Generación de mensajes ajustada a la **periodicidad del cambio de clase (~50 min)**, produciendo **oleadas** en tráfico y contactos a lo largo del día.  
- Un único grupo homogéneo de 60 nodos, **radio de corto alcance (10 m)** y **buffers grandes (50 MB)**: el foco está más en la estructura temporal que en el estrés por recursos.  
- Sirve como **punto de referencia** para comparar con escenarios de campus más extremos (exam day, hackathon, stadium, library, drill).

### 8. Correlación con otros escenarios (core 23)

Usando el espacio de **23 features core** (`analysis/data/correlation_pearson_core23.csv`):

- **Más similares (top 3):**
  - R3_WildlifeTracking — r ≈ **0.39**  
  - T5_VeryLongTtl_6to24h — r ≈ **0.27**  
  - T2_FewHugeMsgs_LowRate — r ≈ **0.24**
- **Más diferentes (top 3)** (menor \|r\|):
  - R9_ExtremeRange_200m — r ≈ **-0.00**  
  - R12_SpeedExtremeHigh — r ≈ **-0.00**  
  - D8_InfrastructureReturns_BackboneLinks — r ≈ **0.00**

Referencias: `analysis/reports/correlation_core23_report.txt` y `analysis/data/correlation_pearson_core23.csv`.

**Interpretación**

La similitud con **R3_WildlifeTracking** está impulsada principalmente por el perfil core: escala comparable de población, velocidades tipo peatón, radio de corto alcance y ausencia de modelos de movimiento estructurados (sin WDM/MapRoute/Cluster/Bus). La similitud casi nula con escenarios de rango o velocidad extremos concuerda con que esos regímenes están dominados por una única “palanca” core (rango o velocidad) que C1 no comparte.

### 9. Asignación de cluster

En el clustering Ward k=7 sobre el espacio core 23 (`analysis/data/cluster_assignments_core23.csv`):

- **Cluster 5** — escenarios tipo campus / densidad moderada en espacio libre (interpretación por composición del cluster).

### 10. Outputs de simulación (opcional)

Si se han ejecutado las simulaciones y se han extraído métricas (`analysis/data/output_metrics.csv`):

| Métrica | Valor |
|--------|-------|
| delivery_ratio | 0.9286 |
| latency_mean | 1863.4769 |
| overhead_ratio | 58.0769 |
| drop_ratio | 33.7143 |

**Interpretación**

El delivery ratio alto es consistente con densidad moderada y buffers grandes bajo enrutamiento Epidemic. El overhead ratio también es esperable porque el flooding replica agresivamente durante las olas de contacto, generando transmisiones redundantes. La latencia refleja el ritmo de mezcla periódico: muchas entregas ocurren en la siguiente ola y no inmediatamente.
