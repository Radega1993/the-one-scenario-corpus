# Map policy — corpus_v1 (active benchmark)

> **2026-05:** Geometric validation: [`maps/map_assets_final_validation.md`](maps/map_assets_final_validation.md).  
> **worldSize calibration:** [`spatial/world_size_occupancy_calibration.md`](spatial/world_size_occupancy_calibration.md) — SSOT: `analysis/data/world_size_calibration.csv`.

## Summary

The active benchmark uses **one fixed OSM map per environmental family** (six families, **540** scenarios in `corpus_v1/` plus **45** structural bases in `base_scenarios/`). Legacy layouts (mixed Helsinki/Manhattan per family, free-space mobility, family `07_` synthetic grid, and **720**-scenario `corpus_v2` counts) are **retired**.

| Family | Map | worldSize (m) | Corpus scenarios |
|--------|-----|---------------|-----------------:|
| `01_urban` | HelsinkiDowntown | 1713 × 1459 | 84 |
| `02_campus` | KumpulaCampus | 1148 × 1036 | 72 |
| `03_vehicles` | ManhattanMidtownGrid | 2120 × 1986 | 60 |
| `04_rural` | NuuksioSparseTrails | 2470 × 2565 | 144 |
| `05_disaster` | HelsinkiDisrupted | 1711 × 1874 | 108 |
| `06_social` | KallioCommunityCompact | 1124 × 1149 | 72 |

**Policy:** within a family, differences come from mobility parameters, density, traffic profiles (TP01–TP12), and routing — not from swapping maps or per-scenario `worldSize`.

## Maintenance commands (repo root)

```bash
bash scenarios/setup/bootstrap_maps.sh --install
python3 scenarios/setup/validate_maps.py
python3 scenarios/setup/calibrate_world_size_per_map.py --apply
python3 scenarios/setup/migrate_corpus_maps.py --world-size-only
python3 scenarios/setup/audit_world_size_settings.py
```

After `worldSize` changes, **re-simulate** affected scenarios before using spatial occupancy metrics (`coverage_road_cells_pct`).

## Documentation

- Wiki: [02-Maps-and-Map-Generation](../../.wiki-clone/02-Maps-and-Map-Generation.md), [03-Installation](../../.wiki-clone/03-Installation.md)
- Pipeline: [`map_preparation_pipeline.md`](map_preparation_pipeline.md)
- Route naming: [`maps/route_semantic_policy.md`](maps/route_semantic_policy.md)

## Known gaps

**504/540** corpus scenarios run with maps in git. **36** scenarios (R2, S1, S6 bases × 12 TPs) need auxiliary route WKT not yet in the tree — see Installation wiki.

## Historical note

One-time migration from pre-2026 mixed-map corpus is complete; per-map `finalize_*` scripts and 720-scenario audit reports were removed. Use `regenerate_family_routes.py` only when route assets change.
