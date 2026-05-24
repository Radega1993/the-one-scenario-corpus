## Escenario C5 — C5_Library_Quiet

### 1. Visión general

- **Scenario ID:** C5  
- **Nombre:** C5_Library_Quiet  
- **Familia:** Campus  
- **Fichero settings:** `corpus_v1/02_campus/C5_Library_Quiet.settings`

**Objetivo**

Este escenario modela una **biblioteca tranquila**: las personas permanecen sentadas largos periodos con movimientos pequeños e infrecuentes, generando contactos escasos pero potencialmente largos. Es una variante campus de baja movilidad diseñada para contrastar con escenarios de oleadas (C1) y de bursts por ventanas (C4), enfatizando store-carry-forward durante estancias largas con tráfico moderado.

### 2. Configuración del escenario (features core)

Los valores provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 247500.0 | 550 m × 450 m (biblioteca) |
| aspect_ratio | 0.818 | min(550,450)/max(550,450) |
| N | 42 | 42 nodos móviles |
| nrofHostGroups | 1 | Un único host group |
| speed_mean | 0.2 | Media 0.1–0.3 m/s (muy lento) |
| wait_mean | 1200.0 | Media 600–1800 s (10–30 min) |
| mm_WDM | 0 | Sin WorkingDayMovement |
| mm_RWP | 1 | RandomWaypoint |
| mm_MapRoute | 0 | Sin rutas en mapa |
| mm_Cluster | 0 | Sin ClusterMovement |
| mm_Bus | 0 | Sin BusMovement |
| mm_Linear | 0 | Sin LinearMovement |
| transmitRange | 7.0 | Rango corto (tipo biblioteca) |
| bufferSize | 54,000,000.0 | Buffers 54 MB |
| transmitSpeed | 1,700,000.0 | 1.7 MB/s |
| msgTtl | 6800.0 | TTL largo (escala sesión de estudio) |
| event_interval_mean | 60.0 | Media 40–80 s entre mensajes |
| event_size_mean | 100000.0 | 100 kB |
| nrof_event_generators | 1 | Un flujo (Events1) |
| pattern_burst | 0 | Sin bursts por ventanas |
| pattern_hub_target | 0 | Sin destinos tipo hub |
| workDayLength | — | No aplica (no WDM) |
| ownCarProb | — | No aplica (no WDM/vehicular) |
| clusterRange_mean | — | No aplica (no ClusterMovement) |

### 3. Modelo de movilidad

C7 usa **RandomWaypoint** en un área 550×450 m con palancas de baja movilidad:

- Velocidad 0.1–0.3 m/s (andar lento).  
- Tiempo de espera 600–1800 s (10–30 min) representando sesiones largas sentado/estudiando.

Un único host group; sin rutas en mapa ni hotspots.

**Implicación DTN**

Las pausas largas reducen la frecuencia de encuentros, pero cuando hay contactos pueden durar más (nodos cercanos durante estancias), permitiendo transferencias pese a baja velocidad. Este régimen tiende a **latencias altas** y hace que la entrega dependa de fases raras de movimiento y de persistencia de contacto.

### 4. Patrón de tráfico

Tráfico mediante un único `MessageEventGenerator` (`Events1`):

- Intervalo 40–80 s (media ≈ 60 s).  
- Tamaño 50k–150k (media ≈ 100 kB).  
- Fuentes/destinos aleatorios entre 42 nodos.

**Implicación DTN**

La carga ofrecida es moderada, pero la baja movilidad limita las oportunidades de forwarding. El TTL largo permite que los mensajes persistan a través de varios ciclos de estudiar/moverse, por lo que la entrega es posible pero suele retrasarse.

### 5. Comportamiento de red esperado

- **Oportunidades de contacto escasas:** dominan las estancias largas; mezcla limitada.  
- **Entrega moderada-alta plausible con TTL largo** si los contactos persisten, aunque la baja movilidad limita throughput.  
- **Overhead moderado:** la replicación está limitada por pocos encuentros.  
- **Latencia alta esperable:** muchos mensajes esperan al siguiente episodio de movimiento/contacto.

### 6. Rol dentro del corpus

Este escenario se incluye como caso campus de **estancia larga “quiet”** con:

- movilidad muy baja (0.1–0.3 m/s, esperas 10–30 min),
- tráfico moderado (intervalo medio ≈60 s),
- TTL largo (6800).

Complementa día de exámenes (C2) y hackathon (C3) aportando un baseline “tranquilo” de estancias largas, y ayuda a separar efectos de estancia larga frente a otras palancas (bursts, oleadas periódicas, evacuación direccional).

### 7. Características distintivas

- Baja movilidad con esperas largas (semántica biblioteca).  
- Rango de transmisión más pequeño (7 m) que otros campus.  
- TTL largo y tasa de mensajes moderada.  
- RandomWaypoint en espacio libre, un grupo (baseline limpio de campus long-stay).

### 8. Correlación con otros escenarios (core 23)

Usando el espacio de **23 features core** (`analysis/data/correlation_pearson_core23.csv`):

- **Más similares (top 3):**
  - C3_Hackathon_24h — r ≈ **0.88**  
  - C2_ExamDay_LongStays — r ≈ **0.83**  
  - R3_WildlifeTracking — r ≈ **0.60**
- **Más diferentes (top 3):**
  - U2_SparseSuburb_HelsinkiMedium — r ≈ **-0.50**  
  - U1_CBD_Commuting_HelsinkiMedium — r ≈ **-0.46**  
  - U4_CongestionHotspot_HelsinkiMedium — r ≈ **-0.41**

**Interpretación**

La similitud con **C2/C3** está impulsada por el régimen compartido de estancias largas y baja velocidad en campus. La similitud con **R3** viene del perfil de baja movilidad en espacio libre. La correlación negativa con escenarios urbanos WDM refleja una estructura de movimiento totalmente distinta (commuting y patrones guiados por mapa frente a estancias tranquilas prolongadas).

### 9. Asignación de cluster

En el clustering Ward k=7 sobre el espacio core 23 (`analysis/data/cluster_assignments_core23.csv`):

- **Cluster 7** — escenarios de estancias largas / baja movilidad / estrés (incluye C2/C3/C7/C8, entre otros).

### 10. Outputs de simulación (opcional)

Si se han ejecutado las simulaciones y se han extraído métricas (`analysis/data/output_metrics.csv`):

| Métrica | Valor |
|--------|-------|
| delivery_ratio | 0.6556 |
| latency_mean | 9614.211 |
| overhead_ratio | 42.5506 |
| drop_ratio | 22.9225 |

**Interpretación**

La entrega moderada-alta es coherente con TTL largo y con contactos que, cuando ocurren, pueden durar lo suficiente para transferencias. La latencia media alta refleja pausas largas y mezcla infrecuente. El overhead es moderado porque la replicación está limitada por pocos encuentros; el drop ratio indica que, pese al TTL largo, las oportunidades limitadas y la dinámica de buffers siguen generando pérdidas no triviales.
