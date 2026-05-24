# the-one-scenario-corpus — Wiki Home

**English** | [Español](Home-es)

---

## In 2 Minutes

This project provides a reproducible corpus for DTN/OppNets research in The ONE simulator, plus a full analysis pipeline and documentation stack for paper writing.

Current paper-ready status:

- **60 scenarios** across **7 families**
- Diversity analysis in **full-46** and **core-23** descriptor spaces
- Freeze declared as **final optimized baseline** (publishable, not optimal final corpus)

---

## Final Snapshot (official)

| Metric | Value |
|------|--------|
| full-46 max \|r\| | `0.9377` |
| full-46 pairs \|r\| >= 0.7 | `46/1770 (2.6%)` |
| full-46 min cosine | `0.0620` |
| full-46 silhouette (Ward k=7) | `0.2929` |
| core-23 max \|r\| | `0.9829` |
| core-23 pairs \|r\| >= 0.7 | `58/1770 (3.3%)` |
| core-23 silhouette (Ward k=7) | `0.2681` |
| feature-feature core | `mm_WDM <-> mm_Bus = 0.9393` |

Official frozen numbers are maintained in [Final-frozen-results](Final-frozen-results).

---

## Research Focus

- Build a scenario set that is broad enough to benchmark routing protocols without linear redundancy collapse.
- Keep a transparent methodology (features, NaN/normalization, correlation, clustering, ablation).
- Preserve traceability from scenario settings to analysis artifacts and conclusions.

---

## Quick Navigation

### Project Overview
- [Research-goals](Research-goals)
- [Thesis-phases](Thesis-phases)
- [Contributions](Contributions)
- [Repository-structure](Repository-structure)

### Corpus
- [Corpus-overview](Corpus-overview)
- [Scenario-families](Scenario-families)
- [Corpus-versioning](Corpus-versioning)
- [Dropped-scenarios-evolution](Dropped-scenarios-evolution)
- [Scenario-catalog](Scenario-catalog)

### Methodology
- [Scenario-representation](Scenario-representation)
- [Core-vs-extended-features](Core-vs-extended-features)
- [Feature-selection-rationale](Feature-selection-rationale)
- [NaN-and-normalization-policy](NaN-and-normalization-policy)
- [Diversity-analysis-methodology](Diversity-analysis-methodology)
- [Marginal-test](Marginal-test)
- [Ablation-methodology](Ablation-methodology)
- [Methodological-limitations](Methodological-limitations)

### Results
- [Results-overview](Results-overview)
- [Final-frozen-results](Final-frozen-results)
- [Optimization-history](Optimization-history)
- [Feature-feature-analysis](Feature-feature-analysis)
- [Clustering-analysis](Clustering-analysis)
- [Output-space-analysis](Output-space-analysis)
- [Figures](Figures)

### Reproducibility
- [Quickstart](Quickstart)
- [Running-analysis-pipeline](Running-analysis-pipeline)
- [Generating-figures](Generating-figures)
- [Using-corpus-in-the-one](Using-corpus-in-the-one)
- [Data-and-artifacts](Data-and-artifacts)

