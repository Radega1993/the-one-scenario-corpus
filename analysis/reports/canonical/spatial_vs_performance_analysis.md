# Spatial occupancy vs routing performance (corpus_v1)

Generated: 2026-06-05 12:40 UTC

## Executive summary

- **Scenarios merged:** 540 (manifest + output_metrics + spatial_occupancy_metrics).
- **Pearson** `final_coverage_pct` vs `delivery_ratio` (all scenarios): **r = 0.1994** (n=540).
- **Pearson** `useful_time_ratio` vs `delivery_ratio`: **r = 0.0032** (n=396).
- **Interpretation:** Low *world* grid coverage on map-based mobility (WDM, MAP_UNDERUSED) does not imply simulation failure; it reflects roads vs rectangular world bounds.
- **Paper figure:** [`spatial_coverage_by_family_paper.png`](../figures/paper/supplementary/spatial_coverage_by_family_paper.png)

## Global correlation

| X | Y | r | n |
|---|---|--:|--:|
| final_coverage_pct | delivery_ratio | 0.1994 | 540 |
| useful_time_ratio | delivery_ratio | 0.0032 | 396 |

## Median by family

| Family | median coverage % | median delivery |
|--------|------------------:|----------------:|
| `03_vehicles` | 17.24 | 0.6274 |
| `04_rural` | 17.74 | 0.7613 |
| `01_urban` | 25.04 | 0.3325 |
| `05_disaster` | 45.08 | 0.8196 |
| `02_campus` | 55.52 | 0.8498 |
| `06_social` | 56.60 | 0.7709 |

## Low spatial coverage scenarios

Scenarios with `final_coverage_pct < 12%`: **48** (typical urban WDM / MAP_UNDERUSED).

Do not exclude these from the benchmark without documenting in Methods; stratify by `map_dataset` or family when comparing protocols.

## Relation to useful simulation time

`useful_time_ratio` measures contact activity duration; `final_coverage_pct` measures explored grid fraction. They are complementary — see [`useful_simulation_time_report.md`](useful_simulation_time_report.md) and [`message_analysis_window_policy.md`](message_analysis_window_policy.md).

## Regeneration

```bash
python3 scenarios/analysis/analyze_spatial_vs_performance.py
```
