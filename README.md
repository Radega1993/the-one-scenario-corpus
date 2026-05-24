# the-one-scenario-corpus

*(English. Spanish: [README.es.md](README.es.md).)*

**Scenario corpus and analysis pipeline** for the [The ONE](https://akeranen.github.io/the-one/) simulator (Opportunistic Network Environment). This project provides simulation configurations (`.settings`), tools to extract features, analyse correlations and validate scenario diversity, plus a dashboard to explore results. It targets **evaluating routing protocols in opportunistic networks** (DTN/OppNets) for theses and papers: a reproducible benchmark with documented scenarios and traffic profiles.

**Requirements:** Java and The ONE built (repo root); Python 3 with `numpy`, `pandas`, `scipy`, `matplotlib`, `streamlit` (e.g. project venv at repo root).

---

## Current paper-ready state

| Item | Value |
|------|--------|
| **Active corpus** | [`corpus_v2/`](corpus_v2/) |
| **Simulations** | **720** (= 60 base scenarios × 12 Traffic Profiles TP01–TP12) |
| **Base scenarios** | 60 (mobility reference in [`corpus_v1/`](corpus_v1/)) |
| **Traffic profiles** | 12 (TP01 Baseline … TP12 GroupToGroup) |
| **Status** | Main benchmark under **methodological freeze / review** |
| **Canonical results** | [analysis/reports/RESULTADOS_ACTUALES.md](analysis/reports/RESULTADOS_ACTUALES.md) |
| **Paper figures** | [analysis/figures/paper/](analysis/figures/paper/) |
| **Paper tables** | [analysis/figures/paper/tables/](analysis/figures/paper/tables/) |
| **Freeze checklist gate** | [analysis/reports/paper_freeze_checklist.md](analysis/reports/paper_freeze_checklist.md) |
| **Protocol KPI policy** | [analysis/reports/canonical/protocol_benchmark_kpi_policy.md](analysis/reports/canonical/protocol_benchmark_kpi_policy.md) |
| **Historical v1 dropped** | [`_archive/corpus_dropped_v1/`](_archive/corpus_dropped_v1/) (moved from root) |

**Diversity snapshot (720 scenarios, from frozen analysis):**

- **Core-23:** max \|r\| = 1.0; 11 325 pairs (4.4%) with \|r\| ≥ 0.7; ablation silhouette (Ward k=7) = **0.3451**
- **Full-46:** 8 356 pairs (3.2%) with \|r\| ≥ 0.7; silhouette = **0.2680**
- **Feature–feature (core):** one high pair remains: `mm_WDM ↔ mm_Bus = 0.9393`

There is **no `corpus_v3/`**; any v3 proposal lives only in [`_archive/`](_archive/) as historical material.

---

## Project structure

| Path | Role |
|------|------|
| [`corpus_v2/`](corpus_v2/) | **Active** benchmark — 720 `.settings`, [`manifest.csv`](corpus_v2/manifest.csv) |
| [`corpus_v1/`](corpus_v1/) | Historical mobility base — 60 `.settings` |
| [`corpus_dropped_v1/`](corpus_dropped_v1/) | Archived v1 scenarios removed for redundancy (10) |
| [`analysis/`](analysis/) | Pipeline, `data/`, `figures/`, `reports/`, dashboard |
| [`_archive/`](_archive/) | Historical artifacts (wiki backups, pilots, legacy v3 scripts) |
| [`.wiki-clone/`](.wiki-clone/) | Active **paper wiki** (EN, flat numbered pages `01-` … `14-`) |
| [`INVENTARIO.md`](INVENTARIO.md) | Full repository map (source vs generated) |
| [`internal/`](internal/) | Private thesis notes (gitignored) |

Corpus directories are **versioned** (`corpus_v1`, `corpus_v2`, …) so scripts can select `--corpus corpus_v2` without breaking older paths.

---

## Documentation

| Document | Purpose |
|----------|---------|
| [INVENTARIO.md](INVENTARIO.md) | Complete file map and archive layout |
| [analysis/SCRIPTS_INDEX.md](analysis/SCRIPTS_INDEX.md) | Script roles and **official paper pipeline** |
| [analysis/reports/RESULTADOS_ACTUALES.md](analysis/reports/RESULTADOS_ACTUALES.md) | Frozen diversity and ablation metrics |
| [analysis/figures/README.md](analysis/figures/README.md) | Figure catalogue (720 scenarios) |
| [analysis/docs/features_core_vs_extended.md](analysis/docs/features_core_vs_extended.md) | Why 23 core vs 46 extended features |
| [corpus_v2/README.md](corpus_v2/README.md) | Traffic profiles and benchmark design |

Pipeline details: [analysis/README.md](analysis/README.md). Full **.settings reference** (sections 1–15): [README.es.md](README.es.md) (Spanish).

---

## Source vs generated

| Type | Paths |
|------|--------|
| **Source (keep in git)** | `corpus_v2/`, `corpus_v1/`, `corpus_dropped_v1/`, `analysis/*.py`, `analysis/lib/`, `analysis/dashboard/`, `analysis/docs/`, overlay `*.txt`, `protocol_overlays/`, wiki in `.wiki-clone/` |
| **Generated (regenerable)** | `analysis/data/*.csv`, most of `analysis/reports/`, `analysis/figures/` (PNG/PDF) |
| **Simulation outputs (expensive)** | Repo-root `reports/` (`*MessageStatsReport.txt`, spatial CSVs, etc.) |

Regenerate analysis outputs with the [official pipeline](#official-pipeline) below.

---

## Official pipeline

Full step-by-step commands (simulation → outputs → features → figures → wiki): **[analysis/SCRIPTS_INDEX.md](analysis/SCRIPTS_INDEX.md)**.

**Quick start** (from repo root):

```bash
# 1. Run simulations (batch)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \
  --extra-settings scenarios/analysis/overlays/spatial_occupancy_reports_overrides.txt \
  --jobs 4

# 2. Analysis phases (outputs, features, correlation, paper package)
python3 scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase output_metrics
python3 scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase indirects
python3 scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase all
python3 scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase figures_paper
python3 scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase tables_paper

# 3. Spatial + message timing + TP validation
python3 scenarios/analysis/scripts/validation/analyze_spatial_occupancy.py \
  --manifest scenarios/corpus_v2/manifest.csv --reports-dir reports --corpus corpus_v2
python3 scenarios/analysis/analyze_message_creation_times.py
python3 scenarios/analysis/scripts/validation/validate_traffic_profiles.py

# 4. Aggregated figures
python3 scenarios/analysis/run_figures_aggregated.py --corpus corpus_v2
```

---

## Dashboard

Interactive exploration (corpus health, TP profiles, spatial heatmaps, raw reports):

```bash
streamlit run scenarios/analysis/dashboard.py
# or with venv:
./venv/bin/streamlit run scenarios/analysis/dashboard.py
```

---

## Configuration guide (.settings)

The long reference for all `.settings` options (Scenario, MovementModel, Groups, interfaces, Events, Reports, Routers, etc.) is in **[README.es.md](README.es.md)** (Spanish). Option names match The ONE simulator documentation.

---

## Author

**the-one-scenario-corpus** — scenario corpus and analysis for The ONE.  
**Author:** Raül de Arriba
