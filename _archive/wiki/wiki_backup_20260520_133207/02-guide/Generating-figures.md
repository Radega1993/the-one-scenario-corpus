# Generating figures

Purpose: regenerate figure assets used in results pages.

```bash
cd scenarios/analysis
source ../../venv/bin/activate
python run_analysis.py --phase figures
python run_analysis.py --phase outputs
```

Generated files are written to `analysis/figures`.
