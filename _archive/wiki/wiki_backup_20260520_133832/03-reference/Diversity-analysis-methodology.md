# Diversity analysis methodology

Purpose: define how scenario diversity is evaluated.

## Core metrics

- Pearson correlation (scenario vectors in standardized space).
- Spearman correlation (rank-based robustness).
- Cosine distance (angular separation in descriptor space).
- Ward clustering (`k=7`) and silhouette for structural cohesion/separation.

## Principle

Diversity is not assessed with a single metric; results are interpreted jointly across correlation, geometry, and clustering.
