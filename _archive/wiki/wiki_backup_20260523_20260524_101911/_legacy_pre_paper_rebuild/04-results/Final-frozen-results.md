# Final frozen results

Purpose: official source of final paper-facing metrics.

Related artifacts:

- `analysis/reports/RESULTADOS_ACTUALES.md`
- `analysis/reports/correlation_report.txt`
- `analysis/reports/correlation_core23_report.txt`
- `analysis/reports/ablation_report.txt`

## Official snapshot

### Full-46

- `max|r| = 0.9377`
- `pairs |r| >= 0.7 = 46/1770 (2.6%)`
- `min cosine = 0.0620`
- `silhouette (Ward k=7) = 0.2929`

### Core-23

- `max|r| = 0.9829`
- `pairs |r| >= 0.7 = 58/1770 (3.3%)`
- `min cosine = 0.0152`
- `silhouette (Ward k=7) = 0.2681`

### Feature-feature (core)

- `mm_WDM <-> mm_Bus = 0.9393`

### Ablation

- `reduced17: 63 (3.6%), silhouette 0.2215`
- `core23: 58 (3.3%), silhouette 0.2681`
- `full46: 46 (2.6%), silhouette 0.2929`

## Freeze statement

This version is the official **final optimized baseline**: stable and publishable, with declared limitations; not an optimal final corpus.
