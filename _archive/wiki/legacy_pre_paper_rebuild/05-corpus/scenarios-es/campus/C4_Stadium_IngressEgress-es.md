## Escenario C4 — C4_Stadium_IngressEgress

### 1. Visión general

- **Scenario ID:** C4  
- **Nombre:** C4_Stadium_IngressEgress  
- **Familia:** Campus  
- **Fichero settings:** `corpus_v1/02_campus/C4_Stadium_IngressEgress.settings`

**Objetivo**

Este escenario modela un **evento de estadio con olas de entrada y salida**: la multitud llega, se mezcla durante una ventana corta previa, luego el entorno permanece relativamente tranquilo, y finalmente ocurre una segunda ola en la salida. La palanca clave son **dos picos de tráfico en ventanas temporales** (ingress + egress), diseñados para crear oportunidades DTN cortas e intensas separadas por un periodo largo de baja actividad.

### 2. Configuración del escenario (features core)

Los valores provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 800000.0 | 1000 m × 800 m (área estadio) |
| aspect_ratio | 0.8 | min(1000,800)/max(1000,800) |
| N | 80 | 80 nodos móviles (multitud) |
| nrofHostGroups | 1 | Un único host group |
| speed_mean | 0.85 | Media 0.5–1.2 m/s (caminando) |
| wait_mean | 105.0 | Media 30–180 s |
| mm_WDM | 0 | Sin WorkingDayMovement |
| mm_RWP | 1 | RandomWaypoint |
| mm_MapRoute | 0 | Sin rutas en mapa |
| mm_Cluster | 0 | Sin ClusterMovement |
| mm_Bus | 0 | Sin BusMovement |
| mm_Linear | 0 | Sin LinearMovement |
| transmitRange | 9.0 | Radio de corto alcance |
| bufferSize | 43,000,000.0 | Buffers 43 MB |
| transmitSpeed | 2,350,000.0 | 2.35 MB/s |
| msgTtl | 7200.0 | TTL 7200 (unidades de simulación; escala de evento) |
| event_interval_mean | 10.0 | Media 5–15 s durante las ventanas activas |
| event_size_mean | 100000.0 | 100 kB |
| nrof_event_generators | 2 | Dos picos: Events1 + Events2 |
| pattern_burst | 1 | Tráfico por ventanas (Events*.time) |
| pattern_hub_target | 0 | Sin destinos tipo hub |
| workDayLength | — | No aplica (no WDM) |
| ownCarProb | — | No aplica (no WDM/vehicular) |
| clusterRange_mean | — | No aplica (no ClusterMovement) |

### 3. Modelo de movilidad

C4 usa **RandomWaypoint** en un área 1000×800 m:

- Velocidad 0.5–1.2 m/s y esperas cortas (30–180 s) representan movimiento de multitud y paradas breves.  
- No hay rutas en mapa; el movimiento es mezcla en espacio libre dentro de un área acotada.
- La duración del escenario es **10 800 s (3 h)**, coherente con un evento corto.

**Implicación DTN**

Con 80 nodos en 0.8 km² y velocidad moderada, el escenario puede producir **alta oportunidad de contacto** durante las ventanas del evento. Al no haber restricciones por mapa, la conectividad depende de densidad y rango más que de cuellos de botella; esto tiende a amplificar la replicación epidémica cuando hay tráfico.

### 4. Patrón de tráfico

El tráfico lo generan **dos MessageEventGenerators**, creando **dos bursts fuertes**:

- `Events.nrof = 2` con `Events1` y `Events2`.  
- **Burst de entrada (ingress)**: `Events1.time = 0, 900` (primeros 15 min), `Events1.interval = 5, 15` → media ≈ 10 s.  
- **Burst de salida (egress)**: `Events2.time = 6300, 7200` (últimos 15 min), `Events2.interval = 5, 15` → media ≈ 10 s.  
- Tamaño 50k–150k (media ≈ 100 kB); fuentes/destinos aleatorios entre 0..80.

Fuera de esas ventanas, prácticamente no hay generación de mensajes: el escenario alterna fases de **burst de alta carga** y un periodo largo de calma.

**Implicación DTN**

Las ventanas de burst alinean la carga ofrecida con periodos cortos de mezcla intensa, lo que suele producir **entrega muy alta** pero también **overhead muy alto** bajo flooding: la replicación explota cuando contactos y tráfico están al máximo. La pausa larga intermedia actúa como fase de “carry”, donde el reenvío depende de movilidad sin nuevas inyecciones.

### 5. Comportamiento de red esperado

- **Dos ventanas favorables para entrega:** entrada y salida crean oportunidades de forwarding intensas.  
- **Entrega muy alta plausible con Epidemic** durante bursts (densidad alta, esperas cortas).  
- **Overhead muy alto esperable:** dos bursts de alta tasa + replicación epidémica multiplican transmisiones redundantes.  
- **Latencia dependiente del momento:** mensajes creados cerca de una ventana pueden entregarse rápido; si sobreviven al periodo quieto pueden esperar hasta la siguiente ventana.

### 6. Rol dentro del corpus

Este escenario se incluye como caso **burst por ventanas temporales en entorno de multitud** con:

- una multitud grande (N=80) en un área moderada,
- dos ventanas explícitas de tráfico (pattern_burst=1) para representar entrada/salida,
- intervalos muy cortos durante bursts (≈10 s) y un periodo largo de calma.

Sirve como referencia para **carga y mezcla impulsadas por bursts**, complementando oleadas periódicas (C1) y regímenes de estancias largas/baja movilidad (C2/C3).

### 7. Características distintivas

- **Dos picos explícitos de tráfico** mediante `Events1.time` y `Events2.time` (ingress + egress).  
- **Carga instantánea alta** durante bursts (intervalo medio ≈10 s) con dos generadores.  
- Duración corta (3 h) representando un único evento.  
- Multitud mayor (80 nodos) en 1000×800 m frente a otros escenarios de campus.  
- Diseñado para tensionar **tráfico burst** y **overhead epidémico** más que store-carry-forward a largo plazo.

### 8. Correlación con otros escenarios (core 23)

Usando el espacio de **23 features core** (`analysis/data/correlation_pearson_core23.csv`):

- **Más similares (top 3):**
  - T8_BurstTraffic_TimeWindows — r ≈ **0.93**  
  - T3_MixedBimodal_SmallAndLarge — r ≈ **0.48**  
  - D8_InfrastructureReturns_BackboneLinks — r ≈ **0.23**
- **Más diferentes (top 3)** (menor \|r\|):
  - T14_Buffer_200M — r ≈ **0.00**  
  - R8_IntermittentPower — r ≈ **0.00**  
  - C5_Library_Quiet — r ≈ **0.01**

Referencias: `analysis/reports/correlation_core23_report.txt` y `analysis/data/correlation_pearson_core23.csv`.

**Interpretación**

C4 es muy similar a **T8_BurstTraffic_TimeWindows** porque ambos están dominados por la palanca core **pattern_burst** y por intervalos muy cortos durante ventanas activas. La correlación casi nula con escenarios dominados por buffer o disponibilidad (buffers extremos, potencia intermitente) refleja que esas palancas no están presentes aquí; C4 está definido principalmente por **tráfico burst por ventanas** combinado con movilidad moderada de multitud.

### 9. Asignación de cluster

En el clustering Ward k=7 sobre el espacio core 23 (`analysis/data/cluster_assignments_core23.csv`):

- **Cluster 4** — escenarios impulsados por ventanas/bursts (interpretación por composición; incluye patrones tipo T8).

### 10. Outputs de simulación (opcional)

Si se han ejecutado las simulaciones y se han extraído métricas (`analysis/data/output_metrics.csv`):

| Métrica | Valor |
|--------|-------|
| delivery_ratio | 1.0 |
| latency_mean | 2202.4995 |
| overhead_ratio | 77.3057 |
| drop_ratio | 0.0 |

**Interpretación**

La entrega perfecta es coherente con ventanas de burst concentradas y alta oportunidad de contacto, junto con TTL largo relativo a las 3 h de ejecución. El overhead muy alto es esperable con enrutamiento Epidemic cuando los bursts coinciden con mezcla densa: el forwarding redundante se dispara. El drop 0 sugiere que los buffers fueron suficientes para la carga ofrecida en esta configuración.
