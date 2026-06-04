# Analysis artifact producers

## Summary

- ACTIVE_CORE: 7 scripts
- ACTIVE_OPTIONAL: 22 scripts
- ACTIVE_SUPPORT: 20 scripts
- LEGACY: 2 scripts

## Producers table

| script_path | role | status | outputs(data/reports/figures) | notes |
|---|---|---|---|---|
| `analysis/analysis_menu.py` | utility | ACTIVE_OPTIONAL | corpus_benchmark_validation.csv|output_metrics.csv|paper_freeze_checklist.csv|scenario_diagnosis.csv|settings_audit.csv/corpus_benchmark_validation.md|inventory_update_report.md|message_analysis_window_policy.md|paper_figures_tables_readiness.md|paper_freeze_checklist.md|protocol_benchmark_kpi_policy.md|scenario_diagnosis.md|spatial_vs_performance_analysis.md|tp_validation_report.md|traffic_profile_kpi_analysis.md | mentions 720 |
| `analysis/dashboard/__init__.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/dashboard/app.py` | dashboard | ACTIVE_OPTIONAL | - | mentions 720 |
| `analysis/dashboard/components.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/dashboard/data_loaders.py` | dashboard | ACTIVE_OPTIONAL | - | mentions 720 |
| `analysis/dashboard/pages/__init__.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/dashboard/pages/analysis_pipeline.py` | dashboard | ACTIVE_OPTIONAL | - | mentions 720 |
| `analysis/dashboard/pages/benchmark_kpis.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/dashboard/pages/corpus_audit.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/dashboard/pages/figures_guide.py` | dashboard | ACTIVE_OPTIONAL | - | mentions 720 |
| `analysis/dashboard/pages/home.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/dashboard/pages/message_window.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/dashboard/pages/protocols.py` | dashboard | ACTIVE_OPTIONAL | protocol_comparison_placeholder.png | mentions 720 |
| `analysis/dashboard/pages/raw_reports.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/dashboard/pages/scenario_detail.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/dashboard/pages/scenario_explorer.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/dashboard/pages/spatial.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/dashboard/pages/traffic_profiles.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/dashboard/pages/useful_time.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/dashboard.py` | dashboard | ACTIVE_SUPPORT | - | - |
| `analysis/lib/__init__.py` | library | ACTIVE_CORE | - | - |
| `analysis/lib/benchmark_select.py` | library | ACTIVE_CORE | - | - |
| `analysis/lib/connectivity_timeline.py` | library | ACTIVE_CORE | - | - |
| `analysis/lib/map_context.py` | library | ACTIVE_CORE | - | - |
| `analysis/lib/paths.py` | library | ACTIVE_OPTIONAL | - | mentions corpus_v2 |
| `analysis/lib/report_paths.py` | library | ACTIVE_OPTIONAL | - | mentions corpus_v2 |
| `analysis/lib/scenario_diagnosis.py` | library | ACTIVE_CORE | scenario_diagnosis.csv | - |
| `analysis/lib/scenario_select.py` | library | ACTIVE_OPTIONAL | - | mentions corpus_v2 |
| `analysis/lib/settings_audit.py` | library | ACTIVE_CORE | - | - |
| `analysis/lib/spatial_occupancy_io.py` | library | ACTIVE_CORE | - | - |
| `analysis/lib/traffic_profile_generator.py` | library | ACTIVE_OPTIONAL | - | - |
| `analysis/run_all_scenarios.py` | simulation_runner | ACTIVE_OPTIONAL | - | - |
| `analysis/run_analysis.py` | main_analysis_pipeline | ACTIVE_OPTIONAL | ablation_metrics.csv|correlation_pearson.csv|features.csv|output_metrics.csv/RESULTADOS_ACTUALES.md|ablation_report.txt|correlation_report.txt|features_report.md|features_report.txt/heatmap_feature_feature_core.png|pca_by_family.png | mentions corpus_v2; mentions 720 |
| `analysis/run_figures_aggregated.py` | utility | ACTIVE_OPTIONAL | - | mentions 720 |
| `analysis/scripts/paper/analyze_spatial_vs_performance.py` | paper_artifacts | ACTIVE_SUPPORT | spatial_coverage_by_family_paper.png | - |
| `analysis/scripts/paper/analyze_traffic_profile_kpis.py` | paper_artifacts | ACTIVE_OPTIONAL | traffic_profile_kpi_summary.csv|traffic_profile_stats.csv/traffic_profile_kpi_analysis.md | mentions 720 |
| `analysis/scripts/paper/build_inventory_update_report.py` | paper_artifacts | ACTIVE_SUPPORT | output_metrics.csv | - |
| `analysis/scripts/paper/build_message_analysis_window_policy.py` | paper_artifacts | ACTIVE_OPTIONAL | message_analysis_window_by_tp.csv|message_analysis_window_policy.csv|message_creation_time_summary.csv|traffic_profile_windows.csv/message_analysis_window_policy.md/message_creation_time_boxplot_by_tp.png|message_creation_time_hist_by_tp.png | mentions 720 |
| `analysis/scripts/paper/build_paper_figures_tables_index.py` | paper_artifacts | ACTIVE_OPTIONAL | RESULTADOS_ACTUALES.md | mentions 720 |
| `analysis/scripts/paper/build_paper_freeze_checklist.py` | paper_artifacts | ACTIVE_OPTIONAL | paper_freeze_checklist.csv/paper_freeze_checklist.md | mentions 720 |
| `analysis/scripts/paper/build_protocol_benchmark_kpi_policy.py` | paper_artifacts | ACTIVE_OPTIONAL | protocol_benchmark_kpi_definitions.csv|traffic_profile_kpi_summary.csv | mentions 720 |
| `analysis/scripts/validation/analyze_message_creation_times.py` | validation | ACTIVE_OPTIONAL | message_creation_time_summary.csv/message_creation_time_audit.md/message_creation_time_boxplot_by_tp.png|message_creation_time_hist_by_tp.png | mentions 720 |
| `analysis/scripts/validation/analyze_spatial_occupancy.py` | validation | ACTIVE_SUPPORT | spatial_coverage_timeseries.csv|spatial_occupancy_metrics.csv/spatial_occupancy_analysis_summary.md/spatial_occupancy_curves_by_family.png | - |
| `analysis/scripts/validation/audit_settings.py` | validation | ACTIVE_SUPPORT | settings_audit.csv | - |
| `analysis/scripts/validation/compute_useful_simulation_time.py` | validation | ACTIVE_OPTIONAL | useful_simulation_time_metrics.csv/useful_simulation_time_report.md | mentions 720 |
| `analysis/scripts/validation/diagnose_scenarios.py` | validation | ACTIVE_SUPPORT | - | - |
| `analysis/scripts/validation/validate_corpus_benchmark.py` | validation | ACTIVE_OPTIONAL | corpus_benchmark_validation.csv|scenario_diagnosis.csv/corpus_benchmark_validation.md | mentions 720 |
| `analysis/scripts/validation/validate_traffic_profiles.py` | validation | ACTIVE_OPTIONAL | tp_validation_by_base.csv|tp_validation_settings.csv|tp_validation_summary.csv|traffic_profile_windows.csv/tp_validation_report.md | mentions corpus_v2 |
| `analysis/scripts/wiki/build_wiki_research_reports.py` | wiki_sync | LEGACY | simulation_time_policy.csv | mentions 720 |
| `analysis/scripts/wiki/populate_wiki_paper.py` | wiki_sync | LEGACY | corpus_v1_combined_manifest.csv|features.csv|features_normalized.csv|indirect_features_diego.csv|message_creation_time_summary.csv|output_metrics.csv|simulation_time_policy.csv|spatial_occupancy_metrics.csv|useful_simulation_time_metrics.csv/RESULTADOS_ACTUALES.md|ablation_report.txt|base_scenarios_validation.md|corpus_v2_revision_changelog.md|correlation_core23_report.txt|correlation_report.txt|evaluation_metrics_review.md|feature_feature_correlation_report.txt|features_report.md|message_analysis_window_policy.md|message_creation_time_audit.md|paper_phase1_action_plan.md|scenario_diagnosis.md|simulation_time_policy.md|spatial_occupancy_report.md|tp_validation_report.md | mentions corpus_v2; mentions 720 |
| `analysis/validate_base_scenarios.py` | validation | ACTIVE_SUPPORT | - | - |