# Robustness extension 1200 → 2000 — Phase 1 closure report (v1)

**Run:** seed 42, `TARGET_TOTAL=2000`, fault-tolerant pipeline  
**Decision:** `stop_at_1200_confirmed_by_2000`  
**Generated:** 2026-06-22

---

## Mandatory scope statement

> The extension to 2000 candidates does not aim to prove that no additional maps can be generated. Instead, it tests whether additional candidates provide non-redundant feature-space coverage within the declared map-topology design space.

---

## 1. Why extend beyond 1200?

Batch 1200 already satisfied extension confirmation (800→1000→1200). The 1600/2000 batches were pre-registered in `map_design_space_saturation_v1.yaml` as a **robustness check**: reviewers may ask whether stopping at 1200 was premature given OSM queue backlog or synthetic headroom. Extending to 2000 tests post-1200 tranches under the same extension criteria without changing the declared design space.

---

## 2. What was generated?

| Quantity | At 1200 | At 2000 | Δ |
|----------|---------|---------|---|
| Candidates | 1200 | 2000 | +800 |
| Valid maps | 1055 | 1378 | +323 |
| Invalid | 145 | 622 | +477 |
| k-medoids clusters | 32 | 37 | +5 |
| Mean NN L2 | 0.340 | 0.331 | −2.6% |
| OSM valid fraction | 56.8% | 43.5% | OSM pool saturated (599 OSM valid, unchanged count) |

The +800 candidates added **323** further valid maps (+30.6% relative to the 1200 pool) but **477** additional failures — failure rate rose sharply in post-1200 tranches (58.8% and 60.5% invalid per 400-candidate tranche).

---

## 3. Did archetype or source coverage change?

No. All batches through 2000: `valid_archetypes_covered = 15`, `valid_anchors_covered = 19`, `archetype_set_changed = false`, no new `source_type` families.

---

## 4. Extension transitions post-1200

Criteria (same as 800→1200 extension): marginal valid &lt; 30%, clusters &lt; 16%, mean medoid &lt; 8%, ≥ 50% redundant+invalid, stable archetype/source sets.

| Transition | New valid | Marginal / prev pool | near_redundant | invalid | redundant+invalid | rel_clusters | rel_mean_medoid | Pass |
|------------|-----------|---------------------|----------------|---------|-------------------|--------------|-----------------|------|
| 1200 → 1600 | 165 | 15.6% | 13.3% | 58.8% | **72.1%** | 9.4% | 6.1% | **yes** |
| 1600 → 2000 | 158 | 13.0% | 15.2% | 60.5% | **75.7%** | 5.7% | 3.5% | **yes** |

Both transitions passed → `robustness_extension_confirmed: true`.

---

## 5. Why not stop at 1600 or 2000?

Although post-1200 tranches added some valid maps, **both** robustness windows met saturation criteria. The decision policy treats consecutive post-1200 confirmation as evidence that batch **1200** was already an adequate methodological ceiling: later valid maps are predominantly near-redundant or came with high invalid yield.

`stop_at_1600` would apply if 1200→1600 failed extension but 1600→2000 passed (measurable diversity in the first post-1200 window). That pattern did **not** occur.

`stop_at_2000` would apply if only the final window saturated and heuristic pointed to max batch. Here, **both** windows saturated while confirming 1200.

---

## 6. Near-redundancy threshold sensitivity

See `near_redundancy_threshold_sensitivity_report.md`. For 1200→1600 and 1600→2000, `redundant_plus_invalid ≥ 50%` holds for thresholds **0.15–0.35** (invalid fraction dominates in post-1200 tranches).

---

## 7. Anchor audit (19, not 20)

YAML declares **19** anchors (15 OSM + 4 trace-only). All 19 have ≥1 valid map at N = 2000. Prior documents incorrectly stated "20 / 16 OSM". See `map_anchor_count_correction_v1.md` and `map_anchor_inventory_v1.md`.

---

## 8. Separability and intra-archetype status (at N = 2000)

- Global inter/intra centroid ratio: **1.74** (1378 valid maps)
- All 15 archetypes: ACCEPTABLE or WELL_COVERED; 0 × `NEEDS_MORE_GENERATION`
- Largest valid counts: `dense_urban_irregular` (199), `industrial_disrupted` (158), `island_or_partitioned` (117)

---

## 9. Operational vs methodological reporting

| Audience | Report N | Valid pool | Rationale |
|----------|----------|------------|-----------|
| Engineering / prototyping | 800 | 696 | Operational plateau |
| Paper / methods | **1200** | **1055** | Methodological stop, confirmed by 2000 extension |
| Robustness appendix | 2000 | 1378 | Shows +323 valid after 1200 with ≥72% redundant+invalid tranches |

---

## 10. Official decision phrase

From `map_space_saturation_decision.json`:

> Map generation methodological stop remains at N=1200 candidates (1055 validation-passing maps at batch 1200, 15/15 declared archetypes covered). A robustness extension to N=2000 candidates added 323 further valid maps while post-1200 tranches showed >=50% redundant or invalid new maps, confirming that the 1200 stopping decision was not premature. Completeness is defined with respect to this declared design space, not all possible real-world environments.

**Machine-readable:** `decision: stop_at_1200_confirmed_by_2000`, `decision_tier: methodological_1200`, `stop_rule_mode: robustness_extension_confirmation`.

---

## Reproduction

```bash
source venv/bin/activate
python scenarios/setup/generate_map_space_saturation_v1.py --estimate-only --target-total 2000 --seed 42
bash scenarios/setup/run_saturation_extension_1600_2000.sh --skip-synth-rebuild
# or resume analysis only:
bash scenarios/setup/run_saturation_extension_1600_2000.sh --from-phase=E
```

---

*Phase 1 — extension 1200→2000 report, June 2026*
