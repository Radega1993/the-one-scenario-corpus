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

## Interpretar cobertura baja (mapa “casi vacío”)

`final_coverage_pct` es la fracción de celdas del rectángulo **`MovementModel.worldSize`** visitadas al menos una vez. En escenarios **WorkingDayMovement** sobre `data/HelsinkiMedium` o `data/Manhattan`, los nodos siguen rutas y POIs: **no recorren todo el rectángulo** del mundo. Valores del orden de **5–15%** pueden ser normales; no indican por sí solos un fallo de simulación.

Los heatmaps muestran dos paneles (por defecto):

1. **Mundo completo** — `worldSize` con calles WKT y, si existe, PNG de fondo.
2. **Zoom** — solo el bbox de celdas con `visit_count > 0` (escala log para ver detalle).

## Capas de mapa en los heatmaps (`analyze_spatial_occupancy.py`)

| Capa | Origen | Alineación |
|------|--------|------------|
| Calles | `data/HelsinkiMedium/roads.wkt` o `data/Manhattan/roads.wkt` | Misma transformación que `MapBasedMovement.readMap()`: espejo en Y, traslación al origen (coordenadas de simulación). Implementación: `lib/map_context.py`. |
| Raster (opcional) | `GUI.UnderlayImage.fileName` del `.settings` (p. ej. `data/helsinki_underlay.png`) | Estirado a `[0, world_x] × [0, world_y]` (aproximación a la GUI; la GUI aplica además offset/scale/rotate en píxeles). El PNG puede no estar versionado en git. |
| Ocupación | `*_spatial_occupancy_grid.csv` | `imshow` en metros, escala **log**, ceros transparentes. |

El dataset se infiere del `.settings` (`MapBasedMovement.mapFile1`, rutas `Group.*LocationsFile`, o nombre `*HelsinkiMedium*` / `*Manhattan*`).

Opciones CLI: `--heatmap-layout dual|full|zoom`, `--heatmap-linear`, `--heatmap-no-roads`, `--heatmap-no-underlay`.

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
