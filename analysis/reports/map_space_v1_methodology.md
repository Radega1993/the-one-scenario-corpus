# map_space_v1 Methodology

**Version:** 1.0 (anchor-based)  
**Date:** 2026-06-14

## Defensible claim

> The selected maps form an approximate ε-cover of the generated map-topology design space under normalized feature distance. Completeness is defined with respect to the **declared design space**, not all environments on Earth.

## Design space components

### 1. Real OSM anchors (15)

Documented bboxes from literature and The ONE tradition. See [`real_map_anchors_v1.yaml`](../config/real_map_anchors_v1.yaml).

Each anchor generates:
- **Exact** window at anchor centre
- **Offset variants** (N/E/S/W, 200–1500 m)
- Window sizes: 500–5000 m by `expected_use`

### 2. Trace references (4) — not maps

INFOCOM/Info5, INFOCOM 2006, RollerNet, Haggle-contacts-only parameterize **synthetic** generators (`conference_event_compact`, etc.). No OSM download.

### 3. Synthetic generators (14)

Controlled topology: grid, jittered_grid, radial_city, hub_and_spoke, corridor, tree_trails, sparse_rural, clustered_communities, partitioned_bridge, disrupted_grid, conference_event_compact, campus_compact, bus_route_corridor, multi_component_with_bridges.

## Pipeline

1. **Generate** 600 candidates (`--seed 42`, stable seeds)
2. **Validate** PASS/WARNING/STRESS/FAIL
3. **Extract** 23 topology features + `community_score`
4. **Prune** to 60 (k-medoids / epsilon-cover + anchor quotas)
5. **Install** to `data/` with conditional assets
6. **Scenarios** via `--maps-manifest` (no Traffic Profiles)

## Allowed claims

- explicit map-topology design space
- real-trace-inspired map anchors
- OSM-based real map anchors
- synthetic topology generators
- feature-space diversity
- epsilon-cover approximation
- scenario generation over selected maps
- Traffic Profiles applied later

## Prohibited claims

- all possible situations on Earth
- all possible real-world maps
- complete representation of reality
- mathematically complete Earth coverage
- linearly independent scenarios

## Commands

```bash
python3 scenarios/setup/generate_map_space_v1.py --estimate-only
python3 scenarios/setup/generate_map_space_v1.py --generate --max-maps 600 --seed 42 --force
python3 scenarios/setup/validate_map_space_v1.py --update-manifest --extract-features
python3 scenarios/setup/prune_map_space_v1.py --method epsilon-cover --target-n 60 --seed 42
python3 scenarios/setup/install_selected_maps_v1.py
python3 scenarios/setup/generate_scenario_space_v1.py --estimate-only \
  --maps-manifest scenarios/map_space_v1/selected_maps/manifest_maps_selected.csv
```
