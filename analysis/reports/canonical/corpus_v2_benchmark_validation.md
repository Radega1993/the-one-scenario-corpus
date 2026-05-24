# Corpus v2 benchmark validation

Generated: 2026-05-24 20:47 UTC

## Executive summary

- **Corpus:** `corpus_v2` — **720** scenarios (60 bases × 12 TP)
- **Settings files:** 720
- **Manifest rows:** 720
- **Output metrics:** 720 rows
- **Spatial metrics:** 720 rows
- **Scenarios needing attention (non-ok, non-valido_extremo):** 134

### Validation status counts

| Status | Count |
|--------|------:|
| `configuracion_sospechosa` | 130 |
| `ok` | 274 |
| `pendiente_revision` | 4 |
| `valido_extremo` | 312 |

## Completeness

| Check | Result |
|-------|--------|
| `.settings` in corpus_v2 | 720 |
| manifest.csv data rows | 720 |
| Scenario bases | 60 |
| Traffic profiles | 12 |
| output_metrics.csv | 720 |
| spatial_occupancy_metrics.csv | 720 |
| indirect_features_diego.csv | 720 |
| message_creation_time_summary.csv | 720 |
| useful_simulation_time_metrics.csv | 720 |
| Null delivery_ratio | 0 |
| Zero delivery_ratio | 65 |
| Zero total_encounters | 24 |

## Problem distribution

### By family

| family | ok | valido_extremo | pendiente_revision | configuracion_sospechosa | error_probable |
|--------|---:|---:|---:|---:|---:|
| `01_urban` | 22 | 49 | 2 | 11 | 0 |
| `02_campus` | 56 | 9 | 1 | 6 | 0 |
| `03_vehicles` | 49 | 7 | 1 | 3 | 0 |
| `04_rural` | 56 | 40 | 0 | 48 | 0 |
| `05_disaster` | 34 | 18 | 0 | 56 | 0 |
| `06_social` | 57 | 9 | 0 | 6 | 0 |
| `07_traffic` | 0 | 180 | 0 | 0 | 0 |

### By traffic profile

| TP | ok | valido_extremo | pendiente_revision | configuracion_sospechosa | error_probable |
|----|---:|---:|---:|---:|---:|
| `TP01` | 26 | 21 | 0 | 13 | 0 |
| `TP02` | 26 | 22 | 0 | 12 | 0 |
| `TP03` | 28 | 21 | 0 | 11 | 0 |
| `TP04` | 17 | 37 | 0 | 6 | 0 |
| `TP05` | 24 | 32 | 0 | 4 | 0 |
| `TP06` | 24 | 19 | 0 | 17 | 0 |
| `TP07` | 26 | 21 | 0 | 13 | 0 |
| `TP08` | 19 | 19 | 0 | 22 | 0 |
| `TP09` | 16 | 35 | 0 | 9 | 0 |
| `TP10` | 23 | 28 | 0 | 9 | 0 |
| `TP11` | 26 | 29 | 0 | 5 | 0 |
| `TP12` | 19 | 28 | 4 | 9 | 0 |

## Methodological answers

### 1. Is corpus_v2 sufficiently complete to use as a benchmark?

**Yes for configuration/diversity benchmarking** — all 720 `.settings`, manifest rows, feature matrices, output metrics, spatial metrics, and auxiliary CSVs are present (720/720).

**Almost ready for routing protocol comparison** — two scenarios lack output metrics (`error_probable`, see CSV); message analysis window (policy B) is not yet enforced in the pipeline.

### 2. Which scenarios should be kept as valid extremes?

- **TP12** cross-group partition controls (`include_control`)
- **TP04 / TP05 / TP10** stress load and CriticalTTL tiers (`include_stress`)
- **R10 / R11** and disconnected bases with `ZERO_CONTACTS` (`include_control` / `document_as_extreme`)
- **07_traffic** family (traffic-pattern laboratory)
- **MAP_UNDERUSED** WDM scenarios (~8–10% world grid coverage on roads — not a simulation failure)

Count `valido_extremo`: **312** scenarios.

### 3. Which scenarios need review before the paper?

- **0** scenarios with missing outputs → re-simulate
- **130** suspicious configs (zero delivery with contacts, etc.)
- **4** pending revision (P0/P1 map, worldSize, latency window)
- Urban WDM **MAP_TOO_LARGE / MAP_UNDERUSED** — document in Methods, optional worldSize crop

### 4. Which problems do NOT block the paper?

- Diversity metrics frozen in `RESULTADOS_ACTUALES.md` (720 scenarios)
- Low spatial *world* coverage on map-based mobility (roads vs rectangle world)
- Stress-tier extremes reported separately from main claims
- 24 disconnected control scenarios (documented in tp_validation_report)

### 5. Which problems COULD block protocol comparison?

- **Message analysis window not implemented** — compare protocols only after policy B in pipeline
- **Missing output metrics** (2 scenarios) — exclude or re-simulate before ranking
- **Mixing P0 scenarios in main split** without stratification (use `manifest_revision.csv` benchmark_split)
- **TP05 zero-delivery** in aggregate main-tier ranking without stress tier separation

## Recommended splits

Align protocol runs with `corpus_v2/manifest_revision.csv`:

- **main:** TP01–TP08 on viable bases; exclude `error_probable` and `configuracion_sospechosa`
- **stress:** TP09–TP11, TP04–TP06 load, all `07_traffic`
- **control:** TP12 partition, disconnected extremes

## Next steps

1. Re-simulate `S1_StrongCommunities_SeparateClusters__TP03_ManySmall` and `__TP11_ManyToOne`
2. Implement TTL-aware message window in `output_metrics` pipeline
3. Filter validation CSV when exporting paper tables (`validation_status == ok` for main tier)
4. Re-run after settings revision: `validate_corpus_v2_benchmark.py`

## Artifacts

- Validation table: [`data/corpus_v2_benchmark_validation.csv`](../data/corpus_v2_benchmark_validation.csv)
- Diagnosis: [`data/scenario_diagnosis.csv`](../data/scenario_diagnosis.csv)
- TP validation: [`tp_validation_report.md`](tp_validation_report.md)
- Frozen diversity: [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)
