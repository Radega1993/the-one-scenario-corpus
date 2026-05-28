# Data inventory final

## Summary

- ARCHIVE_LEGACY: 3
- KEEP_CANONICAL: 11
- KEEP_SUPPORT: 31
- REGENERATE_REQUIRED: 15

## Inventory

| file | rows | detected_scope | status | action | notes |
|---|---:|---|---|---|---|
| `analysis/data/ablation_metrics.csv` | 3 | n/a | REGENERATE_REQUIRED | regenerate ablation in current env | - |
| `analysis/data/analysis_artifact_producers.csv` | 51 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/base_scenarios_map_migration.csv` | 45 | 45_base_like | KEEP_SUPPORT | keep | - |
| `analysis/data/base_scenarios_validation.csv` | 45 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/benchmark_definition.csv` | 720 | legacy_720_like | REGENERATE_REQUIRED | regenerate_for_570_or_archive_if_unused | - |
| `analysis/data/cluster_assignments.csv` | 720 | legacy_720_like | REGENERATE_REQUIRED | regenerate_for_570_or_archive_if_unused | - |
| `analysis/data/cluster_assignments_core23.csv` | 720 | legacy_720_like | REGENERATE_REQUIRED | regenerate_for_570_or_archive_if_unused | - |
| `analysis/data/corpus_benchmark_validation.csv` | 570 | 570_combined | KEEP_SUPPORT | keep | - |
| `analysis/data/corpus_v1_combined_manifest.csv` | 570 | 570_combined | KEEP_CANONICAL | keep | - |
| `analysis/data/corpus_v2_benchmark_validation.csv` | 720 | legacy_720_like | ARCHIVE_LEGACY | archive | - |
| `analysis/data/corpus_v2_revision_prioritized.csv` | 996 | n/a | ARCHIVE_LEGACY | archive | - |
| `analysis/data/corpus_v2_revision_summary.csv` | 60 | n/a | ARCHIVE_LEGACY | archive | - |
| `analysis/data/correlation_pearson.csv` | 570 | n/a | KEEP_CANONICAL | keep | - |
| `analysis/data/correlation_pearson_core23.csv` | 570 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/correlation_pearson_outputs.csv` | 720 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/correlation_pearson_pvalues.csv` | 570 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/correlation_spearman.csv` | 570 | n/a | KEEP_CANONICAL | keep | - |
| `analysis/data/correlation_spearman_outputs.csv` | 720 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/distance_cosine.csv` | 570 | n/a | KEEP_CANONICAL | keep | - |
| `analysis/data/distance_cosine_core23.csv` | 570 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/distance_cosine_outputs.csv` | 720 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/distance_euclidean.csv` | 570 | n/a | KEEP_CANONICAL | keep | - |
| `analysis/data/distance_euclidean_outputs.csv` | 720 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/feature_decision_deltas.csv` | 46 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/feature_feature_correlation_core.csv` | 23 | n/a | KEEP_CANONICAL | keep | - |
| `analysis/data/features.csv` | 570 | n/a | KEEP_CANONICAL | keep | - |
| `analysis/data/features_core.csv` | 570 | n/a | KEEP_CANONICAL | keep | - |
| `analysis/data/features_normalized.csv` | 570 | n/a | KEEP_CANONICAL | keep | - |
| `analysis/data/features_reduced.csv` | 570 | n/a | KEEP_CANONICAL | keep | - |
| `analysis/data/indirect_features_diego.csv` | 570 | 570_combined | KEEP_SUPPORT | keep | - |
| `analysis/data/map_inventory.csv` | 7 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/map_policy_validation.csv` | 720 | legacy_720_like | REGENERATE_REQUIRED | regenerate_for_570_or_archive_if_unused | - |
| `analysis/data/message_analysis_window_by_tp.csv` | 12 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/message_analysis_window_policy.csv` | 720 | legacy_720_like | REGENERATE_REQUIRED | regenerate_for_570_or_archive_if_unused | - |
| `analysis/data/message_creation_time_summary.csv` | 720 | legacy_720_like | REGENERATE_REQUIRED | regenerate_for_570_or_archive_if_unused | - |
| `analysis/data/normalization_params.csv` | 46 | n/a | KEEP_CANONICAL | keep | - |
| `analysis/data/output_metrics.csv` | 566 | partial_566 | REGENERATE_REQUIRED | refresh missing simulation outputs | rows=566, expected around 570 combined |
| `analysis/data/output_metrics.csv.example` |  | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/output_metrics_normalized.csv` | 720 | legacy_720_like | REGENERATE_REQUIRED | regenerate_for_570_or_archive_if_unused | - |
| `analysis/data/paper_freeze_checklist.csv` | 48 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/protocol_benchmark_kpi_definitions.csv` | 48 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/realism_thresholds.yaml` |  | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/reports_reorganization_manifest.csv` | 46 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/scenario_diagnosis.csv` | 720 | legacy_720_like | REGENERATE_REQUIRED | regenerate_for_570_or_archive_if_unused | - |
| `analysis/data/scenario_list.txt` |  | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/settings_audit.csv` | 720 | legacy_720_like | REGENERATE_REQUIRED | regenerate_for_570_or_archive_if_unused | - |
| `analysis/data/simulation_completion_status.csv` | 570 | 570_combined | KEEP_SUPPORT | keep | - |
| `analysis/data/simulation_pending.txt` |  | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/simulation_pending_not_started.txt` |  | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/simulation_status_temp.csv` | 570 | 570_combined | KEEP_SUPPORT | keep | - |
| `analysis/data/simulation_time_policy.csv` | 720 | legacy_720_like | REGENERATE_REQUIRED | regenerate_for_570_or_archive_if_unused | - |
| `analysis/data/spatial_coverage_timeseries.csv` | 99348 | legacy_720_like | REGENERATE_REQUIRED | regenerate_for_570_or_archive_if_unused | - |
| `analysis/data/spatial_occupancy_metrics.csv` | 720 | legacy_720_like | REGENERATE_REQUIRED | regenerate_for_570_or_archive_if_unused | - |
| `analysis/data/tp_validation_by_base.csv` | 60 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/tp_validation_settings.csv` | 570 | 570_combined | KEEP_SUPPORT | keep | - |
| `analysis/data/tp_validation_summary.csv` | 24 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/traffic_profile_kpi_summary.csv` | 12 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/traffic_profile_stats.csv` | 12 | n/a | KEEP_SUPPORT | keep | - |
| `analysis/data/traffic_profile_windows.csv` | 570 | 570_combined | KEEP_SUPPORT | keep | - |
| `analysis/data/useful_simulation_time_metrics.csv` | 720 | legacy_720_like | REGENERATE_REQUIRED | regenerate_for_570_or_archive_if_unused | - |
