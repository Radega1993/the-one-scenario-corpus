# Paper phase 1 action plan

Generated: 2026-05-24 10:28 UTC

## Closed decisions

- Corpus benchmark = **synthetic/semi-synthetic**, not empirical traces
- **corpus_v1**: 720 scenarios = 60 bases × 12 TP
- Traffic = Events overlay; mobility from v1 base per scenario
- Minimum routing metrics: delivery, latency, overhead, drops
- Wiki rebuilt paper-oriented; old wiki backed up to `_archive/wiki/wiki_backup_20260520_133832`

## Pending decisions

- [ ] Re-run full corpus after settings revision
- [ ] Complete spatial occupancy 720/720
- [ ] Add hopcount to output_metrics pipeline
- [ ] Freeze benchmark_split in main manifest

## Priority tasks

1. Re-simulate corpus_v1 with Diego17 + spatial reports
2. Re-run `diagnose_scenarios.py` and `build_corpus_v1_revision_plan.py`
3. Regenerate `output_metrics.csv` from new reports
4. Select **main** benchmark subset (~40 bases × TP01–08) from `manifest_revision.csv`
5. First protocol comparison (Epidemic vs Prophet vs …) on main split only

## Missing for paper

| Item | Status |
|------|--------|
| Protocol comparison tables | Not started |
| Spatial figures all families | Partial |
| Message window in metrics pipeline | Policy only |
| Statistical tests across protocols | Not started |

## Can write in Methods now

- Scenario families and TP design
- Synthetic traffic generation (MessageEventGenerator)
- Map-constrained vs synthetic mobility taxonomy
- Evaluation metrics definitions
- Reproducibility (scripts in `scenarios/analysis/`)

## Do not claim yet

- Final delivery rankings after revision until re-sim
- Geographic diversity beyond Helsinki+Manhattan
- Optimal corpus size without re-diagnosis

## Recommended execution order

1. Simulation batch (720)
2. `run_analysis.py --phase output_metrics indirects`
3. `analyze_spatial_occupancy.py` (full manifest)
4. `diagnose_scenarios.py` + research reports refresh
5. Protocol experiments on `benchmark_split=main`