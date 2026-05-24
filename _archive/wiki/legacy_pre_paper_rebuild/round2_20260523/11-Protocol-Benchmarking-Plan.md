# Protocol benchmarking plan

**Status:** draft | **Updated:** 2026-05-20 11:41 UTC

## Purpose

How to compare routing protocols fairly.

## Content

1. **Subset:** `benchmark_split=main` in `manifest_revision.csv` (TP01–TP08, viable bases).
2. **Fixed settings:** same mobility, map, TP; only `Group.router` changes.
3. **Metrics:** primary four from [09-Evaluation-Metrics](09-Evaluation-Metrics).
4. **Window:** TTL-aware message filter (see [08-Message-Generation](08-Message-Generation-and-Analysis-Window)).
5. **Runs:** N seeds or confidence intervals if time permits.

**Stress tier** (TP10, TP04, 07_traffic): report separately, not mixed with main claims.

**Control tier** (TP12): validate partition behavior, not delivery ranking.


## Internal links

[09-Evaluation-Metrics](09-Evaluation-Metrics), [14-Paper-Freeze-Checklist](14-Paper-Freeze-Checklist)

## Open questions

Which protocols first?

## Paper usage

Methods — protocol comparison; Results.
