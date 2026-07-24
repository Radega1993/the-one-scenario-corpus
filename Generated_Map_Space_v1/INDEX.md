# GMS-v1 index — `Generated_Map_Space_v1`

**Fase overview (ES):** [`README.md`](README.md)  
**Phase status:** `STOP_AMENDED_CEILING_2000` / `freeze_candidate` (see [`data/map_space_revised_v2_saturation_decision.json`](data/map_space_revised_v2_saturation_decision.json)).

## Docs

- [Architecture](docs/map_generation_architecture_v2.md)
- [Methodological readiness](docs/map_generation_v2_methodological_readiness.md)
- [Saturation report](docs/map_space_revised_v2_saturation_report.md)
- [STOP diagnostics @2000](docs/stop_diagnostics_ceiling_2000.md)
- [Pool revalidation](docs/map_space_revised_v2_pool_revalidation_attrition.md)
- [Validation](docs/map_space_revised_v2_validation_report.md)
- [Features extract](docs/map_space_revised_v2_saturation_features_report.md)
- [Run log](docs/map_generation_revised_v2_run.md)
- [Dry-run](docs/map_generation_v2_dry_run.md)
- [Audit / changelog / failures / OSM anchors / allocation / trace mapping](docs/)
- History (phase rationale): [`docs/history/`](docs/history/)

## Config

- [`config/map_design_space.yaml`](config/map_design_space.yaml) — design space (key `map_design_space_revised_v2`)
- [`config/saturation_protocol.yaml`](config/saturation_protocol.yaml)
- [`config/saturation_protocol_amendment_ceiling_2000.yaml`](config/saturation_protocol_amendment_ceiling_2000.yaml) — post-hoc STOP amendment
- [`config/archetype_source_allocation.yaml`](config/archetype_source_allocation.yaml)
- [`config/trace_to_map_generation_policy.yaml`](config/trace_to_map_generation_policy.yaml)

## Layout

| Path | Role |
|------|------|
| [`downloaded_external_traces/`](downloaded_external_traces/) | Trace registry + downloads |
| `batch_*/wkt/` | GMS pool WKTs |
| [`data/`](data/) | Features, decisions, transform freeze |
| [`docs/history/`](docs/history/) | Archetype justification, trace inventory rationale, generation review |
| [`figures/saturation/`](figures/saturation/) | Saturation curves |

## Commands (from this pack)

```bash
cd scenarios/Generated_Map_Space_v1
# scripts = pack; ../setup = solo map_geometry (compartido)
export PYTHONPATH=scripts:../setup

# Dry-run plan
python scripts/generate.py \
  --config config/map_design_space.yaml \
  --dry-run --write-plan --target-total 90 --seed 42

# Generate (syn / OSM / all)
python scripts/generate.py \
  --config config/map_design_space.yaml \
  --generate --source synthetic --target-total 1600 --seed 42

# Validate / features / saturation
python scripts/validate.py
python scripts/extract_features.py --geometry-only-normalized
python scripts/analyze_saturation.py

# OSM progress
bash scripts/watch_osm_progress.sh
# or: bash scripts/watch_osm_progress.sh --once
```
