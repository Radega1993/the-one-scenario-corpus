# Spatial occupancy vs routing performance (corpus_v1)

Generated: 2026-05-27 13:55 UTC

## Executive summary

- **Scenarios merged:** 536 (manifest + output_metrics + spatial_occupancy_metrics).
- **Pearson** `final_coverage_pct` vs `delivery_ratio` (all scenarios): **r = 0.4187** (n=361).
- **Pearson** `useful_time_ratio` vs `delivery_ratio`: **r = -0.1964** (n=361).
- **Interpretation:** Low *world* grid coverage on map-based mobility (WDM, MAP_UNDERUSED) does not imply simulation failure; it reflects roads vs rectangular world bounds.
- **Paper figure:** [`spatial_coverage_by_family_paper.png`](../figures/paper/supplementary/spatial_coverage_by_family_paper.png)

## Global correlation

| X | Y | r | n |
|---|---|--:|--:|
| final_coverage_pct | delivery_ratio | 0.4187 | 361 |
| useful_time_ratio | delivery_ratio | -0.1964 | 361 |

## Median by family

| Family | median coverage % | median delivery |
|--------|------------------:|----------------:|
| `04_rural` | 73.40 | 0.733 |
| `05_disaster` | 85.78 | 0.5659 |
| `06_social` | 89.08 | 0.6292 |
| `02_campus` | 93.16 | 0.8498 |
| `01_urban` | nan | 0.374 |
| `03_vehicles` | nan | 0.7585 |

## Low spatial coverage scenarios

Scenarios with `final_coverage_pct < 12%`: **59** (typical urban WDM / MAP_UNDERUSED).

Do not exclude these from the benchmark without documenting in Methods; stratify by `map_dataset` or family when comparing protocols.

## Relation to useful simulation time

`useful_time_ratio` measures contact activity duration; `final_coverage_pct` measures explored grid fraction. They are complementary — see [`useful_simulation_time_report.md`](useful_simulation_time_report.md) and [`message_analysis_window_policy.md`](message_analysis_window_policy.md).

## Regeneration

```bash
python3 scenarios/analysis/analyze_spatial_vs_performance.py
```