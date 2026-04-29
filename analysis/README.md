# Scenario corpus analysis (The ONE)

*(English. Spanish: [README.es.md](README.es.md).)*

This directory contains the analysis pipeline for the scenario corpus: extraction of **stable, reportable features**, normalisation, correlations, figures and reports for the opportunistic routing protocol benchmark.

**Context:** the scenario corpus is in [../corpus_v1](../corpus_v1); the ONE configuration guide is in [../README.md](../README.md) (summary) and [../README.es.md](../README.es.md) (full .settings reference).

---

## Single script with phases (recommended)

One script (`run_analysis.py`) with several phases that can be run independently. This avoids duplicating the parser and feature definitions, and lets you run only the steps you need or re-run later phases without re-extracting.

- **Phases:** `features` → `features_report` → `normalize` → `correlation` → `feature_correlation` → `ablation` → `figures` → `figures_paper` → `tables_paper` → `indirects` → `output_metrics` → `outputs`. Each phase writes to `data/`, `figures/` or `reports/`. Use `--phase all` to run the full pipeline (including `indirects`).
- **Outputs:** intermediate results in `data/` (e.g. `features.csv` -> `features_normalized.csv`, `features_core.csv` 23 cols, `features_reduced.csv` 17 cols).
- **Core vs extended:** methodology in [docs/features_core_vs_extended.md](docs/features_core_vs_extended.md) (23 core features for diversity/paper, 46 extended for exploration). Space uses **world_area** (Wx×Wy) and **aspect_ratio** = min(Wx,Wy)/max(Wx,Wy). **NaN policy:** z-score per column ignoring NaN; then impute NaN -> 0 in standardized space (§4).

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

**Current results (final optimized freeze):** **60 scenarios**, **46 features** (extended); **23 core** for methodology/paper.  
**Full-46:** 46 pairs (2.6%) with `|r| >= 0.7`; `max |r| = 0.9377`; `min cosine = 0.0620`; Silhouette (Ward k=7) `0.2929`.  
**Core-23:** 58 pairs (3.3%) with `|r| >= 0.7`; `max |r| = 0.9829`; `min cosine = 0.0152`; Silhouette `0.2681`.  
Feature-feature (core): one high pair remains, `mm_WDM <-> mm_Bus = 0.9393`.  
This release is a **stable, publishable baseline** (not an optimal final corpus).  
**Why 23 core / why discarded:** [docs/features_core_vs_extended.md](docs/features_core_vs_extended.md), [docs/features_decision.md](docs/features_decision.md). Single reference: [reports/RESULTADOS_ACTUALES.md](reports/RESULTADOS_ACTUALES.md).

**46 features** per scenario: **space** (**world_area** = Wx×Wy, **aspect_ratio** = min(Wx,Wy)/max(Wx,Wy), N, density, speed_mean, pause_ratio, wait_mean, movement-model one-hot), **contact** (transmitRange, contact_rate_proxy), **traffic** (event_interval_mean, event_size_mean, msgTtl, pattern_*, nrof_event_generators, event2_*), **resources** (bufferSize, transmitSpeed), **WDM** (workDayLength, ownCarProb, ...), **cluster** (clusterRange_mean, extended). Core 23 list and methodology: [docs/features_core_vs_extended.md](docs/features_core_vs_extended.md). Full list and settings not used: `reports/features_report.md`, [docs/features_decision.md](docs/features_decision.md).

---

## What the script does (`run_analysis.py`)

1. **`--phase features`**: Read all `.settings`, build the 46‑dim feature vector (world_area, aspect_ratio, N, …), write `data/features.csv` and `scenario_list.txt`.
2. **`--phase features_report`**: Write `reports/features_report.txt` and `features_report.md` (features used + settings not used with reasons).
3. **`--phase normalize`**: Z-score per column (ignoring NaN), then impute NaN -> 0 (§4). Writes `features_normalized.csv`, `normalization_params.csv`, `features_core.csv` (23), `features_reduced.csv` (17).
4. **`--phase correlation`**: Scenario–scenario Pearson/Spearman, cosine and Euclidean distance. Criterion: |r| < 0.7 for ≥95% of pairs. FDR and Bonferroni.
5. **`--phase feature_correlation`**: Feature-feature correlation matrix 23x23 (core); `data/feature_feature_correlation_core.csv`, `figures/heatmap_feature_feature_core.png`, `reports/feature_feature_correlation_report.txt`.
6. **`--phase ablation`**: Compare diversity metrics for 17 vs 23 vs 46 features (max |r|, mean |r|, pairs >=0.7, Silhouette). `reports/ablation_report.txt`, `data/ablation_metrics.csv`.
7. **`--phase figures`**: Heatmaps, histograms, PCA scatter + comparative figures by space (`figures/by_space/` for `reduced_17`, `core_23`, `full_46`).
8. **`--phase figures_paper`**: Curated paper figures in `figures/paper/{main,supplementary}` (PNG+PDF).
9. **`--phase tables_paper`**: Curated paper tables in `figures/paper/tables/` (`*_es.md`, `*_en.md`).
10. **`--phase indirects`**: Indirect Diego-style metrics from report files (`data/indirect_features_diego.csv`, `reports/indirect_features_report.*`).
11. **`--phase output_metrics`**: Build `data/output_metrics.csv` from `*_MessageStatsReport.txt` (`--reports-dir` if needed).
12. **`--phase outputs`**: Correlation/distance on output vectors; requires `output_metrics.csv`.

With `--phase all`: features → features_report → normalize → correlation → feature_correlation → ablation → figures → output_metrics → indirects (outputs run separately when `output_metrics.csv` exists).

---

## Run all simulations (generate reports)

To get all ONE reports (MessageStatsReport, ContactTimesReport, etc.) in `reports/`:

```bash
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1
# List only, no run:
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 --dry-run

# Force all reports needed for Diego17 real / indirects:
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \
  --extra-settings scenarios/analysis/diego17_reports_overrides.txt

# Same command using project venv:
./venv/bin/python scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \
  --extra-settings scenarios/analysis/diego17_reports_overrides.txt
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

# Feature-feature correlation (core 23x23)
python3 scenarios/analysis/run_analysis.py --phase feature_correlation

# Ablation 17 vs 23 vs 46
python3 scenarios/analysis/run_analysis.py --phase ablation

# Figures
python3 scenarios/analysis/run_analysis.py --phase figures

# Paper-ready figures package
python3 scenarios/analysis/run_analysis.py --phase figures_paper

# Paper-ready tables package (ES+EN)
python3 scenarios/analysis/run_analysis.py --phase tables_paper

# Indirects (Diego-style) from reports/
python3 scenarios/analysis/run_analysis.py --phase indirects

# Output metrics from reports
python3 scenarios/analysis/run_analysis.py --phase output_metrics

# Outputs correlation (needs output_metrics.csv)
python3 scenarios/analysis/run_analysis.py --phase outputs

# All phases (features → … → output_metrics → indirects)
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase all

# Same (venv)
./venv/bin/python scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase all
```

Output paths are relative to `scenarios/analysis/`. Requires `numpy` and `pandas`.

### Interactive dashboard

```bash
streamlit run scenarios/analysis/dashboard.py   # from repo root
# or from scenarios/analysis:
streamlit run dashboard.py
# or with venv:
./venv/bin/streamlit run scenarios/analysis/dashboard.py
```

Requires `streamlit` and `pandas`.
