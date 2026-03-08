# the-one-scenario-corpus

*(English. Spanish: [README.es.md](README.es.md).)*

**Scenario corpus and analysis pipeline** for the [The ONE](https://akeranen.github.io/the-one/) simulator (Opportunistic Network Environment). This project provides simulation configurations (`.settings`), tools to extract features, analyse correlations and check that scenarios are not redundant, and a dashboard to visualise results. It is intended for **evaluating routing protocols in opportunistic networks** (DTN/OppNets) for theses or papers: a reproducible benchmark with varied, documented scenarios.

| Content | Description |
|---------|-------------|
| **corpus_v1/** | 70 `.settings` scenarios by family (urban, campus, vehicles, rural, disaster, social, traffic). |
| **analysis/** | Feature extraction, correlation, output metrics, figures and [interactive dashboard](analysis/README.md). |
| **ROADMAP.md** / **ROADMAP.es.md** | Next steps: bilingual docs, GitHub Wiki; diversity criteria (|r| < 0.7, cos_dist). Spanish: [ROADMAP.es.md](ROADMAP.es.md). |

### Why names like `corpus_v1`

The corpus directory is named **`corpus_v1`** (not just `corpus`) so the **scenario set can be versioned** without breaking scripts or paths: if a second corpus is defined later (e.g. `corpus_v2` with fewer scenarios or another taxonomy), `corpus_v1` stays unchanged and commands can use `--corpus corpus_v1` or `--corpus corpus_v2`. The same idea applies to scenario names (U1, D2, T10…) and data files (e.g. `output_metrics.csv.example`): a version suffix or prefix helps with future iterations.

**Typical flow:** run simulations → generate reports in `reports/` → analysis (`run_analysis.py`) → view in the dashboard.

**Requirements:** Java and the ONE built (repo root), Python 3 with `numpy`, `pandas`, `scipy`, `matplotlib`, `streamlit` (e.g. project venv).

**Quick commands** (from repo root):

```bash
# Run all corpus simulations (batch, no GUI)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1

# Full analysis (features → correlation → figures → output_metrics)
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase all
python3 scenarios/analysis/run_analysis.py --phase outputs

# Interactive dashboard
streamlit run scenarios/analysis/dashboard.py
```

Phase details and options: [analysis/README.md](analysis/README.md). Full **.settings configuration reference** (sections 1–15) and detailed analysis/dashboard description: [README.es.md](README.es.md) (Spanish).

---

## Configuration guide (.settings)

The long reference for all `.settings` options (Scenario, MovementModel, Groups, interfaces, Events, Reports, Routers, etc.) and the minimal scenario example is in **[README.es.md](README.es.md)** (Spanish). An English translation of the guide can be added later; the option names and structure are the same in the ONE simulator.

---

## Corpus analysis and dashboard

Analysis (feature extraction, correlation between scenarios, validation on outputs) is done with the **pipeline in `scenarios/analysis/`**:

- **Main script:** `scenarios/analysis/run_analysis.py`, run by phase: `features` → `normalize` → `correlation` → `figures` → `output_metrics` → `outputs`. See [analysis/README.md](analysis/README.md) for the full phase list and options.
- **Outputs:** `analysis/data/` (feature CSV, normalised, correlation/distance matrices, `output_metrics.csv`), `analysis/figures/` (heatmaps, histograms, scatter), `analysis/reports/` (text reports).
- **Benchmark criterion:** |r| < 0.7 between scenario vectors (parameters or outputs); FDR/Bonferroni correction for multiple comparisons.

**Interactive dashboard:** to view everything in one place (summary, results by phase, per-scenario detail, compare scenarios):

```bash
streamlit run scenarios/analysis/dashboard.py   # from repo root
```

Requires `streamlit` and `pandas` (and analysis dependencies in the project venv).

---

## Author

<<<<<<< HEAD
**the-one-scenario-corpus** — corpus y análisis de escenarios para The ONE.

- **Autor:** Raül de Arriba
=======
**the-one-scenario-corpus** — scenario corpus and analysis for The ONE.  
**Author:** Raül de Arriba
>>>>>>> 39337bd (docs(scenarios): bilingual README/ROADMAP, drop checklist, 70 scenarios)
