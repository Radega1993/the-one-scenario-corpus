# Running analysis pipeline

Purpose: run the official analysis sequence on `corpus_v1`.

## Main command

```bash
cd scenarios/analysis
source ../../venv/bin/activate
python run_analysis.py --corpus corpus_v1 --phase all
```

## Outputs

- `analysis/data/*`
- `analysis/reports/*`
- `analysis/figures/*`

Official frozen metrics reference: [Final-frozen-results](Final-frozen-results).
