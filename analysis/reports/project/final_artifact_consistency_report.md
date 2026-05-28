# Final artifact consistency report

| check_id | check_name | expected | observed | status | severity | recommended_fix |
|---|---|---|---|---|---|---|
| C001 | base_scenarios_count | 45 | 45 | PASS | BLOCKER | regenerate base_scenarios |
| C002 | corpus_v1_count | 540 | 540 | PASS | BLOCKER | verify corpus_v1 split |
| C003 | stress_controls_count | 30 | 30 | PASS | BLOCKER | verify stress_controls flattening |
| C004 | combined_manifest_rows | 570 | 570 | PASS | BLOCKER | rebuild combined manifest |
| C005 | output_metrics_rows | ~570 | 566 | WARN | MAJOR | rerun output_metrics for missing reports |
| C006 | features_rows | 570 | 570 | PASS | MAJOR | rerun features phase |
| C007 | spatial_metrics_scope | 570 or explicit legacy | 720 | WARN | MAJOR | legacy 720 spatial metrics; regenerate or archive as legacy |
| C008 | active corpus_v2 refs outside archive | 0 (except legacy context) | 15 | WARN | MAJOR | review docs/scripts and keep only legacy context |
| C009 | active corpus_v3 refs outside archive | 0 (except legacy context) | 14 | WARN | MINOR | review historical mentions |
| C010 | active 720 refs outside archive | historical context only | 123 | WARN | MINOR | mark as historical or update to 570 |
| C011 | resultados_actuales | analysis/reports/RESULTADOS_ACTUALES.md | True | PASS | INFO | generate missing artifact |
| C012 | paper_freeze_checklist | analysis/reports/paper_freeze_checklist.md | True | PASS | INFO | generate missing artifact |
| C013 | message_analysis_window_policy | analysis/reports/canonical/message_analysis_window_policy.md | True | PASS | INFO | generate missing artifact |
| C014 | protocol_benchmark_kpi_policy | analysis/reports/canonical/protocol_benchmark_kpi_policy.md | True | PASS | INFO | generate missing artifact |
| C015 | traffic_profile_kpi_analysis | analysis/reports/canonical/traffic_profile_kpi_analysis.md | True | PASS | INFO | generate missing artifact |
| C016 | corpus_benchmark_validation | analysis/reports/canonical/corpus_benchmark_validation.md | True | PASS | INFO | generate missing artifact |
| C017 | paper_figures_main_dir | analysis/figures/paper/main | True | PASS | INFO | generate missing artifact |
| C018 | paper_tables_dir | analysis/figures/paper/tables | True | PASS | INFO | generate missing artifact |
