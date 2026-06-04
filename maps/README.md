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
│   ├── KallioCommunityCompact/  → 06_social
│   └── /      → 07_ (sintético)
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
python3 scenarios/setup/audit_route_usage.py
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --validation
python3 scenarios/setup/generate_map_final_report.py
```

Política de nombres: `analysis/reports/maps/route_semantic_policy.md`.

Salidas: `analysis/data/map_route_semantic_inventory.csv`, `family_route_generation_summary.csv`, `bus_route_validation.csv`, `map_poi_validation.csv`, informes en `analysis/reports/maps/`.

**Nota:** Los ficheros de ruta son paradas de `routeFile`, no calles. The ONE calcula el movimiento entre paradas sobre `roads.wkt`. Las figuras muestran path resuelto (sólido) y orden de paradas (punteado).

## HelsinkiDowntown (01_urban) — paper-ready

Mapa cerrado para el paper. Pipeline dedicado:

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_helsinki_downtown.py --dry-run
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_helsinki_downtown.py --apply --install
```

Salidas: `analysis/data/maps/HelsinkiDowntown_*.csv`, informes `analysis/reports/maps/HelsinkiDowntown_*.md`, figuras `analysis/figures/paper/maps/HelsinkiDowntown_paper_ready.png`.

Decisión final: `analysis/reports/maps/HelsinkiDowntown_final_decision.md`. Wiki: `.wiki-clone/09-Urban-Family.md`.

## KumpulaCampus (02_campus) — paper-ready

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_kumpula_campus.py --apply --install
```

Salidas: `analysis/data/maps/KumpulaCampus_*.csv`, `analysis/reports/maps/KumpulaCampus_final_decision.md`, figura paper en `analysis/figures/paper/maps/KumpulaCampus_paper_ready.png`.

Wiki: `.wiki-clone/10-Campus-Family.md`. C4 renombrado a `CampusEvent_IngressEgress`.

## ManhattanMidtownGrid (03_vehicles) — paper-ready

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_manhattan_midtown.py --apply --install
```

Salidas: `analysis/data/maps/ManhattanMidtownGrid_*.csv`, `analysis/reports/maps/ManhattanMidtownGrid_final_decision.md`, figura paper en `analysis/figures/paper/maps/ManhattanMidtownGrid_paper_ready.png`.

Wiki: `.wiki-clone/11-Vehicles-Family.md`. Rutas `A_vehicle_route` / `B_vehicle_route`; sin `A_bus.wkt` en settings.

## NuuksioSparseTrails (04_rural) — paper-ready

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_nuuksio_sparse_trails.py --apply --install
```

Salidas: `analysis/data/maps/NuuksioSparseTrails_*.csv`, `analysis/reports/maps/NuuksioSparseTrails_final_decision.md`, figura paper en `analysis/figures/paper/maps/NuuksioSparseTrails_paper_ready.png`.

Wiki: `.wiki-clone/12-Rural-Family.md`. Patrulla `A_ranger_patrol`; R1 renombrado a `R1_Rural_SparseSPMM`.

## HelsinkiDisrupted (05_disaster) — paper-ready

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_helsinki_disrupted.py --apply --install
```

Salidas: `analysis/data/maps/HelsinkiDisrupted_*.csv`, `analysis/reports/maps/HelsinkiDisrupted_final_decision.md`, figura paper en `analysis/figures/paper/maps/HelsinkiDisrupted_paper_ready.png`.

Wiki: `.wiki-clone/13-Disaster-Family.md`. Rutas `A_emergency_route` / `B_mule_route`; D5 Group1 → SPMM.

## KallioCommunityCompact (06_social) — paper-ready

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_kallio_community_compact.py --apply --install
```

Salidas: `analysis/data/maps/KallioCommunityCompact_*.csv`, `analysis/reports/maps/KallioCommunityCompact_final_decision.md`, figura paper en `analysis/figures/paper/maps/KallioCommunityCompact_paper_ready.png`.

Wiki: `.wiki-clone/14-Social-Family.md`. Rutas `A_community_route` / `B_community_route` (assets opcionales); S1/S6 map-aware routes.