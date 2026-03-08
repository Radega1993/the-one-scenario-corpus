# Wiki content — the-one-scenario-corpus

This folder contains **Markdown pages** for the project's **GitHub Wiki**, in **English and Spanish**.

---

## How to publish to GitHub Wiki

### Option 1: Clone the wiki repo and copy files

1. Clone the wiki (GitHub creates it when you open the Wiki tab):
   ```bash
   git clone https://github.com/Radega1993/the-one-scenario-corpus.wiki.git
   cd the-one-scenario-corpus.wiki
   ```
2. Copy the `.md` files from this `wiki/` folder into the wiki repo. In GitHub Wiki:
   - **Home** is the page that shows by default — rename or create `Home.md` as the main page.
   - Other pages: create a file named like `Quickstart.md`, `Methodology.md`, etc. (spaces in the name become `-` in the URL, e.g. `Results-overview.md` → "Results-overview").
3. Commit and push:
   ```bash
   git add .
   git commit -m "Add wiki pages (EN+ES)"
   git push origin master
   ```

### Option 2: Create pages manually in the GitHub web interface

1. In the repo, open the **Wiki** tab.
2. Create a new page for each file (e.g. "Home", "Quickstart", "Methodology", "Results-overview", "Corpus-overview", "Diversity-status", "Analysis-pipeline-reference", "Scenario-catalog").
3. For Spanish versions, create pages with suffix `-es` (e.g. "Home-es", "Quickstart-es") and paste the content from the corresponding `*-es.md` files.

### Option 3: Use a script to sync

You can write a small script that copies `wiki/*.md` into the cloned wiki repo and renames if needed (e.g. `Home.md` → `Home.md` for wiki home). Then run it before pushing.

---

## Page list (EN + ES)

| English (main) | Spanish |
|----------------|--------|
| Home | Home-es |
| Quickstart | Quickstart-es |
| Installation | Installation-es |
| Reproducibility | Reproducibility-es |
| Methodology | Methodology-es |
| Results-overview | Results-overview-es |
| Figures | Figures-es |
| Corpus-overview | Corpus-overview-es |
| Diversity-status | Diversity-status-es |
| Analysis-pipeline-reference | Analysis-pipeline-reference-es |
| Scenario-catalog | Scenario-catalog-es |
| Directory-structure | Directory-structure-es |
| Roadmap | Roadmap-es |

---

## Setting the wiki home page

In GitHub Wiki, the **Home** page is the one named **Home**. So:

- Copy `Home.md` to the wiki repo as `Home.md` (it will become the main page).
- Copy `Home-es.md` as `Home-es.md` so the Spanish version is at "Home-es".

---

## Links between pages

Links in the markdown use names like `[Quickstart](Quickstart)` or `[Results overview](Results-overview)`. In GitHub Wiki, page names are the file names without `.md`. So:

- `Quickstart.md` → page "Quickstart", link `[Quickstart](Quickstart)`
- `Results-overview.md` → page "Results-overview", link `[Results overview](Results-overview)`

Internal links should work as-is. Links to the main repo (e.g. README, ROADMAP) use full GitHub URLs.

---

## Adding family and scenario pages later

- **Family pages:** Create e.g. `Urban-scenarios.md`, `Campus-scenarios.md`, … (and `-es` versions) with a table of scenarios and short descriptions. Linked from [Corpus-overview](Corpus-overview).
- **Scenario catalog:** The page [Scenario-catalog](Scenario-catalog) is an index; you can add subpages per scenario (e.g. `U1-CBD-Commuting`) over time.
