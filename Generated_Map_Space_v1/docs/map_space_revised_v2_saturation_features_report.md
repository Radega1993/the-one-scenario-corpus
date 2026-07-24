# map_space_saturation_features_report.md

Generated: 2026-07-23T18:33:59.323418+00:00

## 1. Summary

- maps_with_features: 1860
- maps_excluded_fail: 140
- validation PASS: 1741
- validation WARNING: 0
- validation STRESS: 119

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

- batch_0100: 87
- batch_0200: 96
- batch_0400: 188
- batch_0600: 188
- batch_0800: 190
- batch_1000: 194
- batch_1200: 200
- batch_1600: 359
- batch_2000: 358

## 6. Distribution by archetype

- dense_urban_irregular: 273
- industrial_disrupted: 201
- campus_compact: 183
- clustered_communities: 162
- island_or_partitioned: 148
- rural_roads: 140
- corridor_linear: 136
- bus_route_urban_suburban: 127
- urban_grid: 103
- conference_event_compact: 96
- sparse_trails: 95
- hub_and_spoke: 61
- compact_residential: 53
- radial_city: 50
- suburban_low_density: 32

## 7. Outliers (IQR method)

### road_density
- v2_syn_partitioned_bridge_0191: 0.0374
- v2_syn_partitioned_bridge_0659: 0.0373
- v2_syn_partitioned_bridge_0347: 0.0371
- v2_syn_partitioned_bridge_0503: 0.0369
- v2_syn_partitioned_bridge_0035: 0.0367

### dead_end_ratio
- v2_syn_tree_trails_0025: 0.6694
- v2_syn_tree_trails_0077: 0.6694
- v2_syn_tree_trails_0129: 0.6694
- v2_syn_tree_trails_0181: 0.6694
- v2_syn_tree_trails_0233: 0.6694

### n_nodes
- v2_osm_kallio_community_offset_w_5000m_500m_0209: 93063.0000
- v2_osm_kallio_community_offset_w_5000m_500m_0549: 93063.0000
- v2_osm_kallio_community_offset_w_5000m_200m_0124: 92058.0000
- v2_osm_kallio_community_offset_w_5000m_200m_0464: 92058.0000
- v2_osm_kallio_community_offset_w_5000m_200m_0804: 92058.0000

### gridness_score
- (none detected)

## 8. Degenerate / suspect maps

- count: 1
  - v2_syn_bus_route_corridor_0104: n_edges=20 tree_like=0.7143 omissions=

## 9. Duplicate feature signatures

- duplicate_groups: 332
- max_group_size: 35
  - 35 maps: v2_syn_disrupted_grid_0382, v2_trs_oviedo_asturies_er_20160808_disrupted_grid_0003, v2_trs_oviedo_asturies_er_20160808_disrupted_grid_0012, v2_trs_oviedo_asturies_er_20160808_disrupted_grid_0021...
  - 33 maps: v2_trs_haggle_one_cambridge_city_complete_conference_event_compact_0001, v2_trs_haggle_one_cambridge_city_complete_conference_event_compact_0010, v2_trs_haggle_one_cambridge_city_complete_conference_event_compact_0019, v2_trs_haggle_one_cambridge_city_complete_conference_event_compact_0028...
  - 26 maps: v2_syn_corridor_0277, v2_syn_corridor_0433, v2_syn_corridor_0589, v2_syn_corridor_0745...
  - 16 maps: v2_syn_tree_trails_0012, v2_syn_tree_trails_0064, v2_syn_tree_trails_0116, v2_syn_tree_trails_0168...
  - 12 maps: v2_osm_cambridge_haggle_exact_500m_0m_0000, v2_osm_cambridge_haggle_exact_500m_0m_0085, v2_osm_cambridge_haggle_exact_500m_0m_0170, v2_osm_cambridge_haggle_exact_500m_0m_0255...

## 10. Excluded FAIL maps

Documented in `map_space_saturation_features_excluded_fail.csv` (140 rows).

## 11. Recommendations

- Use `map_space_saturation_features_normalized.csv` for distance/cluster saturation metrics.
- FAIL maps are excluded from the primary feature-space; re-include only after re-validation.
- Duplicate OSM signatures are expected when variants share identical windows; dedupe in saturation analysis.
- Proceed to Phase 2: batch-wise saturation curves (n_clusters, max nearest distance, archetype coverage).

