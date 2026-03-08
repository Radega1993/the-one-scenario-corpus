# Methodology

**English** | [Español](Methodology-es)

---

This section describes how the corpus is **designed** and **evaluated**: scenario design, feature extraction, normalization, correlation, distance metrics, clustering, output-based analysis, and diversity criteria.

---

## Scenario design methodology

- **One scenario** = one `.settings` file. Each file defines a full ONE simulation: movement model, groups, interfaces, message events, reports, etc.
- **Design goal:** Cover different **families** (urban, campus, vehicles, rural, disaster, social, traffic) so that routing protocols are tested on varied mobility, traffic, and resource regimes.
- **Diversity goal:** Scenarios should not be **linearly redundant** (high correlation in feature space). We diversify by changing structure (map, mobility regime, resources), not only single parameters.
- **Versioning:** The corpus is named **corpus_v1** so future versions (e.g. corpus_v2) can coexist; scripts take `--corpus corpus_v1`.

---

## Feature extraction

- Each `.settings` file is **parsed** and converted into a **feature vector** of fixed length.
- Features are **stable** (reproducible from the file) and **reportable** (suitable for papers).
- **Groups of features:**
  1. **Mobility / space:** world size (Wx, Wy), number of nodes (N), density, speed mean, pause ratio, wait mean, movement-model one-hot (WDM, RWP, MapRoute, Cluster, Bus, ShortestPath, External).
  2. **Contact:** transmit range, contact-rate proxy (density × range² × speed).
  3. **Traffic:** event interval mean, event size mean, msgTtl, traffic pattern (uniform / burst / hub_target), number of event generators.
  4. **Resources:** buffer size, transmit speed.
  5. **WDM (WorkingDayMovement):** workDayLength, timeDiffSTD, probGoShoppingAfterWork, nrOfMeetingSpots, nrOfOffices (when applicable).

- **Current count:** 33 features per scenario. The exact list is in `scenarios/analysis/` (see [Analysis pipeline reference](Analysis-pipeline-reference) or repo README).

---

## Normalization

- After extraction, the feature matrix **X** (one row per scenario, one column per feature) is **z-score normalized** per feature:
  - \( Z_{s,j} = (X_{s,j} - \mu_j) / \sigma_j \)
- If a feature has zero variance, it is set to 0.
- **Output:** `features_normalized.csv` and `normalization_params.csv` (means and standard deviations). Correlation and distance are computed on **Z**.

---

## Correlation analysis

- **Correlation between scenarios** = correlation between their **feature vectors** (rows of Z).
- For each pair of scenarios (i, k): **Pearson** r(Z_i, Z_k) and **Spearman** (rank correlation).
- **Threshold:** We aim for **|r| < 0.7** for at least 95% of pairs (or 100% with `--strict`). High |r| means the two scenarios are linearly similar in parameter space.
- **Multiple comparisons:** We have m = n(n−1)/2 pairs. For each pair we test H₀: ρ = 0. We apply **FDR (Benjamini–Hochberg)** and **Bonferroni** to control false discoveries. The goal is to show that no pair has both high |r| and statistical significance after correction.

---

## Distance metrics

- **Cosine distance:** 1 − cos_sim(Z_i, Z_k). Measures **angle** between vectors (0 = identical direction, 2 = opposite).
- **Euclidean distance:** ||Z_i − Z_k||. Measures **magnitude** difference.
- **Diversity criterion:** Minimum cosine distance **> 0.05**; **no pair** with cos_dist < 0.05 (no almost-identical scenarios).

---

## Clustering

- **Method:** Ward (hierarchical) on the normalised feature matrix Z.
- **Output:** `cluster_assignments.csv` (scenario → cluster), `clustering_report.txt`.
- **Use:** Identify clusters of similar scenarios; choose representatives; diversify the rest (see “scenarios to diversify”).

---

## Output-based analysis

- **Outputs** = ONE result metrics per scenario: delivery ratio, latency mean, overhead ratio, drop ratio (from MessageStatsReport).
- We build a **vector per scenario** from these metrics, normalise, and compute **Pearson/Spearman and distances** between output vectors. This checks redundancy in **behaviour** (delivery, latency, etc.), not only in **parameters**.

---

## Diversity criteria (summary)

| Criterion | Target |
|-----------|--------|
| **Pearson \|r\|** | < 0.7 for ≥95% of pairs (or 100%) |
| **Cosine distance (min)** | > 0.05 |
| **Pairs with cos_dist < 0.05** | 0 |
| **Silhouette (optional)** | > 0.3 for clustering quality |

**“Scenario to diversify”:** A scenario that appears in many high-|r| pairs or in a dense cluster; we modify its `.settings` (speed, waitTime, transmitRange, workDayLength, TTL, buffer, etc.) to move it away in feature space. The list is in `analysis/reports/scenarios_to_diversify.txt`.

---

## See also

- [Results overview](Results-overview) — Current numbers and figures  
- [Corpus overview](Corpus-overview) — Families and design  
- [Analysis pipeline reference](Analysis-pipeline-reference) — Phases and artefacts  
