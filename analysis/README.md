# Scenario corpus analysis (The ONE)

*(English. Spanish: [README.es.md](README.es.md).)*

This directory contains the analysis pipeline for the scenario corpus: extraction of **stable, reportable features**, normalisation, correlations, figures and reports for the opportunistic routing protocol benchmark.

**Context:** the scenario corpus is in [../corpus_v1](../corpus_v1); the ONE configuration guide is in [../README.md](../README.md) (summary) and [../README.es.md](../README.es.md) (full .settings reference).

---

## Single script with phases (recommended)

One script (`run_analysis.py`) with several phases that can be run independently. This avoids duplicating the parser and feature definitions, and lets you run only the steps you need or re-run later phases without re-extracting.

- **Phases:** `features` → `features_report` → `normalize` → `correlation` → `figures` → `output_metrics` → `outputs`. Each phase writes to `data/`, `figures/` or `reports/`. Use `--phase all` to run features through output_metrics.
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

**Current results (benchmark status):** 70 scenarios, 46 features; **95.9%** of pairs with |r| < 0.7 (98 pairs, 4.1%, with |r| ≥ 0.7); max |r| **0.938**; cosine distance min **0.0527** (0 pairs below 0.05); Silhouette 0.294. Full table: [reports/diversity_targets.md](reports/diversity_targets.md).

**46 features** per scenario: **mobility/space** (Wx, Wy, N, density, speed_mean, pause_ratio, wait_mean, movement-model one-hot including mm_Linear), **contact** (transmitRange, contact_rate_proxy), **traffic** (event_interval_mean, event_size_mean, msgTtl, pattern_*, nrof_event_generators, event2_interval_mean, event2_size_mean when applicable), **resources** (bufferSize, transmitSpeed), **WDM** (workDayLength, timeDiffSTD, probGoShoppingAfterWork, nrOfMeetingSpots, nrOfOffices, officeSize, nrOfShops, ownCarProb, shopSize, officeWaitTime_mean, shoppingWaitTime_mean, eveningGroupSize_mean, eveningWaitTime_mean, afterShoppingStopTime_mean), and **cluster** (clusterRange_mean when ClusterMovement). Full list and settings not used: `reports/features_report.md` and `reports/features_decision.md`.

---

## What the script does (`run_analysis.py`)

1. **`--phase features`**: Read all `.settings`, build the 46‑dim feature vector, write `data/features.csv` and `scenario_list.txt`.
2. **`--phase features_report`**: Write `reports/features_report.txt` and `features_report.md` (features used + settings not used with reasons).
3. **`--phase normalize`**: Z-score normalise features → `data/features_normalized.csv`, `normalization_params.csv`.
4. **`--phase correlation`**: From normalised matrix Z: Pearson/Spearman correlation, cosine and Euclidean distance. Outputs in `data/` and `reports/`. Criterion: |r| < 0.7 for ≥95% of pairs (`--strict` for 100%). FDR and Bonferroni.
5. **`--phase figures`**: Heatmaps, histograms, PCA scatter → `figures/`.
6. **`--phase output_metrics`**: Build `data/output_metrics.csv` from `*_MessageStatsReport.txt` (`--reports-dir` if needed).
7. **`--phase outputs`**: Correlation/distance on output vectors; requires `output_metrics.csv`.

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

# Features report (list features + settings not used)
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase features_report

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
