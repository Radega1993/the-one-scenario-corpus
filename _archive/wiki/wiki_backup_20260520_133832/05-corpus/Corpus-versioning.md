# Corpus versioning

Purpose: explain how the corpus evolved and what is the official frozen set.

## Current official version

- **`corpus_v1`** is the official, frozen set used for the paper baseline.
- It contains **60 scenarios** across 7 families.

## Evolution logic

- Initial corpus generation focused on broad thematic coverage.
- Iterative diversification rounds reduced high pairwise redundancy.
- Final freeze keeps a practical trade-off: publishable baseline with declared limitations.

## Versioning rule

If future revisions modify scenario content or composition, they should be published under a new corpus label (for example `corpus_v2`) while preserving `corpus_v1` for reproducibility.
