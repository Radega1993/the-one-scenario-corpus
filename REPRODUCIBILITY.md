# Reproducibility — scenario corpus reorganization (2026-05-27)

## Directory layout (paper)

| Path | Role | `.settings` count |
|------|------|------------------:|
| `base_scenarios/` | Structural mobility bases (no TP) | 45 |
| `corpus_v1/` | Environmental benchmark with Traffic Profiles | 540 |
| **Paper benchmark** | Simulation and analysis | **540** |

**Simulation:**

```bash
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v1          # 540
```

Legacy pre-rename mobility corpus: `_archive/legacy_corpus_v1_pre_rename/` (60 files).

## Structural bases

`base_scenarios/` is version-controlled (45 files). After map or `worldSize` changes:

```bash
python3 scenarios/setup/build_base_scenarios_manifest.py
python3 scenarios/setup/audit_world_size_settings.py
```

## Regenerate manifests

```bash
cd scenarios/setup
python3 regenerate_manifests.py --corpus-dir ../corpus_v1
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
