# Corpus v2 benchmark validation

Generated: 2026-06-05 12:42 UTC

## Executive summary

- **Corpus:** `corpus_v1` — **540** scenarios (45 bases × 12 TP)
- **Settings files:** 540
- **Manifest rows:** 540
- **Output metrics:** 600 rows
- **Spatial metrics:** 540 rows
- **Scenarios needing attention (non-ok, non-valido_extremo):** 118

### Validation status counts

| Status | Count |
|--------|------:|
| `configuracion_sospechosa` | 64 |
| `ok` | 235 |
| `pendiente_revision` | 54 |
| `valido_extremo` | 187 |

## Completeness

| Check | Result |
|-------|--------|
| `.settings` in corpus_v1 | 540 |
| manifest.csv data rows | 540 |
| Scenario bases | 45 |
| Traffic profiles | 12 |
| output_metrics.csv | 600 |
| spatial_occupancy_metrics.csv | 540 |
| indirect_features_diego.csv | 540 |
| message_creation_time_summary.csv | 540 |
| useful_simulation_time_metrics.csv | 540 |
| Null delivery_ratio | 0 |
| Zero delivery_ratio | 4 |
| Zero total_encounters | 0 |

## Problem distribution

### By family

| family | ok | valido_extremo | pendiente_revision | configuracion_sospechosa | error_probable |
|--------|---:|---:|---:|---:|---:|
| `01_urban` | 0 | 34 | 38 | 12 | 0 |
| `02_campus` | 54 | 11 | 1 | 6 | 0 |
| `03_vehicles` | 0 | 45 | 12 | 3 | 0 |
| `04_rural` | 103 | 30 | 0 | 11 | 0 |
| `05_disaster` | 60 | 37 | 0 | 11 | 0 |
| `06_social` | 18 | 30 | 3 | 21 | 0 |

### By traffic profile

| TP | ok | valido_extremo | pendiente_revision | configuracion_sospechosa | error_probable |
|----|---:|---:|---:|---:|---:|
| `TP01` | 24 | 9 | 6 | 6 | 0 |
| `TP02` | 27 | 9 | 6 | 3 | 0 |
| `TP03` | 27 | 9 | 6 | 3 | 0 |
| `TP04` | 4 | 41 | 0 | 0 | 0 |
| `TP05` | 28 | 14 | 3 | 0 | 0 |
| `TP06` | 20 | 5 | 3 | 17 | 0 |
| `TP07` | 25 | 9 | 6 | 5 | 0 |
| `TP08` | 8 | 4 | 3 | 30 | 0 |
| `TP09` | 6 | 39 | 0 | 0 | 0 |
| `TP10` | 21 | 22 | 2 | 0 | 0 |
| `TP11` | 21 | 17 | 7 | 0 | 0 |
| `TP12` | 24 | 9 | 12 | 0 | 0 |

## Methodological answers

### 1. Is corpus_v1 sufficiently complete to use as a benchmark?

**Yes for configuration/diversity benchmarking** — all 540 `.settings`, manifest rows, feature matrices, output metrics, spatial metrics, and auxiliary CSVs align with corpus scope.

**Ready for routing protocol comparison** — **0** scenarios with `error_probable` (missing outputs, see CSV); message analysis window (policy B) is not yet enforced in the pipeline.

### 2. Which scenarios should be kept as valid extremes?

- **TP12** cross-group partition controls (`include_control`)
- **TP04 / TP05 / TP10** stress load and CriticalTTL tiers (`include_stress`)
- **R10 / R11** and disconnected bases with `ZERO_CONTACTS` (`include_control` / `document_as_extreme`)
- **MAP_UNDERUSED** WDM scenarios (~8–10% world grid coverage on roads — not a simulation failure)

Count `valido_extremo`: **187** scenarios.

### 3. Which scenarios need review before the paper?

- **0** scenarios with missing outputs → re-simulate
- **64** suspicious configs (zero delivery with contacts, etc.)
- **54** pending revision (P0/P1 map, worldSize, latency window)
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

1. No missing-output scenarios — corpus output metrics complete
2. Implement TTL-aware message window in `output_metrics` pipeline
3. Filter validation CSV when exporting paper tables (`validation_status == ok` for main tier)
4. Re-run after settings revision: `validate_corpus_benchmark.py`

## Artifacts

- Validation table: [`data/corpus_benchmark_validation.csv`](../data/corpus_benchmark_validation.csv)
- Diagnosis: [`data/scenario_diagnosis.csv`](../data/scenario_diagnosis.csv)
- TP validation: [`tp_validation_report.md`](tp_validation_report.md)
- Frozen diversity: [`RESULTADOS_ACTUALES.md`](RESULTADOS_ACTUALES.md)
