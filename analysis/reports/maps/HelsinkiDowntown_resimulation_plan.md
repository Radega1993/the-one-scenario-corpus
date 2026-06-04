# HelsinkiDowntown — re-simulation plan

Generated: 2026-05-28T17:49:25

## Recommendation

**Re-run urban simulations** after POI and bus WKT updates before publishing new KPIs.

- Affected scenario settings: **91** (7 base × 12 TP + variants).
- U2 rename changes `Scenario.name` only; geometry unchanged but external pipelines may need path updates.

## Not in scope

- Traffic Profile blocks (`Events*`) unchanged.
- No automatic simulation launch in this task.

## Priority order

1. U1, U4 (CBD / congestion) — primary bus route sensitivity
2. U2 SparseUrban — density lever
3. U3–U7 as needed for paper tables