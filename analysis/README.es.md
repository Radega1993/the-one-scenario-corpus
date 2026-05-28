# Análisis del corpus de escenarios (The ONE)

*(Versión en castellano. English: [README.md](README.md).)*

Este directorio contiene el pipeline de análisis de los escenarios del corpus: extracción de **features estables y reportables**, normalización, correlaciones, gráficos e informes para el benchmark de protocolos de enrutamiento en redes oportunistas.

**Índice de scripts (roles y pipeline paper):** [SCRIPTS_INDEX.md](SCRIPTS_INDEX.md).

**Contexto:** benchmark activo [../corpus_v1](../corpus_v1) (540) + [../stress_controls](../stress_controls) (30); base estructural en [../base_scenarios](../base_scenarios) (45). Guía ONE: [../README.es.md](../README.es.md).

---

## Estado actual listo para paper

| Elemento | Valor |
|----------|--------|
| **Corpus activo** | `corpus_v1` (540) + `stress_controls` (30) = 570 simulaciones |
| **Estado** | Benchmark principal bajo congelación / revisión metodológica |
| **Resultados congelados** | [reports/RESULTADOS_ACTUALES.md](reports/RESULTADOS_ACTUALES.md) |
| **Figuras paper** | [figures/paper/main/](figures/paper/main/), [figures/paper/supplementary/](figures/paper/supplementary/) |
| **Tablas paper** | [figures/paper/tables/](figures/paper/tables/) (Markdown ES/EN) |
| **Catálogo de figuras** | [figures/README.md](figures/README.md) |

**Diversidad (570 escenarios):** ver métricas regeneradas y vigentes en [reports/RESULTADOS_ACTUALES.md](reports/RESULTADOS_ACTUALES.md).

---

## Documentación clave

| Documento | Propósito |
|-----------|-----------|
| [../INVENTARIO.md](../INVENTARIO.md) | Mapa completo/dashboard del repo (fuente vs generado) |
| [SCRIPTS_INDEX.md](SCRIPTS_INDEX.md) | Roles de scripts y pipeline paper oficial |
| [reports/RESULTADOS_ACTUALES.md](reports/RESULTADOS_ACTUALES.md) | Métricas congeladas |
| [figures/README.md](figures/README.md) | Catálogo de figuras |
| [docs/features_core_vs_extended.md](docs/features_core_vs_extended.md) | Core 23 vs extended 46 |
| [../corpus_v1/README.md](../corpus_v1/README.md) | Perfiles de tráfico y diseño del benchmark |

---

## Fuente vs generado (este directorio)

| Tipo | Rutas |
|------|--------|
| **Fuente** | `*.py`, `lib/`, `dashboard/`, `docs/`, overlays `*.txt`, `protocol_overlays/`, `data/realism_thresholds.yaml`, READMEs de figuras |
| **Generado** | `data/*.csv`, la mayoría de `reports/`, `figures/*.png` / `*.pdf` |
| **Salidas de simulación** | `reports/` en la raíz del repo (leídas por `output_metrics`, espacial, indirectas) |

Regenerar con el [pipeline oficial](#pipeline-oficial) siguiente.

---

## Pipeline oficial

Comandos completos (12 pasos): **[SCRIPTS_INDEX.md](SCRIPTS_INDEX.md)**.

1. Simulación — `run_all_scenarios.py --corpus corpus_v1` + overlays routing/contacto + espacial  
2. Métricas de salida — `run_analysis.py --phase output_metrics` (+ `indirects`)  
3. Features — `--phase features` → `normalize` → `correlation` → `feature_correlation` → `ablation`  
4. Espacial — `scripts/validation/analyze_spatial_occupancy.py`  
5. Creación de mensajes — `analyze_message_creation_times.py`  
6. Validación TP — `validate_traffic_profiles.py`  
7. Figuras — `--phase figures_paper` + `run_figures_aggregated.py`  
8. Tablas — `--phase tables_paper`  
9. Wiki — `build_wiki_research_reports.py` → `populate_wiki_paper.py`

---

## Un script con fases (recomendado)

**Resultados actuales (`corpus_v1`, 570 escenarios):** **46 features** extendidas; **core 23** para metodología/paper. Ver [reports/RESULTADOS_ACTUALES.md](reports/RESULTADOS_ACTUALES.md).

- **Core-23:** max \|r\| = 1,0; 11 325 pares (4,4 %) con \|r\| ≥ 0,7; silhouette ablación (Ward k=7) = 0,3451  
- **Full-46:** 8 356 pares (3,2 %) con \|r\| ≥ 0,7; silhouette = 0,2680  
- **Feature–feature (core):** `mm_WDM ↔ mm_Bus = 0,9393`  

Metodología core/extended: [docs/features_core_vs_extended.md](docs/features_core_vs_extended.md).

Se usa **un solo script** (`run_analysis.py`) con varias fases ejecutables de forma independiente. Espacio: **world_area** (Wx×Wy) y **aspect_ratio** = min(Wx,Wy)/max(Wx,Wy). **Política NaN (§4):** z-score por columna ignorando NaN; luego imputar NaN → 0 en espacio estandarizado.

- **Ventajas**: una única entrada, resultados intermedios en `data/` (p. ej. `features.csv` -> `features_normalized.csv`, `features_core.csv` 23 cols, `features_reduced.csv` 17 cols), posibilidad de `--phase all` para correr todo.
- **Fases**: `features` → `features_report` → `normalize` → `correlation` → `feature_correlation` → `ablation` → `figures` → `figures_paper` → `tables_paper` → `indirects` → `output_metrics` → `outputs`. Cada fase escribe en `data/`, `figures/` o `reports/`.

Alternativa con **varios scripts** (uno por paso) sería útil si quisieras orquestar pasos en otro lenguaje o herramienta; por ahora el diseño con un script y fases es más simple de mantener.

---

## Estructura de directorios

```
analysis/
├── README.md / README.es.md   # Este documento: definiciones y guía del análisis
├── analysis_menu.py           # Menú interactivo en castellano (lanza otros scripts)
├── lib/                       # Utilidades: rutas, connectivity_timeline, spatial_occupancy_io
├── dashboard.py        # Dashboard Streamlit (corpus_v1): salud, TP, explorador, espacial, auditoría
├── dashboard/          # Paquete: app.py, data_loaders.py, pages/
├── run_all_scenarios.py # Ejecuta todas las simulaciones del corpus (one.sh por cada .settings)
├── data/               # Datos derivados (features.csv, features_normalized.csv, matrices, output_metrics.csv)
├── figures/            # Gráficos; catálogo en figures/README.md; agregadas en figures/aggregated/
├── run_figures_aggregated.py  # Figuras legibles por familia / TP / base×TP
├── reports/            # Informes de texto y resúmenes (correlation_report.txt, etc.)
└── run_analysis.py     # Script principal por fases (extracción → correlación → reporte)
```

- **Menú interactivo:** `analysis_menu.py` — ver [MENU.md](MENU.md): simulación (1–2), pipeline (3), paper/validación (4a–4n), tiempo útil/mensajes/espacial (5–7), dashboard (8), figuras (9). Corpus legacy congelado.

- **data/**: Vectores de features por escenario, matrices de correlación/distancias, exports en CSV.
- **figures/**: Figuras en PNG/PDF. **Catálogo y veredictos:** [figures/README.md](figures/README.md). Con 570 escenarios no use heatmaps N×N; use `figures/aggregated/` y `figures/paper/main/`.
- **reports/**: Conclusiones en texto (`correlation_report.txt`), y **observaciones para trabajo posterior** (`observaciones_correlacion.md`).

El script `run_analysis.py` se ejecuta por fases y escribe siempre en esta estructura. Para explorar el **corpus_v1** (570 escenarios, perfiles TP, diagnóstico, heatmaps) usa el **dashboard** (`dashboard.py`): 8 vistas temáticas, filtros globales en la barra lateral y tablas unificadas desde `manifest.csv` + CSV en `data/`.

---

## Features estables y reportables

Definimos un conjunto de **features** extraíbles de los `.settings` que son **estables** (reproducibles a partir del archivo) y **reportables** (útiles para describir el escenario en papers e informes). Se agrupan en cuatro bloques.

### 1. Movilidad / espacio

| Feature | Descripción | Unidad / notas |
|--------|-------------|-----------------|
| **world_area** | Área del mundo Wx×Wy | m² |
| **aspect_ratio** | Relación de aspecto min(Wx,Wy)/max(Wx,Wy) ∈ (0, 1] | adimensional |
| **N** | Número total de nodos (suma de todos los grupos) | — |
| **density** | Densidad de nodos: N / world_area; excluida del core por redundancia | nodos/km² (proxy) |
| **speed_mean** | Velocidad media de movimiento (media del rango min–max si está definido) | m/s |
| **pause_ratio** | Fracción de tiempo en pausa: `wait_mean / (wait_mean + t_move)`. Usamos un segmento típico de movimiento (p. ej. 60 s) como proxy de tiempo entre pausas | 0–1 (adimensional) |
| **wait_mean** | Tiempo medio de espera entre waypoints | s |
| **mm_*** | Tipo de movimiento (one-hot): **mm_WDM**, **mm_RWP**, **mm_MapRoute**, **mm_Cluster**, **mm_Bus**, **mm_ShortestPath**, **mm_External** | 0/1 |

*Nota:* Si hay varios grupos con distintos `speed`/`waitTime`, se puede tomar el del primer grupo o una media ponderada por `nrofHosts`; en la v1 usamos el primer grupo que sobrescriba el valor por defecto.

### 2. Contacto esperado

| Feature | Descripción | Unidad / notas |
|--------|-------------|-----------------|
| **transmitRange** | Rango de transmisión (radio) | m |
| **contact_rate_proxy** | Proxy de tasa de contacto: `density × transmitRange² × speed_mean` (con factores de escala para unidades coherentes). Indica “cuánto contacto” cabe esperar por movilidad y rango | adimensional (relativo) |

### 3. Tráfico

| Feature | Descripción | Unidad / notas |
|--------|-------------|-----------------|
| **event_interval_mean** | Intervalo medio entre generación de mensajes (Events1.interval, y si hay varios generadores se puede promediar o reportar el principal) | s |
| **event_size_mean** | Tamaño medio de mensaje (Events1.size; si hay rango, media) | bytes |
| **msgTtl** | TTL de mensajes (Group.msgTtl en minutos; si no está definido, “infinito” → valor alto fijo para el vector) | min (reportable también en s si se desea) |
| **traffic_pattern** | Patrón de tráfico: **uniform** (origen/destino aleatorio en hosts), **burst** (Events*.time restringe a ventanas), **hub_target** (Events*.tohosts restringido a pocos destinos). Se puede codificar como one-hot: pattern_uniform, pattern_burst, pattern_hub_target | 0/1 |
| **nrof_event_generators** | Número de generadores de eventos (Events.nrof). Útil para distinguir tráfico unimodal vs bimodal/multimodal | — |

### 4. Recursos

| Feature | Descripción | Unidad / notas |
|--------|-------------|-----------------|
| **bufferSize** | Tamaño de buffer por nodo | bytes |
| **transmitSpeed** | Velocidad de transmisión del interfaz | bytes/s (o bps si se prefiere) |

### 5. WDM / actividad (WorkingDayMovement)

Solo tienen valor cuando el escenario usa WorkingDayMovement; en el resto son NaN.

| Feature | Descripción | Unidad / notas |
|--------|-------------|-----------------|
| **workDayLength** | Duración de la jornada laboral | s |
| **timeDiffSTD** | Desviación típica del desfase horario (despertar) | s |
| **probGoShoppingAfterWork** | Probabilidad de actividad tras el trabajo | 0–1 |
| **nrOfMeetingSpots** | Número de meeting spots | — |
| **nrOfOffices** | Número de oficinas | — |

---

## Propuestas adicionales (para mejor resultado)

- **Scenario.endTime**, **nrofHostGroups**, **has_active_times**: ya incluidos.
- **workDayLength**, **timeDiffSTD**, **probGoShoppingAfterWork**, **nrOfMeetingSpots**, **nrOfOffices**: ya incluidos (bloque WDM; ayudan a diferenciar escenarios urbanos/vehículos que comparten mapa).
- **mm_Cluster**: ClusterMovement en el one-hot (R2, D1, D2, S1, S6).
- **traffic_pattern**: Derivado de configuración (burst, hub_target, uniform).

Con esto el vector de features permite distinguir mejor escenarios que comparten HelsinkiMedium y WorkingDayMovement (p. ej. U9/U10 por workDayLength, U12 por timeDiffSTD, U2 por probGoShoppingAfterWork, U3/C5 por nrOfMeetingSpots, U1/U5 por nrOfOffices).

---

## Qué hace el script (`run_analysis.py`)

El script se organiza **por partes**:

1. **Extracción de features** (`--phase features`): Lee todos los `.settings` bajo el directorio indicado (p. ej. `corpus_v1`), aplica el parser de settings y construye el vector de features definido arriba. Escribe en `data/` un CSV con una fila por escenario y una columna por feature (`features.csv`, `scenario_list.txt`).
2. **Normalización** (`--phase normalize`): Lee `data/features.csv` y aplica **z-score por característica** usando solo valores no-NaN; luego **imputa NaN -> 0** en el espacio estandarizado (§4 features_core_vs_extended.md). Salida: `features_normalized.csv`, `normalization_params.csv`, `features_core.csv` (23), `features_reduced.csv` (17).
3. **Correlación entre escenarios** (`--phase correlation`): Lee `data/features_normalized.csv` (matriz Z, n×d con n = número de escenarios). **Pearson** r(Si, Sk) = corr(Zi, Zk); **Spearman** (correlación de rangos); **métricas geométricas**: distancia coseno (1 − cos_sim) y distancia euclídea entre filas de Z. Salidas en `data/`: `correlation_pearson.csv`, `correlation_spearman.csv`, `distance_cosine.csv`, `distance_euclidean.csv`, `correlation_pearson_pvalues.csv`. Criterio: **|r| < 0.7** para todos o ≥95% de los pares (`--strict` exige 100%). **Test y corrección múltiple**: p-value por par (H0: ρ=0), **FDR (Benjamini-Hochberg)** y **Bonferroni** (`--fdr-alpha`). Objetivo: no pares con |r| alto y significativos tras corrección. Informes: `reports/correlation_report.txt` (incluye resumen Spearman y distancias), `reports/multiple_comparisons_report.txt`. Matrices de Pearson/Spearman entre vectores de escenarios, distancias coseno y euclídea; se guardan en `data/`.
4. **Correlación feature-feature** (`--phase feature_correlation`): Matriz 23x23 entre las features del core. Salida: `data/feature_feature_correlation_core.csv`, `figures/heatmap_feature_feature_core.png`, `reports/feature_feature_correlation_report.txt`.
5. **Ablación** (`--phase ablation`): Compara métricas (max |r|, media |r|, pares >=0.7, Silhouette) para 17, 23 y 46 features. Salida: `reports/ablation_report.txt`, `data/ablation_metrics.csv`.
6. **Figuras** (`--phase figures`): Histogramas de correlación, scatter par con mayor |r|, heatmap feature×feature (23×23). **Heatmaps N×N entre escenarios omitidos por defecto si n>100** (corpus_v1); use `--include-full-heatmaps` solo para depuración. Comparativas en `figures/by_space/`.
7. **Figuras paper** (`--phase figures_paper`): paquete curado en `figures/paper/{main,supplementary}` (ver [figures/README.md](figures/README.md)).
7b. **Figuras agregadas** (`--phase figures_aggregated` o `run_figures_aggregated.py`): boxplots y heatmaps **base×TP** por familia en `figures/aggregated/`.
8. **Tablas paper** (`--phase tables_paper`): tablas Markdown ES/EN en `figures/paper/tables/`.
9. **Indirectas Diego** (`--phase indirects`): calcula indirectas desde reportes (`data/indirect_features_diego.csv`, `reports/indirect_features_report.*`).
10. **Rellenado de métricas de salida** (`--phase output_metrics`): **Automatiza** la creación de `data/output_metrics.csv` a partir de los ficheros `*_MessageStatsReport.txt` en el directorio de reportes (por defecto `reports/` en la raíz del repo; `--reports-dir` para otro). Parsea: `delivery_prob` → `delivery_ratio`, `latency_avg` → `latency_mean`, `overhead_ratio`, `drop_ratio` = dropped/created. Una fila por escenario (nombre del fichero). No hace falta rellenar el CSV a mano si ya tienes los reportes del ONE.
11. **Validación sobre outputs** (`--phase outputs`): Vectores Y_s por escenario; correlaciones en `data/` y `reports/outputs_correlation_report.txt`; histograma en `figures/histogram_correlations_outputs.png` (heatmap N×N solo con `--include-full-heatmaps`). Requiere `output_metrics.csv`.
9. **(Opcional) Informe final**: Resumen en `reports/report.txt` (y opcionalmente más salidas) con max |r|, fracción de pares por encima del umbral y conclusión sobre “no correlación lineal fuerte” / “conjunto no redundante”.

Con `--phase all` se ejecutan: features → features_report → normalize → correlation → feature_correlation → ablation → figures → output_metrics → indirects. La validación `outputs` se ejecuta con `--phase outputs` por separado.

---

## Ejecutar todas las simulaciones (generar reportes)

Para tener todos los outputs (MessageStatsReport, ContactTimesReport, etc.) en `reports/`, ejecuta el ONE para cada escenario del corpus con **`run_all_scenarios.py`**:

```bash
# Desde la raíz del repo (recomendado)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1

# Solo listar, sin ejecutar
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 --dry-run

# Forzar todos los reportes necesarios para Diego17 real / indirectas
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt

# Mismo comando con el venv del proyecto
./venv/bin/python scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt

# Ejecución en paralelo (recomendado para corpus_v1)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \
  --timeout 14400 --jobs 6
```

Requisitos: Java, el ONE compilado (`one.sh` en la raíz). Los reportes se escriben en el directorio configurado en cada `.settings` (por defecto `reports/`). Después puedes ejecutar `run_analysis.py --phase output_metrics` para rellenar `data/output_metrics.csv` desde esos reportes.

### Paralelización (`--jobs`)

- `run_all_scenarios.py` soporta ejecución paralela con `--jobs N`.
- Empieza con `--jobs 4` o `--jobs 6`; sube solo si CPU/RAM están estables.
- En esta máquina (`16` cores), un rango práctico suele ser `--jobs 6..8`.
- No lances dos ejecuciones completas del corpus al mismo tiempo sobre el mismo directorio `reports/`.

---

## Cómo ejecutar (análisis)

Desde el directorio `scenarios/analysis/` (o con el path adecuado a `corpus_v1`):

```bash
# Extracción de features → data/features.csv
python3 run_analysis.py --corpus corpus_v1 --phase features

# Normalización z-score → data/features_normalized.csv, data/normalization_params.csv
python3 run_analysis.py --corpus corpus_v1 --phase normalize

# Matriz de correlación entre escenarios → data/*.csv, reports/*.txt
python3 run_analysis.py --phase correlation
python3 run_analysis.py --phase correlation --threshold 0.7 --strict   # exige 100% pares con |r|<0.7

# Correlación feature-feature (core 23x23) -> data/, figures/, reports/
python3 run_analysis.py --phase feature_correlation

# Ablación 17 vs 23 vs 46 -> reports/ablation_report.txt, data/ablation_metrics.csv
python3 run_analysis.py --phase ablation

# Gráficos → figures/*.png, figures/*.pdf (requiere correlation previa)
python3 run_analysis.py --phase figures

# Figuras paper (main/supplementary, PNG+PDF)
python3 run_analysis.py --phase figures_paper

# Tablas paper (ES+EN)
python3 run_analysis.py --phase tables_paper

# Indirectas estilo Diego desde reports/
python3 run_analysis.py --phase indirects

# Rellenar output_metrics.csv desde reports/*_MessageStatsReport.txt (automatizado)
python3 run_analysis.py --phase output_metrics
# Si los reportes están en otro directorio:
python3 run_analysis.py --phase output_metrics --reports-dir /ruta/a/reports

# Validación sobre outputs (requiere data/output_metrics.csv)
python3 run_analysis.py --phase outputs

# Todas las fases (features → ... → output_metrics → indirects; outputs por separado)
python3 run_analysis.py --corpus corpus_v1 --phase all

# Con el venv del proyecto (si numpy/pandas están en el venv)
../venv/bin/python run_analysis.py --corpus corpus_v1 --phase features
../venv/bin/python run_analysis.py --corpus corpus_v1 --phase normalize
../venv/bin/python run_analysis.py --corpus corpus_v1 --phase all
```

O desde la raíz del repo:

```bash
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase features
```

Las rutas de salida son siempre relativas a `scenarios/analysis/` (data/, figures/, reports/). Requiere `numpy` y, para CSV cómodo, `pandas`.

### Dashboard interactivo

Para ver todos los resultados en un único sitio (resumen, por fase, por escenario, comparar escenarios):

```bash
./venv/bin/streamlit run scenarios/analysis/dashboard.py   # desde la raíz del repo
```

**Vistas:** Inicio · Perfiles TP · Explorador · Detalle escenario · Espacial · Auditoría · Pipeline clásico · Reportes crudos.

Requiere `streamlit`, `pandas` y `altair`.
