## Escenario C3 — C3_Hackathon_24h

### 1. Visión general

- **Scenario ID:** C3  
- **Nombre:** C3_Hackathon_24h  
- **Familia:** Campus  
- **Fichero settings:** `corpus_v1/02_campus/C3_Hackathon_24h.settings`

**Objetivo**

Este escenario modela un **hackathon de 24 horas** en un campus: los participantes permanecen en mesas o zonas de trabajo durante periodos largos (20–60 min) con movilidad muy baja, y la simulación dura **24 horas** (86 400 s). Captura **presencia continua**, actividad nocturna y mezcla local en un mismo espacio. Las palancas son tiempos de espera largos, velocidad muy baja y duración extendida de la simulación, tensionando store-carry-forward a lo largo de un día completo con movimiento escaso.

### 2. Configuración del escenario (features core)

Los valores provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 480000.0 | 800 m × 600 m (campus) |
| aspect_ratio | 0.75 | min(800,600)/max(800,600) |
| N | 40 | 40 nodos móviles |
| nrofHostGroups | 1 | Un único host group |
| speed_mean | 0.25 | Media 0.1–0.4 m/s (muy lento, mesa/descanso) |
| wait_mean | 2400.0 | Media 1200–3600 s (20–60 min en un lugar) |
| mm_WDM | 0 | Sin WorkingDayMovement |
| mm_RWP | 1 | RandomWaypoint |
| mm_MapRoute | 0 | Sin rutas en mapa |
| mm_Cluster | 0 | Sin ClusterMovement |
| mm_Bus | 0 | Sin BusMovement |
| mm_Linear | 0 | Sin LinearMovement |
| transmitRange | 11.0 | Alcance corto tipo Bluetooth |
| bufferSize | 46000000.0 | Buffers 46 MB |
| transmitSpeed | 2350000.0 | 2.35 MB/s |
| msgTtl | 3200.0 | TTL (unidades de simulación; largo, escala hackathon) |
| event_interval_mean | 210.0 | Media 120–300 s entre mensajes |
| event_size_mean | 100000.0 | 100 kB |
| nrof_event_generators | 1 | Un flujo (Events1) |
| pattern_burst | 0 | Sin bursts por ventanas temporales |
| pattern_hub_target | 0 | Sin destinos tipo hub |
| workDayLength | — | No aplica (no WDM) |
| ownCarProb | — | No aplica (no WDM/vehicular) |
| clusterRange_mean | — | No aplica (no ClusterMovement) |

### 3. Modelo de movilidad

C3 usa **RandomWaypoint** en 800×600 m con **palancas de hackathon**:

- **Velocidad** 0.1–0.4 m/s: movimiento muy lento (entre mesas, zona de descanso, vuelta).  
- **Tiempo de espera** 1200–3600 s (20–60 min): estancias largas en un mismo sitio (trabajo o descanso).  
- **Duración de simulación** 86 400 s (24 h): actividad continua durante la noche; oportunidades de contacto y tráfico se extienden todo el día.

Un único host group, 40 nodos homogéneos, sin mapa ni hotspots.

**Implicación DTN**

Velocidad muy baja y pausas largas **reducen mucho las oportunidades de contacto** y **aumentan el peso del store-carry-forward**. La mezcla es local e infrecuente; los mensajes pueden permanecer en buffer mucho tiempo. El horizonte de 24 h permite entregas tardías que en escenarios más cortos expirarían, pero la latencia puede ser alta.

### 4. Patrón de tráfico

El tráfico lo genera un único **MessageEventGenerator** (`Events1`):

- **Intervalo**: `Events1.interval = 120, 300` → media ≈ **210 s** entre mensajes por fuente (tasa moderada).  
- **Tamaño**: `Events1.size = 50k, 150k` → media ≈ **100 kB**.  
- **Fuentes/destinos**: `Events1.hosts = 0, 40` (todos los nodos pueden participar; destinos aleatorios).

Tráfico **moderado y regular** a lo largo de las 24 h; sin ventanas de burst ni destinos hub. El TTL largo (3200) permite que los mensajes permanezcan en la red muchas horas, así que la entrega depende de las escasas fases de movimiento.

**Implicación DTN**

La carga ofrecida es **moderada** frente a contactos **muy escasos**, por lo que la presión en buffers es menor que en C2, pero la entrega sigue dependiendo del reenvío en las pocas ventanas de mezcla. El TTL largo reduce drops por expiración y permite entregas tardías, a costa de latencia media alta.

### 5. Comportamiento de red esperado

- **Oportunidades de contacto escasas y ocasionales:** estancias largas y velocidad muy baja; la mezcla ocurre sobre todo cuando los nodos se mueven entre “sesiones”.  
- **Entrega moderada** plausible: TTL largo y 24 h dan margen al store-carry-forward, pero los contactos limitados acotan el throughput.  
- **Overhead** moderado: la replicación está limitada por pocos contactos.  
- **Latencia alta** esperable: muchos mensajes esperan mucho hasta el siguiente encuentro, por lo que la latencia media puede ser del orden de miles de segundos.

### 6. Rol dentro del corpus

Este escenario se incluye como **variante campus hackathon 24 h** con:

- movilidad muy baja (0.1–0.4 m/s, esperas 20–60 min),
- **simulación de 24 h** (distinta del baseline campus de 12 h),
- TTL largo (3200) y tasa de tráfico moderada.

Se usa para comparar el comportamiento **duración extendida / baja movilidad** con día de exámenes (C2), biblioteca (C7) y cambio de clase (C1), y para tensionar protocolos a lo largo de un día completo de mezcla escasa.

### 7. Características distintivas

- **Ejecución de 24 h** (Scenario.endTime = 86 400 s): único escenario campus con duración de día completo.  
- **Tiempos de espera muy largos** (20–60 min) y **velocidad muy baja** (0.1–0.4 m/s): semántica de hackathon en mesa.  
- **TTL largo (3200)** para que los mensajes persistan a lo largo de muchos ciclos de movimiento.  
- Mismo **RandomWaypoint en espacio libre**, un grupo y un flujo que C1/C2; se diferencia por duración y por pausa/velocidad extremas.

### 8. Correlación con otros escenarios (core 23)

Usando el espacio de **23 features core** (`analysis/data/correlation_pearson_core23.csv`):

- **Más similares (top 3):**
  - C2_ExamDay_LongStays — r ≈ **0.91**  
  - C5_Library_Quiet — r ≈ **0.88**  
  - R3_WildlifeTracking — r ≈ **0.69**
- **Más diferentes (top 3)** (menor \|r\|):
  - D2_PartitionedCity_MuleBridge — r ≈ **0.00**  
  - T2_FewHugeMsgs_LowRate — r ≈ **0.00**  
  - R9_ExtremeRange_200m — r ≈ **-0.01**

Referencias: `analysis/reports/correlation_core23_report.txt` y `analysis/data/correlation_pearson_core23.csv`.

**Interpretación**

La alta similitud con **C2** y **C7** se debe al perfil compartido: campus, RandomWaypoint, estancias largas, escala de nodos y régimen de tráfico comparables. Los tres tensionan **baja movilidad y presencia prolongada**. La similitud con **R3** viene de velocidad/espera y movilidad en espacio libre comparables. La correlación casi nula con D2, T2 y R9 refleja palancas distintas: ciudad particionada con mulas, tráfico dominado por pocos mensajes grandes o rango extremo, que no coinciden con el perfil de C3 (duración larga, baja movilidad).

### 9. Asignación de cluster

En el clustering Ward k=7 sobre el espacio core 23 (`analysis/data/cluster_assignments_core23.csv`):

- **Cluster 7** — escenarios de estancias largas / baja movilidad / estrés (con C2, C5, C6, R1, R3 y varios T/D).

### 10. Outputs de simulación (opcional)

Si se han ejecutado las simulaciones y se han extraído métricas (`analysis/data/output_metrics.csv`):

| Métrica | Valor |
|--------|-------|
| delivery_ratio | 0.5561 |
| latency_mean | 10912.98 |
| overhead_ratio | 39.18 |
| drop_ratio | 20.71 |

**Interpretación**

La **entrega moderada** es coherente con contactos escasos pero TTL largo: muchos mensajes acaban teniendo oportunidad de reenvío a lo largo de las 24 h. La **latencia media alta** (≈10 900 s) refleja esperas largas entre contactos. El **overhead** es moderado porque la replicación está limitada por pocas oportunidades de contacto. El **drop ratio** indica una fracción no despreciable de mensajes que expiran o se descartan pese al TTL largo, en línea con la movilidad muy baja.
