# Real Map Anchors v1 — Classification Report (Fase 2)

**Config:** [`real_map_anchors_v1.yaml`](../config/real_map_anchors_v1.yaml)  
**Date:** 2026-06-14

---

## Purpose

This catalog grounds `map_space_v1` in literature- and dataset-known environments. It separates:

1. **Downloadable OSM maps** (`osm_bbox`, `osm_region_or_reference`)
2. **Contact traces without reliable geography** (`trace_reference_not_map`)
3. **Synthetic maps parameterized by traces** (`trace_reference_synthetic` at generation time)

---

## Classification summary

| anchor_id | anchor_type | Map action | Archetype |
|-----------|-------------|------------|-----------|
| helsinki_downtown | osm_bbox | OSM download | dense_urban_irregular |
| kumpula_campus | osm_bbox | OSM download | campus_compact |
| kallio_community | osm_bbox | OSM download | compact_residential |
| helsinki_disrupted | osm_bbox | OSM download | industrial_disrupted |
| nuuksio_sparse_trails | osm_bbox | OSM download | sparse_trails |
| manhattan_midtown | osm_bbox | OSM download | urban_grid |
| sf_cabspotting_downtown | osm_bbox | OSM download | dense_urban_irregular |
| sf_mission_corridor | osm_bbox | OSM download | corridor_linear |
| dieselnet_amherst | osm_region_or_reference | OSM download (Amherst bbox) | bus_route_urban_suburban |
| cambridge_haggle | osm_bbox | OSM download | dense_urban_irregular |
| mit_campus_reality | osm_bbox | OSM download | campus_compact |
| lapland_rural_sparse | osm_bbox | OSM download | rural_roads |
| tampere_suburban | osm_bbox | OSM download | suburban_low_density |
| helsinki_archipelago | osm_bbox | OSM download (partitioned OK) | island_or_partitioned |
| london_industrial_corridor | osm_bbox | OSM download | industrial_disrupted |
| infocom_event_compact | trace_reference_not_map | **Synthetic only** | conference_event_compact |
| infocom_2006_trace | trace_reference_not_map | **Synthetic only** | conference_event_compact |
| rollernet_trace | trace_reference_not_map | **Synthetic only** | corridor |
| haggle_contacts_only | trace_reference_not_map | **Synthetic only** | clustered_communities |

**Total:** 15 OSM-downloadable anchors + 4 trace-only references = 19 anchors.

---

## OSM-downloadable anchors (15)

These produce `source_type: osm` candidates via `generate_map_space_v1.py`:

- Exact anchor bbox (window = anchor extent)
- Controlled offset variants around anchor centre
- Window sizes: 500–5000 m per `map_design_space_v1.yaml` rules

Legacy 6 maps map 1:1 to anchors: `helsinki_downtown`, `kumpula_campus`, `manhattan_midtown`, `nuuksio_sparse_trails`, `helsinki_disrupted`, `kallio_community`.

New geographic diversity: SF (2), Amherst/DieselNet, Cambridge, MIT, Lapland, Tampere, Helsinki archipelago, London industrial.

---

## Contact traces — not direct maps (4)

### INFOCOM/Info5 (`infocom_event_compact`)

- **Dataset:** INFOCOM 2005 iMote contact trace
- **Not a map:** Venue coordinates are not used as OSM bbox without documented venue
- **Action:** Generate `conference_event_compact` synthetic maps with `source_type: trace_reference_synthetic` and `anchor_id: infocom_event_compact`

### INFOCOM 2006 (`infocom_2006_trace`)

- Same treatment as Info5; second conference-event synthetic family member.

### RollerNet (`rollernet_trace`)

- Sparse mobile contacts; parametrizes `corridor` / sparse synthetics.

### Haggle contacts-only (`haggle_contacts_only`)

- Geographic map provided separately by `cambridge_haggle` OSM anchor
- This anchor drives `clustered_communities` synthetic parameterization from social contact density patterns

---

## Synthetic-only archetypes from traces

| Generator | Trace anchor | Justification |
|-----------|--------------|---------------|
| conference_event_compact | infocom_* | Compact venue layout, high local density, short paths |
| corridor (params) | rollernet_trace | Linear mobility pattern |
| clustered_communities | haggle_contacts_only | Community clusters with sparse inter-links |

---

## Dataset basis references

| Anchor | Literature / dataset |
|--------|---------------------|
| Helsinki* | The ONE simulator tradition, Keränen et al. |
| Manhattan | NYC Taxi, grid vehicular DTN |
| SF Cabspotting | Piorkowski et al., UC Berkeley Cabspotting |
| DieselNet/Amherst | UMass DieselNet, PVTA bus traces |
| Cambridge/Haggle | Haggle project, Cambridge iMote traces |
| MIT Reality | Eagle & Pentland, Reality Mining |
| INFOCOM/Info5 | Chaintreau et al., INFOCOM 2005 contact traces |
| Nuuksio | Finnish trail / rural OppNet scenarios |

---

## Claims

**Allowed:** real-trace-inspired map anchors; OSM-based anchors from documented bboxes; synthetic topology for trace-only datasets.

**Prohibited:** Claiming INFOCOM/Info5 is a downloaded geographic map; claiming complete Earth coverage.
