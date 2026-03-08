# Directory structure

**English** | [Español](Directory-structure-es)

---

Reference: layout of the **scenarios** folder. Full detail: [STRUCTURE.md](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/STRUCTURE.md) in the repo.

---

## Tree (summary)

```
scenarios/
├── README.md, README.es.md, ROADMAP.md, ROADMAP.es.md, .gitignore
├── STRUCTURE.md, WIKI_CHECKLIST.md, wiki/
├── corpus_v1/               (70 scenario .settings)
│   ├── 01_urban/     (12)  02_campus/ (8)  03_vehicles/ (8)
│   ├── 04_rural/     (12)  05_disaster/ (9)  06_social/ (6)  07_traffic/ (15)
└── analysis/
    ├── run_analysis.py, run_all_scenarios.py, dashboard.py
    ├── README.md, README.es.md
    ├── data/          CSV: features, correlation, distance, output_metrics
    ├── figures/       heatmaps, histograms, scatter (PNG/PDF)
    └── reports/       .txt reports and .md notes
```

---

## One-line description per directory

- **scenarios/** — Project root: README, ROADMAP, STRUCTURE, wiki source, corpus_v1, analysis.
- **corpus_v1/** — 70 `.settings` files in 7 family subfolders (01_urban … 07_traffic).
- **analysis/** — Pipeline scripts and docs.
- **analysis/data/** — Generated CSV: features, normalized, correlation matrices, distances, output_metrics.
- **analysis/figures/** — Generated plots: heatmaps, histograms, PCA scatter.
- **analysis/reports/** — Text reports and notes (.md).
- **wiki/** — Markdown source for GitHub Wiki (EN + ES).

---

## See also

- [STRUCTURE.md in repo](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/STRUCTURE.md)
- [Quickstart](Quickstart) — Where to run commands
- [Reproducibility](Reproducibility) — Regenerating data/ and figures/
