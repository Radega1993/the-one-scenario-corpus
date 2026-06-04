# Wiki final structure review

Generated: 2026-05-28 17:46 UTC

## Summary

- Reorganized `scenarios/.wiki-clone/` into **18 numbered sections** plus `Home.md`.
- Active wiki documents **current corpus only** (no legacy map/corpus callouts in section pages).
- Map assets: **7/7** PNG under `assets/maps/`.
- Corpus counts documented: **45** base + **540** corpus_v1 + **30** stress = **540** settings files.

## Final tree (active markdown)

```
Home.md
01-research-goal-and-scope/README.md
02-benchmark-methodology/README.md
03-installation/README.md
04-repository-structure/README.md
05-maps-and-map-generation/README.md
06-scenario-families/01-urban.md
06-scenario-families/02-campus.md
06-scenario-families/03-vehicles.md
06-scenario-families/04-rural.md
06-scenario-families/05-disaster.md
06-scenario-families/06-social.md
06-scenario-families/07-stress-scenarios.md
06-scenario-families/README.md
07-traffic-profiles/README.md
08-running-simulations/README.md
09-protocol-benchmarking/README.md
10-output-metrics-and-kpis/README.md
11-message-analysis-window-policy/README.md
12-spatial-occupancy-and-useful-simulation-time/README.md
13-corpus-diversity-validation/README.md
14-figures-and-tables/README.md
15-reproducibility-checklist/README.md
16-known-limitations/README.md
17-references/README.md
18-changelog-freeze-status/README.md
```

## Page status

| # | Section | Path | Exists | Complete | Notes |
|---|---------|------|--------|----------|-------|
| 1 | Research goal and scope | `01-research-goal-and-scope/README.md` | yes | yes | brief |
| 2 | Benchmark methodology | `02-benchmark-methodology/README.md` | yes | yes | brief |
| 3 | Installation | `03-installation/README.md` | yes | yes | migrated |
| 4 | Repository structure | `04-repository-structure/README.md` | yes | yes | brief |
| 5 | Maps and map generation | `05-maps-and-map-generation/README.md` | yes | yes | migrated |
| 6 | Scenario families | `06-scenario-families/README.md` | yes | yes | migrated |
| 7 | Traffic profiles | `07-traffic-profiles/README.md` | yes | yes | full |
| 8 | Running simulations | `08-running-simulations/README.md` | yes | yes | full |
| 9 | Protocol benchmarking | `09-protocol-benchmarking/README.md` | yes | yes | index |
| 10 | Output metrics and KPIs | `10-output-metrics-and-kpis/README.md` | yes | yes | index |
| 11 | Message analysis window policy | `11-message-analysis-window-policy/README.md` | yes | yes | index |
| 12 | Spatial occupancy and useful sim time | `12-spatial-occupancy-and-useful-simulation-time/README.md` | yes | yes | index |
| 13 | Corpus diversity validation | `13-corpus-diversity-validation/README.md` | yes | yes | index |
| 14 | Figures and tables | `14-figures-and-tables/README.md` | yes | yes | index |
| 15 | Reproducibility checklist | `15-reproducibility-checklist/README.md` | yes | yes | index |
| 16 | Known limitations | `16-known-limitations/README.md` | yes | yes | index |
| 17 | References | `17-references/README.md` | yes | yes | migrated |
| 18 | Changelog and freeze status | `18-changelog-freeze-status/README.md` | yes | yes | index |

## Legacy term audit (active wiki only)

Patterns: `corpus_v2`, `HelsinkiMedium`, `720`, `seven environmental`, `07_traffic`, `traffic stress family`.

- **Total matches in active pages:** 0 (cleaned 2026-05-28; TTL values use `7200` minutes, not the `720` scenario count).

## Broken links (heuristic)

- **Broken link checks (section READMEs):** 13
- Placeholder targets like `Usage`, `Traffic-Profiles` removed from migrated pages where found.

## TODOs

- Regenerate `paper_freeze_checklist.md` via `build_paper_freeze_checklist.py` if missing.
- > TODO: verify after final analysis run — any KPI not regenerated after new simulation batch.

## CSV

Machine-readable status: `scenarios/analysis/data/wiki_final_structure_review.csv`