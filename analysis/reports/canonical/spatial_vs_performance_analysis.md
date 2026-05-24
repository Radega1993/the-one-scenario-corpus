# Spatial occupancy vs routing performance (corpus_v2)

Generated: 2026-05-24 12:02 UTC

## Executive summary

- **Scenarios merged:** 720 (manifest + output_metrics + spatial_occupancy_metrics).
- **Pearson** `final_coverage_pct` vs `delivery_ratio` (all scenarios): **r = -0.1338** (n=718).
- **Pearson** `useful_time_ratio` vs `delivery_ratio`: **r = -0.0019** (n=718).
- **Interpretation:** Low *world* grid coverage on map-based mobility (WDM, MAP_UNDERUSED) does not imply simulation failure; it reflects roads vs rectangular world bounds.
- **Paper figure:** [`spatial_coverage_by_family_paper.png`](../figures/paper/supplementary/spatial_coverage_by_family_paper.png)

## Global correlation

| X | Y | r | n |
|---|---|--:|--:|
| final_coverage_pct | delivery_ratio | -0.1338 | 718 |
| useful_time_ratio | delivery_ratio | -0.0019 | 718 |

## Median by family

| Family | median coverage % | median delivery |
|--------|------------------:|----------------:|
| `03_vehicles` | 3.60 | 0.4051 |
| `01_urban` | 7.96 | 0.2993 |
| `04_rural` | 71.92 | 0.03425 |
| `05_disaster` | 85.68 | 0.09135 |
| `07_traffic` | 92.00 | 0.03415 |
| `06_social` | 92.04 | 0.13 |
| `02_campus` | 93.16 | 0.6472 |

## Low spatial coverage scenarios

Scenarios with `final_coverage_pct < 12%`: **211** (typical urban WDM / MAP_UNDERUSED).

Do not exclude these from the benchmark without documenting in Methods; stratify by `map_dataset` or family when comparing protocols.

## Relation to useful simulation time

`useful_time_ratio` measures contact activity duration; `final_coverage_pct` measures explored grid fraction. They are complementary — see [`useful_simulation_time_report.md`](useful_simulation_time_report.md) and [`message_analysis_window_policy.md`](message_analysis_window_policy.md).

## Regeneration

```bash
python3 scenarios/analysis/analyze_spatial_vs_performance.py
```
