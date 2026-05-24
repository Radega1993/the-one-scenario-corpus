# Message generation and analysis window

**Status:** draft | **Updated:** 2026-05-20 11:41 UTC

## Purpose

When messages are created and which to analyze.

## Content

**Messages are NOT all injected at t=0.** First creation ≥ `interval_min` after sim start (see [message_creation_time_audit.md](../analysis/reports/message_creation_time_audit.md)).

| TP | Temporal behavior |
|----|-------------------|
| TP01–TP06, TP08–TP12 | Spread across simulation (~median 50% endTime) |
| TP07 | Burst window ~20–28% endTime |
| TP02 | Often latest creations near end (long intervals) |

## Recommended policy

**B: TTL-aware window + 5% warmup** ([message_analysis_window_policy.md](../analysis/reports/message_analysis_window_policy.md))

```
valid message m iff 0.05*endTime <= t_create(m) <= endTime - msgTtl
```

Late messages in last 10%: label **censored_late**, exclude from latency comparison.


## Internal links

[09-Evaluation-Metrics](09-Evaluation-Metrics), [07-Simulation-Time-and-Warmup](07-Simulation-Time-and-Warmup)

## Open questions

Implement window in output_metrics pipeline?

## Paper usage

Methods — traffic and metric window.
