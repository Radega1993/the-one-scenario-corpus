# Reports reorganization audit

**Date:** 2026-05-24 15:00 UTC  
**Operator:** automated reorg (plan `reports_reorganization_wiki`)  
**Corpus:** `corpus_v2` (unchanged)

## 1. Backup

| Artifact | Path |
|----------|------|
| Snapshot (before) | `analysis/reports/_reports_reorganization_before_20260524_145824.txt` |
| Tar backup | `analysis/reports_backup_20260524_145824.tar.gz` (74 KB) |

## 2. Tree before / after

**Before:** 46 files in flat `analysis/reports/` (+ `project/` with one file).

**After:**

```
analysis/reports/
├── README.md
├── RESULTADOS_ACTUALES.md
├── paper_freeze_checklist.md
├── canonical/          (5)
├── pipeline/           (13)
├── validation/         (6)
├── policies/           (1)
├── paper_gate/         (3)
├── spatial/            (3)
├── traffic_profiles/   (empty)
├── wiki_meta/          (4)
├── project/            (6 incl. this report)
└── _archive_local/     (3 legacy)
```

## 3. Files moved (summary)

Full manifest: [../../data/reports_reorganization_manifest.csv](../../data/reports_reorganization_manifest.csv) (46 rows).

| Category | Count | Examples |
|----------|------:|----------|
| canonical | 5 | `traffic_profile_kpi_analysis.md`, `protocol_benchmark_kpi_policy.md` |
| pipeline | 13 | `correlation_report.txt`, `features_report.md` |
| validation | 6 | `tp_validation_report.md`, `settings_audit.md` |
| policies | 1 | `simulation_time_policy.md` |
| paper_gate | 3 | `paper_figures_tables_readiness.md` |
| spatial | 3 | `useful_simulation_time_report.md` |
| wiki_meta | 4 | `wiki_paper_rebuild_report.md` |
| project | 5 | `REPORTS_INVENTORY.md`, `project_reorganization_report.md` |
| _archive_local | 3 | `trace_realism_audit.md`, `check_tp12_d2.md` |
| root (unchanged) | 3 | `RESULTADOS_ACTUALES.md`, `paper_freeze_checklist.md`, `README.md` |

**UNCATEGORIZED:** none.

## 4. Files not moved

| File | Reason |
|------|--------|
| `RESULTADOS_ACTUALES.md` | Canonical numeric freeze (root) |
| `paper_freeze_checklist.md` | Paper gate (root) |
| `README.md` | Index (root, rewritten) |
| `_reports_reorganization_before_*.txt` | Audit snapshot |

## 5. Links updated

- `scenarios/README.md`, `README.es.md`, `INVENTARIO.md`
- `analysis/README.md`, `SCRIPTS_INDEX.md`, `dashboard/README.md`
- `corpus_v2/README.md` (legacy TP12 notes → `_archive_local/`)
- `.wiki-clone/` pages: Home, 04–14, CHANGELOG, References
- `analysis/populate_wiki_paper.py`, `run_analysis.py` (pipeline paths + RESULTADOS links)
- `lib/report_paths.py` — canonical path registry for scripts

## 6. Broken links pending

| Location | Note |
|----------|------|
| `scenarios/_archive/**` | Historical paths left intentional |
| `limitations.md` | Never existed; freeze checklist marks absent |

## 7. Wiki status: **UPDATED**

| Check | Result |
|-------|--------|
| Canonical report links | Updated in Home, 04, 08, 11, 12, 14 |
| Pipeline txt links | Updated in 05, 06 |
| corpus_v2 active / no corpus_v3 | Home |
| Synthetic vs real traces | Home, 04 |
| Spatial ≠ connectivity | 08 |
| Protocol KPIs (DR, latency, overhead, drop) | 07 |
| TP07 burst / TP10 stress | 04 |
| Figures index | Home → `FIGURES_AND_TABLES_INDEX.md` |

**Gaps (documented, no new pages):**

- No dedicated `11-Limitations` wiki page (`limitations.md` missing).
- No `12-Figures-and-Tables` page — covered via Home + `FIGURES_AND_TABLES_INDEX.md`.

## 8. Wiki pages reviewed / modified

**Reviewed:** Home, 01–14, README, CHANGELOG, Glossary, References.

**Modified:** Home, 04, 08, 14, CHANGELOG (+ bulk path sed on all `.wiki-clone/*.md`).

## 9. Figures validated (existence)

| Path | OK |
|------|:--:|
| `figures/message_creation_time_boxplot_by_tp.png` | yes |
| `figures/message_creation_time_hist_by_tp.png` | yes |
| `figures/aggregated/spatial_coverage_by_family.png` | yes |
| `figures/paper/main/` (multiple) | yes |
| `figures/paper/supplementary/` | yes |
| `figures/paper/FIGURES_AND_TABLES_INDEX.md` | yes |

## 10. Tables / CSV validated

| Path | OK |
|------|:--:|
| `figures/paper/tables/*.md` | yes |
| `data/traffic_profile_kpi_summary.csv` | yes |
| `data/protocol_benchmark_kpi_definitions.csv` | yes |

## 11. Canonical reports detected

1. `RESULTADOS_ACTUALES.md` (root)  
2. `canonical/traffic_profile_kpi_analysis.md`  
3. `canonical/protocol_benchmark_kpi_policy.md`  
4. `canonical/message_analysis_window_policy.md`  
5. `canonical/spatial_vs_performance_analysis.md`  
6. `canonical/corpus_v2_benchmark_validation.md`  
7. `paper_freeze_checklist.md` (root)

## 12. Code changes

- **New:** `lib/report_paths.py`, `validate_reports_reorganization.py`
- **Updated:** `run_analysis.py`, freeze/figures/wiki builders, validators, dashboard loaders/pages

## 13. Validation

```bash
python3 scenarios/analysis/validate_reports_reorganization.py
# Exit 0 — 46/46 basenames accounted for
```

## 14. Recommendations before paper writing

1. Re-run `build_paper_freeze_checklist.py` after any pipeline refresh.
2. Resolve remaining `error_probable` (e.g. S1 TP03) via targeted re-sim if needed — out of scope for this reorg.
3. Multi-protocol runs still required for Results claims.
4. Promote main figures from `revisar` → `lista` in `FIGURES_AND_TABLES_INDEX.md`.

## Status: **DONE** (reorg + wiki link pass). **PARTIAL** for paper Results until multi-protocol simulations exist.
