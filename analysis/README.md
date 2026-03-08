# Scenario corpus analysis (The ONE)

*(English. Spanish: [README.es.md](README.es.md).)*

This directory contains the analysis pipeline for the scenario corpus: extraction of **stable, reportable features**, normalisation, correlations, figures and reports for the opportunistic routing protocol benchmark.

**Context:** the scenario corpus is in [../corpus_v1](../corpus_v1); the ONE configuration guide is in [../README.md](../README.md) (summary) and [../README.es.md](../README.es.md) (full .settings reference).

---

## Single script with phases (recommended)

One script (`run_analysis.py`) with several phases that can be run independently. This avoids duplicating the parser and feature definitions, and lets you run only the steps you need or re-run later phases without re-extracting.

- **Phases:** `features` → `normalize` → `correlation` → `figures` → `output_metrics` → `outputs`. Each phase writes to `data/`, `figures/` or `reports/`. Use `--phase all` to run features through output_metrics.
- **Outputs:** intermediate results in `data/` (e.g. `features.csv` → `features_normalized.csv`).

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

Features are extracted from `.settings` and grouped into: **mobility/space** (Wx, Wy, N, density, speed_mean, pause_ratio, wait_mean, movement-model one-hot), **contact** (transmitRange, contact_rate_proxy), **traffic** (event_interval_mean, event_size_mean, msgTtl, traffic_pattern, nrof_event_generators), **resources** (bufferSize, transmitSpeed), and **WDM** (workDayLength, timeDiffSTD, probGoShoppingAfterWork, nrOfMeetingSpots, nrOfOffices) when applicable. Full tables: [README.es.md](README.es.md).

---

## What the script does (`run_analysis.py`)

1. **`--phase features`**: Read all `.settings` under the given corpus dir, build the feature vector, write `data/features.csv` and `scenario_list.txt`.
2. **`--phase normalize`**: Z-score normalise features → `data/features_normalized.csv`, `normalization_params.csv`.
3. **`--phase correlation`**: From normalised matrix Z (n×d, n = number of scenarios): Pearson and Spearman correlation, cosine and Euclidean distance between scenario vectors. Outputs in `data/` and `reports/`. Criterion: |r| < 0.7 for all or ≥95% of pairs (`--strict` for 100%). FDR and Bonferroni for multiple comparisons.
4. **`--phase figures`**: Heatmaps, histograms, PCA scatter → `figures/`.
5. **`--phase output_metrics`**: Build `data/output_metrics.csv` from `*_MessageStatsReport.txt` in the reports dir (`--reports-dir` if needed).
6. **`--phase outputs`**: Correlation/distance on output vectors (delivery_ratio, latency_mean, etc.); requires `output_metrics.csv`.

With `--phase all`: features → normalize → correlation → figures → output_metrics (outputs phase is run separately when `output_metrics.csv` exists).

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

# Normalise
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase normalize

# Correlation (and optional --threshold 0.7 --strict)
python3 scenarios/analysis/run_analysis.py --phase correlation

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
