# Map Generator Refactor Audit (Fase 1)

**Date:** 2026-06-14  
**Scope:** `scenarios/setup/` map pipeline — legacy 6-map corpus vs `map_space_v1`  
**Frozen zones (not modified):** `corpus_v1/`, `base_scenarios/`, existing benchmark results

---

## Executive summary

The repository currently operates two parallel map pipelines:

1. **Legacy (6 manual maps):** `download_maps.sh` → `prepare_maps.py` → `validate_maps.py` → `data/`
2. **New (`map_space_v1`):** `generate_map_space_v1.py` → `validate_map_space_v1.py` → `prune_map_space_v1.py` → selected manifest

The structural scenario generator (`generate_scenario_space_v1.py`) still reads only the 6 legacy maps from `data/` and hardcoded YAML. This audit documents what must change for anchor-based, reproducible map-topology coverage.

---

## Hardcoded elements

### MAP_DEFS (6 maps, triplicated)

| File | Symbol | Maps |
|------|--------|------|
| [`map_config.py`](../setup/map_config.py) | `MAP_DEFS` | 6 |
| [`prepare_maps.py`](../setup/prepare_maps.py) | `MAP_DEFS` (duplicate) | 6 |
| [`download_maps.sh`](../setup/download_maps.sh) | inline Python `MAP_DEFS` | 6 |

Each entry: `bbox`, `crs`, `family`, `network_type`, `poi_density`. Families `01_urban` … `06_social` are fixed.

**Action:** Mark legacy; single source of truth moves to `real_map_anchors_v1.yaml` + `map_design_space_v1.yaml`.

### ACTIVE_MAPS (6 names)

Defined in [`map_geometry.py`](../setup/map_geometry.py) and imported by:

- `build_map_assets_inventory.py`
- `build_map_route_semantic_inventory.py`
- `calibrate_world_size_per_map.py`
- `render_wiki_map_previews.py`
- `repair_bus_routes.py`
- `validate_bus_routes.py`
- `validate_map_pois.py`
- `regenerate_family_routes.py`

**Action:** Legacy scripts keep `ACTIVE_MAPS`; new pipeline uses `manifest_maps.csv` / `manifest_maps_selected.csv`.

### Family-based validation assumptions

- `FAMILY_THRESHOLD_M` in `map_geometry.py` — snap thresholds per `01_urban` … `06_social`
- `prepare_maps.py` always generates WDM POIs (`A_homes`, `A_offices`, `A_meetingspots`) and bus routes for every map
- `scenario_space_settings_builder.py` — `MAP_ALLOWED_MODELS` and `MAP_ASSETS` keyed by 6 legacy names only

**Action:** Conditional asset policy (`map_asset_policy_v1.yaml`); manifest-driven movement compatibility.

### `generate_map_space_v1.py` blockers

| Issue | Location | Impact |
|-------|----------|--------|
| `hash((seed, *parts))` | `_pick_rng`, synthetic RNG | Non-reproducible across Python runs |
| `region_pools` random bbox | `iter_osm_candidates` | OSM without literature anchor |
| `graph_from_bbox(bbox=(north,south,east,west))` | `_download_osm_graph` | Wrong order for OSMnx v2 `(west,south,east,north)` |
| Missing manifest columns | `MANIFEST_COLUMNS` | No `anchor_id`, `dataset_basis`, `n_nodes`, `n_edges` |
| `region_pool` in metadata | `write_metadata` | Should be `anchor_id` |

**Action:** Fase 4 refactor (stable seeds, anchor-based OSM, OSMnx compat wrapper).

### `scenario_design_space_v1.yaml`

Dimension `maps` lists 6 fixed entries with `world_size_x/y`, `allowed_movement_models`.

**Action:** Externalize to `--maps-manifest` (Fase 8).

### `bootstrap_maps.sh`

Single path: download → prepare → validate (legacy). No `map_space_v1` branch.

**Action:** Add documented parallel entry point; keep legacy intact.

---

## Reusable components (keep)

| Module | Role |
|--------|------|
| [`map_geometry.py`](../setup/map_geometry.py) | WKT I/O, sim coords, `world_size_from_sim_roads`, road graph |
| [`map_space_topology.py`](../setup/map_space_topology.py) | Feature extraction, map discovery |
| [`map_space_synthetic.py`](../setup/map_space_synthetic.py) | Synthetic generators (extend with 3 archetypes) |
| [`validate_map_space_v1.py`](../setup/validate_map_space_v1.py) | Validation pipeline |
| [`extract_map_features_v1.py`](../setup/extract_map_features_v1.py) | Feature CSV |
| [`prune_map_space_v1.py`](../setup/prune_map_space_v1.py) | Feature-space pruning |
| [`seed_osm_cache_from_legacy.py`](../setup/seed_osm_cache_from_legacy.py) | Offline OSM fallback only |
| [`repair_map_pois.py`](../setup/repair_map_pois.py) | POI snap repair |
| [`validate_bus_routes.py`](../setup/validate_bus_routes.py) | Route validation |

---

## Move to YAML/CSV

| Data | Target file |
|------|-------------|
| Real geographic anchors | `real_map_anchors_v1.yaml` |
| OSM window sizes, variant offsets, synthetic params | `map_design_space_v1.yaml` |
| POI/route generation rules | `map_asset_policy_v1.yaml` |
| Generated map pool | `map_space_v1/manifest_maps.csv` |
| Selected maps | `map_space_v1/selected_maps/manifest_maps_selected.csv` |
| Validation/features | `analysis/data/map_space_v1_*.csv` |

---

## Pipeline classification

### Legacy (retain for backward compatibility)

```
bootstrap_maps.sh
  → download_maps.sh (MAP_DEFS)
  → prepare_maps.py (MAP_DEFS + always POIs/routes)
  → validate_maps.py
  → data/{HelsinkiDowntown,...}/
```

Used by: frozen `corpus_v1`, existing papers referencing 6 maps.

### New pipeline (primary for structural corpus v2)

```
real_map_anchors_v1.yaml
  → map_design_space_v1.yaml
  → generate_map_space_v1.py (--generate)
  → map_asset_generator_v1.py (conditional POIs/routes)
  → validate_map_space_v1.py
  → extract_map_features_v1.py
  → prune_map_space_v1.py
  → install_selected_maps_v1.py
  → generate_scenario_space_v1.py --maps-manifest
```

Traffic Profiles applied **later** — not in this pipeline.

---

## Risks

| Risk | Mitigation |
|------|------------|
| Overpass rate limits / connection refused | Retries, cache per `map_id`, `seed_osm_cache_from_legacy.py` as `--offline-fallback` |
| `hash()` breaks cross-run reproducibility | `stable_seed()` via SHA-256 |
| OSMnx v1/v2 API drift | `graph_from_bbox_compat()` version detection |
| POIs on non-WDM maps | `map_asset_policy_v1.yaml` + validation check |
| Hub-and-spoke / clustered_communities too sparse | Tune discrete parameters; min edge count guard |
| Scenario generator assumes 6 maps | `--maps-manifest` with legacy fallback |
| Duplicate OSM topology from legacy cache | Regenerate from real anchors (user decision) |

---

## Recommended next steps

1. Publish `real_map_anchors_v1.yaml` (Fase 2)
2. Redesign `map_design_space_v1.yaml` — anchor-based OSM, no random region pools (Fase 3)
3. Refactor `generate_map_space_v1.py` (Fase 4) and regenerate pool
4. Conditional assets (Fase 5), validation extensions (Fase 6)
5. Prune to 60 + `install_selected_maps_v1.py` (Fase 7)
6. Wire scenarios (Fase 8), document claims (Fase 9)
