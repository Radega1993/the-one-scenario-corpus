# Referencia del pipeline de análisis

**Español** | [English](Analysis-pipeline-reference)

---

Referencia técnica de **run_analysis.py**: fases, entradas, salidas y artefactos.

---

## Script y uso

- **Script:** `scenarios/analysis/run_analysis.py`
- **Ejecutar desde:** Raíz del repositorio (padre de `scenarios/`).
- **Ejemplo:** `python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase all`

---

## Fases (orden)

| Fase | Objetivo | Entradas principales | Salidas principales |
|------|----------|----------------------|----------------------|
| **features** | Extraer vector de features de cada .settings | directorio del corpus (p. ej. corpus_v1) | `data/features.csv`, `data/scenario_list.txt` |
| **normalize** | Normalizar features con z-score | `data/features.csv` | `data/features_normalized.csv`, `data/normalization_params.csv` |
| **correlation** | Pearson, Spearman, distancia coseno y euclídea | `data/features_normalized.csv` | `data/correlation_*.csv`, `data/distance_*.csv`, `reports/correlation_report.txt`, `reports/multiple_comparisons_report.txt`, `reports/clustering_report.txt`, `data/cluster_assignments.csv` |
| **figures** | Heatmaps, histogramas, scatter PCA | `data/*.csv` (de correlation) | `figures/*.png`, `figures/*.pdf` |
| **output_metrics** | Construir output_metrics desde reportes del ONE | `*_MessageStatsReport.txt` (p. ej. en reports/) | `data/output_metrics.csv` |
| **outputs** | Correlación/distancias sobre vectores de salida | `data/output_metrics.csv` | `data/*_outputs.csv`, `reports/outputs_correlation_report.txt`, `figures/heatmap_pearson_outputs.*` |

---

## Opciones principales

- `--corpus <ruta>` — Ruta al directorio del corpus (necesaria para `features`; puede ser relativa, p. ej. `corpus_v1` si se ejecuta desde la raíz con scenarios/corpus_v1).
- `--phase <nombre>` — Una de: `features`, `normalize`, `correlation`, `figures`, `output_metrics`, `outputs`, `all`. Con `all` se ejecutan features → normalize → correlation → figures → output_metrics (no `outputs`).
- `--reports-dir <ruta>` — Para `output_metrics`: directorio con los reportes del ONE (por defecto: `reports/` en la raíz del ONE).
- `--threshold 0.7` — Umbral de correlación para los informes (por defecto 0.7).
- `--strict` — Exigir que el 100 % de pares tengan |r| < umbral (fase correlation).

---

## Resumen de artefactos

| Ubicación | Contenido |
|-----------|-----------|
| **analysis/data/** | features.csv, features_normalized.csv, normalization_params.csv, correlation_pearson.csv, correlation_spearman.csv, correlation_pearson_pvalues.csv, distance_cosine.csv, distance_euclidean.csv, cluster_assignments.csv, output_metrics.csv, *_outputs.csv |
| **analysis/figures/** | heatmap_pearson.*, heatmap_spearman.*, histogram_correlations_*.*, scatter_pca_regression.*, scatter_max_r_pair_regression.*, heatmap_pearson_outputs.* |
| **analysis/reports/** | correlation_report.txt, multiple_comparisons_report.txt, clustering_report.txt, scenarios_to_diversify.txt, outputs_correlation_report.txt, observaciones_correlacion.md, plan_radical_scenarios.md |

---

## Ver también

- [Quickstart](Quickstart-es) — Cómo ejecutar el pipeline  
- [Metodología](Methodology-es) — Definición de features y correlación  
- [Resumen de resultados](Results-overview-es) — Resultados principales  
