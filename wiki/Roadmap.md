# Roadmap

**English** | [Español](Roadmap-es)

---

Project roadmap: documentation, wiki, and diversity criteria. Full version in the repo: **[ROADMAP.md](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/ROADMAP.md)** (English), **[ROADMAP.es.md](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/ROADMAP.es.md)** (Spanish).

---

## Current state

- **corpus_v1**: 70 scenarios. Steps 4.1 (clustering), 4.2 (diversification) and 4.3 (~10 radical scenarios) are **done**.
- **Next priority**: Bilingual documentation (section 1) and wiki (section 2).

---

## 1. Documentation (EN/ES)

- README and analysis/README in English; Spanish in `.es.md`.
- Optional: .settings guide and code comments in English.

---

## 2. GitHub Wiki

- Home, Quickstart, Methodology, Results, Corpus overview, scenario families, scenario catalog.
- Optional: auto-generation of per-scenario wiki pages from corpus + features.

---

## 3. Corpus diversity: criteria and goals

- **|r| < 0.7** for ≥95% of pairs (or 100%).
- **Min cosine distance > 0.05**; no pair with cos_dist < 0.05.
- **Silhouette > 0.3** if clustering is used.
- Goals: max |r| < 0.85; pairs with |r| ≥ 0.7 **< 3%**; min cos_dist > 0.05.

---

## 4. Scenario plan (completed)

- **4.1** Cluster (Ward) — Done  
- **4.2** Diversify (scenarios_to_diversify.txt) — Done  
- **4.3** Add ~10 radical scenarios — Done  

After changes: run `run_analysis.py --corpus corpus_v1 --phase all` to refresh metrics.

---

## Wiki maintenance

- Keep Home and Quickstart in sync with the repo.
- Update Results and Diversity status when re-running analysis.
- Add or expand scenario catalog and family pages as needed.
