# Corpus v3 design

## Goals

1. **~40–50 main benchmark bases** with diversified maps (not only HelsinkiMedium).
2. **Stress** subset (TP10, small buffers, critical TTL) clearly tagged.
3. **Diagnostic / extreme** (TP12 partition, ZERO_CONTACTS controls) separated.
4. Explicit separation: mobility (v1 base) / map profile / TP / protocol overlays.

## Proposed splits (from plan generator)

- Main-tagged base×TP rows: **387**
- Stress-tagged: **251**
- Diagnostic-tagged: **82**
- Unique bases in main split: **43**
- Unique bases in stress split: **58**

## Map profiles

See [`scenarios/maps/map_profiles.md`](../../maps/map_profiles.md) and `data/map_profile_plan.csv`.

## Actions

| Action | When |
|--------|------|
| `keep` | Base behaves; minor TP tuning only |
| `adjust` | TP differentiation or traffic parameters |
| `redesign_mobility` | >50% TP with non-structural ZERO_DELIVERY |
| `change_map` | Helsinki-only urban/vehicle/disaster with spatial P0/P1 |
| `stress_only` | Traffic family T* bases |
| `exclude_main` | Do not include in main benchmark (manual filter in v3 build) |

Implementation status: **proposal only** (`corpus_v3/` not populated).
