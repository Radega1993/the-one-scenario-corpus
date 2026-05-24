# Wiki content — the-one-scenario-corpus

This folder (`.wiki-clone`) contains **Markdown pages** for the project's **GitHub Wiki**, in **English and Spanish**. The structure below makes it easy to find the file you need.

---

## Structure (where to find what)

| Folder | Content | Files (EN + ES) |
|--------|---------|------------------|
| **01-home** | Entry point, overview, key results | Home, Home-es |
| **02-guide** | How to run and reproduce | Quickstart, Installation, Reproducibility, Running-analysis-pipeline, Generating-figures, Using-corpus-in-the-one, Data-and-artifacts |
| **03-reference** | Methodology and feature/resource reference | Methodology, Scenario-representation, Core-vs-extended-features, Feature-selection-rationale, NaN-and-normalization-policy, Diversity-analysis-methodology, Marginal-test, Ablation-methodology, Methodological-limitations, Features-reference, Core-features, Extended-features, Full-feature-registry, Extraction-formulas, Analysis-pipeline-reference |
| **04-results** | Correlation, diversity, figures | Results-overview, Final-frozen-results, Optimization-history, Feature-feature-analysis, Clustering-analysis, Output-space-analysis, Diversity-status, Figures |
| **05-corpus** | Corpus design, scenario index, and family pages | Corpus-overview, Scenario-families, Corpus-versioning, Dropped-scenarios-evolution, Directory-structure, Scenario-catalog, Scenario-details, Urban/Campus/Vehicle/Rural/Disaster/Social/Traffic-scenarios |

Each topic has an English (e.g. `Home.md`) and a Spanish (e.g. `Home-es.md`) file.

---

## Quick file list

- **Home / estado del benchmark:** `01-home/Home.md`, `01-home/Home-es.md`
- **Resultados y diversidad:** `04-results/Results-overview.md`, `04-results/Diversity-status.md` (+ `-es`)
- **Referencia de features (46):** `03-reference/Features-reference.md` (+ `-es`)
- **Metodología:** `03-reference/Methodology.md` (+ `-es`)
- **Guía rápida / instalación:** `02-guide/Quickstart.md`, `02-guide/Installation.md` (+ `-es`)
- **Reproducibilidad y ejecución:** `02-guide/Running-analysis-pipeline.md`, `Generating-figures.md`, `Using-corpus-in-the-one.md`, `Data-and-artifacts.md` (+ `-es`)
- **Catálogo y detalle de escenarios:** `05-corpus/Scenario-catalog.md`, `05-corpus/Scenario-details.md`, `05-corpus/*-scenarios.md` (60 escenarios, páginas por familia) (+ `-es`)

---

## How to publish to GitHub Wiki

GitHub Wiki uses a flat structure: all pages are `.md` files in the root. Links use the page name (e.g. `[Quickstart](Quickstart)`, `[U1](U1_CBD_Commuting_HelsinkiMedium)`).

1. **Clone the wiki repo** (if you use a separate wiki repo):
   ```bash
   git clone https://github.com/USER/REPO.wiki.git
   cd REPO.wiki
   ```
2. **Copy all content.** Run from the wiki repo root (adjust `WIKI_ROOT` to the path of `.wiki-clone`):
   ```bash
   WIKI_ROOT=../scenarios/.wiki-clone   # adjust path as needed

   # Top-level pages (flatten)
   for d in 01-home 02-guide 03-reference 04-results 05-corpus; do
     cp $WIKI_ROOT/$d/*.md . 2>/dev/null
   done

   # Scenario pages (flatten to root)
   find $WIKI_ROOT/05-corpus/scenarios-en -name "*.md" -exec cp {} . \;
   find $WIKI_ROOT/05-corpus/scenarios-es -name "*.md" -exec cp {} . \;
   ```
3. **Set the wiki Home:** In GitHub Wiki settings, the default page is "Home" — so `Home.md` is the main page.
4. Commit and push the wiki.

Internal links use flat page names (e.g. `[U1](U1_CBD_Commuting_HelsinkiMedium)`). The publish script flattens scenario pages to the wiki root so these links work.

---

## Page list (EN + ES)

| English | Spanish | Folder |
|---------|---------|--------|
| Home | Home-es | 01-home |
| Quickstart | Quickstart-es | 02-guide |
| Installation | Installation-es | 02-guide |
| Reproducibility | Reproducibility-es | 02-guide |
| Running-analysis-pipeline | Running-analysis-pipeline-es | 02-guide |
| Generating-figures | Generating-figures-es | 02-guide |
| Using-corpus-in-the-one | Using-corpus-in-the-one-es | 02-guide |
| Data-and-artifacts | Data-and-artifacts-es | 02-guide |
| Methodology | Methodology-es | 03-reference |
| Scenario-representation | Scenario-representation-es | 03-reference |
| Core-vs-extended-features | Core-vs-extended-features-es | 03-reference |
| Feature-selection-rationale | Feature-selection-rationale-es | 03-reference |
| NaN-and-normalization-policy | NaN-and-normalization-policy-es | 03-reference |
| Diversity-analysis-methodology | Diversity-analysis-methodology-es | 03-reference |
| Marginal-test | Marginal-test-es | 03-reference |
| Ablation-methodology | Ablation-methodology-es | 03-reference |
| Methodological-limitations | Methodological-limitations-es | 03-reference |
| Features-reference | Features-reference-es | 03-reference |
| Core-features | Core-features-es | 03-reference |
| Extended-features | Extended-features-es | 03-reference |
| Full-feature-registry | Full-feature-registry-es | 03-reference |
| Extraction-formulas | Extraction-formulas-es | 03-reference |
| Analysis-pipeline-reference | Analysis-pipeline-reference-es | 03-reference |
| Results-overview | Results-overview-es | 04-results |
| Final-frozen-results | Final-frozen-results-es | 04-results |
| Optimization-history | Optimization-history-es | 04-results |
| Feature-feature-analysis | Feature-feature-analysis-es | 04-results |
| Clustering-analysis | Clustering-analysis-es | 04-results |
| Output-space-analysis | Output-space-analysis-es | 04-results |
| Diversity-status | Diversity-status-es | 04-results |
| Figures | Figures-es | 04-results |
| Corpus-overview | Corpus-overview-es | 05-corpus |
| Scenario-families | Scenario-families-es | 05-corpus |
| Corpus-versioning | Corpus-versioning-es | 05-corpus |
| Dropped-scenarios-evolution | Dropped-scenarios-evolution-es | 05-corpus |
| Directory-structure | Directory-structure-es | 05-corpus |
| Scenario-catalog | Scenario-catalog-es | 05-corpus |
| Scenario-details | Scenario-details-es | 05-corpus |
| Urban-scenarios | Urban-scenarios-es | 05-corpus |
| Campus-scenarios | Campus-scenarios-es | 05-corpus |
| Vehicle-scenarios | Vehicle-scenarios-es | 05-corpus |
| Rural-scenarios | Rural-scenarios-es | 05-corpus |
| Disaster-scenarios | Disaster-scenarios-es | 05-corpus |
| Social-scenarios | Social-scenarios-es | 05-corpus |
| Traffic-scenarios | Traffic-scenarios-es | 05-corpus |
