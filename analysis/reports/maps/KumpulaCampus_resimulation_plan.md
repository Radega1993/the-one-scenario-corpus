# KumpulaCampus — re-simulation plan

Generated: 2026-05-28T17:59:12

## Recommendation

- **Re-run campus simulations** if POI or shuttle WKT changed before publishing new KPIs.
- **C4 rename / C6 cleanup** change scenario names and settings structure only; mobility geometry unchanged — update external pipelines referencing `C4_Stadium_*`.

## Scope

- Affected settings files: **78** (6 base × 12 TP + variants).
- Traffic Profile blocks (`Events*`) not modified.

## Priority

1. C1, C4 (class change, event peaks)
2. C3 hackathon (24h)
3. C2, C5, C6 as needed
