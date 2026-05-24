# Referencia de features

**Español** | [English](Features-reference)

---

Esta página documenta los **46 features** utilizados para el análisis de correlación y diversidad, y los **settings que no se utilizan** en el vector de features, con el motivo en cada caso.

Se distingue un **conjunto core de 23 features** (para validación de diversidad y paper) y el **conjunto extendido de 46** (para exploración y dashboard). Metodología: `analysis/reports/features_core_vs_extended.md`. El vector se extrae con `run_analysis.py` (fase `features`). El informe se genera con `--phase features_report` y se escribe en `analysis/reports/features_report.txt` y `features_report.md`.

---

## Features utilizados (46)

Forman el vector por escenario usado para correlación Pearson/Spearman, distancia coseno, clustering y figuras. El espacio se codifica como **world_area** y **aspect_ratio** (no Wx, Wy por separado).

| Feature | Descripción | Origen (setting) |
|---------|-------------|------------------|
| world_area | Área del mundo Wx×Wy (m²) | MovementModel.worldSize |
| aspect_ratio | Relación de aspecto min(Wx,Wy)/max(Wx,Wy) ∈ (0,1] | MovementModel.worldSize |
| N | Número de hosts | Scenario.nrofHostGroups, Group*.nrofHosts |
| density | Densidad proxy (hosts/km²); excluida del core (redundante con N, world_area) | N, world_area (derivado) |
| speed_mean | Velocidad media (m/s) | Group*.speed |
| pause_ratio | Ratio pausa/(movimiento+pausa) | Group*.waitTime (derivado) |
| wait_mean | Tiempo de espera medio (s) | Group*.waitTime |
| mm_WDM | Usa WorkingDayMovement (0/1) | Group*.movementModel |
| mm_RWP | Usa RandomWaypoint (0/1) | Group*.movementModel |
| mm_MapRoute | Usa MapRouteMovement (0/1) | Group*.movementModel |
| mm_Cluster | Usa ClusterMovement (0/1) | Group*.movementModel |
| mm_Bus | Usa BusMovement (0/1) | Group*.movementModel |
| mm_ShortestPath | Usa ShortestPathMapBasedMovement (0/1) | Group*.movementModel |
| mm_External | Usa External/ExternalPathMovement (0/1) | Group*.movementModel |
| mm_Linear | Usa LinearMovement (0/1) | Group*.movementModel |
| transmitRange | Rango de transmisión (m) | bt0.transmitRange / interface.transmitRange |
| contact_rate_proxy | Proxy tasa de contacto | density, transmitRange, speed (derivado) |
| event_interval_mean | Intervalo medio entre mensajes (s) | Events1.interval |
| event_size_mean | Tamaño medio de mensaje (bytes) | Events1.size |
| msgTtl | TTL de mensajes (s) | Group*.msgTtl |
| pattern_uniform | Patrón tráfico uniforme (0/1) | Events* (sin time/tohosts) |
| pattern_burst | Patrón tráfico con ventana temporal (0/1) | Events*.time |
| pattern_hub_target | Patrón tráfico dirigido a hubs (0/1) | Events*.tohosts |
| nrof_event_generators | Número de generadores de eventos | Events.nrof |
| bufferSize | Tamaño de buffer (bytes) | Group*.bufferSize |
| transmitSpeed | Velocidad de transmisión (bytes/s) | bt0.transmitSpeed |
| workDayLength | Duración jornada laboral (s); NaN si no WDM | Group*.workDayLength |
| timeDiffSTD | Desv. estándar diferencia horaria (s); NaN si no WDM | Group*.timeDiffSTD |
| probGoShoppingAfterWork | Prob. ir de compras; NaN si no WDM | Group*.probGoShoppingAfterWork |
| nrOfMeetingSpots | Número de puntos de encuentro; NaN si no WDM | Group*.nrOfMeetingSpots |
| nrOfOffices | Número de oficinas; NaN si no WDM | Group*.nrOfOffices |
| officeSize | Tamaño de oficina (personas); NaN si no WDM | Group*.officeSize |
| nrOfShops | Número de tiendas; NaN si no WDM | Group*.nrOfShops |
| ownCarProb | Prob. poseer coche (0–1); relevante vehicular/WDM | Group*.ownCarProb |
| shopSize | Tamaño de tienda (personas); NaN si no WDM | Group*.shopSize |
| officeWaitTime_mean | Tiempo espera en oficina medio (s); NaN si no WDM | Group*.officeMinWaitTime, officeMaxWaitTime |
| shoppingWaitTime_mean | Tiempo espera compras medio (s); NaN si no WDM | Group*.shoppingMinWaitTime, shoppingMaxWaitTime |
| eveningGroupSize_mean | Tamaño grupo actividad evening medio; NaN si no WDM | Group*.minGroupSize, maxGroupSize |
| eveningWaitTime_mean | Tiempo espera actividad evening medio (s); NaN si no WDM | Group*.minWaitTime, maxWaitTime |
| afterShoppingStopTime_mean | Tiempo parada tras compras medio (s); NaN si no WDM | Group*.minAfterShoppingStopTime, maxAfterShoppingStopTime |
| clusterRange_mean | Radio medio de clusters (m); NaN si no ClusterMovement | Group*.clusterRange |
| event2_interval_mean | Intervalo medio 2.º flujo de eventos (s); NaN si Events.nrof&lt;2 o filePath | Events2.interval |
| event2_size_mean | Tamaño medio 2.º flujo (bytes); NaN si Events.nrof&lt;2 o filePath | Events2.size |
| Scenario.endTime | Duración de la simulación (s) | Scenario.endTime |
| nrofHostGroups | Número de grupos de hosts | Scenario.nrofHostGroups |
| has_active_times | Grupos con activeTimes definido (0/1) | Group*.activeTimes |

---

## Settings no utilizados

Estas claves aparecen en uno o más `.settings` del corpus pero **no** se usan para construir el vector de features. Se indica el motivo.

**Categorías de motivo:**

- **Ruta de fichero / no comparable:** paths a mapas o datos; no son comparables numéricamente entre escenarios.
- **Referencia interna:** identificadores del simulador (p. ej. busControlSystemNr, shoppingControlSystemNr).
- **Mismo en todo el corpus:** poca o ninguna variabilidad (p. ej. router=EpidemicRouter, bt0.type).
- **Redundante:** ya capturado por otro feature (p. ej. Events1.hosts ≈ N).
- **No incluido en el diseño actual:** posible extensión futura; o detalle fino que sustituimos por un agregado (p. ej. officeWaitTime_mean en lugar de Pareto/min/max).

| Setting | Motivo |
|---------|--------|
| `Events1.class` | Tipo de generador; mismo en todo el corpus |
| `Events1.hosts` | Rango de hosts; redundante con N |
| `Events1.prefix` | Identificador de mensajes |
| `Events2.*` (class, filePath, hosts, nrofPreload, prefix) | No incluido en el diseño actual; posible extensión futura |
| `Group.LinearMovement.*` | No incluido en el diseño actual; posible extensión futura |
| `Group.busControlSystemNr` | Referencia interna al sistema de buses |
| `Group.eveningActivityControlSystemNr` | Referencia interna |
| `Group.homeLocationsFile` | Ruta de fichero; no comparable entre mapas |
| `Group.maxAfterShoppingStopTime` | No incluido |
| `Group.meetingSpotsFile` | Ruta de fichero; no comparable |
| `Group.minAfterShoppingStopTime` | No incluido; detalle fino de actividad post-compras |
| `Group.nrofInterfaces` | Casi siempre 1; poca variabilidad |
| `Group.officeLocationsFile` | Ruta de fichero; no comparable |
| `Group.officeWaitTimeParetoCoeff` | No incluido; detalle fino de WDM (usa officeWaitTime_mean) |
| `Group.okMaps` | No incluido en el diseño actual; posible extensión futura |
| `Group.routeFile` | Ruta de fichero |
| `Group.routeType` | No incluido en el diseño actual; posible extensión futura |
| `Group.router` | Mismo en todo el corpus (EpidemicRouter) |
| `Group.shoppingControlSystemNr` | Referencia interna |
| `Group.shoppingWaitTimeParetoCoeff` | No incluido (usa shoppingWaitTime_mean) |
| `Group1.*` (routeFile, routeType, groupID, busControlSystemNr, clusterCenter, clusterRange, LinearMovement.*, nrofInterfaces, router) | Ruta de fichero, referencia interna o identificador; o no en diseño |
| `Group2` … `Group12` (clusterCenter, clusterRange, groupID, routeFile, etc.) | Idem para el resto de grupos |
| `MapBasedMovement.mapFile1`, `MapBasedMovement.nrofMapFiles` | Ruta/cantidad de ficheros; no comparable numéricamente |
| `MovementModel.rngSeed` | Aleatoriedad; no caracteriza el escenario de forma estable |
| `Report.*` | Configuración de salida, no de escenario |
| `Scenario.name` | Identificador del escenario, no feature numérica |
| `Scenario.simulateConnections`, `Scenario.updateInterval` | Parámetro de simulación fijo |
| `bt0.type` | Tipo de interfaz; mismo en todo el corpus |

---

## Véase también

- [Metodología](Methodology-es) — Cómo se definen features y correlación  
- [Referencia del pipeline de análisis](Analysis-pipeline-reference-es) — Fases y salidas  
- [Resumen de resultados](Results-overview-es) — Métricas actuales  
