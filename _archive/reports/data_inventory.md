# Data and artifact inventory

Generated: 2026-05-20 11:40 UTC

## Analysis CSV (`scenarios/analysis/data/`)

| File | Rows (approx) | Role |
|------|-------------:|------|
| `ablation_metrics.csv` | 3 | Supporting analysis |
| `cluster_assignments.csv` | 720 | Supporting analysis |
| `cluster_assignments_core23.csv` | 720 | Supporting analysis |
| `corpus_v2_revision_prioritized.csv` | 996 | Supporting analysis |
| `corpus_v2_revision_summary.csv` | 60 | Per-base revision actions |
| `corpus_v3_plan.csv` | 720 | Supporting analysis |
| `correlation_pearson.csv` | 720 | Supporting analysis |
| `correlation_pearson_core23.csv` | 720 | Supporting analysis |
| `correlation_pearson_outputs.csv` | 63 | Supporting analysis |
| `correlation_pearson_pvalues.csv` | 720 | Supporting analysis |
| `correlation_spearman.csv` | 720 | Supporting analysis |
| `correlation_spearman_outputs.csv` | 63 | Supporting analysis |
| `distance_cosine.csv` | 720 | Supporting analysis |
| `distance_cosine_core23.csv` | 720 | Supporting analysis |
| `distance_cosine_outputs.csv` | 63 | Supporting analysis |
| `distance_euclidean.csv` | 720 | Supporting analysis |
| `distance_euclidean_outputs.csv` | 63 | Supporting analysis |
| `feature_decision_deltas.csv` | 46 | Supporting analysis |
| `feature_feature_correlation_core.csv` | 23 | Supporting analysis |
| `features.csv` | 720 | Supporting analysis |
| `features_core.csv` | 720 | Supporting analysis |
| `features_normalized.csv` | 720 | Supporting analysis |
| `features_reduced.csv` | 720 | Supporting analysis |
| `indirect_features_diego.csv` | 720 | Connectivity indirect features |
| `map_profile_plan.csv` | 10 | Supporting analysis |
| `message_creation_time_summary.csv` | 720 | Supporting analysis |
| `normalization_params.csv` | 46 | Supporting analysis |
| `output_metrics.csv` | 720 | Primary routing outcomes (delivery, latency, overhead, drops) |
| `output_metrics.csv.example` | — | Supporting analysis |
| `output_metrics_normalized.csv` | 63 | Supporting analysis |
| `realism_thresholds.yaml` | — | Supporting analysis |
| `scenario_diagnosis.csv` | 720 | Problem flags cross-audit |
| `scenario_list.txt` | — | Supporting analysis |
| `settings_audit.csv` | 720 | Parsed .settings features |
| `spatial_coverage_timeseries.csv` | 14210 | Supporting analysis |
| `spatial_occupancy_metrics.csv` | 98 | Grid spatial coverage (partial) |
| `tp_validation_by_base.csv` | 60 | Supporting analysis |
| `tp_validation_settings.csv` | 720 | Supporting analysis |
| `tp_validation_summary.csv` | 24 | Supporting analysis |
| `traffic_profile_windows.csv` | 720 | Supporting analysis |
| `useful_simulation_time_metrics.csv` | 720 | Useful simulation time from connectivity |

## Reports (`scenarios/analysis/reports/`)

Markdown reports: **27**

## Figures

- Spatial heatmaps: **98** PNG under `figures/spatial_heatmaps/`

## Corpus

- `corpus_v2` settings: **720**
- ONE reports in `reports/`: **806** MessageStats (approx)

## Known gaps

- Spatial occupancy: **~99/720** scenarios in `spatial_occupancy_metrics.csv`
- Simulation metrics may be **pre–corpus_v2 revision** until re-run (see `corpus_v2_revision_changelog.md`)
- Wiki backup: `wiki_backup_20260520_133832/`
