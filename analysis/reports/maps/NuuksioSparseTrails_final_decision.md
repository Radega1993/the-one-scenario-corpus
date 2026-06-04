# NuuksioSparseTrails — final decision

**Status:** PASS — paper-ready

Generated: 2026-05-28T18:15:34

## Summary

NuuksioSparseTrails is the sole map for **04_rural**. Finalization covers POI audit (50/120 m),
ranger patrol validation/regeneration, settings audit (A_bus fix, R1 rename), scenario classification, figures, and wiki.

## Scenario classification

- `rural_realistic`: 6
- `rural_extreme_control`: 6

## Methodological note

NuuksioSparseTrails is used as a sparse rural trail map. Low spatial coverage, low encounter rates, and low delivery ratios are expected outcomes in this family and should not be interpreted as configuration errors by default.

## Reproducibility

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_nuuksio_sparse_trails.py --dry-run
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_nuuksio_sparse_trails.py --apply --install
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps NuuksioSparseTrails --validation
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps NuuksioSparseTrails --paper-ready
bash scenarios/setup/bootstrap_maps.sh --install
```

## Artifacts

| Artifact | Path |
|----------|------|
| Asset inventory | `analysis/data/maps/NuuksioSparseTrails_asset_inventory.csv` |
| Classification | `analysis/data/maps/NuuksioSparseTrails_rural_scenario_classification.csv` |
| POI report | `analysis/reports/maps/NuuksioSparseTrails_poi_report.md` |
| Ranger route | `analysis/data/maps/NuuksioSparseTrails_ranger_route_validation.csv` |
| Settings audit | `analysis/data/maps/NuuksioSparseTrails_rural_settings_audit.csv` |
| Validation figure | `analysis/figures/maps/NuuksioSparseTrails_validation.png` |
| Paper figure | `analysis/figures/paper/maps/NuuksioSparseTrails_paper_ready.png` |
| Wiki | `.wiki-clone/09-Rural-Family.md` |

## R1 rename and historical data

`R1_Rural_RandomWaypoint` → `R1_Rural_SparseSPMM` in settings and manifests. Analysis CSVs (`output_metrics.csv`, etc.) are **not** bulk-updated.

## Excluded

Other map families; OSM full regen; Traffic Profile changes; automatic re-simulation.