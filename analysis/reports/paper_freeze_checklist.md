# Paper freeze checklist (corpus_v1)

Generated: 2026-05-28 07:46 UTC

**Scope:** paper with **multi-protocol routing comparison** on corpus_v1.
**Active corpus:** `corpus_v1` (not corpus_v3).

## Executive summary

- Simulations in manifest: **570** (expected 570)
- Settings files: **570**
- Output metrics null delivery: **0**
- Benchmark `error_probable`: **168**
- Benchmark `configuracion_sospechosa`: **106**
- Main figures lista/revisar: **8/8** lista, **0** revisar

## Status legend

| Status | Meaning |
|--------|---------|
| DONE | Complete, corpus_v1-aligned, traceable |
| PARTIAL | Exists but incomplete, stale, or needs human review |
| MISSING | Required artifact absent |
| BLOCKER | Blocks central paper claims |

## Corpus

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| CORP-01 | manifest.csv 720 rows + 720 .settings | **DONE** | manifest rows=570, settings=570 | — |
| CORP-02 | Factorial design 60 bases x 12 TP x 7 families documented | **DONE** | corpus_v1/README.md; corpus_overview_paper.png (lista) | — |
| CORP-03 | Benchmark splits frozen in main manifest | **PARTIAL** | manifest_revision.csv exists | Freeze benchmark_split into manifest or document split CSV as canonical |
| CORP-04 | Active docs reference corpus_v1 only (no corpus_v3 as active) | **DONE** | README.md and INVENTARIO.md declare corpus_v1 active; corpus_v3 only in _archive | — |

## Features

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| FEAT-01 | features.csv and features_core.csv 720 scenarios | **PARTIAL** | features=540, features_core=540 | — |
| FEAT-02 | Diversity metrics frozen n=720 | **DONE** | RESULTADOS_ACTUALES.md | — |
| FEAT-03 | Feature-feature redundancy acceptable | **PARTIAL** | Persistent high pair mm_WDM <-> mm_Bus = 0.9393; max |r|=1.0 between scenarios | Disclose in Methods; justify core-23 retention |
| FEAT-04 | Ablation 17/23/46 documented | **DONE** | table_ablation_metrics_en/es lista; ablation reports | — |

## Figures

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| FIG-01 | FIGURES_AND_TABLES_INDEX.md complete | **DONE** | 22 indexed items | — |
| FIG-02 | Main paper figures ready (lista) | **DONE** | lista=8/8, revisar=0 | Regenerate 7 main figures marked revisar |
| FIG-03 | Supplementary figures ready (lista) | **PARTIAL** | lista=4/5, revisar=1 | Regenerate supplementary figures marked revisar |
| FIG-04 | Protocol comparison figure (real data) | **MISSING** | Only protocol_comparison_placeholder.png | Run multi-protocol simulations and plot comparison |

## Kpis

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| KPI-01 | Per-TP KPIs under Epidemic | **DONE** | traffic_profile_kpi_summary.csv + traffic_profile_kpi_analysis.md | — |
| KPI-02 | Protocol benchmark KPI policy document | **DONE** | present | Write protocol_benchmark_kpi_policy.md |
| KPI-03 | protocol_benchmark_kpi_definitions.csv | **DONE** | present | Generate KPI definitions CSV for multi-protocol comparison |
| KPI-04 | Core-4 metrics agreed for cross-protocol comparison | **PARTIAL** | Defined in TP report; not validated across protocols | Formalize in protocol_benchmark_kpi_policy.md after runs |

## Limitations

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| LIM-01 | Limitations documented (maps WDM synthetic stress tiers) | **PARTIAL** | Dispersed in benchmark validation (106 sospechosa, 312 valido_extremo) | Consolidate into Methods/Limitations section |
| LIM-02 | Threats-to-validity section frozen | **MISSING** | No single limitations.md report | Write limitations/threats section or report |
| LIM-03 | Extreme scenarios excluded from main protocol ranking | **PARTIAL** | manifest_revision splits exist; not enforced in analysis outputs | Apply benchmark_split filter in protocol comparison tables |

## Message Windows

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| MSG-01 | Canonical message window policy document | **DONE** | message_analysis_window_policy.md (full window primary; optional 10% censor) | — |
| MSG-02 | Policy implemented in output_metrics extraction pipeline | **PARTIAL** | Canonical policy documented; output_metrics uses full MessageStatsReport aggregates | Optional: implement explicit window filter in extraction code for appendix |
| MSG-03 | Per-scenario policy CSV 720 rows | **PARTIAL** | message_analysis_window_policy.csv rows=540 | — |

## Outputs

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| OUT-01 | output_metrics.csv complete 720 rows | **PARTIAL** | rows=540; null delivery=0 | — |
| OUT-02 | ONE reports (MessageStats Connectivity spatial grid) | **PARTIAL** | Repo reports/ not versioned; 168 scenarios incomplete | Re-simulate incomplete scenarios; archive report paths in manifest |
| OUT-03 | Auxiliary outputs (indirect useful time) | **DONE** | useful_simulation_time_metrics=True; indirect_features=True | — |

## Reproducibility

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| REP-01 | Official pipeline documented (SCRIPTS_INDEX) | **DONE** | analysis/SCRIPTS_INDEX.md 12-step pipeline | — |
| REP-02 | Dashboard for paper exploration | **DONE** | dashboard_readiness_report.md | — |
| REP-03 | One-command regeneration figures and tables | **PARTIAL** | Commands in index; 1 figures still revisar | Run build_paper_figures_tables_index.py after regen |
| REP-04 | Simulation outputs (reports/) reproducible from manifest | **PARTIAL** | reports/ at repo root not fully versioned; re-sim cost high | Document exact one.sh invocations per scenario batch |

## Settings

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| SET-01 | Settings audit for all 720 scenarios | **DONE** | settings_audit.csv present | — |
| SET-02 | Traffic Profile settings validation (TP01-TP12) | **PARTIAL** | tp_validation_settings.csv; KPI summary: validated=0, partial=0, blocked=12 | Resolve TP03/TP11 blocked (S1 missing outputs) |
| SET-03 | P0/P1 map worldSize WDM issues resolved or excluded | **PARTIAL** | bench validation: pendiente_revision=1, configuracion_sospechosa=106 | Formalize exclusion in benchmark_split main tier |

## Simulations

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| SIM-01 | ONE batch Epidemic complete 720/720 | **PARTIAL** | output_metrics rows=540; null delivery_ratio=0; error_probable=168 | Re-simulate S1_StrongCommunities TP03 and TP11 |
| SIM-02 | Multi-protocol simulations (PRoPHET MaxProp etc.) | **MISSING** | Wiki 12-Benchmark-Protocol-Comparison: no runs; protocol_comparison_placeholder only | Run batch with analysis/protocol_overlays/ on main split |
| SIM-03 | Batch reproducibility documented (commands seeds) | **PARTIAL** | SCRIPTS_INDEX covers Epidemic; no executed multi-protocol runbook | Document and run multi-protocol batch before writing Results |

## Spatial Occupancy

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| SPAT-01 | spatial_occupancy_metrics.csv 720 rows | **PARTIAL** | rows=720 | — |
| SPAT-02 | Spatial heatmaps 720 scenarios | **PARTIAL** | PNG count=720 | — |
| SPAT-03 | Spatial vs performance analysis report | **DONE** | spatial_vs_performance_analysis.md present | Write spatial_vs_performance_analysis.md linking coverage to delivery |
| SPAT-04 | Paper figure spatial_coverage_by_family_paper | **PARTIAL** | Indexed status revisar; summary stale=False | Regenerate figure; refresh spatial_occupancy_analysis_summary.md |

## Tables

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| TAB-01 | English paper tables (diversity ablation families features) | **DONE** | tables lista=9/9 | — |
| TAB-02 | Spanish draft tables | **DONE** | ES tables marked lista in index | — |
| TAB-03 | Multi-protocol results tables | **MISSING** | No protocol comparison result tables | Generate after multi-protocol batch |

## Traffic Profiles

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| TP-01 | 12 Traffic Profiles defined and experimentally validated | **PARTIAL** | validated=0, partial=0, blocked=12 | Unblock TP03/TP11 after re-simulation |
| TP-02 | Traffic Profile KPI analysis report | **DONE** | traffic_profile_kpi_analysis.md | — |
| TP-03 | Stress/directional/control tiers in protocol comparison pipeline | **PARTIAL** | Splits in manifest_revision.csv; not wired to multi-protocol runs | Integrate tiers when running protocol comparison |

## Wiki

| ID | Item | Status | Evidence | Action |
|----|------|--------|----------|--------|
| WIKI-01 | Paper wiki rebuild pages 01-14 | **PARTIAL** | .wiki-clone present; key pages draft status | — |
| WIKI-02 | Wiki aligned with canonical analysis reports | **DONE** | No drift detected on message window | Update 11-Message-Analysis-Window.md to match canonical policy |
| WIKI-03 | Formal freeze checklist in analysis/reports | **DONE** | This report (paper_freeze_checklist.md) supersedes informal wiki checklist | — |

## Critical blockers (writing gate)

- **SIM-02** (MISSING): Multi-protocol simulations (PRoPHET MaxProp etc.) — Wiki 12-Benchmark-Protocol-Comparison: no runs; protocol_comparison_placeholder only
- **FIG-04** (MISSING): Protocol comparison figure (real data) — Only protocol_comparison_placeholder.png
- **TAB-03** (MISSING): Multi-protocol results tables — No protocol comparison result tables

## Block summary

| Block | DONE | PARTIAL | MISSING | BLOCKER |
|-------|-----:|--------:|--------:|--------:|
| corpus | 3 | 1 | 0 | 0 |
| features | 2 | 2 | 0 | 0 |
| figures | 2 | 1 | 1 | 0 |
| kpis | 3 | 1 | 0 | 0 |
| limitations | 0 | 2 | 1 | 0 |
| message_windows | 1 | 2 | 0 | 0 |
| outputs | 1 | 2 | 0 | 0 |
| reproducibility | 2 | 2 | 0 | 0 |
| settings | 1 | 2 | 0 | 0 |
| simulations | 0 | 2 | 1 | 0 |
| spatial_occupancy | 1 | 3 | 0 | 0 |
| tables | 2 | 0 | 1 | 0 |
| traffic_profiles | 1 | 2 | 0 | 0 |
| wiki | 2 | 1 | 0 | 0 |

## Minimum path to READY_FOR_WRITING

1. Complete re-simulation of any missing Epidemic outputs (e.g. S1 TP03 if still null).
2. Run multi-protocol batch on `manifest_revision.csv` main split with `protocol_overlays/`.
3. Regenerate `output_metrics.csv` per protocol; build comparison figures/tables.
4. Re-run `build_paper_freeze_checklist.py`.

## Final recommendation

### **READY_WITH_MINOR_FIXES**

Core corpus documentation and Epidemic baseline are in place.
Address remaining PARTIAL items and complete multi-protocol runs before Results claims.


## Regeneration

```bash
scenarios/analysis/.venv/bin/python scenarios/analysis/build_paper_freeze_checklist.py
# or from scenarios/analysis:
python build_paper_freeze_checklist.py
```

Machine-readable: [`data/paper_freeze_checklist.csv`](../data/paper_freeze_checklist.csv).
