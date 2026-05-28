# Wiki paper rebuild report (round2)

Generated: 2026-05-24 UTC

## Backup

| Item | Value |
|------|-------|
| Status | **OK** |
| Path | `scenarios/_archive/wiki/wiki_backup_20260523_20260524_101911/` |
| Markdown files | 242 |
| Log | `BACKUP_INFO.md` in backup folder |
| Previous backup | `wiki_backup_20260520_133832` (223 pages) |

Pre-rebuild snapshot taken before round2 restructure (flat 18-page taxonomy, corpus_v1 720 metrics).

---

## Pages created (new filenames)

| Page | Role |
|------|------|
| `05-Feature-Space.md` | 46 extended / 23 core features, NaN policy |
| `06-Diversity-Validation.md` | Frozen diversity metrics (720), ablation, feature–feature |
| `07-Output-Metrics.md` | Routing benchmark metrics, output_metrics.csv |
| `09-Message-Creation-Time.md` | Temporal message creation per TP |
| `11-Message-Analysis-Window.md` | TTL-aware analysis window (policy B); **pending implementation** |

---

## Pages modified (rewritten)

| Page | Changes |
|------|---------|
| `Home.md` | New wiki map, corpus_v1 720, synthetic/semi-synthetic disclaimers, canonical links |
| `01-Research-Goal.md` | Links to 12-Benchmark; template unified |
| `02-Corpus-Overview.md` | v1/v2/dropped; no corpus_v3; manifest + revision |
| `03-Scenario-Families.md` | 7 families, 84 scenarios for 01_urban |
| `04-Traffic-Profiles.md` | TP as experimental factors |
| `08-Spatial-Occupancy.md` | Renumbered from 06; **720/720** spatial metrics |
| `10-Simulation-Time-Policy.md` | Renumbered from 07; warmup 5% |
| `12-Benchmark-Protocol-Comparison.md` | Renumbered from 11; blocked until window closed |
| `13-Dashboard-and-Reproducibility.md` | Merged reproducibility + dashboard + SCRIPTS_INDEX |
| `14-Paper-Freeze-Checklist.md` | Updated checkboxes (output/spatial 720 ✓) |
| `Glossary.md` | Expanded terms (synthetic, censored_late, spatial ≠ connectivity) |
| `References.md` | Updated paths |
| `CHANGELOG.md` | Entry 2026-05-24 round2 restructure |
| `README.md` | Points to new structure and backup |

---

## Pages archived

Moved to `.wiki-clone/_legacy_pre_paper_rebuild/round2_20260523/`:

- `05-Mobility-and-Maps.md` (content integrated into Home, 02, 05, 08, Glossary)
- `06-Spatial-Occupancy.md` (superseded by `08-Spatial-Occupancy.md`)
- `07-Simulation-Time-and-Warmup.md` (superseded by `10-Simulation-Time-Policy.md`)
- `08-Message-Generation-and-Analysis-Window.md` (split into 09 + 11)
- `09-Evaluation-Metrics.md` (merged into `07-Output-Metrics.md`)
- `10-Results-Summary.md` (merged into 06 + 07)
- `11-Protocol-Benchmarking-Plan.md` (superseded by `12-Benchmark-Protocol-Comparison.md`)
- `12-Limitations-and-Threats-to-Validity.md` (themes distributed across Home, 02, 04, 08, 11, 12, Glossary)
- `13-Reproducibility.md` (merged into `13-Dashboard-and-Reproducibility.md`)

Legacy v1 bilingual wiki remains in `_legacy_pre_paper_rebuild/` (01-home … 05-corpus).

---

## Inconsistencies found and resolved

| Issue | Before | After |
|-------|--------|-------|
| Spatial coverage count | ~99/720 in old `06-Spatial-Occupancy.md` | **720/720** in `08-Spatial-Occupancy.md` |
| Broken link | `data_inventory.md` (archived) | `INVENTARIO.md`, `SCRIPTS_INDEX.md` |
| Diversity metrics | Absent or v1 (60 scenarios) in legacy | `RESULTADOS_ACTUALES.md` metrics in `06-Diversity-Validation.md` |
| Wiki structure | 19 pages with mixed naming | 18 flat pages per paper taxonomy |
| Freeze checklist | All items unchecked / outdated | output + spatial 720 marked done |
| TP justification doc | `internal/16-traffic_profiles_v1_justification.md` not found | Cited `corpus_v1/README.md` + tp_validation_report |
| Message window | Documented but not flagged as blocker | Explicit **pending** on 11, 12, 14 |

---

## Methodological messages documented

- Traces are **synthetic/semi-synthetic** (real map geometry; simulated mobility and messages)
- Traffic profiles are **experimental factors**
- Spatial occupancy **≠** connectivity
- Routing outputs serve **benchmark comparison**, not empirical realism
- **Message analysis window not closed** — protocol comparison blocked until implemented

---

## Scripts used

```bash
scenarios/analysis/.venv/bin/python scenarios/analysis/build_wiki_research_reports.py
scenarios/analysis/.venv/bin/python scenarios/analysis/populate_wiki_paper.py
```

Source of truth for page content: `scenarios/analysis/populate_wiki_paper.py`.

---

## Round 3 alignment (2026-05-24)

| Page | Change |
|------|--------|
| `11-Message-Analysis-Window.md` | Aligned with canonical `message_analysis_window_policy.md` (full-window primary; no Policy B draft) |
| `12-Benchmark-Protocol-Comparison.md` | Links to `protocol_benchmark_kpi_policy.md` + definitions CSV |
| `14-Paper-Freeze-Checklist.md` | Points to formal `paper_freeze_checklist.md` |
| `_legacy_pre_paper_rebuild/` | Moved to `_archive/wiki/legacy_pre_paper_rebuild/` |

New analysis deliverables: `protocol_benchmark_kpi_policy.md`, `spatial_vs_performance_analysis.md`.

---

## Next steps before paper

1. **Optional:** implement message window filter in `output_metrics` code; primary policy is full-window (documented).
2. Run protocol comparison experiments on `benchmark_split=main` (TP01–TP08, viable bases).
3. Re-run diagnosis; resolve or exclude P0 scenarios.
4. Freeze `manifest_revision.csv` into main manifest.
5. Review TP05 msgTtl mismatches on U4/U6 (documented as intentional).
6. Update paper figures/tables if metrics change after any settings revision.
7. Pin ONE commit hash and venv/requirements in reproducibility section.

---

## Related reports

- [wiki_rebuild_summary.md](wiki_rebuild_summary.md) — executive summary (2026-05-20 + round2 pointer)
- [wiki_new_index.md](wiki_new_index.md) — page index (regenerated by build script)
- [wiki_old_audit.md](wiki_old_audit.md) — legacy wiki audit
