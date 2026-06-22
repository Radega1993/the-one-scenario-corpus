# Map Asset Policy v1 (Fase 5)

**Config:** [`map_asset_policy_v1.yaml`](../config/map_asset_policy_v1.yaml)

---

## Rationale

Legacy `prepare_maps.py` generates WDM POIs (`A_homes`, `A_offices`, `A_meetingspots`) and bus routes for **every** map. Most `map_space_v1` candidates are topology probes — not all need auxiliary assets.

---

## POI generation

Generated **only when**:

- `archetype` ∈ `{dense_urban_irregular, campus_compact, compact_residential, conference_event_compact}`, or
- `expected_use` from anchor includes `wdm` / `campus` / `event`

POIs are snapped to road graph nodes (`snap_max_m: 500`).

**Not generated** for: rural trails, sparse synthetics, hub-and-spoke, radial grids (unless explicitly WDM-capable).

---

## Route generation

Generated **only when**:

- `archetype` supports vehicular/bus movement, or
- `expected_use` includes `vehicle`, `bus_routes`, `corridor`, `rural_patrol`

Route files are waypoint LINESTRINGs resolved by The ONE on `roads.wkt`.

Validation rules (via `validate_bus_routes.py`):

- Points within `worldSize`
- Snap distance &lt; 50 m
- Resolvable path on road graph
- Minimum length 200 m

---

## Movement compatibility

| Movement model | Required assets |
|----------------|-----------------|
| WorkingDayMovement | homes + offices + meetingspots |
| BusMovement | bus or vehicle route WKT |
| MapRouteMovement | any route WKT |
| ShortestPathMapBasedMovement | roads.wkt only |
| ClusterMovement | worldSize (roads optional) |

---

## Implementation

`map_asset_generator_v1.py` reads policy and manifest/metadata; invoked after WKT generation or during `install_selected_maps_v1.py` for selected maps only.
