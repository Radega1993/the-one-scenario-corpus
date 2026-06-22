# Intra-archetype saturation analysis (v1)

Generated: 2026-06-22 09:22 UTC

## Purpose

For each of the 15 declared archetypes, this report measures **internal** diversity in raw feature space (sub-z-score within archetype): unique vectors, internal k-medoids clusters, nearest-neighbour distances, and near-redundancy (NN &lt; 0.25).

Global feature-space saturation at N = 1200 is documented in `map_space_saturation_report.md`. This analysis answers whether any single archetype remains undersampled or collapsed.

## Status rules

| Status | Criterion |
|--------|-----------|
| WELL_COVERED | n ≥ 40, near_redundant_fraction &lt; 0.35, n_clusters_internal ≥ 3 |
| ACCEPTABLE | n ≥ 30 |
| LOW_SAMPLE_BUT_ACCEPTABLE | n &lt; 30 with OSM-only or trace-backed justification |
| NEEDS_MORE_GENERATION | otherwise |

## Results

| Archetype | n_valid | n_unique | n_clusters | mean_nn | near_red_frac | status |
|-----------|---------|----------|------------|---------|---------------|--------|
| urban_grid | 108 | 108 | 10 | 0.694 | 0.204 | WELL_COVERED |
| dense_urban_irregular | 199 | 199 | 14 | 0.593 | 0.407 | ACCEPTABLE |
| campus_compact | 109 | 109 | 10 | 0.463 | 0.679 | ACCEPTABLE |
| compact_residential | 41 | 41 | 6 | 0.407 | 0.341 | WELL_COVERED |
| corridor_linear | 100 | 100 | 10 | 0.510 | 0.460 | ACCEPTABLE |
| bus_route_urban_suburban | 38 | 38 | 6 | 0.425 | 0.526 | ACCEPTABLE |
| radial_city | 72 | 72 | 8 | 2.248 | 0.000 | WELL_COVERED |
| hub_and_spoke | 75 | 75 | 9 | 1.310 | 0.000 | WELL_COVERED |
| sparse_trails | 116 | 116 | 11 | 0.838 | 0.466 | ACCEPTABLE |
| rural_roads | 62 | 62 | 8 | 1.478 | 0.548 | ACCEPTABLE |
| industrial_disrupted | 158 | 158 | 13 | 0.678 | 0.354 | ACCEPTABLE |
| island_or_partitioned | 117 | 117 | 11 | 0.728 | 0.256 | WELL_COVERED |
| conference_event_compact | 75 | 75 | 9 | 1.442 | 0.053 | WELL_COVERED |
| clustered_communities | 75 | 75 | 9 | 2.183 | 0.000 | WELL_COVERED |
| suburban_low_density | 33 | 33 | 5 | 0.161 | 0.879 | ACCEPTABLE |

## Interpretation

- Minimum sample size: **33** (`suburban_low_density`).
- Archetypes flagged NEEDS_MORE_GENERATION: **none**.
- With global saturation confirmed at batch 1200, per-archetype counts of 33–169 are sufficient: further batch growth added mostly near-redundant maps in the **global** pool (≥50% redundant/invalid in post-800 tranches).
- OSM-only archetypes (`compact_residential`, `suburban_low_density`) have no dedicated synthetic generator by design; their sample sizes reflect anchor variant policy, not generator failure.

## Figures

- `saturation_by_archetype_valid_maps.png`
- `saturation_by_archetype_nn_distance.png`
- `saturation_by_archetype_clusters.png`
