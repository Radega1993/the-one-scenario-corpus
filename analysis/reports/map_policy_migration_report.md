# Informe de migración de mapas — corpus_v1

> **2026-05 update:** Geometric validation and bus-route repair:
> [`analysis/reports/maps/map_assets_final_validation.md`](maps/map_assets_final_validation.md).

## 1. Resumen ejecutivo

Se han migrado los **720 ficheros `.settings`** del corpus v2 para que cada una de las 7 familias ambientales use un mapa fijo, reproducible y metodológicamente coherente. Esto elimina la heterogeneidad arbitraria donde escenarios de la misma familia usaban mapas distintos (Helsinki y Manhattan mezclados), o directamente no usaban mapa (free-space).

**Resultado:** 720/720 ficheros migrados y validados correctamente.

| Métrica | Valor |
|---------|-------|
| Ficheros migrados | 720 |
| Ficheros renombrados | 168 |
| Modelos de movimiento convertidos | 504 (RandomWaypoint/LinearMovement -> ShortestPathMapBasedMovement) |
| ClusterCenter recalculados | 72 ficheros |
| Validación post-migración | 720/720 PASS |

## 2. Política de mapas por familia

| Familia | Mapa asignado | worldSize (m) | Fuente | Escenarios | Ficheros |
|---------|---------------|---------------|--------|------------|----------|
| 01_urban | HelsinkiDowntown | 2093 x 1838 | OSM (Helsinki centro) | 7 | 84 |
| 02_campus | KumpulaCampus | 1524 x 1416 | OSM (Campus Kumpula) | 6 | 72 |
| 03_vehicles | ManhattanMidtownGrid | 2500 x 2366 | OSM (Midtown Manhattan) | 5 | 60 |
| 04_rural | NuuksioSparseTrails | 2848 x 2945 | OSM (Parque Nuuksio) | 12 | 144 |
| 05_disaster | HelsinkiDisrupted | 2067 x 2206 | OSM (Kalasatama industrial) | 9 | 108 |
| 06_social | KallioCommunityCompact | 1458 x 1529 | OSM (Barrio Kallio) | 6 | 72 |

## 3. Justificación: por qué cada familia usa un mapa distinto

Cada familia del benchmark representa un arquetipo de movilidad DTN fundamentalmente diferente:

- **01_urban (HelsinkiDowntown):** Red viaria urbana densa con transporte público. Los escenarios WorkingDayMovement necesitan calles reales con alta densidad de intersecciones para modelar congestión peatonal y vehicular. Helsinki Downtown es el estándar histórico de The ONE.

- **02_campus (KumpulaCampus):** Zona compacta con caminos peatonales y accesos internos. La movilidad de estudiantes necesita un área pequeña y densa, no una ciudad entera.

- **03_vehicles (ManhattanMidtownGrid):** Grid regular ideal para benchmarks vehiculares. Las rutas de taxi y bus necesitan intersecciones predecibles y carriles definidos.

- **04_rural (NuuksioSparseTrails):** Red dispersa de senderos forestales. La baja densidad de caminos y las grandes distancias entre nodos reflejan escenarios rurales/wildlife reales.

- **05_disaster (HelsinkiDisrupted):** Infraestructura portuaria e industrial con pocas rutas alternativas. Ideal para modelar escenarios donde la infraestructura está dañada o es limitada.

- **06_social (KallioCommunityCompact):** Barrio residencial denso. La proximidad física entre vecinos genera patrones de contacto realistas para escenarios sociales/comunitarios.

- **07_ ():** Grid sintético controlado sin sesgo geográfico. Funciona como baseline experimental, análogo a un grupo control en un experimento.

## 4. Por qué ya no se mezclan mapas arbitrariamente

En la versión anterior del corpus, existían problemas metodológicos graves:

1. **Variable confundidora:** Dentro de 01_urban, 5 escenarios usaban HelsinkiMedium (8295x7304m) y 2 usaban Manhattan (6038x5608m). La diferencia de topología, densidad de calles y tamaño de mundo introducía variación no controlada que se confundía con el efecto de los levers del escenario.

2. **Inconsistencia de worldSize:** Incluso dentro de la misma familia, los worldSize variaban significativamente (ej: 07_ iba de 3800x3000 a 7200x5600). Esto hace que la densidad de nodos por unidad de área sea diferente entre escenarios de la misma familia, invalidando comparaciones directas.

3. **Ausencia de mapas:** 43 de 60 escenarios base no usaban mapa alguno (free-space). El modelo RandomWaypoint no confina nodos a calles, lo que produce dinámicas de contacto fundamentalmente diferentes a las de un entorno real.

**Solución aplicada:** Un mapa fijo por familia garantiza que la variación observada se debe exclusivamente a los factores controlados (protocolo de routing, traffic profile, parámetros del escenario), no al mapa ni al worldSize.

## 5. Cambios aplicados

### 5.1 Actualización de mapas y worldSize

Todos los ficheros ahora apuntan a `data/{MapName}/roads.wkt` con el worldSize correcto del mapa generado por el pipeline OSM-to-WKT.

### 5.2 Conversión de modelos de movimiento

504 ficheros convertidos de free-space a map-based:

| Modelo original | Modelo nuevo | Ficheros afectados |
|----------------|-------------|-------------------|
| RandomWaypoint | ShortestPathMapBasedMovement | 492 |
| LinearMovement | ShortestPathMapBasedMovement | 12 |
| ClusterMovement | ClusterMovement (mantenido) | — |
| WorkingDayMovement | WorkingDayMovement (mantenido) | — |
| MapRouteMovement | MapRouteMovement (mantenido) | — |
| BusMovement | BusMovement (mantenido) | — |

**ShortestPathMapBasedMovement** mueve nodos entre puntos aleatorios del grafo de calles siguiendo el camino más corto, en lugar de moverse en línea recta como RandomWaypoint. Esto confina la movilidad a las calles del mapa.

### 5.3 Recalculo de ClusterMovement

72 ficheros con ClusterMovement (familias 04_rural, 05_disaster, 06_social) tuvieron sus `clusterCenter` y `clusterRange` recalculados proporcionalmente al nuevo worldSize:

```
ratio_x = nuevo_worldSize_x / viejo_worldSize_x
ratio_y = nuevo_worldSize_y / viejo_worldSize_y
nuevo_center = (viejo_center_x * ratio_x, viejo_center_y * ratio_y)
nuevo_range  = viejo_range * promedio(ratio_x, ratio_y)
```

Ejemplo (S1_StrongCommunities, worldSize 8000x6000 -> 1458x1529):
- Cluster A: (1200,1200) -> (219,306), range 200 -> 44
- Cluster B: (6800,1200) -> (1239,306), range 200 -> 44

### 5.4 Renombrado de ficheros

168 ficheros que contenían el nombre del mapa antiguo en su nombre fueron renombrados:
- `*_HelsinkiMedium_*` -> `*_HelsinkiDowntown_*` (01_urban), `*_ManhattanMidtownGrid_*` (03_vehicles), `*_NuuksioSparseTrails_*` (04_rural), `*_HelsinkiDisrupted_*` (05_disaster)
- `*_Manhattan_*` -> `*_HelsinkiDowntown_*` (01_urban)

### 5.5 Actualización de rutas de datos

Todas las referencias a ficheros de datos actualizadas:
- `data/HelsinkiMedium/roads.wkt` -> `data/{MapName}/roads.wkt`
- `data/HelsinkiMedium/A_bus.wkt` -> `data/{MapName}/A_bus.wkt`
- `data/Manhattan/bus.wkt` -> `data/{MapName}/A_bus.wkt` (formato normalizado)
- `data/*/A_homes.wkt`, `A_offices.wkt`, `A_meetingspots.wkt` -> rutas del mapa de la familia

## 6. Mapas reales vs sintéticos

### Mapas reales (OSM)

**Ventajas:**
- Topología de calles realista (grados de nodo heterogéneos)
- POIs basados en datos reales de OpenStreetMap
- Mayor validez externa para resultados experimentales

**Limitaciones:**
- Sesgo geográfico (Helsinki != una ciudad africana o asiática)
- Los datos OSM varían con el tiempo
- La calidad depende de la cobertura de la zona en OSM

### Mapa sintético ()

**Ventajas:**
- Controlabilidad total: grid regular sin sesgo geográfico
- Reproducibilidad perfecta (determinista)
- Ideal como baseline para aislar el efecto del protocolo

**Limitaciones:**
- Baja validez ecológica (grids regulares no existen en la realidad)
- Grado uniforme de nodos (todos = 4)
- No captura obstáculos naturales

## 7. Impacto en la simulación

**IMPORTANTE:** Esta migración invalida todos los resultados de simulación anteriores. Es necesario re-simular los 720 escenarios del corpus completo porque:

1. Los worldSize han cambiado, alterando la densidad de nodos
2. Los modelos de movimiento han cambiado (free-space -> map-based)
3. Las rutas de bus y POIs son diferentes
4. Los ClusterCenter están en posiciones diferentes

## 8. Backup y reversibilidad

Los ficheros originales se conservan en:
```
scenarios/corpus_v1/_backup_pre_migration/
```

Para revertir la migración:
```bash
cd scenarios/corpus_v1
for fam in 01_urban 02_campus 03_vehicles 04_rural 05_disaster 06_social 07_; do
  rm -f "$fam"/*.settings
  cp _backup_pre_migration/"$fam"/*.settings "$fam"/
done
```

## 9. Validación

- **map_policy_validation.csv**: 720 rows, todas con `validation_status = OK`
- **Post-validación**: 0 ficheros con rutas rotas, 0 con clusterCenter fuera de bounds, 0 con referencias huérfanas
- **Mapas instalados**: 7 directorios en `data/` con roads.wkt, POIs y bus routes validados

## 10. Ficheros generados/modificados

| Fichero | Acción |
|---------|--------|
| `scenarios/setup/migrate_corpus_maps.py` | Script de migración (creado) |
| `scenarios/analysis/data/map_policy_validation.csv` | Validación de 720 ficheros (creado) |
| `scenarios/analysis/reports/map_policy_migration_report.md` | Este informe (creado) |
| `scenarios/corpus_v1/_backup_pre_migration/` | Backup de 720 ficheros originales (creado) |
| `data/{7 mapas}/` | WKT maps instalados (copiados) |
| 720 ficheros `.settings` | Migrados (modificados + 168 renombrados) |