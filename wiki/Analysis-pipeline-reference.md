# Analysis pipeline reference

**English** | [Español](Analysis-pipeline-reference-es)

---

Technical reference for **run_analysis.py**: phases, inputs, outputs, and artefacts.

---

## Script and usage

- **Script:** `scenarios/analysis/run_analysis.py`
- **Run from:** Repository root (parent of `scenarios/`).
- **Example:** `python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase all`

---

## Phases (order)

| Phase | Purpose | Main inputs | Main outputs |
|-------|---------|-------------|--------------|
| **features** | Extract feature vector from each .settings | corpus dir (e.g. corpus_v1) | `data/features.csv`, `data/scenario_list.txt` |
| **normalize** | Z-score normalise features | `data/features.csv` | `data/features_normalized.csv`, `data/normalization_params.csv` |
| **correlation** | Pearson, Spearman, cosine & Euclidean distance | `data/features_normalized.csv` | `data/correlation_*.csv`, `data/distance_*.csv`, `reports/correlation_report.txt`, `reports/multiple_comparisons_report.txt`, `reports/clustering_report.txt`, `data/cluster_assignments.csv` |
| **figures** | Heatmaps, histograms, PCA scatter | `data/*.csv` (from correlation) | `figures/*.png`, `figures/*.pdf` |
| **output_metrics** | Build output_metrics from ONE reports | `*_MessageStatsReport.txt` (e.g. in reports/) | `data/output_metrics.csv` |
| **outputs** | Correlation/distances on output vectors | `data/output_metrics.csv` | `data/*_outputs.csv`, `reports/outputs_correlation_report.txt`, `figures/heatmap_pearson_outputs.*` |

---

## Key options

- `--corpus <path>` — Path to corpus directory (required for `features`; can be relative, e.g. `corpus_v1` if run from repo root with scenarios/corpus_v1).
- `--phase <name>` — One of: `features`, `normalize`, `correlation`, `figures`, `output_metrics`, `outputs`, `all`. With `all`, runs features → normalize → correlation → figures → output_metrics (not `outputs`).
- `--reports-dir <path>` — For `output_metrics`: directory containing ONE report files (default: `reports/` at ONE root).
- `--threshold 0.7` — Correlation threshold for reports (default 0.7).
- `--strict` — Require 100% of pairs with |r| < threshold (for correlation phase).

---

## Artefacts summary

| Location | Contents |
|----------|----------|
| **analysis/data/** | features.csv, features_normalized.csv, normalization_params.csv, correlation_pearson.csv, correlation_spearman.csv, correlation_pearson_pvalues.csv, distance_cosine.csv, distance_euclidean.csv, cluster_assignments.csv, output_metrics.csv, *_outputs.csv |
| **analysis/figures/** | heatmap_pearson.*, heatmap_spearman.*, histogram_correlations_*.*, scatter_pca_regression.*, scatter_max_r_pair_regression.*, heatmap_pearson_outputs.* |
| **analysis/reports/** | correlation_report.txt, multiple_comparisons_report.txt, clustering_report.txt, scenarios_to_diversify.txt, outputs_correlation_report.txt, observaciones_correlacion.md, plan_radical_scenarios.md |

---

## See also

- [Quickstart](Quickstart) — How to run the pipeline  
- [Methodology](Methodology) — How features and correlation are defined  
- [Results overview](Results-overview) — Main results  
