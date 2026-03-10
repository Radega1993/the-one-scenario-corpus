# Scenario corpus analysis (The ONE)

*(English. Spanish: [README.es.md](README.es.md).)*

This directory contains the analysis pipeline for the scenario corpus: extraction of **stable, reportable features**, normalisation, correlations, figures and reports for the opportunistic routing protocol benchmark.

**Context:** the scenario corpus is in [../corpus_v1](../corpus_v1); the ONE configuration guide is in [../README.md](../README.md) (summary) and [../README.es.md](../README.es.md) (full .settings reference).

---

## Single script with phases (recommended)

One script (`run_analysis.py`) with several phases that can be run independently. This avoids duplicating the parser and feature definitions, and lets you run only the steps you need or re-run later phases without re-extracting.

- **Phases:** `features` → `features_report` → `normalize` → `correlation` → `feature_correlation` → `ablation` → `figures` → `output_metrics` → `outputs`. Each phase writes to `data/`, `figures/` or `reports/`. Use `--phase all` to run the full pipeline.
- **Outputs:** intermediate results in `data/` (e.g. `features.csv` → `features_normalized.csv`, `features_core.csv` 24 cols, `features_reduced.csv` 17 cols).
- **Core vs extended:** methodology in [docs/features_core_vs_extended.md](docs/features_core_vs_extended.md) (24 core features for diversity/paper, 46 extended for exploration). Space uses **world_area** (Wx×Wy) and **aspect_ratio** = min(Wx,Wy)/max(Wx,Wy). **NaN policy:** z-score per column ignoring NaN; then impute NaN → 0 in standardized space (§4).

---

## Directory structure

```
analysis/
├── README.md / README.es.md   # This document: definitions and pipeline guide
├── dashboard.py                # Interactive dashboard (Streamlit)
├── run_all_scenarios.py       # Runs all corpus simulations (one.sh per .settings)
├── data/                       # Derived data (features, matrices, output_metrics.csv)
├── figures/                    # Plots (heatmaps, scatter, histograms)
├── reports/                    # Text reports and notes
└── run_analysis.py            # Main script by phase
```

---

## Features (summary)

**Current results (benchmark status):** **60 scenarios**, **46 features** (extended); **24 core** for diversity/paper. **Core 24:** 88 pairs (5.0%) with |r| ≥ 0.7; max |r| **0.9708** (U11↔U12); min cosine 0.0295; Silhouette (Ward k=7) **0.3227**. Space 46: 54 pairs (3.1%) with |r| ≥ 0.7; max |r| 0.9357. **Why 24 core / why discarded:** [docs/features_core_vs_extended.md](docs/features_core_vs_extended.md), [docs/features_decision.md](docs/features_decision.md). Single reference: [reports/RESULTADOS_ACTUALES.md](reports/RESULTADOS_ACTUALES.md).

**46 features** per scenario: **space** (**world_area** = Wx×Wy, **aspect_ratio** = min(Wx,Wy)/max(Wx,Wy), N, density, speed_mean, pause_ratio, wait_mean, movement-model one-hot), **contact** (transmitRange, contact_rate_proxy), **traffic** (event_interval_mean, event_size_mean, msgTtl, pattern_*, nrof_event_generators, event2_*), **resources** (bufferSize, transmitSpeed), **WDM** (workDayLength, ownCarProb, …), **cluster** (clusterRange_mean). Core 24 list and methodology: [docs/features_core_vs_extended.md](docs/features_core_vs_extended.md). Full list and settings not used: `reports/features_report.md`, [docs/features_decision.md](docs/features_decision.md).

---

## What the script does (`run_analysis.py`)

1. **`--phase features`**: Read all `.settings`, build the 46‑dim feature vector (world_area, aspect_ratio, N, …), write `data/features.csv` and `scenario_list.txt`.
2. **`--phase features_report`**: Write `reports/features_report.txt` and `features_report.md` (features used + settings not used with reasons).
3. **`--phase normalize`**: Z-score per column (ignoring NaN), then impute NaN → 0 (§4). Writes `features_normalized.csv`, `normalization_params.csv`, `features_core.csv` (24), `features_reduced.csv` (17).
4. **`--phase correlation`**: Scenario–scenario Pearson/Spearman, cosine and Euclidean distance. Criterion: |r| < 0.7 for ≥95% of pairs. FDR and Bonferroni.
5. **`--phase feature_correlation`**: Feature–feature correlation matrix 24×24 (core); `data/feature_feature_correlation_core.csv`, `figures/heatmap_feature_feature_core.png`, `reports/feature_feature_correlation_report.txt`.
6. **`--phase ablation`**: Compare diversity metrics for 17 vs 24 vs 46 features (max |r|, mean |r|, pairs ≥0.7, Silhouette). `reports/ablation_report.txt`, `data/ablation_metrics.csv`.
7. **`--phase figures`**: Heatmaps, histograms, PCA scatter → `figures/`.
8. **`--phase output_metrics`**: Build `data/output_metrics.csv` from `*_MessageStatsReport.txt` (`--reports-dir` if needed).
9. **`--phase outputs`**: Correlation/distance on output vectors; requires `output_metrics.csv`.

With `--phase all`: features → normalize → correlation → feature_correlation → ablation → figures → output_metrics (outputs run separately when `output_metrics.csv` exists).

---

## Run all simulations (generate reports)

To get all ONE reports (MessageStatsReport, ContactTimesReport, etc.) in `reports/`:

```bash
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1
# List only, no run:
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 --dry-run
```

Requires Java and the ONE built (`one.sh` at repo root). Then run `run_analysis.py --phase output_metrics` to fill `data/output_metrics.csv` from those reports.

---

## Run analysis

From repo root (or with paths adjusted):

```bash
# Features
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase features

# Features report (list features + settings not used)
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase features_report

# Normalise
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase normalize

# Correlation (and optional --threshold 0.7 --strict)
python3 scenarios/analysis/run_analysis.py --phase correlation

# Feature–feature correlation (core 24×24)
python3 scenarios/analysis/run_analysis.py --phase feature_correlation

# Ablation 17 vs 24 vs 46
python3 scenarios/analysis/run_analysis.py --phase ablation

# Figures
python3 scenarios/analysis/run_analysis.py --phase figures

# Output metrics from reports
python3 scenarios/analysis/run_analysis.py --phase output_metrics

# Outputs correlation (needs output_metrics.csv)
python3 scenarios/analysis/run_analysis.py --phase outputs

# All phases (features → … → output_metrics)
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase all
```

Output paths are relative to `scenarios/analysis/`. Requires `numpy` and `pandas`.

### Interactive dashboard

```bash
streamlit run scenarios/analysis/dashboard.py   # from repo root
# or from scenarios/analysis:
streamlit run dashboard.py
```

Requires `streamlit` and `pandas`.
