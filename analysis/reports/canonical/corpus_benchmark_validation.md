# Corpus v2 benchmark validation

Generated: 2026-06-04 10:26 UTC

## Executive summary

- **Corpus:** `corpus_v1` — **540** scenarios (45 bases × 12 TP)
- **Settings files:** 540
- **Manifest rows:** 540
- **Output metrics:** 540 rows
- **Spatial metrics:** 540 rows
- **Scenarios needing attention (non-ok, non-valido_extremo):** 124

### Validation status counts

| Status | Count |
|--------|------:|
| `configuracion_sospechosa` | 112 |
| `error_probable` | 10 |
| `ok` | 318 |
| `pendiente_revision` | 2 |
| `valido_extremo` | 98 |

## Completeness

| Check | Result |
|-------|--------|
| `.settings` in corpus_v1 | 540 |
| manifest.csv data rows | 540 |
| Scenario bases | 45 |
| Traffic profiles | 12 |
| output_metrics.csv | 540 |
| spatial_occupancy_metrics.csv | 540 |
| indirect_features_diego.csv | 540 |
| message_creation_time_summary.csv | 540 |
| useful_simulation_time_metrics.csv | 540 |
| Null delivery_ratio | 10 |
| Zero delivery_ratio | 4 |
| Zero total_encounters | 0 |

## Problem distribution

### By family

| family | ok | valido_extremo | pendiente_revision | configuracion_sospechosa | error_probable |
|--------|---:|---:|---:|---:|---:|
| `01_urban` | 72 | 12 | 0 | 0 | 0 |
| `02_campus` | 53 | 12 | 1 | 6 | 0 |
| `03_vehicles` | 55 | 5 | 0 | 0 | 0 |
| `04_rural` | 51 | 16 | 1 | 66 | 10 |
| `05_disaster` | 34 | 36 | 0 | 38 | 0 |
| `06_social` | 53 | 17 | 0 | 2 | 0 |

### By traffic profile

| TP | ok | valido_extremo | pendiente_revision | configuracion_sospechosa | error_probable |
|----|---:|---:|---:|---:|---:|
| `TP01` | 32 | 1 | 0 | 11 | 1 |
| `TP02` | 33 | 1 | 0 | 10 | 1 |
| `TP03` | 33 | 1 | 0 | 10 | 1 |
| `TP04` | 8 | 34 | 0 | 2 | 1 |
| `TP05` | 30 | 2 | 0 | 13 | 0 |
| `TP06` | 32 | 1 | 0 | 11 | 1 |
| `TP07` | 32 | 1 | 0 | 11 | 1 |
| `TP08` | 29 | 1 | 0 | 15 | 0 |
| `TP09` | 9 | 30 | 0 | 5 | 1 |
| `TP10` | 25 | 11 | 0 | 8 | 1 |
| `TP11` | 26 | 10 | 0 | 8 | 1 |
| `TP12` | 29 | 5 | 2 | 8 | 1 |

### error_probable scenarios

- `R2_VillagesTrails_InterVillage__TP01_Baseline` — missing delivery_ratio (simulation report incomplete or absent)
- `R2_VillagesTrails_InterVillage__TP02_LowLoad` — missing delivery_ratio (simulation report incomplete or absent)
- `R2_VillagesTrails_InterVillage__TP03_ManySmall` — missing delivery_ratio (simulation report incomplete or absent)
- `R2_VillagesTrails_InterVillage__TP04_FewLarge` — missing delivery_ratio (simulation report incomplete or absent)
- `R2_VillagesTrails_InterVillage__TP06_OneToMany` — missing delivery_ratio (simulation report incomplete or absent)
- `R2_VillagesTrails_InterVillage__TP07_BurstWindow` — missing delivery_ratio (simulation report incomplete or absent)
- `R2_VillagesTrails_InterVillage__TP09_Bimodal` — missing delivery_ratio (simulation report incomplete or absent)
- `R2_VillagesTrails_InterVillage__TP10_Storm` — missing delivery_ratio (simulation report incomplete or absent)
- `R2_VillagesTrails_InterVillage__TP11_ManyToOne` — missing delivery_ratio (simulation report incomplete or absent)
- `R2_VillagesTrails_InterVillage__TP12_GroupToGroup` — missing delivery_ratio (simulation report incomplete or absent)

## Methodological answers

### 1. Is corpus_v1 sufficiently complete to use as a benchmark?

**Yes for configuration/diversity benchmarking** — all 540 `.settings`, manifest rows, feature matrices, output metrics, spatial metrics, and auxiliary CSVs align with corpus scope.

**Almost ready for routing protocol comparison** — two scenarios lack output metrics (`error_probable`, see CSV); message analysis window (policy B) is not yet enforced in the pipeline.

### 2. Which scenarios should be kept as valid extremes?

- **TP12** cross-group partition controls (`include_control`)
- **TP04 / TP05 / TP10** stress load and CriticalTTL tiers (`include_stress`)
- **R10 / R11** and disconnected bases with `ZERO_CONTACTS` (`include_control` / `document_as_extreme`)
- **MAP_UNDERUSED** WDM scenarios (~8–10% world grid coverage on roads — not a simulation failure)

Count `valido_extremo`: **98** scenarios.

### 3. Which scenarios need review before the paper?

- **10** scenarios with missing outputs → re-simulate
- **112** suspicious configs (zero delivery with contacts, etc.)
- **2** pending revision (P0/P1 map, worldSize, latency window)
- Urban WDM **MAP_TOO_LARGE / MAP_UNDERUSED** — document in Methods, optional worldSize crop

### 4. Which problems do NOT block the paper?

- Diversity metrics frozen in `RESULTADOS_ACTUALES.md` (540 scenarios, `corpus_v1` only)
- Low spatial *world* coverage on map-based mobility (roads vs rectangle world)
- High-load TP extremes (TP04/TP05/TP10) reported separately from main-tier claims when needed
- 24 disconnected control scenarios (documented in tp_validation_report)

### 5. Which problems COULD block protocol comparison?

- **Message analysis window not implemented** — compare protocols only after policy B in pipeline
- **Missing output metrics** (2 scenarios) — exclude or re-simulate before ranking
- **Mixing P0 scenarios in main split** without stratification (use `manifest_revision.csv` benchmark_split)
- **TP05 zero-delivery** in aggregate main-tier ranking without separating high-load TPs

## Recommended splits

Align protocol runs with `corpus_v1/manifest_revision.csv`:

- **main:** TP01–TP08 on viable bases; exclude `error_probable` and `configuracion_sospechosa`
- **Extreme load TPs:** TP09–TP11, TP04–TP06 on environmental bases
- **control:** TP12 partition, disconnected extremes

## Next steps

1. Re-simulate `S1_StrongCommunities_SeparateClusters__TP03_ManySmall` and `__TP11_ManyToOne`
2. Implement TTL-aware message window in `output_metrics` pipeline
3. Filter validation CSV when exporting paper tables (`validation_status == ok` for main tier)
4. Re-run after settings revision: `validate_corpus_benchmark.py`

## Artifacts

- Validation table: [`data/corpus_benchmark_validation.csv`](../data/corpus_benchmark_validation.csv)
- Diagnosis: [`data/scenario_diagnosis.csv`](../data/scenario_diagnosis.csv)
- TP validation: [`tp_validation_report.md`](tp_validation_report.md)
- Frozen diversity: [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)
