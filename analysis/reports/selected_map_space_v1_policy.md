# Selected map space v1 — selection policy

## Why prune the 1055-map pool?

Phase 1 produced **1055 valid maps** at batch ≤1200. That pool is methodologically saturated but too large to cross with structural scenario dimensions (movement models, densities, groups, network parameters). Many maps are near-redundant in normalized topology feature space; scenario generation needs a **representative subset**, not the full saturated corpus.

## Why not pick an arbitrary count?

The official size **N** is not fixed a priori (not 60, 75, or 90 by decree). We grid-search **30–120** maps across five selection methods and apply an **elbow rule** on `max_distance_to_selected` once hard constraints are met. The smallest **N** with diminishing marginal coverage gain is preferred to limit downstream scenario cost.

## Why compare multiple sizes and methods?

Different methods trade off global medoid coverage, outlier preservation, and stratified archetype quotas. Comparing **k-medoids**, **farthest-point sampling**, **epsilon-cover**, **stratified k-medoids**, and **hybrid stratified diversity** makes the choice auditable and reviewer-defensible.

## Archetype minimums

All **15 declared archetypes** must appear in the selection. Policy enforces at least **2 maps per archetype** (3 preferred when N≥45 in the hybrid method). This prevents a diversity-optimal but category-blind subset from dropping rare topologies.

## Outlier preservation

Topological outliers (high distance to the pool centroid or to medoids) are explicitly added in hybrid selection so the subset does not collapse to dense urban “modes” only.

## Manageability for scenarios

Each selected map may spawn multiple structural scenarios. Keeping **N** at the constraint-satisfying elbow minimises compute while preserving declared design-space coverage.

## Pool boundary

Selection uses **batch_target ≤ 1200** only. Maps valid only in the 1600–2000 robustness extension are excluded from the pool (see `map_selection_pool_v1_audit.md`).

## Official decision workflow

1. Run experiments (`--run-experiments`).
2. Filter rows with `constraints_satisfied == true`.
3. Prefer **hybrid**; fallback **stratified-kmedoids**.
4. Apply elbow on `max_distance_to_selected` (5% marginal improvement threshold).
5. Write `selected_map_space_v1_decision.json` and generate official set.
