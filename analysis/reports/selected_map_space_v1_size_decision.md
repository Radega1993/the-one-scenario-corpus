# Selected map space v1 — size decision

Generated: 2026-06-22T10:15:23.962033+00:00

- **Official method:** `hybrid`
- **Official N:** 75
- **Constraints satisfied:** True

## Rationale

elbow at n=75: marginal max_distance improvement 0.038 < 0.05

## Paper-ready claim

> The selected map set is a representative subset of the saturated map-design pool. It preserves categorical coverage of the declared archetypes while reducing feature-space redundancy through diversity-based selection.

## Coverage metrics

```json
{
  "target_n": 75,
  "epsilon": "",
  "n_selected": 75,
  "mean_distance_to_selected": 0.9077715186241148,
  "median_distance_to_selected": 0.7593945014062968,
  "p95_distance_to_selected": 2.350206395986264,
  "max_distance_to_selected": 5.672421006863205,
  "mean_pairwise_selected_distance": 9.94615408159435,
  "min_pairwise_selected_distance": 0.037507887813350876,
  "archetype_coverage": 15,
  "source_type_coverage": 3,
  "anchor_coverage": 18,
  "min_maps_per_archetype": 3,
  "max_single_archetype_fraction": 0.10666666666666667,
  "osm_fraction": 0.4533333333333333,
  "synthetic_fraction": 0.32,
  "trace_reference_synthetic_fraction": 0.22666666666666666,
  "outlier_preservation": 0.18867924528301888,
  "redundancy_within_selected": 0.05333333333333334,
  "constraints_satisfied": true
}
```
