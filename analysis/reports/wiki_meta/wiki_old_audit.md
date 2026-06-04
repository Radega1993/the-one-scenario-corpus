# Audit of previous wiki (pre-rebuild)

Generated: 2026-05-24 10:28 UTC

Backup location: `/home/raul/Documents/the-one/scenarios/_archive/wiki/wiki_backup_20260520_133832`

- Total markdown pages scanned: **242**
- English-primary pages (excl. `*-es.md`): **130**
- Spanish duplicate pages (`*-es.md`): **111**

## Inventory by folder

| Folder | Pages |
|--------|------:|
| `(root)` | 19 |
| `_legacy_pre_paper_rebuild` | 223 |

## Pages to migrate (update for corpus_v1)

- `03-reference/Methodological-limitations.md` — rewrite, do not copy verbatim
- `03-reference/Methodology.md` — rewrite, do not copy verbatim
- `02-guide/Reproducibility.md` — rewrite, do not copy verbatim
- `03-reference/Extraction-formulas.md` — rewrite, do not copy verbatim
- `03-reference/NaN-and-normalization-policy.md` — rewrite, do not copy verbatim

## Obsolete for paper (archive only)

- 01-home/Home.md (60-scenario freeze, corpus_v1)
- 04-results/Final-frozen-results.md
- 04-results/Diversity-status.md
- 05-corpus/Corpus-overview.md (v1 only)
- 05-corpus/scenarios-en/* (per-scenario v1 catalog)

## Duplicate / bilingual overhead

- **223** files are all `.md`; ~half are `*-es.md` mirrors of English pages.
- New wiki: **English-first** at repository root; Spanish optional later.

## Incomplete relative to thesis/paper needs

- No TP01-TP12 traffic profile methodology
- No spatial occupancy / grid metrics
- No protocol routing benchmark plan
- No message analysis window policy
- No corpus_v1 revision / manifest_revision

## Proposed new structure

See [wiki_new_index.md](wiki_new_index.md).

## Sample of old page paths (first 30)

```
01-Research-Goal.md
02-Corpus-Overview.md
03-Scenario-Families.md
04-Traffic-Profiles.md
05-Mobility-and-Maps.md
06-Spatial-Occupancy.md
07-Simulation-Time-and-Warmup.md
08-Message-Generation-and-Analysis-Window.md
09-Evaluation-Metrics.md
10-Results-Summary.md
11-Protocol-Benchmarking-Plan.md
12-Limitations-and-Threats-to-Validity.md
13-Reproducibility.md
14-Paper-Freeze-Checklist.md
CHANGELOG.md
Glossary.md
Home.md
References.md
_legacy_pre_paper_rebuild/01-home/Contributions.md
_legacy_pre_paper_rebuild/01-home/Home.md
_legacy_pre_paper_rebuild/01-home/Repository-structure.md
_legacy_pre_paper_rebuild/01-home/Research-goals.md
_legacy_pre_paper_rebuild/01-home/Thesis-phases.md
_legacy_pre_paper_rebuild/02-guide/Data-and-artifacts.md
_legacy_pre_paper_rebuild/02-guide/Generating-figures.md
_legacy_pre_paper_rebuild/02-guide/Installation.md
_legacy_pre_paper_rebuild/02-guide/Quickstart.md
_legacy_pre_paper_rebuild/02-guide/Reproducibility.md
_legacy_pre_paper_rebuild/02-guide/Running-analysis-pipeline.md
_legacy_pre_paper_rebuild/02-guide/Using-corpus-in-the-one.md
...
```