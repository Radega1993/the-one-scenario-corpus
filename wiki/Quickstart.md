# Quickstart

**English** | [Español](Quickstart-es)

---

Get the corpus running: install dependencies, run scenarios, run the analysis pipeline, and open the dashboard.

---

## Requirements

See **[Installation](Installation)** for step-by-step setup (clone ONE, compile, Python venv, verify).

- **Java** (e.g. OpenJDK 11+) — for The ONE simulator
- **The ONE** — built from source (compile with `./compile.sh` in the ONE root)
- **Python 3** with: `numpy`, `pandas`, `scipy`, `matplotlib`, `streamlit`
- **Repository** — either the scenario corpus only, or the full ONE repo with `scenarios/` inside it (or linked)

---

## Project layout

Typical layout:

- **ONE root** (e.g. `the-one/` or `the-one-scenario-corpus/`) — contains `one.sh`, `compile.sh`, `default_settings.txt`, `reports/` (where ONE writes report files)
- **scenarios/** — contains `corpus_v1/`, `analysis/`, README, ROADMAP, and this wiki content

If the scenario corpus is a **separate repo**, run the ONE from its repo and point scripts to the path where you cloned the scenarios (e.g. `--corpus /path/to/scenarios/corpus_v1`).

---

## 1. Running scenarios (The ONE)

**Run a single scenario** (from the ONE root):

```bash
./one.sh -b 1 scenarios/corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiMedium.settings
```

**Run all 70 scenarios** (from the ONE root, or from the repo that contains `scenarios/`):

```bash
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1
```

- Reports (e.g. `*_MessageStatsReport.txt`) are written to the directory set in each `.settings` (often `reports/` at the ONE root).
- To only list scenarios without running: add `--dry-run`.

---

## 2. Running the analysis pipeline

From the **repository root** (parent of `scenarios/`):

```bash
# Extract features → analysis/data/features.csv
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase features

# Normalise (z-score) → analysis/data/features_normalized.csv
python3 scenarios/analysis/run_analysis.py --phase normalize

# Correlation matrices and reports → analysis/data/*.csv, analysis/reports/*.txt
python3 scenarios/analysis/run_analysis.py --phase correlation

# Figures → analysis/figures/*.png, *.pdf
python3 scenarios/analysis/run_analysis.py --phase figures

# Build output_metrics.csv from ONE reports (if reports/ exists)
python3 scenarios/analysis/run_analysis.py --phase output_metrics

# Output-based correlation (needs output_metrics.csv)
python3 scenarios/analysis/run_analysis.py --phase outputs
```

**Run everything (features through output_metrics) in one go:**

```bash
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase all
```

Run `outputs` separately after you have `analysis/data/output_metrics.csv` (from ONE runs + `output_metrics` phase).

---

## 3. Using the dashboard

From the **repository root**:

```bash
streamlit run scenarios/analysis/dashboard.py
```

- Opens a browser with: summary, results by phase, per-scenario view, scenario comparison.
- Requires `streamlit` and `pandas` (and the same Python env as the pipeline).

---

## Where outputs go

| Output | Path (relative to repo) |
|--------|-------------------------|
| Feature CSV, normalized, matrices | `scenarios/analysis/data/` |
| Figures (heatmaps, scatter, histograms) | `scenarios/analysis/figures/` |
| Text reports (correlation, clustering, etc.) | `scenarios/analysis/reports/` |
| ONE report files | Usually `reports/` at ONE root (configurable in .settings) |

---

## Common issues

- **Java/ONE not found** — Run from the directory that contains `one.sh`; ensure ONE is compiled.
- **Python module not found** — Use a venv and install dependencies: `pip install numpy pandas scipy matplotlib streamlit`.
- **Corpus path** — Use `--corpus corpus_v1` if you run from the repo root and `corpus_v1` is at `scenarios/corpus_v1`. Otherwise use the full path to the corpus directory.
- **output_metrics phase** — Needs ONE report files (e.g. `*_MessageStatsReport.txt`) in the reports directory; run scenarios first or set `--reports-dir` if reports are elsewhere.

---

## Next steps

- [Installation](Installation) — Step-by-step setup
- [Reproducibility](Reproducibility) — Regenerating analysis from scratch
- [Methodology](Methodology) — How features and correlation work  
- [Results overview](Results-overview) — Main results and figures  
- [Corpus overview](Corpus-overview) — Scenario families and design  
