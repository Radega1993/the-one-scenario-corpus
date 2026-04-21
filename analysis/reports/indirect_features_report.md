# Indirectas tipo Diego (estado actual de datos)

- Escenarios procesados: **60**
- Calculados con `ConnectivityONEReport`: **1**
- Calculados con fallback agregado: **59**
- Con encounters > 0: **58**
- Con `Scenario.endTime` disponible: **60**

## Calculadas con datos actuales (cuando hay datos)

- `contact_time_mean_s`
- `inter_contact_time_mean_s`
- `contact_time_per_min`
- `total_encounters`
- `inter_contact_time_proxy_s`
- `ratio_contact_nodes`
- `popularity_top10_ratio`
- `encounters_top10_mean`
- `sociability_top10_mean`
- `betweenness_centrality` (solo con `ConnectivityONEReport`)
- `window_centrality_mean` (solo con `ConnectivityONEReport`)

## Para completar Diego17 real

Ejecuta simulaciones con overrides de reportes:

```
python scenarios/analysis/run_all_scenarios.py --corpus corpus_v1 \
  --extra-settings scenarios/analysis/diego17_reports_overrides.txt
```

Luego re-ejecuta `run_all_scenarios.py` y después `run_analysis.py --phase indirects`.

CSV: `/home/raul/Documents/the-one/scenarios/analysis/data/indirect_features_diego.csv`
