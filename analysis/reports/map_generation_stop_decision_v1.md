# Map generation stop decision: batches 800–2000 (v1)

**Status:** Phase 1 closed — methodological stop at 1200, confirmed by robustness extension to 2000  
**Decision record:** `map_space_saturation_decision.json` (`decision: stop_at_1200_confirmed_by_2000`, `robustness_extension_confirmed: true`)  
**Reference run:** 2000 generated candidates, 1378 validation-passing maps, 622 failures (~31.1%)

---

## Official statement

> Batch 800 is treated as the operational saturation point, while batch 1200 is retained as the methodological stopping point because two consecutive post-800 extensions confirmed diminishing feature-space returns. A robustness extension to batch 2000 confirmed that post-1200 tranches also showed diminishing non-redundant returns, without overturning the 1200 methodological stop.

---

## 1. Mandatory evaluation batches

| Batch | Generated | Valid maps | Invalid | Clusters | mean_nn L2 | Archetypes | Role |
|-------|-----------|------------|---------|----------|------------|------------|------|
| **100** | 100 | 84 | 16 | 9 | 1.408 | 15/15 | Categorical coverage achieved early |
| **800** | 800 | 696 | 104 | 26 | 0.420 | 15/15 | **Operational saturation point** |
| **1000** | 1000 | 877 | 123 | 30 | 0.384 | 15/15 | Extension window 1 (post-800) |
| **1200** | 1200 | 1055 | 145 | 32 | 0.340 | 15/15 | **Methodological stopping point** |
| **1600** | 1600 | 1220 | 380 | 35 | 0.334 | 15/15 | Robustness window 1 (post-1200) |
| **2000** | 2000 | 1378 | 622 | 37 | 0.331 | 15/15 | **Robustness ceiling evaluated** |

Source: `map_space_saturation_metrics.csv`, decision JSON generated 2026-06-22.

---

## 2. Three roles of evaluation batches

| Batch | Role |
|-------|------|
| **100** | All 15 archetypes represented from first evaluation point |
| **800** | Operational pool (696 valid); extension-eligible transitions begin |
| **1200** | Official methodological stop after 800→1000→1200 extension confirmation |
| **1600 / 2000** | Robustness check — not a claim that Earth has no more maps |

---

## 3. Extension 800 → 1000 → 1200

| Transition | New valid | Marginal growth | redundant+invalid | extension_pass |
|------------|-----------|-----------------|-------------------|----------------|
| 800 → 1000 | 181 | 26.0% | 58.7% | **yes** |
| 1000 → 1200 | 178 | 20.3% | 63.2% | **yes** |

`extension_confirmed: true` at batch 1200.

---

## 4. Robustness extension 1200 → 1600 → 2000

| Transition | New valid | Marginal growth | redundant+invalid | robustness_pass |
|------------|-----------|-----------------|-------------------|-----------------|
| 1200 → 1600 | 165 | 15.6% | 72.1% | **yes** |
| 1600 → 2000 | 158 | 13.0% | 75.7% | **yes** |

`robustness_extension_confirmed: true` → decision label `stop_at_1200_confirmed_by_2000`.

**Interpretation:** Post-1200 tranches added 323 valid maps (+30.6% vs 1200 pool) but ≥72% of each 400-candidate tranche was redundant or invalid. OSM valid count plateaued at 599 — further candidates were predominantly synthetic retries with high failure rate.

---

## 5. Why 1200 remains the official methodological stop

1. Pre-declared ladder and extension rules were satisfied at 1200 before the robustness run.
2. Extension to 2000 **confirmed** saturation rather than revealing a need to move the stop to 1600 or 2000.
3. Reporting N = 2000 as the paper ceiling would overstate methodological closure while citing a pool where 31% of candidates fail validation.
4. `decision_tier: methodological_1200` in decision JSON encodes this explicitly.

---

## 6. Decision artefacts

| Artefact | Path |
|----------|------|
| Machine-readable decision | `scenarios/analysis/data/map_space_saturation_decision.json` |
| Metrics by batch | `scenarios/analysis/data/map_space_saturation_metrics.csv` |
| Transition evaluation | `scenarios/analysis/data/map_space_saturation_by_batch.csv` |
| Extension narrative | `scenarios/analysis/reports/map_generation_extension_1200_2000_v1.md` |
| Methodology synthesis | `scenarios/analysis/reports/map_space_saturation_methodology_final.md` |
| Threshold sensitivity | `scenarios/analysis/reports/near_redundancy_threshold_sensitivity_report.md` |
| Run manifest (2000) | `scenarios/analysis/data/map_space_saturation_extension_2000_run_manifest.json` |

**Paper-ready claim** (from decision JSON):

> Map generation methodological stop remains at N=1200 candidates (1055 validation-passing maps at batch 1200, 15/15 declared archetypes covered). A robustness extension to N=2000 candidates added 323 further valid maps while post-1200 tranches showed >=50% redundant or invalid new maps, confirming that the 1200 stopping decision was not premature. Completeness is defined with respect to this declared design space, not all possible real-world environments.

---

## 7. Scope reminder

Stopping at 1200 (confirmed at 2000) does **not** mean no further maps could be generated. It means that, under the declared design space and metrics, additional batches are expected to yield predominantly redundant or invalid candidates relative to the existing pool.

> The extension to 2000 candidates does not aim to prove that no additional maps can be generated. Instead, it tests whether additional candidates provide non-redundant feature-space coverage within the declared map-topology design space.

---

*Phase 1 map generation — stop decision v1 (updated for N=2000 robustness)*
