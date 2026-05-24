# Evaluation metrics review (routing benchmark)

Generated: 2026-05-24 10:28 UTC

Source: `MessageStatsReport` (The ONE) → `output_metrics.csv`; indirect mobility from `ConnectivityONEReport`.

## Primary metrics (paper main tables)

| Metric | ONE source | Measures | Interpretation | Risks | Paper use |
|--------|------------|----------|----------------|-------|-------------|
| delivery_ratio | delivery_prob | Fraction created messages delivered | Higher = better reach | Saturated ~1 hides differentiation | Main comparison |
| latency_mean | latency_avg | Mean delivery delay (s) | Lower = faster | NaN if zero deliveries | Main comparison |
| overhead_ratio | overhead_ratio | Relay cost vs deliveries | Lower = efficient | Extreme if few deliveries | Main comparison |
| drop_ratio | derived | Drops / started | Loss under congestion | High on TP04/TP10 | Secondary |

## Secondary (MessageStatsReport fields)

| Metric | Field | Use |
|--------|-------|-----|
| created | created | Load generated |
| started | started | Forwarding attempts |
| relayed | relayed | Relay load |
| delivered | delivered | Absolute deliveries |
| hopcount_avg | hopcount_avg | Path length |
| response_prob | response_prob | Request-response (if used) |

## Diagnostic / mobility (not protocol outcomes)

| Metric | Source | Use |
|--------|--------|-----|
| total_encounters | ConnectivityONEReport | Mobility/connectivity |
| contact_time_per_min | indirect CSV | Activity density |
| coverage_world_ratio | SpatialOccupancyReport | Map usage |

## Minimum set for protocol comparison

1. delivery_ratio
2. latency_mean (only if delivery > 0)
3. overhead_ratio
4. drop_ratio
5. hopcount_avg (from report parsing extension)
6. total_encounters (context column)

## Open questions

- Add hopcount/buffertime to `output_metrics.csv` pipeline?
- Normalize latency by useful window vs full endTime?
