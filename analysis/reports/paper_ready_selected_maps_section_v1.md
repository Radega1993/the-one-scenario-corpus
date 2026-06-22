# Paper-ready section — Map selection (v1)

## Map subset selection

From the saturated map-design pool (1,055 valid maps at batch ≤1,200), we selected a representative subset for structural scenario generation. Selection used normalised topology features (33 numeric descriptors plus source-type indicators) with z-scores computed on the pool subset only. We compared k-medoids, farthest-point sampling, epsilon-cover, stratified k-medoids, and a hybrid stratified-diversity method under explicit coverage constraints: all 15 declared archetypes, all three source types (OSM, synthetic, trace-reference synthetic), minimum maps per archetype, and bounds on OSM/synthetic/trace fractions.

The official subset (N=75, hybrid method, seed 42) was chosen where marginal reduction in maximum feature-space distance to the nearest selected map fell below 5% relative to the next smaller grid size, subject to constraint satisfaction. Post-selection audit confirmed 15/15 archetype coverage, 3/3 source-type coverage, and mean/median/p95 distances to the nearest selected representative.

**Claim (limited scope):** The selected map set is a representative subset of the saturated map-design pool. It preserves categorical coverage of the declared archetypes while reducing feature-space redundancy through diversity-based selection. This does not claim coverage of all real-world road networks.

## Inputs for scenario design

The manifest `manifest_selected_maps.csv` lists 75 maps with WKT geometry, metadata, and selection roles. This set is the map factor level for the forthcoming structural scenario space.
