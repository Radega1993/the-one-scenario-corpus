# Analysis cleanup final report

## Executive summary

- Completed docs+wiki finalization for paper writing readiness on top of the analysis cleanup.
- Raw The ONE reports under `../../reports/` were not modified.
- Active benchmark confirmed: `base_scenarios` 45, `corpus_v1` 540, `stress_controls` 30, combined 570.

## Review metrics (final pass)

- Scripts reviewed: 51
- CSV/data artifacts reviewed: 60
- Reports reviewed: 60
- Figures reviewed: 830
- Kept artifacts: 924
- Archived artifacts: 11
- Regeneration-required artifacts: 15
- Wiki pages audited (active set): 23
- Wiki warnings: 0 (broken links: 0)
- Consistency checks: PASS=13 WARN=5 FAIL=0

## Area status

| Area | Reviewed | Kept | Archived | Needs regeneration | Status |
|---|---:|---:|---:|---:|---|
| Data | 60 | 42 | 3 | 15 | complete |
| Reports | 60 | 52 | 8 | 0 | complete |
| Figures | 830 | 830 | 0 | 0 | complete |
| Wiki sync | 23 | 23 | 0 | 0 | complete |

## Canonical artifacts

| Canonical artifact | Path | Status | Used in paper |
|---|---|---|---|
| Frozen results | `analysis/reports/RESULTADOS_ACTUALES.md` | ready | yes |
| Combined manifest | `analysis/data/corpus_v1_combined_manifest.csv` | ready | yes |
| Benchmark validation | `analysis/reports/canonical/corpus_benchmark_validation.md` | ready | yes |
| TP validation | `analysis/reports/validation/tp_validation_report.md` | ready | yes |
| Message policy | `analysis/reports/canonical/message_analysis_window_policy.md` | ready | yes |
| Protocol KPI policy | `analysis/reports/canonical/protocol_benchmark_kpi_policy.md` | ready | yes |
| Paper figures | `analysis/figures/paper/main/` | ready | yes |
| Paper tables | `analysis/figures/paper/tables/` | ready | yes |
| Wiki sync audit | `analysis/reports/wiki_meta/wiki_final_sync_audit.md` | ready | support |

## Pending actions before final submission

- Install `scipy` in `scenarios/analysis/.venv` and rerun `run_analysis.py --phase ablation` to refresh `ablation_metrics.csv` in the current environment.
- Regenerate spatial occupancy datasets to strict 570 if required; current spatial CSV is legacy-720 fallback to keep dependent reports operable.
- Close remaining consistency WARNs (`output_metrics` 566 vs 570, and legacy-string counters in broad docs) when simulation outputs are complete.

## Writing readiness conclusion

Docs, reports, figures, and wiki are organized and synchronized enough to start writing the paper now, using canonical artifacts listed in `paper_artifacts_index.md`.
