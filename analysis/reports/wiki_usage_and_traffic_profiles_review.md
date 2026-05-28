# Wiki Usage and Traffic Profiles review

Generated: 2026-05-28 19:14 UTC

## Summary

- Created [`04-Usage.md`](../../.wiki-clone/04-Usage.md) — practical guide for simulations, batch runner, overlays, analysis, validation, dashboard.
- Created [`06-Traffic-Profiles.md`](../../.wiki-clone/06-Traffic-Profiles.md) — TP01–TP12 methodology with parameter table from generator + corpus spot-checks.
- Updated [`Home.md`](../../.wiki-clone/Home.md), [`03-Installation.md`](../../.wiki-clone/03-Installation.md), [`05-Scenario-Families.md`](../../.wiki-clone/05-Scenario-Families.md) links.
- Backup: `scenarios/.wiki-clone/_backup_before_usage_tp_pages_*`
- Flat wiki structure preserved (no 18-folder reorganization).

## Pages created or updated

| Page | Status | Notes |
|------|--------|-------|
| `04-Usage.md` | Created | Full mandatory H2 sections |
| `06-Traffic-Profiles.md` | Created | 12 TP blocks + summary/comparison tables |
| `Home.md` | Updated | Links to 04-Usage, 06-Traffic-Profiles |
| `03-Installation.md` | Updated | Related link to Usage |
| `05-Scenario-Families.md` | Updated | Links to Usage and Traffic Profiles |

## Commands documented

| Command group | Verified from script help | Notes |
|---------------|--------------------------:|-------|
| `run_all_scenarios.py` | yes | --help verified |
| `run_analysis.py` | yes | phases verified |
| `run_figures_aggregated.py` | partial | argparse read; --help needs matplotlib |
| `validate_traffic_profiles.py` | yes |  |
| `analyze_spatial_occupancy.py` | partial | argparse read; runtime needs pandas |
| `analyze_message_creation_times.py` | partial | argparse read |
| `audit_settings.py` | yes |  |
| `diagnose_scenarios.py` | partial | needs pandas for import |

## Traffic Profiles documented

| TP | Documented | Parameters extracted | Notes |
|----|:----------:|:--------------------:|-------|
| TP01 | yes | yes | Section in 06-Traffic-Profiles.md |
| TP02 | yes | yes | Section in 06-Traffic-Profiles.md |
| TP03 | yes | yes | Section in 06-Traffic-Profiles.md |
| TP04 | yes | yes | Section in 06-Traffic-Profiles.md |
| TP05 | yes | yes | Section in 06-Traffic-Profiles.md |
| TP06 | yes | yes | Section in 06-Traffic-Profiles.md |
| TP07 | yes | yes | Section in 06-Traffic-Profiles.md |
| TP08 | yes | yes | Section in 06-Traffic-Profiles.md |
| TP09 | yes | yes | Section in 06-Traffic-Profiles.md |
| TP10 | yes | yes | Section in 06-Traffic-Profiles.md |
| TP11 | yes | yes | Section in 06-Traffic-Profiles.md |
| TP12 | yes | yes | Section in 06-Traffic-Profiles.md |

## Broken links

Heuristic check on updated pages: **51** broken relative links.

Common intentional targets: `Reproducibility` in Home remains a forward reference (not created in this task).

## Missing files

- Report paths referenced under `scenarios/analysis/reports/validation/` and `canonical/` — verified present for TP validation and message policy.
- `diagnose_scenarios.py` documented only if needed; optional for Usage page (not primary).

## Legacy terms found

| Term | Count (updated pages) |
|------|----------------------:|
| corpus_v2 | 2 |
| HelsinkiMedium | 1 |

No active corpus_v2 or HelsinkiMedium-as-current-map language added to new pages.

## Recommendations before paper writing

1. Run full validation pipeline after any new simulation batch: `validate_traffic_profiles.py`, `run_analysis.py --phase output_metrics`.
2. Align message KPI windows with TP07 burst policy (`message_analysis_window_policy.md`).
3. Resolve `Reproducibility` wiki page or retarget Home link.
4. Install Python deps (`requirements.txt`) before running figure/validation scripts locally.

## CSV

Machine-readable: [`wiki_usage_and_traffic_profiles_review.csv`](../data/wiki_usage_and_traffic_profiles_review.csv)
