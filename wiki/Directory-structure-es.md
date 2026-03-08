# Estructura de directorios

**Español** | [English](Directory-structure)

---

Referencia: organización de la carpeta **scenarios** y dónde están el corpus, datos de análisis, figuras e informes. Detalle completo: [STRUCTURE.md](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/STRUCTURE.md) en el repo.

---

## Árbol (resumen)

```
scenarios/
├── README.md, README.es.md, ROADMAP.md, ROADMAP.es.md, .gitignore
├── STRUCTURE.md, WIKI_CHECKLIST.md, WIKI_CHECKLIST.es.md
├── wiki/                    ← Fuente de la wiki (Home, Quickstart, Methodology, …)
├── corpus_v1/               ← 70 escenarios .settings por familia
│   ├── 01_urban/     (12)
│   ├── 02_campus/    (8)
│   ├── 03_vehicles/  (8)
│   ├── 04_rural/     (12)
│   ├── 05_disaster/  (9)
│   ├── 06_social/    (6)
│   └── 07_traffic/   (15)
└── analysis/
    ├── run_analysis.py, run_all_scenarios.py, dashboard.py
    ├── README.md, README.es.md
    ├── data/          ← CSV: features, normalizado, correlación, distancias, output_metrics
    ├── figures/       ← heatmaps, histogramas, scatter (PNG/PDF)
    └── reports/       ← Informes .txt y notas .md
```

---

## Descripción en una línea por directorio

| Directorio | Descripción |
|------------|-------------|
| **scenarios/** | Raíz del proyecto: README, ROADMAP, STRUCTURE, fuente wiki, corpus_v1, analysis. |
| **corpus_v1/** | 70 ficheros `.settings` en 7 subcarpetas por familia (01_urban … 07_traffic). |
| **corpus_v1/01_urban … 07_traffic** | Una carpeta por familia con los .settings de esa familia. |
| **analysis/** | Scripts del pipeline (run_analysis.py, run_all_scenarios.py, dashboard.py) y documentación. |
| **analysis/data/** | CSV y listas generados: features, normalizado, matrices de correlación, distancias, clusters, output_metrics. |
| **analysis/figures/** | Gráficos generados: heatmaps Pearson/Spearman, histogramas, scatter PCA, par max-r. |
| **analysis/reports/** | Informes de texto (correlation_report.txt, clustering_report.txt, etc.) y notas (.md). |
| **wiki/** | Código fuente en Markdown de las páginas de la wiki de GitHub (EN + ES). |

---

## Ver también

- [STRUCTURE.md en el repo](https://github.com/Radega1993/the-one-scenario-corpus/blob/main/STRUCTURE.md) — Descripción completa de directorios y ficheros
- [Quickstart](Quickstart-es) — Dónde ejecutar comandos y dónde se escriben las salidas
- [Reproducibilidad](Reproducibility-es) — Regenerar data/ y figures/
