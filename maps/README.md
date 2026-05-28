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
│   └── ControlCompactGrid/      → 07_stress_controls (sintético)
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
