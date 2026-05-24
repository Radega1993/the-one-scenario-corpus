# Map realism review

Generated: 2026-05-20 11:40 UTC

- Bases using HelsinkiMedium: **168** / 60 unique bases in audit
- U2/U4 migrated to **Manhattan** (projected activity WKT) in corpus_v2 revision

## What real maps add

- Constrained movement on roads (MapBasedMovement, WDM)
- Realistic geographic extent and bottlenecks

## Limits of single-map reuse

- Urban/vehicle/disaster scenarios share Helsinki geometry → correlated spatial features
- Cannot claim geographic diversity without multiple maps

## Large worldSize + low coverage

| Case | Interpretation | Action |
|------|----------------|--------|
| WDM on full Helsinki grid, ~8–10% world coverage | Mobility explores roads, not empty world | Crop worldSize to roads bbox |
| RWP tiny range in huge world | Design bug | Reduce world or increase range |

## Recommendations

1. **Keep Helsinki** for WDM urban benchmark (after worldSize crop).
2. **Manhattan** for U2/U4 diversity (document projected WKT limitation).
3. **Campus/rural/social:** synthetic worlds without OSM — separate map realism from mobility realism.
4. **Paper:** separate "map-constrained" vs "synthetic arena" families in methods.
