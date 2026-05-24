## Escenario C2 — C2_ExamDay_LongStays

### 1. Visión general

- **Scenario ID:** C2  
- **Nombre:** C2_ExamDay_LongStays  
- **Familia:** Campus  
- **Fichero settings:** `corpus_v1/02_campus/C2_ExamDay_LongStays.settings`

**Objetivo**

Este escenario modela **dinámicas de día de exámenes en un campus**: pocas sesiones con **estancias largas** en aulas de examen (baja movilidad, esperas largas) y movimiento lento entre ubicaciones. Los nodos permanecen en sitio 10–30 minutos y luego se mueven despacio al siguiente lugar. Proporciona una variante de campus **baja movilidad / alta pausa** frente al baseline de cambio de clase (C1), tensionando store-carry-forward y las escasas oportunidades de contacto durante las ventanas de examen.

### 2. Configuración del escenario (features core)

Los valores provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 412500.0 | 750 m × 550 m (campus) |
| aspect_ratio | 0.733 | min(750,550)/max(750,550) |
| N | 48 | 48 nodos móviles |
| nrofHostGroups | 1 | Un único host group |
| speed_mean | 0.35 | Media 0.2–0.5 m/s (movimiento lento tipo examen) |
| wait_mean | 1200.0 | Media 600–1800 s (10–30 min en sala) |
| mm_WDM | 0 | Sin WorkingDayMovement |
| mm_RWP | 1 | RandomWaypoint |
| mm_MapRoute | 0 | Sin rutas en mapa |
| mm_Cluster | 0 | Sin ClusterMovement |
| mm_Bus | 0 | Sin BusMovement |
| mm_Linear | 0 | Sin LinearMovement |
| transmitRange | 13.0 | Alcance corto, algo mayor que C1 |
| bufferSize | 48000000.0 | Buffers 48 MB |
| transmitSpeed | 1900000.0 | 1.9 MB/s |
| msgTtl | 60.0 | TTL 60 (unidades de simulación, ~1 h) |
| event_interval_mean | 90.0 | Media 60–120 s entre mensajes (tasa más alta que C1) |
| event_size_mean | 100000.0 | 100 kB |
| nrof_event_generators | 1 | Un flujo (Events1) |
| pattern_burst | 0 | Sin bursts por ventanas temporales |
| pattern_hub_target | 0 | Sin destinos tipo hub |
| workDayLength | — | No aplica (no WDM) |
| ownCarProb | — | No aplica (no WDM/vehicular) |
| clusterRange_mean | — | No aplica (no ClusterMovement) |

### 3. Modelo de movilidad

C2 usa **RandomWaypoint** en un área 750×550 m con **palancas de día de exámenes**:

- **Velocidad** 0.2–0.5 m/s: movimiento muy lento (pasillos, entrada/salida de aulas).  
- **Tiempo de espera** 600–1800 s (10–30 min): estancias largas en un mismo sitio, simulando tiempo en sesión de examen.  
- Los nodos eligen waypoints uniformemente; las pausas largas dominan la época, por lo que la movilidad es **baja** respecto a C1.

Un único host group, 48 nodos homogéneos, sin mapa ni hotspots.

**Implicación DTN**

Velocidad baja y pausas largas **reducen las oportunidades de contacto** y **aumentan la dependencia del store-carry-forward**. La diversidad de caminos es limitada; mensajes creados durante una estancia larga solo pueden reenviarse cuando los nodos vuelven a moverse. Esto tensiona protocolos que asumen mezcla más frecuente.

### 4. Patrón de tráfico

El tráfico lo genera un único **MessageEventGenerator** (`Events1`):

- **Intervalo**: `Events1.interval = 60, 120` → media ≈ **90 s** entre mensajes por fuente (tasa más alta que C1).  
- **Tamaño**: `Events1.size = 50k, 150k` → media ≈ **100 kB**.  
- **Fuentes/destinos**: `Events1.hosts = 0, 48` (todos los nodos pueden participar; destinos aleatorios).

Es decir, **tasa de tráfico más alta** con **movilidad más baja**: más mensajes ofrecidos en periodos con contactos relativamente escasos, aumentando contención y dependencia de buffer y TTL.

**Implicación DTN**

La combinación de **carga ofrecida alta** (intervalo medio 90 s) y **oportunidades de contacto escasas** (estancias largas, movimiento lento) tiende a aumentar presión en buffers y riesgo de drop, sobre todo con **TTL corto (60)**. La entrega depende mucho de que los mensajes puedan reenviarse en la siguiente ventana de movilidad.

### 5. Comportamiento de red esperado

- **Oportunidades de contacto escasas:** pausas largas y velocidad baja reducen la mezcla; muchos contactos solo cuando los nodos se mueven entre “sesiones”.  
- **Entrega moderada-baja** plausible: ventanas de reenvío limitadas y TTL corto pueden hacer que los mensajes expiren antes de llegar.  
- **Overhead** moderado si la replicación ocurre sobre todo en las fases breves de mezcla.  
- **Latencia** puede ser alta cuando los mensajes se crean en una estancia larga y deben esperar a la siguiente fase de movimiento.

### 6. Rol dentro del corpus

Este escenario se incluye como **variante campus día de exámenes** con:

- baja movilidad (velocidad lenta, esperas largas),
- tasa de tráfico más alta que C1 (90 s frente a ~50 min de intervalo medio),
- TTL corto (60) y misma familia (Campus, RandomWaypoint, espacio libre).

Se usa para comparar el comportamiento **baja movilidad / alta pausa** con el baseline de cambio de clase (C1) y con otros escenarios de campus (hackathon, biblioteca, estadio), y para tensionar store-carry-forward y sensibilidad a buffer/TTL.

### 7. Características distintivas

- **Tiempos de espera muy largos** (10–30 min) y **velocidad muy baja** (0.2–0.5 m/s): semántica de aula de examen.  
- **TTL corto (60)** respecto a las pausas largas: los mensajes deben entregarse en un tiempo limitado.  
- **Un único flujo de tráfico** con **tasa más alta** que C1, aumentando la carga en contactos escasos.  
- Mismo **RandomWaypoint en espacio libre** y **un solo grupo** que C1, pero con estrés opuesto: estructura temporal dominada por estancias largas en lugar de oleadas periódicas.

### 8. Correlación con otros escenarios (core 23)

Usando el espacio de **23 features core** (`analysis/data/correlation_pearson_core23.csv`):

- **Más similares (top 3):**
  - C3_Hackathon_24h — r ≈ **0.91**  
  - C5_Library_Quiet — r ≈ **0.83**  
  - D3_Aftershock_ErraticMobility — r ≈ **0.64**
- **Más diferentes (top 3)** (menor \|r\|):
  - T15_TransmitSpeed_256k — r ≈ **-0.01**  
  - T10_HighRateLowSpeed_Congestion — r ≈ **0.01**  
  - T7_TargetedToHubs_FewDestinations — r ≈ **-0.01**

Referencias: `analysis/reports/correlation_core23_report.txt` y `analysis/data/correlation_pearson_core23.csv`.

**Interpretación**

La alta similitud con **C3_Hackathon_24h** y **C5_Library_Quiet** se explica por el perfil core compartido: misma familia campus, RandomWaypoint, espacio libre, escala de nodos similar y tráfico/intervalo en un régimen comparable. Los tres tienen estancias largas o presencia sostenida (examen, hackathon, biblioteca). La correlación casi nula con T15/T10/T7 refleja palancas distintas (velocidad de transmisión, congestión, tráfico hub-target) que no coinciden con el diseño de C2 centrado en movilidad y espera.

### 9. Asignación de cluster

En el clustering Ward k=7 sobre el espacio core 23 (`analysis/data/cluster_assignments_core23.csv`):

- **Cluster 7** — escenarios de estancias largas / baja movilidad / estrés (interpretación por composición: C2, C3, C5, C6, R1, R3, varios T y D).

### 10. Outputs de simulación (opcional)

Si se han ejecutado las simulaciones y se han extraído métricas (`analysis/data/output_metrics.csv`):

| Métrica | Valor |
|--------|-------|
| delivery_ratio | 0.2857 |
| latency_mean | 2354.73 |
| overhead_ratio | 42.62 |
| drop_ratio | 12.79 |

**Interpretación**

El **delivery ratio bajo** es coherente con oportunidades de contacto escasas y TTL corto: muchos mensajes expiran o se descartan antes de la entrega. El **overhead** es moderado frente a escenarios de alta mezcla porque la replicación está limitada por menos contactos. La **latencia** refleja la estructura de pausas largas: los mensajes que se entregan suelen esperar a la siguiente fase de movimiento, por lo que la latencia media está en el mismo orden que la escala de espera.
