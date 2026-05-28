# Diversity metric interpretation (paper, EN)

| Metric | What it measures | How computed here | Interpretation for this corpus |
|---|---|---|---|
| Pearson \|r\| (scenario–scenario) | Linear similarity of standardized feature vectors | Correlation between rows of `features_*` after z-score | High \|r\| ⇒ redundant scenario configuration |
| Spearman \|r\| | Rank-order similarity | Spearman on standardized vectors | Robustness check vs Pearson |
| Cosine distance | Angular separation in feature space | `1 - cos_sim` between scenario vectors | Low distance ⇒ near-collinear scenarios |
| Euclidean distance | Magnitude-aware separation | L2 distance between scenario vectors | Complements cosine for scale effects |
| Ward clustering (k=7) | Unsupervised grouping in feature space | Hierarchical clustering on standardized vectors | Stratification / structure check |
| Silhouette | Cluster cohesion vs separation | From cosine distance matrix + Ward labels | Higher ⇒ better-separated clusters |
| Ablation 17/23/46 | Feature-set trade-off | Same metrics on reduced/core/full spaces | Core-23 balances interpretability and separation |

**Canonical scope:** `corpus_v1` only — **540** scenarios. `stress_controls` (30) are documented separately.
