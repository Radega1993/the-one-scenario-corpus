# HelsinkiDisrupted — final decision

**Status:** PASS — paper-ready

Generated: 2026-05-28T18:21:32

## Summary

HelsinkiDisrupted is the sole map for **05_disaster**. Finalization covers POI audit (40/100 m),
emergency/mule route validation/regeneration, settings audit (D5 SPMM), scenario classification, figures, and wiki.

## Scenario classification

- Narrative (realistic + bridge/mule): 6
- Controls (TTL + stress): 3

## Methodological note

HelsinkiDisrupted is used as a degraded urban disaster map. Low delivery, high latency, and structural partitioning can be expected outcomes in specific scenarios and should not be interpreted as configuration errors by default.

## Reproducibility

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_helsinki_disrupted.py --dry-run
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_helsinki_disrupted.py --apply --install
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps HelsinkiDisrupted --validation
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps HelsinkiDisrupted --paper-ready
bash scenarios/setup/bootstrap_maps.sh --install
```

## Artifacts

| Artifact | Path |
|----------|------|
| Asset inventory | `analysis/data/maps/HelsinkiDisrupted_asset_inventory.csv` |
| Classification | `analysis/data/maps/HelsinkiDisrupted_disaster_scenario_classification.csv` |
| POI report | `analysis/reports/maps/HelsinkiDisrupted_poi_report.md` |
| Routes | `analysis/data/maps/HelsinkiDisrupted_route_validation.csv` |
| Settings audit | `analysis/data/maps/HelsinkiDisrupted_disaster_settings_audit.csv` |
| Validation figure | `analysis/figures/maps/HelsinkiDisrupted_validation.png` |
| Paper figure | `analysis/figures/paper/maps/HelsinkiDisrupted_paper_ready.png` |
| Wiki | `.wiki-clone/10-Disaster-Family.md` |

## Excluded

Other map families; OSM full regen; Traffic Profile changes; automatic re-simulation.