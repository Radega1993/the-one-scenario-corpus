# Checklist — 60 escenarios para validación de protocolos

Corpus de escenarios sin correlación lineal para la primera parte de la tesis/paper. Cada escenario debe tener un **vector de parámetros documentado**; la diversidad viene de familias distintas: map-based vs open space, clúster vs mezcla, carga vs TTL, etc.

**Formato:** `[ ]` ID — Nombre — Idea (qué lo hace distinto) + palancas a configurar.

---

## A) Urbanos map-based (Helsinki/Manhattan), actividad diaria (12)

| # | ID | Nombre | Idea | Palancas |
|---|----|--------|------|----------|
| 1 | [x] | **U1** | CBD commuting (WDM): oficinas concentradas, picos mañana/tarde | `workDayLength`, `timeDiffSTD`, densidad (nrofHosts, nrOfOffices) |
| 2 | [x] | **U2** | Retail-heavy: probabilidad alta de compras tras trabajo | `probGoShoppingAfterWork`, `maxAfterShoppingStopTime` |
| 3 | [x] | **U3** | Nightlife clusters: muchos meeting spots, grupos grandes | `nrOfMeetingSpots`, `minGroupSize`, `maxGroupSize` |
| 4 | [x] | **U4** | Rainy day slow mobility: velocidades bajas + esperas altas | `speed`, `waitTime` (rangos bajos velocidad, altos espera) |
| 5 | [x] | **U5** | Sparse suburb: mundo grande, pocos puntos de interés, baja densidad | `MovementModel.worldSize`, `nrOfOffices`, nrofHosts bajo |
| 6 | [x] | **U6** | Dense downtown: mundo más pequeño, alta densidad, rangos cortos | world size pequeño, `transmitRange` bajo, nrofHosts alto |
| 7 | [x] | **U7** | Micro-mobility: muchos nodos, buffer pequeño, mensajes pequeños | `nrofHosts`, `bufferSize`, `Events1.size` (pequeños) |
| 8 | [x] | **U8** | Congestion hotspot: map okNodes limitado (solo calles principales) | `MapBasedMovement.okMaps` (Group.okMaps restringido) |
| 9 | [x] | **U9** | Workday short: jornada 4 h | `workDayLength` = 14400 |
| 10 | [x] | **U10** | Workday long: jornada 12 h | `workDayLength` = 43200 |
| 11 | [x] | **U11** | Office wait Pareto heavy-tail: colas “largas” en oficina | `officeWaitTimeParetoCoeff`, `officeMinWaitTime`, `officeMaxWaitTime` |
| 12 | [x] | **U12** | High time variance: desincronizar despertar/horarios | `timeDiffSTD` alto |

---

## B) Campus / evento / estadio (map-based o free-space) (8)

| # | ID | Nombre | Idea | Palancas |
|---|----|--------|------|----------|
| 13 | [x] | **C1** | Campus class change: oleadas cada ~50 min | Eventos/intervalos temporales (Events1.interval o Events1.time) |
| 14 | [x] | **C2** | Exam day: pocas sesiones, permanencias largas | `waitTime` muy largo, pocos waypoints |
| 15 | [x] | **C3** | Hackathon 24 h: permanencias muy largas, movilidad baja | `Scenario.endTime` 24h, `speed` bajo, `waitTime` alto |
| 16 | [x] | **C4** | Stadium ingress/egress: dos picos fuertes y luego vacío | Patrón de eventos (Events1.time) o grupos con activeTimes |
| 17 | [x] | **C5** | Festival multi-escenario: 3–5 hotspots cambiantes | Varios meeting spots / POIs, posible ExternalPath o rutas |
| 18 | [x] | **C6** | Conference networking: grupos que se forman/disuelven | `minGroupSize`, `maxGroupSize`, `minWaitTime`, `maxWaitTime` |
| 19 | [x] | **C7** | Library quiet: baja movilidad, alto delivery si contactos prolongados | `speed` bajo, `waitTime` alto, transmitRange/velocidad normales |
| 20 | [x] | **C8** | Emergency drill / evacuación: movimiento direccional y rápido | Modelo lineal o camino fijo, `speed` alto, direcciones concentradas |

---

## C) Vehículos / taxis / transporte (map-based) (8)

| # | ID | Nombre | Idea | Palancas |
|---|----|--------|------|----------|
| 21 | [x] | **V1** | Taxi low: pocos taxis, alta movilidad | Grupo pequeño MapRouteMovement/tipo taxi, `speed` alto |
| 22 | [x] | **V2** | Taxi high: muchos taxis; contactos cortos y frecuentes | nrofHosts alto en grupo taxi, rutas, `waitTime` bajo |
| 23 | [x] | **V3** | Bus-only carriers: nodos “bus” como mules con rutas fijas | Solo grupo(s) BusMovement, rutas fijas, sin peatones WDM |
| 24 | [x] | **V4** | Mixed bus+ped: 2 grupos — peatones WDM + buses | Group1 bus, Group2 WDM (como U1_CBD_Commuting_HelsinkiMedium.settings), `busControlSystemNr` |
| 25 | [x] | **V5** | Rush hour bus density: más buses en horas punta | Más hosts BusMovement, o varios grupos bus con rutas distintas |
| 26 | [x] | **V6** | Car ownership 0% | `ownCarProb` = 0 (solo bus) |
| 27 | [x] | **V7** | Car ownership 100% | `ownCarProb` = 1 (solo coche) |
| 28 | [x] | **V8** | Road closure: okMaps restringido (simula obras) | `Group.okMaps` con menos mapas (solo vías alternativas) |

---

## D) Rural / wilderness / baja conectividad (8)

| # | ID | Nombre | Idea | Palancas |
|---|----|--------|------|----------|
| 29 | [x] | **R1** | Rural random waypoint: gran world, pocos nodos | `MovementModel.worldSize` grande, nrofHosts bajo, RandomWaypoint |
| 30 | [x] | **R2** | Villages & trails: 3 aldeas separadas, movilidad entre ellas | Varios mapas/POIs o rutas que conectan zonas, 3 “clusters” |
| 31 | [x] | **R3** | Wildlife tracking: nodos se mueven lento, TTL muy alto | `speed` bajo, `msgTtl` alto (o Events poco frecuentes) |
| 32 | [x] | **R4** | Park rangers: 2–3 mules con rutas largas | 2–3 hosts MapRouteMovement, rutas largas (WKT) |
| 33 | [x] | **R5** | Mountain rescue: mensajes críticos pequeños, TTL corto | `Events1.size` pequeño, `msgTtl` bajo (minutos) |
| 34 | [x] | **R6** | Sparse + long range: rangos mayores (LoRa-like) | `transmitRange` alto, nrofHosts bajo, world grande |
| 35 | [x] | **R7** | Sparse + tiny buffer: presión de buffer fuerte | `bufferSize` pequeño, tráfico moderado |
| 36 | [x] | **R8** | Intermittent power: interfaces que “duermen” | `activeTimes` o varios grupos con ventanas de actividad |

---

## E) Disaster / post-catástrofe (8)

| # | ID | Nombre | Idea | Palancas |
|---|----|--------|------|----------|
| 37 | [x] | **D1** | Shelter hotspots: refugios como hubs humanos | POIs/meeting spots concentrados, muchos nodos hacia pocos sitios |
| 38 | [x] | **D2** | Partitioned city: 2 particiones con puente (un mule) | Dos grupos en zonas separadas + 1 host que cruza (MapRoute) |
| 39 | [x] | **D3** | Aftershock mobility: movilidad errática; contactos impredecibles | RandomWaypoint/RandomWalk, speed/waitTime variables |
| 40 | [x] | **D4** | Medical triage: prioridades (si se modela por apps/msg class) | (Requiere extensión de mensajes/apps si el ONE lo soporta) |
| 41 | [x] | **D5** | UAV mule: 1–2 nodos rápidos recorriendo ruta | 1–2 hosts MapRouteMovement, `speed` muy alto |
| 42 | [x] | **D6** | Short TTL critical: TTL 5–10 min, tamaños pequeños | `msgTtl` 5–10 min, `Events1.size` pequeño |
| 43 | [x] | **D7** | High load: generación de mensajes muy alta | `Events1.interval` bajo, `Events1.size` moderado |
| 44 | [x] | **D8** | Infrastructure returns: a mitad de simulación sube rango / baja pérdidas | Run arrays o varios runs; o documentar como “meta-escenario” |

---

## F) Social / comunidad / proximidad (6)

| # | ID | Nombre | Idea | Palancas |
|---|----|--------|------|----------|
| 45 | [x] | **S1** | Strong communities: clústers con pocos enlaces entre clústers | POIs/clusters separados, okMaps o rutas que no mezclan mucho |
| 46 | [x] | **S2** | Weak communities: mezcla alta, clústers difusos | Muchos meeting spots, world pequeño, alta movilidad |
| 47 | [x] | **S3** | Periodic meetings: cada X minutos se juntan grupos | `waitTime` / `speed` que generen encuentros periódicos |
| 48 | [x] | **S4** | Random mixing: movilidad aleatoria sin hotspots | RandomWaypoint, sin POIs concentrados |
| 49 | [x] | **S5** | Two-layer: estudiantes + staff (2 grupos con speeds diferentes) | Group1/Group2 con `speed` y/o `waitTime` distintos |
| 50 | [x] | **S6** | Family groups: grupos pequeños persistentes | `minGroupSize`/`maxGroupSize` pequeños, `maxWaitTime` alto |

---

## G) Tráfico / mensajería y recursos extremos (10)

| # | ID | Nombre | Idea | Palancas |
|---|----|--------|------|----------|
| 51 | [x] | **T1** | Many small msgs: 1–5 KB, alta tasa | `Events1.size` 1k–5k, `Events1.interval` bajo |
| 52 | [x] | **T2** | Few huge msgs: 1–5 MB, baja tasa | `Events1.size` 1M–5M, `Events1.interval` alto |
| 53 | [x] | **T3** | Mixed bimodal: mezcla pequeños + grandes | Dos generadores de eventos (Events1/Events2) o rango amplio size |
| 54 | [x] | **T4** | Very short TTL: 300–600 s | `msgTtl` 5–10 min |
| 55 | [x] | **T5** | Very long TTL: 6–24 h | `msgTtl` 360–1440 min |
| 56 | [x] | **T6** | Uniform sources: from/to aleatorios | `Events1.hosts` amplio, sin `tohosts` (o tohosts = hosts) |
| 57 | [x] | **T7** | Targeted to hubs: muchos mensajes hacia un subconjunto | `Events1.tohosts` restringido a pocos hosts (hubs) |
| 58 | [x] | **T8** | Burst traffic: ráfagas en ventanas de tiempo | `Events1.time` en ventanas cortas, o varios Events con time distintos |
| 59 | [x] | **T9** | Buffer stress: buffers pequeños + tráfico alto | `bufferSize` bajo, `Events1.interval` bajo, size moderado |
| 60 | [x] | **T10** | High rate + low speed: “peor caso” congestión | `Events1.interval` bajo, `transmitSpeed` bajo, muchos mensajes |

---

## Resumen por familia

| Familia | Cantidad | IDs |
|--------|----------|-----|
| A) Urbanos map-based (WDM) | 12 | U1–U12 |
| B) Campus / evento / estadio | 8 | C1–C8 |
| C) Vehículos / transporte | 8 | V1–V8 |
| D) Rural / baja conectividad | 8 | R1–R8 |
| E) Disaster / post-catástrofe | 8 | D1–D8 |
| F) Social / comunidad | 6 | S1–S6 |
| G) Tráfico y recursos extremos | 10 | T1–T10 |
| **Total** | **60** | |

---

## Notas para el paper

- **Vector de parámetros:** Para cada escenario, documentar en un .settings (o tabla anexa) el valor concreto de cada palanca usada.
- **Diversidad:** La variedad debe venir de **familias distintas** (map-based vs open space, clúster vs mezcla, carga vs TTL, movilidad alta vs baja).
- **Correlación:** Evitar que los 60 escenarios sean variaciones lineales de uno solo; combinar ejes (movimiento, tráfico, recursos, topología).
- **Reproducibilidad:** Fijar `MovementModel.rngSeed` (y semillas de eventos si aplica) por escenario y documentarlos.

Cuando implementes cada escenario, marca la casilla correspondiente en la tabla y asocia el archivo (p. ej. `corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiMedium.settings` → U1 o referencia similar).
