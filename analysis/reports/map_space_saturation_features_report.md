# map_space_saturation_features_report.md

Generated: 2026-06-22T09:22:05.549928+00:00

## 1. Summary

- maps_with_features: 1378
- maps_excluded_fail: 622
- validation PASS: 1303
- validation WARNING: 0
- validation STRESS: 75

## 2. Features generated

- `world_size_x`: Simulation world width (m) from metadata.
- `world_size_y`: Simulation world height (m) from metadata.
- `world_area`: world_size_x * world_size_y.
- `bbox_width`: Road network bounding box width (m).
- `bbox_height`: Road network bounding box height (m).
- `useful_area`: Area of road bbox (m²).
- `useful_area_ratio`: useful_area / world_area.
- `n_nodes`: Unique graph nodes (rounded coordinates).
- `n_edges`: Unique undirected road segments.
- `total_road_length_m`: Sum of segment lengths (m).
- `road_density`: n_edges / world_area.
- `avg_edge_length_m`: Mean segment length (m).
- `median_edge_length_m`: Median segment length (m).
- `avg_degree`: 2|E|/|N|.
- `max_degree`: Maximum node degree.
- `dead_end_ratio`: Fraction of degree-1 nodes.
- `intersection_ratio`: Fraction of nodes with degree >= 3.
- `n_components`: Connected components.
- `largest_component_ratio`: Largest component size / n_nodes.
- `bridge_edges_count`: NetworkX bridge edges.
- `bridge_edges_ratio`: bridge_edges_count / n_edges.
- `articulation_points_count`: NetworkX articulation points.
- `articulation_points_ratio`: articulation_points_count / n_nodes.
- `graph_diameter_approx`: 2 × eccentricity from highest-degree node.
- `avg_shortest_path_approx`: Mean shortest path over random node pairs (sampled).
- `circuity_approx`: Mean shortest-path / Euclidean ratio (sampled pairs).
- `orientation_entropy`: Entropy of edge bearing histogram (36 bins).
- `gridness_score`: Fraction of edges aligned to N-S/E-W (±15°).
- `corridor_score`: Elongation of node point cloud (1 = line-like).
- `radial_score`: Hub concentration vs periphery.
- `partition_score`: 1 - largest_component_ratio when partitioned.
- `community_score`: Greedy modularity intra-community edge fraction.
- `tree_like_score`: Tree-likeness of largest component.
- `supports_map_based`: (categorical flag from archetype table)
- `supports_route_movement_candidate`: (categorical flag from archetype table)
- `supports_cluster_overlay`: (categorical flag from archetype table)
- `supports_wdm_candidate`: (categorical flag from archetype table)
- `supports_bus_route_candidate`: (categorical flag from archetype table)

## 3. Omitted features

- No per-map feature omissions recorded.

## 4. Sampling methodology

- `graph_diameter_approx`: 2 × eccentricity from highest-degree node (exact on sampled BFS tree).
- `avg_shortest_path_approx`: mean Dijkstra distance over up to 64 random node pairs (`sampling_seed` per map).
- `circuity_approx`: mean (shortest-path / Euclidean) over up to 64 pairs (seed+1).
- For graphs with n_nodes > 10_000, sample count reduced to 32.
- `community_score`: greedy modularity; NaN if algorithm fails.

## 5. Distribution by batch

- batch_0100: 84
- batch_0200: 85
- batch_0400: 172
- batch_0600: 180
- batch_0800: 175
- batch_1000: 181
- batch_1200: 178
- batch_1600: 165
- batch_2000: 158

## 6. Distribution by archetype

- dense_urban_irregular: 199
- industrial_disrupted: 158
- island_or_partitioned: 117
- sparse_trails: 116
- campus_compact: 109
- urban_grid: 108
- corridor_linear: 100
- clustered_communities: 75
- conference_event_compact: 75
- hub_and_spoke: 75
- radial_city: 72
- rural_roads: 62
- compact_residential: 41
- bus_route_urban_suburban: 38
- suburban_low_density: 33

## 7. Outliers (IQR method)

### road_density
- SYN_partitioned_bridge_none_1640: 0.0208
- SYN_partitioned_bridge_none_1617: 0.0207
- SYN_partitioned_bridge_none_1659: 0.0204
- SYN_partitioned_bridge_none_1913: 0.0174
- SYN_partitioned_bridge_none_1876: 0.0172

### dead_end_ratio
- SYN_tree_trails_none_0925: 0.6694
- SYN_tree_trails_none_0977: 0.6694
- SYN_tree_trails_none_1134: 0.6694
- SYN_tree_trails_none_1182: 0.6694
- SYN_tree_trails_none_1342: 0.6694

### n_nodes
- OSM_kallio_community_offset_n_5000m_200m_0034: 89016.0000
- OSM_kallio_community_offset_n_5000m_200m_0610: 89016.0000
- OSM_kallio_community_offset_n_5000m_500m_0462: 87098.0000
- OSM_kallio_community_offset_n_5000m_500m_1048: 87098.0000
- OSM_kallio_community_offset_n_5000m_1000m_0313: 81691.0000

### gridness_score
- (none detected)

## 8. Degenerate / suspect maps

- count: 0

## 9. Duplicate feature signatures

- duplicate_groups: 208
- max_group_size: 11
  - 11 maps: OSM_helsinki_archipelago_offset_s_1000m_200m_0003, OSM_helsinki_archipelago_offset_s_1000m_200m_0114, OSM_helsinki_archipelago_offset_s_1000m_200m_0224, OSM_helsinki_archipelago_offset_s_1000m_200m_0331...
  - 11 maps: OSM_helsinki_archipelago_offset_s_1000m_500m_0030, OSM_helsinki_archipelago_offset_s_1000m_500m_0141, OSM_helsinki_archipelago_offset_s_1000m_500m_0252, OSM_helsinki_archipelago_offset_s_1000m_500m_0357...
  - 11 maps: OSM_helsinki_disrupted_offset_w_1000m_200m_0005, OSM_helsinki_disrupted_offset_w_1000m_200m_0115, OSM_helsinki_disrupted_offset_w_1000m_200m_0225, OSM_helsinki_disrupted_offset_w_1000m_200m_0332...
  - 11 maps: OSM_helsinki_disrupted_offset_w_1000m_500m_0031, OSM_helsinki_disrupted_offset_w_1000m_500m_0142, OSM_helsinki_disrupted_offset_w_1000m_500m_0253, OSM_helsinki_disrupted_offset_w_1000m_500m_0358...
  - 11 maps: OSM_helsinki_downtown_exact_1000m_0m_0006, OSM_helsinki_downtown_exact_1000m_0m_0117, OSM_helsinki_downtown_exact_1000m_0m_0229, OSM_helsinki_downtown_exact_1000m_0m_0336...

## 10. Excluded FAIL maps

Documented in `map_space_saturation_features_excluded_fail.csv` (622 rows).

## 11. Recommendations

- Use `map_space_saturation_features_normalized.csv` for distance/cluster saturation metrics.
- FAIL maps are excluded from the primary feature-space; re-include only after re-validation.
- Duplicate OSM signatures are expected when variants share identical windows; dedupe in saturation analysis.
- Proceed to Phase 2: batch-wise saturation curves (n_clusters, max nearest distance, archetype coverage).

