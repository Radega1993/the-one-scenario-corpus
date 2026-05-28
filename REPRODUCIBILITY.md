# Reproducibility — scenario corpus reorganization (2026-05-27)

## Directory layout (paper)

| Path | Role | `.settings` count |
|------|------|------------------:|
| `base_scenarios/` | Structural mobility bases (no TP) | 45 |
| `corpus_v1/` | Environmental benchmark with Traffic Profiles | 540 |
| `stress_controls/07_stress_controls/` | Stress/control laboratory (TP01 + TP10) | 30 |
| **Combined paper benchmark** | Analysis/validation (`include_stress=True`) | **570** |

**Simulation:** `--corpus corpus_v1` runs **540** environmental scenarios only. Stress/control is separate:

```bash
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1          # 540
python3 scenarios/analysis/run_all_scenarios.py --corpus stress_controls  # 30
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 --benchmark all  # 570
```

Legacy pre-rename mobility corpus: `_archive/legacy_corpus_v1_pre_rename/` (60 files).

## Regenerate structural bases

```bash
cd scenarios/setup
python3 migrate_base_scenarios_maps.py \
  --source ../_archive/legacy_corpus_v1_pre_rename \
  --dest ../base_scenarios
python3 build_base_scenarios_manifest.py --dest ../base_scenarios
```

## Regenerate manifests

```bash
cd scenarios/setup
python3 regenerate_manifests.py --corpus-dir ../corpus_v1
python3 regenerate_manifests.py --corpus-dir ../stress_controls --flat-family 07_stress_controls
cd ../analysis
python3 -c "from lib.paths import build_combined_manifest_csv; print(build_combined_manifest_csv())"
```

## Validations

```bash
cd scenarios/analysis
.venv/bin/python validate_base_scenarios.py
.venv/bin/python scripts/validation/validate_traffic_profiles.py --corpus corpus_v1
.venv/bin/python scripts/validation/validate_corpus_benchmark.py
```

## Full analysis pipeline

```bash
cd scenarios/analysis
.venv/bin/python run_analysis.py --corpus corpus_v1 --phase all
.venv/bin/python run_analysis.py --corpus corpus_v1 --phase figures
.venv/bin/python run_analysis.py --corpus corpus_v1 --phase figures_paper
.venv/bin/python run_analysis.py --corpus corpus_v1 --phase tables_paper
.venv/bin/python run_figures_aggregated.py --corpus corpus_v1
```

## Wiki (local clone)

```bash
cd scenarios/analysis
.venv/bin/python scripts/wiki/populate_wiki_paper.py
```

Output: `scenarios/.wiki-clone/` (not pushed to remote wiki by default).

## Backup before changes

Full snapshot: `scenarios/_archive/corpus_rename_backup_20260527_113536/` — see `BACKUP_INFO.md`.
