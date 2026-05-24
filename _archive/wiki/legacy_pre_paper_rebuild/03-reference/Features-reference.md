# Features reference

**English** | [Español](Features-reference-es)

---

This page documents the **46 features** (extended) and the **23 core features** used for diversity and paper, and the **settings that are not used** in the feature vector, with the reason for each.

- **Why 23 are core:** They define the scenario (scientific change if they vary), have low redundancy within core, are interpretable and tied to network hypotheses (mobility, contact, traffic, resources), and are corpus-wide (no over-representing a single family). Full justification: [features_core_vs_extended.md](../../analysis/docs/features_core_vs_extended.md).
- **Why others are discarded or extended:** Settings not used (IDs, paths, constants, redundant, implementation detail): [features_decision.md](../../analysis/docs/features_decision.md). Extended (e.g. density, pause_ratio, mm_ShortestPath, event2_*, pattern_uniform, WDM detail) are for exploration/dashboard only; reasons in features_core_vs_extended.md §3.
- **Single results reference:** [RESULTADOS_ACTUALES.md](../../analysis/reports/RESULTADOS_ACTUALES.md).

The feature vector is extracted by `run_analysis.py` (phase `features`). Reports: `--phase features_report` → `analysis/reports/features_report.txt` and `features_report.md`.

---

## Features used (46)

These form the per-scenario vector used for Pearson/Spearman correlation, cosine distance, clustering, and figures. Space is encoded as **world_area** and **aspect_ratio** (not Wx, Wy separately).

| Feature | Description | Origin (setting) |
|---------|-------------|------------------|
| world_area | World area Wx×Wy (m²) | MovementModel.worldSize |
| aspect_ratio | Aspect ratio min(Wx,Wy)/max(Wx,Wy) ∈ (0,1] | MovementModel.worldSize |
| N | Number of hosts | Scenario.nrofHostGroups, Group*.nrofHosts |
| density | Density proxy (hosts/km²); excluded from core (redundant with N, world_area) | N, world_area (derived) |
| speed_mean | Mean speed (m/s) | Group*.speed |
| pause_ratio | Pause/(move+pause) ratio | Group*.waitTime (derived) |
| wait_mean | Mean wait time (s) | Group*.waitTime |
| mm_WDM | Uses WorkingDayMovement (0/1) | Group*.movementModel |
| mm_RWP | Uses RandomWaypoint (0/1) | Group*.movementModel |
| mm_MapRoute | Uses MapRouteMovement (0/1) | Group*.movementModel |
| mm_Cluster | Uses ClusterMovement (0/1) | Group*.movementModel |
| mm_Bus | Uses BusMovement (0/1) | Group*.movementModel |
| mm_ShortestPath | Uses ShortestPathMapBasedMovement (0/1) | Group*.movementModel |
| mm_External | Uses External/ExternalPathMovement (0/1) | Group*.movementModel |
| mm_Linear | Uses LinearMovement (0/1) | Group*.movementModel |
| transmitRange | Transmission range (m) | bt0.transmitRange / interface.transmitRange |
| contact_rate_proxy | Contact rate proxy | density, transmitRange, speed (derived) |
| event_interval_mean | Mean message interval (s) | Events1.interval |
| event_size_mean | Mean message size (bytes) | Events1.size |
| msgTtl | Message TTL (s) | Group*.msgTtl |
| pattern_uniform | Uniform traffic pattern (0/1) | Events* (no time/tohosts) |
| pattern_burst | Burst/time-window traffic (0/1) | Events*.time |
| pattern_hub_target | Hub-targeted traffic (0/1) | Events*.tohosts |
| nrof_event_generators | Number of event generators | Events.nrof |
| bufferSize | Buffer size (bytes) | Group*.bufferSize |
| transmitSpeed | Transmission speed (bytes/s) | bt0.transmitSpeed |
| workDayLength | Work day length (s); NaN if not WDM | Group*.workDayLength |
| timeDiffSTD | Time diff std (s); NaN if not WDM | Group*.timeDiffSTD |
| probGoShoppingAfterWork | Prob. go shopping; NaN if not WDM | Group*.probGoShoppingAfterWork |
| nrOfMeetingSpots | Number of meeting spots; NaN if not WDM | Group*.nrOfMeetingSpots |
| nrOfOffices | Number of offices; NaN if not WDM | Group*.nrOfOffices |
| officeSize | Office size (persons); NaN if not WDM | Group*.officeSize |
| nrOfShops | Number of shops; NaN if not WDM | Group*.nrOfShops |
| ownCarProb | Car ownership probability (0–1); vehicular/WDM | Group*.ownCarProb |
| shopSize | Shop size (persons); NaN if not WDM | Group*.shopSize |
| officeWaitTime_mean | Mean office wait time (s); NaN if not WDM | Group*.officeMinWaitTime, officeMaxWaitTime |
| shoppingWaitTime_mean | Mean shopping wait time (s); NaN if not WDM | Group*.shoppingMinWaitTime, shoppingMaxWaitTime |
| eveningGroupSize_mean | Evening activity group size mean; NaN if not WDM | Group*.minGroupSize, maxGroupSize |
| eveningWaitTime_mean | Evening activity wait time mean (s); NaN if not WDM | Group*.minWaitTime, maxWaitTime |
| afterShoppingStopTime_mean | Mean stop time after shopping (s); NaN if not WDM | Group*.minAfterShoppingStopTime, maxAfterShoppingStopTime |
| clusterRange_mean | Mean cluster radius (m); NaN if not ClusterMovement | Group*.clusterRange |
| event2_interval_mean | Mean interval 2nd event stream (s); NaN if Events.nrof&lt;2 or filePath | Events2.interval |
| event2_size_mean | Mean size 2nd event stream (bytes); NaN if Events.nrof&lt;2 or filePath | Events2.size |
| Scenario.endTime | Simulation duration (s) | Scenario.endTime |
| nrofHostGroups | Number of host groups | Scenario.nrofHostGroups |
| has_active_times | Groups with activeTimes defined (0/1) | Group*.activeTimes |

---

## Settings not used

These keys appear in one or more `.settings` files in the corpus but are **not** used to build the feature vector. Reason is given for each.

| Setting | Reason |
|---------|--------|
| `Events1.class` | Generator type; same across corpus |
| `Events1.hosts` | Host range; redundant with N |
| `Events1.prefix` | Message identifier |
| `Events2.*` (class, filePath, hosts, nrofPreload, prefix) | Not in current design; possible future extension |
| `Group.LinearMovement.*` | Not in current design; possible future extension |
| `Group.busControlSystemNr` | Internal reference to bus system |
| `Group.eveningActivityControlSystemNr` | Internal reference |
| `Group.homeLocationsFile` | File path; not comparable across maps |
| `Group.meetingSpotsFile` | Same |
| `Group.officeLocationsFile` | Same |
| `Group.routeFile` | File path |
| `Group.router` | Same in entire corpus (EpidemicRouter) |
| `Group.nrofInterfaces` | Almost always 1; low variability |
| `Group.officeWaitTimeParetoCoeff` | Fine-grained WDM detail (we use officeWaitTime_mean) |
| `Group.shoppingWaitTimeParetoCoeff` | Same (we use shoppingWaitTime_mean) |
| `Group.minAfterShoppingStopTime`, `Group.maxAfterShoppingStopTime` | Not included; fine-grained post-shopping detail |
| `Group.shoppingControlSystemNr` | Internal reference |
| `Group.okMaps`, `Group.routeType` | Not in current design |
| `Group1.*` (routeFile, routeType, groupID, busControlSystemNr, clusterCenter, clusterRange, LinearMovement.*, nrofInterfaces, router) | File paths, internal refs, or identifiers; or not in design |
| `Group2` … `Group12` (clusterCenter, clusterRange, groupID, routeFile, etc.) | Same as above for other groups |
| `MapBasedMovement.mapFile1`, `MapBasedMovement.nrofMapFiles` | File path/count; not comparable numerically |
| `MovementModel.rngSeed` | Randomness; does not characterise scenario stably |
| `Report.*` | Output configuration, not scenario input |
| `Scenario.name` | Scenario identifier, not a numeric feature |
| `Scenario.simulateConnections`, `Scenario.updateInterval` | Fixed simulation parameters |
| `bt0.type` | Interface type; same across corpus |

---

## See also

- [Methodology](Methodology) — How features and correlation are defined  
- [Analysis pipeline reference](Analysis-pipeline-reference) — Phases and outputs  
- [Results overview](Results-overview) — Current metrics  
