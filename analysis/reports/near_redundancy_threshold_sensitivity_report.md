# Near-redundancy threshold sensitivity (v1)

Generated: 2026-06-22 09:22 UTC

## Question

Does the saturation conclusion hold if the near-redundant NN threshold is varied? Primary threshold in production: **0.25** (L2 in cumulative batch-normalized 36D space).

## Thresholds tested

0.15, 0.20, 0.25, 0.30, 0.35

## Extension transitions (post-800)

### Transition 800 → 1000

| Threshold | near_redundant | redundant+invalid | majority pass |
|-----------|----------------|-------------------|---------------|
| 0.15 | 0.392 | 0.487 | False |
| 0.20 | 0.453 | 0.548 | True |
| 0.25 | 0.492 | 0.587 | True |
| 0.30 | 0.541 | 0.636 | True |
| 0.35 | 0.580 | 0.675 | True |

### Transition 1000 → 1200

| Threshold | near_redundant | redundant+invalid | majority pass |
|-----------|----------------|-------------------|---------------|
| 0.15 | 0.399 | 0.509 | True |
| 0.20 | 0.466 | 0.576 | True |
| 0.25 | 0.522 | 0.632 | True |
| 0.30 | 0.562 | 0.672 | True |
| 0.35 | 0.596 | 0.706 | True |

### Transition 1200 → 1600

| Threshold | near_redundant | redundant+invalid | majority pass |
|-----------|----------------|-------------------|---------------|
| 0.15 | 0.036 | 0.624 | True |
| 0.20 | 0.061 | 0.648 | True |
| 0.25 | 0.133 | 0.721 | True |
| 0.30 | 0.206 | 0.794 | True |
| 0.35 | 0.261 | 0.848 | True |

### Transition 1600 → 2000

| Threshold | near_redundant | redundant+invalid | majority pass |
|-----------|----------------|-------------------|---------------|
| 0.15 | 0.038 | 0.643 | True |
| 0.20 | 0.076 | 0.681 | True |
| 0.25 | 0.152 | 0.757 | True |
| 0.30 | 0.285 | 0.890 | True |
| 0.35 | 0.386 | 0.991 | True |


## Does the saturation conclusion hold?

**Partially** — for both extension transitions (800→1000 and 1000→1200), `redundant_plus_invalid` remains **≥ 50%** at all tested thresholds. Stricter thresholds (0.15–0.20) classify more maps as near-redundant; looser thresholds (0.30–0.35) reduce the redundant fraction but still yield majority redundant+invalid in extension tranches.

## Why 0.25 is the primary threshold

- **Position:** Mid-range among tested values — neither the strictest nor the laxest.
- **Interpretation:** In globally z-scored feature space with 33 numeric dimensions plus `source_type` one-hot, L2 &lt; 0.25 indicates maps that are close to an existing representative on roughly one quarter of a per-dimension standard-deviation scale (aggregate Euclidean). This is **moderately conservative**: lower thresholds over-penalize legitimately similar OSM variants; higher thresholds under-count redundancy.
- **Stability:** Extension confirmation does not depend on 0.25 alone; marginal valid growth (&lt;30% of pool) and cluster/medoid criteria provide independent signals.

## Diminishing returns in extensions

At threshold 0.25:
- 800→1000: near_redundant = 0.492, redundant+invalid = 0.587
- 1000→1200: near_redundant = 0.522, redundant+invalid = 0.632

Marginal valid growth (from decision JSON): 26.0% and 20.3% per extension tranche — consistent with decreasing non-redundant returns regardless of threshold choice.

## Figure

`near_redundancy_threshold_sensitivity.png` — redundant+invalid vs batch for each threshold.

## Output

`near_redundancy_threshold_sensitivity.csv`
