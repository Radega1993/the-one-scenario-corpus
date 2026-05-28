# ManhattanMidtownGrid — final decision

**Status:** PASS — paper-ready

Generated: 2026-05-28T18:06:14

## Summary

ManhattanMidtownGrid is the sole map for **03_vehicles**. Finalization covers POI audit (30/75 m),
vehicle routes A/B validation/regeneration, settings audit (legacy bus paths), figures, and wiki.

## Reproducibility

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_manhattan_midtown.py --dry-run
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_manhattan_midtown.py --apply --install
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps ManhattanMidtownGrid --validation
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps ManhattanMidtownGrid --paper-ready
bash scenarios/setup/bootstrap_maps.sh --install
```

## Artifacts

| Artifact | Path |
|----------|------|
| Asset inventory | `analysis/data/maps/ManhattanMidtownGrid_asset_inventory.csv` |
| Geometry validation | `analysis/data/maps/ManhattanMidtownGrid_geometry_validation.csv` |
| POI report | `analysis/reports/maps/ManhattanMidtownGrid_poi_report.md` |
| Vehicle routes | `analysis/data/maps/ManhattanMidtownGrid_vehicle_route_validation.csv` |
| Settings audit | `analysis/data/maps/ManhattanMidtownGrid_vehicle_settings_audit.csv` |
| Validation | `analysis/figures/maps/ManhattanMidtownGrid_validation.png` |
| Paper figure | `analysis/figures/paper/maps/ManhattanMidtownGrid_paper_ready.png` |
| Wiki | `.wiki-clone/08-Vehicles-Family.md` |

## Excluded

Other map families; OSM full regen; Traffic Profile changes; automatic re-simulation.
