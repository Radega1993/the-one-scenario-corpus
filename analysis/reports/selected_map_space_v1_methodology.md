# Selected map space v1 — methodology

## Scope

Representative map selection (Phase 2) prunes the Phase 1 **official pool @1200**: 1055 valid maps (`batch_target ≤ 1200`, PASS/WARNING/STRESS). Maps added only in the 1600–2000 robustness extension are excluded.

## Feature space

- Numeric topology features from `extract_map_space_saturation_features.py` (`NUMERIC_FEATURE_COLUMNS`, 33 dims).
- **Z-score normalisation recomputed on the 1055-map pool only** (not the global 1378 @2000 normalisation).
- One-hot encoding of `source_type` (osm, synthetic, trace_reference_synthetic) appended when `include_source_type_one_hot: true`.
- Final matrix dimension: **36**.

## Distance metric

L2 Euclidean distance in the combined feature matrix (`pairwise_l2` from Phase 1 analysis utilities).

## Selection methods

| Method | Description |
|--------|-------------|
| **kmedoids** | Global k-medoids (k-means++ init + local medoid swap) |
| **farthest** | Farthest-point sampling from pool centroid |
| **epsilon-cover** | Greedy cover until all pool points within ε of some selected map |
| **stratified-kmedoids** | Per-archetype quotas (min 2) + intra-archetype k-medoids |
| **hybrid** | Min 3/archetype (if N≥45), intra medoids, global outliers, source-type-balanced FPS |

## Hard constraints (policy YAML)

- 15/15 archetypes represented
- 3/3 source types represented
- `min_maps_per_archetype ≥ 2`
- OSM fraction ∈ [0.25, 0.60]; synthetic ≥ 0.25; trace ≥ 0.05
- `max_single_archetype_fraction ≤ 0.15`
- `max_single_anchor_fraction ≤ 0.10`

## Size decision

Grid: N ∈ {30, 45, 60, 75, 90, 120} × methods; epsilon-cover ε ∈ {0.20…0.50}.

Official method: **hybrid** (fallback stratified-kmedoids). Official N chosen by **elbow** on `max_distance_to_selected`: smallest N where marginal improvement vs previous tier < 5% and constraints hold.

**Result:** N = **75**, `constraints_satisfied: true` (see `selected_map_space_v1_decision.json`).

## Outputs

- Official set: `scenarios/selected_map_space_v1/` (manifest, features, WKT copies)
- Experiments: `selected_map_space_v1_selection_experiments.csv`
- Audit: `selected_map_space_v1_coverage_report.md`

## Claim (limited)

> The selected map set is a representative subset of the saturated map-design pool. It preserves categorical coverage of the declared archetypes while reducing feature-space redundancy through diversity-based selection.

This does **not** claim worldwide map coverage.
