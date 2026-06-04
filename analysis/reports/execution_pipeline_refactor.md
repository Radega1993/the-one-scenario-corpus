# Execution Pipeline Refactor

**Date:** 2026-05-26
**Scope:** Benchmark-aware execution modes for `run_all_scenarios.py`

---

## 1. Summary

The simulation runner (`run_all_scenarios.py`) has been extended with benchmark-tier awareness, runtime estimation, and reproducibility metadata. All existing CLI arguments continue to work identically.

## 2. New CLI Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--benchmark {core,stress,all}` | choice | None | Filter scenarios using `benchmark_definition.csv` |
| `--exclude-deprecated` | flag | False | Exclude scenarios marked deprecated |
| `--estimate-runtime` | flag | False | Print estimated total simulation time and exit |
| `--reproducibility-log PATH` | path | `reports/reproducibility_metadata.json` | Where to write reproducibility metadata JSON |

## 3. Benchmark Tier Definitions

Tiers are defined in `analysis/data/benchmark_definition.csv`:

| Tier | Filter | Scenarios | Description |
|------|--------|-----------|-------------|
| `core` | `included_in_core == TRUE` | 540 | Environmental families (01-06) x 12 TP |
| `stress` | `included_in_stress == TRUE` | 30 | Stress/control family (07) x TP01 + TP10 |
| `all` | `core OR stress` | 540 | All active scenarios |

Deprecated scenarios (150 archived TP combinations) are excluded when `--benchmark` is used or `--exclude-deprecated` is set.

## 4. Argument Composition

New arguments compose with existing filters via AND logic:

1. `--benchmark` selects a base set from `benchmark_definition.csv`
2. `--family`, `--tp`, `--scenario-base`, `--name-regex` narrow further
3. `--exclude-deprecated` removes deprecated scenarios

Example: `--benchmark core --family 01_urban --tp TP01` selects only the 7 urban TP01 scenarios from the core benchmark.

## 5. Runtime Estimation

`--estimate-runtime` reads `Scenario.endTime` from `manifest.csv` for each selected scenario, sums the total simulated time, and prints:
- Number of selected scenarios
- Total simulated seconds/hours
- Estimated wall-clock time at 1x speed (single worker)
- Estimated wall-clock time with `--jobs N` parallelism

No simulations are executed when this flag is set.

## 6. Reproducibility Metadata

After each batch run, a JSON file is written with:

```json
{
  "timestamp": "2026-05-26T05:30:00+00:00",
  "command_line": ["scenarios/analysis/run_all_scenarios.py", "--benchmark", "core"],
  "python_version": "3.12.x",
  "java_version": "openjdk version 17.0.x",
  "one_version": "v1.6.0 (2014-01-01)",
  "git_hash": "abc123...",
  "benchmark_tier": "core",
  "scenarios_run": 540,
  "ok": 540,
  "fail": 0,
  "elapsed_seconds": 3600.5,
  "jobs": 4,
  "filters": { ... }
}
```

This enables exact reproduction of any batch run.

## 7. Menu Integration

`analysis_menu.py` option 1 ("Run all scenarios") now offers a benchmark tier selector:
- `0` = no filter (entire corpus, legacy behavior)
- `1` = core (540 environmental)
- `2` = stress (30 stress/control)
- `3` = all active (540)

A runtime estimation prompt is also available before execution.

## 8. Backwards Compatibility

All changes are additive:
- No `--benchmark` = no filtering (runs everything in the corpus directory, exactly as before)
- `--exclude-deprecated` defaults to False when `--benchmark` is not used
- `--estimate-runtime` is opt-in
- Reproducibility metadata is written silently without affecting simulation behavior
- All existing `--family`, `--tp`, `--settings`, `--select-file`, `--gui`, `--jobs`, `--timeout`, `--dry-run`, `--name-regex`, `--scenario-base`, `--extra-settings` work identically

## 9. Implementation Files

| File | Action |
|------|--------|
| `analysis/lib/benchmark_select.py` | Created: benchmark tier selection + endtime loading |
| `analysis/run_all_scenarios.py` | Modified: new args, benchmark filter, estimate, metadata |
| `analysis/analysis_menu.py` | Modified: benchmark tier prompt in option 1 |