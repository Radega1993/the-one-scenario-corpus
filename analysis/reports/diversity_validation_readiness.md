# Diversity validation readiness report

Generated: 2026-05-28 07:47 UTC

**Corpus scope:** `corpus_v1` only — **540** scenarios (stress_controls excluded)

**Expected pairs:** C(540,2) = 145530

**Decision (diversity scope):** `READY_FOR_PAPER`

**Combined benchmark (570 routing/outputs):** `READY_WITH_MINOR_FIXES` (output_metrics=540/570; not part of diversity freeze)

## Project structure (active)

- **base_scenarios/**: 45 structural bases (no TP)
- **corpus_v1/**: 540 environmental scenarios with TP (diversity scope)
- **stress_controls/**: 30 stress/control lab (excluded from diversity freeze)
- **Combined paper benchmark:** 570 (540 + 30)
- **Diversity validation scope:** 540 (`corpus_v1` only, `--no-stress`)
- **Legacy archive:** `_archive/diversity_legacy_20260527/` (720-era CSVs; not canonical)
- Legacy CSV count in archive: 3

**Pipeline reports:** canonical paths are under `analysis/reports/pipeline/` (flat `reports/*.txt` names are legacy aliases).

## Summary

- PASS: 51
- WARN: 1
- FAIL: 0

## Canonical artifacts (diversity freeze)

| Type | Path |
|------|------|
| Data | `analysis/data/features*.csv`, `correlation_*.csv`, `distance_*.csv`, `ablation_metrics.csv` |
| Reports | `analysis/reports/RESULTADOS_ACTUALES.md`, `analysis/reports/pipeline/*.txt` |
| Figures | `analysis/figures/paper/main/` (F001–F006) |
| Tables | `analysis/figures/paper/tables/table_*_en.md` |
| Methodology | `analysis/docs/features_core_vs_extended.md` |

## Checklist

| item_id | category | artifact | status | severity | notes |
|---|---|---|---|---|---|
| S001 | consistency | corpus_v1_settings_count | PASS | INFO | observed=540 |
| D001 | data | features.csv | PASS | INFO | rows=540 |
| D002 | data | features_normalized.csv | PASS | INFO | rows=540 features=46 |
| D003 | data | features_reduced.csv | PASS | INFO | rows=540 features=17 |
| D004 | data | features_core.csv | PASS | INFO | rows=540 features=23 |
| D005 | data | normalization_params.csv | PASS | INFO | rows=46 |
| D006 | data | correlation_pearson.csv | PASS | INFO | matrix 540x540 |
| D007 | data | correlation_spearman.csv | PASS | INFO | matrix 540x540 |
| D008 | data | distance_cosine.csv | PASS | INFO | matrix 540x540 |
| D009 | data | distance_euclidean.csv | PASS | INFO | matrix 540x540 |
| D010 | data | correlation_pearson_core23.csv | PASS | INFO | matrix 540x540 |
| D011 | data | distance_cosine_core23.csv | PASS | INFO | matrix 540x540 |
| D012 | data | cluster_assignments.csv | PASS | INFO | rows=540 |
| D013 | data | cluster_assignments_core23.csv | PASS | INFO | rows=540 |
| D014 | data | feature_feature_correlation_core.csv | PASS | INFO | matrix 23x23 |
| D015 | data | ablation_metrics.csv | PASS | INFO | rows=3 total_pairs=145530 |
| S003 | consistency | scenario_ids_aligned | PASS | INFO | n=540 aligned |
| S004_correlat | consistency | correlation_pearson.csv_finite | PASS | INFO | nan_frac=0.0000 inf=0 |
| S004_correlat | consistency | correlation_spearman.csv_finite | PASS | INFO | nan_frac=0.0000 inf=0 |
| S004_distance | consistency | distance_cosine.csv_finite | PASS | INFO | nan_frac=0.0000 inf=0 |
| S004_distance | consistency | distance_euclidean.csv_finite | PASS | INFO | nan_frac=0.0000 inf=0 |
| S005 | consistency | ablation_feature_dims | PASS | INFO | 17/23/46 verified |
| S006 | consistency | RESULTADOS_vs_ablation | PASS | INFO | numeric fields match ablation_metrics.csv |
| S002 | consistency | features_scope_no_stress | PASS | INFO | rows=540 stress_like=0 |
| R001 | report | RESULTADOS_ACTUALES.md | PASS | INFO | pipeline path OK |
| R002 | report | correlation_report.txt | PASS | INFO | pipeline path OK |
| R003 | report | correlation_core23_report.txt | PASS | INFO | pipeline path OK |
| R004 | report | ablation_report.txt | PASS | INFO | pipeline path OK |
| R005 | report | feature_feature_correlation_report.txt | PASS | INFO | pipeline path OK |
| R006 | report | multiple_comparisons_report.txt | PASS | INFO | pipeline path OK |
| R007 | report | clustering_report.txt | PASS | INFO | pipeline path OK |
| R008 | report | scenarios_to_diversify.txt | PASS | INFO | pipeline path OK |
| R009 | report | scenarios_to_diversify_core23.txt | PASS | INFO | pipeline path OK |
| F001 | figure | histogram_correlations_pearson_paper.png | PASS | INFO | MAIN_PAPER |
| F002 | figure | pca_by_family.png | PASS | INFO | MAIN_PAPER |
| F003 | figure | pca_by_cluster.png | PASS | INFO | MAIN_PAPER |
| F004 | figure | ablation_pairs_high_bar.png | PASS | INFO | MAIN_PAPER |
| F005 | figure | ablation_silhouette_bar.png | PASS | INFO | MAIN_PAPER |
| F006 | figure | heatmap_feature_feature_core.png | PASS | INFO | MAIN_PAPER |
| T001 | table | table_diversity_metrics_en.md | PASS | INFO | present |
| T002 | table | table_ablation_metrics_en.md | PASS | INFO |  |
| T003 | table | table_core_vs_extended_en.md | PASS | INFO |  |
| T004 | table | table_families_en.md | PASS | INFO |  |
| T005 | table | table_diversity_criteria_en.md | PASS | INFO | present |
| DOC001 | readme | features_core_vs_extended.md | PASS | INFO |  |
| DOC002 | readme | analysis README.md | PASS | INFO |  |
| DOC003 | readme | SCRIPTS_INDEX.md | PASS | INFO |  |
| DOC004 | wiki | wiki 07-Diversity-Validation | PASS | INFO |  |
| DOC005 | wiki | wiki Resultados-Actuales | PASS | INFO |  |
| C001 | consistency | root_README_diversity_scope | PASS | INFO | OK |
| C002 | consistency | FIGURES_AND_TABLES_INDEX | PASS | INFO | diversity validation PASS in index |
| C003 | consistency | output_metrics_benchmark_scope | WARN | MINOR | rows=540 expected 570 for combined benchmark (not diversity scope) |

## Warnings

- **C003** output_metrics_benchmark_scope: rows=540 expected 570 for combined benchmark (not diversity scope) → complete simulations and rerun output_metrics

## Recommended actions (non-diversity)

- Complete combined benchmark simulations (570) and regenerate `output_metrics.csv` if routing results are needed.
- Regenerate `spatial_occupancy_metrics.csv` for 540/570 scope (current file may still be 720 legacy).
- Archive candidates: see [diversity_archive_candidates.md](diversity_archive_candidates.md)
