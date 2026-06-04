# KumpulaCampus — final decision (paper-ready)

**Map:** `KumpulaCampus` · **Family:** `02_campus` · **Status:** CLOSED (paper-ready)

Generated: 2026-05-28

## Executive summary

| Check | Result |
|-------|--------|
| Global closure | **PASS** |
| WKT assets | Complete |
| Settings audit | PASS (78 files) |
| Shuttle route | WARNING (optional asset; one sim-origin stop documented) |
| POIs | 65 reviewed, 6 corrected (>60 m / border) |
| C4 rename | `C4_CampusEvent_IngressEgress` (13 files) |
| C6 cleanup | LinearMovement residuals removed (13 files) |

## Why this map for 02_campus

University of Helsinki Kumpula campus: compact OSM extract with internal roads and pedestrian paths (`network_type: all`), `worldSize` 1524×1416 m. All scenarios use `ShortestPathMapBasedMovement` on `data/KumpulaCampus/roads.wkt`.

## Scenarios (C1–C6)

| ID | Scenario | Focus |
|----|----------|-------|
| C1 | Campus_ClassChange | Between-class mobility |
| C2 | ExamDay_LongStays | Long exam waits |
| C3 | Hackathon_24h | 86400 s event |
| C4 | CampusEvent_IngressEgress | Bimodal ingress/egress peaks |
| C5 | Library_Quiet | Low mobility, long waits |
| C6 | EmergencyDrill_Evacuation | Fast map-based evacuation |

## Shuttle asset

`A_campus_shuttle.wkt` is **not** referenced in `.settings` (optional figure/documentation). Solid line = Dijkstra path on roads; dotted = stop order.

## Figures

| Use | Path |
|-----|------|
| Paper | `scenarios/analysis/figures/paper/maps/KumpulaCampus_paper_ready.png` |
| Wiki | `scenarios/.wiki-clone/assets/maps/KumpulaCampus.png` |
| Validation | `scenarios/analysis/figures/maps/KumpulaCampus_validation.png` |

## Re-simulation

Recommended after POI/shuttle WKT updates. See `KumpulaCampus_resimulation_plan.md`.

## Reproducibility commands

```bash
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_kumpula_campus.py --dry-run
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_kumpula_campus.py --apply --install
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps KumpulaCampus --validation
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps KumpulaCampus --paper-ready
bash scenarios/setup/bootstrap_maps.sh --install
```

## Deliverables

`scenarios/analysis/data/maps/KumpulaCampus_*.csv`, reports `scenarios/analysis/reports/maps/KumpulaCampus_*.md`.