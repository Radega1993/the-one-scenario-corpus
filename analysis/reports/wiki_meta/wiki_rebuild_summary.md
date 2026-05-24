# Wiki rebuild — executive summary

Generated: 2026-05-20 (UTC) · **Round2 update:** 2026-05-24

**Full round2 report:** [wiki_paper_rebuild_report.md](wiki_paper_rebuild_report.md) — backup 20260523, 18-page flat taxonomy, metrics 720, spatial 720/720, archived superseded pages in `round2_20260523/`.

## Backup (round2)

| Item | Value |
|------|-------|
| Status | **OK** |
| Path | `scenarios/_archive/wiki/wiki_backup_20260523_20260524_101911/` |
| Files | 242 markdown pages |
| Log | `BACKUP_INFO.md` in backup folder |

## Backup (initial rebuild 2026-05-20)

| Item | Value |
|------|-------|
| Status | **OK** |
| Path | `scenarios/_archive/wiki/wiki_backup_20260520_133832` |
| Files | 223 markdown pages |

## New wiki (round2 — current)

| Item | Value |
|------|-------|
| Path | `scenarios/.wiki-clone/` |
| Pages | 18 flat EN (Home + 01–14 + Glossary + References + CHANGELOG) |
| Key pages | `05-Feature-Space`, `06-Diversity-Validation`, `07-Output-Metrics`, `11-Message-Analysis-Window` |
| Superseded pages | `_legacy_pre_paper_rebuild/round2_20260523/` |

## New wiki (initial 2026-05-20)

| Item | Value |
|------|-------|
| Path | `scenarios/.wiki-clone/` |
| Pages | 18 (Home + 01–14 + References + CHANGELOG + Glossary) |
| Legacy | `_legacy_pre_paper_rebuild/` (v1 bilingual wiki) |

## Reports generated

| Report | Path |
|--------|------|
| Old wiki audit | `wiki_old_audit.md` |
| New index | `wiki_new_index.md` |
| Data inventory | `INVENTARIO.md` (repo map; `data_inventory.md` archived) |
| Current results | `current_results_review.md` |
| Evaluation metrics | `evaluation_metrics_review.md` |
| Message analysis window | `message_analysis_window_policy.md` |
| Simulation time policy | `simulation_time_policy.md` + `data/simulation_time_policy.csv` |
| Map realism | `map_realism_review.md` |
| Paper phase 1 plan | `paper_phase1_action_plan.md` |
| **Round2 rebuild report** | `wiki_paper_rebuild_report.md` |

Pre-existing reports integrated: `message_creation_time_audit.md`, `spatial_occupancy_report.md`, `corpus_v2_revision_*`.

## Methodological decisions documented

1. **Traces:** map-constrained real geometry + synthetic mobility + synthetic traffic + simulated contacts/deliveries (not empirical traces).
2. **Spatial occupancy:** grid coverage explains oversized worlds; separate from connectivity.
3. **Message timing:** not all at t=0; TP07 burst mid-sim; ~10% messages in last 10% sim for many TPs.
4. **Metrics:** delivery, latency, overhead, drops as primary; encounters/spatial as diagnostic.
5. **Analysis window:** recommended **TTL-aware + 5% warmup** (policy B).
6. **Simulation time:** 12 h default sufficient; prefer worldSize fix over extending time.

## Resolved vs pending

| Resolved in wiki | Still pending (data) |
|------------------|----------------------|
| Taxonomy real/synthetic | **Message analysis window** in pipeline (blocker) |
| TP01–TP12 documented | Protocol comparison experiments |
| Benchmark splits (manifest_revision) | Freeze manifest for paper |
| Spatial metrics **720/720** | Pin ONE commit / venv for paper |
| Output metrics **720/720** | Re-run diagnosis P0 scenarios |
| Diversity metrics in RESULTADOS_ACTUALES | Update paper figures if settings change |

## Next steps

1. Implement message analysis window (policy B) before protocol comparison.
2. Run protocol benchmarking on `benchmark_split=main`.
3. Freeze `manifest_revision.csv` into main manifest.
4. Re-run diagnosis; resolve P0 scenarios.
