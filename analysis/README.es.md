# Análisis del corpus de escenarios (The ONE)

*(Versión en castellano. English: [README.md](README.md).)*

Este directorio contiene el pipeline de análisis de los escenarios del corpus: extracción de **features estables y reportables**, normalización, correlaciones, gráficos e informes para el benchmark de protocolos de enrutamiento en redes oportunistas.

**Contexto:** el corpus de escenarios está en [../corpus_v1](../corpus_v1); la guía de configuración del ONE está en [../README.es.md](../README.es.md).

---

## Un script con fases (recomendado)

Se usa **un solo script** (`run_analysis.py`) con varias fases ejecutables de forma independiente. Así se evita duplicar el parser y la definición de features, y se pueden ejecutar solo los pasos que interesen o repetir fases posteriores sin volver a extraer datos.

- **Ventajas**: una única entrada, resultados intermedios en `data/` (p. ej. `features.csv` → `features_normalized.csv`), posibilidad de `--phase all` para correr todo.
- **Fases**: `features` → `normalize` → `correlation` → `figures` → `output_metrics` → `outputs`. Cada fase escribe en `data/`, `figures/` o `reports/` y puede ejecutarse por separado (p. ej. solo normalizar si ya tienes `features.csv`).

Alternativa con **varios scripts** (uno por paso) sería útil si quisieras orquestar pasos en otro lenguaje o herramienta; por ahora el diseño con un script y fases es más simple de mantener.

---

## Estructura de directorios

```
analysis/
├── README.md / README.es.md   # Este documento: definiciones y guía del análisis
├── dashboard.py        # Dashboard interactivo (Streamlit): resumen, por fase, por escenario, comparar
├── run_all_scenarios.py # Ejecuta todas las simulaciones del corpus (one.sh por cada .settings)
├── data/               # Datos derivados (features.csv, features_normalized.csv, matrices, output_metrics.csv)
├── figures/            # Gráficos (heatmaps, scatter, histogramas)
├── reports/            # Informes de texto y resúmenes (correlation_report.txt, etc.)
└── run_analysis.py     # Script principal por fases (extracción → correlación → reporte)
```

- **data/**: Vectores de features por escenario, matrices de correlación/distancias, exports en CSV.
- **figures/**: Figuras en PNG/PDF para informes y paper.
- **reports/**: Conclusiones en texto (`correlation_report.txt`), y **observaciones para trabajo posterior** (`observaciones_correlacion.md`).

El script `run_analysis.py` se ejecuta por fases y escribe siempre en esta estructura. Para visualizar resultados de forma interactiva (por fase, por escenario, comparación entre escenarios) se puede usar el **dashboard** (`dashboard.py`) con Streamlit.

---

## Features estables y reportables

Definimos un conjunto de **features** extraíbles de los `.settings` que son **estables** (reproducibles a partir del archivo) y **reportables** (útiles para describir el escenario en papers e informes). Se agrupan en cuatro bloques.

### 1. Movilidad / espacio

| Feature | Descripción | Unidad / notas |
|--------|-------------|-----------------|
| **Wx** | Ancho del mundo (eje X) | m |
| **Wy** | Alto del mundo (eje Y) | m |
| **N** | Número total de nodos (suma de todos los grupos) | — |
| **density** | Densidad de nodos: N / (Wx×Wy), escalada a “por km²” (×10⁶ si área en m²) | nodos/km² (proxy) |
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
2. **Normalización** (`--phase normalize`): Lee `data/features.csv` y aplica **z-score por característica**: \( X_{s,j}^{\text{norm}} = (X_{s,j} - \mu_j) / \sigma_j \), con \(\mu_j\), \(\sigma_j\) la media y desviación típica de la característica \(j\). Si \(\sigma_j = 0\) (columna constante), se deja en 0. Parámetros guardados en `data/normalization_params.csv`; salida: `data/features_normalized.csv`.
3. **Correlación entre escenarios** (`--phase correlation`): Lee `data/features_normalized.csv` (matriz Z, n×d con n = número de escenarios). **Pearson** r(Si, Sk) = corr(Zi, Zk); **Spearman** (correlación de rangos); **métricas geométricas**: distancia coseno (1 − cos_sim) y distancia euclídea entre filas de Z. Salidas en `data/`: `correlation_pearson.csv`, `correlation_spearman.csv`, `distance_cosine.csv`, `distance_euclidean.csv`, `correlation_pearson_pvalues.csv`. Criterio: **|r| < 0.7** para todos o ≥95% de los pares (`--strict` exige 100%). **Test y corrección múltiple**: p-value por par (H0: ρ=0), **FDR (Benjamini-Hochberg)** y **Bonferroni** (`--fdr-alpha`). Objetivo: no pares con |r| alto y significativos tras corrección. Informes: `reports/correlation_report.txt` (incluye resumen Spearman y distancias), `reports/multiple_comparisons_report.txt`. Matrices de Pearson/Spearman entre vectores de escenarios, distancias coseno y euclídea; se guardan en `data/`.
4. **Figuras** (`--phase figures`): Heatmaps Pearson/Spearman, histogramas de correlaciones, scatter PCA 2D y scatter par con mayor |r|; se guardan en `figures/` (.png y .pdf).
5. **Rellenado de métricas de salida** (`--phase output_metrics`): **Automatiza** la creación de `data/output_metrics.csv` a partir de los ficheros `*_MessageStatsReport.txt` en el directorio de reportes (por defecto `reports/` en la raíz del repo; `--reports-dir` para otro). Parsea: `delivery_prob` → `delivery_ratio`, `latency_avg` → `latency_mean`, `overhead_ratio`, `drop_ratio` = dropped/created. Una fila por escenario (nombre del fichero). No hace falta rellenar el CSV a mano si ya tienes los reportes del ONE.
6. **Validación sobre outputs** (`--phase outputs`): Vectores Y_s por escenario (delivery_ratio, latency_mean, overhead_ratio, drop_ratio) a partir de `data/output_metrics.csv`; mismo procedimiento (z-score, Pearson, Spearman, distancias). Salidas en `data/` y `reports/outputs_correlation_report.txt`; heatmap en `figures/heatmap_pearson_outputs.png`. Requiere `output_metrics.csv` (generable con `--phase output_metrics`).
7. **(Opcional) Informe final**: Resumen en `reports/report.txt` (y opcionalmente más salidas) con max |r|, fracción de pares por encima del umbral y conclusión sobre “no correlación lineal fuerte” / “conjunto no redundante”.

Las fases `features`, `normalize`, `correlation`, `figures`, `output_metrics` y `outputs` están implementadas. Con `--phase all` se ejecutan: features → normalize → correlation → figures → output_metrics (si existe el directorio de reportes). La validación `outputs` se ejecuta solo con `--phase outputs` (tras tener `output_metrics.csv`, a mano o con `--phase output_metrics`).

---

## Ejecutar todas las simulaciones (generar reportes)

Para tener todos los outputs (MessageStatsReport, ContactTimesReport, etc.) en `reports/`, ejecuta el ONE para cada escenario del corpus con **`run_all_scenarios.py`**:

```bash
# Desde la raíz del repo (recomendado)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1

# Solo listar, sin ejecutar
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 --dry-run
```

Requisitos: Java, el ONE compilado (`one.sh` en la raíz). Los reportes se escriben en el directorio configurado en cada `.settings` (por defecto `reports/`). Después puedes ejecutar `run_analysis.py --phase output_metrics` para rellenar `data/output_metrics.csv` desde esos reportes.

---

## Cómo ejecutar (análisis)

Desde el directorio `scenarios/` (o con el path adecuado a `corpus_v1`):

```bash
# Extracción de features → data/features.csv
python3 run_analysis.py --corpus corpus_v1 --phase features

# Normalización z-score → data/features_normalized.csv, data/normalization_params.csv
python3 run_analysis.py --corpus corpus_v1 --phase normalize

# Matriz de correlación entre escenarios → data/*.csv, reports/*.txt
python3 run_analysis.py --phase correlation
python3 run_analysis.py --phase correlation --threshold 0.7 --strict   # exige 100% pares con |r|<0.7

# Gráficos → figures/*.png, figures/*.pdf (requiere correlation previa)
python3 run_analysis.py --phase figures

# Rellenar output_metrics.csv desde reports/*_MessageStatsReport.txt (automatizado)
python3 run_analysis.py --phase output_metrics
# Si los reportes están en otro directorio:
python3 run_analysis.py --phase output_metrics --reports-dir /ruta/a/reports

# Validación sobre outputs (requiere data/output_metrics.csv)
python3 run_analysis.py --phase outputs

# Todas las fases (features → normalize → correlation → figures → output_metrics; outputs por separado)
python3 run_analysis.py --corpus corpus_v1 --phase all

# Con el venv del proyecto (si numpy/pandas están en el venv)
../venv/bin/python run_analysis.py --corpus corpus_v1 --phase features
../venv/bin/python run_analysis.py --corpus corpus_v1 --phase normalize
```

O desde la raíz del repo:

```bash
cd scenarios && python3 run_analysis.py --corpus corpus_v1 --phase features
```

Las rutas de salida son siempre relativas a `scenarios/analysis/` (data/, figures/, reports/). Requiere `numpy` y, para CSV cómodo, `pandas`.

### Dashboard interactivo

Para ver todos los resultados en un único sitio (resumen, por fase, por escenario, comparar escenarios):

```bash
streamlit run dashboard.py   # desde scenarios/analysis
# o desde la raíz del repo:
streamlit run scenarios/analysis/dashboard.py
```

Requiere `streamlit` y `pandas`.
