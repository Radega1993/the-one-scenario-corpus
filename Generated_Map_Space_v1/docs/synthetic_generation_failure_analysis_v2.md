# Synthetic generation failure analysis v2

**Pool:** `scenarios/Generated_Map_Space_v1/` (engineering validation pool)
**Manifest:** `/home/raul/Documents/the-one/scenarios/Generated_Map_Space_v1/manifest_maps_all.csv`
**Degenerate count:** 51

## Policy

- Failed attempts remain in `manifest_maps_all.csv` (`FAIL_BUILD_SYNTHETIC_DEGENERATE`).
- Do **not** silently regenerate until PASS without recording failures (avoids survival bias).
- This analysis is required before completing remaining OSM downloads.

## Summary by generator

| Generator | Planned | OK | Degenerate | Rate | Main cause |
|-----------|--------:|---:|-----------:|-----:|------------|
| `bus_route_corridor` | 37 | 12 | 25 | 67.6% | too_few_edges (5 < 20) |
| `campus_compact` | 57 | 45 | 12 | 21.1% | too_few_nodes (14 < 20) |
| `clustered_communities` | 98 | 98 | 0 | 0.0% |  |
| `conference_event_compact` | 58 | 58 | 0 | 0.0% |  |
| `corridor` | 57 | 50 | 7 | 12.3% | too_few_edges (17 < 20) |
| `disrupted_grid` | 57 | 57 | 0 | 0.0% |  |
| `grid` | 37 | 37 | 0 | 0.0% |  |
| `hub_and_spoke` | 37 | 37 | 0 | 0.0% |  |
| `jittered_grid` | 37 | 37 | 0 | 0.0% |  |
| `partitioned_bridge` | 57 | 57 | 0 | 0.0% |  |
| `radial_city` | 36 | 29 | 7 | 19.4% | too_few_nodes (19 < 20) |
| `sparse_rural` | 57 | 57 | 0 | 0.0% |  |
| `tree_trails` | 36 | 36 | 0 | 0.0% |  |

## Degenerate by archetype

- `bus_route_urban_suburban`: 25
- `campus_compact`: 12
- `corridor_linear`: 7
- `radial_city`: 7

## Degenerate by source_type

- `synthetic`: 51

## Degenerate by error_notes

- `too_few_edges (17 < 20)`: 7
- `too_few_nodes (19 < 20)`: 7
- `too_few_nodes (16 < 20)`: 6
- `too_few_edges (19 < 20)`: 5
- `too_few_nodes (14 < 20)`: 5
- `too_few_edges (5 < 20)`: 4
- `too_few_edges (9 < 20)`: 4
- `too_few_nodes (18 < 20)`: 3
- `too_few_edges (16 < 20)`: 2
- `too_few_edges (13 < 20)`: 2
- `too_few_edges (10 < 20)`: 2
- `too_few_edges (11 < 20)`: 1
- `too_few_edges (6 < 20)`: 1
- `too_few_edges (7 < 20)`: 1
- `too_few_edges (12 < 20)`: 1

## Interpretation

All recorded degenerates in the current engineering pool are `source_type=synthetic` (not `trace_reference_synthetic`). Failures concentrate on generators whose discrete parameter extremes produce graphs below validation floors (`min_nodes=20`, `min_edges=20`):

- `bus_route_corridor`: sparse stop/corridor layouts at low `n_stops` / narrow corridors.
- `campus_compact`: few buildings × low path density → too few nodes.
- `corridor` / `radial_city`: extreme length/width or ring/spoke settings near minima.

### Recommended actions (before more generation)

1. Tighten discrete parameter ranges so mid/high settings always clear validation floors, **or**
2. Lower floors only with an explicit methodological note (not preferred), **or**
3. Keep ranges but treat degenerates as part of the design surface (documented attrition).

Do not drop failed rows from the manifest.

