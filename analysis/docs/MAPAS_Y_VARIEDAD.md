# Mapas y datos disponibles para variedad de escenarios

**Objetivo:** Dar variedad estructural (world_area, aspect_ratio en core 24) usando los mapas y datos en `data/` para bajar correlación y acercar a <5% pares |r|≥0.7, manteniendo cada escenario con información única para investigadores.

---

## 1. Qué hay en `data/`

| Recurso | Uso en corpus | Nota |
|--------|----------------|------|
| **HelsinkiMedium/** | Mapas y ubicaciones para WDM + Bus (Urban, Campus, Vehicles) | `roads.wkt`; subcarpetas A–H con `*_homes.wkt`, `*_offices.wkt`, `*_meetingspots.wkt`, `*_bus.wkt`. **Único dataset con todo lo necesario para WorkingDayMovement + Bus.** |
| **Manhattan/** | No usado en corpus | Solo `roads.wkt` y `bus.wkt`. **Faltan** homes, offices, meetingspots para WDM; habría que generarlos para usar Manhattan como segundo mapa urbano. |
| **cluster/** | Algunos escenarios ClusterMovement | `origin.wkt`, `ferryroute.wkt`. |
| **Raíz data/** | Varios | `roads.wkt`, `pedestrian_paths.wkt`, `main_roads.wkt`, `demo_bus.wkt`, `shops.wkt`, tram*.wkt, *POIs.wkt. No forman un dataset completo WDM equivalente a HelsinkiMedium. |

**Conclusión:** Para escenarios Urban/Campus/Vehicle (WDM+Bus) el único mapa con ubicaciones compatibles es **HelsinkiMedium**. La variedad en core 24 se consigue con **MovementModel.worldSize** (Wx, Wy): cambia **world_area** = Wx×Wy y **aspect_ratio** = min(Wx,Wy)/max(Wx,Wy). El path del mapa no es feature; solo worldSize entra en las 24 core.

---

## 2. Bloque con mismo worldSize (origen de alta correlación)

Varios escenarios compartían **worldSize = 8495, 7504** (máximo del mapa), por tanto mismo world_area y aspect_ratio:

- **01_urban:** U1, U2, U3, U11, U10  
- **03_vehicles:** V1, V3, V4, V7  

Con 9 escenarios idénticos en 2 dimensiones core (world_area, aspect_ratio), la correlación en 24D se dispara. **Estrategia:** asignar a cada uno un **worldSize distinto** (dentro del rango válido del mapa, ≤ 8495×7504) para que world_area y aspect_ratio difieran.

---

## 3. Valores worldSize asignados (variedad dentro de HelsinkiMedium)

Se mantiene el mismo mapa y rutas (HelsinkiMedium) para que la simulación siga siendo válida; solo se varía el tamaño del mundo simulado (ventana sobre el mapa). Valores elegidos para que (world_area, aspect_ratio) sean distintos:

| Escenario | worldSize anterior | worldSize nuevo | world_area (m²) | aspect_ratio |
|-----------|--------------------|-----------------|------------------|--------------|
| U1_CBD_Commuting | 8495, 7504 | 8495, 7504 (referencia) | 63.78e6 | 0.883 |
| U2_RetailHeavy | 8495, 7504 | 8000, 7000 | 56.0e6 | 0.875 |
| U3_NightlifeClusters | 8495, 7504 | 8200, 7200 | 59.04e6 | 0.878 |
| U11_OfficeWaitHeavyTail | 8495, 7504 | 7800, 6800 | 53.04e6 | 0.872 |
| U10_WorkdayLong | 8495, 7504 | 7600, 6600 | 50.16e6 | 0.868 |
| V4_MixedBusPed | 8495, 7504 | 8300, 7300 | 60.59e6 | 0.880 |
| V1_TaxiLow | 8495, 7504 | 7900, 6900 | 54.51e6 | 0.874 |
| V3_BusOnlyCarriers | 8495, 7504 | 8100, 7100 | 57.51e6 | 0.877 |
| V7_CarOwnership_100 | 8495, 7504 | 8400, 7400 | 62.16e6 | 0.881 |

Así se obtienen 9 combinaciones distintas de (world_area, aspect_ratio) en el bloque que antes era idéntico. Tras aplicar estos cambios y re-ejecutar el pipeline (features → normalize → correlation), los **pares con |r|≥0.7 en core 24** se mantienen en **200 (8,3%)**; la ganancia es que ya no hay escenarios duplicados en espacio/forma (world_area, aspect_ratio), lo que refuerza que cada escenario tenga una firma distinta para investigadores.

---

## 4. Variedad futura con más mapas

- **Manhattan:** Para usar un segundo mapa urbano (otra topología, otro aspect_ratio típico) haría falta disponer de `*_homes.wkt`, `*_offices.wkt`, `*_meetingspots.wkt` compatibles con WorkingDayMovement en `data/Manhattan/` (o adaptar el ONE a otro formato). Entonces se podrían crear escenarios “Urban_Manhattan” con worldSize adecuado al mapa.
- **HelsinkiMedium con otras rutas:** El dataset tiene varias rutas (A_bus…H_bus) y conjuntos de ubicaciones (A–H). El corpus usa sobre todo A_*. Cambiar a B_* o C_* en algunos escenarios cambiaría la **estructura de contactos** en simulación pero **no** el vector 24D (las features solo ven worldSize, no el path del routeFile). Para que eso se refleje en diversidad habría que (a) definir features que capturen la ruta, o (b) aceptar que la diversidad de comportamiento viene de la simulación y no del vector core.

Este documento se actualizará si se añaden mapas o datasets nuevos en `data/`.
