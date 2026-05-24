## Escenario {{ID}} — {{Name}}

### 1. Visión general

- **Scenario ID:** {{ID}}  
- **Nombre:** {{Name}}  
- **Familia:** {{Family}}  
- **Fichero settings:** `{{SettingsPath}}`

**Objetivo**

Descripción corta de qué modela el escenario y por qué existe en el corpus.

### 2. Configuración del escenario (features core)

Valores de `analysis/data/features.csv` (raw) mapeados al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | {{value}} | p. ej. Wx×Wy (m²) |
| aspect_ratio | {{value}} | min(Wx,Wy)/max(Wx,Wy) (0–1] |
| N | {{value}} | Número de nodos |
| nrofHostGroups | {{value}} | Número de grupos |
| speed_mean | {{value}} | Velocidad media (m/s) |
| wait_mean | {{value}} | Espera media (s) |
| mm_WDM | {{0/1}} | WorkingDayMovement presente |
| mm_RWP | {{0/1}} | RandomWaypoint presente |
| mm_MapRoute | {{0/1}} | MapRoute presente |
| mm_Cluster | {{0/1}} | ClusterMovement presente |
| mm_Bus | {{0/1}} | BusMovement presente |
| mm_Linear | {{0/1}} | LinearMovement presente |
| transmitRange | {{value}} | Rango transmisión (m) |
| bufferSize | {{value}} | Buffer (bytes) |
| transmitSpeed | {{value}} | Velocidad transmisión (bytes/s) |
| msgTtl | {{value}} | TTL (unidades o s/h) |
| event_interval_mean | {{value}} | Intervalo medio entre mensajes |
| event_size_mean | {{value}} | Tamaño medio (bytes) |
| nrof_event_generators | {{value}} | Nº de generadores |
| pattern_burst | {{0/1}} | Tráfico en ventanas (burst) |
| pattern_hub_target | {{0/1}} | Tráfico hacia hubs |
| workDayLength | {{value/—}} | Duración workday (s/h) o no aplica |
| ownCarProb | {{value/—}} | Prob. coche o no aplica |
| clusterRange_mean | {{value/—}} | Radio medio cluster (m) o no aplica |

### 3. Modelo de movilidad

Descripción “en humano”: modelo(s), cómo se mueven los nodos, ritmo (si aplica).

**Implicación DTN**

Qué implica esta movilidad en contactos, diversidad de caminos, cuellos de botella (1–3 frases).

### 4. Patrón de tráfico

Quién genera mensajes, intervalo/tasa, tamaños, destinos (uniform/burst/hub), uno o dos streams.

**Implicación DTN**

Qué implica este patrón en oportunidades de reenvío, carga ofrecida, ventanas fáciles/difíciles (1–3 frases).

### 5. Comportamiento de red esperado

- Bullet 1: oportunidades de contacto (periodicidad, mezcla, escasez).  
- Bullet 2: entrega (alta/baja plausible y por qué).  
- Bullet 3: overhead (esperado por replicación/contactos).  
- Bullet 4: latencia (escala y relación con movilidad/tráfico).

### 6. Rol dentro del corpus

Este escenario se incluye como **{{rol}}** con:

- característica 1 (p. ej. densidad, periodicidad, restricciones).  
- característica 2.  
- característica 3.

Se usa para comparar / tensionar … (contra qué otros escenarios o qué aspecto DTN).

### 7. Características distintivas

- Bullet 1.  
- Bullet 2.  
- Bullet 3 (opcional).

### 8. Correlación con otros escenarios (core 23)

Usando `analysis/data/correlation_pearson_core23.csv`:

- **Más similares (top 3):**
  - {{Escenario}} — r ≈ **{{valor}}**
  - {{Escenario}} — r ≈ **{{valor}}**
  - {{Escenario}} — r ≈ **{{valor}}**
- **Más diferentes (top 3)** (menor \|r\|):
  - {{Escenario}} — r ≈ **{{valor}}**
  - {{Escenario}} — r ≈ **{{valor}}**
  - {{Escenario}} — r ≈ **{{valor}}**

Referencias: `analysis/reports/correlation_core23_report.txt`, `analysis/data/correlation_pearson_core23.csv`.

**Interpretación**

Por qué los más similares comparten perfil core (movilidad, tráfico, recursos); por qué los más diferentes no comparten las “palancas” de este escenario (1–3 frases).

### 9. Asignación de cluster

En el clustering Ward k=7 sobre el espacio core 23 (`analysis/data/cluster_assignments_core23.csv`):

- **Cluster {{id}}** — descripción corta del cluster (p. ej. campus estancias largas, urbano WDM, estrés tráfico).

### 10. Outputs de simulación (opcional)

Si hay métricas en `analysis/data/output_metrics.csv`:

| Métrica | Valor |
|--------|-------|
| delivery_ratio | {{value}} |
| latency_mean | {{value}} |
| overhead_ratio | {{value}} |
| drop_ratio | {{value}} |

**Interpretación**

Coherencia (o no) del delivery/overhead/latencia con la movilidad y el tráfico del escenario (1–3 frases).
