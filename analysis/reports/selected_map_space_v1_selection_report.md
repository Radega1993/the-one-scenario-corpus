# Selected map space v1 — selection report

## Experiment summary

- **Pool:** 1055 maps @1200
- **Seed:** 42
- **Methods:** kmedoids, farthest, stratified-kmedoids, hybrid, epsilon-cover
- **Target sizes:** 30, 45, 60, 75, 90, 120
- **Epsilon grid:** 0.20, 0.25, 0.30, 0.35, 0.40, 0.50

Full results: [`selected_map_space_v1_selection_experiments.csv`](../data/selected_map_space_v1_selection_experiments.csv)

## Official decision

| Field | Value |
|-------|-------|
| Method | **hybrid** |
| N | **75** |
| Constraints satisfied | **true** |
| Reason | Elbow at n=75: marginal max_distance improvement 0.038 < 0.05 |

### Coverage at N=75 (hybrid)

| Metric | Value |
|--------|------:|
| mean_distance_to_selected | 0.908 |
| max_distance_to_selected | 5.672 |
| p95_distance_to_selected | 2.350 |
| archetype_coverage | 15/15 |
| source_type_coverage | 3/3 |
| anchor_coverage | 18 |
| min_maps_per_archetype | 3 |
| osm_fraction | 0.453 |
| synthetic_fraction | 0.320 |
| trace_fraction | 0.227 |

## Method comparison (constraint-satisfying runs)

| method | min N satisfying constraints | max_distance @ min N |
|--------|-----------------------------:|---------------------:|
| kmedoids | 75 | 4.623 |
| farthest | — (never satisfies min 2/archetype) | — |
| stratified-kmedoids | 30 | 18.726 |
| hybrid | 30 | 18.726 |

Hybrid satisfies constraints at N=30 but with high `max_distance`; elbow on the hybrid grid selects **N=75** (max_distance 5.672) as the cost/coverage trade-off before marginal gains fall below 5%.

## Epsilon-cover reference

Epsilon-cover runs produce variable N (not fixed target). See experiments CSV for `n_selected` per ε. Not chosen as official method because N is not directly comparable to scenario-cost grid.

## Figures

- `figures/selected_map_space_v1/coverage_vs_n.png`
- `figures/selected_map_space_v1/max_distance_vs_n.png`
- `figures/selected_map_space_v1/p95_distance_vs_n.png`
- `figures/selected_map_space_v1/source_type_balance_vs_n.png`
- `figures/selected_map_space_v1/archetype_coverage_vs_n.png`
- `figures/selected_map_space_v1/selection_method_comparison.png`
