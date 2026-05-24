# Using corpus in The ONE

Purpose: run scenarios from `corpus_v1` with The ONE simulator.

## Single scenario

```bash
./one.sh -b 1 scenarios/corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiMedium.settings
```

## Batch run

```bash
python scenarios/analysis/run_all_scenarios.py --corpus corpus_v1
```

Reports are written according to scenario report settings (default `reports/`).
