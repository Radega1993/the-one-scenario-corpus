# Mapas del benchmark — The ONE Simulator

Este directorio contiene los mapas WKT generados por el pipeline automatizado para el corpus `corpus_v1`.

## Estructura

```
maps/
├── raw/           # GraphML + GeoJSON descargados de OSM (no en git, regenerables)
├── processed/     # Grafos intermedios (no en git, regenerables)
├── wkt/           # WKT finales — roads, POIs, bus routes (en git)
│   ├── HelsinkiDowntown/        → 01_urban
│   ├── KumpulaCampus/           → 02_campus
│   ├── ManhattanMidtownGrid/    → 03_vehicles
│   ├── NuuksioSparseTrails/     → 04_rural
│   ├── HelsinkiDisrupted/       → 05_disaster
│   └── KallioCommunityCompact/  → 06_social
└── validation/    # JSONs de validación por mapa
```

## Regenerar desde cero

```bash
pip install -r scenarios/setup/requirements_maps.txt
bash scenarios/setup/bootstrap_maps.sh
```

Esto descarga datos de OpenStreetMap, los convierte a WKT (con reproyección a metros y extracción del componente conexo) y valida conectividad, POIs y worldSize.

## Instalar en data/

```bash
bash scenarios/setup/bootstrap_maps.sh --install
```

Copia los directorios WKT a `data/{MapName}/` donde The ONE los referencia via `MapBasedMovement.mapFile`.

## Formato WKT

The ONE espera:
- **roads.wkt**: `LINESTRING (x1 y1, x2 y2, ...)` — coordenadas en metros, grafo conexo
- **A_homes.wkt**, **A_offices.wkt**, **A_meetingspots.wkt**: `POINT (x y)`
- **A_bus.wkt**: `LINESTRING (x1 y1, x2 y2, ...)` — ruta de bus

## Informe metodológico

Ver `analysis/reports/map_preparation_pipeline.md` para la justificación de la política de mapas, métricas por mapa y diferencias entre mapas reales y sintéticos.

## Inventario

Ver `analysis/data/map_inventory.csv` para el resumen cuantitativo (segmentos, nodos, worldSize, cobertura, POIs).

## worldSize calibrado (2026-05)

Fórmula: `ceil(max_road_sim) + occupancy_margin_m` por eje (origen en 0,0). Tabla canónica: `analysis/data/world_size_calibration.csv`.

| Mapa | worldSize (m) | margin (m) |
|------|---------------|------------|
| HelsinkiDowntown | 1713 × 1459 | 20 |
| KumpulaCampus | 1148 × 1036 | 20 |
| ManhattanMidtownGrid | 2120 × 1986 | 20 |
| NuuksioSparseTrails | 2470 × 2565 | 20 |
| HelsinkiDisrupted | 1711 × 1874 | 20 |
| KallioCommunityCompact | 1124 × 1149 | 20 |

Recalibrar y propagar a `.settings`:

```bash
python3 scenarios/setup/calibrate_world_size_per_map.py --apply
python3 scenarios/setup/migrate_corpus_maps.py --world-size-only
python3 scenarios/setup/audit_world_size_settings.py
```

## Validación de rutas semánticas y POIs

```bash
python3 scenarios/setup/build_map_route_semantic_inventory.py
python3 scenarios/setup/regenerate_family_routes.py --all --dry-run
python3 scenarios/setup/regenerate_family_routes.py --all --apply --install
python3 scenarios/setup/rename_route_files_semantic.py --apply
python3 scenarios/setup/build_map_assets_inventory.py --include-data
python3 scenarios/setup/validate_maps.py
python3 scenarios/setup/validate_bus_routes.py
python3 scenarios/setup/validate_map_pois.py
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --validation
```

Política de nombres: `analysis/reports/maps/route_semantic_policy.md`.

Salidas: `analysis/data/map_route_semantic_inventory.csv`, `family_route_generation_summary.csv`, `bus_route_validation.csv`, `map_poi_validation.csv`. Validación consolidada: `analysis/reports/maps/map_assets_final_validation.md`.

**Nota:** Los ficheros de ruta son paradas de `routeFile`, no calles. The ONE calcula el movimiento entre paradas sobre `roads.wkt`. Las figuras muestran path resuelto (sólido) y orden de paradas (punteado).

## Regenerar rutas por mapa (solo si cambian POIs o política de rutas)

Los mapas en git ya están listos para simular con `bootstrap_maps.sh --install`. Si modificas rutas de bus/vehículo/comunidad bajo `wkt/`:

```bash
python3 scenarios/setup/regenerate_family_routes.py --map HelsinkiDowntown --dry-run
python3 scenarios/setup/regenerate_family_routes.py --map HelsinkiDowntown --apply --install
```

Repite con `--map` `KumpulaCampus`, `ManhattanMidtownGrid`, `NuuksioSparseTrails`, `HelsinkiDisrupted`, o `KallioCommunityCompact`. Wiki por familia: `.wiki-clone/09-Urban-Family.md` … `14-Social-Family.md`.

## Rutas auxiliares por escenario (R2 / S1 / S6)

22 ficheros `routeFile` específicos de escenario (no rutas de familia). Generación acotada — no toca `roads.wkt` ni `A_*` semánticos:

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/generate_scenario_aux_routes.py --dry-run
scenarios/analysis/.venv/bin/python scenarios/setup/generate_scenario_aux_routes.py --apply --install
```

Ficheros: `NuuksioSparseTrails/R2_village_{1,2,3}.wkt`, `R2_inter_village.wkt`; `KallioCommunityCompact/S1_community_{1..4}.wkt`, `S1_bridge_route.wkt`; `S6_family_{1..12}.wkt`, `S6_shared_civic.wkt`.