# Reproducibilidad

**Español** | [English](Reproducibility)

---

Cómo **regenerar** el análisis desde cero y dónde están los artefactos generados. Ver [Quickstart](Quickstart-es) para la lista de comandos.

---

## Regenerar todo el análisis desde cero

Ejecutar desde la **raíz del repositorio** (padre de `scenarios/`). Orden de fases:

1. **Features** — Lee todos los `.settings` del corpus y construye la matriz de features.
   ```bash
   python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase features
   ```
2. **Normalize** — Normalización z-score (requiere `data/features.csv`).
   ```bash
   python3 scenarios/analysis/run_analysis.py --phase normalize
   ```
3. **Correlation** — Pearson, Spearman, distancia coseno y euclídea, clustering (requiere `data/features_normalized.csv`).
   ```bash
   python3 scenarios/analysis/run_analysis.py --phase correlation
   ```
4. **Figures** — Heatmaps, histogramas, scatter PCA (requiere salidas de correlation).
   ```bash
   python3 scenarios/analysis/run_analysis.py --phase figures
   ```
5. **Output metrics** — Construye `output_metrics.csv` desde los reportes del ONE (requiere `*_MessageStatsReport.txt` en el directorio de reportes).
   ```bash
   python3 scenarios/analysis/run_analysis.py --phase output_metrics
   ```
   Si los reportes están en otra ruta: `--reports-dir /ruta/a/reports`
6. **Outputs** — Correlación sobre vectores de salida (requiere `data/output_metrics.csv`).
   ```bash
   python3 scenarios/analysis/run_analysis.py --phase outputs
   ```

**Un solo comando** para los pasos 1–5:
```bash
python3 scenarios/analysis/run_analysis.py --corpus corpus_v1 --phase all
```
Luego ejecutar `--phase outputs` por separado si tienes `output_metrics.csv`.

---

## Regenerar solo las figuras

Si ya tienes `data/features_normalized.csv` y las matrices de correlación:

```bash
python3 scenarios/analysis/run_analysis.py --phase figures
```

Las figuras se escriben en `scenarios/analysis/figures/` (PNG y PDF).

---

## Dónde están los artefactos generados

| Ubicación | Contenido |
|-----------|-----------|
| **scenarios/analysis/data/** | features.csv, features_normalized.csv, normalization_params.csv, correlation_*.csv, distance_*.csv, cluster_assignments.csv, output_metrics.csv, *_outputs.csv |
| **scenarios/analysis/figures/** | heatmap_*.png/.pdf, histogram_*.png/.pdf, scatter_*.png/.pdf |
| **scenarios/analysis/reports/** | correlation_report.txt, multiple_comparisons_report.txt, clustering_report.txt, scenarios_to_diversify.txt, outputs_correlation_report.txt, observaciones_correlacion.md, plan_radical_scenarios.md |

Los reportes del ONE (p. ej. `*_MessageStatsReport.txt`) se escriben en el directorio configurado en cada `.settings` (suele ser `reports/` en la raíz del ONE).

---

## Reproducibilidad de las ejecuciones del ONE

- Cada escenario usa una **semilla** fija cuando está definida (p. ej. `MovementModel.rngSeed` en el .settings). Mismo .settings + misma versión del ONE → mismo movimiento y eventos.
- Para reproducir la fase **output_metrics** y **outputs**, ejecuta los mismos escenarios con la misma compilación del ONE y vuelve a lanzar `output_metrics` y `outputs`. El pipeline de análisis (features → correlation) es determinista con el mismo corpus y código.

---

## Ver también

- [Quickstart](Quickstart-es) — Todos los comandos
- [Instalación](Installation-es) — Configuración inicial
- [Referencia del pipeline](Analysis-pipeline-reference-es) — Fases y artefactos en detalle
