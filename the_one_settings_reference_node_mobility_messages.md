# The ONE `.settings` reference for scenario generation

**Purpose.** This document summarizes the configurable features that appear in official The ONE settings and in the provided `U1_CBD_Commuting_HelsinkiDowntown__TP03_ManySmall.settings` example. It is intended to support the next phase of the project: defining a valid scenario design space before applying Traffic Profiles.

**Scope.** The tables focus on three groups of parameters:

1. **Node / group / network configuration**
2. **Mobility / map configuration**
3. **Message / event generation configuration**

It also includes reports and routing parameters because they are required to make scenarios executable and analyzable.

**Important note.** The ONE is Java-based and many settings are class-specific. A key is only valid if the referenced class reads it. Therefore, the ranges below are not universal mathematical limits. They are practical, defensible ranges for scenario generation, based on official settings, The ONE conventions, and the U1 example. Values outside these ranges may still run, but should be treated as stress, invalid, or requiring explicit justification.

---

## 1. Sources analyzed

### 1.1 Official The ONE repository

The official repository exposes the standard structure of The ONE, including:

- `default_settings.txt`
- `example_settings/`
- `wdm_settings/`
- `data/`
- `src/`
- `toolkit/`

The official root `default_settings.txt` is the main reference for global settings, group settings, interfaces, maps, message generation, reports, routers, optimization and GUI configuration.

### 1.2 Provided project setting

The provided setting corresponds to:

```text
U1_CBD_Commuting_HelsinkiDowntown__TP03_ManySmall.settings
```

It combines:

- map-aware movement over `data/HelsinkiDowntown/roads.wkt`;
- one bus group using `BusMovement`;
- one pedestrian group using `WorkingDayMovement`;
- WDM activity files for homes, offices and meeting spots;
- TP03 message generation: many small messages;
- Epidemic routing;
- `MessageStatsReport` and `ContactTimesReport`.

---

## 2. High-level `.settings` structure

A complete The ONE scenario usually contains these blocks:

```text
Scenario.*                  # simulation identity and time
MovementModel.*             # global movement seed, warmup, world size
MapBasedMovement.*          # map files for map-aware movement
Group.* / GroupN.*          # default group and group-specific parameters
<interfaceId>.*             # interface type, speed, range
Events.* / EventsN.*        # message or external event generation
Report.*                    # output reports
RouterSpecific.*            # optional router-specific parameters
Optimization.*              # simulation performance parameters
GUI.*                       # optional GUI visualization settings
```

---

# Part A — Node, group and network settings

## A.1 Scenario-level settings

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `Scenario.name` | Required | String | Unique simulation name. Used in reports and logs. | Unique alphanumeric name, usually with `_` and optional `__TPxx_Label`. | Must not collide with another scenario if reports share a folder. |
| `Scenario.simulateConnections` | Required/recommended | Boolean | Enables/disables connection simulation between nodes. | `true`, `false` | For DTN/OppNet routing evaluation, use `true`. |
| `Scenario.updateInterval` | Required/recommended | Seconds, float | Simulation update step. | `0.1`, `0.5`, `1.0` | Smaller values increase precision but slow simulation. Your U1 uses `0.1`. |
| `Scenario.endTime` | Required | Seconds | Total simulation duration. | 6h = `21600`, 12h = `43200`, 24h = `86400`; trace-inspired: 1–30 days for long studies. | For candidate generation, start with 6h, 12h, 24h before multi-day runs. |
| `Scenario.nrofHostGroups` | Required | Integer | Number of host groups declared. | `1–6` typical; higher possible. | Must match `Group1`, `Group2`, ... definitions. |

## A.2 Group defaults and group-specific overrides

The ONE supports a default `Group.*` block and overrides per `GroupN.*`. A group-specific value overrides the default.

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `Group.groupID` / `GroupN.groupID` | Required per group | String prefix | Prefix used for host names. | `p`, `c`, `b`, `v`, `a`, `g`, etc. | In official default, comments describe `groupID` as the group identifier/prefix. |
| `Group.nrofHosts` / `GroupN.nrofHosts` | Required per group or inherited | Integer | Number of hosts in a group. | Real-trace guided: 30–500 total. Per group: 1–200 typical. | Avoid huge dense groups with Epidemic unless marked stress. |
| `Group.bufferSize` / `GroupN.bufferSize` | Required/recommended | Bytes with suffix | Message buffer size. | `5M`, `10M`, `50M`, `100M`; stress: lower or higher. | U1 uses defaults around `45M–52M`. |
| `Group.router` / `GroupN.router` | Required | Router class name | Routing algorithm used by hosts. | `EpidemicRouter`, `ProphetRouter`, `SprayAndWaitRouter`, `MaxPropRouter` if available. | Use one default router for structural candidate generation; compare protocols later with overlays. |
| `Group.nrofInterfaces` / `GroupN.nrofInterfaces` | Required | Integer | Number of network interfaces. | `1–2` typical. | Must match `Group.interface1`, `Group.interface2`, etc. |
| `Group.interface1` / `GroupN.interface1` | Required if `nrofInterfaces >= 1` | Interface id | Assigns interface to group. | Example: `bt0`, `btInterface`. | Interface id must have a corresponding `<id>.type`. |
| `Group.interface2` / `GroupN.interface2` | Optional | Interface id | Adds second interface. | Example: `highspeedInterface`, `bb0`. | Useful for buses, infrastructure, backbone scenarios. |
| `Group.msgTtl` / `GroupN.msgTtl` | Optional but recommended | Minutes | Time-to-live of messages created by the group. | TP-independent structural placeholder: `300`, `720`, `1440`; TP-specific later. | In your project, TP TTL is implemented here, not in `Events1.ttl`. |
| `Group.activeTimes` / `GroupN.activeTimes` | Optional | Time intervals | Defines when nodes are active. | `start1,end1,start2,end2,...` | Official default comments list this as available. Use carefully; can change contact opportunities. |
| `Group.busControlSystemNr` / `GroupN.busControlSystemNr` | WDM/Bus optional/required depending on model | Integer | Links WDM users to a bus control system. | `-1` for default/global control system in your settings. | In U1, a bus host is created first to register stops. |

## A.3 Interface settings

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `<id>.type` | Required for each interface id | Interface class | Defines interface implementation. | `SimpleBroadcastInterface` | Official default uses `SimpleBroadcastInterface`. |
| `<id>.transmitSpeed` | Required | Bytes per second with suffix | Transmission speed. | `250k`, `2.4M`, `10M` | Official comments describe transmit speed as bytes per second. Your U1 uses `2.4M`. |
| `<id>.transmitRange` | Required | Meters | Radio/contact range. | `10`, `25`, `50`, `100`, `200`; stress: `1000`; event-only backbone: `0`. | Official default uses Bluetooth `10` m and high-speed `1000` m. Dense maps + large ranges cause many contacts. |

## A.4 Router-specific settings

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `ProphetRouter.secondsInTimeUnit` | Optional | Seconds | PRoPHET time unit. | `30` official default. | Only relevant for `ProphetRouter`. |
| `SprayAndWaitRouter.nrofCopies` | Optional | Integer | Number of Spray and Wait copies. | `2–20`; official default `6`. | Only relevant for Spray and Wait. |
| `SprayAndWaitRouter.binaryMode` | Optional | Boolean | Enables binary Spray and Wait. | `true`, `false`; official default `true`. | Only relevant for Spray and Wait. |

---

# Part B — Mobility and map settings

## B.1 Global movement settings

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `MovementModel.rngSeed` | Optional but required for reproducibility | Integer | Seed for movement model random generator. | `1–999999`; use documented seed list. | Essential for reproducibility. |
| `MovementModel.worldSize` | Required for non-implicit worlds; recommended always | `width, height` in meters | Simulation area size. | Must match map bounds or desired free-space area. | U1 uses `1713, 1459`. Wrong world size can distort spatial occupancy. |
| `MovementModel.warmup` | Optional | Seconds | Pre-simulation movement warmup before real simulation. | `0`, `1000`, `3600` | Official default uses `1000`. Use `0` if you want exact start state. |

## B.2 Map-based movement settings

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `MapBasedMovement.nrofMapFiles` | Required for map-based models | Integer | Number of WKT map layers. | `1–4` common. | Official default uses 4 map files. U1 uses 1 road file. |
| `MapBasedMovement.mapFile1` | Required if `nrofMapFiles >= 1` | Path to WKT | Main map graph or layer. | `data/<MapName>/roads.wkt` | Must exist and fit `worldSize`. |
| `MapBasedMovement.mapFile2...N` | Optional | Path to WKT | Additional map layers. | main roads, pedestrian paths, shops, etc. | Official default uses roads, main roads, pedestrian paths, shops. |
| `Group.okMaps` / `GroupN.okMaps` | Optional | List of map indexes | Restricts which map layers a group can use. | Example: `1`, `1,3`; default all maps. | Official default uses `Group2.okMaps = 1` for cars. |
| `Group.pois` / `GroupN.pois` | Optional | POI indexes and probabilities | Sets Points of Interest for ShortestPathMapBasedMovement. | `poiIndex1, prob1, poiIndex2, prob2, ...` | Official default comments list this for SPMBM. |

## B.3 Common mobility settings by group

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `Group.movementModel` / `GroupN.movementModel` | Required | Movement class name | Selects node mobility model. | `ShortestPathMapBasedMovement`, `MapRouteMovement`, `WorkingDayMovement`, `BusMovement`, `RandomWaypoint`, `ClusterMovement` if available in fork. | Required for every group or inherited from `Group`. |
| `Group.speed` / `GroupN.speed` | Required/recommended | `min, max` m/s | Movement speed range. | Pedestrian: `0.5,1.5` or `0.5,2.0`; bus/vehicle: `2.7,13.9`, `7,10`; stress only higher. | Official comments define speed in m/s. |
| `Group.waitTime` / `GroupN.waitTime` | Required/recommended | `min, max` seconds | Pause after reaching destination. | `0,120`, `10,30`, `30,240`, `300,1800` | Large waits reduce mobility/contact dynamics. |

## B.4 ShortestPathMapBasedMovement

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `Group.movementModel = ShortestPathMapBasedMovement` | Required to use model | Class name | Nodes choose destinations and move along shortest paths on WKT graph. | Use with valid `MapBasedMovement.mapFile*`. | Official default uses this as common movement model. |
| `Group.okMaps` | Optional | Map layer index list | Restricts movement to selected map layers. | `1`, `1,3`, default all. | Useful for cars vs pedestrians. |
| `Group.pois` | Optional | POI indexes/probabilities | Biases destinations. | Probabilities should be non-negative; sum should be meaningful. | Use only if POI map/layer is defined. |
| `Group.speed` | Required/recommended | m/s range | Speed on paths. | Pedestrian or vehicular depending group. | Keep consistent with scenario role. |
| `Group.waitTime` | Required/recommended | seconds range | Pause at destinations. | `0,120` typical. |  |

## B.5 MapRouteMovement and BusMovement

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `Group.movementModel = MapRouteMovement` | Required to use model | Class name | Moves along a predefined route file. | Use for trams, buses, fixed vehicle routes. | Official default uses `MapRouteMovement` for tram groups. |
| `Group.movementModel = BusMovement` | Required to use bus model | Class name | Bus-like movement along route/stops. | Use with route files and bus control system. | U1 uses a bus group to register stops. |
| `Group.routeFile` / `GroupN.routeFile` | Required for route-based movement | Path to WKT route | Route followed by nodes. | `data/<MapName>/A_bus.wkt`, `data/tram3.wkt` | Must exist. Should align with road graph or bus stops. |
| `Group.routeType` / `GroupN.routeType` | Required/recommended for route movement | Integer | Defines route behavior/type. | Official examples use `1` and `2`. | Treat as categorical; validate against The ONE implementation. |
| `Group.busControlSystemNr` | Required for WDM bus integration | Integer | Selects bus control system. | `-1` in your corpus. | If WDM users rely on buses, at least one bus route/host may be needed. |
| `Group.speed` | Required | m/s range | Route vehicle speed. | Bus/tram: `7,10`; slow vehicle: `2.7,13.9`. | U1 bus uses `7,10`. |
| `Group.waitTime` | Required/recommended | seconds range | Waiting at route stops. | `10,30` official/U1 typical. |  |

## B.6 WorkingDayMovement

`WorkingDayMovement` is a composite activity-based model. In your U1 example it requires route and location files and controls home, office, shopping and evening activities.

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `Group.movementModel = WorkingDayMovement` | Required to use model | Class name | Activity-based daily mobility. | Use for commuting/campus/urban people. | Requires compatible WDM files. |
| `Group.routeFile` | Required/recommended | Path to WKT route | Public transport/bus route reference. | `data/<MapName>/A_bus.wkt` | U1 uses this for WDM stack. |
| `Group.homeLocationsFile` | Required | WKT points/polygons | Home locations. | `data/<MapName>/A_homes.wkt` | Must exist. |
| `Group.officeLocationsFile` | Required | WKT points/polygons | Office/work locations. | `data/<MapName>/A_offices.wkt` | Must exist. |
| `Group.meetingSpotsFile` | Required for evening activity | WKT points/polygons | Meeting/evening activity locations. | `data/<MapName>/A_meetingspots.wkt` | Must exist if evening activity is enabled. |
| `Group.timeDiffSTD` | Optional/recommended | Seconds | Variance/spread in activity times. | `0–3600`; U1: `1200`. | Higher values spread rush peaks. |
| `Group.workDayLength` | Optional/recommended | Seconds | Workday duration. | `14400–36000`; U1: `28800`. | 8h = 28800. |
| `Group.nrOfOffices` | Optional/recommended | Integer | Number of offices used by WDM. | `5–50`; U1: `12`. | Lower values concentrate commuters. |
| `Group.officeSize` | Optional/recommended | Integer | Capacity/size of offices. | `10–200`; U1: `60`. | Should scale with number of hosts. |
| `Group.officeWaitTimeParetoCoeff` | Optional | Float | Shape parameter for office waiting time. | `1.1–3.0`; U1: `1.4`. | Values near 1 can be heavy-tailed. |
| `Group.officeMinWaitTime` | Optional | Seconds | Minimum office wait. | `60–1800`; U1: `300`. |  |
| `Group.officeMaxWaitTime` | Optional | Seconds | Maximum office wait. | `600–14400`; U1: `900`. | Must be >= min. |
| `Group.nrOfMeetingSpots` | Optional/recommended | Integer | Number of meeting spots. | `3–30`; U1: `10`. |  |
| `Group.minGroupSize` | Optional | Integer | Minimum evening group size. | `1–5`; U1: `1`. | Must be <= max. |
| `Group.maxGroupSize` | Optional | Integer | Maximum evening group size. | `2–20`; U1: `5`. | Should fit `nrofHosts`. |
| `Group.minWaitTime` | Optional | Seconds | Minimum evening/activity wait. | `60–1800`; U1: `300`. | Ambiguous generic name; used by WDM activity. |
| `Group.maxWaitTime` | Optional | Seconds | Maximum evening/activity wait. | `600–7200`; U1: `1800`. | Must be >= min. |
| `Group.eveningActivityControlSystemNr` | Optional | Integer | Control system id for evening activity. | `-1` or non-negative ids. | U1 uses `-1`. |
| `Group.shoppingControlSystemNr` | Optional | Integer | Control system id for shopping activity. | `-1` or non-negative ids. | U1 uses `-1`. |
| `Group.nrOfShops` | Optional | Integer | Number of shops. | `3–50`; U1: `15`. |  |
| `Group.shopSize` | Optional | Integer | Capacity/size of shops. | `5–100`; U1: `25`. |  |
| `Group.shoppingWaitTimeParetoCoeff` | Optional | Float | Shopping wait shape. | `1.1–3.0`; U1: `1.4`. |  |
| `Group.shoppingMinWaitTime` | Optional | Seconds | Minimum shop wait. | `30–600`; U1: `60`. |  |
| `Group.shoppingMaxWaitTime` | Optional | Seconds | Maximum shop wait. | `300–3600`; U1: `600`. |  |
| `Group.minAfterShoppingStopTime` | Optional | Seconds | Minimum stop after shopping. | `0–600`; U1: `60`. |  |
| `Group.maxAfterShoppingStopTime` | Optional | Seconds | Maximum stop after shopping. | `60–3600`; U1: `600`. | Must be >= min. |
| `Group.probGoShoppingAfterWork` | Optional | Probability | Probability of shopping after work. | `0.0–1.0`; U1: `0.3`. |  |
| `Group.ownCarProb` | Optional | Probability | Probability that user owns/uses car. | `0.0–1.0`; U1: `0.0`. | Set >0 only if car behavior is supported/configured. |

## B.7 ClusterMovement

`ClusterMovement` is not in the official default settings shown above, but it appears in your project. It is a free-space/community model, not a map-following model, unless your fork modifies it.

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `Group.movementModel = ClusterMovement` | Required to use model | Class name | Moves nodes around a local cluster center. | Use for social, disaster partitions, local routines. | Does not necessarily use map roads. |
| `Group.clusterCenter` | Required | `x, y` meters | Center of local movement. | Must be inside `worldSize`. | Validate against map useful area if map-aware interpretation is required. |
| `Group.clusterRange` | Required | Meters | Radius/extent around cluster center. | `20–500`; often proportional to map size. | Too small = dense contact explosion; too large = weak community. |
| `Group.speed` | Required/recommended | m/s range | Local movement speed. | `0.3–1.5` pedestrian/local. |  |
| `Group.waitTime` | Required/recommended | seconds range | Local pause time. | `30,240`, `60,600`, etc. |  |

## B.8 RandomWaypoint

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `Group.movementModel = RandomWaypoint` | Required to use model | Class name | Free-space random destination movement. | Use as baseline/theoretical model. | Requires `MovementModel.worldSize`. |
| `Group.speed` | Required/recommended | m/s range | Movement speed. | Pedestrian: `0.5,1.5`; vehicle only if justified. |  |
| `Group.waitTime` | Required/recommended | seconds range | Pause between random movements. | `0,120`, `30,300`, `300,1800`. |  |

---

# Part C — Message and event settings

## C.1 Event framework

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `Events.nrof` | Required if using events | Integer | Number of event generators. | `1–3` typical. | TP09 uses two generators in your project. |
| `EventsN.class` | Required for each event generator | Event class name | Defines event generator type. | `MessageEventGenerator`, `ExternalEventsQueue` | Contact traces/backbones use external events. |

## C.2 MessageEventGenerator

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `EventsN.class = MessageEventGenerator` | Required to use generator | Class name | Creates messages during simulation. |  | Official default uses `MessageEventGenerator`. |
| `EventsN.interval` | Required | `min,max` seconds | Time between new message creations. | Low load: `120,600`; baseline: `60,120`; high load: `10,30`; storm: lower. | Your TP03 uses `10,30`. |
| `EventsN.size` | Required | `min,max` bytes with suffix | Message size range. | Small: `1k,10k`; baseline: `50k,150k`; large: `500k,1M+`. | Official default uses `500k,1M`; U1 TP03 uses `1k,10k`. |
| `EventsN.hosts` | Required/recommended | `first,last` host index range | Allowed source/destination host address range. | `0,totalHosts`; e.g. U1: `0,81`. | Must match host count/addressing convention. |
| `EventsN.prefix` | Required/recommended | String | Message id prefix. | `M`, `B`, `S`, etc. | Official default uses `M`. |
| `EventsN.time` | Optional | `start,end` seconds | Restricts message generation to a time window. | `0,endTime`, burst windows such as `21600,28800`. | Use for bursts, warmup-safe windows, or post-event traffic. |
| `EventsN.tohosts` | Optional | `first,last` host range | Restricts message destinations. | Hub/sink/group ranges. | Used for one-to-many, many-to-one, hub-target or group-to-group profiles. |

## C.3 TTL implementation

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `Group.msgTtl` / `GroupN.msgTtl` | Optional but important | Minutes | Message lifetime. | Critical: `5–15`; baseline: `300–720`; long: `1440+`. | In your fork/project, TTL is controlled here, not with `EventsN.ttl`. |

## C.4 ExternalEventsQueue

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `EventsN.class = ExternalEventsQueue` | Required to use external events | Class name | Reads events from a file. | Used for connection traces/backbone events. | Your D8 uses forced CONN events. DieselNet converter outputs contact events. |
| `EventsN.filePath` | Required | Path | External event file. | `scenarios/.../events.txt` | Must exist. |
| `EventsN.nrofPreload` | Optional | Integer | Number of events to preload. | `10–1000`; D8 example uses `50`. | Tune for performance. |

## C.5 Neutral placeholder message block for structural candidate generation

For `scenario_space_v1`, before Traffic Profiles, use a neutral executable block only to keep settings runnable:

```text
Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 60, 120
Events1.size = 50k, 150k
Events1.hosts = 0, <total_hosts>
Events1.prefix = M
Group.msgTtl = 300
```

This block should be documented as **placeholder traffic**, not as an experimental Traffic Profile.

---

# Part D — Reports and analysis settings

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `Report.nrofReports` | Required for reports | Integer | Number of report classes loaded. | `1–10` typical. | Must match `Report.report1..N`. |
| `Report.reportDir` | Required/recommended | Path | Output directory. | `reports/` | Shared report dir requires unique `Scenario.name`. |
| `Report.report1`, `Report.report2`, ... | Required if `nrofReports > 0` | Report class name | Selects output reports. | `MessageStatsReport`, `ContactTimesReport`, `ConnectivityONEReport`, custom reports. | Official default uses MessageStats and ContactTimes. |
| `Report.warmup` | Optional | Seconds | Report warmup period. | `0`, `1000`, `3600`. | Official default uses `0`. |

Recommended reports for candidate validation:

| Report | Use |
|---|---|
| `MessageStatsReport` | delivery, latency, overhead, drops. |
| `ContactTimesReport` | contact duration distribution. |
| `ConnectivityONEReport` / equivalent | contact events over time. |
| `NodePositionReport` / custom | positions for spatial occupancy and heatmaps. |
| `SpatialOccupancyReport` / custom | grid occupancy metrics. |

---

# Part E — Optimization and GUI settings

These are not part of the scientific scenario definition, but they can affect performance or visualization.

| Setting | Required? | Type / format | What it does | Practical range / values | Notes |
|---|---:|---|---|---|---|
| `Optimization.cellSizeMult` | Optional | Number | Optimization grid/cell multiplier. | Official default `5`. | Affects simulation speed. |
| `Optimization.randomizeUpdateOrder` | Optional | Boolean | Randomizes host update order. | `true`, `false`; official default `true`. | Keep fixed for reproducibility. |
| `GUI.UnderlayImage.fileName` | Optional | Path | GUI map underlay image. | PNG path. | Visualization only. |
| `GUI.UnderlayImage.offset` | Optional | `x,y` pixels | Underlay image offset. | Depends on image. |  |
| `GUI.UnderlayImage.scale` | Optional | Float | Underlay scale. | Depends on image/map. |  |
| `GUI.UnderlayImage.rotate` | Optional | Radians | Underlay rotation. | Small float. |  |

---

# Part F — Analysis of the provided U1 setting

## F.1 Node/network configuration

| Aspect | Value in U1 | Assessment |
|---|---|---|
| Simulation duration | `43200` seconds, 12h | Reasonable for a workday/commuting scenario. |
| Update interval | `0.1` | Precise but computationally more expensive. |
| Total hosts | 1 bus + 80 pedestrians = 81 | Reasonable urban pedestrian density. |
| Router | `EpidemicRouter` | Good baseline/stress router, but can explode with high contact density and high traffic. |
| Buffer | `45M–52M` | Reasonable; not too small for TP03 small messages. |
| Interface | `SimpleBroadcastInterface`, `2.4M`, range `10m` | Bluetooth-like proximity. Good for OppNet contact simulation. |
| TTL | `7200` minutes | Very long for TP03. This means most messages do not expire within 12h. Good if intentionally testing load, but not good for critical TTL behavior. |

## F.2 Mobility configuration

| Aspect | Value in U1 | Assessment |
|---|---|---|
| Map | `HelsinkiDowntown/roads.wkt` | Coherent with urban/CBD commuting. |
| Bus | `BusMovement`, `A_bus.wkt`, speed `7,10` | Coherent as public transport support. Validate route alignment with roads. |
| Pedestrians | `WorkingDayMovement` | Strong choice for commuting narrative. |
| Pedestrian speed | `0.5,1.5` m/s | Realistic. |
| Pedestrian wait | `0,120` | Reasonable for urban movement. |
| Offices | `nrOfOffices=12`, `officeSize=60` | Concentrated CBD behavior. Good narrative. |
| Workday length | `28800` seconds | 8h. Coherent. |
| Shopping probability | `0.3` | Reasonable optional evening/shopping behavior. |
| Car probability | `0.0` | Coherent if this scenario is pedestrian + bus. |

## F.3 Message configuration

| Aspect | Value in U1 TP03 | Assessment |
|---|---|---|
| Event class | `MessageEventGenerator` | Standard. |
| Interval | `10,30` seconds | High message creation rate. Correct for `ManySmall`, but computationally heavier with Epidemic. |
| Size | `1k,10k` | Coherent with many small messages. |
| Hosts | `0,81` | Covers all hosts. Check whether host indexing is inclusive/exclusive in your parser/report assumptions. |
| Prefix | `M` | Standard. |

## F.4 Main risks

1. **Epidemic + TP03 + dense WDM contacts** can create high relay counts.
2. **TTL = 7200 minutes** is much longer than the simulation. This is fine for high-delivery/load behavior but should be documented.
3. **BusControlSystem dependency** is fragile: if the bus host or route is removed, WDM bus stop registration may fail.
4. **Spatial occupancy interpretation** must use useful map area, not the full white bounding box, otherwise coverage can be underestimated.

---

# Part G — Recommended parameter grid for `scenario_space_v1`

## G.1 Structural normal ranges

| Dimension | Suggested values |
|---|---|
| `Scenario.endTime` | `21600`, `43200`, `86400` |
| total hosts | `30`, `40`, `60`, `80`, `100`, `150`, `200`, `300`, `500` |
| pedestrian speed | `0.5,1.0`, `0.5,1.5`, `0.8,1.8` |
| vehicle speed | `2.7,7.0`, `7,10`, `5,15` m/s if justified |
| wait time | `0,120`, `30,240`, `60,600`, `300,1800` |
| transmit range | `10`, `25`, `50`, `100`, `200` |
| buffer size | `5M`, `10M`, `50M`, `100M` |
| groups | `1`, `2`, `3`, `4` |
| router placeholder | `EpidemicRouter` initially, overlays later |

## G.2 Stress-only ranges

| Dimension | Stress values | Why stress |
|---|---|---|
| total hosts | `500+` | Heavy contact and routing load. |
| transmit range | `200+`, `1000` | Very dense connectivity. |
| message interval | `<10s` | High traffic pressure. |
| compact map + many nodes | Any | Contact explosion risk. |
| Epidemic + high density + high load | Any | Can cause timeouts. |

---

# Part H — Validity rules for scenario generation

| Rule id | Rule |
|---|---|
| `R001` | `Scenario.name` must be unique. |
| `R002` | `Scenario.nrofHostGroups` must match declared `GroupN` blocks. |
| `R003` | Total hosts must be consistent with `Events1.hosts` if a placeholder traffic block is generated. |
| `R004` | Any referenced map or route file must exist. |
| `R005` | `MapRouteMovement` and `BusMovement` require `routeFile`. |
| `R006` | Map-based movement requires at least one `MapBasedMovement.mapFileN`. |
| `R007` | `ClusterMovement` requires valid `clusterCenter` and `clusterRange`. |
| `R008` | Cluster centers must be inside `MovementModel.worldSize`. |
| `R009` | `min` values must be <= `max` values for speed, wait and size intervals. |
| `R010` | Pedestrian groups should not use vehicular speeds unless explicitly marked as stress/hybrid. |
| `R011` | Dense compact maps with high transmit range and many hosts should be marked as stress. |
| `R012` | WDM scenarios require homes, offices and meeting spot files. |
| `R013` | If WDM depends on bus control, at least one bus route/host must be present. |
| `R014` | Reports count must match declared reports. |
| `R015` | Traffic Profiles must not be applied in `scenario_space_v1`; only placeholder events are allowed. |

---

# Part I — Paper-ready methodological wording

The scenario generator should not claim to cover “all possible real-world situations.” A defensible formulation is:

> The generated candidate pool covers an explicitly defined scenario design space derived from simulator constraints, real-trace parameter ranges, and map-aware mobility configurations. Completeness is therefore defined with respect to this declared design space, not with respect to all possible DTN/OppNet environments.

