## Escenario D4 — D4_MedicalTriage_TwoClasses

### 1. Visión general

- **Scenario ID:** D4  
- **Nombre:** D4_MedicalTriage_TwoClasses  
- **Familia:** Disaster  
- **Fichero settings:** `corpus_v1/05_disaster/D4_MedicalTriage_TwoClasses.settings`

**Objetivo**

Aproximación de triaje médico con dos clases de nodos y dos generadores de tráfico (crítico vs rutinario).

### 2. Configuración del escenario (features core)

Los valores siguientes provienen de `analysis/data/features.csv` (raw) y del mapeo al subconjunto core de 23.

| Feature | Valor | Comentario |
|---------|-------|------------|
| world_area | 24750000 | Área total de simulación (m^2) |
| aspect_ratio | 0.8182 | min(width,height)/max(width,height) |
| N | 50 | Nodos totales |
| nrofHostGroups | 2 | Número de host groups |
| speed_mean | 1.2 | Velocidad media configurada (m/s) |
| wait_mean | 60 | Tiempo medio de pausa/espera (s) |
| mm_WDM | 0 | WorkingDayMovement activo (1/0) |
| mm_RWP | 1 | RandomWaypoint activo (1/0) |
| mm_MapRoute | 0 | MapRouteMovement activo (1/0) |
| mm_Cluster | 0 | ClusterMovement activo (1/0) |
| mm_Bus | 0 | BusMovement activo (1/0) |
| mm_Linear | 0 | LinearMovement activo (1/0) |
| transmitRange | 10 | Alcance de interfaz (m) |
| bufferSize | 50000000 | Node buffer (bytes) |
| transmitSpeed | 2000000 | Velocidad de interfaz (bytes/s) |
| msgTtl | 10 | TTL de mensajes |
| event_interval_mean | 30 | Media del intervalo de Events1 |
| event_size_mean | 4500 | Tamaño medio de Events1 (bytes) |
| nrof_event_generators | 2 | Número de generadores de eventos |
| pattern_burst | 0 | Ventanas burst en tráfico (1/0) |
| pattern_hub_target | 1 | Patrón de tráfico hub-target (1/0) |
| workDayLength | — | No usado en este escenario |
| ownCarProb | — | No usado en este escenario |
| clusterRange_mean | — | Radio medio de cluster si hay ClusterMovement |

### 3. Modelo de movilidad

- **World size:** `5500, 4500`  
- **Rango base de velocidad:** `0.4, 1.4`  
- **Rango base de espera:** `20, 240`

RandomWaypoint con dos host groups y generadores asimétricos bidireccionales.

**Implicación DTN**

Este diseño de movilidad crea un régimen disaster de contacto restringido donde la conectividad depende de puentes temporales, clusters locales densos o relés oportunistas, más que de caminos estables extremo a extremo.

### 4. Patrón de tráfico

- `Events.nrof = 2`  
- `Events1.interval = 15, 45`  
- `Events1.size = 1k, 8k`  
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
  - T7_TargetedToHubs_FewDestinations — r ≈ **0.75**
  - T3_MixedBimodal_SmallAndLarge — r ≈ **0.42**
  - T11_TTL_1min — r ≈ **0.27**
- **Más diferentes (top 3)** (menor |r|):
  - T1_ManySmallMsgs_HighRate — r ≈ **-0.03**
  - C3_Hackathon_24h — r ≈ **-0.03**
  - C5_Library_Quiet — r ≈ **-0.03**

Referencias: `analysis/reports/correlation_core23_report.txt` y `analysis/data/correlation_pearson_core23.csv`.

**Interpretación**

Los escenarios más próximos comparten las mismas palancas estructurales principales (familia de movilidad, estructura de host groups y escala de tráfico), mientras que correlaciones cercanas a cero suelen corresponder a escenarios dominados por factores ortogonales (p. ej., rango/velocidad extremos, map routing o regímenes distintos de TTL/carga).

### 9. Asignación de cluster

En el clustering Ward k=7 sobre el espacio core 23 (`cluster_assignments_core23.csv`), este escenario pertenece a:

- **Cluster 7**.

### 10. Outputs de simulación (opcional)

Si se han ejecutado simulaciones y extraído métricas (`analysis/data/output_metrics.csv`):

| Métrica | Valor |
|---------|-------|
| delivery_ratio | 0.0175 |
| latency_mean | 21161.86 |
| overhead_ratio | 33.8333 |
| drop_ratio | 0.8674065420560748 |

**Interpretación**

Estos outputs son coherentes con las restricciones disaster del escenario: la entrega refleja disponibilidad de puentes y viabilidad del TTL; el overhead refleja presión de replicación en contactos locales; valores faltantes de latencia/overhead indican ausencia de entregas exitosas en la ejecución analizada.
