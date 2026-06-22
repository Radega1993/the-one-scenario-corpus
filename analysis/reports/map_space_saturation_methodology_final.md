# Map space saturation methodology — Phase 1 final synthesis

**Status:** Phase 1 closed with robustness extension to N = 2000  
**Decision:** `stop_at_1200_confirmed_by_2000` (`robustness_extension_confirmed: true`)  
**Generated:** 2026-06-22

---

## Canonical counts

| Quantity | Value | Source |
|----------|-------|--------|
| Declared anchors in YAML | **19** | `real_anchors.anchors` (15 OSM + 4 trace-only) |
| Map-topology archetypes | **15** | `map_archetype_definitions_v1.csv` |
| Evaluation batches | 100, 200, 400, 600, 800, 1000, 1200, **1600**, **2000** | `map_design_space_saturation_v1.yaml` |
| Candidates generated (max) | **2000** | `manifest_maps_all.csv` |
| Validation-passing maps (max) | **1378** | `map_space_saturation_features.csv` |
| Validation failures (max) | **622** (~31.1%) | `map_space_saturation_validation.csv` |
| Anchors with ≥1 valid map | **19** | `map_anchor_inventory_v1.csv` |
| Synthetic maps without geographic anchor | **570** | features where `anchor_id` empty |

Distinguish always: **19 declared in YAML** vs **N with valid map** (currently 19/19).

---

## Design space and scope

The benchmark replaces six legacy hand-picked maps with a **declared fifteen-archetype map-topology design space**. Nineteen real anchors document provenance (fifteen OSM-downloadable regions; four contact-trace references that parametrize synthetic topologies).

**Completeness claim (mandatory):**

> We do not claim to cover all possible real-world maps. Completeness is defined with respect to the declared map-topology design space.

**Robustness extension (mandatory):**

> The extension to 2000 candidates does not aim to prove that no additional maps can be generated. Instead, it tests whether additional candidates provide non-redundant feature-space coverage within the declared map-topology design space.

---

## Pipeline

1. **Plan** — stratified candidate queue to `TARGET_TOTAL` (SHA-256 seeds, ~50% OSM / ~50% synthetic+trace-reference)
2. **Build** — OSM acquisition (fault-tolerant) + synthetic generators (13 algorithms)
3. **Validate** — PASS / WARNING / STRESS retained; FAIL excluded from features
4. **Extract** — 33 numeric graph features + metadata per valid map
5. **Analyze** — cumulative batch metrics, extension transitions, stop decision, figures

**Reproducibility runners:**

- `run_saturation_extension_1000_1200.sh` — first methodological closure
- `run_saturation_extension_1600_2000.sh` — robustness extension (manifest: `map_space_saturation_extension_2000_run_manifest.json`)

---

## Feature space and saturation metrics

Per cumulative batch B, using only maps with `batch_target ≤ B`:

- Valid / invalid counts, unique feature vectors
- k-medoids clusters (k ≈ √n, cap 50)
- Mean/median NN L2 in 36D space (33 z-scored features + `source_type` one-hot)
- Medoid distance improvements (mean, max)
- Near-redundancy: new valid maps within L2 **0.25** of any prior valid map

Archetype coverage reached **15/15** from batch 100; later batches tested feature-space redundancy, not categorical discovery.

---

## Stop rules (layered)

### Strict rule (YAML)

Seven criteria over two consecutive transitions (5% cluster/medoid thresholds, stable archetype/source sets, majority redundant+invalid).

### Extension confirmation (800 → 1000 → 1200)

Relaxed criteria when `prev_batch ≥ 800` and 15/15 archetypes covered:

- Marginal valid growth &lt; 30% of previous valid pool
- Relative cluster growth &lt; 16%; mean medoid improvement &lt; 8%
- ≥ 50% redundant or invalid per tranche
- No new archetypes or source types

**Result at N = 1200:** both 800→1000 and 1000→1200 passed → `extension_confirmed: true`, methodological stop at batch 1200.

### Robustness extension (1200 → 1600 → 2000)

Same extension function with `prev_batch ≥ 1200`. Evaluated only when data reach batch 2000.

**Result at N = 2000:** both 1200→1600 and 1600→2000 passed → `robustness_extension_confirmed: true`, decision label `stop_at_1200_confirmed_by_2000`. Methodological stop **remains batch 1200**; extension confirms it was not premature.

| Tier | Batch | Valid maps | Role |
|------|-------|------------|------|
| Operational | 800 | 696 | Efficient internal pool |
| Methodological (official) | **1200** | **1055** | Paper stop point |
| Robustness evaluated | 2000 | 1378 | Confirms post-1200 diminishing returns |

---

## Key artefacts

| Artefact | Path |
|----------|------|
| Decision JSON | `map_space_saturation_decision.json` |
| Metrics by batch | `map_space_saturation_metrics.csv` |
| Transitions | `map_space_saturation_by_batch.csv` |
| Anchor inventory | `map_anchor_inventory_v1.csv` |
| Anchor correction note | `map_anchor_count_correction_v1.md` |
| Extension narrative | `map_generation_extension_1200_2000_v1.md` |
| Stop decision | `map_generation_stop_decision_v1.md` |
| Paper text | `paper_ready_map_generation_section_v1.md` |
| Index | `INDEX_MAP_GENERATION_PHASE1_FINAL.md` |

---

*Phase 1 map generation — methodology final, June 2026*
