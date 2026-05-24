## Escenario C6 — C6_EmergencyDrill_Evacuation

### 1. Visión general

- **Scenario ID:** C6  
- **Nombre:** C6_EmergencyDrill_Evacuation  
- **Familia:** Campus  
- **Fichero settings:** `corpus_v1/02_campus/C6_EmergencyDrill_Evacuation.settings`

**Objetivo**

Este escenario modela un **simulacro de emergencia / evacuación** con **movimiento rápido y direccional hacia una salida**. A diferencia del resto de escenarios campus que usan RandomWaypoint en espacio libre, aquí se usa **LinearMovement** para que la multitud se desplace como por un pasillo: desde un lado (entrada) hacia un objetivo en el extremo opuesto (salida), generando contactos transitorios y estructurados durante el flujo de evacuación.

### 2. Configuración del escenario (features core)

Los valores provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 200000.0 | 500 m × 400 m |
| aspect_ratio | 0.8 | min(500,400)/max(500,400) |
| N | 80 | 80 nodos móviles |
| nrofHostGroups | 1 | Un único host group |
| speed_mean | 3.0 | Media 2.0–4.0 m/s (corriendo) |
| wait_mean | 5.0 | Media 0–10 s |
| mm_WDM | 0 | Sin WorkingDayMovement |
| mm_RWP | 0 | Sin RandomWaypoint |
| mm_MapRoute | 0 | Sin rutas en mapa |
| mm_Cluster | 0 | Sin ClusterMovement |
| mm_Bus | 0 | Sin BusMovement |
| mm_Linear | 1 | LinearMovement (evacuación direccional) |
| transmitRange | 10.0 | Radio de corto alcance |
| bufferSize | 50,000,000.0 | Buffers 50 MB |
| transmitSpeed | 2,000,000.0 | 2 MB/s |
| msgTtl | 10000.0 | TTL 10,000 (unidades; largo vs 2 h) |
| event_interval_mean | 20.0 | Media 10–30 s entre mensajes |
| event_size_mean | 30000.0 | Media 10k–50k (≈30 kB) |
| nrof_event_generators | 1 | Un flujo (Events1) |
| pattern_burst | 0 | Sin bursts por ventanas temporales |
| pattern_hub_target | 0 | Sin destinos tipo hub |
| workDayLength | — | No aplica (no WDM) |
| ownCarProb | — | No aplica (no WDM/vehicular) |
| clusterRange_mean | — | No aplica (no ClusterMovement) |

### 3. Modelo de movilidad

C8 usa **LinearMovement** en un mundo 500×400 m:

- Los nodos se mueven en una línea desde `startLocation = (50,200)` hacia `endLocation = (450,200)`.  
- `targetType = 1` sesga el movimiento hacia el extremo final (objetivo de evacuación).  
- Velocidades altas (2–4 m/s) y pausas casi nulas (0–10 s), de modo que la población “fluye” rápidamente hacia la salida.
- Duración del escenario **7 200 s (2 h)**.

**Implicación DTN**

El movimiento direccional genera **contactos transitorios y estructurados**: nodos co-mueven, comparten vecindarios durante un tiempo breve y luego se separan. Frente a mezcla aleatoria, la diversidad de caminos puede ser menor y las ventanas de forwarding más cortas, aunque la duración de contacto durante co-movimiento puede bastar para mensajes pequeños.

### 4. Patrón de tráfico

Tráfico mediante un único `MessageEventGenerator` (`Events1`):

- **Intervalo**: 10–30 s (media ≈ 20 s).  
- **Tamaño**: 10k–50k (media ≈ 30 kB).  
- **Fuentes/destinos**: aleatorios entre 80 nodos.

**Implicación DTN**

Con movimiento rápido y pausas cortas, el forwarding depende de si se forman contactos durante el flujo de evacuación. Los tamaños pequeños mejoran la entregabilidad bajo contactos breves; el TTL largo reduce el peso de la expiración frente a la estructura de movilidad.

### 5. Comportamiento de red esperado

- **Oportunidades de forwarding de corta duración:** los contactos los impone el flujo de evacuación, no mezcla estable.  
- **Entrega moderada plausible:** el co-movimiento permite transferencias, pero la separación direccional reduce diversidad multi-salto.  
- **Overhead alto posible con Epidemic:** el flooding replica fuerte cuando grupos co-móviles se encuentran.  
- **Latencia baja para mensajes tempranos:** inyecciones al principio pueden difundirse durante el flujo; mensajes tardíos pueden tener menos oportunidades.

### 6. Rol dentro del corpus

Este escenario se incluye como caso campus de **evacuación direccional**:

- introduce **LinearMovement** (mm_Linear=1), ausente en el resto de campus,
- tensiona contactos rápidos y transitorios a alta velocidad,
- contrasta estructuralmente con los campus RandomWaypoint (C1–C4, C2/C3/C7).

### 7. Características distintivas

- **Flujo de evacuación con LinearMovement** (start→end, `targetType=1`) en vez de mezcla aleatoria.  
- **Velocidad muy alta** (2–4 m/s) y **pausas casi nulas** (0–10 s).  
- **Mensajes pequeños** (10–50 kB) con tasa relativamente alta (10–30 s).  
- Escenario corto (2 h) que modela una ventana de simulacro.

### 8. Correlación con otros escenarios (core 23)

Usando el espacio de **23 features core** (`analysis/data/correlation_pearson_core23.csv`):

- **Más similares (top 3):**
  - S2_WeakCommunities_HighMixing — r ≈ **0.15**  
  - R2_VillagesTrails_ThreeClusters — r ≈ **0.01**  
  - T10_HighRateLowSpeed_Congestion — r ≈ **0.01**
- **Más diferentes (top 3):**
  - R11_SpeedExtremeLow — r ≈ **-0.19**  
  - R1_Rural_RandomWaypoint — r ≈ **-0.19**  
  - R3_WildlifeTracking — r ≈ **-0.18**

**Interpretación**

En general las correlaciones son bajas porque C8 combina un **modelo de movilidad poco común (LinearMovement)** con **velocidad extrema** y pausas casi nulas, haciendo su perfil core muy distinto. Las correlaciones más negativas aparecen frente a regímenes lentos o rurales dispersos, reflejando condiciones de movilidad opuestas.

### 9. Asignación de cluster

En el clustering Ward k=7 sobre el espacio core 23 (`analysis/data/cluster_assignments_core23.csv`):

- **Cluster 7** — escenarios de estrés / outliers (interpretación a nivel de cluster; C8 agrupa con varios regímenes extremos en el clustering core23).

### 10. Outputs de simulación (opcional)

Si se han ejecutado las simulaciones y se han extraído métricas (`analysis/data/output_metrics.csv`):

| Métrica | Valor |
|--------|-------|
| delivery_ratio | 0.5081 |
| latency_mean | 0.4399 |
| overhead_ratio | 77.2128 |
| drop_ratio | 0.0 |

**Interpretación**

La entrega moderada es coherente con contactos breves y estructurados bajo flujo de evacuación. La latencia media extremadamente baja sugiere que los mensajes que se entregan tienden a hacerlo muy rápido durante el flujo (efecto de selección), mientras que otros no llegan a entregarse. El overhead alto es coherente con replicación Epidemic cuando grupos co-móviles se encuentran; drop 0 sugiere buffers suficientes para la carga entregada/replicada en esta ejecución.
