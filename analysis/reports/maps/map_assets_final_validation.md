# Map assets — final validation

Generated: 2026-06-04 15:03 UTC

## Executive summary

- **Maps inventoried:** 6
- **Bus routes validated:** 11 (2 PASS, 9 WARNING, 0 FAIL)
- **POI files validated:** 18 (6 PASS, 7 WARNING, 5 FAIL)

Auxiliary route WKT files are **routeFile waypoints** for `MapRouteMovement`. The ONE routes carriers on the **road graph** between stops (Dijkstra). Wiki figures show a **solid resolved path** and a faint dotted stop-order reference.

Routes were **regenerated per family** (2026-05-28) with semantic filenames, graph-coherent waypoints, and backups under `_backup_semantic_regen_*` / `_backup_route_rename_*`. Settings `routeFile` paths were updated only where already referenced.

## Maps inventory

| Map | Family | Source | Bus files | POI counts (H/O/M) | Status |
|-----|--------|--------|-----------|-------------------|--------|
| HelsinkiDowntown | 01_urban | osm | 3 | 80/40/25 | PASS |
| KumpulaCampus | 02_campus | osm | 1 | 30/20/15 | PASS |
| ManhattanMidtownGrid | 03_vehicles | osm | 2 | 60/50/30 | PASS |
| NuuksioSparseTrails | 04_rural | osm | 1 | 10/5/8 | PASS |
| HelsinkiDisrupted | 05_disaster | osm | 2 | 40/25/15 | PASS |
| KallioCommunityCompact | 06_social | osm | 2 | 70/20/30 | PASS |

## Semantic route inventory

| Map | Current | Recommended | Label | In settings | Action |
|-----|---------|-------------|-------|-------------|--------|
| HelsinkiDowntown | A_bus.wkt | A_bus.wkt | urban_bus | 182 | regenerate_only |
| HelsinkiDowntown | B_bus.wkt | B_bus.wkt | urban_bus | 0 | optional_asset |
| HelsinkiDowntown | C_bus.wkt | C_bus.wkt | urban_bus | 0 | optional_asset |
| KumpulaCampus | A_bus.wkt | A_campus_shuttle.wkt | campus_shuttle | 0 | optional_asset |
| ManhattanMidtownGrid | A_bus.wkt | A_vehicle_route.wkt | vehicle_route | 91 | rename_and_regenerate |
| ManhattanMidtownGrid | B_bus.wkt | B_vehicle_route.wkt | vehicle_route | 13 | rename_and_regenerate |
| NuuksioSparseTrails | A_bus.wkt | A_ranger_patrol.wkt | ranger_patrol | 13 | rename_and_regenerate |
| HelsinkiDisrupted | A_bus.wkt | A_emergency_route.wkt | emergency_route | 13 | rename_and_regenerate |
| HelsinkiDisrupted | B_bus.wkt | B_mule_route.wkt | mule_route | 0 | optional_asset |
| KallioCommunityCompact | A_bus.wkt | A_community_route.wkt | community_route | 0 | optional_asset |
| KallioCommunityCompact | B_bus.wkt | B_community_route.wkt | community_route | 0 | optional_asset |

## Route files (geometry)

| Map | Route | Status | Max dist (m) | Notes |
|-----|-------|--------|--------------|-------|
| HelsinkiDowntown | A_bus.wkt | WARNING | 64.42 |  |
| HelsinkiDowntown | B_bus.wkt | WARNING | 64.42 |  |
| HelsinkiDowntown | C_bus.wkt | WARNING | 64.42 |  |
| KumpulaCampus | A_campus_shuttle.wkt | WARNING | 90.5 |  |
| ManhattanMidtownGrid | A_vehicle_route.wkt | WARNING | 146.45 |  |
| ManhattanMidtownGrid | B_vehicle_route.wkt | PASS | 46.66 |  |
| NuuksioSparseTrails | A_ranger_patrol.wkt | PASS | 116.71 |  |
| HelsinkiDisrupted | A_emergency_route.wkt | WARNING | 97.53 |  |
| HelsinkiDisrupted | B_mule_route.wkt | WARNING | 97.53 |  |
| KallioCommunityCompact | A_community_route.wkt | WARNING | 61.81 |  |
| KallioCommunityCompact | B_community_route.wkt | WARNING | 55.22 |  |

## POIs

| Map | File | Status | Inside WS % | Max dist (m) | Notes |
|-----|------|--------|-------------|--------------|-------|
| HelsinkiDowntown | A_homes.wkt | PASS | 100.0 | 13.72 |  |
| HelsinkiDowntown | A_offices.wkt | FAIL | 100.0 | 121.36 | 14 POIs >50.0m from road |
| HelsinkiDowntown | A_meetingspots.wkt | FAIL | 100.0 | 131.68 | 10 POIs >50.0m from road |
| KumpulaCampus | A_homes.wkt | PASS | 100.0 | 31.11 |  |
| KumpulaCampus | A_offices.wkt | PASS | 100.0 | 38.05 |  |
| KumpulaCampus | A_meetingspots.wkt | PASS | 100.0 | 36.8 |  |
| ManhattanMidtownGrid | A_homes.wkt | PASS | 100.0 | 20.76 |  |
| ManhattanMidtownGrid | A_offices.wkt | WARNING | 100.0 | 130.16 | 4 POIs >50.0m from road |
| ManhattanMidtownGrid | A_meetingspots.wkt | WARNING | 100.0 | 80.94 | 3 POIs >50.0m from road |
| NuuksioSparseTrails | A_homes.wkt | PASS | 100.0 | 19.55 |  |
| NuuksioSparseTrails | A_offices.wkt | FAIL | 100.0 | 619.57 | 3 POIs >150.0m from road |
| NuuksioSparseTrails | A_meetingspots.wkt | FAIL | 100.0 | 280.6 | 3 POIs >150.0m from road |
| HelsinkiDisrupted | A_homes.wkt | WARNING | 100.0 | 62.16 | 3 POIs >50.0m from road |
| HelsinkiDisrupted | A_offices.wkt | WARNING | 100.0 | 50.53 | 1 POIs >50.0m from road |
| HelsinkiDisrupted | A_meetingspots.wkt | FAIL | 100.0 | 306.02 | 5 POIs >50.0m from road |
| KallioCommunityCompact | A_homes.wkt | WARNING | 100.0 | 55.84 | 1 POIs >50.0m from road |
| KallioCommunityCompact | A_offices.wkt | WARNING | 100.0 | 117.24 | 1 POIs >50.0m from road |
| KallioCommunityCompact | A_meetingspots.wkt | WARNING | 100.0 | 97.62 | 2 POIs >50.0m from road |

## POI exceptions

- `HelsinkiDowntown/A_offices.wkt`: 14 POIs >50.0m from road
- `HelsinkiDowntown/A_meetingspots.wkt`: 10 POIs >50.0m from road
- `NuuksioSparseTrails/A_offices.wkt`: 3 POIs >150.0m from road
- `NuuksioSparseTrails/A_meetingspots.wkt`: 3 POIs >150.0m from road
- `HelsinkiDisrupted/A_meetingspots.wkt`: 5 POIs >50.0m from road

## Known limitations

- Some OSM-derived office/meeting POIs remain >50 m from the nearest road segment (WorkingDayMovement still uses them; see POI table). Rural Nuuksio offices are sparse by design.
- Orphan bus files (e.g. `B_bus.wkt` on maps without `.settings` references) are kept for package consistency.
- Re-simulation recommended for scenarios using repaired routes (urban, vehicles, R4, D5).

## Reproduction commands

```bash
python3 scenarios/setup/build_map_route_semantic_inventory.py
python3 scenarios/setup/regenerate_family_routes.py --all --dry-run
python3 scenarios/setup/regenerate_family_routes.py --all --apply --install
python3 scenarios/setup/rename_route_files_semantic.py --apply
python3 scenarios/setup/build_map_assets_inventory.py --include-data
python3 scenarios/setup/validate_maps.py
python3 scenarios/setup/validate_bus_routes.py
python3 scenarios/setup/validate_map_pois.py
python3 scenarios/setup/build_map_route_semantic_inventory.py
python3 scenarios/setup/repair_bus_routes.py --dry-run
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --validation
```

## Paper-ready statement

The benchmark assigns **one fixed map per environmental scenario family** (six OSM extracts in Helsinki and Midtown Manhattan). Street geometry is imported from OpenStreetMap, reprojected to metric coordinates, reduced to the largest connected component, and exported as WKT for The ONE. Auxiliary route files use **semantic names** per family (urban bus, vehicle route, ranger patrol, etc.). Waypoints sit on the road network; carriers follow shortest paths on the graph between stops. POI and route assets are checked against `worldSize` and road proximity before inclusion.
