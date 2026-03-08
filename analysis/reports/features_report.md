# Informe de features

Features utilizados para correlación y diversidad, y settings no utilizados con motivo.

## Features utilizados (46)

| Feature | Descripción | Origen (setting) |
|---------|-------------|------------------|
| Wx | Ancho del mundo (m) | MovementModel.worldSize |
| Wy | Alto del mundo (m) | MovementModel.worldSize |
| N | Número de hosts | Scenario.nrofHostGroups, Group*.nrofHosts |
| density | Densidad proxy (hosts/km²) | N, Wx, Wy (derivado) |
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
| mm_Linear | — | — |
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
| event2_interval_mean | Intervalo medio 2.º flujo (s); NaN si Events.nrof<2 o Events2.filePath | Events2.interval |
| event2_size_mean | Tamaño medio 2.º flujo (bytes); NaN si Events.nrof<2 o Events2.filePath | Events2.size |
| Scenario.endTime | Duración de la simulación (s) | Scenario.endTime |
| nrofHostGroups | Número de grupos de hosts | Scenario.nrofHostGroups |
| has_active_times | Grupos con activeTimes definido (0/1) | Group*.activeTimes |

## Settings no utilizados

| Setting | Motivo |
|---------|--------|
| `Events1.class` | DESCARTADO: Tipo de generador; mismo en todo el corpus. |
| `Events1.hosts` | DESCARTADO: Redundante con N. |
| `Events1.prefix` | DESCARTADO: Identificador de mensajes. |
| `Events2.class` | DESCARTADO: Tipo/identificador; no comparable. |
| `Events2.filePath` | DESCARTADO: Tráfico desde fichero; no extraemos número comparable. |
| `Events2.hosts` | DESCARTADO: Redundante con N. |
| `Events2.nrofPreload` | DESCARTADO: No priorizado para diversidad. |
| `Events2.prefix` | DESCARTADO: Identificador. |
| `Group.LinearMovement.endLocation` | DESCARTADO: Coordenadas; dependen del mapa. |
| `Group.LinearMovement.initLocType` | DESCARTADO: Solo 1 escenario; sin variabilidad. |
| `Group.LinearMovement.startLocation` | DESCARTADO: Coordenadas; dependen del mapa. |
| `Group.LinearMovement.targetType` | DESCARTADO: Solo 1 escenario; sin variabilidad. |
| `Group.busControlSystemNr` | DESCARTADO: Referencia interna al sistema de buses. |
| `Group.eveningActivityControlSystemNr` | DESCARTADO: Referencia interna. |
| `Group.homeLocationsFile` | DESCARTADO: Ruta de fichero; no comparable entre mapas. |
| `Group.meetingSpotsFile` | DESCARTADO: Ruta de fichero; no comparable. |
| `Group.nrofInterfaces` | DESCARTADO: Casi siempre 1; sin variabilidad útil. |
| `Group.officeLocationsFile` | DESCARTADO: Ruta de fichero; no comparable. |
| `Group.officeWaitTimeParetoCoeff` | DESCARTADO: Detalle de distribución; ya usamos officeWaitTime_mean. |
| `Group.okMaps` | DESCARTADO: No usado de forma relevante en el corpus. |
| `Group.routeFile` | DESCARTADO: Ruta de fichero. |
| `Group.routeType` | DESCARTADO: Sin variabilidad útil en el corpus. |
| `Group.router` | DESCARTADO: Mismo en todo el corpus (EpidemicRouter). |
| `Group.shoppingControlSystemNr` | DESCARTADO: Referencia interna. |
| `Group.shoppingWaitTimeParetoCoeff` | DESCARTADO: Ya usamos shoppingWaitTime_mean. |
| `Group1.LinearMovement.endLocation` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group1.LinearMovement.initLocType` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group1.LinearMovement.startLocation` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group1.LinearMovement.targetType` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group1.busControlSystemNr` | DESCARTADO: Referencia interna. |
| `Group1.clusterCenter` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group1.groupID` | DESCARTADO: Identificador de grupo. |
| `Group1.nrofInterfaces` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group1.routeFile` | DESCARTADO: Ruta de fichero (depende del mapa). |
| `Group1.routeType` | DESCARTADO: Mismo valor (1) en escenarios con bus; sin variabilidad. |
| `Group1.router` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group10.clusterCenter` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group10.groupID` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group11.clusterCenter` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group11.groupID` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group12.clusterCenter` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group12.groupID` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.busControlSystemNr` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.clusterCenter` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.eveningActivityControlSystemNr` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.groupID` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.homeLocationsFile` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.meetingSpotsFile` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.nrofInterfaces` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.officeLocationsFile` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.officeWaitTimeParetoCoeff` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.okMaps` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.routeFile` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.routeType` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.router` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.shoppingControlSystemNr` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group2.shoppingWaitTimeParetoCoeff` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group3.clusterCenter` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group3.groupID` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group3.nrofInterfaces` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group3.router` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group4.clusterCenter` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group4.groupID` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group5.clusterCenter` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group5.groupID` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group6.clusterCenter` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group6.groupID` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group7.clusterCenter` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group7.groupID` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group8.clusterCenter` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group8.groupID` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group9.clusterCenter` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `Group9.groupID` | DESCARTADO: Ver features_decision.md (variante de grupo o misma categoría que Group/Group1). |
| `MapBasedMovement.mapFile1` | DESCARTADO: Ruta de fichero; no comparable. |
| `MapBasedMovement.nrofMapFiles` | DESCARTADO: Ruta/cantidad de ficheros; no comparable numéricamente entre mapas. |
| `MovementModel.rngSeed` | DESCARTADO: Aleatoriedad; no caracteriza el escenario de forma estable. |
| `Report.nrofReports` | DESCARTADO: Configuración de salida, no de escenario. |
| `Report.report1` | DESCARTADO: Salida. |
| `Report.report2` | DESCARTADO: Salida. |
| `Report.reportDir` | DESCARTADO: Salida. |
| `Scenario.name` | DESCARTADO: Identificador; no feature numérica. |
| `Scenario.simulateConnections` | DESCARTADO: Parámetro de simulación fijo en todo el corpus. |
| `Scenario.updateInterval` | DESCARTADO: Parámetro de simulación fijo. |
| `bt0.type` | DESCARTADO: Tipo de interfaz; mismo en todo el corpus. |