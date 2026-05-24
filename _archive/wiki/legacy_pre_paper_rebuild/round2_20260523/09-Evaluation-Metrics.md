# Evaluation metrics

**Status:** draft | **Updated:** 2026-05-20 11:41 UTC

## Purpose

Minimum metric set for routing comparison.

## Content

Full review: [evaluation_metrics_review.md](../analysis/reports/evaluation_metrics_review.md)

## Primary (protocol comparison)

| Metric | Source |
|--------|--------|
| delivery_ratio | MessageStatsReport |
| latency_mean | MessageStatsReport |
| overhead_ratio | MessageStatsReport |
| drop_ratio | derived |

## Secondary

hopcount_avg, created, started, relayed, delivered

## Diagnostic (context only)

total_encounters, spatial coverage, contact_time_per_min — **do not** rank protocols on these alone.


## Internal links

[10-Results-Summary](10-Results-Summary), [11-Protocol-Benchmarking-Plan](11-Protocol-Benchmarking-Plan)

## Open questions

Add hopcount to CSV export?

## Paper usage

Methods — metrics; Results tables.
