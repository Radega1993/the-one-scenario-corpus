# Ocupación espacial en The ONE

Este documento describe qué mide la **ocupación espacial** en las simulaciones, cómo se relaciona con otros informes ya existentes y cómo enlazarla con el análisis de **tiempo útil** y conectividad.

## Definición

**Ocupación espacial** (en esta implementación) es el conteo de **visitas a celdas** de una rejilla fija sobre el rectángulo del mundo (`MovementModel.worldSize`), muestreadas a intervalos regulares durante la simulación (post–warmup). La **cobertura** es la fracción de celdas distintas que han recibido al menos una visita hasta un instante (o hasta el final de un bin temporal).

Esto es un proxy de **exploración del espacio de movimiento**, no de calidad de rutas ni de entrega de mensajes.

## Auditoría de informes existentes

| Informe | Qué exporta | ¿Suficiente para rejilla / heatmaps temporales? |
|--------|-------------|-----------------------------------------------|
| `LocationSnapshotReport` | Snapshots periódicos: tiempo y líneas `host x y` (no CSV tabular único por evento). | No agrega rejilla ni serie de cobertura acumulada. Útil como vista ligera de posiciones. |
| `MessageLocationReport` | Ubicaciones ligadas a **mensajes**, no trayectorias completas de nodos. | No para mapas de densidad de nodos. |
| `NodeDensityReport` / `RadiusOfGyrationReport` | Estadísticas agregadas en instantes o resúmenes. | No exportan serie temporal celda a celda para heatmaps. |
| `ConnectivityONEReport` | Eventos de conexión/desconexión para líneas temporales de conectividad. | Mide **topología de contactos**, no ocupación geográfica. Ver `lib/connectivity_timeline.py`. |

Por eso se añaden **`NodePositionReport`** (serie `time,node_id,x,y`) y **`SpatialOccupancyReport`** (tres CSV: rejilla de visitas, serie temporal de cobertura, resumen con umbrales).

## Configuración (namespace de settings)

The ONE resuelve claves de informes como **`NombreClaseSimple.setting`** (y secundario `Report`), por ejemplo:

- `SpatialOccupancyReport.gridSize`
- `NodePositionReport.positionSampleInterval`

No uses `Report.report8.gridSize`; no se resuelve en el `Settings` del informe.

## Métricas de cobertura (denominadores)

| Columna CSV | Denominador | Uso |
|-------------|-------------|-----|
| `coverage_world_pct` / `final_coverage_pct` | `gridSize²` sobre `worldSize` (Java) | Transparencia / comparación con informe |
| `coverage_map_bbox_pct` | Celdas con centro dentro del bbox de `roads.wkt` | Sin márgenes blancos del panel |
| **`coverage_road_cells_pct`** | Celdas que intersectan la red rasterizada | **Métrica principal (paper)** |
| `coverage_road_buffer_{10,15,25}m_pct` | Red + buffer morfológico | Sensibilidad (material suplementario) |

Definición de celda visitada: `visit_count > 0` en la rejilla final. Implementación: `lib/spatial_coverage.py`. Validación campus: [spatial_occupancy_denominator_validation.md](spatial_occupancy_denominator_validation.md).

## Interpretar cobertura baja (mapa “casi vacío”)

`coverage_world_pct` es la fracción de celdas del rectángulo **`MovementModel.worldSize`** visitadas al menos una vez. En escenarios **WorkingDayMovement**, los nodos siguen rutas y POIs: **no recorren todo el rectángulo**. Valores del orden de **5–15%** pueden ser normales; no indican por sí solos un fallo.

**Importante:** un **world % bajo no implica un mapa mal usado**. En campus, `coverage_world_pct` ~40% puede coexistir con **`coverage_road_cells_pct` ~90%** (C1). Usa la métrica de red para comparar familias; reserva world % para transparencia.

Los heatmaps (por defecto, `--zoom-mode roads`):

1. **Mundo completo** — `worldSize` + calles WKT (+ underlay opcional). Título multi-métrica: `world X% · map bbox Y% · road cells Z% · buffer25 …`.
2. **Zoom** — bbox de celdas `road_cell` (o `visited` / `map_bbox` según flag).

## Capas de mapa en los heatmaps (`analyze_spatial_occupancy.py`)

| Capa | Origen | Alineación |
|------|--------|------------|
| Calles | `data/HelsinkiMedium/roads.wkt` o `data/Manhattan/roads.wkt` | Misma transformación que `MapBasedMovement.readMap()`: espejo en Y, traslación al origen (coordenadas de simulación). Implementación: `lib/map_context.py`. |
| Raster (opcional) | `GUI.UnderlayImage.fileName` del `.settings` (p. ej. `data/helsinki_underlay.png`) | Estirado a `[0, world_x] × [0, world_y]` (aproximación a la GUI; la GUI aplica además offset/scale/rotate en píxeles). El PNG puede no estar versionado en git. |
| Ocupación | `*_spatial_occupancy_grid.csv` | `imshow` en metros, escala **log**, ceros transparentes. |

El dataset se infiere del `.settings` (`MapBasedMovement.mapFile1`, rutas `Group.*LocationsFile`, o nombre `*HelsinkiMedium*` / `*Manhattan*`).

Opciones CLI: `--zoom-mode visited|map_bbox|roads` (default `roads`), `--heatmap-layout dual|full|zoom`, `--heatmap-linear`, `--heatmap-no-roads`, `--heatmap-no-underlay`, `--primary-metric coverage_road_cells_pct`.

## Limitaciones

- Mundo **2D plano**; la rejilla no modela obstáculos ni costes de terreno.
- Coordenadas fuera del rectángulo del mundo se **clamp**ean al borde (robustez frente a modelos raros).
- **Resolución** (`gridSize`): más celdas implican más memoria y CSV más grandes.
- La métrica no distingue “obstáculo” vs “celda vacía”: solo visitas muestreadas.
- **Cobertura global** no mide “porcentaje de calles visitadas”, solo del rectángulo de rejilla completo.

## Relación con tiempo útil y conectividad

- **Cobertura espacial** resume cuánto del área de movimiento “ve” la población de nodos a lo largo del tiempo (exploración espacial).
- **Conectividad** (`ConnectivityONEReport`, `lib/connectivity_timeline.py`) resume **oportunidades de reenvío** por contactos, no dónde se ha estado en el mapa.
- **Tiempo útil** ([`useful_simulation_time_report.md`](useful_simulation_time_report.md)) combina ventanas de actividad de conectividad; puede leerse junto con la cobertura espacial como dos vistas complementarias (espacio vs enlaces).

## Artefactos generados

Tras simular con el overlay adecuado (ver `README.md` en `scenarios/analysis/`):

- `{scenario}_NodePositionReport.csv` (si se configura `output` o nombre por defecto del informe).
- `{scenario}_spatial_occupancy_grid.csv`, `{scenario}_spatial_coverage_timeseries.csv`, `{scenario}_spatial_occupancy_summary.csv`.

El script `analyze_spatial_occupancy.py` (`lib/spatial_occupancy_io.py`, `lib/map_context.py`) agrega métricas y figuras bajo `data/` y `figures/spatial_heatmaps/`, y puede escribir un resumen en `reports/spatial_occupancy_analysis_summary.md`.
