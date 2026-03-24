# Core vs extended features — freeze final (core 23)

**Estado:** versión vigente para documentación pública y paper.  
**Referencia canónica:** `analysis/reports/RESULTADOS_ACTUALES.md`.

## 1) Criterio de diseño

Se mantiene una separación metodológica:

- **Core 23**: conjunto principal para diversidad y narrativa del paper.
- **Extended 46**: cobertura completa para exploración, dashboard y material suplementario.

Regla de inclusión en core:

1. aporta dimensión estructural del escenario (no solo detalle de implementación),
2. es interpretable para revisión científica,
3. evita redundancia fuerte dentro del núcleo,
4. mantiene cobertura corpus-wide (sin sesgo excesivo a una sola familia).

## 2) Lista core vigente (23)

`world_area`, `aspect_ratio`, `N`, `nrofHostGroups`, `speed_mean`, `wait_mean`, `mm_WDM`, `mm_RWP`, `mm_MapRoute`, `mm_Cluster`, `mm_Bus`, `mm_Linear`, `transmitRange`, `bufferSize`, `transmitSpeed`, `msgTtl`, `event_interval_mean`, `event_size_mean`, `nrof_event_generators`, `pattern_burst`, `pattern_hub_target`, `workDayLength`, `ownCarProb`.

**Decisión final destacada:** `clusterRange_mean` pasa a extended por cobertura baja y aporte marginal no robusto en el freeze final.

## 3) Política NaN y normalización

- Se normaliza por columna (z-score) **ignorando NaN** en media y desviación.
- Luego se imputa NaN a `0` **solo en espacio estandarizado**.
- Esta decisión es metodológica (comparabilidad en espacio común), no ontológica (no implica que “no aplica” sea valor medio físico).

## 4) Snapshot final (freeze optimizado)

- **Full-46:** `max|r|=0.9377`, `pares>=0.7=46/1770 (2.6%)`, `min cosine=0.0620`, `silhouette=0.2929`.
- **Core-23:** `max|r|=0.9829`, `pares>=0.7=58/1770 (3.3%)`, `min cosine=0.0152`, `silhouette=0.2681`.
- **Feature-feature core:** `mm_WDM <-> mm_Bus = 0.9393` (dependencia residual documentada).
- **Ablación (17/23/46):** `63 (3.6%), 0.2215` / `58 (3.3%), 0.2681` / `46 (2.6%), 0.2929`.

## 5) Framing de paper

La versión actual se presenta como **baseline mejorado, estable y publicable**, con limitaciones declaradas (pares altos residuales, silhouette moderado en core, dependencia `mm_WDM <-> mm_Bus`).  
No se presenta como corpus óptimo final.
