# Clustering analysis

Purpose: summarize cluster-structure interpretation in the frozen baseline.

## Method

- Ward hierarchical clustering (`k=7`) on standardized descriptor space.
- Silhouette used as compact quality indicator.

## Current reading

- `full46` keeps moderate usable structure (`silhouette 0.2929`).
- `core23` keeps interpretability but with more moderate separation (`0.2681`) after optimization.

## Positioning

Clustering is interpreted jointly with correlation and distance metrics, not as a standalone acceptance criterion.
