# HelsinkiDowntown — final decision (paper-ready)

**Map:** `HelsinkiDowntown` · **Family:** `01_urban` · **Status:** CLOSED (paper-ready)

Generated: 2026-05-28

## Executive summary

| Check | Result |
|-------|--------|
| Global closure | **PASS** |
| WKT assets complete | PASS |
| Geometry blocking errors | 0 |
| Bus routes resolvable | PASS (3 routes) |
| POIs inside worldSize | PASS (20 snaps applied for >75 m / border) |
| Urban settings audit | PASS (91 files) |
| Legacy `HelsinkiMedium` paths in 01_urban | None |
| Figures | validation + paper-ready |

## Why this map for 01_urban

Helsinki city centre (Kluuvi / Kamppi / Esplanadi) provides a dense OSM street grid with tram-scale blocks, suitable for `WorkingDayMovement` + bus-integrated pedestrians. A single fixed extract (`worldSize` 2093×1838 m, EPSG:3067) keeps all seven urban base scenarios and 84 TP variants geographically consistent.

## Scenarios using this map

| Base scenario | Role |
|---------------|------|
| U1_CBD_Commuting | CBD office concentration, rush peaks |
| U2_SparseUrban | Low host/office density on same map |
| U3_MicroMobility | Higher pedestrian speed band |
| U4_CongestionHotspot | Hotspot / buffer stress |
| U5_WorkdayShort | Shorter workday |
| U6_OfficeWaitHeavyTail | Heavy-tail office waits |
| U7_HighTimeVariance | High activity time variance |

Each base × 12 traffic profiles in `corpus_v1/01_urban/` → **91** settings files total.

## Movement models and assets

| Group | Model | routeFile | POI files |
|-------|---------|-----------|-----------|
| Group1 | BusMovement | `A_bus.wkt` | — |
| Group2 / Group | WorkingDayMovement | `A_bus.wkt` (required) | homes, offices, meetingspots |

`Group.routeFile` on `WorkingDayMovement` is **required** when `busControlSystemNr = -1` so The ONE registers bus stops (avoids NPE in `getBusStops()`).

Optional route assets: `B_bus.wkt`, `C_bus.wkt` (figures / future use; not referenced in current settings).

## Corrections applied

- **POIs:** 20 points snapped (offices/meetings >75 m from road or border artifacts).
- **Bus routes:** A/B/C regenerated on road graph (CBD N–S, E–W, peripheral loop).
- **U2 rename:** `U2_SparseSuburb` → `U2_SparseUrban` (13 settings + manifests).

Backups: `scenarios/maps/wkt/_backup_helsinki_poi_*`, `_backup_helsinki_bus_*`.

## Acceptable warnings

- Some POIs remain 30–75 m from nearest road segment (OSM building centroids).
- Bus stop vertices may show p95 ≈ 64 m under global 50 m validator; urban extended check PASS.

## Figures for the paper

| Use | Path |
|-----|------|
| Paper main | `scenarios/analysis/figures/paper/maps/HelsinkiDowntown_paper_ready.png` |
| Wiki | `scenarios/.wiki-clone/assets/maps/HelsinkiDowntown.png` |
| Technical supplement | `scenarios/analysis/figures/maps/HelsinkiDowntown_validation.png` |

Legend: **solid** = Dijkstra-resolved path on `roads.wkt`; **dotted** = stop order only.

## Re-simulation

**Recommended** for all `01_urban` scenarios after WKT changes. See [`HelsinkiDowntown_resimulation_plan.md`](HelsinkiDowntown_resimulation_plan.md) and `HelsinkiDowntown_affected_scenarios.csv`.

Traffic Profile blocks (`Events*`) were **not** modified.

## Reproducibility commands

From repository root:

```bash
# Audit only
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_helsinki_downtown.py --dry-run

# Apply POI + bus fixes, install to data/, U2 rename, figures
scenarios/analysis/.venv/bin/python scenarios/setup/finalize_helsinki_downtown.py --apply --install

# Individual steps
scenarios/analysis/.venv/bin/python scenarios/setup/repair_map_pois.py --map HelsinkiDowntown --apply --install
scenarios/analysis/.venv/bin/python scenarios/setup/regenerate_family_routes.py --family 01_urban --apply --install
scenarios/analysis/.venv/bin/python scenarios/setup/audit_helsinki_urban_settings.py --rename-u2 --apply
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps HelsinkiDowntown --validation
scenarios/analysis/.venv/bin/python scenarios/setup/render_wiki_map_previews.py --maps HelsinkiDowntown --paper-ready
bash scenarios/setup/bootstrap_maps.sh --install
```

## Deliverables index

| Artifact | Location |
|----------|----------|
| Asset inventory | `scenarios/analysis/data/maps/HelsinkiDowntown_asset_inventory.csv` |
| Geometry validation | `scenarios/analysis/data/maps/HelsinkiDowntown_geometry_validation.csv` |
| POI validation / corrections | `scenarios/analysis/data/maps/HelsinkiDowntown_poi_*.csv` |
| Bus validation / corrections | `scenarios/analysis/data/maps/HelsinkiDowntown_bus_route_*.csv` |
| Settings audit | `scenarios/analysis/data/maps/HelsinkiDowntown_urban_settings_audit.csv` |
| Affected scenarios | `scenarios/analysis/data/maps/HelsinkiDowntown_affected_scenarios.csv` |