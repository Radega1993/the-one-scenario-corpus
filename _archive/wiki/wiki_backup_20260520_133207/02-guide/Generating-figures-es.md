# Generar figuras

Propósito: regenerar los assets de figuras usados en páginas de resultados.

```bash
cd scenarios/analysis
source ../../venv/bin/activate
python run_analysis.py --phase figures
python run_analysis.py --phase outputs
```

Los ficheros generados se escriben en `analysis/figures`.
