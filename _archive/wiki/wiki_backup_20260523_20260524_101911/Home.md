# The ONE Scenario Corpus — Wiki

**Status:** draft | **Updated:** 2026-05-20 11:41 UTC

## Purpose

Entry point for reviewers and thesis readers.

## Content

This project provides a **controlled synthetic / semi-synthetic benchmark** for DTN and opportunistic routing in [The ONE Simulator](https://github.com/understandable-machine-intelligence-lab/one).

**This corpus is not an empirical mobility trace.** It combines:
- **Real map geometry** (HelsinkiMedium, Manhattan WKT),
- **Synthetic mobility** (WorkingDayMovement, RWP, ClusterMovement, …),
- **Synthetic traffic** (MessageEventGenerator, TP01–TP12),
- **Simulated contacts and protocol outcomes** (EpidemicRouter by default in baseline runs).

## Current status

| Item | Value |
|------|-------|
| Active corpus | `corpus_v2` — **720** scenarios (60 bases × 12 TP) |
| Analysis pipeline | `scenarios/analysis/` |
| Wiki backup | `wiki_backup_20260520_133832/` |
| Metrics validity | **Re-simulation required** after corpus_v2 settings revision |

## Wiki map

| Section | Page |
|---------|------|
| Goal | [01-Research-Goal](01-Research-Goal) |
| Corpus | [02-Corpus-Overview](02-Corpus-Overview), [03-Scenario-Families](03-Scenario-Families), [04-Traffic-Profiles](04-Traffic-Profiles) |
| Mobility & maps | [05-Mobility-and-Maps](05-Mobility-and-Maps) |
| Spatial | [06-Spatial-Occupancy](06-Spatial-Occupancy) |
| Time | [07-Simulation-Time-and-Warmup](07-Simulation-Time-and-Warmup), [08-Message-Generation-and-Analysis-Window](08-Message-Generation-and-Analysis-Window) |
| Metrics | [09-Evaluation-Metrics](09-Evaluation-Metrics), [10-Results-Summary](10-Results-Summary) |
| Protocols | [11-Protocol-Benchmarking-Plan](11-Protocol-Benchmarking-Plan) |
| Validity | [12-Limitations-and-Threats-to-Validity](12-Limitations-and-Threats-to-Validity) |
| Repro | [13-Reproducibility](13-Reproducibility) |
| Freeze | [14-Paper-Freeze-Checklist](14-Paper-Freeze-Checklist) |

## Analysis reports (repo)

- [`scenarios/analysis/reports/`](../analysis/reports/) — machine-generated reviews
- [`data_inventory.md`](../analysis/reports/data_inventory.md)


## Internal links

All numbered pages; [References](References)

## Open questions

Confirm post-revision simulation complete.

## Paper usage

Abstract, Introduction, Methods overview.
