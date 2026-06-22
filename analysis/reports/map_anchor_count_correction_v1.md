# Map anchor count correction (v1)

**Date:** 2026-06-22  
**Auditor:** automated inventory from `map_design_space_saturation_v1.yaml` + `export_map_anchor_inventory_v1.py`

---

## Summary

| Metric | Previous (incorrect) | Corrected |
|--------|----------------------|-----------|
| Declared anchors in YAML | 20 | **19** |
| OSM-downloadable anchors | 16 | **15** |
| Trace-only anchors | 4 | **4** (unchanged) |
| Anchors with ≥1 valid map | 19 (labeled "20") | **19** (N=1200 and N=2000) |
| Synthetic without anchor | 337 @1200 | **570** @2000 |

---

## Root cause

1. **Manual miscount:** Several documents rounded or duplicated an OSM anchor when summarizing the YAML, producing "20 declared" and "16 OSM" without re-parsing `real_anchors.anchors`.
2. **Conflation with `valid_anchors_covered`:** `map_space_saturation_decision.json` reports `valid_anchors_covered: 19`, which equals the **full declared set** (all 19 anchors had valid maps at N=1200). This was misread as "20 declared, 19 covered" instead of "19 declared, 19 covered".
3. **Stale internal list:** Section "Las 20 anclas" in the internal Spanish doc listed **15** OSM rows + 4 trace = 19 visible entries while the header said 20/16.

**Authoritative source:** [`map_design_space_saturation_v1.yaml`](../config/map_design_space_saturation_v1.yaml) — exactly **19** entries under `real_anchors.anchors`.

[`real_map_anchors_v1.md`](real_map_anchors_v1.md) was already correct (15 OSM + 4 trace = 19).

---

## Canonical anchor table (19)

| # | anchor_id | anchor_type | archetype |
|---|-----------|-------------|-----------|
| 1 | helsinki_downtown | osm_bbox | dense_urban_irregular |
| 2 | kumpula_campus | osm_bbox | campus_compact |
| 3 | kallio_community | osm_bbox | compact_residential |
| 4 | manhattan_midtown | osm_bbox | urban_grid |
| 5 | sf_cabspotting_downtown | osm_bbox | dense_urban_irregular |
| 6 | sf_mission_corridor | osm_bbox | corridor_linear |
| 7 | dieselnet_amherst | osm_place | bus_route_urban_suburban |
| 8 | cambridge_haggle | osm_bbox | dense_urban_irregular |
| 9 | mit_campus_reality | osm_bbox | campus_compact |
| 10 | infocom_event_compact | trace_reference_not_map | conference_event_compact |
| 11 | infocom_2006_trace | trace_reference_not_map | conference_event_compact |
| 12 | rollernet_trace | trace_reference_not_map | corridor_linear |
| 13 | haggle_contacts_only | trace_reference_not_map | clustered_communities |
| 14 | nuuksio_sparse_trails | osm_bbox | sparse_trails |
| 15 | lapland_rural_sparse | osm_bbox | rural_roads |
| 16 | helsinki_disrupted | osm_bbox | industrial_disrupted |
| 17 | helsinki_archipelago | osm_bbox | island_or_partitioned |
| 18 | london_industrial_corridor | osm_bbox | industrial_disrupted |
| 19 | tampere_suburban | osm_bbox | suburban_low_density |

Machine-readable: [`map_anchor_inventory_v1.csv`](../data/map_anchor_inventory_v1.csv)

---

## Reporting rule (going forward)

Always report separately:

1. **`declared_anchors_in_yaml`** — count from YAML (currently 19)
2. **`osm_downloadable_anchors`** — `osm_bbox` + `osm_place` (currently 15)
3. **`trace_reference_anchors`** — `trace_reference_not_map` (currently 4)
4. **`anchors_with_valid_maps`** — from features CSV crosswalk (empirical; **19** at N=1200 and N=2000)
5. **`synthetic_maps_without_anchor`** — valid maps with empty `anchor_id` (**570** at N=2000)

Do **not** use `valid_anchors_covered` as a proxy for "declared minus one".

---

## Files updated in this correction

- `scenarios/analysis/data/map_anchor_inventory_v1.csv` (new)
- `scenarios/analysis/reports/map_anchor_inventory_v1.md` (new)
- `scenarios/analysis/reports/map_anchor_count_correction_v1.md` (this file)
- `scenarios/internal/map_space_saturation_archetypes_and_results_v1.md`
- `scenarios/internal/map_generation_phase1_documentation_v1.md`
- `scenarios/analysis/reports/paper_ready_map_generation_section_v1.md`
- `scenarios/analysis/reports/map_generation_stop_decision_v1.md`
- `scenarios/analysis/reports/map_generation_extension_1200_2000_v1.md` (new)
- `scenarios/analysis/reports/map_space_saturation_methodology_final.md` (new)
- `scenarios/analysis/reports/INDEX_MAP_GENERATION_PHASE1_FINAL.md`
- `scenarios/setup/export_map_anchor_inventory_v1.py` (new)
- `scenarios/setup/run_saturation_extension_1600_2000.sh` (new)

---

*Anchor count correction v1 — Phase 1 map generation*
