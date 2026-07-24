# Pool Revalidation and Attrition Report — map_space_revised_v2

**Status:** official project state after Phase B OSM completion
**Pool:** `scenarios/Generated_Map_Space_v1/`
**Manifest rows:** 2000
**OK maps:** 1865 (93.2%)
**Documented failures:** 135 (83 synthetic degenerate + 52 OSM build)

## Methodological position

- The pool passed **engineering validation**; it is **not** yet the definitive Generated Map Space.
- It does **not** by itself justify SMS-v1 selection.
- `N=1200` remains an **initial engineering target**, not a scientific stopping rule.
- Failures remain in the manifest (no documentary survival bias).
- **Decisions:** do **not** repair the 32 `FAIL_BUILD_OSM` in bulk; do **not** regenerate solely to correct global source proportions; **do** check affected (archetype × source) coverage.

```mermaid
flowchart LR
  poolDone[Pool_completed]
  reval[Coverage_attrition_revalidation]
  sat[Incremental_saturation]
  expand[Conditional_1600_2000]
  sms[SMS_v1_selection]
  poolDone --> reval
  reval -->|go| sat
  sat -->|marginal_gain| expand
  sat -->|stable| sms
  expand --> sms
```

## 1. Coverage after attrition (archetype × source)

Survival rate \(r_{a,s} = N^{OK}_{a,s} / N^{planned}_{a,s}\). Planned counts are manifest attempts per cell.

| Archetype | Source | Role | Min | Planned | OK | Failed | Survival | under_min | zero_OK |
|-----------|--------|------|----:|--------:|---:|-------:|---------:|:---------:|:-------:|
| `bus_route_urban_suburban` | `osm` | primary | 8 | 106 | 106 | 0 | 1.000 | False | False |
| `bus_route_urban_suburban` | `synthetic` | supporting | 4 | 62 | 21 | 41 | 0.339 | False | False |
| `campus_compact` | `osm` | primary | 6 | 106 | 106 | 0 | 1.000 | False | False |
| `campus_compact` | `synthetic` | supporting | 4 | 62 | 43 | 19 | 0.694 | False | False |
| `campus_compact` | `trace_reference_synthetic` | supporting | 2 | 34 | 34 | 0 | 1.000 | False | False |
| `clustered_communities` | `osm` | optional | 0 | 0 | 0 | 0 | 0.000 | False | False |
| `clustered_communities` | `synthetic` | supporting | 4 | 62 | 62 | 0 | 1.000 | False | False |
| `clustered_communities` | `trace_reference_synthetic` | primary | 6 | 100 | 100 | 0 | 1.000 | False | False |
| `compact_residential` | `osm` | primary | 4 | 53 | 53 | 0 | 1.000 | False | False |
| `conference_event_compact` | `osm` | optional | 0 | 0 | 0 | 0 | 0.000 | False | False |
| `conference_event_compact` | `synthetic` | supporting | 4 | 62 | 62 | 0 | 1.000 | False | False |
| `conference_event_compact` | `trace_reference_synthetic` | primary | 6 | 34 | 34 | 0 | 1.000 | False | False |
| `corridor_linear` | `osm` | supporting | 4 | 52 | 52 | 0 | 1.000 | False | False |
| `corridor_linear` | `synthetic` | primary | 6 | 62 | 51 | 11 | 0.823 | False | False |
| `corridor_linear` | `trace_reference_synthetic` | supporting | 2 | 33 | 33 | 0 | 1.000 | False | False |
| `dense_urban_irregular` | `osm` | primary | 12 | 212 | 212 | 0 | 1.000 | False | False |
| `dense_urban_irregular` | `synthetic` | supporting | 4 | 61 | 61 | 0 | 1.000 | False | False |
| `hub_and_spoke` | `synthetic` | primary | 8 | 61 | 61 | 0 | 1.000 | False | False |
| `industrial_disrupted` | `osm` | primary | 6 | 106 | 106 | 0 | 1.000 | False | False |
| `industrial_disrupted` | `synthetic` | supporting | 4 | 61 | 61 | 0 | 1.000 | False | False |
| `industrial_disrupted` | `trace_reference_synthetic` | supporting | 2 | 34 | 34 | 0 | 1.000 | False | False |
| `island_or_partitioned` | `osm` | primary | 4 | 53 | 53 | 0 | 1.000 | False | False |
| `island_or_partitioned` | `synthetic` | supporting | 4 | 61 | 61 | 0 | 1.000 | False | False |
| `island_or_partitioned` | `trace_reference_synthetic` | supporting | 2 | 34 | 34 | 0 | 1.000 | False | False |
| `radial_city` | `synthetic` | primary | 8 | 61 | 50 | 11 | 0.820 | False | False |
| `rural_roads` | `osm` | primary | 4 | 53 | 51 | 2 | 0.962 | False | False |
| `rural_roads` | `synthetic` | supporting | 4 | 61 | 60 | 1 | 0.984 | False | False |
| `rural_roads` | `trace_reference_synthetic` | supporting | 2 | 34 | 34 | 0 | 1.000 | False | False |
| `sparse_trails` | `osm` | primary | 4 | 53 | 34 | 19 | 0.642 | False | False |
| `sparse_trails` | `synthetic` | supporting | 4 | 61 | 61 | 0 | 1.000 | False | False |
| `suburban_low_density` | `osm` | primary | 4 | 52 | 32 | 20 | 0.615 | False | False |
| `urban_grid` | `osm` | primary | 8 | 53 | 42 | 11 | 0.792 | False | False |
| `urban_grid` | `synthetic` | supporting | 4 | 61 | 61 | 0 | 1.000 | False | False |

CSV: [`../data/pool_revalidation_archetype_source_survival_v2.csv`](../data/pool_revalidation_archetype_source_survival_v2.csv)

## 2. Soft-target deviation

Targets \(p^* = (0.45,\,0.40,\,0.15)\) for (osm, synthetic, TRS). Realized shares are over **OK** maps only.

| Source | N_OK | p* | p | Δp |
|--------|-----:|---:|--:|---:|
| `osm` | 847 | 0.450 | 0.454155 | +0.004155 |
| `synthetic` | 715 | 0.400 | 0.383378 | -0.016622 |
| `trace_reference_synthetic` | 303 | 0.150 | 0.162466 | +0.012466 |

**Conclusion:** |Δp| is small. **Do not regenerate** maps solely to rebalance global source fractions.

CSV: [`../data/pool_revalidation_soft_target_delta_v2.csv`](../data/pool_revalidation_soft_target_delta_v2.csv)

## 3. Attrition bias

Failures are **not** uniform. Concentrations:

### Synthetic (`FAIL_BUILD_SYNTHETIC_DEGENERATE`)

| Generator | Archetype | Failed | OK same gen | Fail rate | OK in arch×synthetic | Residual coverage |
|-----------|-----------|-------:|------------:|----------:|---------------------:|:-----------------:|
| `bus_route_corridor` | `bus_route_urban_suburban` | 41 | 21 | 0.661 | 21 | True |
| `campus_compact` | `campus_compact` | 19 | 43 | 0.306 | 43 | True |
| `corridor` | `corridor_linear` | 11 | 51 | 0.177 | 51 | True |
| `radial_city` | `radial_city` | 11 | 50 | 0.180 | 50 | True |
| `sparse_rural` | `rural_roads` | 1 | 60 | 0.016 | 60 | True |

### OSM (`FAIL_BUILD_OSM`)

| Anchor | Archetype | Failed | OK same anchor | Fail rate | OK in arch×osm | Residual coverage |
|--------|-----------|-------:|---------------:|----------:|---------------:|:-----------------:|
| `tampere_suburban` | `suburban_low_density` | 20 | 32 | 0.385 | 32 | True |
| `nuuksio_sparse_trails` | `sparse_trails` | 19 | 34 | 0.358 | 34 | True |
| `manhattan_midtown` | `urban_grid` | 11 | 42 | 0.208 | 42 | True |
| `lapland_rural_sparse` | `rural_roads` | 2 | 51 | 0.038 | 51 | True |

Keeping failures in the manifest avoids **documentary** survival bias but does not erase possible **coverage bias** in the OK set. Residual OK > 0 for affected archetype×source cells is required before saturation.

CSV: [`../data/pool_revalidation_attrition_bias_v2.csv`](../data/pool_revalidation_attrition_bias_v2.csv)

## 4. Incremental ladder (defined, not executed)

Saturation must **not** treat N=1117 as a single point. Use cumulative prefixes of OK maps (order: `batch_target`, then `map_id`):

| Ladder N | Maps in prefix | Archetypes | Sources | Arch×src cells | Status |
|---------:|---------------:|-----------:|--------:|---------------:|--------|
| 100 | 100 | 14 | 3 | 27 | defined_not_executed |
| 200 | 200 | 14 | 3 | 27 | defined_not_executed |
| 300 | 300 | 14 | 3 | 27 | defined_not_executed |
| 400 | 400 | 14 | 3 | 27 | defined_not_executed |
| 600 | 600 | 14 | 3 | 27 | defined_not_executed |
| 800 | 800 | 14 | 3 | 27 | defined_not_executed |
| 1000 | 1000 | 14 | 3 | 27 | defined_not_executed |
| 1200 | 1200 | 14 | 3 | 29 | defined_not_executed |
| 1600 | 1600 | 15 | 3 | 31 | defined_not_executed |
| 1865 (full_OK_pool) | 1865 | 15 | 3 | 31 | defined_not_executed |

Expansion **1600 → 2000** is **conditional**: activate only if saturation curves show relevant marginal gain. Recommended future stop signals (several consecutive batches):

- \(\Delta C_N = C_N - C_{N-\Delta N} < \varepsilon_C\)
- \(\Delta K_N \approx 0\) (cluster count stability)
- New maps do not materially change geometric structure of the feature space

Metrics per N (for the **next** phase): new archetypes covered, new clusters, feature-space coverage increment, distance to nearest representative, cluster stability, archetype×source coverage.

CSV: [`../data/pool_revalidation_incremental_ladder_v2.csv`](../data/pool_revalidation_incremental_ladder_v2.csv)

## 5. Verdict: go / no-go for incremental saturation

**Verdict: `GO`**

No primary/supporting cells with zero OK; matrix floors checked.

### Explicitly deferred

- Feature extraction / PCA / separability on this pool
- Running `analyze_map_space_saturation_v1.py`
- Automatic expansion to 1600/2000
- SMS-v1 selection

### Next step if GO / GO_WITH_WARNINGS

1. Extract saturation features for OK maps under `map_space_revised_v2`.
2. Run **incremental** saturation on ladder prefixes (adapt batch thresholds to include 1117).
3. Expand planner only if marginal gains persist.
4. Select SMS-v1 only when saturation curves justify the stop.

