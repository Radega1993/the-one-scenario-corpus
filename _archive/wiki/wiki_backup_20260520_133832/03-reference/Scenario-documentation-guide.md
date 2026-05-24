# Scenario documentation guide

This guide defines the **standard, paper-ready structure** to document each scenario in the wiki, and where each section’s data should come from (settings vs analysis artefacts).

## What to document per scenario (recommended minimum)

Use the per-scenario template in `05-corpus/scenarios-en/Scenario-template.md`.

### 1) Overview (narrative)

- **Source:** the scenario intent (your design rationale).
- **Include:** what phenomenon it models, why it exists in the corpus, and what “lever(s)” it is designed to control (e.g., TTL, traffic rate, movement regime, map).

### 2) Scenario configuration (core 23)

- **Source (values):** `scenarios/analysis/data/features.csv` (raw/extracted values), using the **23-core list** from `scenarios/analysis/reports/RESULTADOS_ACTUALES.md`.
- **How:** copy the 23 core features for that scenario into the table; keep units consistent (m, s, bytes).
- **Why:** this table is the most compact, comparable “paper view” across all scenarios.

### 3) Mobility model (human description)

- **Source:** the `.settings` file, mainly `MovementModel.*` and `Group*.movementModel`, plus model-specific params.
- **Include:** map/world size, movement regime, heterogeneity (multiple groups), and the day rhythm (if WDM).

### 4) Traffic pattern (human + key settings)

- **Source:** the `.settings` file, mainly `Events.nrof`, `Events1.*`, optional `Events2.*`.
- **Include:** interval/rate, size distribution/range, sources/destinations pattern (uniform vs burst vs hub-target), and how many streams exist.

### 5) Distinguishing characteristics (bullets)

- **Source:** your intent + the “core 23” table.
- **Include:** 3–6 bullets describing what makes the scenario structurally different (not just parameter tweaks).

### 6) Correlation with other scenarios (core 23)

- **Source:** `scenarios/analysis/data/correlation_pearson_core23.csv` (or the summary in `scenarios/analysis/reports/correlation_core23_report.txt`).
- **Include:** top-3 most similar and top-3 most different scenarios (by smallest \(|r|\)).
- **Why:** this grounds the narrative in the diversity validation.

### 7) Cluster assignment

- **Source:** `scenarios/analysis/data/cluster_assignments_core23.csv` (Ward, k=7).
- **Include:** cluster id and a short interpretation (based on the cluster’s members).

### 8) PCA position (optional)

- **Source:** `scenarios/analysis/figures/` (PCA scatter) or a future exported table.
- **Include:** PC1/PC2 if you decide to “freeze” those coordinates for the paper.

### 9) Additional non-core parameters (optional but useful)

- **Source:** `.settings` fields that are important to interpret but not in core 23 (e.g., WDM details like `nrOfOffices`, `nrOfMeetingSpots`, heavy-tail params).
- **Rule:** only include parameters that change the scientific interpretation.

### 10) Simulation outputs (optional, when available)

- **Source:** `scenarios/analysis/data/output_metrics.csv`.
- **Include:** delivery ratio, mean latency, overhead ratio, drop ratio.
- **Note:** outputs are protocol- and run-dependent; keep them clearly labelled as “optional”.

## Bilingual documentation rule (EN/ES)

- **Keep section numbering identical** across EN and ES pages, so they are diffable and paper-export friendly.
- **Keep tables aligned** (same rows/order) for core 23 and outputs.
- **Translate narrative, not variable names:** keep feature names (`world_area`, `event_interval_mean`, etc.) unchanged.

## Consistency checklist (copy/paste)

- [ ] Scenario ID, name, family, and settings path are correct.
- [ ] Core-23 table matches `analysis/data/features.csv`.
- [ ] Correlation section cites core23 artefacts.
- [ ] Cluster id matches `cluster_assignments_core23.csv`.
- [ ] Outputs (if present) match `output_metrics.csv`.
