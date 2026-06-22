# Map selection pool audit (v1)

Generated: 2026-06-22T10:13:22.763428+00:00

## 1. Pool definition

- **Official selection pool:** `batch_target <= 1200` and validation in PASS/WARNING/STRESS.
- **Pool size:** 1055 maps (expected ~1055).
- **Phase 1 saturation decision:** `stop_at_1200_confirmed_by_2000`.

### Why 1200 and not 2000?

Phase 1 extended generation to 2000 candidates as a **robustness check**, not as the design pool.
The decision `stop_at_1200_confirmed_by_2000` confirms that saturation metrics stabilised before 1200;
maps added only in batches 1600–2000 are excluded from representative selection to avoid
contaminating the official design space with post-saturation redundancy.

- Valid maps @2000 (reference): 1378
- Valid maps added post-1200 only: 323
- Excluded from pool (FAIL @≤1200): 0

## 2. Coverage summary

- Archetypes: **15/15**
- Source types: **3/3** (osm=599, synthetic=337, trace_reference_synthetic=119)
- Documented anchors present: **19**

## 3. Validation status

| status | count |
|--------|------:|
| PASS | 1010 |
| STRESS | 45 |

WARNING and STRESS maps are **included** because they remain structurally usable for scenario design;
FAIL maps are excluded.

## 4. Archetype distribution

| archetype | count |
|-----------|------:|
| bus_route_urban_suburban | 38 |
| campus_compact | 98 |
| clustered_communities | 45 |
| compact_residential | 41 |
| conference_event_compact | 45 |
| corridor_linear | 70 |
| dense_urban_irregular | 169 |
| hub_and_spoke | 45 |
| industrial_disrupted | 128 |
| island_or_partitioned | 86 |
| radial_city | 42 |
| rural_roads | 52 |
| sparse_trails | 85 |
| suburban_low_density | 33 |
| urban_grid | 78 |

## 5. Source type distribution

| source_type | count |
|-------------|------:|
| osm | 599 |
| synthetic | 337 |
| trace_reference_synthetic | 119 |

## 6. Anchor distribution

| anchor_id | count |
|-----------|------:|
| cambridge_haggle | 42 |
| dieselnet_amherst | 38 |
| haggle_contacts_only | 45 |
| helsinki_archipelago | 42 |
| helsinki_disrupted | 42 |
| helsinki_downtown | 41 |
| infocom_2006_trace | 23 |
| infocom_event_compact | 22 |
| kallio_community | 41 |
| kumpula_campus | 41 |
| lapland_rural_sparse | 41 |
| london_industrial_corridor | 41 |
| manhattan_midtown | 33 |
| mit_campus_reality | 41 |
| nuuksio_sparse_trails | 41 |
| rollernet_trace | 29 |
| sf_cabspotting_downtown | 41 |
| sf_mission_corridor | 41 |
| tampere_suburban | 33 |

## 7. Excluded maps

- FAIL with batch ≤ 1200: 0
- Valid maps only in extension batches (>1200): 323 (reference only)

## 8. Output

- Pool CSV: `scenarios/analysis/data/map_selection_pool_v1.csv`
