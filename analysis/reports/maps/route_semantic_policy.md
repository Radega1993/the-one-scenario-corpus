# Route semantic policy

Auxiliary route files (`routeFile` in `.settings`) are **waypoint sequences** for `MapRouteMovement`. The ONE resolves movement between stops with **Dijkstra** on `roads.wkt` (`MapRouteMovement` / `DijkstraPathFinder`). Filenames should reflect scenario semantics, not a generic “bus” label on every map.

## Family → naming rules

| Family | Map | Semantic role | Accepted filenames | Rejected / legacy |
|--------|-----|---------------|-------------------|-------------------|
| 01_urban | HelsinkiDowntown | Urban bus lines | `A_bus.wkt`, `B_bus.wkt`, `C_bus.wkt` | `*_patrol`, `*_vehicle` |
| 02_campus | KumpulaCampus | Campus shuttle (optional asset) | `A_campus_shuttle.wkt` | `A_bus.wkt` |
| 03_vehicles | ManhattanMidtownGrid | Longitudinal grid routes | `A_vehicle_route.wkt`, `B_vehicle_route.wkt` | `A_bus.wkt`, `B_bus.wkt` |
| 04_rural | NuuksioSparseTrails | Ranger patrol | `A_ranger_patrol.wkt` | `A_bus.wkt` |
| 05_disaster | HelsinkiDisrupted | Emergency + mule | `A_emergency_route.wkt`, `B_mule_route.wkt` | `A_bus.wkt`, `B_bus.wkt` |
| 06_social | KallioCommunityCompact | Community local routes (optional) | `A_community_route.wkt`, `B_community_route.wkt` | `A_bus.wkt` |
| 07_ |  | Synthetic control route | `A_control_route.wkt` | `A_bus.wkt` |

## Settings update policy

- **Referenced maps only:** `.settings` under `base_scenarios/`, `corpus_v1/`, and `` are updated when `GroupN.routeFile` already points at a renamed path.
- **No new `routeFile`:** Kumpula, Kallio, and  keep movement models without `routeFile` in the corpus; semantic WKT may exist for figures and documentation only.

## Render legend (paper figures)

- **Solid line:** resolved road-following path (Dijkstra between consecutive stops).
- **Faint dashed line + markers:** stop order / `routeFile` waypoint polyline (reference only).
- **Red segment:** stop pair with no graph path (warning in title).

## Rationale by family

1. **Urban** — “Bus” is correct; three orthogonal-style routes cover dense OSM grid.
2. **Campus** — Shuttle tour on compact subgraph; not a public bus network.
3. **Vehicles** — N–S and E–W dominant axes on Manhattan grid; not TSP star tours.
4. **Rural** — Partial trail coverage; ranger patrol, not urban bus.
5. **Disaster** — Short emergency connector + mule segment; distinct from urban transit.
6. **Social** — Short local community paths; optional assets.
7. **Stress** — H/V control on synthetic grid; isolated from core 540 scenarios.

## The ONE runtime

```
routeFile  →  waypoints (WKT LINESTRING vertices)
roads.wkt  →  movement graph (MapBasedMovement.mapFile1)
```

Re-simulation is **not** required for renaming alone; regenerating waypoints changes future runs only.

## Inventory

Machine-readable inventory: `scenarios/analysis/data/map_route_semantic_inventory.csv` (from `build_map_route_semantic_inventory.py`).