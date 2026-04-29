# Informe piloto (corpus_v2) — 3 bases × 10 perfiles (30 simulaciones)

Generado: 2026-04-29 10:46

Datos fuente:
- `scenarios/analysis/data/output_metrics.csv`
- `scenarios/analysis/data/indirect_features_diego.csv`

Piloto: bases `U1_CBD_Commuting_HelsinkiMedium`, `R1_Rural_RandomWaypoint`, `D2_PartitionedCity_MuleBridge` y perfiles `TP01..TP10` (TP definido por sufijo `__TPxx_`).

## Resumen por perfil (TP) — métricas agregadas

| TP | media delivery_ratio | media latency_mean (s) | media drop_ratio |
|---|---:|---:|---:|
| TP01 | 0.2901 | 9634.7 | 0.0000 |
| TP02 | 0.3843 | 13381.9 | 0.0000 |
| TP03 | 0.2839 | 10521.7 | 0.0000 |
| TP04 | 0.1609 | 9572.7 | 39.9939 |
| TP05 | 0.0048 | 92.9 | 1.3303 |
| TP06 | 0.2901 | 9634.7 | 0.0000 |
| TP07 | 0.3421 | 15545.4 | 0.0000 |
| TP08 | 0.2433 | 10169.6 | 38.5670 |
| TP09 | 0.2126 | 9917.5 | 46.1613 |
| TP10 | 0.0858 | 1943.9 | 7.2258 |

## Métricas de salida (MessageStatsReport) — por simulación

| Escenario | TP | delivery_ratio | latency_mean (s) | overhead_ratio | drop_ratio |
|---|---|---:|---:|---:|---:|
| `D2_PartitionedCity_MuleBridge__TP01_Baseline` | TP01 | 0.4476 | 3848.8 | 68.0413 | 0.0000 |
| `D2_PartitionedCity_MuleBridge__TP02_LowLoad` | TP02 | 0.6947 | 10727.4 | 65.1818 | 0.0000 |
| `D2_PartitionedCity_MuleBridge__TP03_ManySmall` | TP03 | 0.4644 | 4857.3 | 67.1273 | 0.0000 |
| `D2_PartitionedCity_MuleBridge__TP04_FewLarge` | TP04 | 0.2873 | 4130.3 | 253.5769 | 66.6354 |
| `D2_PartitionedCity_MuleBridge__TP05_CriticalTTL` | TP05 | 0.0041 | 54.0 | 78.0000 | 1.3162 |
| `D2_PartitionedCity_MuleBridge__TP06_LongTTL` | TP06 | 0.4476 | 3848.8 | 68.0413 | 0.0000 |
| `D2_PartitionedCity_MuleBridge__TP07_BurstWindow` | TP07 | 0.5481 | 7349.6 | 67.0244 | 0.0000 |
| `D2_PartitionedCity_MuleBridge__TP08_HubTarget` | TP08 | 0.4041 | 4104.9 | 84.1148 | 2.8887 |
| `D2_PartitionedCity_MuleBridge__TP09_Bimodal` | TP09 | 0.3333 | 4507.8 | 271.8918 | 78.4347 |
| `D2_PartitionedCity_MuleBridge__TP10_Storm` | TP10 | 0.1974 | 2207.4 | 63.9071 | 13.1122 |
| `R1_Rural_RandomWaypoint__TP01_Baseline` | TP01 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP02_LowLoad` | TP02 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP03_ManySmall` | TP03 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP04_FewLarge` | TP04 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 0.9939 |
| `R1_Rural_RandomWaypoint__TP06_LongTTL` | TP06 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP07_BurstWindow` | TP07 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP08_HubTarget` | TP08 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP09_Bimodal` | TP09 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP10_Storm` | TP10 | 0.0000 | — | — | 0.9183 |
| `U1_CBD_Commuting_HelsinkiMedium__TP01_Baseline` | TP01 | 0.4228 | 15420.5 | 76.9135 | 0.0000 |
| `U1_CBD_Commuting_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.4583 | 16036.5 | 76.0909 | 0.0000 |
| `U1_CBD_Commuting_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.3873 | 16186.0 | 71.5367 | 0.0000 |
| `U1_CBD_Commuting_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.1955 | 15015.1 | 299.7429 | 53.3464 |
| `U1_CBD_Commuting_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.0102 | 131.8 | 67.8000 | 1.6809 |
| `U1_CBD_Commuting_HelsinkiMedium__TP06_LongTTL` | TP06 | 0.4228 | 15420.5 | 76.9135 | 0.0000 |
| `U1_CBD_Commuting_HelsinkiMedium__TP07_BurstWindow` | TP07 | 0.4781 | 23741.2 | 81.8400 | 0.0000 |
| `U1_CBD_Commuting_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.3258 | 16234.4 | 421.9684 | 112.8124 |
| `U1_CBD_Commuting_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.3044 | 15327.3 | 245.0447 | 60.0493 |
| `U1_CBD_Commuting_HelsinkiMedium__TP10_Storm` | TP10 | 0.0599 | 1680.5 | 113.4743 | 7.6470 |

## Indirectas tipo Diego — disponibilidad y rasgos de conectividad

| Escenario | TP | source | contact_time_per_min | contact_time_mean_s | total_encounters | ratio_contact_nodes | popularity_top10_ratio |
|---|---|---|---:|---:|---:|---:|---:|
| `D2_PartitionedCity_MuleBridge__TP01_Baseline` | TP01 | ConnectivityONEReport | 2.4694 | 18.5 | 1778.0 | 0.3799 | 0.4411 |
| `D2_PartitionedCity_MuleBridge__TP02_LowLoad` | TP02 | ConnectivityONEReport | 2.3417 | 18.6 | 1686.0 | 0.3638 | 0.4179 |
| `D2_PartitionedCity_MuleBridge__TP03_ManySmall` | TP03 | ConnectivityONEReport | 2.4458 | 18.7 | 1761.0 | 0.3706 | 0.4304 |
| `D2_PartitionedCity_MuleBridge__TP04_FewLarge` | TP04 | ConnectivityONEReport | 2.2903 | 18.5 | 1649.0 | 0.3545 | 0.4161 |
| `D2_PartitionedCity_MuleBridge__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 2.4694 | 18.5 | 1778.0 | 0.3799 | 0.4411 |
| `D2_PartitionedCity_MuleBridge__TP06_LongTTL` | TP06 | ConnectivityONEReport | 2.4694 | 18.5 | 1778.0 | 0.3799 | 0.4411 |
| `D2_PartitionedCity_MuleBridge__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 2.3250 | 18.1 | 1674.0 | 0.3626 | 0.4286 |
| `D2_PartitionedCity_MuleBridge__TP08_HubTarget` | TP08 | ConnectivityONEReport | 2.3667 | 19.0 | 1704.0 | 0.3614 | 0.4375 |
| `D2_PartitionedCity_MuleBridge__TP09_Bimodal` | TP09 | ConnectivityONEReport | 2.4125 | 18.1 | 1737.0 | 0.3791 | 0.4518 |
| `D2_PartitionedCity_MuleBridge__TP10_Storm` | TP10 | ConnectivityONEReport | 2.3778 | 18.5 | 1712.0 | 0.3710 | 0.4232 |
| `R1_Rural_RandomWaypoint__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP06_LongTTL` | TP06 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `U1_CBD_Commuting_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 3.0417 | 183.8 | 2190.0 | 0.3423 | 0.6155 |
| `U1_CBD_Commuting_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 2.9361 | 182.4 | 2114.0 | 0.3155 | 0.5942 |
| `U1_CBD_Commuting_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 2.7736 | 176.7 | 1997.0 | 0.3007 | 0.5608 |
| `U1_CBD_Commuting_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 2.7569 | 178.5 | 1985.0 | 0.2928 | 0.5569 |
| `U1_CBD_Commuting_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 3.0417 | 183.8 | 2190.0 | 0.3423 | 0.6155 |
| `U1_CBD_Commuting_HelsinkiMedium__TP06_LongTTL` | TP06 | ConnectivityONEReport | 3.0417 | 183.8 | 2190.0 | 0.3423 | 0.6155 |
| `U1_CBD_Commuting_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 2.8847 | 187.3 | 2077.0 | 0.3068 | 0.5757 |
| `U1_CBD_Commuting_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 3.1125 | 165.4 | 2241.0 | 0.3406 | 0.6113 |
| `U1_CBD_Commuting_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 2.8181 | 160.1 | 2029.0 | 0.2847 | 0.5399 |
| `U1_CBD_Commuting_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 3.0125 | 187.5 | 2169.0 | 0.3090 | 0.5966 |

## Notas

- Fuentes de indirectas en el piloto: ConnectivityONEReport=30.
- Si ves `—` en columnas de indirectas, significa que para ese caso no estaban presentes los reportes suficientes (p. ej. no se generó `ConnectivityONEReport` en el piloto para ese escenario).
