# Analysis reports (`scenarios/analysis/reports/`)

Markdown methodology and validation outputs for the **540-scenario** `corpus_v1` benchmark (+ 45 `base_scenarios` for mobility structure). Regenerate from `scenarios/analysis/data/` via scripts in `scenarios/analysis/scripts/` — do not hand-edit metrics.

## Quick reference

| Element | Path |
|---------|------|
| Frozen diversity metrics | [RESULTADOS_ACTUALES.md](RESULTADOS_ACTUALES.md) |
| Paper freeze gate | [paper_freeze_checklist.md](paper_freeze_checklist.md) |
| Map policy (540, 6 families) | [map_policy_migration_report.md](map_policy_migration_report.md) |
| Map pipeline | [map_preparation_pipeline.md](map_preparation_pipeline.md) |
| worldSize calibration | [spatial/world_size_occupancy_calibration.md](spatial/world_size_occupancy_calibration.md) |

## Directory layout

| Folder / file | Role |
|---------------|------|
| [`canonical/`](canonical/) | Paper KPI policies, traffic-profile analysis, benchmark validation |
| [`validation/`](validation/) | Regenerated audits (`settings_audit`, `scenario_diagnosis`, TP validation, …) |
| [`spatial/`](spatial/) | Occupancy methodology, useful simulation time, worldSize calibration |
| [`policies/`](policies/) | Simulation time policy |
| [`pipeline/`](pipeline/) | Outputs from `run_analysis.py` (features, correlation, clustering, …) |
| [`paper_gate/`](paper_gate/) | Figure/dashboard readiness |
| [`maps/`](maps/) | `map_assets_final_validation.md`, `route_semantic_policy.md` |
| `base_scenarios_validation.md` | Base scenario structural checks |

## Canonical reports (paper)

| Report | Topic |
|--------|-------|
| [canonical/traffic_profile_kpi_analysis.md](canonical/traffic_profile_kpi_analysis.md) | KPIs by TP01–TP12 |
| [canonical/protocol_benchmark_kpi_policy.md](canonical/protocol_benchmark_kpi_policy.md) | Protocol comparison metrics |
| [canonical/message_analysis_window_policy.md](canonical/message_analysis_window_policy.md) | Message analysis window |
| [canonical/spatial_vs_performance_analysis.md](canonical/spatial_vs_performance_analysis.md) | Spatial occupancy vs performance |
| [canonical/corpus_benchmark_validation.md](canonical/corpus_benchmark_validation.md) | Combined benchmark validation |

## Validation (regenerated)

| Report | Script |
|--------|--------|
| [validation/settings_audit.md](validation/settings_audit.md) | `audit_settings.py` |
| [validation/scenario_diagnosis.md](validation/scenario_diagnosis.md) | `diagnose_scenarios.py` |
| [validation/tp_validation_report.md](validation/tp_validation_report.md) | `validate_traffic_profiles.py` |
| [validation/message_creation_time_audit.md](validation/message_creation_time_audit.md) | `analyze_message_creation_times.py` |
| [validation/evaluation_metrics_review.md](validation/evaluation_metrics_review.md) | `build_wiki_research_reports.py` |
| [validation/current_results_review.md](validation/current_results_review.md) | `build_wiki_research_reports.py` |

## Spatial

| Report | Notes |
|--------|-------|
| [spatial/spatial_occupancy_report.md](spatial/spatial_occupancy_report.md) | Methodology |
| [spatial/spatial_occupancy_denominator_validation.md](spatial/spatial_occupancy_denominator_validation.md) | Road vs world coverage |
| [spatial/spatial_occupancy_analysis_summary.md](spatial/spatial_occupancy_analysis_summary.md) | Summary pointer |
| [spatial/useful_simulation_time_report.md](spatial/useful_simulation_time_report.md) | Useful simulation time |
| [spatial/world_size_occupancy_calibration.md](spatial/world_size_occupancy_calibration.md) | worldSize calibration (2026-05) |

## Maps

| Report | Notes |
|--------|-------|
| [maps/map_assets_final_validation.md](maps/map_assets_final_validation.md) | Consolidated map/route/POI validation |
| [maps/route_semantic_policy.md](maps/route_semantic_policy.md) | Semantic route file naming |

## Diversity

[diversity_validation_readiness.md](diversity_validation_readiness.md) — readiness gate for 540-scenario diversity freeze (regenerate after full analysis pipeline).

## Simulator vs analysis reports

| Path | Content |
|------|---------|
| `reports/` (repo root) | The ONE `MessageStatsReport`, spatial grids, etc. |
| `scenarios/analysis/reports/` | This tree — methodology and aggregated validation |

## Cleanup (2026-05)

Removed: per-map `*_final_decision`, `*_resimulation_plan`, `wiki_meta/`, `project/`, and other 720-era audit markdown. Historical detail lives in `scenarios/CHANGELOG.md` and `scenarios/_archive/`.
