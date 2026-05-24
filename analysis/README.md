# Scenario corpus analysis (The ONE)

*(English. Spanish: [README.es.md](README.es.md).)*

This directory contains the analysis pipeline for the scenario corpus: extraction of **stable, reportable features**, normalisation, correlations, figures and reports for the opportunistic routing protocol benchmark.

**Script index (roles and paper pipeline):** [SCRIPTS_INDEX.md](SCRIPTS_INDEX.md).

**Context:** active benchmark corpus is [../corpus_v2](../corpus_v2) (720 scenarios); base mobility reference is [../corpus_v1](../corpus_v1). The ONE configuration guide is in [../README.md](../README.md) (summary) and [../README.es.md](../README.es.md) (full .settings reference).

---

## Current paper-ready state

| Item | Value |
|------|--------|
| **Active corpus** | `corpus_v2` — 720 simulations (60 base × 12 TP) |
| **Status** | Main benchmark under methodological freeze / review |
| **Frozen results** | [reports/RESULTADOS_ACTUALES.md](reports/RESULTADOS_ACTUALES.md) |
| **Paper figures** | [figures/paper/main/](figures/paper/main/), [figures/paper/supplementary/](figures/paper/supplementary/) |
| **Paper tables** | [figures/paper/tables/](figures/paper/tables/) (ES/EN Markdown) |
| **Figure catalogue** | [figures/README.md](figures/README.md) |

**Diversity (720 scenarios):** core-23 — max \|r\| = 1.0, 11 325 pairs (4.4%) with \|r\| ≥ 0.7, ablation silhouette 0.3451; full-46 — 8 356 pairs (3.2%), silhouette 0.2680; feature–feature `mm_WDM ↔ mm_Bus = 0.9393`. Details in `RESULTADOS_ACTUALES.md`.

---

## Key documentation

| Document | Purpose |
|----------|---------|
| [../INVENTARIO.md](../INVENTARIO.md) | Full repo map (source vs generated) |
| [SCRIPTS_INDEX.md](SCRIPTS_INDEX.md) | Script roles and official paper pipeline |
| [reports/RESULTADOS_ACTUALES.md](reports/RESULTADOS_ACTUALES.md) | Frozen metrics |
| [figures/README.md](figures/README.md) | Figure catalogue |
| [docs/features_core_vs_extended.md](docs/features_core_vs_extended.md) | Core 23 vs extended 46 |
| [../corpus_v2/README.md](../corpus_v2/README.md) | Traffic profiles and benchmark design |

---

## Source vs generated (this directory)

| Type | Paths |
|------|--------|
| **Source** | `*.py`, `lib/`, `dashboard/`, `docs/`, overlay `*.txt`, `protocol_overlays/`, `data/realism_thresholds.yaml`, figure READMEs |
| **Generated** | `data/*.csv`, most of `reports/`, `figures/*.png` / `*.pdf` |
| **Upstream sim outputs** | Repo-root `reports/` (read by `output_metrics`, spatial, indirects) |

Regenerate with the [official pipeline](#official-pipeline) below.

---

## Official pipeline

Full commands (12 steps): **[SCRIPTS_INDEX.md](SCRIPTS_INDEX.md)**.

1. Simulation — `run_all_scenarios.py --corpus corpus_v2` + routing/contact + spatial overlays  
2. Output metrics — `run_analysis.py --phase output_metrics` (+ `indirects`)  
3. Features — `--phase features` → `normalize` → `correlation` → `feature_correlation` → `ablation`  
4. Spatial — `scripts/validation/analyze_spatial_occupancy.py`  
5. Message creation — `scripts/validation/analyze_message_creation_times.py`  
6. TP validation — `scripts/validation/validate_traffic_profiles.py`  
7. Figures — `--phase figures_paper` + `run_figures_aggregated.py`  
8. Tables — `--phase tables_paper`  
9. Wiki — `scripts/wiki/build_wiki_research_reports.py` → `scripts/wiki/populate_wiki_paper.py`

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
├── README.md / README.es.md / MENU.md
├── analysis_menu.py           # Interactive Spanish menu (submenu Paper/validación)
├── run_analysis.py            # Main pipeline by phase
├── run_all_scenarios.py       # Batch simulations (one.sh)
├── run_figures_aggregated.py
├── dashboard.py               # Streamlit entry
├── overlays/                  # --extra-settings presets (routing/contact, spatial, …)
├── examples/selection_example.txt
├── scripts/
│   ├── paper/                 # KPI policy, freeze checklist, figuras índice, …
│   ├── validation/            # TP validation, spatial, audit, diagnose, …
│   └── wiki/                  # populate_wiki_paper, build_wiki_research_reports
├── lib/                       # paths, traffic_profile_generator, report_paths, …
├── data/ figures/ reports/ docs/ dashboard/ protocol_overlays/
```

---

## Interactive menu (Spanish)

From the **repository root**, run:

```bash
python3 scenarios/analysis/analysis_menu.py
```

Full option map: **[MENU.md](MENU.md)**. The menu delegates to scripts via `subprocess` (Diego17/spatial overlays under `overlays/`). **corpus_v2 is frozen** — generation scripts were removed; TP definitions live in `lib/traffic_profile_generator.py`.

| Menu | Action |
|------|--------|
| **1–2** | Simulations (batch / selection / GUI) |
| **3** | `run_analysis.py` phases |
| **4** | Paper & validation submenu (4a–4n) |
| **5–7** | Useful time, message creation, spatial |
| **8** | Streamlit dashboard |
| **9** | Aggregated / paper figures |

---

## Features (summary)

**Current results (`corpus_v2`, 720 scenarios):** **46 extended features**; **23 core** for methodology/paper. See [reports/RESULTADOS_ACTUALES.md](reports/RESULTADOS_ACTUALES.md).

- **Core-23:** max \|r\| = 1.0; 11 325 pairs (4.4%) with \|r\| ≥ 0.7; ablation silhouette (Ward k=7) = 0.3451  
- **Full-46:** 8 356 pairs (3.2%) with \|r\| ≥ 0.7; silhouette = 0.2680  
- **Feature–feature (core):** `mm_WDM ↔ mm_Bus = 0.9393`  

**Why 23 core / why discarded:** [docs/features_core_vs_extended.md](docs/features_core_vs_extended.md), [docs/features_decision.md](docs/features_decision.md).

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

## Useful simulation time (corpus_v2)

```bash
python3 scenarios/analysis/compute_useful_simulation_time.py
```

→ `data/useful_simulation_time_metrics.csv`, `reports/useful_simulation_time_report.md`  
Parser: `lib/connectivity_timeline.py` (from `ConnectivityONEReport`).

---

## Spatial occupancy (optional)

Enable **NodePositionReport** (CSV `time,node_id,x,y`) and **SpatialOccupancyReport** (grid + coverage CSVs) with an overlay; do not edit corpus `.settings`. Chain after `routing_contact_reports_overrides.txt` so `Report.report1`–`report7` stay unchanged and `report8`–`report9` add the new reports:

```bash
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \
  --extra-settings scenarios/analysis/spatial_occupancy_reports_overrides.txt
```

Methodology and setting keys (`SpatialOccupancyReport.*`, `NodePositionReport.*`): [reports/spatial_occupancy_report.md](reports/spatial_occupancy_report.md).

Post-processing (heatmaps, merged metrics, family-level coverage curves):

```bash
python3 scenarios/analysis/scripts/validation/analyze_spatial_occupancy.py \
  --reports-dir reports \
  --manifest scenarios/corpus_v2/manifest.csv
```

Requires `numpy`, `pandas`, and `matplotlib` (e.g. `scenarios/analysis/.venv`). Heatmaps use **road geometry** from [`data/HelsinkiMedium/`](../data/HelsinkiMedium/) or [`data/Manhattan/`](../data/Manhattan/) (sim-aligned WKT) plus optional **GUI underlay** PNG (`GUI.UnderlayImage.fileName`, e.g. `data/helsinki_underlay.png` if present locally). Default figure layout: full world + zoom on visited cells, log color scale.

```bash
# Optional flags
scenarios/analysis/.venv/bin/python scenarios/analysis/scripts/validation/analyze_spatial_occupancy.py \
  --reports-dir reports --manifest scenarios/corpus_v2/manifest.csv \
  --heatmap-layout dual --families 01_urban
```

Writes `data/spatial_occupancy_metrics.csv` (includes `map_dataset`, `cells_visited_pct`), `figures/spatial_heatmaps/`, etc.

You can also run the same flow from the Spanish interactive menu: [analysis_menu.py](analysis_menu.py) → option **6**.

Use `--skip-heatmaps` to refresh `spatial_occupancy_metrics.csv` from existing grid CSVs only (faster).

---

## Corpus audit & v2 revision planning (corpus_v2)

Reproducible pipeline that audits all 720 `.settings`, cross-checks simulation metrics, assigns problem flags, and produces a **prioritized revision plan for corpus_v2 in-place** (no `corpus_v3/` folder, no automatic `.settings` edits).

**Order of execution** (from repo root; use `.venv` if system Python lacks dependencies):

```bash
PY=scenarios/analysis/.venv/bin/python

# 1. Settings audit → data/settings_audit.csv, reports/settings_audit.md
$PY scenarios/analysis/scripts/validation/audit_settings.py \
  --manifest scenarios/corpus_v2/manifest.csv

# 2. (Optional) Refresh spatial metrics from reports/*_spatial_occupancy_grid.csv
$PY scenarios/analysis/scripts/validation/analyze_spatial_occupancy.py \
  --manifest scenarios/corpus_v2/manifest.csv --reports-dir reports --skip-heatmaps

# 3. Diagnosis (joins output, indirect, spatial) → scenario_diagnosis.*
$PY scenarios/analysis/scripts/validation/diagnose_scenarios.py --reports-dir reports
```

Revision plan/apply scripts were removed after the v2 revision was applied; see `reports/project/corpus_v2_revision_changelog.md`.

**Primary outputs (revision):**

| Artifact | Path |
|----------|------|
| Prioritized table | `data/corpus_v2_revision_prioritized.csv` |
| Per-base summary | `data/corpus_v2_revision_summary.csv` |
| Revision plan (MD) | `reports/corpus_v2_revision_plan.md` |

**Audit / diagnosis outputs:**

| Artifact | Path |
|----------|------|
| Settings audit | `data/settings_audit.csv`, `reports/settings_audit.md` |
| Thresholds | `data/realism_thresholds.yaml` (rules archivadas: `_archive/reports/realism_rules.md`) |
| Diagnosis | `data/scenario_diagnosis.csv`, `reports/scenario_diagnosis.md` |

**Legacy (archived, do not use for rebuild):** `_archive/data/corpus_v3_plan.csv`, `_archive/reports/corpus_v3_*.md`, `_archive/scripts/recommend_corpus_v3.py`.

### Apply revision (historical)

`apply_corpus_v2_revision.py` and `build_corpus_v2_revision_plan.py` were removed (revision already applied). Changelog: `reports/project/corpus_v2_revision_changelog.md`.

`validate_traffic_profiles.py` may report TP05 mismatches on U4/U6 (`msgTtl=15` vs generator default 5) — intentional per revision plan.

Shared modules: `lib/settings_audit.py`, `lib/scenario_diagnosis.py`.

---

## Wiki rebuild (paper-oriented)

Backup of previous wiki: `scenarios/_archive/wiki/wiki_backup_20260520_133832/` (223 pages).

```bash
PY=scenarios/analysis/.venv/bin/python
# Phase 1: reports (audit, results, policies)
$PY scenarios/analysis/build_wiki_research_reports.py
# Phase 2: rebuild .wiki-clone pages (after backup)
$PY scenarios/analysis/populate_wiki_paper.py
```

Wiki root: `scenarios/.wiki-clone/Home.md` — legacy content under `_legacy_pre_paper_rebuild/`.

Summary: [`reports/wiki_rebuild_summary.md`](reports/wiki_rebuild_summary.md).

---

## Traffic profile validation (corpus_v2)

After regenerating `corpus_v2` or before phase-2 protocol runs:

```bash
python3 scenarios/analysis/scripts/validation/validate_traffic_profiles.py
```

Writes `reports/tp_validation_report.md` and `data/tp_validation_*.csv`. Methodology closure: [../internal/17-benchmark_methodology_closure.md](../internal/17-benchmark_methodology_closure.md).

---

## Run all simulations (generate reports)

To get all ONE reports (MessageStatsReport, ContactTimesReport, etc.) in `reports/`:

```bash
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2
# List only, no run:
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 --dry-run

# Force all reports needed for Diego17 real / indirects:
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt

# Same command using project venv:
./venv/bin/python scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt

# Parallel run (recommended for corpus_v2)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \
  --timeout 14400 --jobs 6

# One scenario with GUI (visual)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 --gui \
  --settings scenarios/corpus_v2/01_urban/U1_CBD_Commuting_HelsinkiMedium__TP01_Baseline.settings \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt

# Several scenarios by regex (batch)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 \
  --name-regex 'U2_SparseSuburb_Manhattan|U4_CongestionHotspot_Manhattan' \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt

# Explicit list (batch, two files)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 \
  --settings scenarios/corpus_v2/01_urban/U2_SparseSuburb_Manhattan__TP01_Baseline.settings \
  --settings scenarios/corpus_v2/01_urban/U4_CongestionHotspot_Manhattan__TP01_Baseline.settings

# Whole family (84 scenarios for 01_urban: 7 bases × 12 TP)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 --family 01_urban \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt

# All scenarios with traffic profile TP07 (BurstWindow)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 --tp TP07 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt

# Family + TP
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 \
  --family 01_urban --tp TP01 --tp TP05 --jobs 4

# Selection file (see scenarios/analysis/examples/selection_example.txt)
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 \
  --select-file scenarios/analysis/examples/selection_example.txt --dry-run
```

Requires Java and the ONE built (`one.sh` at repo root). Then run `run_analysis.py --phase output_metrics` to fill `data/output_metrics.csv` from those reports.

Interactive selection (GUI or batch): `analysis_menu.py` → option **2**. Selection file format: `family:`, `tp:`, `base:`, `regex:`, or direct `.settings` paths.

### Parallelization (`--jobs`)

- `run_all_scenarios.py` supports parallel execution with `--jobs N`.
- Start with `--jobs 4` or `--jobs 6`; increase only if CPU/RAM remain stable.
- For this workstation (`16` cores), a practical range is usually `--jobs 6..8`.
- Do **not** launch two full corpus runs at the same time over the same `reports/` directory.

---

## Run analysis

From repo root (or with paths adjusted):

```bash
# Features
python3 scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase features

# Features report (list features + settings not used)
python3 scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase features_report

# Normalise
python3 scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase normalize

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
python3 scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase all

# Same (venv)
./venv/bin/python scenarios/analysis/run_analysis.py --corpus corpus_v2 --phase all
```

Output paths are relative to `scenarios/analysis/`. Requires `numpy` and `pandas`.

### Interactive dashboard (corpus_v2)

Streamlit app focused on **corpus health**, **traffic profiles (TP01–TP12)**, **scenario explorer**, spatial heatmaps, and diagnosis — not only the classic `run_analysis.py` phases.

```bash
# from repo root (recommended: project venv)
./venv/bin/streamlit run scenarios/analysis/dashboard.py
# or: streamlit run scenarios/analysis/dashboard.py
# menu: analysis_menu.py → option 9
```

**Pages:** Resumen corpus · Explorador · KPIs benchmark · Perfiles TP · Ventana mensajes · Tiempo útil · Espacial · Diagnóstico · Protocolos · Detalle escenario · Figuras · Pipeline clásico · Reportes crudos.

**Sidebar filters:** family, scenario base, TP, map dataset, text search; ranges for `delivery_ratio`, `drop_ratio`, `final_coverage_pct`; `bench_validation_status` and `policy_status` (advanced).

**Useful CSV inputs** (under `scenarios/analysis/data/`): `manifest` from `scenarios/corpus_v2/manifest.csv`; joins include `output_metrics.csv`, `scenario_diagnosis.csv`, `settings_audit.csv`, `spatial_occupancy_metrics.csv`, `message_creation_time_summary.csv`, `message_analysis_window_policy.csv`, `useful_simulation_time_metrics.csv`, `corpus_v2_benchmark_validation.csv`, `traffic_profile_kpi_summary.csv`, `tp_validation_settings.csv`, `indirect_features_diego.csv`.

**Docs:** [`dashboard/README.md`](dashboard/README.md) · readiness: [`reports/dashboard_readiness_report.md`](reports/dashboard_readiness_report.md)

### Paper freeze gate

```bash
python3 scenarios/analysis/build_paper_freeze_checklist.py
python3 scenarios/analysis/build_protocol_benchmark_kpi_policy.py
python3 scenarios/analysis/scripts/paper/analyze_spatial_vs_performance.py
```

Canonical gate: [`reports/paper_freeze_checklist.md`](reports/paper_freeze_checklist.md) · protocol KPIs: [`reports/protocol_benchmark_kpi_policy.md`](reports/protocol_benchmark_kpi_policy.md)

**Package layout:** `dashboard/app.py`, `dashboard/data_loaders.py`, `dashboard/pages/*.py`; entrypoint `dashboard.py`.

Requires `streamlit`, `pandas`, and `altair` (see repo `requirements.txt`).
