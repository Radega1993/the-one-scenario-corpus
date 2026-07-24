# Map generation revised v2 — regeneration changelog

## Scope completed

- Removed incomplete `dartmouth_campus_*` traces (inventory/policy/raw/processed/staging/docs).
- Kept `dartmouth_wardriving_20060602`.
- Promoted real extractors: RollerNet, Sassy, LocShare, Oviedo `.one.gz`.
- Enabled GPS summaries for Roma taxi + RioBuses with new OSM anchors `roma_centro`, `rio_centro_buses`.
- Planner quotas: target **1200**, OSM 0.45 / synthetic 0.40 / TRS 0.15.
- Executor writes WKT/metadata/provenance under `scenarios/Generated_Map_Space_v1/`.
- CLI accepts revised v2 `--generate` / `--plan-only` / `--acquire-osm` / `--build`.

## Pool run summary

See [`map_generation_revised_v2_run.md`](map_generation_revised_v2_run.md).

Notes:

- Synthetic + TRS built fully in this run.
- OSM downloads bounded (osmnx installed; ~40+ successful OSM maps including Tampere suburban recovery with larger windows). Remaining OSM slots are `FAIL_DOWNLOAD_SKIPPED` until further `--max-downloads` runs.
- Baseline `map_space_saturation_v1/` untouched.
- 15 archetypes unchanged.

## Commands

```bash
# Dry-run plan
python scenarios/setup/generate_map_space_saturation_v1.py \
  --config scenarios/analysis/config/map_design_space_revised_v2.yaml \
  --dry-run --write-plan --target-total 1200 --seed 42

# Continue OSM acquisition
python scenarios/setup/generate_map_space_saturation_v1.py \
  --config scenarios/analysis/config/map_design_space_revised_v2.yaml \
  --generate --source osm --target-total 1200 --seed 42 --max-downloads 50
```
