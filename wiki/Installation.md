# Installation

**English** | [Español](Installation-es)

---

Step-by-step setup to run the scenario corpus and analysis pipeline. See also [Quickstart](Quickstart) for the minimal commands.

---

## 1. Clone and build The ONE

1. **Clone The ONE** (if you don't have it yet):
   ```bash
   git clone https://github.com/akeranen/the-one.git
   cd the-one
   ```
2. **Compile:**
   ```bash
   chmod +x compile.sh
   ./compile.sh
   ```
3. Ensure **Java** (e.g. OpenJDK 11+) is installed: `java -version`.

---

## 2. Get the scenario corpus

**Option A — Corpus inside the ONE repo**

Clone or copy the `scenarios/` folder (corpus + analysis) into the ONE root, e.g.:

```
the-one/
├── one.sh
├── compile.sh
├── default_settings.txt
├── reports/
└── scenarios/          ← corpus_v1/, analysis/, wiki/, README, etc.
```

**Option B — Corpus as separate repo**

Clone the scenario corpus repo (e.g. `the-one-scenario-corpus`) alongside or elsewhere. When running scripts, use the full path to the corpus: `--corpus /path/to/the-one-scenario-corpus/corpus_v1` (or set `scenarios/` as current directory and use `--corpus corpus_v1` from the parent that contains it).

---

## 3. Python environment

1. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   # or: venv\Scripts\activate  # Windows
   ```
2. **Install dependencies:**
   ```bash
   pip install numpy pandas scipy matplotlib streamlit
   ```
   If the project has a `requirements.txt` at repo root or in `scenarios/`, use:
   ```bash
   pip install -r requirements.txt
   ```

---

## 4. Verify

- **Run one scenario** (from the ONE root):
  ```bash
  ./one.sh -b 1 scenarios/corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiMedium.settings
  ```
  Check that `reports/` (or the dir set in the .settings) contains output files.

- **Run one analysis phase** (from the repo root that contains `scenarios/`):
  ```bash
  python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase features
  ```
  Check that `scenarios/analysis/data/features.csv` and `scenario_list.txt` are created.

---

## See also

- [Quickstart](Quickstart) — Commands for all scenarios and pipeline
- [Reproducibility](Reproducibility) — Regenerating analysis from scratch
