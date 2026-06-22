# Paper-ready section: Map-topology design space and saturation-based generation (v1)

*Draft text for methods / experimental design — English, reviewer-facing.*

---

## Map-topology design space

We define map-topology diversity through a **declared design space** rather than ad hoc selection of a few legacy maps. The space comprises fifteen **map-topology archetypes** (e.g., urban grid, dense irregular urban core, campus compact, bus-route corridor, partitioned islands, conference-event compact), each grounded in DTN/OppNet literature and The ONE map-based traditions. Nineteen **real anchors** document provenance: fifteen are OSM-downloadable geographic regions; four are contact-trace references that parametrize synthetic topologies without pretending that traces are directly downloadable street maps.

Completeness is assessed relative to this declared space. **We do not claim to cover all possible real-world maps. Completeness is defined with respect to the declared map-topology design space.**

Archetypes are categorical **coverage cells**, not a claim that the world has exactly fifteen map types. Continuous variation within and across cells is captured by thirty-three numeric graph and shape features extracted from each road network (scale, connectivity, gridness, corridor structure, partition scores, etc.), plus provenance via `source_type` (OSM, synthetic, trace-reference synthetic).

---

## Real anchors and synthetic topology generators

**OSM anchors** supply real road networks from documented bounding boxes or place geocodes (Helsinki downtown, Manhattan midtown, DieselNet Amherst, Nuuksio trails, Helsinki archipelago, etc.). Each anchor is expanded through a deterministic variant policy: window sizes (500–5000 m), cardinal offsets, and `network_type` (`drive` or `all`) constrained by anchor metadata.

**Synthetic generators** (thirteen algorithms) complement OSM where literature requires topologies not tied to a single bbox (radial city, hub-and-spoke) or where trace data provide contact patterns without venue geometry (INFOCOM events, Haggle clusters, RollerNet corridor mobility). Generators use SHA-256-derived seeds for reproducibility.

**Trace-reference anchors** map contact-trace literature to synthetic instantiation: e.g., `infocom_event_compact` → `conference_event_compact` generator; `haggle_contacts_only` → `clustered_communities`, with geographic pedestrian context optionally represented separately (`cambridge_haggle` OSM). This indirect policy preserves trace fidelity without misrepresenting traces as maps.

Batch composition targets approximately fifty percent OSM-derived and fifty percent synthetic/trace-reference candidates, stratified by anchor, archetype, and source type.

---

## Archetype definition

Each archetype is specified in `map_archetype_definitions_v1.csv` with expected feature bands, literature rationale, and The ONE movement affordances (map-based routing, WDM candidacy, bus routes, cluster overlay). A companion topology matrix (`map_archetype_topology_matrix_v1.csv`) records ordinal assignments along dimensions including density, regularity, compactness, connectivity pattern, centralization, corridor structure, partition/bridge structure, tree-like structure, and primary mobility role.

Fifteen archetypes balance two risks: fewer would merge DTN-distinguishable structures (e.g., vehicular grid vs irregular urban core; radial city vs hub-and-spoke); more would label continuous OSM/generator gradients already measured numerically. Separability analysis in normalized feature space yields a global inter/intra centroid distance ratio of approximately **1.78** — partial overlap is expected and acceptable because archetypes encode coverage and movement semantics, not perfect linear separability.

---

## Map validation

Each candidate map undergoes structural validation before entering the feature pool. Maps with status PASS, WARNING, or STRESS are retained for saturation analysis; FAIL maps are excluded from features but counted in batch yield statistics. In the reference run (N = 2000 candidates evaluated), **1378** maps passed validation and **622** failed (~31.1% failure rate), including OSM build failures and degenerate synthetic graphs. At the methodological stop batch (1200), the failure rate was ~12.1% (1055 valid / 145 invalid).

Validation ensures simulatable geometry (connected usable components, plausible scales) but does not guarantee geographic representativeness of every city on Earth.

---

## Feature extraction

For each valid map we extract thirty-three numeric features from the road graph and embedding: world scale, node/edge counts, road density, degree and dead-end statistics, component and bridge structure, approximate diameter and path length, orientation entropy, and shape scores (gridness, corridor, radial, partition, community, tree-like). Features are stored in `map_space_saturation_features.csv`.

For saturation analysis, features are **z-score normalized cumulatively per evaluation batch** (no lookahead): statistics at batch B use only maps with `batch_target ≤ B`. `source_type` is one-hot encoded, yielding a thirty-six-dimensional vector for distance and clustering. A globally normalized export exists for cross-sectional archetype analysis but primary stop metrics use cumulative normalization.

---

## Saturation analysis

Saturation is measured in **feature space**, not by archetype label counts. For each cumulative batch B ∈ {100, 200, 400, 600, 800, 1000, 1200, **1600**, **2000**} we compute:

- Count of valid maps and unique feature vectors (exact deduplication tolerance 10⁻⁶)
- k-medoids clustering (k ≈ √n, cap 50) and cluster count
- Mean/median nearest-neighbour L2 distance in normalized space
- Distance to k-medoid representatives (mean and max)
- PCA variance explained (2, 5, 10 components)
- **Near-redundancy:** fraction of new valid maps in a tranche whose L2 distance to any map in the previous cumulative set is below **0.25**

Archetype coverage reached **15/15** from batch 100 onward; subsequent growth addressed redundant feature-space filling and OSM queue completion. At the methodological stop (batch 1200) the pool contains **32** k-medoids clusters, mean NN distance **0.34**, and PCA reports **93%** variance in ten components. A robustness extension to N = 2000 raised the evaluated pool to **37** clusters and **1378** valid maps while post-1200 tranches remained majority redundant or invalid.

Per-archetype internal analysis shows sample sizes from 33 to 169 valid maps per family, with status ACCEPTABLE or WELL_COVERED for all fifteen; no archetype requires additional categorical splitting.

---

## Stopping rule

Generation follows a documented batch ladder. A **strict stop rule** (YAML) requires seven conditions over two consecutive batches (cluster growth &lt; 5%, medoid improvement &lt; 5%, stable archetype and source coverage, majority redundant/invalid contribution). For the reference run, a **deliberate extension** beyond batch 800 applied relaxed **extension confirmation** criteria:

- Previous batch ≥ 800 and 15/15 archetypes covered
- Marginal valid growth &lt; 30% of previous valid pool (not an absolute cap on new maps)
- Relative cluster growth &lt; 16%; mean medoid improvement &lt; 8%
- ≥ 50% of each extension tranche near-redundant or invalid
- No new archetypes or source types

Transitions **800→1000** and **1000→1200** both satisfied these conditions (`extension_confirmed: true`). Sensitivity analysis shows the ≥ 50% redundant+invalid conclusion holds for near-redundancy thresholds **0.15–0.35**.

A **robustness extension** to batches 1600 and 2000 applied the same criteria with `prev_batch ≥ 1200`. Transitions **1200→1600** and **1600→2000** also passed (`robustness_extension_confirmed: true`), yielding decision label `stop_at_1200_confirmed_by_2000`: the methodological stop remains batch 1200; the extension confirms it was not premature.

> The extension to 2000 candidates does not aim to prove that no additional maps can be generated. Instead, it tests whether additional candidates provide non-redundant feature-space coverage within the declared map-topology design space.

**Batch 800 is treated as the operational saturation point, while batch 1200 is retained as the methodological stopping point because two consecutive post-800 extensions confirmed diminishing feature-space returns, and a further extension to 2000 confirmed the same pattern post-1200.**

At batch 800: 696 valid maps. From 800 to 1200: +359 further valid maps (+51.6% relative to the 800 pool). From 1200 to 2000: +323 further valid maps (+30.6% relative to the 1200 pool), while post-1200 tranches were ≥72% redundant or invalid — confirming diminishing **non-redundant** returns, not zero new maps.

---

## Limitations

### Scope boundaries (explicit non-claims)

We do **not** claim:

- Coverage of all possible maps on Earth or all geographic environments
- Coverage of all possible mobility situations in the world
- Complete mathematical coverage of reality
- That no further maps could ever be generated

### Permitted claims

We **do** claim:

- **Declared design-space coverage:** all fifteen archetypes have at least one validation-passing map; nineteen anchors documented in YAML (fifteen OSM-downloadable, four trace-only)
- **Feature-space saturation** under stated metrics at batch 1200 (methodological stop)
- **Robustness confirmation** at N = 2000 without overturning the 1200 stop
- **Diminishing non-redundant returns** in post-800 and post-1200 batches
- **Approximate coverage** of the generated map-design space sufficient for structured scenario sampling in The ONE

### Additional limitations

- Feature vectors summarize graph topology, not building interiors, multi-floor venues, or time-varying road closures
- OSM currency and completeness vary by region; Nordic and US anchors are over-represented relative to global geography
- Trace-reference synthetics approximate contact-trace literature topology, not venue-specific floor plans
- Saturation is conditional on the chosen feature set and thresholds; alternative features might extend apparent diversity
- Validation failures (~12%) indicate filtering, not exhaustive enumeration of failure modes worldwide

---

## Summary statistics (reference run)

| Quantity | Value |
|----------|-------|
| Candidates evaluated (max N) | 2000 |
| Validation-passing maps (max) | 1378 |
| Validation failures (max) | 622 |
| Methodological stop batch | 1200 |
| Valid maps at methodological stop | 1055 |
| Archetypes covered | 15/15 |
| Anchors with valid maps | 19 (+ 570 synthetic without geographic anchor) |
| k-medoids clusters (batch 1200 / 2000) | 32 / 37 |
| OSM / synthetic / trace-reference valid fraction (batch 2000) | 43.5% / 41.4% / 15.2% |
| Stop decision | `stop_at_1200_confirmed_by_2000`, `robustness_extension_confirmed: true` |

---

## Suggested figure references

**Saturation (batch cumulative):** `valid_vs_generated.png`, `clusters_vs_generated.png`, `mean_nn_dist_vs_generated.png`, `improvement_pct_vs_batch.png`, `archetype_coverage_vs_batch.png`, `source_type_vs_batch.png`

**Archetype analysis:** `archetype_centroid_distance_heatmap.png`, `archetype_pca_projection.png`, `saturation_by_archetype_valid_maps.png`

**Robustness:** `near_redundancy_threshold_sensitivity.png`

---

*Source artefacts: `map_space_saturation_decision.json`, `map_archetype_justification_v1.md`, `map_generation_stop_decision_v1.md`, `map_archetype_separability_report.md`, `map_saturation_by_archetype_report.md`, `near_redundancy_threshold_sensitivity_report.md`.*
