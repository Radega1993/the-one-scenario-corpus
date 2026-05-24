# Simulation time and warmup

**Status:** draft | **Updated:** 2026-05-20 11:41 UTC

## Purpose

Define useful simulation duration.

## Content

Default `Scenario.endTime = 43200` s (12 h).

**Useful time** (from connectivity): see `useful_simulation_time_metrics.csv` — most scenarios show activity until near end.

**Policy** ([simulation_time_policy.md](../analysis/reports/simulation_time_policy.md)):
- Warmup: first **5%** of endTime excluded from message outcome metrics
- Analysis cutoff: **90%** of endTime for delivery/latency aggregates
- Extend endTime only after fixing mobility (not for oversized worlds)

CSV: `data/simulation_time_policy.csv`


## Internal links

[08-Message-Generation-and-Analysis-Window](08-Message-Generation-and-Analysis-Window)

## Open questions

Per-family warmup overrides?

## Paper usage

Methods — simulation duration.
