# the-one-scenario-corpus

*(English. Spanish: [README.es.md](README.es.md).)*

**Scenario corpus and analysis pipeline** for the [The ONE](https://akeranen.github.io/the-one/) simulator (Opportunistic Network Environment). This project provides simulation configurations (`.settings`), tools to extract features, analyse correlations and validate scenario diversity, plus a dashboard to explore results. It targets **evaluating routing protocols in opportunistic networks** (DTN/OppNets) for theses and papers: a reproducible benchmark with documented scenarios and traffic profiles.

**Requirements:** Java and The ONE built (repo root); Python 3 with `numpy`, `pandas`, `scipy`, `matplotlib`, `streamlit` (e.g. project venv at repo root).

---

## Current paper-ready state

| Item | Value |
|------|--------|
| **Paper benchmark (`--corpus corpus_v1`)** | [`corpus_v1/`](corpus_v1/) (540) + [`stress_controls/`](stress_controls/) (30) = **570** simulations |
| **Structural bases (no TP)** | [`base_scenarios/`](base_scenarios/) — 45 scenarios, families `01_urban` … `06_social` |
| **Traffic profiles** | 12 definitions (TP01–TP12); active assignments per `benchmark_definition.csv` |
| **Status** | Main benchmark under **methodological freeze / review** |
| **Canonical results** | [analysis/reports/RESULTADOS_ACTUALES.md](analysis/reports/RESULTADOS_ACTUALES.md) |
| **Paper figures** | [analysis/figures/paper/](analysis/figures/paper/) |
| **Paper tables** | [analysis/figures/paper/tables/](analysis/figures/paper/tables/) |
| **Freeze checklist gate** | [analysis/reports/paper_freeze_checklist.md](analysis/reports/paper_freeze_checklist.md) |
| **Protocol KPI policy** | [analysis/reports/canonical/protocol_benchmark_kpi_policy.md](analysis/reports/canonical/protocol_benchmark_kpi_policy.md) |
| **Legacy mobility archive** | [`_archive/legacy_corpus_v1_pre_rename/`](_archive/legacy_corpus_v1_pre_rename/) |
| **Historical v1 dropped** | [`_archive/corpus_dropped_v1/`](_archive/corpus_dropped_v1/) |

**Diversity validation freeze (540 scenarios, `corpus_v1` only, no stress — canonical):**

| Space | Pairs \|r\| ≥ 0.7 | % | Silhouette (Ward k=7) |
|-------|------------------:|--:|----------------------:|
| Reduced-17 | 7425 | 5.1% | 0.3355 |
| **Core-23** | 5029 | 3.5% | 0.3045 |
| Full-46 | 3378 | 2.3% | 0.2354 |

Feature–feature (core): `mm_WDM ↔ mm_Bus = 0.9354`. Full tables: [RESULTADOS_ACTUALES.md](analysis/reports/RESULTADOS_ACTUALES.md). Readiness gate: [diversity_validation_readiness.md](analysis/reports/diversity_validation_readiness.md).

The **570** combined benchmark (540 + 30 stress) is separate from this diversity freeze; see routing/output metrics when comparing protocols.

See [CHANGELOG.md](CHANGELOG.md) for the 2026-05-27 nomenclature reorganization (`corpus_v2` → `corpus_v1` + `stress_controls/` + `base_scenarios/`).

---

## Project structure

| Path | Role |
|------|------|
| [`base_scenarios/`](base_scenarios/) | Structural mobility bases (45 `.settings`, no `__TP`) |
| [`corpus_v1/`](corpus_v1/) | Environmental benchmark with Traffic Profiles (540 `.settings`) |
| [`stress_controls/`](stress_controls/) | Stress/control laboratory separated from main corpus (30 `.settings`) |
| [`corpus_dropped_v1/`](corpus_dropped_v1/) | Archived v1 scenarios removed for redundancy (10) |
| [`analysis/`](analysis/) | Pipeline, `data/`, `figures/`, `reports/`, dashboard |
| [`_archive/`](_archive/) | Backups, legacy corpora, historical artifacts |
| [`.wiki-clone/`](.wiki-clone/) | Active **paper wiki** (EN, flat numbered pages `01-` … `15-`) |
| [`INVENTARIO.md`](INVENTARIO.md) | Full repository map (source vs generated) |
| [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) | Commands to regenerate corpora, manifests, analysis |
| [`internal/`](internal/) | Private thesis notes (gitignored) |

**Simulation:** `--corpus corpus_v1` → 540 environmental runs; use `--corpus stress_controls` for the 30 stress/control runs (or `--benchmark all` to merge both in one batch).

**Analysis:** `--corpus corpus_v1` in `run_analysis.py` includes stress for the full paper set (570). The CLI alias `corpus_v2` is deprecated.

---

## Documentation

| Document | Purpose |
|----------|---------|
| [INVENTARIO.md](INVENTARIO.md) | Complete file map and archive layout |
| [analysis/SCRIPTS_INDEX.md](analysis/SCRIPTS_INDEX.md) | Script roles and **official paper pipeline** |
| [analysis/reports/RESULTADOS_ACTUALES.md](analysis/reports/RESULTADOS_ACTUALES.md) | Frozen diversity and ablation metrics |
| [analysis/figures/README.md](analysis/figures/README.md) | Figure catalogue (diversity scope n=540) |
| [analysis/docs/features_core_vs_extended.md](analysis/docs/features_core_vs_extended.md) | Why 23 core vs 46 extended features |
| [corpus_v1/README.md](corpus_v1/README.md) | Traffic profiles and benchmark design |

Pipeline details: [analysis/README.md](analysis/README.md). Full **.settings reference** (sections 1–15): [README.es.md](README.es.md) (Spanish).

---

## Source vs generated

| Type | Paths |
|------|--------|
| **Source (keep in git)** | `corpus_v1/`, `corpus_v1/`, `corpus_dropped_v1/`, `analysis/*.py`, `analysis/lib/`, `analysis/dashboard/`, `analysis/docs/`, overlay `*.txt`, `protocol_overlays/`, wiki in `.wiki-clone/` |
| **Generated (regenerable)** | `analysis/data/*.csv`, most of `analysis/reports/`, `analysis/figures/` (PNG/PDF) |
| **Simulation outputs (expensive)** | Repo-root `reports/` (`*MessageStatsReport.txt`, spatial CSVs, etc.) |

Regenerate analysis outputs with the [official pipeline](#official-pipeline) below.

---

## Official pipeline

Full step-by-step commands (simulation → outputs → features → figures → wiki): **[analysis/SCRIPTS_INDEX.md](analysis/SCRIPTS_INDEX.md)**.

**Quick start** (from repo root):

```bash
# 1. Run simulations (batch)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \
  --extra-settings scenarios/analysis/overlays/spatial_occupancy_reports_overrides.txt \
  --jobs 4

# 2. Analysis phases (outputs, features, correlation, paper package)
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase output_metrics
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase indirects
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase all
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase figures_paper
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase tables_paper

# 3. Spatial + message timing + TP validation
python3 scenarios/analysis/scripts/validation/analyze_spatial_occupancy.py \
  --manifest scenarios/corpus_v1/manifest.csv --reports-dir reports --corpus corpus_v1
python3 scenarios/analysis/analyze_message_creation_times.py
python3 scenarios/analysis/scripts/validation/validate_traffic_profiles.py

# 4. Aggregated figures
python3 scenarios/analysis/run_figures_aggregated.py --corpus corpus_v1
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
