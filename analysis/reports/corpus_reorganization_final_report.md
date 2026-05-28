# Corpus reorganization — final report

**Date:** 2026-05-27  
**Scope:** Nomenclature reorganization per `corpus-reorg-v1` plan (backup → split → manifests → `base_scenarios` → pipeline → wiki → analysis regen).

---

## Summary of changes

| Old path / name | New path / name |
|-----------------|-----------------|
| `scenarios/corpus_v1/` (mobility-only) | `scenarios/_archive/legacy_corpus_v1_pre_rename/` |
| `scenarios/corpus_v2/` (paper benchmark) | `scenarios/corpus_v1/` (540 environmental) |
| `scenarios/corpus_v1/07_stress_controls/` | `scenarios/stress_controls/07_stress_controls/` (30) |
| *(new)* | `scenarios/base_scenarios/` (45 structural bases) |
| CLI `corpus_v2` | Alias of `corpus_v1` (+ `stress_controls/`) |

**Paper simulation count:** **570** (540 + 30), not 720.

---

## Backup

- `scenarios/_archive/corpus_rename_backup_20260527_113536/`
- Includes: old `corpus_v1`, `corpus_v2`, `analysis/data`, `analysis/reports`, `analysis/figures`, `.wiki-clone`
- Metadata: `BACKUP_INFO.md`

---

## File counts (verified)

| Directory | `.settings` |
|-----------|------------:|
| `base_scenarios/` | 45 |
| `corpus_v1/` | 540 |
| `stress_controls/` | 30 |
| **Combined manifest** | 570 rows |

---

## Manifests & scripts added

| Script | Purpose |
|--------|---------|
| `setup/regenerate_manifests.py` | Regenerate `manifest.csv` / `manifest_revision.csv` |
| `setup/migrate_base_scenarios_maps.py` | Build `base_scenarios/` from legacy + map migration |
| `setup/build_base_scenarios_manifest.py` | `base_scenarios/manifest.csv` |
| `analysis/validate_base_scenarios.py` | Structural layer validation |
| `analysis/scripts/validation/validate_corpus_benchmark.py` | Paper benchmark readiness (replaces `validate_corpus_v2_benchmark.py`) |

Combined manifest: `analysis/data/corpus_v1_combined_manifest.csv`

---

## Validations

| Check | Result |
|-------|--------|
| `validate_base_scenarios.py` | **45/45 OK** |
| `validate_traffic_profiles.py --corpus corpus_v1` | **568/570** settings OK |
| `validate_corpus_benchmark.py` | 570 rows written; status mix (191 ok, 168 error_probable, …) |

Reports: `reports/base_scenarios_validation.md`, `reports/validation/tp_validation_report.md`, `reports/canonical/corpus_benchmark_validation.md`

---

## Pipeline updates

- `lib/paths.py`: `CORPUS_V1_DIR`, `STRESS_CONTROLS_DIR`, `BASE_SCENARIOS_DIR`, `collect_settings_paths()`, `build_combined_manifest_csv()`
- `--corpus corpus_v1` resolves **both** `corpus_v1/` and `stress_controls/`
- Dashboard loaders use combined manifest (570 rows)
- `validate_corpus_v2_benchmark.py` removed; menu → `validate_corpus_benchmark.py`
- `run_analysis.py`: fixed pandas read-only array bugs for correlation phases (570 scenarios)

---

## Analysis regeneration (2026-05-27)

Commands:

```bash
cd scenarios/analysis
.venv/bin/python run_analysis.py --corpus corpus_v1 --phase all
.venv/bin/python run_analysis.py --corpus corpus_v1 --phase figures_paper
.venv/bin/python run_analysis.py --corpus corpus_v1 --phase tables_paper
.venv/bin/python run_figures_aggregated.py --corpus corpus_v1
```

**Outputs:** `data/features.csv` (570×46), correlation CSVs, `reports/RESULTADOS_ACTUALES.md`, `figures/paper/`, `figures/aggregated/` (22 PNG).

### Diversity metrics (from `RESULTADOS_ACTUALES.md`)

| Space | max \|r\| | Pairs \|r\| ≥ 0.7 | Share of pairs |
|-------|-----------|-------------------|----------------|
| Core-23 | 1.0 | 5 676 | 3.5% (of 162 165) |
| Full-46 | 1.0 | 3 815 | 2.4% |

Feature–feature (core): `mm_WDM ↔ mm_Bus = 0.9363`

**Note:** `--phase ablation` requires `scipy` in `analysis/.venv` (not installed in this run); silhouette values in `RESULTADOS_ACTUALES.md` ablation table are from the previous frozen report until `scipy` is installed and ablation re-run.

---

## Wiki

- Regenerated via `scripts/wiki/populate_wiki_paper.py`
- New page: `03-Base-Scenarios.md`; pages renumbered 04–15
- Location: `scenarios/.wiki-clone/` (local clone only)

---

## Documentation

Updated: `README.md`, `corpus_v1/README.md`, `INVENTARIO.md` (corpus table), `analysis/SCRIPTS_INDEX.md`, `CHANGELOG.md`, `REPRODUCIBILITY.md`

---

## Active `corpus_v2` references

Allowed in: `_archive/`, legacy report filenames (`corpus_v2_revision_changelog.md`), CLI alias in `lib/paths.py`, historical audit notes under `reports/_archive_local/`.

---

## Pending / follow-up

1. Install `scipy` in `analysis/.venv` and re-run `--phase ablation` for updated silhouette table.
2. Investigate 2 TP validation failures (568/570).
3. Align `output_metrics.csv` row count (566) with 570 manifest rows if missing reports exist.
4. Optional: rename legacy canonical file `corpus_v2_benchmark_validation.md` → archive only (superseded by `corpus_benchmark_validation.md`).
