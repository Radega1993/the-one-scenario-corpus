# the-one-scenario-corpus

*(Versión en castellano. English: [README.md](README.md).)*

**Corpus de escenarios y pipeline de análisis** para el simulador [The ONE](https://akeranen.github.io/the-one/) (Opportunistic Network Environment). Este proyecto proporciona un conjunto de configuraciones de simulación (`.settings`), herramientas para extraer características, analizar correlaciones y validar que los escenarios no son redundantes, y un dashboard para visualizar resultados. Está pensado para **evaluar protocolos de enrutamiento en redes oportunistas** (DTN/OppNets) en el marco de tesis o artículos: un benchmark reproducible con escenarios variados y documentados.

| Contenido | Descripción |
|-----------|-------------|
| **corpus_v1/** | 70 escenarios `.settings` por familia (urban, campus, vehicles, rural, disaster, social, traffic). |
| **analysis/** | Extracción de features, correlación, métricas de salida, figuras y [dashboard interactivo](analysis/README.es.md). |
| **.wiki-clone/** | Contenido de la wiki (EN+ES): organizado en `01-home`, `02-guide`, `03-reference`, `04-results`, `05-corpus`, `06-families`. [Índice](.wiki-clone/README.md); Home y resultados en `01-home/`, `04-results/`. Para publicar en GitHub Wiki, copiar todos los `.md` de las subcarpetas a la raíz del wiki. |
| **ROADMAP.md** / **ROADMAP.es.md** | Próximos pasos: documentación bilingüe; criterios de diversidad (|r| < 0,7, cos_dist). Versión en castellano: [ROADMAP.es.md](ROADMAP.es.md). |

### Por qué nombres como `corpus_v1`

El directorio del corpus se llama **`corpus_v1`** (y no solo `corpus`) para poder **versionar el conjunto de escenarios** sin romper scripts ni rutas: si más adelante se define un segundo corpus con otros criterios (p. ej. `corpus_v2` con menos escenarios o otra taxonomía), se mantiene `corpus_v1` intacto y los comandos pueden elegir `--corpus corpus_v1` o `--corpus corpus_v2`. La misma idea aplica a nombres de escenarios (U1, D2, T10…) y a ficheros de datos (p. ej. `output_metrics.csv.example`): un sufijo o prefijo de versión ayuda a convivir con futuras iteraciones del proyecto.

**Flujo típico:** ejecutar simulaciones → generar reportes en `reports/` → análisis (`run_analysis.py`) → visualizar en el dashboard.

**Requisitos:** Java y el ONE compilado (raíz del repo), Python 3 con `numpy`, `pandas`, `scipy`, `matplotlib`, `streamlit` (p. ej. venv del proyecto).

**Comandos rápidos** (desde la raíz del repo):

```bash
# Ejecutar todas las simulaciones del corpus (modo batch, sin GUI)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1

# Análisis completo (features → correlación → figuras → output_metrics)
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase all
python3 scenarios/analysis/run_analysis.py --phase outputs

# Dashboard interactivo
streamlit run scenarios/analysis/dashboard.py
```

Detalle de fases y opciones en [analysis/README.es.md](analysis/README.es.md); referencia de opciones .settings más abajo en este documento.

---

## Guía de configuración (.settings)

Esta guía documenta **todas** las opciones de configuración disponibles en los archivos `.settings` del simulador The ONE. El objetivo es disponer de una referencia completa para crear y mantener un **corpus de escenarios sin correlación lineal** y validar protocolos de enrutamiento (primera parte de tesis/paper).

---

## 1. Cómo se cargan los settings

- El simulador carga primero `default_settings.txt` (en la raíz del proyecto) y luego el archivo que pasas por línea de comandos (p. ej. `scenarios/corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiMedium.settings`).
- Las claves del archivo de escenario **sobrescriben** las del default.
- **Namespaces**: muchas opciones se buscan con prefijo (p. ej. `Scenario.endTime`, `Group1.speed`). Los valores por grupo heredan de `Group.*` si no se definen en `Group1.*`, `Group2.*`, etc.
- **Sintaxis**: pares `clave = valor`. Comentarios con `#`. En rutas de archivo usar siempre **`/`** (no `\`).
- **Valores numéricos con sufijos** (bytes, bits/s, etc.):
  - `k` = 1000, `M` = 10⁶, `G` = 10⁹
  - `kiB` = 1024, `MiB` = 2²⁰, `GiB` = 2³⁰
  - Ejemplos: `50k`, `2M`, `5M`, `50M`, `250k`, `1M`, `500k`.
- **Valores CSV**: listas separadas por comas, p. ej. `25, 35`, `0.5, 1.5`, `0, 120`.
- **Run arrays** (varios runs con distintos valores):  
  `nombre = [valorRun1 ; valorRun2 ; valorRun3]`  
  Con `./one.sh -b 3 archivo.settings` se usan run 1, 2 y 3; el valor efectivo es el del índice de run (modulo la longitud del array).

---

## 2. Escenario (Scenario.*)

| Clave | Tipo | Descripción | Ejemplo / Valores típicos |
|-------|------|-------------|----------------------------|
| `Scenario.name` | string | Nombre del escenario (logs e informes). | `U1_CBD_Commuting_HelsinkiMedium` |
| `Scenario.endTime` | double (s) | Tiempo de simulación en segundos. | `43200` (12 h) |
| `Scenario.updateInterval` | double (s) | Paso de actualización del mundo. | `0.1` |
| `Scenario.simulateConnections` | boolean | Si se simulan enlaces entre nodos. | `true` |
| `Scenario.nrofHostGroups` | int | Número de grupos de hosts (Group1 … GroupN). | `1`, `2`, `6` |

**Importante**: no existe `Simulation.endTime` ni `Simulation.seed`; se usan `Scenario.endTime` y `MovementModel.rngSeed`.

---

## 3. Mundo y movimiento base (MovementModel.*)

Aplican a todos los modelos de movimiento que no tengan tamaño implícito.

| Clave | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `MovementModel.worldSize` | CSV int (2) | Tamaño del mundo en metros (ancho, alto). | `8495, 7504` |
| `MovementModel.rngSeed` | int | Semilla del RNG de los modelos de movimiento. | `1` |
| `MovementModel.warmup` | double (s) | Tiempo de “calentamiento” moviendo nodos antes de empezar la simulación. | `1000` |

---

## 4. Mapas (MapBasedMovement.*)

Obligatorios para cualquier modelo basado en mapa (ShortestPathMapBasedMovement, MapRouteMovement, WorkingDayMovement, BusMovement, etc.).

| Clave | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `MapBasedMovement.nrofMapFiles` | int | Número de archivos de mapa. | `1`, `4` |
| `MapBasedMovement.mapFile1` … `mapFileN` | string | Rutas a archivos WKT de nodos/aristas. | `data/HelsinkiMedium/roads.wkt` |

Rutas relativas al directorio de ejecución (normalmente la raíz del proyecto). Más mapas permiten distinguir tipos de vías (ej. aceras vs carreteras) y usarlos con `Group.okMaps`.

---

## 5. Grupos (Group.* y GroupN.*)

Cada grupo define un tipo de nodos: prefijo de nombre (`groupID`), número de hosts, modelo de movimiento, router, interfaces y parámetros del modelo.

### 5.1 Parámetros comunes a todos los grupos

| Clave | Namespace | Tipo | Descripción | Ejemplo |
|-------|------------|------|-------------|---------|
| `groupID` | GroupN | string | Prefijo del nombre de los hosts (p, c, b, t…). | `p`, `b` |
| `nrofHosts` | GroupN | int | Número de hosts del grupo. | `40`, `80` |
| `movementModel` | Group | string | Clase del modelo de movimiento (paquete `movement.`). | Ver tabla de modelos más abajo |
| `router` | Group | string | Clase del router (paquete `routing.`). | Ver tabla de routers |
| `bufferSize` | Group | int/string | Tamaño del buffer de mensajes (bytes). Sufijos k, M, G. | `5M`, `50M` |
| `nrofInterfaces` | Group | int | Número de interfaces de red del grupo. | `1`, `2` |
| `interface1` … `interfaceN` | GroupN | string | Nombre (id) del tipo de interfaz. | `bt0`, `btInterface` |
| `speed` | Group | CSV double (2) | Velocidad min,max (m/s). | `0.5, 1.5` |
| `waitTime` | Group | CSV int (2) | Tiempo de espera min,max (s) al llegar a un waypoint. | `0, 120` |
| `msgTtl` | Group | int | TTL de mensajes en minutos (por grupo). Por defecto infinito. | `300` |
| `activeTimes` | Group | CSV | Intervalos de actividad (start1, end1, start2, end2…). | Opcional |
| `okMaps` | GroupN | CSV int | Índices de mapas por los que puede circular el grupo (1..nrofMapFiles). | `1`, `1,2,3` |

Las interfaces se definen **fuera** del namespace del grupo, por nombre (ej. `bt0`, `btInterface`):

| Clave | Namespace | Tipo | Descripción | Ejemplo |
|-------|------------|------|-------------|---------|
| `<id>.type` | (nombre interfaz) | string | Clase de la interfaz (paquete `interfaces.`). | `SimpleBroadcastInterface` |
| `transmitSpeed` | id interfaz | int/string | Velocidad de transmisión (bytes/s). Sufijos k, M. | `250k`, `2M` |
| `transmitRange` | id interfaz | double | Alcance en metros. | `10`, `1000` |
| `scanInterval` | id interfaz | double | Intervalo de escaneo (s). | Opcional |

Ejemplo mínimo de interfaz:

```ini
Group.nrofInterfaces = 1
Group.interface1 = bt0
bt0.type = SimpleBroadcastInterface
bt0.transmitSpeed = 2M
bt0.transmitRange = 10
```

---

## 6. Modelos de movimiento

Clase (valor de `Group.movementModel`) y parámetros específicos que puedes usar en `Group.*` / `GroupN.*`.

| Modelo | Descripción | Parámetros específicos (todos en Group/GroupN) |
|--------|-------------|---------------------------------------------------|
| **RandomWaypoint** | Punto aleatorio en el mundo, pausa, siguiente punto. | (usa solo speed, waitTime, worldSize) |
| **RandomWalk** | Dirección aleatoria, luego recto. | (speed, waitTime, worldSize) |
| **ShortestPathMapBasedMovement** | Rutas por mapa (Dijkstra). | `okMaps`, `pois` (índices y probabilidades POI), `poiFile` (PointsOfInterest) |
| **MapRouteMovement** | Sigue una ruta predefinida (WKT). | `routeFile`, `routeType`, `routeFirstStop` |
| **BusMovement** | Autobús que recorre una ruta y para en paradas. | `routeFile`, `routeType`, `busControlSystemNr` |
| **WorkingDayMovement** | Día laboral: casa → trabajo (bus/coche) → posible actividad nocturna → casa. | Ver sección 7 |
| **ExternalMovement** | Posiciones desde archivo externo. | `file`, `nrofPreload` |
| **ExternalPathMovement** | Rutas desde archivo. | `traceFile`, `activeFile` |
| **StationaryMovement** | Nodo fijo. | `nodeLocation` (coord) |
| **LinearMovement** | Movimiento lineal entre dos puntos. | `startLocation`, `endLocation`, `initLocType`, `targetType` |
| **ClusterMovement** | Dentro de clusters. | (depende de implementación) |

- **routeType** (MapRouteMovement / BusMovement): `1` = circular, `2` = ping-pong (ida y vuelta).
- **routeFirstStop**: índice de la primera parada (0-based); si no se pone o es negativo, se elige aleatoria.

---

## 7. WorkingDayMovement (día laboral) — detalle

Combina: **HomeActivityMovement**, **OfficeActivityMovement**, **BusTravellerMovement** o **CarMovement**, **EveningActivityMovement**. Requiere mapa y, si hay uso de bus, **al menos un grupo con BusMovement** en el mismo `busControlSystemNr` para que existan paradas (si no, NPE en `BusTravellerMovement`).

### 7.1 Parámetros globales WorkingDayMovement

| Clave | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `routeFile` | string | Ruta WKT del bus (para BusTravellerMovement). | `data/HelsinkiMedium/A_bus.wkt` |
| `busControlSystemNr` | int | ID del sistema de buses (-1 = sin buses “reales”, pero hace falta 1 bus en algún grupo para paradas). | `-1` |
| `ownCarProb` | double | Probabilidad de usar coche en lugar de bus. | `0.0`, `0.2` |
| `probGoShoppingAfterWork` | double | Probabilidad de hacer actividad nocturna (ir de compras / quedar). | `0.3` |

### 7.2 HomeActivityMovement

| Clave | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `homeLocationsFile` | string | Archivo WKT con puntos de hogares. | `data/HelsinkiMedium/A_homes.wkt` |
| `timeDiffSTD` | int (s) | Desviación típica del desfase horario (despertar) en segundos. | `1800` |

### 7.3 OfficeActivityMovement

| Clave | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `officeLocationsFile` | string | WKT con ubicaciones de oficinas. | `data/HelsinkiMedium/A_offices.wkt` |
| `workDayLength` | int (s) | Duración de la jornada. | `28800` (8 h) |
| `nrOfOffices` | int | Número de oficinas (si no hay archivo). | `10` |
| `officeSize` | int | Tamaño/radio de oficina. | `40` |
| `officeWaitTimeParetoCoeff` | double | Coef. Pareto para tiempo en oficina. | `1.4` |
| `officeMinWaitTime` | double (s) | Mínimo tiempo en oficina. | `300` |
| `officeMaxWaitTime` | double (s) | Máximo tiempo en oficina. | `900` |

### 7.4 EveningActivityMovement (actividad nocturna / “shopping”)

| Clave | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `meetingSpotsFile` | string | WKT con puntos de encuentro / centros comerciales. | `data/HelsinkiMedium/A_meetingspots.wkt` |
| `shoppingControlSystemNr` | int | ID del sistema de actividad nocturna (-1 = desactivado). | `-1` |
| `nrOfMeetingSpots` | int | Número de spots si no hay archivo. | `10` |
| `minGroupSize` | int | Tamaño mínimo de grupo. | `1` |
| `maxGroupSize` | int | Tamaño máximo de grupo. | `5` |
| `minAfterShoppingStopTime` | int (s) | Mínimo tiempo de espera en el sitio. | `60` |
| `maxAfterShoppingStopTime` | int (s) | Máximo tiempo de espera. | `600` |

En el código, el sistema de “evening activity” se configura con **`shoppingControlSystemNr`** (no `eveningActivityControlSystemNr`). Si en algún ejemplo aparece `eveningActivityControlSystemNr`, puede ser un alias o documentación; el que lee el simulador es `shoppingControlSystemNr`.

### 7.5 BusTravellerMovement (uso interno; mismo grupo que WorkingDayMovement)

- `busControlSystemNr`: mismo que el sistema donde hay al menos un **BusMovement**.
- `probs` (opcional): probabilidades para cadenas de Markov (número de paradas).
- `probTakeOtherBus` (opcional): probabilidad de coger otro bus.

### 7.6 Orden de grupos si hay bus

Para evitar NPE por `getBusStops() == null`, el grupo que tenga **BusMovement** debe crearse **antes** que los peatones con WorkingDayMovement. En The ONE los grupos se crean en orden Group1, Group2, … Por tanto: **Group1 = 1 host BusMovement**, **Group2 = N hosts WorkingDayMovement** (mismo `busControlSystemNr` y mismo `routeFile`).

---

## 8. Eventos (tráfico de mensajes)

### 8.1 Contador y clase

| Clave | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `Events.nrof` | int | Número de generadores de eventos. | `1` |
| `Events1.class` | string | Clase del primer generador (paquete `input.`). | `MessageEventGenerator` |

### 8.2 MessageEventGenerator

| Clave | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `Events1.interval` | CSV int (2) | Intervalo entre mensajes (min, max) en segundos. | `25, 35` |
| `Events1.size` | CSV int (2) | Tamaño del mensaje (min, max) en bytes. Sufijos k, M. | `50k, 150k` |
| `Events1.hosts` | CSV int (2) | Rango de direcciones de hosts (min, max); [min, max). Debe haber al menos 2 nodos. | `0, 81` (81 hosts) |
| `Events1.tohosts` | CSV int (2) | (Opcional) Rango de destinos; si se define, fuentes vienen de `hosts`. | Opcional |
| `Events1.prefix` | string | Prefijo único del ID de mensaje (obligatorio). | `M` |
| `Events1.time` | CSV double (2) | (Opcional) Ventana temporal de creación (inicio, fin) en segundos. | Opcional |

**Importante**: no existen `Events1.toHosts`, `Events1.fromHosts` ni valor `random`; se usan rangos numéricos `hosts` y opcionalmente `tohosts`. El total de hosts es la suma de `Group1.nrofHosts + Group2.nrofHosts + ...`; los índices van de 0 a (totalHosts - 1), por tanto `hosts = 0, totalHosts`.

---

## 9. Reports

| Clave | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `Report.nrofReports` | int | Número de informes. | `2` |
| `Report.reportDir` | string | Directorio de salida (p. ej. relativos a la raíz). | `reports/` |
| `Report.warmup` | double (s) | Período de warmup para informes. | `0` |
| `Report.report1` … `reportN` | string | Clases de informe (paquete `report.`). | Ver tabla |

Algunas clases de informe útiles:

- `MessageStatsReport`, `MessageDeliveryReport`, `MessageDelayReport`, `CreatedMessagesReport`, `DeliveredMessagesReport`
- `ContactTimesReport`, `InterContactTimesReport`, `TotalContactTimeReport`
- `BufferOccupancyReport`, `MessageCopyCountReport`, `DistanceDelayReport`
- `NodeDensityReport`, `LocationSnapshotReport`, `MovementNs2Report`

Cada report puede tener sus propias opciones (p. ej. `MessageStatsReport.output`, `ContactTimesReport.granularity`). Ver clases en `src/report/` si necesitas parámetros concretos.

---

## 10. Routers

Valor de `Group.router` (clase en paquete `routing.`). Algunos parámetros adicionales por router (namespace = nombre de la clase):

| Router | Descripción | Parámetros opcionales (ej. ProphetRouter.xxx) |
|--------|-------------|------------------------------------------------|
| **EpidemicRouter** | Réplica total (flooding). | — |
| **SprayAndWaitRouter** | Spray-and-wait. | `nrofCopies`, `binaryMode` |
| **ProphetRouter** | PROPHET. | `secondsInTimeUnit`, `beta`, `gamma` |
| **MaxPropRouter** | MaxProp. | `probSetMaxSize`, `alpha` |
| **FirstContactRouter** | Primer contacto. | — |
| **DirectDeliveryRouter** | Solo entre origen y destino. | — |
| **PassiveRouter** | No reenvía. | — |
| **WaveRouter** | Wave. | `immunityTime`, `custodyFraction` |
| **LifeRouter** | LIFE. | `nmcount` |

Ejemplo:

```ini
Group.router = EpidemicRouter
# O con parámetros:
# SprayAndWaitRouter.nrofCopies = 6
# SprayAndWaitRouter.binaryMode = true
# ProphetRouter.secondsInTimeUnit = 30
```

---

## 11. Optimización

| Clave | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `Optimization.cellSizeMult` | int | Multiplicador de tamaño de celda (mundo). | `5` |
| `Optimization.randomizeUpdateOrder` | boolean | Aleatorizar orden de actualización de nodos. | `true` |

---

## 12. Variación de escenarios (corpus sin correlación lineal)

Para generar un corpus variado (p. ej. 50–70 escenarios) y reducir correlación entre ellos, conviene variar de forma **sistemática** (pero no lineal) los siguientes ejes:

1. **Duración y semilla**
   - `Scenario.endTime`: 6h, 12h, 24h (21600, 43200, 86400).
   - `MovementModel.rngSeed`: distintos seeds (1, 2, …, 60 o muestreo aleatorio).

2. **Número y tipo de nodos**
   - `GroupN.nrofHosts`: 40, 60, 80, 100.
   - Proporción entre grupos (peatones vs buses/tranvías).

3. **Movimiento**
   - `MovementModel.worldSize` si usas mundo cuadrado/rectangular.
   - `speed`, `waitTime`: distintos rangos (más estáticos vs más móviles).
   - Para WorkingDayMovement: `timeDiffSTD`, `workDayLength`, `probGoShoppingAfterWork`, `ownCarProb`, archivos WKT distintos (A_, B_, C_… en HelsinkiMedium).

4. **Comunicación**
   - `transmitRange`: 5, 10, 20 m.
   - `transmitSpeed`: 250k, 2M, 10M.
   - `bufferSize`: 5M, 50M.

5. **Tráfico**
   - `Events1.interval`: (20,40), (25,35), (30,60).
   - `Events1.size`: (50k,150k), (500k,1M).
   - `Group.msgTtl`: 60, 300, 7200.

6. **Protocolo**
   - Cambiar `Group.router` entre escenarios (EpidemicRouter, ProphetRouter, SprayAndWaitRouter, etc.) para validar protocolos.

7. **Run arrays**
   - Usar `[v1 ; v2 ; v3]` en una misma clave y ejecutar con `-b 3` para obtener 3 escenarios por archivo (útil para barrido de un solo parámetro).

Combinando valores de forma **ortogonal** (p. ej. 4 duraciones × 5 seeds × 3 tamaños de red) se obtienen muchos escenarios; luego se puede filtrar o muestrear para quedarse con un conjunto (p. ej. 70) y comprobar correlación (p. ej. análisis de correlación entre métricas o entre parámetros).

---

## 13. Ejemplo mínimo de escenario

```ini
Scenario.name = mi_escenario
Scenario.endTime = 43200
Scenario.nrofHostGroups = 1
Scenario.simulateConnections = true
Scenario.updateInterval = 0.1

MovementModel.rngSeed = 1
MovementModel.worldSize = 4500, 3400

Group.movementModel = RandomWaypoint
Group.router = EpidemicRouter
Group.nrofHosts = 40
Group.bufferSize = 5M
Group.nrofInterfaces = 1
Group.interface1 = bt0
Group.speed = 0.5, 1.5
Group.waitTime = 0, 120

bt0.type = SimpleBroadcastInterface
bt0.transmitSpeed = 250k
bt0.transmitRange = 10

Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 25, 35
Events1.size = 500k, 1M
Events1.hosts = 0, 40
Events1.prefix = M

Report.nrofReports = 2
Report.reportDir = reports/
Report.report1 = MessageStatsReport
Report.report2 = ContactTimesReport
```

---

## 14. Referencia rápida de namespaces

| Prefijo | Uso |
|---------|-----|
| `Scenario.*` | Nombre, tiempo, grupos, conexiones. |
| `MovementModel.*` | worldSize, rngSeed, warmup. |
| `MapBasedMovement.*` | nrofMapFiles, mapFile1… |
| `Group.*` | Valores por defecto para todos los grupos. |
| `Group1.*`, `Group2.*`, … | Valores específicos del grupo. |
| `bt0.*`, `btInterface.*`, … | Parámetros de cada tipo de interfaz (por nombre). |
| `Events.*`, `Events1.*` | Número de generadores y parámetros de MessageEventGenerator. |
| `Report.*` | Número de informes, directorio, nombres de clases. |
| `ProphetRouter.*`, `SprayAndWaitRouter.*`, … | Parámetros del router si los usa. |

Con esta guía puedes definir de forma precisa cada aspecto del escenario y planificar el corpus de escenarios para la validación de protocolos de enrutamiento.

---

## 15. Análisis del corpus y dashboard

El análisis del corpus (extracción de features, correlación entre escenarios, validación sobre outputs) se hace con el **pipeline en `scenarios/analysis/`**:

- **Script principal:** `scenarios/analysis/run_analysis.py`, ejecutable por fases: `features` → `normalize` → `correlation` → `figures` → `output_metrics` → `outputs`. Ver `scenarios/analysis/README.es.md` para la lista completa de fases y opciones.
- **Salidas:** `analysis/data/` (CSV de features, normalizados, matrices de correlación y distancias, `output_metrics.csv`), `analysis/figures/` (heatmaps, histogramas, scatter), `analysis/reports/` (informes de texto).
- **Criterio de benchmark:** 46 features por escenario; |r| < 0,7 en ≥95% de pares (**95,9 %** cumplido); distancia coseno mín > 0,05 (**0,0527**, 0 pares por debajo); max |r| **0,938**; **98** pares (4,1 %) con |r| ≥ 0,7. Ver [analysis/reports/diversity_targets.md](analysis/reports/diversity_targets.md) para objetivos completos y estado.

**Dashboard interactivo:** para visualizar todo en un solo sitio (resumen, resultados por fase, detalle por escenario, comparación entre escenarios):

```bash
# Desde la raíz del repo
streamlit run scenarios/analysis/dashboard.py

# O desde scenarios/analysis
cd scenarios/analysis && streamlit run dashboard.py
```

Requiere `streamlit`, `pandas` (y las dependencias del análisis en el venv del proyecto).

---

## Autor / contacto

**the-one-scenario-corpus** — corpus y análisis de escenarios para The ONE.

- **Autor:** Raül de Arriba
