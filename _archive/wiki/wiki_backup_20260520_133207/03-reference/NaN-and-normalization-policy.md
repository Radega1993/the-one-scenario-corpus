# NaN and normalization policy

Purpose: document the preprocessing policy used by the analysis pipeline.

## NaN policy

- NaN indicates **structural non-applicability**, not random missingness.
- Typical cases: conditional descriptors (for example WDM-specific fields outside WDM scenarios).

## Normalization policy

1. Compute mean/std per feature using non-NaN values.
2. Apply z-score on valid entries.
3. Replace remaining NaN with `0` in standardized space.

This is a methodological decision to keep scenarios comparable in a common geometry.
