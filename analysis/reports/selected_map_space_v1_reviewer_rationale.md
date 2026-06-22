# Selected map space v1 — reviewer rationale (FAQ)

## Why prune 1055 maps?

Generating structural scenarios (movement × density × groups × network parameters) for every saturated map is computationally prohibitive. Many maps are near-redundant in normalised topology feature space after Phase 1 saturation. A **representative subset** preserves design-space coverage while making the scenario phase tractable.

## Why is this not subjective?

1. **Declared policy** (`selected_map_space_v1_policy.yaml`) fixes pool, features, constraints, and methods before selection.
2. **Multiple methods** compared on the same feature matrix and seed.
3. **Hard constraints** (15 archetypes, 3 source types, fraction bounds) filter invalid subsets.
4. **Data-driven N** via elbow on coverage metrics — not a pre-fixed count.
5. **Post-hoc audit** (`audit_selected_map_space_v1.py`) verifies pool→selected distances and category balance.

## What is preserved?

- All **15 declared archetypes** (≥3 maps each at N=75)
- All **3 source types** (OSM, synthetic, trace-reference synthetic)
- **19 anchors** represented in the official set
- **Topological outliers** via hybrid outlier pass and farthest-point diversity
- **Real OSM** and **controlled synthetic** maps

## What is the correct claim?

**Use:**

> The selected map set is a representative subset of the saturated map-design pool. It preserves categorical coverage of the declared archetypes while reducing feature-space redundancy through diversity-based selection.

**Do not use:**

> The selected maps cover all maps in the world.

## Why 1200 pool and not 2000?

Phase 1 extension to 2000 confirmed saturation at 1200 (`stop_at_1200_confirmed_by_2000`). Post-1200 maps are robustness evidence, not part of the design pool for pruning.

## Relationship to scenarios (next phase)

```
selected maps (75)
    × movement models
    × node densities
    × group structures
    × network parameters
    → structural scenario space
```

Input manifest: `scenarios/selected_map_space_v1/manifest_selected_maps.csv`
