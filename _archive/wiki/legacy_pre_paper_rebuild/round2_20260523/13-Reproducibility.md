# Reproducibility

**Status:** stable | **Updated:** 2026-05-20 11:41 UTC

## Purpose

How to reproduce analyses.

## Content

## Simulation

```bash
python3 scenarios/analysis/run_all_scenarios.py --corpus corpus_v2 \
  --extra-settings scenarios/analysis/diego17_reports_overrides.txt \
  --extra-settings scenarios/analysis/spatial_occupancy_reports_overrides.txt
```

## Analysis pipeline

```bash
PY=scenarios/analysis/.venv/bin/python
$PY scenarios/analysis/audit_settings.py --manifest scenarios/corpus_v2/manifest.csv
$PY scenarios/analysis/diagnose_scenarios.py --reports-dir reports
$PY scenarios/analysis/build_wiki_research_reports.py
```

See [README.md](../analysis/README.md) for full phase list.

## Data artifacts

Listed in [data_inventory.md](../analysis/reports/data_inventory.md)


## Internal links

[14-Paper-Freeze-Checklist](14-Paper-Freeze-Checklist)

## Open questions

Pin ONE commit hash in paper?

## Paper usage

Reproducibility appendix.
