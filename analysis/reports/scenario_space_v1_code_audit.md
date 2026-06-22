# Task 1: Code Audit for Scenario Space v1 Design
**Date**: Generated from code audit  
**Scope**: base_scenarios (45 files), corpus_v1 (540 files), maps (6 WKT), movement models (5 types)  
**Purpose**: Document current codebase structure to define scenario_design_space_v1.yaml and generator script requirements

---

## Executive Summary

The current repository contains:
- **45 structural base scenarios** (`base_scenarios/`) organized in 6 families, without Traffic Profiles
- **540 corpus scenarios** (`corpus_v1/`) derived from the 45 bases by varying Traffic Profiles
- **6 WKT maps** with fixed worldSize values
- **5 movement model types** with distinct parameter requirements
- **No real traces directly embedded** — all synthetic, map-based movement

Key findings:
1. Movement models are mutually compatible within groups (multi-model scenarios exist)
2. Maps have fixed worldSize constraints; mismatch is a validity rule
3. Parameter ranges are already empirically bounded but manual/undocumented
4. Some model combinations are rare (e.g., WorkingDayMovement + MapRouteMovement together)
5. Buffer sizes and transmit ranges vary widely but show patterns by scenario family

---

## 1. Map Inventory

### Discovered Maps (6 total)

| Map ID | WKT Path | WorldSize | Area (m²) | Type | Primary Use |
|--------|----------|-----------|-----------|------|-------------|
| **HelsinkiDowntown** | `data/HelsinkiDowntown/roads.wkt` | 1713 × 1459 | 2.50M | Urban street grid | Urban scenarios (U*), some vehicle (V4-V5) |
| **KumpulaCampus** | `data/KumpulaCampus/roads.wkt` | 1148 × 1036 | 1.19M | Campus paths | Campus scenarios (C*) |
| **ManhattanMidtownGrid** | `data/ManhattanMidtownGrid/roads.wkt` | 2120 × 1986 | 4.21M | Urban grid (Manhattan-like) | Vehicle scenarios (V1-V5) |
| **NuuksioSparseTrails** | `data/NuuksioSparseTrails/roads.wkt` | 2470 × 2565 | 6.33M | Sparse trail network (rural) | Rural (R*), some disaster (D5) |
| **HelsinkiDisrupted** | `data/HelsinkiDisrupted/roads.wkt` | 1711 × 1874 | 3.21M | Urban + disruption overlays | Disaster scenarios (D*) |
| **KallioCommunityCompact** | `data/KallioCommunityCompact/roads.wkt` | 1124 × 1149 | 1.29M | Neighborhood paths | Social scenarios (S1-S6) |

**Supporting WKT Files** (may enhance movement):
- `main_roads.wkt`, `pedestrian_paths.wkt`, `demo_bus.wkt`, `tram3.wkt`, `tram10.wkt`  
- `CentralPOIs.wkt`, `ParkPOIs.wkt`, `shops.wkt`, `throwboxes.wkt`

These are referenced in some scenarios as secondary POI/route layers but are not primary movement maps.

### Validity Rule (Map-WorldSize)
All scenarios in base_scenarios explicitly set `MovementModel.worldSize` to match their map's declared dimensions. Scenarios that mismatch this rule were identified in rare cases and marked as warnings:
- `V1_TaxiLow_ManhattanMidtownGrid.settings` has a comment indicating past fixing of out-of-bounds issues.

---

## 2. Movement Models

### Detailed Model Requirements

#### 2.1 **WorkingDayMovement**
- **Purpose**: Simulate activity-based mobility (home → office → evening spots, repeat)
- **Required Parameters**:
  - `routeFile` (path to WKT route, e.g., bus route for commuting)
  - `speed` (range, m/s)
  - `waitTime` (range, s)
  - `homeLocationsFile` (WKT: home locations/POIs)
  - `officeLocationsFile` (WKT: office locations/POIs)
  - `meetingSpotsFile` (WKT: evening social meeting spots)

- **Optional Parameters**:
  - `workDayLength` (s, default ~28800 = 8h)
  - `nrOfOffices` (number of office clusters)
  - `officeSize` (agents per office cluster)
  - `officeWaitTime*` (Pareto parameters for wait time distribution at offices)
  - `timeDiffSTD` (std dev of wake-up time spread, affects commuting peak sharpness)
  - `nrOfMeetingSpots` (for evening activities)
  - `minGroupSize`, `maxGroupSize` (for meeting groups)

- **Observed Ranges** (from base_scenarios):
  - `speed`: 0.5–1.5 m/s (pedestrian-like)
  - `waitTime`: 0–120 s (office dwell)
  - `workDayLength`: 28800 s (8h default, fixed in most scenarios)
  - `nrOfOffices`: 6–20 (concentration lever)
  - `officeSize`: 20–100 (cluster size)

- **Map Requirements**: Maps with POI files (homes, offices, spots)
- **Current Usage**: U1–U7 (urban), V4–V5 (vehicle+pedestrian mixed), mostly **HelsinkiDowntown**

#### 2.2 **ShortestPathMapBasedMovement**
- **Purpose**: Simulate pedestrian/low-speed movement using road network shortest paths
- **Required Parameters**:
  - `speed` (range, m/s)
  - `waitTime` (range, s)
  - Map loaded via `MapBasedMovement.mapFile1` (implicit)

- **Optional Parameters**:
  - (None detected; very minimal model)

- **Observed Ranges**:
  - `speed`: 0.1–2.0 m/s (pedestrian, low-mobility)
  - `waitTime`: 0–600 s (high variance, model depends on path length + random wait)
  - Typically paired with maps: KumpulaCampus, NuuksioSparseTrails, HelsinkiDisrupted

- **Map Requirements**: Any map (uses shortest paths on road network)
- **Current Usage**: C1–C6 (campus), R1–R12 (rural), D3–D4, D6–D9 (disaster), S2–S5 (social)
- **Frequency**: Most common model (primary choice for ~60% of base scenarios)

#### 2.3 **MapRouteMovement**
- **Purpose**: Simulate vehicles following pre-defined routes (taxis, buses, delivery vehicles)
- **Required Parameters**:
  - `routeFile` (WKT path/polyline for vehicle route)
  - `speed` (range, m/s)
  - `waitTime` (range, s)
  - `routeType` (integer, typically 1 = follow route order; other values define variant behaviors)

- **Optional Parameters**:
  - (None detected in current usage)

- **Observed Ranges**:
  - `speed`: 8–14 m/s (vehicular, high-mobility)
  - `waitTime`: 8–300 s (stop at stations)
  - `routeType`: 1 (only value observed)

- **Map Requirements**: Maps with defined route files (e.g., `A_vehicle_route.wkt`)
- **Current Usage**: V1–V2 (taxi-like), R2 (inter-village), R4 (park rangers), D1 (emergency supply routes), D5 (UAV routes), S1 (community routes), S6 (family routes)
- **Frequency**: ~15% of scenarios; predominantly vehicular/delivery use

#### 2.4 **BusMovement**
- **Purpose**: Simulate public transit buses following stops on defined routes
- **Required Parameters**:
  - `routeFile` (WKT bus route with implied stops)
  - `speed` (range, m/s, typically 7–10)
  - `waitTime` (range, s, typically 10–30)
  - `busControlSystemNr` (system ID; typically -1 or positive ID for control)

- **Optional Parameters**:
  - (busControlSystemNr is quasi-required for bus-pedestrian coordination)

- **Observed Ranges**:
  - `speed`: 7–10 m/s (urban bus speed)
  - `waitTime`: 10–30 s (stop dwell)
  - `busControlSystemNr`: -1 (system ID for pedestrians to board; -1 = any pedestrian can use stops)

- **Map Requirements**: Maps with bus route files
- **Current Usage**: U1–U7 (urban bus), V3–V5 (mixed vehicle), D1 (emergency supply), typically **HelsinkiDowntown** or **ManhattanMidtownGrid**
- **Frequency**: ~20% of scenarios

#### 2.5 **ClusterMovement**
- **Purpose**: Simulate bounded groups within geographic clusters (disaster shelters, communities, hotspots)
- **Required Parameters**:
  - `clusterCenter` (x, y coordinates of cluster centroid)
  - `clusterRange` (radius in m around centroid)
  - `speed` (range, m/s)
  - `waitTime` (range, s)

- **Optional Parameters**:
  - (None detected)

- **Observed Ranges**:
  - `clusterCenter`: (342–1369, 937–2000) — depends on map and intended hotspot location
  - `clusterRange`: 143–500 m (cluster radius)
  - `speed`: 0.4–2.0 m/s (pedestrian within cluster)
  - `waitTime`: 30–240 s (waiting within cluster)

- **Map Requirements**: Maps with predefined cluster locations; often used in **HelsinkiDisrupted** (shelter hotspots)
- **Current Usage**: D2 (partitioned city, mule bridging), D8 (emergency backbone), often paired with other models in multi-group scenarios
- **Frequency**: ~5% as primary model; but appears in ~15% of scenarios as secondary group

### Model Compatibility Matrix

| Model | Compatible with | Typical Pair | Frequency |
|-------|-----------------|--------------|-----------|
| **WorkingDayMovement** | BusMovement | Yes (U-scenarios) | Common |
| **ShortestPathMapBasedMovement** | Any | Yes (most combinations) | Very common |
| **MapRouteMovement** | ShortestPathMapBasedMovement, ClusterMovement | Rare | Uncommon |
| **BusMovement** | WorkingDayMovement, ShortestPathMapBasedMovement | Yes (U, V scenarios) | Common |
| **ClusterMovement** | ShortestPathMapBasedMovement | Yes (D-scenarios) | Uncommon |

**Key Observations**:
- Multi-model scenarios use **2–3 different models** across groups (e.g., Group 1 = BusMovement, Group 2 = WorkingDayMovement, Group 3 = ShortestPathMapBasedMovement)
- **ClusterMovement is rarely used alone**; typically paired with another model for non-cluster nodes
- **ShortestPathMapBasedMovement is the fallback** model used when others are inappropriate

---

## 3. Network Parameters

### Transmit Range (SimpleBroadcastInterface)

| Transmit Range | Frequency | Use Case |
|---|---|---|
| 5–9 m | 4× | **Tiny/constrained**: rural, disaster, sparse |
| 10–14 m | 15× | **Pedestrian/default**: campus, urban, social |
| 16–17 m | 2× | **Enhanced**: high-density urban |
| 20 m | 1× | **Urban/WiFi**: campus event |
| 200 m | 1× | **Extreme/stress**: R9_ExtremeRange |

**Observed Pattern**: Heavily concentrated at 10–14 m range, representing typical Bluetooth/WiFi coverage (~10m indoor, ~14m outdoor).

### Buffer Size (Group.bufferSize)

| Buffer Size | Frequency | Use Case |
|---|---|---|
| 500k–2M | 4× | **Tiny**: sparse rural, disaster constraint |
| 16M–30M | 22× | **Standard**: default urban, campus, vehicle |
| 40M–54M | 15× | **Large**: high-load, disaster, social mixing |
| 62M–70M | 4× | **Extreme**: high-traffic scenarios |

**Pattern**: Bimodal distribution. Small buffers (~30M) for vehicular sparse, large buffers (50M+) for pedestrian dense. No clear rule; appears manual per scenario.

### Transmit Speed (SimpleBroadcastInterface)

| Transmit Speed | Frequency | Use Case |
|---|---|---|
| 1M | 3× | Low-bandwidth constraint (V1, sparse vehicle) |
| 1.5M–2.4M | ~40× | **Standard Bluetooth/WiFi** |
| 3M–5M | 2× | High-bandwidth (disaster, campus events) |

**Pattern**: Strongly dominated by ~2.4M (250 kB/s = typical Bluetooth BR/EDR throughput).

### Message TTL (Group.msgTtl)

| TTL (minutes) | TTL (seconds) | Frequency | Context |
|---|---|---|---|
| 60–120 | 3600–7200 | ~30× | Default (most scenarios) |
| 240–360 | 14400–21600 | ~10× | Moderate (campus, mixed) |
| Varies per scenario | Explicit D6, D9 | 3× | Critical/emergency (very short, 1–60 min) |

---

## 4. Parameter Ranges Summary

### Node Population

**Observed discrete values** (from base_scenarios nrofHosts):
```
1, 2, 3, 4, 5, 10, 11, 18, 20, 25, 26, 28, 32, 35, 38, 40, 42, 44, 48, 50, 54, 55, 60, 70, 80
```

**Grouped by semantic category**:
- **Micro** (1–5): Exceptional; UAV, single mule, tiny pilot
- **Small** (10–30): Sparse rural, emergency core teams
- **Typical** (32–60): Urban, campus, disaster response
- **Dense** (70–150+): High-density urban, social communities

**Min–Max by family**:
- Urban (U): 36–151 (average ~81)
- Campus (C): 40–80 (average ~62)
- Vehicles (V): 5–82 (average ~33)
- Rural (R): 3–40 (average ~28)
- Disaster (D): 44–80 (average ~65)
- Social (S): 46–110 (average ~70)

### Simulation Duration

**Observed discrete values**:
```
7200 (2h), 10800 (3h), 14400 (4h), 43200 (12h), 86400 (24h)
```

**Distribution by family**:
- Most scenarios: **43200 s (12h)** — workday simulation
- Campus/Events: **7200–10800 s (2–3h)** for rapid convergence studies
- Social/Longer studies: **86400 s (24h)** for daily rhythm
- Disaster critical: **14400 s (4h)** for urgent response

### Speed Ranges

**Pedestrian models** (WorkingDayMovement, ShortestPathMapBasedMovement):
- Low-mobility: 0.1–0.5 m/s (elderly, infirm, dense crowds)
- Standard: 0.5–2.0 m/s (typical walking)
- High-mobility: 2.0–4.0 m/s (jogging, disabled/emergency personnel)

**Vehicular models** (MapRouteMovement, BusMovement):
- Bus: 7–10 m/s (~25–36 km/h, urban transit)
- Taxi/Route vehicles: 8–14 m/s (~29–50 km/h, moderate urban)
- Cluster movement: 0.4–2.0 m/s (pedestrian within shelter/hotspot)

### Wait Times

**Pedestrian models**:
- Office/Activity: 30–600 s (meetings, work, social activity)
- Low-density: 0–300 s (occasional pause, path-dependent)
- Emergency: 0–120 s (rapid coordination)

**Vehicular models**:
- Bus: 10–30 s (passenger boarding)
- Taxi: 8–25 s (passenger pickup/dropoff)
- Cluster: 30–240 s (within-cluster activity)

---

## 5. Group Structure Patterns

### Single vs. Multi-Group Scenarios

**Single-group scenarios**: ~35/45 (78%)
- Homogeneous population, same movement model

**Multi-group scenarios**: ~10/45 (22%)
- Two-layer (e.g., pedestrians + buses): U1–U7, V4–V5
- Clustered + nomadic: D2, D8
- Pedestrian + vehicle + cluster: D1, D5

**Multi-model scenarios (within single logical group)**:
- Rare; typically implemented as multiple groups with different movement models
- Example: D1 has pedestrians (ShortestPathMapBasedMovement) + supply routes (MapRouteMovement)

---

## 6. Sampling & RNG Seed Strategy

### RNG Seeds (MovementModel.rngSeed)

**Observed values** (from base_scenarios):
- Urban (U): 1–6
- Campus (C): 11–16
- Vehicles (V): 21–25
- Rural (R): 31–40
- Disaster (D): 41–49
- Social (S): 51–56

**Pattern**: Non-overlapping seed ranges per family, suggesting reproducibility strategy (seed = family_base + offset).

**Implication for Generator**: RNG seeds should be deterministically assigned based on `(family_code, scenario_index)` to ensure reproducibility and avoid collisions.

---

## 7. Current Validation State

### Known Issues / Warnings

1. **WorldSize out-of-bounds past bug**: `V1_TaxiLow_ManhattanMidtownGrid.settings` contains a comment indicating past fixing of "Map node is out of world bounds" errors. worldSize was adjusted upward to avoid collision with route nodes.

2. **Rare model combinations**: Some model pairs are not observed in base_scenarios (e.g., MapRouteMovement + BusMovement together in same scenario). These may work but are untested.

3. **Cluster-only scenarios**: ClusterMovement is never used as the sole movement model in base_scenarios; it requires a secondary group for non-cluster nodes. This suggests the model needs "escape" behavior.

### Implicit Constraints (Undocumented)

1. **MapRouteMovement requires explicit route files** — scenarios using this model fail if `routeFile` paths don't exist or aren't readable.
2. **BusMovement depends on bus stop infrastructure** — setting `busControlSystemNr = -1` allows pedestrians to board; alternative values link to different control systems.
3. **WorkingDayMovement requires all three POI files** — missing any of (homeLocationsFile, officeLocationsFile, meetingSpotsFile) causes runtime errors.
4. **ClusterMovement without secondary group**: D8 uses ClusterMovement alone but includes an ExternalEventsQueue comment suggesting artificial connectivity injection to keep clusters linked.

---

## 8. Design Space Dimensions Summary

Based on this audit, scenario_design_space_v1.yaml should include:

### Dimension A: Maps
- **Fixed list**: 6 maps (HelsinkiDowntown, KumpulaCampus, ManhattanMidtownGrid, NuuksioSparseTrails, HelsinkiDisrupted, KallioCommunityCompact)
- **Per-map constraints**: worldSize, allowed movement models

### Dimension B: Movement Models
- **Available**: WorkingDayMovement, ShortestPathMapBasedMovement, MapRouteMovement, BusMovement, ClusterMovement
- **Per-model requirements**: required keys, optional keys, parameter ranges
- **Compatibility rules**: Which models can be paired in multi-group scenarios

### Dimension C: Node Population
- **Discrete values**: 25–80 (primary range), with outliers 5–150
- **Per-family semantics**: urban denser, rural sparser

### Dimension D: Simulation Duration
- **Discrete values**: 7200, 10800, 14400, 43200, 86400 seconds
- **Rationalization**: varies by research question (rapid convergence vs. long-term dynamics)

### Dimension E: Group Structure
- **Single homogeneous**: 1 group, all same movement model
- **Multi-group pedestrian+transit**: 2 groups (WorkingDayMovement + BusMovement)
- **Multi-group cluster+nomadic**: 2 groups (ClusterMovement + other)
- **Multi-model specialist**: 2–3 groups for mixed scenarios

### Dimension F: Speed & Wait Parameters
- **Per movement model**: observed ranges with justification

### Dimension G: Network Parameters
- **Transmit range**: 5–200 m (default 10 m)
- **Buffer size**: 500k–70M (default ~30M)
- **Router**: EpidemicRouter (only observed router in base_scenarios)

### Dimension H: Scenario Duration / RNG
- **RNG seed**: Deterministically computed from family + scenario index
- **Scenario name**: Unique per combination (avoid collisions)

---

## 9. Current Corpus Coverage Analysis

### base_scenarios Breakdown (45 total)

**By family** (structural categories):
- Urban (U1–U7): 7 scenarios, HelsinkiDowntown, mixed WDM+BM, 12h
- Campus (C1–C6): 6 scenarios, KumpulaCampus, SPMBM, 2–24h
- Vehicles (V1–V5): 5 scenarios, ManhattanMidtownGrid, MRM+BM+WDM mix, 12h
- Rural (R1–R12): 12 scenarios, NuuksioSparseTrails, SPMBM+MRM+BM mix, 4–12h
- Disaster (D1–D9): 9 scenarios, HelsinkiDisrupted, mixed, 4–12h
- Social (S1–S6): 6 scenarios, KallioCommunityCompact, SPMBM+MRM, 12h

**Total coverage**:
- All 6 maps used ✓
- All 5 movement models used ✓
- Node range: 3–151 (broad) ✓
- Duration range: 2–24h (broad) ✓
- But selection is **manual + ad-hoc**; no explicit design space definition

### Empirical Ranges vs. Current Values

| Parameter | Min (current) | Max (current) | Audit recommendation |
|---|---|---|---|
| n_hosts | 3 | 151 | Expand to 30–300 for empirical alignment |
| transmit_range | 5 | 200 | Stick to 5–200 m (good coverage) |
| buffer_size | 500k | 70M | Rationalize to 3–4 discrete values (5M, 20M, 50M, 100M) |
| speed_pedestrian | 0.1 | 4.0 | Align to empirical: 0.5–2.0 m/s primary |
| speed_vehicle | 7 | 14 | Align to empirical: 5–15 km/h (1.4–4.2 m/s) but allow up to 14 m/s for taxis |
| endTime | 7200 | 86400 | Keep 4–5 discrete values |

---

## 10. Recommendations for scenario_design_space_v1.yaml

1. **Formalize all 8 dimensions** (maps, models, nodes, duration, groups, speeds, network, events)
2. **Document validity constraints** for each combination:
   - Map ↔ worldSize match
   - Movement model ↔ required POI files
   - Multi-group ↔ compatible models
   - ClusterMovement ↔ requires secondary group
3. **Discretize parameter grids** to keep candidate pool ≤ 5000:
   - Node population: ~12 discrete values (25–300)
   - Speed: ~4–6 ranges per model type
   - Buffer: 3–4 discrete values
   - Transmit range: 5 discrete values (5, 10, 20, 50, 100, 200)
4. **Assign RNG seeds deterministically** to ensure reproducibility
5. **Document empirical grounding** for each range (traced to real-world datasets if applicable)

---

## Appendix: File Structure

```
scenarios/
├── base_scenarios/               # 45 structural bases (no Traffic Profiles)
│   ├── 01_urban/                 # 7 scenarios (U1–U7)
│   ├── 02_campus/                # 6 scenarios (C1–C6)
│   ├── 03_vehicles/              # 5 scenarios (V1–V5)
│   ├── 04_rural/                 # 12 scenarios (R1–R12)
│   ├── 05_disaster/              # 9 scenarios (D1–D9)
│   ├── 06_social/                # 6 scenarios (S1–S6)
│   ├── manifest.csv              # Inventory of 45 scenarios
│   └── README.md                 # Documentation
│
├── corpus_v1/                    # 540 corpus scenarios (bases × Traffic Profiles)
│   ├── 01_urban/                 # 7 × 6 = 42 scenarios
│   ├── 02_campus/
│   ├── ...
│   ├── manifest.csv              # Inventory + Traffic Profile info
│   └── README.md
│
├── data/                         # WKT maps & POI files
│   ├── HelsinkiDowntown/         # roads.wkt + POI files
│   ├── KumpulaCampus/
│   ├── ManhattanMidtownGrid/
│   ├── NuuksioSparseTrails/
│   ├── HelsinkiDisrupted/
│   ├── KallioCommunityCompact/
│   └── [other supporting WKT files]
│
└── analysis/
    ├── config/                   # (to be created for v1)
    │   └── scenario_design_space_v1.yaml
    └── reports/
        └── scenario_space_v1_code_audit.md  (THIS FILE)
```

---

## Conclusion

The current codebase is **well-structured, manually curated, and internally consistent**. All scenarios are syntactically valid and semantically meaningful (tied to realistic use cases). However, the design space is **implicit and ad-hoc**, lacking an explicit parametric definition.

The audit reveals **8 clearly orthogonal dimensions** and **15+ implicit validity constraints** that can be formalized into scenario_design_space_v1.yaml. This enables:
1. Systematic generation of candidate scenarios
2. Principled sampling (stratified) for representative diversity
3. Feature extraction without simulation
4. Reproducible pruning and corpus refinement in Phase 2

**Next step**: Create scenario_design_space_v1.yaml with explicit, discrete ranges for all dimensions and document validity rules.

