# Catálogo de figuras — análisis corpus_v1

Guía de **todas las figuras** generadas bajo `scenarios/analysis/figures/`: qué preguntan, de dónde salen y si conviene usarlas en el estudio o en el paper.

**Corpus de referencia:** `corpus_v1` — **540** escenarios (6 familias × 12 TP).

**Objetivo del estudio (dos ejes):**

1. **Diversidad de entradas:** los vectores de features normalizados (Z) deben ser suficientemente distintos entre escenarios (criterio metodológico: pocos pares con \|r\| ≥ 0,7; ver `reports/correlation_report.txt`).
2. **No trivialidad de salidas:** delivery, latencia, overhead y drops no deben colapsar en correlaciones lineales obvias entre todos los escenarios (fase `outputs`).

Con **N = 720**, cualquier heatmap **N×N con etiquetas por escenario es ilegible**. Use histogramas agregados, figuras en `aggregated/` y el paquete `paper/main/`.

---

## Árbol de directorios

```
figures/
├── README.md                 ← este catálogo
├── *.png / *.pdf             ← pipeline clásico (--phase figures)
├── by_space/                 ← ablación 17 / 23 / 46 features
├── aggregated/               ← figuras legibles por familia / TP / base (run_figures_aggregated.py)
├── paper/
│   ├── FIGURES_AND_TABLES_INDEX.md   ← catálogo paper (corpus_v1)
│   ├── main/                 ← figuras para artículo
│   ├── supplementary/
│   └── tables/               ← tablas Markdown ES/EN (no raster)
├── spatial_heatmaps/         ← un PNG por escenario (analyze_spatial_occupancy.py)
├── message_creation_time_*.png
└── spatial_occupancy_curves_by_family.png
```

---

## Figuras recomendadas para el paper (6–8)

| Figura | Ruta |
|--------|------|
| Histograma diversidad Pearson (anotado) | `paper/main/histogram_correlations_pearson_paper.png` |
| PCA 2D por familia | `paper/main/pca_by_family.png` |
| PCA 2D por cluster | `paper/main/pca_by_cluster.png` |
| Ablación % pares \|r\|≥0,7 | `paper/main/ablation_pairs_high_bar.png` |
| Ablación silhouette | `paper/main/ablation_silhouette_bar.png` |
| Heatmap feature×feature (core 23) | `paper/main/heatmap_feature_feature_core.png` |
| Delivery por TP (global) | `aggregated/outputs_boxplot_by_tp.png` |
| Heatmap base×TP (delivery) por familia | `aggregated/outputs_heatmap_base_x_tp_{family}.png` |
| Validación tiempos de creación TP | `message_creation_time_boxplot_by_tp.png` |

---

## Catálogo por origen

### Raíz — `run_analysis.py --phase figures`

| Archivo | Generador | Inputs | Pregunta | Audiencia | Veredicto |
|---------|-----------|--------|----------|-----------|-----------|
| `heatmap_pearson.*` | figures | `correlation_pearson.csv` | Matriz 720×720 de r entre Z | Depuración | **No por defecto** (usar `--include-full-heatmaps`) |
| `heatmap_spearman.*` | figures | `correlation_spearman.csv` | Igual, rangos | Depuración | **No por defecto** |
| `histogram_correlations_pearson.*` | figures | idem | ¿Cómo se distribuye r en todo el corpus? | Paper / informe | **Mantener** |
| `histogram_correlations_spearman.*` | figures | idem | Robustez | Suplemento | **Mantener** |
| `scatter_pca_regression.*` | figures | `features_normalized.csv` | PCA 2D con 720 etiquetas | — | **Omitido si N>100** |
| `scatter_max_r_pair_regression.*` | figures | idem | Par con mayor \|r\| en espacio Z | Didáctico | **Mantener** |
| `heatmap_feature_feature_core.*` | feature_correlation | `feature_feature_correlation_core.csv` | Redundancia entre 23 features | Metodología | **Mantener** |
| `heatmap_pearson_outputs.*` | outputs | `correlation_pearson_outputs.csv` | Correlación en espacio de salidas | Depuración | **No por defecto**; ver histograma |

### `by_space/` — mismas fases, distinto d (17 / 23 / 46)

| Patrón | Veredicto |
|--------|-----------|
| `heatmap_pearson_{reduced_17,core_23,full_46}.*` | **No por defecto** (720×720) |
| `histogram_correlations_pearson_{space}.*` | **Mantener** — comparar ablación |
| `scatter_pca_regression_{space}.*` | Opcional; preferir `paper/main/pca_by_family` |

### `paper/` — `--phase figures_paper`

| Archivo | Pregunta | Veredicto |
|---------|----------|-----------|
| `main/histogram_correlations_pearson_paper.*` | Diversidad global anotada | **Principal** |
| `main/pca_by_family.*` | Estructura por familia | **Principal** |
| `main/pca_by_cluster.*` | Coherencia clustering Ward | **Principal** |
| `main/ablation_pairs_high_bar.*` | ¿Core-23 basta? | **Principal** |
| `main/ablation_silhouette_bar.*` | Calidad clusters | **Principal** |
| `main/heatmap_feature_feature_core.*` | Redundancia features | **Principal / suplemento** |
| `supplementary/histogram_correlations_spearman_paper.*` | Robustez | Suplemento |
| `supplementary/histogram_correlations_outputs_paper.*` | Diversidad en salidas | **Suplemento** (sustituye heatmap outputs) |
| `supplementary/heatmap_pearson_outputs_paper.*` | — | **Obsoleto** (solo con `--include-full-heatmaps`) |

### `aggregated/` — `run_figures_aggregated.py`

| Archivo | Dimensión | Pregunta |
|---------|-----------|----------|
| `outputs_boxplot_by_tp.png` | TP01–12 | ¿TP mueven delivery/latency/overhead? |
| `outputs_boxplot_by_tp_faceted.png` | 7 familias × TP | ¿Separación TP homogénea? |
| `outputs_heatmap_base_x_tp_delivery.png` | 60×12 | Panel experimental completo |
| `outputs_heatmap_base_x_tp_{family}.png` | bases×12 por familia | Comparar dentro de familia |
| `correlation_hist_by_family.png` | 7 paneles | Diversidad intra-familia |
| `correlation_tp12_median_offdiag_by_base.png` | 60 bases | ¿TP se diferencian dentro de cada base? |
| `correlation_tp06_tp11_redundancy.png` | bases | ¿TP06≈TP11 en features? |
| `correlation_ablation_histogram_compare.png` | 17/23/46 | Ablación en un solo gráfico |
| `spatial_coverage_by_family.png` | familia | Cobertura espacial agregada |
| `spatial_gallery_{family}.png` | 1 base × TP | Ilustración cualitativa |
| `pearson_block_heatmap_ordered.png` | 720×720 sin etiquetas | Solo con `--include-block-heatmap` |

### Otros scripts

| Origen | Archivos | Veredicto |
|--------|----------|-----------|
| `analyze_message_creation_times.py` | `message_creation_time_hist_by_tp.png`, `message_creation_time_boxplot_by_tp.png` | **Muy útil** — validación TP |
| `analyze_spatial_occupancy.py` | `spatial_heatmaps/{scenario}.png` | **Curar** (no publicar las 720) |
| | `spatial_occupancy_curves_by_family.png` | **Útil** |
| Dashboard Streamlit | Altair interactivo | Complemento filtrable |

---

## Figuras obsoletas o solo depuración

- Heatmaps **720×720** con nombres de escenario (`heatmap_pearson`, `heatmap_spearman`, `heatmap_pearson_outputs`, `by_space/heatmap_*`).
- `scatter_pca_regression` con una etiqueta por escenario.

**Alternativas legibles:** histogramas, `aggregated/`, `paper/main/pca_by_family.png`, heatmaps **base×TP** (≤60×12).

Los CSV (`data/correlation_pearson.csv`, etc.) **siguen generándose** aunque no se dibuje el heatmap.

---

## Cómo regenerar

Desde `scenarios/analysis/` (con venv si aplica):

```bash
# Pipeline clásico (sin heatmaps N×N si N>100)
python3 run_analysis.py --corpus corpus_v1 --phase correlation
python3 run_analysis.py --corpus corpus_v1 --phase figures
python3 run_analysis.py --corpus corpus_v1 --phase output_metrics
python3 run_analysis.py --corpus corpus_v1 --phase outputs
python3 run_analysis.py --corpus corpus_v1 --phase figures_paper

# Figuras agregadas (familia / TP / base)
python3 run_figures_aggregated.py --corpus corpus_v1

# Forzar heatmaps completos (depuración)
python3 run_analysis.py --corpus corpus_v1 --phase figures --include-full-heatmaps

# Tiempos de creación y espacial
python3 analyze_message_creation_times.py
python3 analyze_spatial_occupancy.py --manifest ../corpus_v1/manifest.csv --reports-dir ../../reports
```

**Menú interactivo:** opción **10** (guía + agregadas) o **3** con fase `figures_aggregated`.

**Dashboard:** página **Figuras** (`streamlit run dashboard.py`).

---

## Trazabilidad

| Fase | `data/` | `figures/` | `reports/` |
|------|---------|------------|------------|
| correlation | `correlation_pearson.csv`, … | histogramas (figures) | `correlation_report.txt` |
| outputs | `correlation_pearson_outputs.csv` | histograma outputs | `outputs_correlation_report.txt` |
| figures_paper | — | `paper/main/`, `paper/supplementary/` | — |
| aggregated | manifest + output_metrics + … | `aggregated/` | — |

English summary: [README.en.md](README.en.md).