# Corpus overview

**Status:** needs validation | **Updated:** 2026-05-20 11:41 UTC

## Purpose

Describe corpus versions and scale.

## Content

| Version | Scenarios | Description |
|---------|----------:|-------------|
| corpus_v1 | 60 | Base mobility/settings per use case |
| corpus_v2 | **720** | v1 mobility + **12 traffic profiles** (TP01–TP12) |

**Manifest:** `scenarios/corpus_v2/manifest.csv`  
**Revision sidecar:** `manifest_revision.csv` (`benchmark_split`: main / stress / control)

**Generator:** `generate_corpus_v2_traffic.py` overlays Events* and msgTtl on v1 mobility without changing movement models.

See [corpus_v2_revision_changelog.md](../analysis/reports/corpus_v2_revision_changelog.md) for in-place settings changes (worldSize, TP04 sizes, Manhattan U2/U4).


## Internal links

[03-Scenario-Families](03-Scenario-Families), [04-Traffic-Profiles](04-Traffic-Profiles)

## Open questions

Freeze manifest after re-sim?

## Paper usage

Methods — experimental setup.
