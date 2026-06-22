# INDEX — Map Generation Phase 1 (FINAL)

**Status:** Phase 1 closed — defendible before reviewers  
**Reference run:** N = 2000 candidates evaluated (1378 valid maps); methodological stop at batch **1200** (`stop_at_1200_confirmed_by_2000`, `robustness_extension_confirmed: true`)  
**Frozen:** `scenarios/corpus_v1/` — not modified in this phase  
**Phase 2 (complete):** Map selection from pool @1200 → **75 maps** in `selected_map_space_v1/` — see [`INDEX_SELECTED_MAP_SPACE_V1.md`](INDEX_SELECTED_MAP_SPACE_V1.md)  
**Next step:** Structural scenario generation (separate phase; no scenarios generated here)

---

## Executive summary

Map generation Phase 1 replaces six hand-picked legacy maps with a **declared fifteen-archetype design space**, batch OSM + synthetic generation, feature extraction, and **saturation-based stopping** at batch **1200**, confirmed by a robustness extension to N = 2000. Categorical coverage was complete from batch 100; batches 800→1200 and 1200→2000 confirmed diminishing feature-space returns.

**Official stop statement:** see [`map_generation_stop_decision_v1.md`](map_generation_stop_decision_v1.md).

**Robustness extension:** [`map_generation_extension_1200_2000_v1.md`](map_generation_extension_1200_2000_v1.md).

**Methodology synthesis:** [`map_space_saturation_methodology_final.md`](map_space_saturation_methodology_final.md).

**Paper text:** [`paper_ready_map_generation_section_v1.md`](paper_ready_map_generation_section_v1.md).

---

## Related phases

| Phase | Status | Summary |
|-------|--------|---------|
| **Phase 1** — map space saturation | **CLOSED** | 1055 valid maps @1200; stop `stop_at_1200_confirmed_by_2000` |
| **Phase 2** — selected_map_space_v1 | **DONE** | 75 selected maps; hybrid method; 15/15 archetypes; 3/3 source types |

**Phase 2 official manifest:** [`scenarios/selected_map_space_v1/manifest_selected_maps.csv`](../../selected_map_space_v1/manifest_selected_maps.csv)

**Phase 2 index:** [`INDEX_SELECTED_MAP_SPACE_V1.md`](INDEX_SELECTED_MAP_SPACE_V1.md)

---

## Configuration

| File | Purpose |
|------|---------|
| [`map_design_space_saturation_v1.yaml`](../config/map_design_space_saturation_v1.yaml) | Design space, anchors, generators, batch policy, stop rule spec |
| [`map_archetype_definitions_v1.csv`](../data/map_archetype_definitions_v1.csv) | 15 archetype definitions and literature rationale |
| [`map_archetype_topology_matrix_v1.csv`](../data/map_archetype_topology_matrix_v1.csv) | Ordinal topology dimensions per archetype |

---

## Data (CSV / JSON)

### Core run outputs

| File | Purpose |
|------|---------|
| [`map_space_saturation_features.csv`](../data/map_space_saturation_features.csv) | 1378 valid maps × 33+ features + metadata |
| [`map_space_saturation_features_normalized.csv`](../data/map_space_saturation_features_normalized.csv) | Global z-score + source_type one-hot |
| [`map_space_saturation_metrics.csv`](../data/map_space_saturation_metrics.csv) | Cumulative metrics per batch |
| [`map_space_saturation_by_batch.csv`](../data/map_space_saturation_by_batch.csv) | Transition / stop-rule flags |
| [`map_space_saturation_decision.json`](../data/map_space_saturation_decision.json) | Machine-readable stop decision |
| [`map_anchor_inventory_v1.csv`](../data/map_anchor_inventory_v1.csv) | 19 declared anchors × valid-map coverage |
| [`map_space_saturation_extension_2000_run_manifest.json`](../data/map_space_saturation_extension_2000_run_manifest.json) | Reproducibility manifest for N=2000 run |

### Phase 1 closure analyses

| File | Purpose |
|------|---------|
| [`map_archetype_centroid_distances.csv`](../data/map_archetype_centroid_distances.csv) | Pairwise archetype centroid L2/cosine |
| [`map_archetype_separability_summary.csv`](../data/map_archetype_separability_summary.csv) | Intra/inter separability per archetype |
| [`map_saturation_by_archetype.csv`](../data/map_saturation_by_archetype.csv) | Intra-archetype saturation status |
| [`near_redundancy_threshold_sensitivity.csv`](../data/near_redundancy_threshold_sensitivity.csv) | Threshold sweep 0.15–0.35 |

---

## Scripts

### Generation and extraction

| Script | Purpose |
|--------|---------|
| [`generate_map_space_saturation_v1.py`](../../setup/generate_map_space_saturation_v1.py) | Batch map generation (100…2000) |
| [`export_map_anchor_inventory_v1.py`](../../setup/export_map_anchor_inventory_v1.py) | Anchor inventory from YAML + features |
| [`extract_map_space_saturation_features.py`](../../setup/extract_map_space_saturation_features.py) | Feature extraction from built maps |
| [`run_saturation_extension_1000_1200.sh`](../../setup/run_saturation_extension_1000_1200.sh) | Fault-tolerant extension runner (→1200) |
| [`run_saturation_extension_1600_2000.sh`](../../setup/run_saturation_extension_1600_2000.sh) | Fault-tolerant robustness extension (→2000) |

### Saturation and closure analysis

| Script | Purpose |
|--------|---------|
| [`analyze_map_space_saturation_v1.py`](../../setup/analyze_map_space_saturation_v1.py) | Cumulative batch saturation + 8 figures + decision JSON |
| [`analyze_map_archetype_separability_v1.py`](../../setup/analyze_map_archetype_separability_v1.py) | Archetype separability + heatmap + PCA |
| [`analyze_map_saturation_by_archetype_v1.py`](../../setup/analyze_map_saturation_by_archetype_v1.py) | Per-archetype internal saturation |
| [`analyze_near_redundancy_threshold_sensitivity_v1.py`](../../setup/analyze_near_redundancy_threshold_sensitivity_v1.py) | NN threshold sensitivity |

---

## Reports

| Report | Purpose |
|--------|---------|
| [`map_archetype_justification_v1.md`](map_archetype_justification_v1.md) | Formal justification of 15 archetypes |
| [`map_archetype_separability_report.md`](map_archetype_separability_report.md) | Feature-space separability interpretation |
| [`map_saturation_by_archetype_report.md`](map_saturation_by_archetype_report.md) | Intra-archetype coverage status |
| [`near_redundancy_threshold_sensitivity_report.md`](near_redundancy_threshold_sensitivity_report.md) | Robustness of 0.25 threshold |
| [`map_generation_stop_decision_v1.md`](map_generation_stop_decision_v1.md) | Batches 800–2000 stop narrative |
| [`map_generation_extension_1200_2000_v1.md`](map_generation_extension_1200_2000_v1.md) | Robustness extension report |
| [`map_space_saturation_methodology_final.md`](map_space_saturation_methodology_final.md) | Methodology synthesis |
| [`map_anchor_inventory_v1.md`](map_anchor_inventory_v1.md) | Anchor inventory report |
| [`map_anchor_count_correction_v1.md`](map_anchor_count_correction_v1.md) | 20→19 anchor count correction |
| [`paper_ready_map_generation_section_v1.md`](paper_ready_map_generation_section_v1.md) | English methods text for paper |
| [`map_space_saturation_report.md`](map_space_saturation_report.md) | Automated saturation report |
| [`map_design_space_saturation_v1.md`](map_design_space_saturation_v1.md) | Original design-space methodology |
| [`scenarios/internal/map_space_saturation_archetypes_and_results_v1.md`](../../internal/map_space_saturation_archetypes_and_results_v1.md) | Internal Spanish narrative + figure guide |
| [`scenarios/internal/map_generation_phase1_inventory_v1.md`](../../internal/map_generation_phase1_inventory_v1.md) | **Internal inventory** — reproduction tiers, retention labels, cleanup guide |
| [`scenarios/internal/map_space_selection_methods_and_results_v1.md`](../../internal/map_space_selection_methods_and_results_v1.md) | **Phase 2 internal narrative** (ES) + figure guide |
| [`scenarios/internal/map_generation_phase2_inventory_v1.md`](../../internal/map_generation_phase2_inventory_v1.md) | **Phase 2 internal inventory** |
| [`INDEX_SELECTED_MAP_SPACE_V1.md`](INDEX_SELECTED_MAP_SPACE_V1.md) | **Phase 2 master index** (CLOSED) |
| [`selected_map_space_v1_methodology.md`](selected_map_space_v1_methodology.md) | Phase 2 selection methodology |
| [`selected_map_space_v1_selection_report.md`](selected_map_space_v1_selection_report.md) | Phase 2 experiment results |
| [`selected_map_space_v1_reviewer_rationale.md`](selected_map_space_v1_reviewer_rationale.md) | Phase 2 reviewer FAQ |
| [`paper_ready_selected_maps_section_v1.md`](paper_ready_selected_maps_section_v1.md) | Phase 2 paper-ready methods (EN) |
| [`selected_map_space_v1_coverage_report.md`](selected_map_space_v1_coverage_report.md) | Phase 2 post-selection coverage audit |

---

## Figures (`figures/map_space_saturation/`)

### Global saturation (8)

| Figure | Description |
|--------|-------------|
| `valid_vs_generated.png` | Valid maps vs candidates |
| `unique_vectors_vs_generated.png` | Unique feature vectors |
| `clusters_vs_generated.png` | k-medoids cluster count |
| `mean_nn_dist_vs_generated.png` | Mean NN distance compression |
| `max_medoid_dist_vs_generated.png` | Max medoid coverage distance |
| `improvement_pct_vs_batch.png` | Relative improvement per batch |
| `archetype_coverage_vs_batch.png` | 15/15 categorical coverage |
| `source_type_vs_batch.png` | OSM / synthetic / trace mix |

### Phase 1 closure (7)

| Figure | Description |
|--------|-------------|
| `archetype_centroid_distance_heatmap.png` | 15×15 centroid L2 heatmap |
| `archetype_pca_projection.png` | PCA coloured by archetype |
| `saturation_by_archetype_valid_maps.png` | Valid count per archetype |
| `saturation_by_archetype_nn_distance.png` | Intra-archetype mean NN |
| `saturation_by_archetype_clusters.png` | Internal clusters vs n |
| `near_redundancy_threshold_sensitivity.png` | Threshold sweep |

---

## Final decision

```json
{
  "decision": "stop_at_1200_confirmed_by_2000",
  "recommended_stop_batch": 1200,
  "robustness_extension_confirmed": true,
  "decision_tier": "methodological_1200",
  "max_batch_evaluated": 2000,
  "max_valid_maps": 1378,
  "valid_maps_at_1200": 1055,
  "marginal_valid_maps_after_1200": 323
}
```

Full record: [`map_space_saturation_decision.json`](../data/map_space_saturation_decision.json)

---

## Reproduction commands

```bash
# Activate environment
source venv/bin/activate

# Re-run global saturation analysis (requires features + validation CSVs)
python scenarios/setup/analyze_map_space_saturation_v1.py

# Phase 1 closure analyses
python scenarios/setup/analyze_map_archetype_separability_v1.py
python scenarios/setup/analyze_map_saturation_by_archetype_v1.py
python scenarios/setup/analyze_near_redundancy_threshold_sensitivity_v1.py

# Optional: full robustness extension pipeline (generation — long-running)
python scenarios/setup/generate_map_space_saturation_v1.py --estimate-only --target-total 2000 --seed 42
bash scenarios/setup/run_saturation_extension_1600_2000.sh --skip-synth-rebuild
# resume analysis only:
bash scenarios/setup/run_saturation_extension_1600_2000.sh --from-phase=E

# Anchor inventory (from YAML + features)
python scenarios/setup/export_map_anchor_inventory_v1.py
```

---

## Acceptance checklist (Phase 1 closed)

- [x] Anchor audit: 19 declared (15 OSM + 4 trace), inventory CSV/MD
- [x] Robustness extension to N=2000 evaluated (batches 1600, 2000)
- [x] Stop decision `stop_at_1200_confirmed_by_2000` in decision JSON
- [x] Formal justification of 15 archetypes
- [x] Archetype separability analysis
- [x] Intra-archetype saturation analysis
- [x] Near-redundancy threshold sensitivity
- [x] Stop decision 800 vs 1200 documented
- [x] Paper-ready English section
- [x] Declared design-space scope (not all Earth maps)
- [x] `corpus_v1/` untouched
- [x] No structural scenarios generated in this phase

---

## Next phase (not started here)

**Next step:** structural scenario generation using [`scenarios/selected_map_space_v1/manifest_selected_maps.csv`](../../selected_map_space_v1/manifest_selected_maps.csv).

1. ~~**Map selection / pruning** from 1055 valid maps @batch 1200~~ → **DONE** — [`INDEX_SELECTED_MAP_SPACE_V1.md`](INDEX_SELECTED_MAP_SPACE_V1.md) (75 maps, hybrid, seed 42)
2. **Structural scenario generation** — selected maps × movement models × node densities × group structures × network parameters; extract features, validate diversity, prune redundancy
3. **Do not apply Traffic Profiles yet**
4. Keep `corpus_v1/` and `base_scenarios/` frozen (not modified)

**Phase 2 internal docs:** [`map_space_selection_methods_and_results_v1.md`](../../internal/map_space_selection_methods_and_results_v1.md), [`map_generation_phase2_inventory_v1.md`](../../internal/map_generation_phase2_inventory_v1.md)

---

*Map Generation Phase 1 — final index, June 2026*
