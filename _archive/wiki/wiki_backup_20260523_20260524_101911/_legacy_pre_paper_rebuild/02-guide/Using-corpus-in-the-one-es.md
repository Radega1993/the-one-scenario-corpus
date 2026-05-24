# Usar el corpus en The ONE

Propósito: ejecutar escenarios de `corpus_v1` con el simulador The ONE.

## Escenario individual

```bash
./one.sh -b 1 scenarios/corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiMedium.settings
```

## Ejecución en lote

```bash
python scenarios/analysis/run_all_scenarios.py --corpus corpus_v1
```

Los reportes se escriben según la configuración de reportes de cada escenario (por defecto `reports/`).
