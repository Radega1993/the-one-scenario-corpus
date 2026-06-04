# KallioCommunityCompact — final decision

**Status:** PASS — paper-ready

Generated: 2026-05-28T18:25:33

## Summary

KallioCommunityCompact is the sole map for **06_social**. Finalization covers POI audit (40/100 m),
community route validation/regeneration (figure assets), settings audit (78 files), scenario classification,
runtime risk documentation, figures, and wiki.

## Scenario classification

- Map-based SPMM (S2–S5): 4 base scenarios
- Cluster-based (S1, S6): 2 base scenarios

## ClusterMovement note

In scenarios based on ClusterMovement (S1, S6), community structure is explicitly imposed through cluster centers and ranges. The road network is not used as a path constraint; the compact urban map provides spatial context and a consistent coordinate system.

## Reproducibility

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_kallio_community_compact.py --dry-run
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_kallio_community_compact.py --apply --install
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps KallioCommunityCompact --validation
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps KallioCommunityCompact --paper-ready
bash scenarios/setup/bootstrap_maps.sh --install
```

## Artifacts

| Artifact | Path |
|----------|------|
| Asset inventory | `analysis/data/maps/KallioCommunityCompact_asset_inventory.csv` |
| Classification | `analysis/data/maps/KallioCommunityCompact_social_scenario_classification.csv` |
| POI report | `analysis/reports/maps/KallioCommunityCompact_poi_report.md` |
| Routes | `analysis/data/maps/KallioCommunityCompact_route_validation.csv` |
| Settings audit | `analysis/data/maps/KallioCommunityCompact_social_settings_audit.csv` |
| Runtime risk | `analysis/reports/maps/KallioCommunityCompact_social_runtime_risk.md` |
| Validation figure | `analysis/figures/maps/KallioCommunityCompact_validation.png` |
| Paper figure | `analysis/figures/paper/maps/KallioCommunityCompact_paper_ready.png` |
| Wiki | `.wiki-clone/11-Social-Family.md` |

## Excluded

Other map families; OSM full regen; Traffic Profile changes; `routeFile` assignment; automatic re-simulation.