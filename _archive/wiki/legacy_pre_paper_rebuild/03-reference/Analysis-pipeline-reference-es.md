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
| **features** | Extraer vector de features de cada .settings (world_area, aspect_ratio, …) | directorio del corpus (p. ej. corpus_v1) | `data/features.csv`, `data/scenario_list.txt` |
| **features_report** | Listar features usados + settings no usados (con motivos) | corpus, data/ | `reports/features_report.txt`, `reports/features_report.md` |
| **normalize** | Z-score por columna (ignorando NaN), imputar NaN→0; escribir core/reduced | `data/features.csv` | `data/features_normalized.csv`, `data/normalization_params.csv`, `data/features_core.csv` (23), `data/features_reduced.csv` (17) |
| **correlation** | Pearson, Spearman, distancia coseno y euclídea entre escenarios | `data/features_normalized.csv` | `data/correlation_*.csv`, `data/distance_*.csv`, `reports/correlation_report.txt`, `reports/multiple_comparisons_report.txt`, `reports/clustering_report.txt`, `data/cluster_assignments.csv` |
| **feature_correlation** | Matriz de correlación feature–feature (core 23×23) | `data/features_core.csv` | `data/feature_feature_correlation_core.csv`, `figures/heatmap_feature_feature_core.*`, `reports/feature_feature_correlation_report.txt` |
| **ablation** | Comparar métricas de diversidad (17 vs 23 vs 46 features) | `data/features_normalized.csv`, features_core.csv, features_reduced.csv | `reports/ablation_report.txt`, `data/ablation_metrics.csv` |
| **figures** | Heatmaps, histogramas, scatter PCA | `data/*.csv` (de correlation) | `figures/*.png`, `figures/*.pdf` |
| **output_metrics** | Construir output_metrics desde reportes del ONE | `*_MessageStatsReport.txt` (p. ej. en reports/) | `data/output_metrics.csv` |
| **outputs** | Correlación/distancias sobre vectores de salida | `data/output_metrics.csv` | `data/*_outputs.csv`, `reports/outputs_correlation_report.txt`, `figures/heatmap_pearson_outputs.*` |

---

## Opciones principales

- `--corpus <ruta>` — Ruta al directorio del corpus (necesaria para `features`; puede ser relativa, p. ej. `corpus_v1` si se ejecuta desde la raíz con scenarios/corpus_v1).
- `--phase <nombre>` — Una de: `features`, `features_report`, `normalize`, `correlation`, `feature_correlation`, `ablation`, `figures`, `output_metrics`, `outputs`, `all`. Con `all` se ejecutan features → features_report → normalize → correlation → feature_correlation → ablation → figures → output_metrics (no `outputs`).
- `--reports-dir <ruta>` — Para `output_metrics`: directorio con los reportes del ONE (por defecto: `reports/` en la raíz del ONE).
- `--threshold 0.7` — Umbral de correlación para los informes (por defecto 0.7).
- `--strict` — Exigir que el 100 % de pares tengan |r| < umbral (fase correlation).

---

## Resumen de artefactos

| Ubicación | Contenido |
|-----------|-----------|
| **analysis/data/** | features.csv, features_normalized.csv, normalization_params.csv, **features_core.csv** (23), **features_reduced.csv** (17), correlation_pearson.csv, correlation_spearman.csv, correlation_pearson_pvalues.csv, distance_cosine.csv, distance_euclidean.csv, **feature_feature_correlation_core.csv**, **ablation_metrics.csv**, cluster_assignments.csv, output_metrics.csv, *_outputs.csv |
| **analysis/figures/** | heatmap_pearson.*, heatmap_spearman.*, **heatmap_feature_feature_core.***, histogram_correlations_*.*, scatter_pca_regression.*, scatter_max_r_pair_regression.*, heatmap_pearson_outputs.* |
| **analysis/reports/** | correlation_report.txt, multiple_comparisons_report.txt, **feature_feature_correlation_report.txt**, **ablation_report.txt**, clustering_report.txt, scenarios_to_diversify.txt, **features_report.txt**, **features_report.md**, outputs_correlation_report.txt, observaciones_correlacion.md, plan_radical_scenarios.md |

---

## Ver también

- [Quickstart](Quickstart-es) — Cómo ejecutar el pipeline  
- [Metodología](Methodology-es) — Definición de features y correlación  
- [Referencia de features](Features-reference-es) — Los 46 features (descripción, origen); core 23 vs extended; settings no usados (con motivos)  
- [Resumen de resultados](Results-overview-es) — Resultados principales  
