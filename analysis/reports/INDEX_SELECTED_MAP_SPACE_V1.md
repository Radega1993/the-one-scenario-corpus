# INDEX — Selected map space v1 (Phase 2)

## A. Status

**Status:** CLOSED / reviewer-ready  
**Official selected set:** 75 maps  
**Input pool:** 1055 valid maps @ batch 1200 (`stop_at_1200_confirmed_by_2000`)  
**Selection method:** hybrid_stratified_diversity (`hybrid`)  
**Seed:** 42  
**Constraints satisfied:** true

Phase 1 map generation is closed at batch 1200. Phase 2 representative map selection is closed. The extension to batch 2000 was a **robustness check only** — not the selection pool.

---

## B. Executive summary

| Concept | Value |
|---------|-------|
| Input pool | 1055 |
| Selected maps | 75 |
| Reduction | 7.1% |
| Method | hybrid |
| Archetypes | 15/15 |
| Source types | 3/3 |
| Anchors | 19 |
| Min maps per archetype | 3 |
| Constraints satisfied | true |
| Assets | WKT copied (not symlinks) |

**Size decision:** N=75 chosen by elbow on `max_distance_to_selected` (marginal improvement 3.8% &lt; 5% threshold) with all policy constraints satisfied. See [`selected_map_space_v1_decision.json`](../data/selected_map_space_v1_decision.json).

**Paper-ready claim (limited scope):**

> The selected map set is a representative subset of the saturated map-design pool. It preserves categorical coverage of the declared archetypes while reducing feature-space redundancy through diversity-based selection.

---

## C. Main artefacts

Official directory: [`scenarios/selected_map_space_v1/`](../../selected_map_space_v1/)

| File | Purpose |
|------|---------|
| [`manifest_selected_maps.csv`](../../selected_map_space_v1/manifest_selected_maps.csv) | **Official input for next phase** — 75 rows with selection roles |
| [`selected_map_ids.txt`](../../selected_map_space_v1/selected_map_ids.txt) | One map ID per line |
| [`selected_maps_features.csv`](../../selected_map_space_v1/selected_maps_features.csv) | Feature subset from pool |
| [`selected_maps_summary.csv`](../../selected_map_space_v1/selected_maps_summary.csv) | Aggregates by archetype × source_type |
| [`selected_maps_coverage.csv`](../../selected_map_space_v1/selected_maps_coverage.csv) | Pool vs selected counts per archetype |
| [`selected_maps_rationale.md`](../../selected_map_space_v1/selected_maps_rationale.md) | Per-map selection rationale (auto-generated) |
| [`README.md`](../../selected_map_space_v1/README.md) | Usage, N, method, seed |
| [`wkt/{map_id}/`](../../selected_map_space_v1/wkt/) | Copied `roads.wkt`, `metadata.json`, `preview.png` per map |

---

## D. Scripts

| Script | Purpose |
|--------|---------|
| [`map_selection_v1_common.py`](../../setup/map_selection_v1_common.py) | Shared pool load, feature matrix, metrics, constraints |
| [`audit_map_selection_pool_v1.py`](../../setup/audit_map_selection_pool_v1.py) | Audit @1200 pool → CSV + report |
| [`select_representative_maps_v1.py`](../../setup/select_representative_maps_v1.py) | Five methods, experiments, decision, write-official |
| [`audit_selected_map_space_v1.py`](../../setup/audit_selected_map_space_v1.py) | Post-selection coverage audit + figures |

---

## E. Data

| File | Purpose |
|------|---------|
| [`map_selection_pool_v1.csv`](../data/map_selection_pool_v1.csv) | Official selection pool (1055 rows) |
| [`selected_map_space_v1_selection_experiments.csv`](../data/selected_map_space_v1_selection_experiments.csv) | Method × size × epsilon grid results |
| [`selected_map_space_v1_decision.json`](../data/selected_map_space_v1_decision.json) | Official N, method, metrics, claim |
| [`selected_map_space_v1_coverage.csv`](../data/selected_map_space_v1_coverage.csv) | Per-archetype pool vs selected |
| [`selected_map_space_v1_distance_audit.csv`](../data/selected_map_space_v1_distance_audit.csv) | Each pool map → distance to nearest selected |

**Policy (machine-readable):** [`selected_map_space_v1_policy.yaml`](../config/selected_map_space_v1_policy.yaml)

---

## F. Reports

| Report | Purpose |
|--------|---------|
| [`selected_map_space_v1_policy.md`](selected_map_space_v1_policy.md) | Policy rationale (why prune, why grid sizes) |
| [`map_selection_pool_v1_audit.md`](map_selection_pool_v1_audit.md) | Pool @1200 definition and distributions |
| [`selected_map_space_v1_methodology.md`](selected_map_space_v1_methodology.md) | Methods, feature space, constraints |
| [`selected_map_space_v1_selection_report.md`](selected_map_space_v1_selection_report.md) | Experiment comparison table |
| [`selected_map_space_v1_size_decision.md`](selected_map_space_v1_size_decision.md) | N=75 elbow decision narrative |
| [`selected_map_space_v1_reviewer_rationale.md`](selected_map_space_v1_reviewer_rationale.md) | Reviewer FAQ |
| [`selected_map_space_v1_coverage_report.md`](selected_map_space_v1_coverage_report.md) | Post-selection audit |
| [`paper_ready_selected_maps_section_v1.md`](paper_ready_selected_maps_section_v1.md) | English methods text for paper |
| [`selected_map_space_v1_documentation_update.md`](selected_map_space_v1_documentation_update.md) | Documentation closure changelog |

---

## G. Figures

Directory: [`figures/selected_map_space_v1/`](../figures/selected_map_space_v1/)

### Experiment grid (6)

| Figure | Description |
|--------|-------------|
| `coverage_vs_n.png` | Mean distance to selected vs target N by method |
| `max_distance_vs_n.png` | Max distance to selected vs N — elbow figure |
| `p95_distance_vs_n.png` | P95 coverage distance vs N |
| `source_type_balance_vs_n.png` | OSM fraction vs N across methods |
| `archetype_coverage_vs_n.png` | Archetype count vs N (15/15 line) |
| `selection_method_comparison.png` | Bar comparison of max_distance by method and N |

### Coverage audit (6)

| Figure | Description |
|--------|-------------|
| `selected_archetype_counts.png` | Selected count per archetype |
| `selected_source_type_counts.png` | OSM / synthetic / trace counts |
| `selected_anchor_counts.png` | Selected count per anchor |
| `pool_vs_selected_pca.png` | PCA 2D: full pool vs 75 selected |
| `coverage_distance_histogram.png` | Pool → nearest selected distance distribution |
| `selected_map_distance_heatmap.png` | Pairwise distance among selected maps |

---

## H. Reproduction

```bash
cd /home/raul/Documents/the-one
source venv/bin/activate

python scenarios/setup/audit_map_selection_pool_v1.py
python scenarios/setup/select_representative_maps_v1.py --run-experiments --seed 42
python scenarios/setup/select_representative_maps_v1.py --write-official --seed 42
python scenarios/setup/audit_selected_map_space_v1.py
```

**Prerequisites:** Phase 1 artefacts (`map_space_saturation_features.csv`, `validation.csv`, `manifest_maps_all.csv`). For `--write-official`, WKT assets must exist under `map_space_saturation_v1/`.

---

## I. Claims — allowed and prohibited

### Allowed

- Representative subset of the **saturated map-design pool**
- Preserves **declared archetype coverage** (15/15)
- Reduces **feature-space redundancy** through diversity-based selection
- **Reviewer-ready** selected map set with audited constraints
- Completeness defined with respect to the **declared map-topology design space**

### Prohibited

- Covers **all maps in the world**
- **Globally optimal** subset (only best under declared policy and grid)
- **No redundancy remains** in the full 1055-map pool
- Covers **all possible real-world environments**

---

## J. Next phase

**Next phase:** structural scenario generation.

**Input:**

```text
scenarios/selected_map_space_v1/manifest_selected_maps.csv
```

**Scope:**

```text
selected maps (75)
    × movement models
    × node densities
    × group structures
    × network parameters
    → structural scenario space
```

- Generate structural scenarios; extract features; validate diversity; prune redundancy.
- **Do not apply Traffic Profiles yet.**
- **Do not modify** `scenarios/corpus_v1/` or `scenarios/base_scenarios/`.

---

## Internal documentation (ES)

| Document | Purpose |
|----------|---------|
| [`map_space_selection_methods_and_results_v1.md`](../../internal/map_space_selection_methods_and_results_v1.md) | Narrative, methods, figure guide, acceptance limits |
| [`map_generation_phase2_inventory_v1.md`](../../internal/map_generation_phase2_inventory_v1.md) | Reproduction tiers, KEEP/REGEN, cleanup (~39 MB official set) |
| [`map_space_saturation_archetypes_and_results_v1.md`](../../internal/map_space_saturation_archetypes_and_results_v1.md) | Phase 1 narrative — §12.5–12.6 transition to scenarios |

## Phase 1 link

[`map_generation_phase1_inventory_v1.md`](../../internal/map_generation_phase1_inventory_v1.md) — pool source (1055 @1200).  
[`INDEX_MAP_GENERATION_PHASE1_FINAL.md`](INDEX_MAP_GENERATION_PHASE1_FINAL.md) — Phase 1 master index.

---

*Selected map space v1 — master index, June 2026. Phase 2 CLOSED.*
