# Pruning policies — scenario_space_v1

## strict (implemented)

Greedy pairwise Pearson correlation pruning:

- Accept scenario `i` iff `max_j |r(Z_i, Z_j)| < threshold` for all scenarios `j` already selected.
- Validation: every pair among the selected subset must satisfy `|r| < threshold`.

This is a **pairwise correlation-pruned subset**, not mathematical linear independence.

## balanced (planned)

Goal: relax the strict zero-pairs-above-threshold rule when the design space collapses heavily under feature-based deduplication.

Proposed rule:

1. Start from the strict greedy pass (or a farthest-first variant).
2. Allow up to `max_pair_frac` (e.g. 5%) of selected pairs to exceed `threshold`, if and only if:
   - coverage gaps are filled across `map_id`, `movement_model_primary`, `density_bin`, and `group_structure`;
   - the added scenario improves the minimum retention across under-represented cells in `coverage_audit.csv`.
3. Report both `pairs_above_threshold` and per-dimension retention in the paper.

Selection objective (TBD): maximize minimum cell retention subject to `pairs_above_threshold / C(n,2) <= max_pair_frac`.

CLI sketch:

```bash
python3 scenarios/setup/prune_scenario_space_v1.py \
  --policy balanced \
  --threshold 0.7 \
  --max-pair-frac 0.05
```

Not implemented yet; use `--policy strict` for reproducible runs.
