# Map Preparation Pipeline — Informe metodológico

## 1. Objetivo

Estandarizar los mapas del benchmark `corpus_v1` asignando **un mapa fijo y reproducible por familia**, eliminando la heterogeneidad arbitraria (mezcla de mapas Helsinki/Manhattan, free-space, etc.) que comprometía la validez comparativa entre escenarios.

## 2. Política de mapas por familia

| Familia | Mapa asignado | Fuente | Zona geográfica | worldSize (m) | Justificación |
|---------|--------------|--------|-----------------|---------------|---------------|
| 01_urban | HelsinkiDowntown | OSM | Kluuvi / Kamppi / Esplanadi, Helsinki | 2093 × 1838 | Red viaria densa urbana con transporte público; estándar histórico de The ONE |
| 02_campus | KumpulaCampus | OSM | Campus Kumpula, Universidad de Helsinki | 1524 × 1416 | Zona compacta con peatones, carriles bici y caminos internos |
| 03_vehicles | ManhattanMidtownGrid | OSM | Midtown Manhattan (34th–59th St) | 2500 × 2366 | Grid regular ideal para benchmarks vehiculares |
| 04_rural | NuuksioSparseTrails | OSM | Parque Nacional Nuuksio, Espoo | 2848 × 2945 | Red dispersa de senderos — entorno rural/wildlife |
| 05_disaster | HelsinkiDisrupted | OSM | Kalasatama / Sörnäinen (zona industrial) | 2067 × 2206 | Infraestructura portuaria e industrial — escenarios de desastre |
| 06_social | KallioCommunityCompact | OSM | Barrio Kallio, Helsinki | 1458 × 1529 | Barrio residencial denso — dinámica de comunidad |

## 3. Por qué cada familia usa un mapa distinto

Cada familia del benchmark representa un **arquetipo de movilidad DTN** con dinámicas de contacto fundamentalmente diferentes:

- **Urban** requiere calles reales con alta densidad de intersecciones para modelar congestión peatonal y vehicular.
- **Campus** necesita caminos peatonales y zonas internas (no solo carreteras) para capturar la movilidad de estudiantes.
- **Vehicles** necesita un grid regular que refleje tráfico vehicular con semáforos y carriles.
- **Rural** necesita baja densidad de caminos, grandes distancias entre nodos — reflejando zonas no urbanizadas.
- **Disaster** necesita infraestructura que pueda ser «dañada»: puertos, zonas industriales con pocas rutas alternativas.
- **Social** necesita un barrio residencial donde la proximidad física genere contactos entre vecinos.
- **Traffic** necesita un grid controlado sin sesgo geográfico para aislar el efecto del protocolo de routing.

## 4. Por qué no se mezclan mapas arbitrariamente

En versiones anteriores del corpus, algunos escenarios de la misma familia usaban mapas diferentes (e.g., unos usaban Helsinki y otros Manhattan, o directamente no usaban mapa). Esto introduce **variables confundidoras**:

- El mismo protocolo de routing muestra rendimiento diferente simplemente porque el grafo de movilidad tiene topología distinta.
- No se puede atribuir la variación de KPIs al traffic profile, al número de nodos, ni al buffer size si el mapa cambia entre escenarios de la misma familia.
- Los `worldSize` inconsistentes con el mapa real causan coordenadas fuera de rango o zonas muertas.

La política actual (mapa fijo por familia) garantiza que **la variación observada dentro de una familia se debe exclusivamente a los factores controlados** (protocolo, densidad, buffer), no al mapa.

## 5. Pipeline de reproducción

### Prerrequisitos

```bash
pip install -r scenarios/setup/requirements_maps.txt
```

### Ejecución completa

```bash
bash scenarios/setup/bootstrap_maps.sh
```

Equivale a ejecutar secuencialmente:

1. **`download_maps.sh`** — Descarga grafos de calles de OpenStreetMap via la API Overpass (usando `osmnx`) y POIs (edificios residenciales, comerciales, amenidades). Genera ficheros GraphML y GeoJSON en `scenarios/maps/raw/`.

2. **`prepare_maps.py`** — Convierte cada GraphML a WKT:
   - Reproyecta coordenadas WGS84 a metros (EPSG:3067 para Helsinki, EPSG:32618 para Manhattan).
   - Extrae el componente débilmente conexo más grande (requisito de The ONE).
   - Genera `roads.wkt` con un `LINESTRING` por arista.
   - Genera POIs (`POINT`) a partir de datos OSM reales cuando están disponibles, con fallback a generación aleatoria cerca de nodos del grafo.
   - Genera rutas de bus como `LINESTRING`.
   - Calcula `worldSize = span + 400m margen`.
   - Escribe `metadata.json` por mapa.

3. **`validate_maps.py`** — Valida cada mapa generado:
   - Conectividad del grafo (componente única).
   - Coherencia worldSize vs span real.
   - POIs dentro de los bounds del mapa.
   - Existencia de rutas de bus.
   - Cobertura espacial (longitud de vías / área de worldSize).
   - Genera `map_inventory.csv` y JSONs de validación individuales.

### Instalación en `data/`

```bash
bash scenarios/setup/bootstrap_maps.sh --install
```

Esto copia los directorios WKT finales a `data/{MapName}/` donde The ONE los puede encontrar via `MapBasedMovement.mapFile`.

### Re-descarga forzada

```bash
bash scenarios/setup/bootstrap_maps.sh --force-download
```

## 6. Métricas por mapa

| Mapa | Segmentos | Nodos | Span (m) | worldSize (m) | Cobertura (%) | Homes | Offices | Meeting |
|------|-----------|-------|----------|---------------|---------------|-------|---------|---------|
| HelsinkiDowntown | 575 | 2531 | 1693×1438 | 2093×1838 | 11.9% | 80 | 40 | 25 |
| KumpulaCampus | 4059 | 3632 | 1127×1016 | 1524×1416 | 50.7% | 30 | 20 | 15 |
| ManhattanMidtownGrid | 568 | 2116 | 2099×1966 | 2500×2366 | 12.1% | 60 | 50 | 30 |
| NuuksioSparseTrails | 326 | 965 | 2450×2544 | 2848×2945 | 5.4% | 10 | 5 | 8 |
| HelsinkiDisrupted | 8398 | 7338 | 1690×1853 | 2067×2206 | 45.5% | 40 | 25 | 15 |
| KallioCommunityCompact | 7204 | 5522 | 1103×1128 | 1458×1529 | 59.3% | 70 | 20 | 30 |
|  | 24 | 143 | 1800×1500 | 2000×1700 | 11.6% | 50 | 30 | 20 |

## 7. Diferencias: mapas reales vs sintéticos

### Mapas basados en datos reales (OSM)

**Ventajas:**
- Topología de calles realista (no todos los nodos tienen grado 4).
- Distribución heterogénea de densidad (zonas más densas, parques, agua).
- POIs basados en datos reales de edificios y amenidades.
- Mayor validez externa para resultados experimentales.

**Limitaciones:**
- Dependencia de la calidad de los datos OSM (puede haber vías faltantes o duplicadas).
- La zona elegida introduce sesgo geográfico (e.g., Helsinki ≠ una ciudad africana).
- Los datos cambian con el tiempo — la descarga no es 100% determinista (se recomienda cachear los GraphML).

### Mapas sintéticos ()

**Ventajas:**
- Controlabilidad total: topología, densidad y distribución de POIs son parámetros explícitos.
- Reproducibilidad perfecta (determinista con semilla fija).
- Ideal como baseline para aislar el efecto del protocolo de routing de la topología del mapa.
- Sin sesgo geográfico ni cultural.

**Limitaciones:**
- Baja validez ecológica: los grids regulares no reflejan patrones reales de movilidad.
- Grado uniforme de nodos (todos = 4 en un grid puro), lo que puede ocultar problemas de routing en grafos irregulares.
- No captura obstáculos naturales (agua, parques, zonas peatonales).

### Recomendación

Utilizar mapas reales como configuración primaria y el grid sintético exclusivamente como **control experimental** (familia 07_), de forma análoga a un «control negativo» en un experimento biológico.

## 8. Formato WKT para The ONE

The ONE espera ficheros de texto con geometrías WKT:

```
LINESTRING (x1 y1, x2 y2, x3 y3, ...)
```

- Coordenadas en **metros** (proyección plana, no lat/lon).
- Al cargar, The ONE aplica `mirror()` (invierte Y) y traslada el mínimo al origen (0,0).
- El grafo **debe ser conexo** o la simulación falla con `SimMap is not fully connected`.
- POIs son ficheros con `POINT (x y)`.
- Rutas de bus son `LINESTRING` con los puntos de parada en orden.

## 9. Estructura de directorios generada

```
scenarios/
├── setup/
│   ├── download_maps.sh          # Descarga datos OSM
│   ├── prepare_maps.py           # Convierte OSM → WKT
│   ├── validate_maps.py          # Validación de mapas
│   ├── bootstrap_maps.sh         # Pipeline completo
│   ├── map_config.py             # Definiciones canónicas de mapas
│   └── requirements_maps.txt     # Dependencias pip
└── maps/
    ├── raw/                      # GraphML + GeoJSON descargados (no en git)
    ├── processed/                # Grafos intermedios (no en git)
    ├── wkt/                      # WKT finales (en git)
    │   ├── HelsinkiDowntown/
    │   │   ├── roads.wkt
    │   │   ├── A_homes.wkt
    │   │   ├── A_offices.wkt
    │   │   ├── A_meetingspots.wkt
    │   │   ├── A_bus.wkt
    │   │   └── metadata.json
    │   ├── KumpulaCampus/
    │   ├── ManhattanMidtownGrid/
    │   ├── NuuksioSparseTrails/
    │   ├── HelsinkiDisrupted/
    │   ├── KallioCommunityCompact/
    │   └── /
    └── validation/               # JSONs de validación por mapa
```

## Validación geométrica extendida (2026-05)

Informes detallados de rutas bus, POIs y uso en escenarios:

- `analysis/reports/maps/bus_route_validation_report.md`
- `analysis/reports/maps/map_poi_validation_report.md`
- `analysis/reports/maps/route_usage_by_scenario_report.md`
- `analysis/reports/maps/map_assets_final_validation.md`

Scripts: `scenarios/setup/validate_bus_routes.py`, `validate_map_pois.py`, `repair_bus_routes.py`.