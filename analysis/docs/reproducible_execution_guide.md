# Reproducible Execution Guide

How to run simulations, regenerate outputs, and validate reproducibility for the corpus_v1 benchmark.

---

## Prerequisites

- Java JDK 11+ installed (`java -version`)
- The ONE compiled (`./compile.sh` from repo root)
- Python 3.10+ with dependencies in `scenarios/analysis/.venv/`

## 1. Run the Core Benchmark (540 environmental scenarios)

```bash
# Dry-run first to verify selection
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --benchmark core --dry-run

# Estimate wall-clock time
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --benchmark core --estimate-runtime --jobs 4

# Execute with 4 parallel workers
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --benchmark core --jobs 4 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt
```

## 2. Run the Stress Benchmark (30 stress/control scenarios)

```bash
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --benchmark stress --jobs 4 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt
```

## 3. Run All Active Scenarios (570 = core + stress)

```bash
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --benchmark all --jobs 4 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt
```

## 4. Run a Specific Family or Traffic Profile

```bash
# Only urban scenarios with TP01
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --benchmark core --family 01_urban --tp TP01

# Rural + Disaster families, all TPs
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --benchmark core --family 04_rural --family 05_disaster

# Single scenario in GUI mode
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --gui \
  --settings scenarios/corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiDowntown__TP01_Baseline.settings
```

## 5. Run with a Specific Routing Protocol

Use `--extra-settings` with an overlay that overrides `Group.router`:

```bash
# Create a protocol overlay
cat > /tmp/spray_and_wait.txt << 'EOF'
Group.router = SprayAndWaitRouter
SprayAndWaitRouter.nrofCopies = 6
SprayAndWaitRouter.binaryMode = true
EOF

# Run core benchmark with SprayAndWait
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --benchmark core --jobs 4 \
  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \
  --extra-settings /tmp/spray_and_wait.txt
```

## 6. Regenerate Reports

```bash
# Full analysis pipeline
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase all

# Specific phases
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase features
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase output_metrics
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase correlation
```

## 7. Regenerate Figures

```bash
# Aggregated figures (paper-ready)
python3 scenarios/analysis/run_figures_aggregated.py --corpus corpus_v1

# Full analysis pipeline figures
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase figures
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase figures_paper
```

## 8. Validate Reproducibility

After each batch run, a `reports/reproducibility_metadata.json` is written with the exact command, git hash, Java/Python versions, and results.

### Compare two runs

```bash
# Run 1
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --benchmark core --jobs 4 \
  --reproducibility-log reports/run1_metadata.json

# Run 2 (same or different machine)
python3 scenarios/analysis/run_all_scenarios.py \
  --corpus corpus_v1 --benchmark core --jobs 4 \
  --reproducibility-log reports/run2_metadata.json

# Compare
python3 -c "
import json
r1 = json.load(open('reports/run1_metadata.json'))
r2 = json.load(open('reports/run2_metadata.json'))
for key in ['scenarios_run', 'ok', 'fail', 'git_hash', 'java_version', 'benchmark_tier']:
    v1, v2 = r1.get(key), r2.get(key)
    status = 'MATCH' if v1 == v2 else 'DIFFER'
    print(f'{key}: {status} ({v1} vs {v2})')
"
```

### Key reproducibility checks

1. Same `git_hash` -- same code version
2. Same `java_version` -- same JVM
3. Same `scenarios_run` -- same selection
4. Same `ok` / `fail` counts -- same outcomes
5. Same `benchmark_tier` and `filters` -- same parameters

## 9. Interactive Menu

For an interactive session with guided prompts:

```bash
python3 scenarios/analysis/analysis_menu.py
```

Select option 1 ("Ejecutar todas las simulaciones") and choose a benchmark tier when prompted.

## 10. Quick Reference

| Goal | Command |
|------|---------|
| Core benchmark (dry-run) | `--corpus corpus_v1 --benchmark core --dry-run` |
| Core benchmark (execute) | `--corpus corpus_v1 --benchmark core --jobs 4` |
| Stress benchmark | `--corpus corpus_v1 --benchmark stress --jobs 4` |
| All active | `--corpus corpus_v1 --benchmark all --jobs 4` |
| Estimate time | `--corpus corpus_v1 --benchmark core --estimate-runtime` |
| Single family | `--benchmark core --family 01_urban` |
| Single TP | `--benchmark core --tp TP01` |
| Custom protocol | `--extra-settings overlay.txt` |
| Reproducibility log | `--reproducibility-log reports/my_run.json` |
