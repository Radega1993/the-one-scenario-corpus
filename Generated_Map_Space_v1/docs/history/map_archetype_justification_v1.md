# Formal justification of the 15 map-topology archetypes (v1)

**Status:** Phase 1 closure — reviewer-facing  
**Reference run:** N = 1200 candidates, 1055 validation-passing maps, 15/15 archetypes covered  
**Sources:** `map_archetype_definitions_v1.csv`, `map_design_space_saturation_v1.yaml`, `map_archetype_topology_matrix_v1.csv`, `map_space_saturation_features.csv`

---

## 1. Why we use archetypes

Map-topology archetypes are **declared cells** in a design space, not narrative labels. Each archetype names a family of road-network structures that recur in DTN/OppNet literature and in The ONE map-based scenarios, and that induce distinguishable routing, contact, and movement behaviour in simulation.

Archetypes serve three methodological roles:

1. **Coverage contract** — we can state whether every declared family has at least one valid map (categorical completeness).
2. **Stratified generation** — OSM anchors, synthetic generators, and trace-reference parametrizations are assigned to archetypes so batches do not collapse into one dominant topology.
3. **Interpretability bridge** — reviewers can connect Helsinki downtown, DieselNet buses, INFOCOM events, and Haggle clusters to explicit topology classes without reading 1055 map IDs.

Archetypes are **not** a claim that the real world has exactly fifteen map types. They are the **minimum discrete partition** of our declared design space that preserves DTN-relevant structural distinctions while leaving continuous variation to numeric features and generator parameters.

---

## 2. Why archetypes are not narrative families

Narratives such as “Helsinki urban DTN” or “INFOCOM conference” appear in the repository as **anchors** and **literature references**, not as archetype names. The separation is intentional:

| Layer | Example | Role |
|-------|---------|------|
| Narrative / anchor | `helsinki_downtown`, `infocom_event_compact` | Documents provenance and download or parametrization policy |
| Archetype | `dense_urban_irregular`, `conference_event_compact` | Declares topology class and expected feature bands |
| Map instance | `OSM_helsinki_downtown_exact_1000m_0m_0042` | One concrete network in the pool |

A single narrative anchor maps to one primary archetype, but one archetype may aggregate several anchors (e.g. `dense_urban_irregular` ← Helsinki, SF Cabspotting, Cambridge Haggle). Conversely, trace-only anchors (INFOCOM, Haggle contacts) **do not** supply downloadable maps; they parametrize synthetics that instantiate archetypes indirectly. Confusing narrative with archetype would make completeness unverifiable and would mix provenance with topology.

---

## 3. Topological dimensions that generate the archetypes

Each archetype is characterized along dimensions that are **operationalized** by extracted graph features (33 numeric columns) and shape scores. The topology matrix (`map_archetype_topology_matrix_v1.csv`) records ordinal assignments; features supply continuous measurement within and across archetypes.

### 3.1 Density

**Operational features:** `road_density`, `n_nodes`, `n_edges`, `total_road_length_m`, `avg_degree`.  
**Archetype spread:** from `rural_roads` / `sparse_trails` (low) through `dense_urban_irregular` / `urban_grid` (high). Density separates vehicular urban cores from rural opportunistic networks.

### 3.2 Regularity

**Operational features:** `gridness_score`, `orientation_entropy`.  
**Archetype spread:** `urban_grid` (high regularity) vs `dense_urban_irregular` (mixed/low). Regularity affects predictable routing and WDM suitability.

### 3.3 Compactness

**Operational features:** `useful_area_ratio`, `graph_diameter_approx`, `world_area`.  
**Archetype spread:** `campus_compact`, `conference_event_compact`, `compact_residential` (high compactness) vs elongated `corridor_linear`. Compactness bounds encounter horizons in pedestrian and event mobility.

### 3.4 Connectivity

**Operational features:** `n_components`, `largest_component_ratio`, `avg_degree`, `dead_end_ratio`.  
**Archetype spread:** single-component urban grids vs `island_or_partitioned` (multi-component with bridges). Connectivity determines reachability under disruption.

### 3.5 Centralization

**Operational features:** `radial_score`, hub-spoke degree patterns, `tree_like_score`.  
**Archetype spread:** `radial_city` and `hub_and_spoke` vs decentralized grids. Centralization models hotspot and transit-hub DTN behaviour.

### 3.6 Corridor structure

**Operational features:** `corridor_score`, aspect ratio proxies (`world_size_x` / `world_size_y`), `circuity_approx`.  
**Archetype spread:** `corridor_linear`, `bus_route_urban_suburban`. Corridors encode linear mobility along arterials or bus routes.

### 3.7 Partition / bridges

**Operational features:** `partition_score`, `n_components`, `bridge_edges_count`, `bridge_edges_ratio`.  
**Archetype spread:** `island_or_partitioned`, `clustered_communities`, `industrial_disrupted`. Partitions model fragmented reachability distinct from single-component urban cores.

### 3.8 Tree-like structure

**Operational features:** `tree_like_score`, `dead_end_ratio`, `avg_degree`.  
**Archetype spread:** `sparse_trails`, `hub_and_spoke`, `suburban_low_density` (cul-de-sacs). Tree-like networks increase dead ends and alter store-carry-forward paths.

### 3.9 Compact event mobility

**Operational features:** `community_score`, bounded `graph_diameter_approx`, high internal clustering.  
**Archetype spread:** `conference_event_compact`, partially `clustered_communities`. Event mobility is trace-inspired and compact by design.

### 3.10 Primary mobility role (vehicular / pedestrian / rural / social)

Encoded in archetype definitions (`supports_map_based`, `supports_route_movement`, `supports_wdm`, bus-route flags) and anchor `expected_use` in YAML. Separates e.g. `bus_route_urban_suburban` from `corridor_linear` despite similar corridor scores.

---

## 4. Why fewer than 15 archetypes would merge distinct structures

Collapsing archetypes would blur behaviours that DTN studies treat separately:

| If merged | Lost distinction |
|-----------|------------------|
| `urban_grid` + `dense_urban_irregular` | Gridness/WDM vehicular baseline vs irregular European cores |
| `radial_city` + `hub_and_spoke` | Full radial rings vs sparse hotspot spokes |
| `corridor_linear` + `bus_route_urban_suburban` | Generic corridor vs DieselNet bus arterial semantics |
| `sparse_trails` + `rural_roads` | Pedestrian tree trails vs sparse vehicular roads |
| `conference_event_compact` + `campus_compact` | Event-venue scale vs institutional campus |
| `clustered_communities` + `compact_residential` | Social trace clusters vs geographic residential OSM |
| `island_or_partitioned` + `industrial_disrupted` | Land partitions vs articulation without mandatory splits |

Fewer than 15 cells would therefore **under-specify** the declared design space relative to literature anchors already committed in the YAML.

---

## 5. Why more than 15 archetypes would create artificial labels

Many apparent “new types” are **continuous** along features already extracted:

- OSM window size (500–5000 m) and offset variants shift density and diameter without new taxonomy.
- Synthetic parameter grids (grid rows/cols, jitter, removal rate) explore intra-archetype diversity.
- Slight gridness differences between two European districts do not warrant separate archetypes if both satisfy `dense_urban_irregular` bands.

Adding archetypes for every city or parameter combination would:

1. Explode categorical labels while **not** improving saturation metrics (redundant in feature space).
2. Make the stopping rule depend on label churn rather than feature-space coverage.
3. Conflate geographic novelty with topological novelty.

Continuous gradations belong in **numeric features** and batch sampling, not in proliferating archetype names.

---

## 6. How fine-grained differences are captured by numeric features

Within each archetype, maps vary across 33 numeric topology features plus `source_type`. Examples:

- **Same archetype, different sources:** `dense_urban_irregular` includes OSM Helsinki, SF, Cambridge and `jittered_grid` synthetics — distinguished by `orientation_entropy`, `gridness_score`, scale columns.
- **Same generator, different parameters:** `industrial_disrupted` spans removal rates and articulation counts.
- **Saturation is feature-based:** stop rules use k-medoids clusters, nearest-neighbour distances, and near-redundancy (NN &lt; 0.25 in normalized space), not archetype label counts.

Thus archetypes answer “**which families are represented?**” while features answer “**how much non-redundant diversity exists within and across families?**”

---

## 7. Summary table (15 archetypes, literature, valid maps at N = 1200)

| Archetype | DTN / The ONE basis | Valid maps | Primary source modes |
|-----------|---------------------|------------|----------------------|
| `urban_grid` | Manhattan / NYC taxi grid | 78 | OSM + synthetic |
| `dense_urban_irregular` | Helsinki downtown, SF Cabspotting, Cambridge | 169 | OSM + synthetic |
| `campus_compact` | Kumpula, Reality Mining MIT | 98 | OSM + synthetic |
| `compact_residential` | Kallio community compact | 41 | OSM only |
| `corridor_linear` | SF Mission, RollerNet-inspired | 70 | OSM + synthetic + trace |
| `bus_route_urban_suburban` | DieselNet / PVTA Amherst | 38 | OSM + synthetic |
| `radial_city` | European radial plans | 42 | Synthetic only |
| `hub_and_spoke` | Hotspot / transit hub patterns | 45 | Synthetic only |
| `sparse_trails` | Nuuksio trails | 85 | OSM + synthetic |
| `rural_roads` | Lapland sparse roads | 52 | OSM + synthetic |
| `industrial_disrupted` | Helsinki Disrupted, London industrial | 128 | OSM + synthetic |
| `island_or_partitioned` | Helsinki archipelago | 86 | OSM + synthetic |
| `conference_event_compact` | INFOCOM contact traces | 45 | Trace + synthetic |
| `clustered_communities` | Haggle social DTN | 45 | Trace + synthetic |
| `suburban_low_density` | Tampere suburbs | 33 | OSM only |

---

## 8. Relation to separability and saturation analyses

- **Separability** (`map_archetype_separability_report.md`): centroid distances in normalized feature space show partial overlap between nearby archetypes; perfect separation is **not** required.
- **Intra-archetype saturation** (`map_saturation_by_archetype_report.md`): per-archetype sample sizes and internal NN distances show adequate coverage without further categorical splits.
- **Global saturation** (`map_space_saturation_report.md`): stopping at N = 1200 is justified by feature-space diminishing returns, not by adding archetypes.

---

## 9. Scope boundary

We claim **declared design-space coverage** (15/15 archetypes with valid maps) and **feature-space saturation** under documented metrics. We do **not** claim coverage of all real-world maps or environments. See `paper_ready_map_generation_section_v1.md` for paper-ready wording.

---

## Downloaded real traces

External CRAWDAD / IEEE DataPort connectivity and mobility traces used as
**design anchors / trace references** are staged under
`scenarios/external_traces/` (raw payloads gitignored; not part of the
redistributable SMS-v1 map assets). Source platform:
[IEEE DataPort](https://ieee-dataport.org/).

Current registry size: **16** packages (see
[`../../external_traces/registry/real_trace_inventory_v1.md`](../../external_traces/registry/real_trace_inventory_v1.md)).

### Highlight: `haggle_one_cambridge_city_complete`

| Field | Value |
|-------|-------|
| Origin | `cambridge/haggle/imote/content` (v. 2009-05-29) |
| Format | The ONE `StandardEventsReader` |
| Nodes / contacts / duration | 52 / 10873 / 987529 s (~11.43 days) |
| Archetypes (design support) | `conference_event_compact`, `clustered_communities`, `campus_compact` |
| SMS-v1 anchors supported | `infocom_event_compact`, `infocom_2006_trace`, `haggle_contacts_only`, `cambridge_haggle` |
| Status | downloaded and validated |
| Note | raw trace not redistributed |

Other downloaded families currently registered include `cambridge/haggle`
(source archives), `upmc/rollernet`, `umass/diesel`, `epfl/mobility`,
`roma/taxi`, `oviedo/asturies-er`, `coppe-ufrj/RioBuses`, `dartmouth/wardriving`, `st_andrews/sassy`, `st_andrews/locshare`, and
`microsoft/vanlan`.

Rationale pointer: [`map_real_trace_inventory_and_anchor_rationale_v1.md`](map_real_trace_inventory_and_anchor_rationale_v1.md).

These downloads **justify families of scenarios** already declared in the
15-archetype contract; they do **not** automatically add new archetypes.

### Revised generation architecture (v2, under review)

The baseline generator treated some trace anchors as **labels only**. The revised
pipeline (dry-run ready; full regeneration deferred) connects OSM, synthetic, and
real-trace roles explicitly:

- Audit: [`map_generation_audit_v2.md`](map_generation_audit_v2.md)
- Architecture: [`map_generation_architecture_v2.md`](map_generation_architecture_v2.md)
- Trace policy review: [`trace_to_map_generation_review_v1.md`](trace_to_map_generation_review_v1.md)
- Config: `scenarios/analysis/config/map_design_space_revised_v2.yaml`
- Policy: `scenarios/analysis/config/trace_to_map_generation_policy_v1.yaml`

The 15 archetypes above are **unchanged**.

---

*Topology matrix:* `scenarios/analysis/data/map_archetype_topology_matrix_v1.csv`  
*Definitions:* [`data/map_archetype_definitions_v1.csv`](../../data/map_archetype_definitions_v1.csv)
