# Map archetype separability analysis (v1)

Generated: 2026-06-22 09:22 UTC

## Purpose

This report quantifies how distinct the 15 declared map-topology archetypes are in **normalized feature space** (global z-score + `source_type` one-hot, N = 1378 valid maps). It supports the claim that archetypes are **categorical design-space cells**, not a requirement for perfect linear separability.

## Methodological interpretation (required)

1. **Perfect separation is not required.** Archetypes declare which topology families must appear at least once in the pool. Partial overlap in PCA or centroid space is expected when maps share scale or corridor structure.

2. **Archetypes are categorical coverage.** All 15 archetypes were represented from batch 100 onward (`archetype_coverage_frac = 1.0`). Further generation was driven by **feature-space saturation**, not by adding labels.

3. **Saturation is measured in features, not labels.** Stop rules use k-medoids clusters, nearest-neighbour distances, and near-redundancy fractions — none of which use `archetype` as an input to clustering.

4. **Close pairs are retained for DTN/OppNet reasons.** When centroid distances are small, archetypes remain separate because they encode different movement roles, literature anchors, or The ONE capability flags (WDM, bus routes, cluster overlay).

## Global summary

| Metric | Value |
|--------|-------|
| Valid maps | 1378 |
| Archetypes | 15 |
| Mean intra-archetype L2 (to centroid) | 3.4756 |
| Mean inter-archetype centroid L2 | 6.0344 |
| Global inter/intra ratio (centroid) | 1.736 |
| Overlap threshold (inter/intra ratio) | &lt; 1.2 |

## Five closest archetype pairs (by centroid L2)

| Archetype A | Archetype B | Centroid L2 | Inter/intra ratio |
|-------------|-------------|-------------|-------------------|
| dense_urban_irregular | industrial_disrupted | 0.9071 | 1.355 |
| bus_route_urban_suburban | suburban_low_density | 1.5065 | 1.460 |
| urban_grid | dense_urban_irregular | 1.6406 | 1.474 |
| urban_grid | industrial_disrupted | 1.7418 | 1.464 |
| dense_urban_irregular | campus_compact | 1.8336 | 1.554 |

## Potentially overlapping pairs (inter/intra ratio &lt; 1.2)

| Archetype A | Archetype B | Inter/intra ratio | Centroid L2 |
|-------------|-------------|-------------------|-------------|
| — | — | — | — |

## DTN rationale for close pairs

- **dense_urban_irregular ↔ compact_residential:** Similar urban density but residential archetype targets `community_score` and cluster-overlay scenarios (Kallio); irregular core targets WDM and taxi-style vehicular literature.

- **corridor_linear ↔ bus_route_urban_suburban:** Both score high on `corridor_score`; bus archetype adds DieselNet stop-corridor semantics and `supports_bus_route_candidate` — distinct for vehicular DTN benchmarks.

- **radial_city ↔ hub_and_spoke:** Both use radial motifs; radial_city models continuous ring plans, hub_and_spoke models sparse hotspot peripheries with higher dead-end structure.

- **sparse_trails ↔ rural_roads:** Both low density; trails emphasize `tree_like_score` and pedestrian Nuuksio legacy, rural roads emphasize vehicular Lapland sparsity.

## Figures

- `archetype_centroid_distance_heatmap.png` — pairwise centroid L2 distances
- `archetype_pca_projection.png` — 2D PCA coloured by archetype

## Outputs

- `map_archetype_centroid_distances.csv`
- `map_archetype_separability_summary.csv`

## Conclusion

Archetypes occupy overlapping but structurally motivated regions of feature space. The global inter/intra ratio (1.736) indicates measurable separation at the family level while allowing continuous intra-archetype variation. This is consistent with using archetypes for **coverage** and numeric features for **saturation**.
