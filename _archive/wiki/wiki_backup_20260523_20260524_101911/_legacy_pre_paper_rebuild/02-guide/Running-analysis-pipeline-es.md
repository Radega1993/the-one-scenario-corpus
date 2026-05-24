# Ejecutar el pipeline de análisis

Propósito: ejecutar la secuencia oficial de análisis sobre `corpus_v1`.

## Comando principal

```bash
cd scenarios/analysis
source ../../venv/bin/activate
python run_analysis.py --corpus corpus_v1 --phase all
```

## Salidas

- `analysis/data/*`
- `analysis/reports/*`
- `analysis/figures/*`

Referencia oficial de métricas congeladas: [Final-frozen-results-es](Final-frozen-results-es).
