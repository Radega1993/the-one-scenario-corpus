# Scenario representation

Purpose: define how a `.settings` scenario becomes an analysis unit.

Related artifacts: `analysis/data/features.csv`, `analysis/data/features_normalized.csv`.

## Representation pipeline

1. Parse each `.settings` file.
2. Extract a fixed descriptor vector (full-46 features).
3. Build reduced analysis spaces (`core23`, `reduced17`).
4. Normalize per feature (NaN-aware policy).
5. Compare scenarios in descriptor space and output space.

## Why this matters

It decouples scenario analysis from narrative labels and enables reproducible quantitative diversity checks.
