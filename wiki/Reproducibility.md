# Reproducibility

**English** | [Español](Reproducibility-es)

---

How to **regenerate** the analysis from scratch and where generated artefacts live. See [Quickstart](Quickstart) for the command list.

---

## Regenerating all analysis from scratch

Run from the **repository root** (parent of `scenarios/`). Order:

1. **Features** — `run_analysis.py --corpus corpus_v1 --phase features`
2. **Normalize** — `run_analysis.py --phase normalize`
3. **Correlation** — `run_analysis.py --phase correlation`
4. **Figures** — `run_analysis.py --phase figures`
5. **Output metrics** — `run_analysis.py --phase output_metrics` (needs ONE report files; use `--reports-dir` if needed)
6. **Outputs** — `run_analysis.py --phase outputs` (needs output_metrics.csv)

**Single command** for 1–5: `run_analysis.py --corpus corpus_v1 --phase all`. Then `--phase outputs` separately if you have output_metrics.csv.

---

## Regenerating only figures

If you already have normalized features and correlation matrices:

`run_analysis.py --phase figures`

Output: `scenarios/analysis/figures/` (PNG and PDF).

---

## Where generated artefacts are

- **scenarios/analysis/data/** — features.csv, features_normalized.csv, normalization_params.csv, correlation_*.csv, distance_*.csv, cluster_assignments.csv, output_metrics.csv, *_outputs.csv
- **scenarios/analysis/figures/** — heatmap_*, histogram_*, scatter_* (PNG/PDF)
- **scenarios/analysis/reports/** — correlation_report.txt, multiple_comparisons_report.txt, clustering_report.txt, scenarios_to_diversify.txt, outputs_correlation_report.txt, observaciones_correlacion.md, plan_radical_scenarios.md

ONE report files go to the directory set in each .settings (often `reports/` at ONE root).

---

## Reproducibility of ONE runs

Each scenario can use a fixed seed (e.g. MovementModel.rngSeed). Same .settings and ONE version give the same movement and events. The analysis pipeline is deterministic for the same corpus and code.

---

## See also

- [Quickstart](Quickstart) — All commands
- [Installation](Installation) — Initial setup
- [Analysis pipeline reference](Analysis-pipeline-reference) — Phases and artefacts
