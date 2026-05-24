# Informe completo (corpus_v2) — 60 bases x 12 perfiles (720 simulaciones)

Generado: 2026-04-30 08:02

Fuentes:
- `scenarios/analysis/data/output_metrics.csv`
- `scenarios/analysis/data/indirect_features_diego.csv`

Cobertura: `720` escenarios (`60` bases x `12` perfiles `TP01..TP12`).

## Resumen por perfil (media en 60 escenarios base)

| TP | media delivery_ratio | media latency_mean (s) | media drop_ratio |
|---|---:|---:|---:|
| TP01 | 0.2681 | 11241.3 | 9.1738 |
| TP02 | 0.2950 | 12276.0 | 22.0115 |
| TP03 | 0.2612 | 11786.9 | 4.6673 |
| TP04 | 0.1407 | 11779.6 | 97.3827 |
| TP05 | 0.0262 | 110.6 | 2.1270 |
| TP06 | 0.2864 | 10810.6 | 16.6726 |
| TP07 | 0.3418 | 13576.1 | 14.3641 |
| TP08 | 0.2366 | 11719.9 | 27.4986 |
| TP09 | 0.2137 | 11068.5 | 64.1202 |
| TP10 | 0.0973 | 1662.1 | 12.3885 |
| TP11 | 0.3037 | 11243.0 | 5.4493 |
| TP12 | 0.2576 | 12052.6 | 17.5174 |

## Señales rapidas (ranking global)

**Top 10 delivery_ratio**
- `C1_Campus_ClassChange__TP07_BurstWindow`: delivery_ratio=1.0000, drop_ratio=0.0000
- `C2_ExamDay_LongStays__TP07_BurstWindow`: delivery_ratio=1.0000, drop_ratio=0.0000
- `C4_Stadium_IngressEgress__TP07_BurstWindow`: delivery_ratio=1.0000, drop_ratio=0.0000
- `R12_SpeedExtremeHigh__TP07_BurstWindow`: delivery_ratio=1.0000, drop_ratio=0.0000
- `R9_ExtremeRange_200m__TP07_BurstWindow`: delivery_ratio=1.0000, drop_ratio=0.0000
- `V1_TaxiLow_HelsinkiMedium__TP07_BurstWindow`: delivery_ratio=1.0000, drop_ratio=0.3619
- `V2_TaxiHigh_HelsinkiMedium__TP07_BurstWindow`: delivery_ratio=1.0000, drop_ratio=0.0000
- `V2_TaxiHigh_HelsinkiMedium__TP12_GroupToGroup`: delivery_ratio=0.9959, drop_ratio=0.2270
- `V2_TaxiHigh_HelsinkiMedium__TP01_Baseline`: delivery_ratio=0.9896, drop_ratio=0.0000
- `V2_TaxiHigh_HelsinkiMedium__TP02_LowLoad`: delivery_ratio=0.9896, drop_ratio=0.0000

**Bottom 10 delivery_ratio**
- `D1_ShelterHotspots_Clusters__TP12_GroupToGroup`: delivery_ratio=0.0000, drop_ratio=0.0000
- `D2_PartitionedCity_MuleBridge__TP12_GroupToGroup`: delivery_ratio=0.0000, drop_ratio=0.0000
- `D3_Aftershock_ErraticMobility__TP05_CriticalTTL`: delivery_ratio=0.0000, drop_ratio=1.0000
- `D4_MedicalTriage_TwoClasses__TP05_CriticalTTL`: delivery_ratio=0.0000, drop_ratio=1.0147
- `D5_UAVMule_FastRoute_HelsinkiMedium__TP02_LowLoad`: delivery_ratio=0.0000, drop_ratio=0.0000
- `D5_UAVMule_FastRoute_HelsinkiMedium__TP04_FewLarge`: delivery_ratio=0.0000, drop_ratio=0.0000
- `D5_UAVMule_FastRoute_HelsinkiMedium__TP06_OneToMany`: delivery_ratio=0.0000, drop_ratio=0.0794
- `D5_UAVMule_FastRoute_HelsinkiMedium__TP08_HubTarget`: delivery_ratio=0.0000, drop_ratio=0.0000
- `D5_UAVMule_FastRoute_HelsinkiMedium__TP11_ManyToOne`: delivery_ratio=0.0000, drop_ratio=0.0000
- `D6_ShortTtlCritical_5to10min__TP02_LowLoad`: delivery_ratio=0.0000, drop_ratio=0.0000

**Top 10 drop_ratio (peor congestion/expiracion)**
- `S1_StrongCommunities_SeparateClusters__TP04_FewLarge`: drop_ratio=4150.5722, delivery_ratio=0.1500
- `U3_MicroMobility_HelsinkiMedium__TP02_LowLoad`: drop_ratio=1320.4842, delivery_ratio=0.3158
- `S1_StrongCommunities_SeparateClusters__TP09_Bimodal`: drop_ratio=1230.3520, delivery_ratio=0.2160
- `U3_MicroMobility_HelsinkiMedium__TP07_BurstWindow`: drop_ratio=564.7663, delivery_ratio=0.1766
- `U3_MicroMobility_HelsinkiMedium__TP12_GroupToGroup`: drop_ratio=546.0450, delivery_ratio=0.4949
- `D1_ShelterHotspots_Clusters__TP09_Bimodal`: drop_ratio=456.4966, delivery_ratio=0.2801
- `U3_MicroMobility_HelsinkiMedium__TP06_OneToMany`: drop_ratio=444.3062, delivery_ratio=0.4979
- `V2_TaxiHigh_HelsinkiMedium__TP09_Bimodal`: drop_ratio=427.7500, delivery_ratio=0.9069
- `D1_ShelterHotspots_Clusters__TP04_FewLarge`: drop_ratio=399.8883, delivery_ratio=0.2011
- `U3_MicroMobility_HelsinkiMedium__TP01_Baseline`: drop_ratio=399.3410, delivery_ratio=0.1019

## Resultados por simulacion (MessageStatsReport)

| Escenario | TP | delivery_ratio | latency_mean (s) | overhead_ratio | drop_ratio |
|---|---:|---:|---:|---:|---:|
| `C1_Campus_ClassChange__TP01_Baseline` | TP01 | 0.9726 | 1443.7 | 57.2662 | 0.0000 |
| `C1_Campus_ClassChange__TP02_LowLoad` | TP02 | 0.9684 | 1456.2 | 57.9022 | 0.0000 |
| `C1_Campus_ClassChange__TP03_ManySmall` | TP03 | 0.9593 | 1501.5 | 58.0415 | 0.0000 |
| `C1_Campus_ClassChange__TP04_FewLarge` | TP04 | 0.5028 | 2374.3 | 311.2198 | 151.5028 |
| `C1_Campus_ClassChange__TP05_CriticalTTL` | TP05 | 0.0253 | 157.8 | 48.5833 | 2.2063 |
| `C1_Campus_ClassChange__TP06_OneToMany` | TP06 | 0.9536 | 1469.1 | 67.9427 | 10.7392 |
| `C1_Campus_ClassChange__TP07_BurstWindow` | TP07 | 1.0000 | 1657.2 | 58.0000 | 0.0000 |
| `C1_Campus_ClassChange__TP08_HubTarget` | TP08 | 0.8680 | 1952.2 | 324.5891 | 252.4515 |
| `C1_Campus_ClassChange__TP09_Bimodal` | TP09 | 0.6766 | 2661.9 | 358.8779 | 230.3269 |
| `C1_Campus_ClassChange__TP10_Storm` | TP10 | 0.7648 | 2019.3 | 47.6918 | 36.6269 |
| `C1_Campus_ClassChange__TP11_ManyToOne` | TP11 | 0.9608 | 1429.3 | 82.7854 | 26.3804 |
| `C1_Campus_ClassChange__TP12_GroupToGroup` | TP12 | 0.9611 | 1487.7 | 58.3872 | 0.0000 |
| `C2_ExamDay_LongStays__TP01_Baseline` | TP01 | 0.8589 | 5456.5 | 46.4758 | 0.0000 |
| `C2_ExamDay_LongStays__TP02_LowLoad` | TP02 | 0.8842 | 5554.7 | 46.0119 | 0.0000 |
| `C2_ExamDay_LongStays__TP03_ManySmall` | TP03 | 0.8547 | 5428.8 | 46.0235 | 0.0000 |
| `C2_ExamDay_LongStays__TP04_FewLarge` | TP04 | 0.3425 | 6123.2 | 191.4355 | 61.3149 |
| `C2_ExamDay_LongStays__TP05_CriticalTTL` | TP05 | 0.0062 | 123.3 | 44.6667 | 1.2676 |
| `C2_ExamDay_LongStays__TP06_OneToMany` | TP06 | 0.8619 | 6500.5 | 51.4438 | 5.0887 |
| `C2_ExamDay_LongStays__TP07_BurstWindow` | TP07 | 1.0000 | 4916.8 | 46.0000 | 0.0000 |
| `C2_ExamDay_LongStays__TP08_HubTarget` | TP08 | 0.6990 | 6368.0 | 209.8142 | 124.4258 |
| `C2_ExamDay_LongStays__TP09_Bimodal` | TP09 | 0.5751 | 7072.2 | 232.1021 | 118.3005 |
| `C2_ExamDay_LongStays__TP10_Storm` | TP10 | 0.2098 | 2236.3 | 44.0588 | 9.8315 |
| `C2_ExamDay_LongStays__TP11_ManyToOne` | TP11 | 0.8062 | 5828.6 | 58.4706 | 7.9103 |
| `C2_ExamDay_LongStays__TP12_GroupToGroup` | TP12 | 0.8609 | 5320.4 | 46.8765 | 0.0000 |
| `C3_Hackathon_24h__TP01_Baseline` | TP01 | 0.7012 | 13644.4 | 175.0888 | 104.4004 |
| `C3_Hackathon_24h__TP02_LowLoad` | TP02 | 0.8187 | 13828.8 | 38.6709 | 0.0000 |
| `C3_Hackathon_24h__TP03_ManySmall` | TP03 | 0.8413 | 13530.1 | 37.0842 | 0.0000 |
| `C3_Hackathon_24h__TP04_FewLarge` | TP04 | 0.3051 | 15407.3 | 80.3333 | 23.3898 |
| `C3_Hackathon_24h__TP05_CriticalTTL` | TP05 | 0.0062 | 74.0 | 16.5000 | 1.0996 |
| `C3_Hackathon_24h__TP06_OneToMany` | TP06 | 0.8271 | 13160.1 | 112.9241 | 77.4066 |
| `C3_Hackathon_24h__TP07_BurstWindow` | TP07 | 0.9323 | 15581.9 | 270.9393 | 227.8301 |
| `C3_Hackathon_24h__TP08_HubTarget` | TP08 | 0.5028 | 14557.4 | 165.0921 | 74.7154 |
| `C3_Hackathon_24h__TP09_Bimodal` | TP09 | 0.4987 | 15993.4 | 122.5806 | 54.4045 |
| `C3_Hackathon_24h__TP10_Storm` | TP10 | 0.0470 | 2070.4 | 39.9050 | 2.8044 |
| `C3_Hackathon_24h__TP11_ManyToOne` | TP11 | 0.5847 | 12919.9 | 136.5343 | 64.1945 |
| `C3_Hackathon_24h__TP12_GroupToGroup` | TP12 | 0.6472 | 14049.1 | 178.3223 | 98.0409 |
| `C4_Stadium_IngressEgress__TP01_Baseline` | TP01 | 0.8264 | 2308.7 | 74.8800 | 0.0000 |
| `C4_Stadium_IngressEgress__TP02_LowLoad` | TP02 | 0.8750 | 2012.0 | 73.3333 | 0.0000 |
| `C4_Stadium_IngressEgress__TP03_ManySmall` | TP03 | 0.7658 | 2321.9 | 79.6000 | 0.0000 |
| `C4_Stadium_IngressEgress__TP04_FewLarge` | TP04 | 0.6136 | 2631.3 | 170.3333 | 76.7045 |
| `C4_Stadium_IngressEgress__TP05_CriticalTTL` | TP05 | 0.0083 | 25.7 | 90.0000 | 1.7025 |
| `C4_Stadium_IngressEgress__TP06_OneToMany` | TP06 | 0.7459 | 2676.8 | 77.8242 | 0.0000 |
| `C4_Stadium_IngressEgress__TP07_BurstWindow` | TP07 | 1.0000 | 2495.9 | 78.0000 | 0.0000 |
| `C4_Stadium_IngressEgress__TP08_HubTarget` | TP08 | 0.7664 | 2136.4 | 75.7594 | 0.0000 |
| `C4_Stadium_IngressEgress__TP09_Bimodal` | TP09 | 0.7569 | 2370.7 | 114.2110 | 36.3056 |
| `C4_Stadium_IngressEgress__TP10_Storm` | TP10 | 0.4711 | 2196.4 | 68.4800 | 29.0299 |
| `C4_Stadium_IngressEgress__TP11_ManyToOne` | TP11 | 0.6803 | 2633.1 | 86.1386 | 0.0000 |
| `C4_Stadium_IngressEgress__TP12_GroupToGroup` | TP12 | 0.7833 | 2205.8 | 76.2872 | 0.0000 |
| `C5_Library_Quiet__TP01_Baseline` | TP01 | 0.6037 | 14442.3 | 38.9762 | 0.0000 |
| `C5_Library_Quiet__TP02_LowLoad` | TP02 | 0.5895 | 14717.2 | 41.8036 | 0.0000 |
| `C5_Library_Quiet__TP03_ManySmall` | TP03 | 0.5814 | 14703.9 | 38.4701 | 0.0000 |
| `C5_Library_Quiet__TP04_FewLarge` | TP04 | 0.2762 | 12348.6 | 65.6000 | 14.3481 |
| `C5_Library_Quiet__TP05_CriticalTTL` | TP05 | 0.0041 | 144.4 | 21.5000 | 1.0801 |
| `C5_Library_Quiet__TP06_OneToMany` | TP06 | 0.6062 | 14754.9 | 39.4133 | 0.0062 |
| `C5_Library_Quiet__TP07_BurstWindow` | TP07 | 0.9333 | 17590.4 | 40.6571 | 0.0000 |
| `C5_Library_Quiet__TP08_HubTarget` | TP08 | 0.5567 | 13794.8 | 50.8870 | 7.5742 |
| `C5_Library_Quiet__TP09_Bimodal` | TP09 | 0.3817 | 14263.5 | 71.3258 | 18.9136 |
| `C5_Library_Quiet__TP10_Storm` | TP10 | 0.0361 | 2045.9 | 36.4305 | 2.1929 |
| `C5_Library_Quiet__TP11_ManyToOne` | TP11 | 0.7031 | 13309.3 | 32.9194 | 0.0000 |
| `C5_Library_Quiet__TP12_GroupToGroup` | TP12 | 0.5951 | 14975.7 | 39.7251 | 0.0000 |
| `C6_EmergencyDrill_Evacuation__TP01_Baseline` | TP01 | 0.5185 | 0.5 | 74.1429 | 0.0000 |
| `C6_EmergencyDrill_Evacuation__TP02_LowLoad` | TP02 | 0.6471 | 0.5 | 60.0909 | 0.0000 |
| `C6_EmergencyDrill_Evacuation__TP03_ManySmall` | TP03 | 0.5081 | 1.2 | 77.2128 | 0.0000 |
| `C6_EmergencyDrill_Evacuation__TP04_FewLarge` | TP04 | 0.4828 | 1.6 | 79.1429 | 0.0000 |
| `C6_EmergencyDrill_Evacuation__TP05_CriticalTTL` | TP05 | 0.5185 | 0.5 | 74.1429 | 37.9383 |
| `C6_EmergencyDrill_Evacuation__TP06_OneToMany` | TP06 | 0.4348 | 0.5 | 81.8000 | 0.0000 |
| `C6_EmergencyDrill_Evacuation__TP07_BurstWindow` | TP07 | 0.5152 | 0.5 | 74.7059 | 0.0000 |
| `C6_EmergencyDrill_Evacuation__TP08_HubTarget` | TP08 | 0.4720 | 0.5 | 83.0132 | 0.0000 |
| `C6_EmergencyDrill_Evacuation__TP09_Bimodal` | TP09 | 0.5208 | 0.7 | 72.9400 | 0.0000 |
| `C6_EmergencyDrill_Evacuation__TP10_Storm` | TP10 | 0.4449 | 25.0 | 796.8860 | 343.4312 |
| `C6_EmergencyDrill_Evacuation__TP11_ManyToOne` | TP11 | 0.4037 | 0.7 | 97.7077 | 0.0000 |
| `C6_EmergencyDrill_Evacuation__TP12_GroupToGroup` | TP12 | 0.5250 | 0.6 | 74.4286 | 0.0000 |
| `D1_ShelterHotspots_Clusters__TP01_Baseline` | TP01 | 0.3128 | 529.5 | 79.8553 | 0.0000 |
| `D1_ShelterHotspots_Clusters__TP02_LowLoad` | TP02 | 0.2396 | 452.5 | 102.6957 | 0.0000 |
| `D1_ShelterHotspots_Clusters__TP03_ManySmall` | TP03 | 0.3046 | 538.8 | 80.8063 | 0.0000 |
| `D1_ShelterHotspots_Clusters__TP04_FewLarge` | TP04 | 0.2011 | 765.0 | 2024.3333 | 399.8883 |
| `D1_ShelterHotspots_Clusters__TP05_CriticalTTL` | TP05 | 0.0679 | 162.4 | 61.6970 | 5.1770 |
| `D1_ShelterHotspots_Clusters__TP06_OneToMany` | TP06 | 0.4433 | 483.8 | 228.2558 | 69.9361 |
| `D1_ShelterHotspots_Clusters__TP07_BurstWindow` | TP07 | 0.3049 | 507.0 | 81.8468 | 0.0000 |
| `D1_ShelterHotspots_Clusters__TP08_HubTarget` | TP08 | 0.3722 | 441.9 | 62.7535 | 0.0000 |
| `D1_ShelterHotspots_Clusters__TP09_Bimodal` | TP09 | 0.2801 | 693.9 | 1684.7178 | 456.4966 |
| `D1_ShelterHotspots_Clusters__TP10_Storm` | TP10 | 0.3034 | 621.3 | 244.6931 | 73.6163 |
| `D1_ShelterHotspots_Clusters__TP11_ManyToOne` | TP11 | 0.4299 | 487.3 | 56.7842 | 0.0000 |
| `D1_ShelterHotspots_Clusters__TP12_GroupToGroup` | TP12 | 0.0000 | — | — | 0.0000 |
| `D2_PartitionedCity_MuleBridge__TP01_Baseline` | TP01 | 0.4476 | 3848.8 | 68.0413 | 0.0000 |
| `D2_PartitionedCity_MuleBridge__TP02_LowLoad` | TP02 | 0.6947 | 10727.4 | 65.1818 | 0.0000 |
| `D2_PartitionedCity_MuleBridge__TP03_ManySmall` | TP03 | 0.4644 | 4857.3 | 67.1273 | 0.0000 |
| `D2_PartitionedCity_MuleBridge__TP04_FewLarge` | TP04 | 0.2873 | 4130.3 | 253.5769 | 66.6354 |
| `D2_PartitionedCity_MuleBridge__TP05_CriticalTTL` | TP05 | 0.0041 | 54.0 | 78.0000 | 1.3162 |
| `D2_PartitionedCity_MuleBridge__TP06_OneToMany` | TP06 | 0.4423 | 3346.7 | 69.8042 | 1.0113 |
| `D2_PartitionedCity_MuleBridge__TP07_BurstWindow` | TP07 | 0.5481 | 7349.6 | 67.0244 | 0.0000 |
| `D2_PartitionedCity_MuleBridge__TP08_HubTarget` | TP08 | 0.4041 | 4104.9 | 84.1148 | 2.8887 |
| `D2_PartitionedCity_MuleBridge__TP09_Bimodal` | TP09 | 0.3333 | 4507.8 | 271.8918 | 78.4347 |
| `D2_PartitionedCity_MuleBridge__TP10_Storm` | TP10 | 0.1974 | 2207.4 | 63.9071 | 13.1122 |
| `D2_PartitionedCity_MuleBridge__TP11_ManyToOne` | TP11 | 0.4361 | 3892.7 | 72.0969 | 0.0000 |
| `D2_PartitionedCity_MuleBridge__TP12_GroupToGroup` | TP12 | 0.0000 | — | — | 0.0000 |
| `D3_Aftershock_ErraticMobility__TP01_Baseline` | TP01 | 0.0225 | 24355.8 | 58.9091 | 0.0000 |
| `D3_Aftershock_ErraticMobility__TP02_LowLoad` | TP02 | 0.0309 | 33087.6 | 42.0000 | 0.0000 |
| `D3_Aftershock_ErraticMobility__TP03_ManySmall` | TP03 | 0.0221 | 18096.2 | 34.9184 | 0.0000 |
| `D3_Aftershock_ErraticMobility__TP04_FewLarge` | TP04 | 0.0221 | 15922.4 | 28.0000 | 0.0000 |
| `D3_Aftershock_ErraticMobility__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0000 |
| `D3_Aftershock_ErraticMobility__TP06_OneToMany` | TP06 | 0.0330 | 18968.8 | 0.9063 | 0.0794 |
| `D3_Aftershock_ErraticMobility__TP07_BurstWindow` | TP07 | 0.0329 | 23511.0 | 60.6667 | 0.0000 |
| `D3_Aftershock_ErraticMobility__TP08_HubTarget` | TP08 | 0.0371 | 15254.4 | 31.8611 | 0.0000 |
| `D3_Aftershock_ErraticMobility__TP09_Bimodal` | TP09 | 0.0153 | 21025.6 | 50.8889 | 0.0000 |
| `D3_Aftershock_ErraticMobility__TP10_Storm` | TP10 | 0.0016 | 1663.9 | 70.4000 | 1.0270 |
| `D3_Aftershock_ErraticMobility__TP11_ManyToOne` | TP11 | 0.0423 | 20485.5 | 27.9512 | 0.0000 |
| `D3_Aftershock_ErraticMobility__TP12_GroupToGroup` | TP12 | 0.0245 | 21751.6 | 56.5000 | 0.0000 |
| `D4_MedicalTriage_TwoClasses__TP01_Baseline` | TP01 | 0.0819 | 20121.0 | 42.1538 | 0.0000 |
| `D4_MedicalTriage_TwoClasses__TP02_LowLoad` | TP02 | 0.0833 | 17252.9 | 40.5000 | 0.0000 |
| `D4_MedicalTriage_TwoClasses__TP03_ManySmall` | TP03 | 0.0652 | 18724.9 | 35.7708 | 0.0000 |
| `D4_MedicalTriage_TwoClasses__TP04_FewLarge` | TP04 | 0.0773 | 15188.4 | 23.4286 | 0.0994 |
| `D4_MedicalTriage_TwoClasses__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0147 |
| `D4_MedicalTriage_TwoClasses__TP06_OneToMany` | TP06 | 0.1247 | 20678.1 | 31.8017 | 0.0794 |
| `D4_MedicalTriage_TwoClasses__TP07_BurstWindow` | TP07 | 0.1314 | 20545.8 | 46.0217 | 0.0000 |
| `D4_MedicalTriage_TwoClasses__TP08_HubTarget` | TP08 | 0.0907 | 21253.7 | 36.4659 | 0.0000 |
| `D4_MedicalTriage_TwoClasses__TP09_Bimodal` | TP09 | 0.0788 | 20402.2 | 33.3556 | 0.0000 |
| `D4_MedicalTriage_TwoClasses__TP10_Storm` | TP10 | 0.0059 | 1652.4 | 39.5556 | 1.1324 |
| `D4_MedicalTriage_TwoClasses__TP11_ManyToOne` | TP11 | 0.1196 | 16982.4 | 21.7500 | 0.0000 |
| `D4_MedicalTriage_TwoClasses__TP12_GroupToGroup` | TP12 | 0.0920 | 21936.8 | 49.2444 | 0.0000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP01_Baseline` | TP01 | 0.0125 | 963.5 | 17.0000 | 0.0000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.0000 | — | — | 0.0000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.0050 | 571.6 | 37.7273 | 0.0000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.0000 | — | — | 0.0000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.0042 | 219.2 | 20.5000 | 1.0793 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.0000 | — | — | 0.0794 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP07_BurstWindow` | TP07 | 0.0028 | 576.0 | 65.0000 | 0.0000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.0000 | — | — | 0.0000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.0087 | 461.2 | 23.2000 | 0.0000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP10_Storm` | TP10 | 0.0050 | 419.5 | 43.3226 | 1.1217 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.0000 | — | — | 0.0000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.0389 | 327.3 | 2.8947 | 0.0000 |
| `D6_ShortTtlCritical_5to10min__TP01_Baseline` | TP01 | 0.0062 | 516.2 | 131.0000 | 0.0000 |
| `D6_ShortTtlCritical_5to10min__TP02_LowLoad` | TP02 | 0.0000 | — | — | 0.0000 |
| `D6_ShortTtlCritical_5to10min__TP03_ManySmall` | TP03 | 0.0109 | 5415.2 | 54.6250 | 0.0000 |
| `D6_ShortTtlCritical_5to10min__TP04_FewLarge` | TP04 | 0.0000 | — | — | 0.0000 |
| `D6_ShortTtlCritical_5to10min__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 0.9938 |
| `D6_ShortTtlCritical_5to10min__TP06_OneToMany` | TP06 | 0.0000 | — | — | 0.0000 |
| `D6_ShortTtlCritical_5to10min__TP07_BurstWindow` | TP07 | 0.0078 | 1095.4 | 147.0000 | 0.0000 |
| `D6_ShortTtlCritical_5to10min__TP08_HubTarget` | TP08 | 0.0062 | 4092.6 | 115.0000 | 0.0000 |
| `D6_ShortTtlCritical_5to10min__TP09_Bimodal` | TP09 | 0.0052 | 516.2 | 145.0000 | 0.0000 |
| `D6_ShortTtlCritical_5to10min__TP10_Storm` | TP10 | 0.0024 | 1439.5 | 76.2000 | 0.9077 |
| `D6_ShortTtlCritical_5to10min__TP11_ManyToOne` | TP11 | 0.0000 | — | — | 0.0000 |
| `D6_ShortTtlCritical_5to10min__TP12_GroupToGroup` | TP12 | 0.0189 | 7612.9 | 30.3333 | 0.0000 |
| `D7_HighLoad_TrafficStorm__TP01_Baseline` | TP01 | 0.0062 | 3134.7 | 124.0000 | 0.0000 |
| `D7_HighLoad_TrafficStorm__TP02_LowLoad` | TP02 | 0.0000 | — | — | 0.0000 |
| `D7_HighLoad_TrafficStorm__TP03_ManySmall` | TP03 | 0.0108 | 4767.1 | 55.5000 | 0.0000 |
| `D7_HighLoad_TrafficStorm__TP04_FewLarge` | TP04 | 0.0000 | — | — | 0.0000 |
| `D7_HighLoad_TrafficStorm__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 0.9876 |
| `D7_HighLoad_TrafficStorm__TP06_OneToMany` | TP06 | 0.0000 | — | — | 0.1077 |
| `D7_HighLoad_TrafficStorm__TP07_BurstWindow` | TP07 | 0.0086 | 4244.7 | 123.0000 | 0.0000 |
| `D7_HighLoad_TrafficStorm__TP08_HubTarget` | TP08 | 0.0123 | 8188.9 | 55.2500 | 0.0000 |
| `D7_HighLoad_TrafficStorm__TP09_Bimodal` | TP09 | 0.0104 | 6030.9 | 66.5000 | 0.0000 |
| `D7_HighLoad_TrafficStorm__TP10_Storm` | TP10 | 0.0029 | 1132.1 | 69.8333 | 0.9232 |
| `D7_HighLoad_TrafficStorm__TP11_ManyToOne` | TP11 | 0.0000 | — | — | 0.0000 |
| `D7_HighLoad_TrafficStorm__TP12_GroupToGroup` | TP12 | 0.0189 | 5594.0 | 40.0000 | 0.0000 |
| `D8_InfrastructureReturns_BackboneLinks__TP01_Baseline` | TP01 | 0.4753 | 1961.5 | 77.0693 | 0.0000 |
| `D8_InfrastructureReturns_BackboneLinks__TP02_LowLoad` | TP02 | 0.4583 | 2032.8 | 79.6818 | 0.0000 |
| `D8_InfrastructureReturns_BackboneLinks__TP03_ManySmall` | TP03 | 0.4530 | 1885.6 | 80.5741 | 0.0000 |
| `D8_InfrastructureReturns_BackboneLinks__TP04_FewLarge` | TP04 | 0.2961 | 3348.2 | 540.8113 | 152.3575 |
| `D8_InfrastructureReturns_BackboneLinks__TP05_CriticalTTL` | TP05 | 0.0123 | 182.7 | 61.6667 | 1.7551 |
| `D8_InfrastructureReturns_BackboneLinks__TP06_OneToMany` | TP06 | 0.4732 | 1971.5 | 82.2549 | 3.6124 |
| `D8_InfrastructureReturns_BackboneLinks__TP07_BurstWindow` | TP07 | 0.4890 | 2108.4 | 78.7528 | 0.0000 |
| `D8_InfrastructureReturns_BackboneLinks__TP08_HubTarget` | TP08 | 0.4320 | 1994.1 | 123.3938 | 17.5557 |
| `D8_InfrastructureReturns_BackboneLinks__TP09_Bimodal` | TP09 | 0.3677 | 2694.0 | 494.9860 | 167.8969 |
| `D8_InfrastructureReturns_BackboneLinks__TP10_Storm` | TP10 | 0.3984 | 1928.4 | 77.2011 | 30.5990 |
| `D8_InfrastructureReturns_BackboneLinks__TP11_ManyToOne` | TP11 | 0.4948 | 2048.3 | 73.8750 | 0.0000 |
| `D8_InfrastructureReturns_BackboneLinks__TP12_GroupToGroup` | TP12 | 0.0000 | — | — | 0.0000 |
| `D9_Critical_1minTTL__TP01_Baseline` | TP01 | 0.0287 | 14496.7 | 44.3571 | 0.0000 |
| `D9_Critical_1minTTL__TP02_LowLoad` | TP02 | 0.0211 | 23856.3 | 53.0000 | 0.0000 |
| `D9_Critical_1minTTL__TP03_ManySmall` | TP03 | 0.0282 | 16396.0 | 44.7619 | 0.0000 |
| `D9_Critical_1minTTL__TP04_FewLarge` | TP04 | 0.0112 | 28566.9 | 100.5000 | 0.0000 |
| `D9_Critical_1minTTL__TP05_CriticalTTL` | TP05 | 0.0021 | 253.7 | 6.0000 | 1.0062 |
| `D9_Critical_1minTTL__TP06_OneToMany` | TP06 | 0.0371 | 22495.1 | 31.9722 | 0.0000 |
| `D9_Critical_1minTTL__TP07_BurstWindow` | TP07 | 0.0568 | 12733.3 | 48.4762 | 0.0000 |
| `D9_Critical_1minTTL__TP08_HubTarget` | TP08 | 0.0103 | 22731.2 | 160.4000 | 0.0000 |
| `D9_Critical_1minTTL__TP09_Bimodal` | TP09 | 0.0293 | 13689.5 | 43.5294 | 0.0000 |
| `D9_Critical_1minTTL__TP10_Storm` | TP10 | 0.0032 | 1457.1 | 40.4000 | 1.0456 |
| `D9_Critical_1minTTL__TP11_ManyToOne` | TP11 | 0.0134 | 13526.4 | 106.2308 | 0.0000 |
| `D9_Critical_1minTTL__TP12_GroupToGroup` | TP12 | 0.0286 | 16335.1 | 48.5714 | 0.0000 |
| `R10_TinyRange_5m__TP01_Baseline` | TP01 | 0.0104 | 10174.1 | 21.2000 | 0.0000 |
| `R10_TinyRange_5m__TP02_LowLoad` | TP02 | 0.0000 | — | — | 0.0000 |
| `R10_TinyRange_5m__TP03_ManySmall` | TP03 | 0.0068 | 16408.7 | 27.6000 | 0.0000 |
| `R10_TinyRange_5m__TP04_FewLarge` | TP04 | 0.0000 | — | — | 0.0000 |
| `R10_TinyRange_5m__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 0.9959 |
| `R10_TinyRange_5m__TP06_OneToMany` | TP06 | 0.0216 | 15361.9 | 5.5238 | 0.0794 |
| `R10_TinyRange_5m__TP07_BurstWindow` | TP07 | 0.0111 | 18827.7 | 28.7500 | 0.0000 |
| `R10_TinyRange_5m__TP08_HubTarget` | TP08 | 0.0134 | 22237.7 | 13.2308 | 0.0000 |
| `R10_TinyRange_5m__TP09_Bimodal` | TP09 | 0.0103 | 10156.9 | 19.0000 | 0.0000 |
| `R10_TinyRange_5m__TP10_Storm` | TP10 | 0.0006 | 2534.1 | 42.0000 | 0.9457 |
| `R10_TinyRange_5m__TP11_ManyToOne` | TP11 | 0.0443 | 21330.9 | 3.8140 | 0.0000 |
| `R10_TinyRange_5m__TP12_GroupToGroup` | TP12 | 0.0082 | 18014.5 | 24.7500 | 0.0000 |
| `R11_SpeedExtremeLow__TP01_Baseline` | TP01 | 0.0000 | — | — | 0.0000 |
| `R11_SpeedExtremeLow__TP02_LowLoad` | TP02 | 0.0000 | — | — | 0.0000 |
| `R11_SpeedExtremeLow__TP03_ManySmall` | TP03 | 0.0000 | — | — | 0.0000 |
| `R11_SpeedExtremeLow__TP04_FewLarge` | TP04 | 0.0000 | — | — | 0.0000 |
| `R11_SpeedExtremeLow__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 0.9959 |
| `R11_SpeedExtremeLow__TP06_OneToMany` | TP06 | 0.0000 | — | — | 0.0794 |
| `R11_SpeedExtremeLow__TP07_BurstWindow` | TP07 | 0.0000 | — | — | 0.0000 |
| `R11_SpeedExtremeLow__TP08_HubTarget` | TP08 | 0.0000 | — | — | 0.0000 |
| `R11_SpeedExtremeLow__TP09_Bimodal` | TP09 | 0.0000 | — | — | 0.0000 |
| `R11_SpeedExtremeLow__TP10_Storm` | TP10 | 0.0000 | — | — | 0.9186 |
| `R11_SpeedExtremeLow__TP11_ManyToOne` | TP11 | 0.0000 | — | — | 0.0000 |
| `R11_SpeedExtremeLow__TP12_GroupToGroup` | TP12 | 0.0000 | — | — | 0.0000 |
| `R12_SpeedExtremeHigh__TP01_Baseline` | TP01 | 0.8824 | 3546.5 | 35.5619 | 0.0000 |
| `R12_SpeedExtremeHigh__TP02_LowLoad` | TP02 | 0.9583 | 2156.1 | 37.7717 | 0.0000 |
| `R12_SpeedExtremeHigh__TP03_ManySmall` | TP03 | 0.7298 | 6844.3 | 9.9248 | 0.0000 |
| `R12_SpeedExtremeHigh__TP04_FewLarge` | TP04 | 0.3408 | 10996.1 | 11.6721 | 0.2402 |
| `R12_SpeedExtremeHigh__TP05_CriticalTTL` | TP05 | 0.0210 | 86.9 | 28.2000 | 1.5861 |
| `R12_SpeedExtremeHigh__TP06_OneToMany` | TP06 | 0.7072 | 7038.7 | 20.7434 | 0.0866 |
| `R12_SpeedExtremeHigh__TP07_BurstWindow` | TP07 | 1.0000 | 5548.0 | 36.3878 | 0.0000 |
| `R12_SpeedExtremeHigh__TP08_HubTarget` | TP08 | 0.7897 | 5857.0 | 19.9739 | 0.1845 |
| `R12_SpeedExtremeHigh__TP09_Bimodal` | TP09 | 0.6777 | 6343.7 | 22.7943 | 0.0000 |
| `R12_SpeedExtremeHigh__TP10_Storm` | TP10 | 0.2386 | 1929.4 | 4.9299 | 2.0518 |
| `R12_SpeedExtremeHigh__TP11_ManyToOne` | TP11 | 0.7763 | 6380.3 | 20.0066 | 0.0000 |
| `R12_SpeedExtremeHigh__TP12_GroupToGroup` | TP12 | 0.9018 | 3992.3 | 33.0363 | 0.0000 |
| `R1_Rural_RandomWaypoint__TP01_Baseline` | TP01 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP02_LowLoad` | TP02 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP03_ManySmall` | TP03 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP04_FewLarge` | TP04 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 0.9939 |
| `R1_Rural_RandomWaypoint__TP06_OneToMany` | TP06 | 0.0000 | — | — | 0.0794 |
| `R1_Rural_RandomWaypoint__TP07_BurstWindow` | TP07 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP08_HubTarget` | TP08 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP09_Bimodal` | TP09 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP10_Storm` | TP10 | 0.0000 | — | — | 0.9183 |
| `R1_Rural_RandomWaypoint__TP11_ManyToOne` | TP11 | 0.0000 | — | — | 0.0000 |
| `R1_Rural_RandomWaypoint__TP12_GroupToGroup` | TP12 | 0.0000 | — | — | 0.0000 |
| `R2_VillagesTrails_ThreeClusters__TP01_Baseline` | TP01 | 0.2259 | 7743.9 | 38.4722 | 0.0000 |
| `R2_VillagesTrails_ThreeClusters__TP02_LowLoad` | TP02 | 0.2371 | 8979.5 | 34.9130 | 0.0000 |
| `R2_VillagesTrails_ThreeClusters__TP03_ManySmall` | TP03 | 0.2359 | 8366.4 | 34.6958 | 0.0000 |
| `R2_VillagesTrails_ThreeClusters__TP04_FewLarge` | TP04 | 0.1492 | 7544.4 | 78.5556 | 9.3260 |
| `R2_VillagesTrails_ThreeClusters__TP05_CriticalTTL` | TP05 | 0.0042 | 204.8 | 23.0000 | 1.0900 |
| `R2_VillagesTrails_ThreeClusters__TP06_OneToMany` | TP06 | 0.2454 | 8521.5 | 34.3866 | 0.0794 |
| `R2_VillagesTrails_ThreeClusters__TP07_BurstWindow` | TP07 | 0.2727 | 6705.1 | 39.3333 | 0.0000 |
| `R2_VillagesTrails_ThreeClusters__TP08_HubTarget` | TP08 | 0.1814 | 7860.3 | 45.3352 | 0.0000 |
| `R2_VillagesTrails_ThreeClusters__TP09_Bimodal` | TP09 | 0.2205 | 7776.4 | 60.2598 | 7.5885 |
| `R2_VillagesTrails_ThreeClusters__TP10_Storm` | TP10 | 0.0507 | 1997.9 | 32.2949 | 2.4922 |
| `R2_VillagesTrails_ThreeClusters__TP11_ManyToOne` | TP11 | 0.2515 | 7481.1 | 32.6598 | 0.0000 |
| `R2_VillagesTrails_ThreeClusters__TP12_GroupToGroup` | TP12 | 0.0000 | — | — | 0.0000 |
| `R3_WildlifeTracking__TP01_Baseline` | TP01 | 0.0041 | 23405.3 | 19.0000 | 0.0000 |
| `R3_WildlifeTracking__TP02_LowLoad` | TP02 | 0.0000 | — | — | 0.0000 |
| `R3_WildlifeTracking__TP03_ManySmall` | TP03 | 0.0058 | 17196.6 | 14.5385 | 0.0000 |
| `R3_WildlifeTracking__TP04_FewLarge` | TP04 | 0.0056 | 4419.4 | 36.0000 | 0.1444 |
| `R3_WildlifeTracking__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 0.9938 |
| `R3_WildlifeTracking__TP06_OneToMany` | TP06 | 0.0000 | — | — | 0.0794 |
| `R3_WildlifeTracking__TP07_BurstWindow` | TP07 | 0.0054 | 27400.3 | 17.5000 | 0.0000 |
| `R3_WildlifeTracking__TP08_HubTarget` | TP08 | 0.0000 | — | — | 0.0000 |
| `R3_WildlifeTracking__TP09_Bimodal` | TP09 | 0.0052 | 19782.2 | 15.3333 | 0.0000 |
| `R3_WildlifeTracking__TP10_Storm` | TP10 | 0.0005 | 1930.2 | 17.0000 | 0.9277 |
| `R3_WildlifeTracking__TP11_ManyToOne` | TP11 | 0.0000 | — | — | 0.0000 |
| `R3_WildlifeTracking__TP12_GroupToGroup` | TP12 | 0.0041 | 22421.8 | 21.5000 | 0.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP01_Baseline` | TP01 | 0.5364 | 6202.7 | 0.9380 | 0.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.5208 | 6400.9 | 1.0400 | 0.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.5278 | 7533.3 | 0.8329 | 0.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.3536 | 3296.5 | 5.9531 | 2.8066 |
| `R4_ParkRangers_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.0894 | 106.0 | 1.1163 | 1.0936 |
| `R4_ParkRangers_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.4814 | 7621.5 | 1.0600 | 0.1258 |
| `R4_ParkRangers_HelsinkiMedium__TP07_BurstWindow` | TP07 | 0.7923 | 8349.5 | 0.8897 | 0.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.5347 | 7110.3 | 0.9351 | 0.0990 |
| `R4_ParkRangers_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.4508 | 5516.6 | 4.9579 | 2.6891 |
| `R4_ParkRangers_HelsinkiMedium__TP10_Storm` | TP10 | 0.1732 | 1151.3 | 1.6000 | 1.1988 |
| `R4_ParkRangers_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.7206 | 10445.5 | 0.5937 | 0.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.4990 | 6295.8 | 0.9098 | 0.0020 |
| `R5_MountainRescue__TP01_Baseline` | TP01 | 0.0186 | 4278.6 | 5.0000 | 0.0000 |
| `R5_MountainRescue__TP02_LowLoad` | TP02 | 0.0303 | 628.1 | 2.0000 | 0.0000 |
| `R5_MountainRescue__TP03_ManySmall` | TP03 | 0.0122 | 5442.8 | 13.2222 | 0.0000 |
| `R5_MountainRescue__TP04_FewLarge` | TP04 | 0.0172 | 4469.3 | 3.0000 | 0.0000 |
| `R5_MountainRescue__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 0.9752 |
| `R5_MountainRescue__TP06_OneToMany` | TP06 | 0.0000 | — | — | 0.0000 |
| `R5_MountainRescue__TP07_BurstWindow` | TP07 | 0.0259 | 4815.2 | 6.6667 | 0.0000 |
| `R5_MountainRescue__TP08_HubTarget` | TP08 | 0.0062 | 5558.1 | 21.0000 | 0.0000 |
| `R5_MountainRescue__TP09_Bimodal` | TP09 | 0.0155 | 4278.6 | 6.6667 | 0.0000 |
| `R5_MountainRescue__TP10_Storm` | TP10 | 0.0005 | 2509.7 | 100.0000 | 0.7975 |
| `R5_MountainRescue__TP11_ManyToOne` | TP11 | 0.0000 | — | — | 0.0000 |
| `R5_MountainRescue__TP12_GroupToGroup` | TP12 | 0.0000 | — | — | 0.0000 |
| `R6_SparseLongRange__TP01_Baseline` | TP01 | 0.0433 | 11337.6 | 17.6667 | 0.0000 |
| `R6_SparseLongRange__TP02_LowLoad` | TP02 | 0.0208 | 13154.5 | 35.5000 | 0.0000 |
| `R6_SparseLongRange__TP03_ManySmall` | TP03 | 0.0636 | 10003.0 | 14.5493 | 0.0000 |
| `R6_SparseLongRange__TP04_FewLarge` | TP04 | 0.0330 | 10008.4 | 21.5000 | 0.2747 |
| `R6_SparseLongRange__TP05_CriticalTTL` | TP05 | 0.0021 | 113.6 | 17.0000 | 1.0289 |
| `R6_SparseLongRange__TP06_OneToMany` | TP06 | 0.0969 | 10786.9 | 16.4149 | 0.0794 |
| `R6_SparseLongRange__TP07_BurstWindow` | TP07 | 0.0904 | 9506.8 | 18.3529 | 0.0000 |
| `R6_SparseLongRange__TP08_HubTarget` | TP08 | 0.0670 | 6974.3 | 10.8308 | 0.0000 |
| `R6_SparseLongRange__TP09_Bimodal` | TP09 | 0.0532 | 10966.9 | 14.6129 | 0.0360 |
| `R6_SparseLongRange__TP10_Storm` | TP10 | 0.0099 | 1579.2 | 18.4590 | 1.1005 |
| `R6_SparseLongRange__TP11_ManyToOne` | TP11 | 0.0608 | 6317.3 | 14.5593 | 0.0000 |
| `R6_SparseLongRange__TP12_GroupToGroup` | TP12 | 0.0798 | 10428.3 | 13.6154 | 0.0000 |
| `R7_SparseTinyBuffer__TP01_Baseline` | TP01 | 0.0041 | 7408.2 | 30.0000 | 0.7531 |
| `R7_SparseTinyBuffer__TP02_LowLoad` | TP02 | 0.0103 | 16704.5 | 38.0000 | 0.0000 |
| `R7_SparseTinyBuffer__TP03_ManySmall` | TP03 | 0.0131 | 14303.5 | 30.8276 | 0.1849 |
| `R7_SparseTinyBuffer__TP04_FewLarge` | TP04 | 0.0000 | — | — | 0.0000 |
| `R7_SparseTinyBuffer__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 0.9979 |
| `R7_SparseTinyBuffer__TP06_OneToMany` | TP06 | 0.0000 | — | — | 0.9897 |
| `R7_SparseTinyBuffer__TP07_BurstWindow` | TP07 | 0.0167 | 13671.6 | 10.3333 | 0.7056 |
| `R7_SparseTinyBuffer__TP08_HubTarget` | TP08 | 0.0010 | 12791.5 | 64.0000 | 0.8990 |
| `R7_SparseTinyBuffer__TP09_Bimodal` | TP09 | 0.0052 | 12407.0 | 30.0000 | 0.7734 |
| `R7_SparseTinyBuffer__TP10_Storm` | TP10 | 0.0000 | — | — | 0.9961 |
| `R7_SparseTinyBuffer__TP11_ManyToOne` | TP11 | 0.0000 | — | — | 0.7928 |
| `R7_SparseTinyBuffer__TP12_GroupToGroup` | TP12 | 0.0061 | 6931.9 | 14.0000 | 0.8487 |
| `R8_IntermittentPower__TP01_Baseline` | TP01 | 0.0166 | 10184.0 | 24.2500 | 0.0000 |
| `R8_IntermittentPower__TP02_LowLoad` | TP02 | 0.0000 | — | — | 0.0000 |
| `R8_IntermittentPower__TP03_ManySmall` | TP03 | 0.0140 | 12770.4 | 22.0968 | 0.0000 |
| `R8_IntermittentPower__TP04_FewLarge` | TP04 | 0.0056 | 7492.5 | 51.0000 | 0.0168 |
| `R8_IntermittentPower__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 0.9979 |
| `R8_IntermittentPower__TP06_OneToMany` | TP06 | 0.0258 | 14244.8 | 4.0800 | 0.2340 |
| `R8_IntermittentPower__TP07_BurstWindow` | TP07 | 0.0222 | 16317.1 | 25.2500 | 0.0000 |
| `R8_IntermittentPower__TP08_HubTarget` | TP08 | 0.0165 | 18324.8 | 23.3125 | 0.0000 |
| `R8_IntermittentPower__TP09_Bimodal` | TP09 | 0.0191 | 9985.6 | 17.6364 | 0.0000 |
| `R8_IntermittentPower__TP10_Storm` | TP10 | 0.0011 | 1898.6 | 52.4286 | 0.9769 |
| `R8_IntermittentPower__TP11_ManyToOne` | TP11 | 0.0186 | 16742.4 | 18.8333 | 0.0000 |
| `R8_IntermittentPower__TP12_GroupToGroup` | TP12 | 0.0102 | 8123.1 | 41.4000 | 0.0000 |
| `R9_ExtremeRange_200m__TP01_Baseline` | TP01 | 0.8571 | 6692.4 | 37.6936 | 0.0000 |
| `R9_ExtremeRange_200m__TP02_LowLoad` | TP02 | 0.8333 | 6571.0 | 39.2625 | 0.0000 |
| `R9_ExtremeRange_200m__TP03_ManySmall` | TP03 | 0.8584 | 6578.8 | 37.9424 | 0.0000 |
| `R9_ExtremeRange_200m__TP04_FewLarge` | TP04 | 0.3017 | 8075.8 | 190.7963 | 54.2179 |
| `R9_ExtremeRange_200m__TP05_CriticalTTL` | TP05 | 0.0126 | 103.4 | 37.0000 | 1.4517 |
| `R9_ExtremeRange_200m__TP06_OneToMany` | TP06 | 0.8598 | 5980.4 | 39.9808 | 2.1443 |
| `R9_ExtremeRange_200m__TP07_BurstWindow` | TP07 | 1.0000 | 6895.6 | 38.0000 | 0.0000 |
| `R9_ExtremeRange_200m__TP08_HubTarget` | TP08 | 0.7072 | 6686.6 | 187.7259 | 113.5567 |
| `R9_ExtremeRange_200m__TP09_Bimodal` | TP09 | 0.6272 | 7515.2 | 217.3917 | 120.6829 |
| `R9_ExtremeRange_200m__TP10_Storm` | TP10 | 0.1664 | 2052.9 | 37.3493 | 6.8438 |
| `R9_ExtremeRange_200m__TP11_ManyToOne` | TP11 | 0.8691 | 6692.7 | 39.3938 | 1.8031 |
| `R9_ExtremeRange_200m__TP12_GroupToGroup` | TP12 | 0.8630 | 6460.5 | 38.0474 | 0.0000 |
| `S1_StrongCommunities_SeparateClusters__TP01_Baseline` | TP01 | 0.2403 | 982.3 | 107.9831 | 0.0000 |
| `S1_StrongCommunities_SeparateClusters__TP02_LowLoad` | TP02 | 0.1443 | 850.3 | 176.7143 | 0.0000 |
| `S1_StrongCommunities_SeparateClusters__TP03_ManySmall` | TP03 | — | — | — | — |
| `S1_StrongCommunities_SeparateClusters__TP04_FewLarge` | TP04 | 0.1500 | 961.1 | 27734.4074 | 4150.5722 |
| `S1_StrongCommunities_SeparateClusters__TP05_CriticalTTL` | TP05 | 0.0570 | 10.9 | 126.3571 | 8.0896 |
| `S1_StrongCommunities_SeparateClusters__TP06_OneToMany` | TP06 | 0.2608 | 1191.2 | 184.6166 | 21.5639 |
| `S1_StrongCommunities_SeparateClusters__TP07_BurstWindow` | TP07 | 0.2398 | 905.1 | 109.8750 | 0.0000 |
| `S1_StrongCommunities_SeparateClusters__TP08_HubTarget` | TP08 | 0.1897 | 1195.6 | 134.3315 | 0.0000 |
| `S1_StrongCommunities_SeparateClusters__TP09_Bimodal` | TP09 | 0.2160 | 1046.9 | 5784.4803 | 1230.3520 |
| `S1_StrongCommunities_SeparateClusters__TP10_Storm` | TP10 | 0.2473 | 921.8 | 103.6955 | 25.0134 |
| `S1_StrongCommunities_SeparateClusters__TP11_ManyToOne` | TP11 | 0.2608 | 1112.2 | 98.3676 | 0.0000 |
| `S1_StrongCommunities_SeparateClusters__TP12_GroupToGroup` | TP12 | 0.0000 | — | — | 0.0000 |
| `S2_WeakCommunities_HighMixing__TP01_Baseline` | TP01 | 0.6132 | 13103.9 | 88.2483 | 14.8292 |
| `S2_WeakCommunities_HighMixing__TP02_LowLoad` | TP02 | 0.6771 | 12619.8 | 77.0154 | 0.0000 |
| `S2_WeakCommunities_HighMixing__TP03_ManySmall` | TP03 | 0.4094 | 15550.4 | 44.8958 | 0.0000 |
| `S2_WeakCommunities_HighMixing__TP04_FewLarge` | TP04 | 0.2291 | 14693.6 | 70.0976 | 12.7765 |
| `S2_WeakCommunities_HighMixing__TP05_CriticalTTL` | TP05 | 0.0041 | 131.0 | 21.0000 | 1.0823 |
| `S2_WeakCommunities_HighMixing__TP06_OneToMany` | TP06 | 0.4021 | 15181.4 | 67.9718 | 1.5216 |
| `S2_WeakCommunities_HighMixing__TP07_BurstWindow` | TP07 | 0.9231 | 16799.1 | 91.1935 | 31.2885 |
| `S2_WeakCommunities_HighMixing__TP08_HubTarget` | TP08 | 0.4588 | 12659.5 | 91.4337 | 23.0402 |
| `S2_WeakCommunities_HighMixing__TP09_Bimodal` | TP09 | 0.3540 | 14072.9 | 75.2621 | 16.9124 |
| `S2_WeakCommunities_HighMixing__TP10_Storm` | TP10 | 0.0305 | 2091.1 | 64.1596 | 2.8297 |
| `S2_WeakCommunities_HighMixing__TP11_ManyToOne` | TP11 | 0.5082 | 14066.8 | 76.6369 | 5.6784 |
| `S2_WeakCommunities_HighMixing__TP12_GroupToGroup` | TP12 | 0.6033 | 12151.6 | 93.0780 | 18.1350 |
| `S3_PeriodicMeetings_RegularRhythm__TP01_Baseline` | TP01 | 0.1408 | 23017.9 | 51.7313 | 0.0000 |
| `S3_PeriodicMeetings_RegularRhythm__TP02_LowLoad` | TP02 | 0.1875 | 22116.7 | 45.8333 | 0.0000 |
| `S3_PeriodicMeetings_RegularRhythm__TP03_ManySmall` | TP03 | 0.1602 | 19692.5 | 33.8814 | 0.0000 |
| `S3_PeriodicMeetings_RegularRhythm__TP04_FewLarge` | TP04 | 0.0829 | 22194.1 | 40.4000 | 1.4696 |
| `S3_PeriodicMeetings_RegularRhythm__TP05_CriticalTTL` | TP05 | 0.0021 | 142.9 | 17.0000 | 1.0315 |
| `S3_PeriodicMeetings_RegularRhythm__TP06_OneToMany` | TP06 | 0.1113 | 22446.6 | 36.3519 | 0.3052 |
| `S3_PeriodicMeetings_RegularRhythm__TP07_BurstWindow` | TP07 | 0.2571 | 21377.3 | 47.6667 | 0.0000 |
| `S3_PeriodicMeetings_RegularRhythm__TP08_HubTarget` | TP08 | 0.1804 | 22499.6 | 31.8114 | 0.0000 |
| `S3_PeriodicMeetings_RegularRhythm__TP09_Bimodal` | TP09 | 0.1191 | 20269.8 | 37.9853 | 0.5832 |
| `S3_PeriodicMeetings_RegularRhythm__TP10_Storm` | TP10 | 0.0109 | 1967.2 | 35.6567 | 1.2894 |
| `S3_PeriodicMeetings_RegularRhythm__TP11_ManyToOne` | TP11 | 0.0186 | 9577.2 | 320.2222 | 0.0000 |
| `S3_PeriodicMeetings_RegularRhythm__TP12_GroupToGroup` | TP12 | 0.1554 | 19684.8 | 46.3289 | 0.0000 |
| `S4_RandomMixing_NoHotspots__TP01_Baseline` | TP01 | 0.0379 | 19990.8 | 61.3889 | 0.0000 |
| `S4_RandomMixing_NoHotspots__TP02_LowLoad` | TP02 | 0.0316 | 17332.1 | 70.6667 | 0.0000 |
| `S4_RandomMixing_NoHotspots__TP03_ManySmall` | TP03 | 0.0371 | 18159.6 | 54.0610 | 0.0000 |
| `S4_RandomMixing_NoHotspots__TP04_FewLarge` | TP04 | 0.0387 | 12254.7 | 31.2857 | 0.6851 |
| `S4_RandomMixing_NoHotspots__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0063 |
| `S4_RandomMixing_NoHotspots__TP06_OneToMany` | TP06 | 0.0165 | 6228.9 | 53.6250 | 0.6711 |
| `S4_RandomMixing_NoHotspots__TP07_BurstWindow` | TP07 | 0.0780 | 20427.7 | 46.2500 | 0.0000 |
| `S4_RandomMixing_NoHotspots__TP08_HubTarget` | TP08 | 0.0454 | 19827.6 | 54.6591 | 0.0691 |
| `S4_RandomMixing_NoHotspots__TP09_Bimodal` | TP09 | 0.0334 | 16172.8 | 54.9474 | 0.3779 |
| `S4_RandomMixing_NoHotspots__TP10_Storm` | TP10 | 0.0042 | 1709.6 | 51.0000 | 1.1285 |
| `S4_RandomMixing_NoHotspots__TP11_ManyToOne` | TP11 | 0.1598 | 22705.8 | 14.6387 | 0.0000 |
| `S4_RandomMixing_NoHotspots__TP12_GroupToGroup` | TP12 | 0.0286 | 17860.1 | 78.7143 | 0.0000 |
| `S5_TwoLayer_StudentsStaff__TP01_Baseline` | TP01 | 0.3417 | 19147.0 | 59.5183 | 0.0000 |
| `S5_TwoLayer_StudentsStaff__TP02_LowLoad` | TP02 | 0.4632 | 16630.4 | 64.5909 | 0.0000 |
| `S5_TwoLayer_StudentsStaff__TP03_ManySmall` | TP03 | 0.2127 | 19015.2 | 32.2585 | 0.0000 |
| `S5_TwoLayer_StudentsStaff__TP04_FewLarge` | TP04 | 0.1436 | 18690.2 | 39.1923 | 0.7182 |
| `S5_TwoLayer_StudentsStaff__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0437 |
| `S5_TwoLayer_StudentsStaff__TP06_OneToMany` | TP06 | 0.1526 | 18831.0 | 46.6284 | 0.0794 |
| `S5_TwoLayer_StudentsStaff__TP07_BurstWindow` | TP07 | 0.5822 | 19240.4 | 56.1053 | 0.0000 |
| `S5_TwoLayer_StudentsStaff__TP08_HubTarget` | TP08 | 0.2763 | 18915.2 | 47.3881 | 0.0000 |
| `S5_TwoLayer_StudentsStaff__TP09_Bimodal` | TP09 | 0.2243 | 19734.8 | 38.1473 | 0.2017 |
| `S5_TwoLayer_StudentsStaff__TP10_Storm` | TP10 | 0.0112 | 1926.4 | 70.5507 | 1.6924 |
| `S5_TwoLayer_StudentsStaff__TP11_ManyToOne` | TP11 | 0.2454 | 22394.7 | 55.9622 | 0.0000 |
| `S5_TwoLayer_StudentsStaff__TP12_GroupToGroup` | TP12 | 0.2924 | 18588.3 | 72.9790 | 0.0000 |
| `S6_FamilyGroups_SmallPersistent__TP01_Baseline` | TP01 | 0.0595 | 1372.4 | 40.6552 | 0.0000 |
| `S6_FamilyGroups_SmallPersistent__TP02_LowLoad` | TP02 | 0.0737 | 2512.8 | 33.0000 | 0.0000 |
| `S6_FamilyGroups_SmallPersistent__TP03_ManySmall` | TP03 | 0.0646 | 1578.8 | 37.7310 | 0.0000 |
| `S6_FamilyGroups_SmallPersistent__TP04_FewLarge` | TP04 | 0.0497 | 2161.7 | 63.8889 | 0.9392 |
| `S6_FamilyGroups_SmallPersistent__TP05_CriticalTTL` | TP05 | 0.0205 | 113.4 | 38.7000 | 1.7844 |
| `S6_FamilyGroups_SmallPersistent__TP06_OneToMany` | TP06 | 0.0742 | 2018.9 | 45.6806 | 0.7608 |
| `S6_FamilyGroups_SmallPersistent__TP07_BurstWindow` | TP07 | 0.0640 | 1596.1 | 39.2083 | 0.0000 |
| `S6_FamilyGroups_SmallPersistent__TP08_HubTarget` | TP08 | 0.0134 | 1762.9 | 178.8462 | 0.0000 |
| `S6_FamilyGroups_SmallPersistent__TP09_Bimodal` | TP09 | 0.0639 | 1560.4 | 37.2162 | 0.0000 |
| `S6_FamilyGroups_SmallPersistent__TP10_Storm` | TP10 | 0.0542 | 1115.3 | 38.0478 | 2.8532 |
| `S6_FamilyGroups_SmallPersistent__TP11_ManyToOne` | TP11 | 0.0660 | 2304.2 | 36.0781 | 0.0000 |
| `S6_FamilyGroups_SmallPersistent__TP12_GroupToGroup` | TP12 | 0.0000 | — | — | 0.0000 |
| `T10_HighRateLowSpeed_Congestion__TP01_Baseline` | TP01 | 0.0228 | 15815.8 | 48.7273 | 0.0000 |
| `T10_HighRateLowSpeed_Congestion__TP02_LowLoad` | TP02 | 0.0105 | 30587.2 | 124.0000 | 0.0000 |
| `T10_HighRateLowSpeed_Congestion__TP03_ManySmall` | TP03 | 0.0277 | 13543.0 | 31.3065 | 0.0000 |
| `T10_HighRateLowSpeed_Congestion__TP04_FewLarge` | TP04 | 0.0110 | 18683.5 | 21.5000 | 0.0552 |
| `T10_HighRateLowSpeed_Congestion__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0062 |
| `T10_HighRateLowSpeed_Congestion__TP06_OneToMany` | TP06 | 0.0340 | 8163.3 | 14.4242 | 0.6381 |
| `T10_HighRateLowSpeed_Congestion__TP07_BurstWindow` | TP07 | 0.0440 | 12835.8 | 42.3125 | 0.0000 |
| `T10_HighRateLowSpeed_Congestion__TP08_HubTarget` | TP08 | 0.0186 | 13081.4 | 48.3889 | 0.0000 |
| `T10_HighRateLowSpeed_Congestion__TP09_Bimodal` | TP09 | 0.0242 | 14024.2 | 20.2143 | 0.0138 |
| `T10_HighRateLowSpeed_Congestion__TP10_Storm` | TP10 | 0.0034 | 1705.1 | 25.5714 | 1.0050 |
| `T10_HighRateLowSpeed_Congestion__TP11_ManyToOne` | TP11 | 0.0330 | 14423.4 | 29.1875 | 0.0000 |
| `T10_HighRateLowSpeed_Congestion__TP12_GroupToGroup` | TP12 | 0.0204 | 9072.9 | 58.2000 | 0.0000 |
| `T11_TTL_1min__TP01_Baseline` | TP01 | 0.4884 | 8288.9 | 68.9437 | 28.3658 |
| `T11_TTL_1min__TP02_LowLoad` | TP02 | 0.7813 | 8579.0 | 28.3867 | 0.0000 |
| `T11_TTL_1min__TP03_ManySmall` | TP03 | 0.5954 | 11559.0 | 15.6103 | 0.0000 |
| `T11_TTL_1min__TP04_FewLarge` | TP04 | 0.2011 | 8316.0 | 26.5278 | 5.7207 |
| `T11_TTL_1min__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.1311 |
| `T11_TTL_1min__TP06_OneToMany` | TP06 | 0.5814 | 8983.6 | 31.5603 | 13.8608 |
| `T11_TTL_1min__TP07_BurstWindow` | TP07 | 0.8412 | 9876.0 | 50.8146 | 35.6518 |
| `T11_TTL_1min__TP08_HubTarget` | TP08 | 0.3649 | 8323.1 | 48.1384 | 15.5670 |
| `T11_TTL_1min__TP09_Bimodal` | TP09 | 0.3947 | 8768.3 | 50.6044 | 16.9000 |
| `T11_TTL_1min__TP10_Storm` | TP10 | 0.0847 | 1923.1 | 25.2457 | 3.0185 |
| `T11_TTL_1min__TP11_ManyToOne` | TP11 | 0.5495 | 8005.0 | 33.2758 | 13.8773 |
| `T11_TTL_1min__TP12_GroupToGroup` | TP12 | 0.5092 | 8845.2 | 62.1446 | 26.7342 |
| `T12_TTL_Infinite_Buffer200M__TP01_Baseline` | TP01 | 0.0308 | 16210.9 | 50.0000 | 0.0000 |
| `T12_TTL_Infinite_Buffer200M__TP02_LowLoad` | TP02 | 0.0105 | 1440.8 | 143.0000 | 0.0000 |
| `T12_TTL_Infinite_Buffer200M__TP03_ManySmall` | TP03 | 0.0339 | 15852.4 | 33.1711 | 0.0000 |
| `T12_TTL_Infinite_Buffer200M__TP04_FewLarge` | TP04 | 0.0110 | 10021.2 | 88.0000 | 0.0000 |
| `T12_TTL_Infinite_Buffer200M__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0021 |
| `T12_TTL_Infinite_Buffer200M__TP06_OneToMany` | TP06 | 0.0660 | 11911.5 | 16.7031 | 0.0000 |
| `T12_TTL_Infinite_Buffer200M__TP07_BurstWindow` | TP07 | 0.0613 | 13862.0 | 44.1304 | 0.0000 |
| `T12_TTL_Infinite_Buffer200M__TP08_HubTarget` | TP08 | 0.0433 | 15548.7 | 33.1905 | 0.0000 |
| `T12_TTL_Infinite_Buffer200M__TP09_Bimodal` | TP09 | 0.0380 | 14673.0 | 33.6364 | 0.0000 |
| `T12_TTL_Infinite_Buffer200M__TP10_Storm` | TP10 | 0.0042 | 2259.1 | 31.3462 | 1.0440 |
| `T12_TTL_Infinite_Buffer200M__TP11_ManyToOne` | TP11 | 0.0619 | 15891.6 | 20.4000 | 0.0000 |
| `T12_TTL_Infinite_Buffer200M__TP12_GroupToGroup` | TP12 | 0.0204 | 14156.7 | 52.9000 | 0.0000 |
| `T13_Buffer_256k__TP01_Baseline` | TP01 | 0.0021 | 1071.9 | 20.0000 | 0.9049 |
| `T13_Buffer_256k__TP02_LowLoad` | TP02 | 0.0104 | 4063.5 | 21.0000 | 0.2083 |
| `T13_Buffer_256k__TP03_ManySmall` | TP03 | 0.0110 | 9890.5 | 11.7917 | 0.4865 |
| `T13_Buffer_256k__TP04_FewLarge` | TP04 | 0.0000 | — | — | 0.0000 |
| `T13_Buffer_256k__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 0.9979 |
| `T13_Buffer_256k__TP06_OneToMany` | TP06 | 0.0010 | 107.5 | 18.0000 | 0.9959 |
| `T13_Buffer_256k__TP07_BurstWindow` | TP07 | 0.0056 | 6686.2 | 7.0000 | 0.8635 |
| `T13_Buffer_256k__TP08_HubTarget` | TP08 | 0.0031 | 1054.3 | 7.0000 | 0.9526 |
| `T13_Buffer_256k__TP09_Bimodal` | TP09 | 0.0018 | 1071.9 | 36.0000 | 0.8561 |
| `T13_Buffer_256k__TP10_Storm` | TP10 | 0.0000 | — | — | 0.9925 |
| `T13_Buffer_256k__TP11_ManyToOne` | TP11 | 0.0165 | 3546.4 | 2.0625 | 0.9103 |
| `T13_Buffer_256k__TP12_GroupToGroup` | TP12 | 0.0000 | — | — | 0.9611 |
| `T14_Buffer_200M__TP01_Baseline` | TP01 | 0.1813 | 20764.0 | 37.4023 | 0.0000 |
| `T14_Buffer_200M__TP02_LowLoad` | TP02 | 0.2000 | 18171.1 | 46.7895 | 0.0000 |
| `T14_Buffer_200M__TP03_ManySmall` | TP03 | 0.1423 | 19009.6 | 28.8418 | 0.0000 |
| `T14_Buffer_200M__TP04_FewLarge` | TP04 | 0.1236 | 19239.0 | 11.6818 | 0.0000 |
| `T14_Buffer_200M__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0208 |
| `T14_Buffer_200M__TP06_OneToMany` | TP06 | 0.0485 | 20764.7 | 11.1489 | 0.0000 |
| `T14_Buffer_200M__TP07_BurstWindow` | TP07 | 0.2918 | 22623.7 | 35.4466 | 0.0000 |
| `T14_Buffer_200M__TP08_HubTarget` | TP08 | 0.2144 | 22086.2 | 22.7692 | 0.0000 |
| `T14_Buffer_200M__TP09_Bimodal` | TP09 | 0.1272 | 20575.4 | 24.1370 | 0.0000 |
| `T14_Buffer_200M__TP10_Storm` | TP10 | 0.0105 | 1784.2 | 34.0462 | 1.2626 |
| `T14_Buffer_200M__TP11_ManyToOne` | TP11 | 0.2474 | 27272.8 | 24.9792 | 0.0000 |
| `T14_Buffer_200M__TP12_GroupToGroup` | TP12 | 0.2045 | 20208.8 | 34.9000 | 0.0000 |
| `T15_TransmitSpeed_256k__TP01_Baseline` | TP01 | 0.2669 | 15952.6 | 10.9923 | 0.0000 |
| `T15_TransmitSpeed_256k__TP02_LowLoad` | TP02 | 0.4421 | 16975.7 | 35.7143 | 0.0000 |
| `T15_TransmitSpeed_256k__TP03_ManySmall` | TP03 | 0.2568 | 15954.6 | 11.2153 | 0.0000 |
| `T15_TransmitSpeed_256k__TP04_FewLarge` | TP04 | 0.0110 | 17837.8 | 7.5000 | 0.0000 |
| `T15_TransmitSpeed_256k__TP05_CriticalTTL` | TP05 | 0.0021 | 45.3 | 30.0000 | 1.0534 |
| `T15_TransmitSpeed_256k__TP06_OneToMany` | TP06 | 0.1062 | 15250.0 | 15.0680 | 0.0794 |
| `T15_TransmitSpeed_256k__TP07_BurstWindow` | TP07 | 0.4347 | 19807.5 | 9.0552 | 0.0000 |
| `T15_TransmitSpeed_256k__TP08_HubTarget` | TP08 | 0.2072 | 15323.4 | 8.2886 | 0.0000 |
| `T15_TransmitSpeed_256k__TP09_Bimodal` | TP09 | 0.2124 | 15824.1 | 14.2439 | 0.0000 |
| `T15_TransmitSpeed_256k__TP10_Storm` | TP10 | 0.0168 | 1842.6 | 5.7981 | 1.0141 |
| `T15_TransmitSpeed_256k__TP11_ManyToOne` | TP11 | 0.0907 | 14693.1 | 34.6250 | 0.0000 |
| `T15_TransmitSpeed_256k__TP12_GroupToGroup` | TP12 | 0.2311 | 16561.5 | 12.1947 | 0.0000 |
| `T1_ManySmallMsgs_HighRate__TP01_Baseline` | TP01 | 0.0607 | 18240.1 | 44.3793 | 0.0000 |
| `T1_ManySmallMsgs_HighRate__TP02_LowLoad` | TP02 | 0.0722 | 20831.5 | 31.8571 | 0.0000 |
| `T1_ManySmallMsgs_HighRate__TP03_ManySmall` | TP03 | 0.0583 | 20758.6 | 23.0538 | 0.0000 |
| `T1_ManySmallMsgs_HighRate__TP04_FewLarge` | TP04 | 0.0331 | 14530.8 | 22.0000 | 0.9061 |
| `T1_ManySmallMsgs_HighRate__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0021 |
| `T1_ManySmallMsgs_HighRate__TP06_OneToMany` | TP06 | 0.0485 | 18040.4 | 22.2128 | 0.7814 |
| `T1_ManySmallMsgs_HighRate__TP07_BurstWindow` | TP07 | 0.0989 | 21039.3 | 30.9459 | 0.2460 |
| `T1_ManySmallMsgs_HighRate__TP08_HubTarget` | TP08 | 0.0732 | 19962.0 | 20.5775 | 0.1588 |
| `T1_ManySmallMsgs_HighRate__TP09_Bimodal` | TP09 | 0.0417 | 13142.9 | 36.1250 | 0.8212 |
| `T1_ManySmallMsgs_HighRate__TP10_Storm` | TP10 | 0.0032 | 1926.7 | 58.5000 | 1.0952 |
| `T1_ManySmallMsgs_HighRate__TP11_ManyToOne` | TP11 | 0.0340 | 10809.9 | 53.6061 | 0.0670 |
| `T1_ManySmallMsgs_HighRate__TP12_GroupToGroup` | TP12 | 0.0777 | 21168.0 | 30.5526 | 0.1800 |
| `T2_FewHugeMsgs_LowRate__TP01_Baseline` | TP01 | 0.0349 | 24552.2 | 52.0588 | 0.0000 |
| `T2_FewHugeMsgs_LowRate__TP02_LowLoad` | TP02 | 0.0722 | 21683.2 | 25.8571 | 0.0000 |
| `T2_FewHugeMsgs_LowRate__TP03_ManySmall` | TP03 | 0.0415 | 20458.0 | 36.0109 | 0.0000 |
| `T2_FewHugeMsgs_LowRate__TP04_FewLarge` | TP04 | 0.0449 | 20922.5 | 28.6250 | 0.0562 |
| `T2_FewHugeMsgs_LowRate__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0041 |
| `T2_FewHugeMsgs_LowRate__TP06_OneToMany` | TP06 | 0.0000 | — | — | 0.0794 |
| `T2_FewHugeMsgs_LowRate__TP07_BurstWindow` | TP07 | 0.0496 | 23372.9 | 56.3889 | 0.0000 |
| `T2_FewHugeMsgs_LowRate__TP08_HubTarget` | TP08 | 0.0412 | 16963.3 | 42.6000 | 0.0000 |
| `T2_FewHugeMsgs_LowRate__TP09_Bimodal` | TP09 | 0.0343 | 23913.8 | 43.0500 | 0.0000 |
| `T2_FewHugeMsgs_LowRate__TP10_Storm` | TP10 | 0.0032 | 2005.0 | 54.1000 | 1.0849 |
| `T2_FewHugeMsgs_LowRate__TP11_ManyToOne` | TP11 | 0.0000 | — | — | 0.0000 |
| `T2_FewHugeMsgs_LowRate__TP12_GroupToGroup` | TP12 | 0.0409 | 16090.3 | 42.3000 | 0.0000 |
| `T3_MixedBimodal_SmallAndLarge__TP01_Baseline` | TP01 | 0.0370 | 17717.1 | 43.1111 | 0.0000 |
| `T3_MixedBimodal_SmallAndLarge__TP02_LowLoad` | TP02 | 0.0309 | 16126.6 | 38.0000 | 0.0000 |
| `T3_MixedBimodal_SmallAndLarge__TP03_ManySmall` | TP03 | 0.0316 | 16426.7 | 38.7571 | 0.0000 |
| `T3_MixedBimodal_SmallAndLarge__TP04_FewLarge` | TP04 | 0.0281 | 18094.5 | 38.6000 | 0.0056 |
| `T3_MixedBimodal_SmallAndLarge__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0021 |
| `T3_MixedBimodal_SmallAndLarge__TP06_OneToMany` | TP06 | 0.0691 | 19263.4 | 16.8060 | 0.0794 |
| `T3_MixedBimodal_SmallAndLarge__TP07_BurstWindow` | TP07 | 0.0606 | 18850.7 | 39.3182 | 0.0000 |
| `T3_MixedBimodal_SmallAndLarge__TP08_HubTarget` | TP08 | 0.0361 | 15529.4 | 43.4000 | 0.0000 |
| `T3_MixedBimodal_SmallAndLarge__TP09_Bimodal` | TP09 | 0.0343 | 17614.9 | 39.6500 | 0.0000 |
| `T3_MixedBimodal_SmallAndLarge__TP10_Storm` | TP10 | 0.0037 | 1745.1 | 42.5217 | 1.0676 |
| `T3_MixedBimodal_SmallAndLarge__TP11_ManyToOne` | TP11 | 0.0309 | 16002.5 | 52.5333 | 0.0000 |
| `T3_MixedBimodal_SmallAndLarge__TP12_GroupToGroup` | TP12 | 0.0429 | 10977.9 | 47.0476 | 0.0000 |
| `T4_VeryShortTtl_5to10min__TP01_Baseline` | TP01 | 0.0062 | 4991.2 | 24.5000 | 0.0000 |
| `T4_VeryShortTtl_5to10min__TP02_LowLoad` | TP02 | 0.0000 | — | — | 0.0000 |
| `T4_VeryShortTtl_5to10min__TP03_ManySmall` | TP03 | 0.0053 | 6134.3 | 32.3750 | 0.0000 |
| `T4_VeryShortTtl_5to10min__TP04_FewLarge` | TP04 | 0.0000 | — | — | 0.4118 |
| `T4_VeryShortTtl_5to10min__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0000 |
| `T4_VeryShortTtl_5to10min__TP06_OneToMany` | TP06 | 0.0000 | — | — | 0.7842 |
| `T4_VeryShortTtl_5to10min__TP07_BurstWindow` | TP07 | 0.0082 | 6598.8 | 28.5000 | 0.0000 |
| `T4_VeryShortTtl_5to10min__TP08_HubTarget` | TP08 | 0.0031 | 4141.1 | 50.5000 | 0.0000 |
| `T4_VeryShortTtl_5to10min__TP09_Bimodal` | TP09 | 0.0052 | 4991.2 | 27.5000 | 0.0699 |
| `T4_VeryShortTtl_5to10min__TP10_Storm` | TP10 | 0.0012 | 1746.9 | 40.0000 | 0.9252 |
| `T4_VeryShortTtl_5to10min__TP11_ManyToOne` | TP11 | 0.0000 | — | — | 0.0000 |
| `T4_VeryShortTtl_5to10min__TP12_GroupToGroup` | TP12 | 0.0031 | 6067.1 | 45.0000 | 0.0000 |
| `T5_VeryLongTtl_6to24h__TP01_Baseline` | TP01 | 0.1071 | 21970.2 | 40.6275 | 0.0000 |
| `T5_VeryLongTtl_6to24h__TP02_LowLoad` | TP02 | 0.1042 | 24886.3 | 45.8000 | 0.0000 |
| `T5_VeryLongTtl_6to24h__TP03_ManySmall` | TP03 | 0.0917 | 19500.9 | 30.1520 | 0.0000 |
| `T5_VeryLongTtl_6to24h__TP04_FewLarge` | TP04 | 0.0838 | 20140.0 | 28.0000 | 0.5084 |
| `T5_VeryLongTtl_6to24h__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0105 |
| `T5_VeryLongTtl_6to24h__TP06_OneToMany` | TP06 | 0.1010 | 20637.5 | 26.2653 | 0.0433 |
| `T5_VeryLongTtl_6to24h__TP07_BurstWindow` | TP07 | 0.1662 | 23782.0 | 39.9000 | 0.0000 |
| `T5_VeryLongTtl_6to24h__TP08_HubTarget` | TP08 | 0.1124 | 24865.8 | 32.9725 | 0.0000 |
| `T5_VeryLongTtl_6to24h__TP09_Bimodal` | TP09 | 0.0871 | 20495.3 | 31.4800 | 0.1760 |
| `T5_VeryLongTtl_6to24h__TP10_Storm` | TP10 | 0.0076 | 1682.2 | 33.9574 | 1.1674 |
| `T5_VeryLongTtl_6to24h__TP11_ManyToOne` | TP11 | 0.2557 | 23810.7 | 13.7016 | 0.0000 |
| `T5_VeryLongTtl_6to24h__TP12_GroupToGroup` | TP12 | 0.1166 | 22106.4 | 38.6667 | 0.0000 |
| `T6_UniformSources_RandomFromTo__TP01_Baseline` | TP01 | 0.0329 | 12973.0 | 31.6250 | 0.0000 |
| `T6_UniformSources_RandomFromTo__TP02_LowLoad` | TP02 | 0.0316 | 19386.3 | 41.6667 | 0.0000 |
| `T6_UniformSources_RandomFromTo__TP03_ManySmall` | TP03 | 0.0250 | 15599.2 | 32.9643 | 0.0000 |
| `T6_UniformSources_RandomFromTo__TP04_FewLarge` | TP04 | 0.0276 | 20112.9 | 29.6000 | 0.0000 |
| `T6_UniformSources_RandomFromTo__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0041 |
| `T6_UniformSources_RandomFromTo__TP06_OneToMany` | TP06 | 0.0412 | 15445.5 | 8.3500 | 0.0000 |
| `T6_UniformSources_RandomFromTo__TP07_BurstWindow` | TP07 | 0.0453 | 20752.7 | 41.4118 | 0.0000 |
| `T6_UniformSources_RandomFromTo__TP08_HubTarget` | TP08 | 0.0351 | 20615.6 | 28.9118 | 0.0000 |
| `T6_UniformSources_RandomFromTo__TP09_Bimodal` | TP09 | 0.0328 | 12230.7 | 25.1053 | 0.0000 |
| `T6_UniformSources_RandomFromTo__TP10_Storm` | TP10 | 0.0036 | 1807.0 | 33.3182 | 1.0332 |
| `T6_UniformSources_RandomFromTo__TP11_ManyToOne` | TP11 | 0.0361 | 20656.6 | 25.3143 | 0.0000 |
| `T6_UniformSources_RandomFromTo__TP12_GroupToGroup` | TP12 | 0.0409 | 15181.2 | 21.2000 | 0.0000 |
| `T7_TargetedToHubs_FewDestinations__TP01_Baseline` | TP01 | 0.0534 | 15688.4 | 33.1538 | 0.0000 |
| `T7_TargetedToHubs_FewDestinations__TP02_LowLoad` | TP02 | 0.0309 | 8428.5 | 59.6667 | 0.0000 |
| `T7_TargetedToHubs_FewDestinations__TP03_ManySmall` | TP03 | 0.0393 | 18610.7 | 35.1839 | 0.0000 |
| `T7_TargetedToHubs_FewDestinations__TP04_FewLarge` | TP04 | 0.0337 | 16697.5 | 35.6667 | 0.0674 |
| `T7_TargetedToHubs_FewDestinations__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0082 |
| `T7_TargetedToHubs_FewDestinations__TP06_OneToMany` | TP06 | 0.0155 | 18026.0 | 5.1333 | 0.0794 |
| `T7_TargetedToHubs_FewDestinations__TP07_BurstWindow` | TP07 | 0.0964 | 18508.5 | 34.6000 | 0.0000 |
| `T7_TargetedToHubs_FewDestinations__TP08_HubTarget` | TP08 | 0.0598 | 17100.1 | 30.4655 | 0.0000 |
| `T7_TargetedToHubs_FewDestinations__TP09_Bimodal` | TP09 | 0.0446 | 15768.4 | 29.7308 | 0.0000 |
| `T7_TargetedToHubs_FewDestinations__TP10_Storm` | TP10 | 0.0041 | 1716.4 | 41.6400 | 1.0801 |
| `T7_TargetedToHubs_FewDestinations__TP11_ManyToOne` | TP11 | 0.0948 | 20758.1 | 18.6196 | 0.0000 |
| `T7_TargetedToHubs_FewDestinations__TP12_GroupToGroup` | TP12 | 0.0327 | 14918.3 | 44.4375 | 0.0000 |
| `T8_BurstTraffic_TimeWindows__TP01_Baseline` | TP01 | 0.0452 | 16899.2 | 31.4545 | 0.0000 |
| `T8_BurstTraffic_TimeWindows__TP02_LowLoad` | TP02 | 0.0103 | 9585.6 | 121.0000 | 0.0000 |
| `T8_BurstTraffic_TimeWindows__TP03_ManySmall` | TP03 | 0.0402 | 16741.0 | 32.8764 | 0.0000 |
| `T8_BurstTraffic_TimeWindows__TP04_FewLarge` | TP04 | 0.0393 | 17966.3 | 24.5714 | 0.0000 |
| `T8_BurstTraffic_TimeWindows__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0062 |
| `T8_BurstTraffic_TimeWindows__TP06_OneToMany` | TP06 | 0.0351 | 18908.2 | 13.1176 | 0.0000 |
| `T8_BurstTraffic_TimeWindows__TP07_BurstWindow` | TP07 | 0.0716 | 19992.1 | 37.7692 | 0.0000 |
| `T8_BurstTraffic_TimeWindows__TP08_HubTarget` | TP08 | 0.0412 | 16574.5 | 31.9000 | 0.0000 |
| `T8_BurstTraffic_TimeWindows__TP09_Bimodal` | TP09 | 0.0377 | 16926.2 | 30.6818 | 0.0000 |
| `T8_BurstTraffic_TimeWindows__TP10_Storm` | TP10 | 0.0021 | 2084.2 | 70.8462 | 1.0642 |
| `T8_BurstTraffic_TimeWindows__TP11_ManyToOne` | TP11 | 0.0381 | 14609.9 | 36.5405 | 0.0000 |
| `T8_BurstTraffic_TimeWindows__TP12_GroupToGroup` | TP12 | 0.0348 | 19447.9 | 42.0000 | 0.0000 |
| `T9_BufferStress_SmallBufferHighTraffic__TP01_Baseline` | TP01 | 0.0166 | 24833.1 | 59.3750 | 0.0290 |
| `T9_BufferStress_SmallBufferHighTraffic__TP02_LowLoad` | TP02 | 0.0211 | 36505.8 | 45.5000 | 0.0000 |
| `T9_BufferStress_SmallBufferHighTraffic__TP03_ManySmall` | TP03 | 0.0206 | 16533.2 | 36.3043 | 0.0000 |
| `T9_BufferStress_SmallBufferHighTraffic__TP04_FewLarge` | TP04 | 0.0000 | — | — | 0.7790 |
| `T9_BufferStress_SmallBufferHighTraffic__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.0021 |
| `T9_BufferStress_SmallBufferHighTraffic__TP06_OneToMany` | TP06 | 0.0000 | — | — | 0.9247 |
| `T9_BufferStress_SmallBufferHighTraffic__TP07_BurstWindow` | TP07 | 0.0275 | 21784.3 | 61.2000 | 0.1346 |
| `T9_BufferStress_SmallBufferHighTraffic__TP08_HubTarget` | TP08 | 0.0258 | 16347.4 | 28.3600 | 0.2629 |
| `T9_BufferStress_SmallBufferHighTraffic__TP09_Bimodal` | TP09 | 0.0086 | 22845.2 | 58.6000 | 0.5889 |
| `T9_BufferStress_SmallBufferHighTraffic__TP10_Storm` | TP10 | 0.0028 | 1158.4 | 25.2353 | 0.9922 |
| `T9_BufferStress_SmallBufferHighTraffic__TP11_ManyToOne` | TP11 | 0.0000 | — | — | 0.0567 |
| `T9_BufferStress_SmallBufferHighTraffic__TP12_GroupToGroup` | TP12 | 0.0164 | 21008.8 | 53.5000 | 0.0307 |
| `U1_CBD_Commuting_HelsinkiMedium__TP01_Baseline` | TP01 | 0.4228 | 15420.5 | 76.9135 | 0.0000 |
| `U1_CBD_Commuting_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.4583 | 16036.5 | 76.0909 | 0.0000 |
| `U1_CBD_Commuting_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.3873 | 16186.0 | 71.5367 | 0.0000 |
| `U1_CBD_Commuting_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.1955 | 15015.1 | 299.7429 | 53.3464 |
| `U1_CBD_Commuting_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.0102 | 131.8 | 67.8000 | 1.6809 |
| `U1_CBD_Commuting_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.6144 | 13197.5 | 177.2198 | 64.1010 |
| `U1_CBD_Commuting_HelsinkiMedium__TP07_BurstWindow` | TP07 | 0.4781 | 23741.2 | 81.8400 | 0.0000 |
| `U1_CBD_Commuting_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.3258 | 16234.4 | 421.9684 | 112.8124 |
| `U1_CBD_Commuting_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.3044 | 15327.3 | 245.0447 | 60.0493 |
| `U1_CBD_Commuting_HelsinkiMedium__TP10_Storm` | TP10 | 0.0599 | 1680.5 | 113.4743 | 7.6470 |
| `U1_CBD_Commuting_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.7247 | 13898.2 | 41.6003 | 0.0000 |
| `U1_CBD_Commuting_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.5358 | 13412.2 | 231.2939 | 79.8650 |
| `U2_SparseSuburb_HelsinkiMedium__TP01_Baseline` | TP01 | 0.2573 | 14958.8 | 31.6098 | 0.0000 |
| `U2_SparseSuburb_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.2474 | 13541.0 | 29.6250 | 0.0000 |
| `U2_SparseSuburb_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.2341 | 15073.8 | 28.4732 | 0.0000 |
| `U2_SparseSuburb_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.1713 | 13894.1 | 54.0000 | 7.6851 |
| `U2_SparseSuburb_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.0084 | 26.7 | 26.7500 | 1.2176 |
| `U2_SparseSuburb_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.5309 | 11649.0 | 37.2680 | 1.5340 |
| `U2_SparseSuburb_HelsinkiMedium__TP07_BurstWindow` | TP07 | 0.3342 | 21436.7 | 34.2480 | 0.0000 |
| `U2_SparseSuburb_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.1443 | 10216.2 | 107.8286 | 6.3227 |
| `U2_SparseSuburb_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.1788 | 13820.6 | 59.1456 | 6.9601 |
| `U2_SparseSuburb_HelsinkiMedium__TP10_Storm` | TP10 | 0.0495 | 1454.4 | 35.9607 | 2.6676 |
| `U2_SparseSuburb_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.5464 | 11299.3 | 13.0340 | 0.0000 |
| `U2_SparseSuburb_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.4254 | 11253.2 | 36.8221 | 0.0020 |
| `U3_MicroMobility_HelsinkiMedium__TP01_Baseline` | TP01 | 0.1019 | 12660.3 | 3960.3265 | 399.3410 |
| `U3_MicroMobility_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.3158 | 16440.3 | 4303.1000 | 1320.4842 |
| `U3_MicroMobility_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.2817 | 15898.0 | 1035.8698 | 274.7020 |
| `U3_MicroMobility_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.0166 | 29942.9 | 6861.3333 | 113.8232 |
| `U3_MicroMobility_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.0166 | 93.4 | 65.2500 | 2.0790 |
| `U3_MicroMobility_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.4979 | 12563.5 | 901.2112 | 444.3062 |
| `U3_MicroMobility_HelsinkiMedium__TP07_BurstWindow` | TP07 | 0.1766 | 21054.5 | 3228.0000 | 564.7663 |
| `U3_MicroMobility_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.0608 | 15772.1 | 5016.1695 | 303.5371 |
| `U3_MicroMobility_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.1557 | 14461.8 | 2550.0444 | 386.9412 |
| `U3_MicroMobility_HelsinkiMedium__TP10_Storm` | TP10 | 0.0172 | 936.1 | 1478.3585 | 26.2988 |
| `U3_MicroMobility_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.3330 | 15225.6 | 449.8204 | 145.8990 |
| `U3_MicroMobility_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.4949 | 14258.6 | 1112.5909 | 546.0450 |
| `U4_CongestionHotspot_HelsinkiMedium__TP01_Baseline` | TP01 | 0.2622 | 15867.6 | 75.2558 | 0.0000 |
| `U4_CongestionHotspot_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.3750 | 13749.1 | 69.6111 | 0.0000 |
| `U4_CongestionHotspot_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.2705 | 15995.0 | 71.7667 | 0.0000 |
| `U4_CongestionHotspot_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.1397 | 14250.0 | 358.5600 | 45.8045 |
| `U4_CongestionHotspot_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.3435 |
| `U4_CongestionHotspot_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.4598 | 12216.2 | 141.5987 | 31.6402 |
| `U4_CongestionHotspot_HelsinkiMedium__TP07_BurstWindow` | TP07 | 0.4071 | 23809.7 | 74.7047 | 0.0000 |
| `U4_CongestionHotspot_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.2701 | 15732.9 | 194.2710 | 36.8845 |
| `U4_CongestionHotspot_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.1888 | 15541.6 | 223.7838 | 32.5629 |
| `U4_CongestionHotspot_HelsinkiMedium__TP10_Storm` | TP10 | 0.0386 | 1768.6 | 73.4706 | 3.6687 |
| `U4_CongestionHotspot_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.5649 | 13428.3 | 27.5109 | 0.0000 |
| `U4_CongestionHotspot_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.5092 | 12862.4 | 126.9036 | 27.2209 |
| `U5_WorkdayShort_HelsinkiMedium__TP01_Baseline` | TP01 | 0.2093 | 8511.5 | 73.6893 | 0.0000 |
| `U5_WorkdayShort_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.2188 | 8301.5 | 74.1429 | 0.0000 |
| `U5_WorkdayShort_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.2078 | 10042.0 | 64.1367 | 0.0000 |
| `U5_WorkdayShort_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.1229 | 8585.7 | 239.4091 | 24.8436 |
| `U5_WorkdayShort_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.0081 | 71.0 | 43.5000 | 1.3476 |
| `U5_WorkdayShort_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.3660 | 5825.5 | 69.1268 | 0.1845 |
| `U5_WorkdayShort_HelsinkiMedium__TP07_BurstWindow` | TP07 | 0.3798 | 10388.1 | 74.5396 | 0.0000 |
| `U5_WorkdayShort_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.2546 | 9210.0 | 51.2470 | 0.0000 |
| `U5_WorkdayShort_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.1837 | 7935.5 | 264.1296 | 38.0850 |
| `U5_WorkdayShort_HelsinkiMedium__TP10_Storm` | TP10 | 0.0406 | 1680.3 | 79.2040 | 4.1295 |
| `U5_WorkdayShort_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.3969 | 6675.2 | 30.9273 | 0.0000 |
| `U5_WorkdayShort_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.3783 | 6217.4 | 72.8000 | 0.1391 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP01_Baseline` | TP01 | 0.2541 | 16742.4 | 77.7280 | 0.0000 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.2292 | 16935.9 | 91.8636 | 0.0000 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.2728 | 16284.2 | 71.7636 | 0.0000 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.1117 | 17018.6 | 231.4500 | 20.4972 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.0000 | — | — | 1.3923 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.4763 | 12493.6 | 75.9762 | 0.0000 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP07_BurstWindow` | TP07 | 0.3197 | 22863.8 | 78.6154 | 0.0000 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.2320 | 15806.5 | 77.2222 | 0.0000 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.2211 | 17507.9 | 213.9154 | 33.8095 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP10_Storm` | TP10 | 0.0391 | 1633.9 | 67.9253 | 3.5605 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.5309 | 12878.8 | 24.3476 | 0.0000 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.4826 | 12008.5 | 76.8771 | 0.0000 |
| `U7_HighTimeVariance_HelsinkiMedium__TP01_Baseline` | TP01 | 0.3313 | 16086.5 | 78.9325 | 0.0000 |
| `U7_HighTimeVariance_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.3958 | 13690.4 | 81.4737 | 0.0000 |
| `U7_HighTimeVariance_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.3729 | 16095.8 | 72.9190 | 0.0000 |
| `U7_HighTimeVariance_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.1341 | 10569.4 | 315.9583 | 37.1844 |
| `U7_HighTimeVariance_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.0081 | 49.5 | 90.7500 | 1.7317 |
| `U7_HighTimeVariance_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.5969 | 11944.6 | 218.4473 | 85.1742 |
| `U7_HighTimeVariance_HelsinkiMedium__TP07_BurstWindow` | TP07 | 0.4372 | 25227.3 | 77.9063 | 0.0000 |
| `U7_HighTimeVariance_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.4196 | 16282.1 | 159.4029 | 42.7505 |
| `U7_HighTimeVariance_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.2228 | 15444.3 | 236.5344 | 42.0034 |
| `U7_HighTimeVariance_HelsinkiMedium__TP10_Storm` | TP10 | 0.0629 | 1659.9 | 72.5412 | 5.3860 |
| `U7_HighTimeVariance_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.6619 | 13259.1 | 41.0794 | 0.0000 |
| `U7_HighTimeVariance_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.6258 | 11927.5 | 87.0131 | 6.1452 |
| `V1_TaxiLow_HelsinkiMedium__TP01_Baseline` | TP01 | 0.8887 | 5848.7 | 4.3109 | 1.8021 |
| `V1_TaxiLow_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.9375 | 3541.9 | 2.9556 | 0.0000 |
| `V1_TaxiLow_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.6493 | 3870.4 | 2.4633 | 0.0000 |
| `V1_TaxiLow_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.2363 | 4102.8 | 6.0000 | 2.1264 |
| `V1_TaxiLow_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.1959 | 127.2 | 2.5158 | 1.4742 |
| `V1_TaxiLow_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.9113 | 2872.9 | 5.7025 | 3.5144 |
| `V1_TaxiLow_HelsinkiMedium__TP07_BurstWindow` | TP07 | 1.0000 | 12061.4 | 3.1657 | 0.3619 |
| `V1_TaxiLow_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.8784 | 3661.8 | 15.2124 | 12.9402 |
| `V1_TaxiLow_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.8460 | 2928.7 | 10.3558 | 8.8858 |
| `V1_TaxiLow_HelsinkiMedium__TP10_Storm` | TP10 | 0.2739 | 1215.9 | 2.5216 | 1.6103 |
| `V1_TaxiLow_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.8969 | 2767.1 | 15.6023 | 12.7629 |
| `V1_TaxiLow_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.5276 | 5263.3 | 1.7984 | 0.1636 |
| `V2_TaxiHigh_HelsinkiMedium__TP01_Baseline` | TP01 | 0.9896 | 406.5 | 24.0565 | 0.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.9896 | 386.2 | 23.9158 | 0.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.9887 | 429.0 | 24.0399 | 0.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.6500 | 1776.7 | 382.1709 | 245.0722 |
| `V2_TaxiHigh_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.3499 | 143.8 | 20.3373 | 8.0849 |
| `V2_TaxiHigh_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.9887 | 379.4 | 46.7716 | 23.3361 |
| `V2_TaxiHigh_HelsinkiMedium__TP07_BurstWindow` | TP07 | 1.0000 | 474.0 | 24.0000 | 0.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.9237 | 755.2 | 400.3125 | 357.6845 |
| `V2_TaxiHigh_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.9069 | 1137.7 | 485.5323 | 427.7500 |
| `V2_TaxiHigh_HelsinkiMedium__TP10_Storm` | TP10 | 0.8389 | 1048.6 | 63.2408 | 53.3979 |
| `V2_TaxiHigh_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.9711 | 421.6 | 70.6837 | 46.6237 |
| `V2_TaxiHigh_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.9959 | 372.4 | 24.1745 | 0.2270 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP01_Baseline` | TP01 | 0.3560 | 1459.7 | 6.8786 | 0.0000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.3684 | 1131.2 | 6.4857 | 0.0000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.4057 | 3975.1 | 4.1268 | 0.0000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.3297 | 3913.3 | 10.5667 | 3.6154 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.0761 | 105.8 | 5.4865 | 1.4095 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.2289 | 3771.7 | 4.6081 | 0.0794 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP07_BurstWindow` | TP07 | 0.4105 | 5614.8 | 6.1409 | 0.0000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.1206 | 6936.4 | 96.9402 | 9.5227 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.3448 | 2824.5 | 10.3532 | 2.7530 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP10_Storm` | TP10 | 0.2607 | 1111.4 | 3.8865 | 1.9064 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.1804 | 2589.0 | 16.3371 | 0.0000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.0000 | — | — | 0.0000 |
| `V4_CarOwnership_0_HelsinkiMedium__TP01_Baseline` | TP01 | 0.4004 | 13575.6 | 81.7970 | 0.0000 |
| `V4_CarOwnership_0_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.4688 | 14729.2 | 75.1333 | 0.0000 |
| `V4_CarOwnership_0_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.3931 | 13699.6 | 76.5298 | 0.0000 |
| `V4_CarOwnership_0_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.2011 | 15014.6 | 469.4444 | 89.3743 |
| `V4_CarOwnership_0_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.0122 | 139.0 | 93.5000 | 2.1301 |
| `V4_CarOwnership_0_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.5588 | 10582.1 | 296.7159 | 125.6464 |
| `V4_CarOwnership_0_HelsinkiMedium__TP07_BurstWindow` | TP07 | 0.5109 | 19930.2 | 83.9091 | 0.0000 |
| `V4_CarOwnership_0_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.2711 | 12836.0 | 548.5285 | 127.0485 |
| `V4_CarOwnership_0_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.2857 | 13488.3 | 886.1190 | 238.4507 |
| `V4_CarOwnership_0_HelsinkiMedium__TP10_Storm` | TP10 | 0.0724 | 1570.2 | 117.2220 | 9.3339 |
| `V4_CarOwnership_0_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.6299 | 10783.3 | 46.1227 | 0.0000 |
| `V4_CarOwnership_0_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.6585 | 9886.6 | 444.5683 | 246.3027 |
| `V5_CarOwnership_100_HelsinkiMedium__TP01_Baseline` | TP01 | 0.3161 | 18674.4 | 79.3203 | 0.0000 |
| `V5_CarOwnership_100_HelsinkiMedium__TP02_LowLoad` | TP02 | 0.3684 | 18707.3 | 87.4286 | 0.0000 |
| `V5_CarOwnership_100_HelsinkiMedium__TP03_ManySmall` | TP03 | 0.2976 | 19548.4 | 55.9307 | 0.0000 |
| `V5_CarOwnership_100_HelsinkiMedium__TP04_FewLarge` | TP04 | 0.1638 | 18268.5 | 93.7241 | 10.6497 |
| `V5_CarOwnership_100_HelsinkiMedium__TP05_CriticalTTL` | TP05 | 0.0145 | 84.4 | 42.8571 | 1.6157 |
| `V5_CarOwnership_100_HelsinkiMedium__TP06_OneToMany` | TP06 | 0.3660 | 14764.1 | 69.1746 | 5.3876 |
| `V5_CarOwnership_100_HelsinkiMedium__TP07_BurstWindow` | TP07 | 0.4100 | 27142.1 | 71.8176 | 0.0000 |
| `V5_CarOwnership_100_HelsinkiMedium__TP08_HubTarget` | TP08 | 0.3041 | 18219.6 | 75.3085 | 6.0124 |
| `V5_CarOwnership_100_HelsinkiMedium__TP09_Bimodal` | TP09 | 0.2276 | 18718.7 | 80.4318 | 8.2569 |
| `V5_CarOwnership_100_HelsinkiMedium__TP10_Storm` | TP10 | 0.0397 | 1503.5 | 66.7061 | 3.4824 |
| `V5_CarOwnership_100_HelsinkiMedium__TP11_ManyToOne` | TP11 | 0.6196 | 16106.0 | 27.2712 | 0.0000 |
| `V5_CarOwnership_100_HelsinkiMedium__TP12_GroupToGroup` | TP12 | 0.3865 | 14756.0 | 61.5026 | 0.0000 |

## Indirectas tipo Diego (completo)

| Escenario | TP | source | contact_time_per_min | contact_time_mean_s | total_encounters | ratio_contact_nodes | popularity_top10_ratio |
|---|---:|---|---:|---:|---:|---:|---:|
| `C1_Campus_ClassChange__TP01_Baseline` | TP01 | ConnectivityONEReport | 5.8597 | 14.0 | 4219.0 | 0.9192 | 0.9689 |
| `C1_Campus_ClassChange__TP02_LowLoad` | TP02 | ConnectivityONEReport | 5.8694 | 13.8 | 4226.0 | 0.9107 | 0.9718 |
| `C1_Campus_ClassChange__TP03_ManySmall` | TP03 | ConnectivityONEReport | 5.8139 | 13.7 | 4186.0 | 0.8921 | 0.9661 |
| `C1_Campus_ClassChange__TP04_FewLarge` | TP04 | ConnectivityONEReport | 5.8333 | 14.0 | 4200.0 | 0.9073 | 0.9605 |
| `C1_Campus_ClassChange__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 5.8597 | 14.0 | 4219.0 | 0.9192 | 0.9689 |
| `C1_Campus_ClassChange__TP06_OneToMany` | TP06 | ConnectivityONEReport | 5.8986 | 13.8 | 4247.0 | 0.9113 | 0.9548 |
| `C1_Campus_ClassChange__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 5.8417 | 13.7 | 4206.0 | 0.9090 | 0.9718 |
| `C1_Campus_ClassChange__TP08_HubTarget` | TP08 | ConnectivityONEReport | 5.8986 | 13.8 | 4247.0 | 0.9113 | 0.9548 |
| `C1_Campus_ClassChange__TP09_Bimodal` | TP09 | ConnectivityONEReport | 5.8597 | 14.0 | 4219.0 | 0.9192 | 0.9689 |
| `C1_Campus_ClassChange__TP10_Storm` | TP10 | ConnectivityONEReport | 5.8986 | 13.6 | 4247.0 | 0.9102 | 0.9605 |
| `C1_Campus_ClassChange__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 5.8986 | 13.8 | 4247.0 | 0.9113 | 0.9548 |
| `C1_Campus_ClassChange__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 5.7403 | 13.9 | 4133.0 | 0.9107 | 0.9661 |
| `C2_ExamDay_LongStays__TP01_Baseline` | TP01 | ConnectivityONEReport | 1.1694 | 78.4 | 842.0 | 0.5222 | 0.6213 |
| `C2_ExamDay_LongStays__TP02_LowLoad` | TP02 | ConnectivityONEReport | 1.1694 | 78.4 | 842.0 | 0.5222 | 0.6213 |
| `C2_ExamDay_LongStays__TP03_ManySmall` | TP03 | ConnectivityONEReport | 1.1597 | 82.0 | 835.0 | 0.5230 | 0.6298 |
| `C2_ExamDay_LongStays__TP04_FewLarge` | TP04 | ConnectivityONEReport | 1.1694 | 78.4 | 842.0 | 0.5222 | 0.6213 |
| `C2_ExamDay_LongStays__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 1.1694 | 78.4 | 842.0 | 0.5222 | 0.6213 |
| `C2_ExamDay_LongStays__TP06_OneToMany` | TP06 | ConnectivityONEReport | 1.1528 | 74.5 | 830.0 | 0.5239 | 0.6468 |
| `C2_ExamDay_LongStays__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 1.1694 | 78.4 | 842.0 | 0.5222 | 0.6213 |
| `C2_ExamDay_LongStays__TP08_HubTarget` | TP08 | ConnectivityONEReport | 1.1528 | 74.5 | 830.0 | 0.5239 | 0.6468 |
| `C2_ExamDay_LongStays__TP09_Bimodal` | TP09 | ConnectivityONEReport | 1.1694 | 78.4 | 842.0 | 0.5222 | 0.6213 |
| `C2_ExamDay_LongStays__TP10_Storm` | TP10 | ConnectivityONEReport | 1.1556 | 75.5 | 832.0 | 0.5479 | 0.6596 |
| `C2_ExamDay_LongStays__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 1.1528 | 74.5 | 830.0 | 0.5239 | 0.6468 |
| `C2_ExamDay_LongStays__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 1.1681 | 78.5 | 841.0 | 0.5213 | 0.6213 |
| `C3_Hackathon_24h__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.3819 | 104.3 | 550.0 | 0.5026 | 0.6474 |
| `C3_Hackathon_24h__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.3819 | 104.3 | 550.0 | 0.5026 | 0.6474 |
| `C3_Hackathon_24h__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.3819 | 104.3 | 550.0 | 0.5026 | 0.6474 |
| `C3_Hackathon_24h__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.3819 | 104.3 | 550.0 | 0.5026 | 0.6474 |
| `C3_Hackathon_24h__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.3819 | 104.3 | 550.0 | 0.5026 | 0.6474 |
| `C3_Hackathon_24h__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.3632 | 109.6 | 523.0 | 0.4987 | 0.6667 |
| `C3_Hackathon_24h__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.3819 | 104.3 | 550.0 | 0.5026 | 0.6474 |
| `C3_Hackathon_24h__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.3632 | 109.6 | 523.0 | 0.4987 | 0.6667 |
| `C3_Hackathon_24h__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.3819 | 104.3 | 550.0 | 0.5026 | 0.6474 |
| `C3_Hackathon_24h__TP10_Storm` | TP10 | ConnectivityONEReport | 0.3819 | 104.3 | 550.0 | 0.5026 | 0.6474 |
| `C3_Hackathon_24h__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.3632 | 109.6 | 523.0 | 0.4987 | 0.6667 |
| `C3_Hackathon_24h__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.3819 | 104.3 | 550.0 | 0.5026 | 0.6474 |
| `C4_Stadium_IngressEgress__TP01_Baseline` | TP01 | ConnectivityONEReport | 5.1778 | 14.9 | 932.0 | 0.2566 | 0.3418 |
| `C4_Stadium_IngressEgress__TP02_LowLoad` | TP02 | ConnectivityONEReport | 5.1778 | 14.9 | 932.0 | 0.2566 | 0.3418 |
| `C4_Stadium_IngressEgress__TP03_ManySmall` | TP03 | ConnectivityONEReport | 5.1278 | 14.2 | 923.0 | 0.2532 | 0.3576 |
| `C4_Stadium_IngressEgress__TP04_FewLarge` | TP04 | ConnectivityONEReport | 5.1778 | 14.9 | 932.0 | 0.2566 | 0.3418 |
| `C4_Stadium_IngressEgress__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 5.1778 | 14.9 | 932.0 | 0.2566 | 0.3418 |
| `C4_Stadium_IngressEgress__TP06_OneToMany` | TP06 | ConnectivityONEReport | 5.0000 | 14.1 | 900.0 | 0.2424 | 0.3339 |
| `C4_Stadium_IngressEgress__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 5.1778 | 14.9 | 932.0 | 0.2566 | 0.3418 |
| `C4_Stadium_IngressEgress__TP08_HubTarget` | TP08 | ConnectivityONEReport | 5.0000 | 14.1 | 900.0 | 0.2424 | 0.3339 |
| `C4_Stadium_IngressEgress__TP09_Bimodal` | TP09 | ConnectivityONEReport | 5.1778 | 14.9 | 932.0 | 0.2566 | 0.3418 |
| `C4_Stadium_IngressEgress__TP10_Storm` | TP10 | ConnectivityONEReport | 5.1667 | 15.0 | 930.0 | 0.2513 | 0.3418 |
| `C4_Stadium_IngressEgress__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 5.0000 | 14.1 | 900.0 | 0.2424 | 0.3339 |
| `C4_Stadium_IngressEgress__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 4.8500 | 14.9 | 873.0 | 0.2402 | 0.3228 |
| `C5_Library_Quiet__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.3181 | 76.3 | 229.0 | 0.2427 | 0.3463 |
| `C5_Library_Quiet__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.3208 | 73.0 | 231.0 | 0.2369 | 0.3463 |
| `C5_Library_Quiet__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.3181 | 76.3 | 229.0 | 0.2427 | 0.3463 |
| `C5_Library_Quiet__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.3181 | 76.3 | 229.0 | 0.2427 | 0.3463 |
| `C5_Library_Quiet__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.3181 | 76.3 | 229.0 | 0.2427 | 0.3463 |
| `C5_Library_Quiet__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.3181 | 76.3 | 229.0 | 0.2427 | 0.3463 |
| `C5_Library_Quiet__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.3181 | 76.3 | 229.0 | 0.2427 | 0.3463 |
| `C5_Library_Quiet__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.3181 | 76.3 | 229.0 | 0.2427 | 0.3463 |
| `C5_Library_Quiet__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.3181 | 76.3 | 229.0 | 0.2427 | 0.3463 |
| `C5_Library_Quiet__TP10_Storm` | TP10 | ConnectivityONEReport | 0.3181 | 76.3 | 229.0 | 0.2427 | 0.3463 |
| `C5_Library_Quiet__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.3181 | 76.3 | 229.0 | 0.2427 | 0.3463 |
| `C5_Library_Quiet__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.3181 | 76.3 | 229.0 | 0.2427 | 0.3463 |
| `C6_EmergencyDrill_Evacuation__TP01_Baseline` | TP01 | ConnectivityONEReport | 29.7500 | 4.2 | 3570.0 | 1.0000 | 1.0000 |
| `C6_EmergencyDrill_Evacuation__TP02_LowLoad` | TP02 | ConnectivityONEReport | 29.7500 | 4.2 | 3570.0 | 1.0000 | 1.0000 |
| `C6_EmergencyDrill_Evacuation__TP03_ManySmall` | TP03 | ConnectivityONEReport | 29.7500 | 4.2 | 3570.0 | 1.0000 | 1.0000 |
| `C6_EmergencyDrill_Evacuation__TP04_FewLarge` | TP04 | ConnectivityONEReport | 29.7500 | 4.2 | 3570.0 | 1.0000 | 1.0000 |
| `C6_EmergencyDrill_Evacuation__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 29.7500 | 4.2 | 3570.0 | 1.0000 | 1.0000 |
| `C6_EmergencyDrill_Evacuation__TP06_OneToMany` | TP06 | ConnectivityONEReport | 29.7500 | 4.2 | 3570.0 | 1.0000 | 1.0000 |
| `C6_EmergencyDrill_Evacuation__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 29.7500 | 4.2 | 3570.0 | 1.0000 | 1.0000 |
| `C6_EmergencyDrill_Evacuation__TP08_HubTarget` | TP08 | ConnectivityONEReport | 29.7500 | 4.2 | 3570.0 | 1.0000 | 1.0000 |
| `C6_EmergencyDrill_Evacuation__TP09_Bimodal` | TP09 | ConnectivityONEReport | 29.7500 | 4.2 | 3570.0 | 1.0000 | 1.0000 |
| `C6_EmergencyDrill_Evacuation__TP10_Storm` | TP10 | ConnectivityONEReport | 29.7500 | 4.2 | 3570.0 | 1.0000 | 1.0000 |
| `C6_EmergencyDrill_Evacuation__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 29.7500 | 4.2 | 3570.0 | 1.0000 | 1.0000 |
| `C6_EmergencyDrill_Evacuation__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 29.7500 | 4.2 | 3570.0 | 1.0000 | 1.0000 |
| `D1_ShelterHotspots_Clusters__TP01_Baseline` | TP01 | ConnectivityONEReport | 17.3278 | 23.2 | 12476.0 | 0.3196 | 0.4304 |
| `D1_ShelterHotspots_Clusters__TP02_LowLoad` | TP02 | ConnectivityONEReport | 17.0806 | 24.5 | 12298.0 | 0.3196 | 0.4304 |
| `D1_ShelterHotspots_Clusters__TP03_ManySmall` | TP03 | ConnectivityONEReport | 17.1958 | 23.3 | 12381.0 | 0.3196 | 0.4304 |
| `D1_ShelterHotspots_Clusters__TP04_FewLarge` | TP04 | ConnectivityONEReport | 17.2319 | 23.5 | 12407.0 | 0.3196 | 0.4304 |
| `D1_ShelterHotspots_Clusters__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 17.3278 | 23.2 | 12476.0 | 0.3196 | 0.4304 |
| `D1_ShelterHotspots_Clusters__TP06_OneToMany` | TP06 | ConnectivityONEReport | 17.1097 | 22.9 | 12319.0 | 0.3196 | 0.4304 |
| `D1_ShelterHotspots_Clusters__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 17.2861 | 24.7 | 12446.0 | 0.3196 | 0.4304 |
| `D1_ShelterHotspots_Clusters__TP08_HubTarget` | TP08 | ConnectivityONEReport | 17.1097 | 22.9 | 12319.0 | 0.3196 | 0.4304 |
| `D1_ShelterHotspots_Clusters__TP09_Bimodal` | TP09 | ConnectivityONEReport | 17.0056 | 24.2 | 12244.0 | 0.3196 | 0.4304 |
| `D1_ShelterHotspots_Clusters__TP10_Storm` | TP10 | ConnectivityONEReport | 16.9014 | 24.3 | 12169.0 | 0.3196 | 0.4304 |
| `D1_ShelterHotspots_Clusters__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 17.1097 | 22.9 | 12319.0 | 0.3196 | 0.4304 |
| `D1_ShelterHotspots_Clusters__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 17.2389 | 23.5 | 12412.0 | 0.3196 | 0.4304 |
| `D2_PartitionedCity_MuleBridge__TP01_Baseline` | TP01 | ConnectivityONEReport | 2.4694 | 18.5 | 1778.0 | 0.3799 | 0.4411 |
| `D2_PartitionedCity_MuleBridge__TP02_LowLoad` | TP02 | ConnectivityONEReport | 2.3417 | 18.6 | 1686.0 | 0.3638 | 0.4179 |
| `D2_PartitionedCity_MuleBridge__TP03_ManySmall` | TP03 | ConnectivityONEReport | 2.4458 | 18.7 | 1761.0 | 0.3706 | 0.4304 |
| `D2_PartitionedCity_MuleBridge__TP04_FewLarge` | TP04 | ConnectivityONEReport | 2.2903 | 18.5 | 1649.0 | 0.3545 | 0.4161 |
| `D2_PartitionedCity_MuleBridge__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 2.4694 | 18.5 | 1778.0 | 0.3799 | 0.4411 |
| `D2_PartitionedCity_MuleBridge__TP06_OneToMany` | TP06 | ConnectivityONEReport | 2.3667 | 19.0 | 1704.0 | 0.3614 | 0.4375 |
| `D2_PartitionedCity_MuleBridge__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 2.3250 | 18.1 | 1674.0 | 0.3626 | 0.4286 |
| `D2_PartitionedCity_MuleBridge__TP08_HubTarget` | TP08 | ConnectivityONEReport | 2.3667 | 19.0 | 1704.0 | 0.3614 | 0.4375 |
| `D2_PartitionedCity_MuleBridge__TP09_Bimodal` | TP09 | ConnectivityONEReport | 2.4125 | 18.1 | 1737.0 | 0.3791 | 0.4518 |
| `D2_PartitionedCity_MuleBridge__TP10_Storm` | TP10 | ConnectivityONEReport | 2.3778 | 18.5 | 1712.0 | 0.3710 | 0.4232 |
| `D2_PartitionedCity_MuleBridge__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 2.3667 | 19.0 | 1704.0 | 0.3614 | 0.4375 |
| `D2_PartitionedCity_MuleBridge__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 2.3597 | 18.3 | 1699.0 | 0.3642 | 0.4232 |
| `D3_Aftershock_ErraticMobility__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0639 | 7.4 | 46.0 | 0.0509 | 0.0905 |
| `D3_Aftershock_ErraticMobility__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0639 | 7.4 | 46.0 | 0.0509 | 0.0905 |
| `D3_Aftershock_ErraticMobility__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0639 | 7.4 | 46.0 | 0.0509 | 0.0905 |
| `D3_Aftershock_ErraticMobility__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0639 | 7.4 | 46.0 | 0.0509 | 0.0905 |
| `D3_Aftershock_ErraticMobility__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0639 | 7.4 | 46.0 | 0.0509 | 0.0905 |
| `D3_Aftershock_ErraticMobility__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0639 | 7.4 | 46.0 | 0.0509 | 0.0905 |
| `D3_Aftershock_ErraticMobility__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0639 | 7.4 | 46.0 | 0.0509 | 0.0905 |
| `D3_Aftershock_ErraticMobility__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0639 | 7.4 | 46.0 | 0.0509 | 0.0905 |
| `D3_Aftershock_ErraticMobility__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0639 | 7.4 | 46.0 | 0.0509 | 0.0905 |
| `D3_Aftershock_ErraticMobility__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0639 | 7.4 | 46.0 | 0.0509 | 0.0905 |
| `D3_Aftershock_ErraticMobility__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0639 | 7.4 | 46.0 | 0.0509 | 0.0905 |
| `D3_Aftershock_ErraticMobility__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0639 | 7.4 | 46.0 | 0.0509 | 0.0905 |
| `D4_MedicalTriage_TwoClasses__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0917 | 17.9 | 66.0 | 0.0720 | 0.1524 |
| `D4_MedicalTriage_TwoClasses__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0917 | 17.9 | 66.0 | 0.0720 | 0.1524 |
| `D4_MedicalTriage_TwoClasses__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0917 | 17.9 | 66.0 | 0.0720 | 0.1524 |
| `D4_MedicalTriage_TwoClasses__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0917 | 17.9 | 66.0 | 0.0720 | 0.1524 |
| `D4_MedicalTriage_TwoClasses__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0917 | 17.9 | 66.0 | 0.0720 | 0.1524 |
| `D4_MedicalTriage_TwoClasses__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0917 | 17.9 | 66.0 | 0.0720 | 0.1524 |
| `D4_MedicalTriage_TwoClasses__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0917 | 17.9 | 66.0 | 0.0720 | 0.1524 |
| `D4_MedicalTriage_TwoClasses__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0917 | 17.9 | 66.0 | 0.0720 | 0.1524 |
| `D4_MedicalTriage_TwoClasses__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0917 | 17.9 | 66.0 | 0.0720 | 0.1524 |
| `D4_MedicalTriage_TwoClasses__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0917 | 17.9 | 66.0 | 0.0720 | 0.1524 |
| `D4_MedicalTriage_TwoClasses__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0917 | 17.9 | 66.0 | 0.0720 | 0.1524 |
| `D4_MedicalTriage_TwoClasses__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0917 | 17.9 | 66.0 | 0.0720 | 0.1524 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.5889 | 14.6 | 424.0 | 0.4000 | 0.6000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.5306 | 15.8 | 382.0 | 0.4000 | 0.6000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.5778 | 14.1 | 416.0 | 0.4000 | 0.6000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.5542 | 14.3 | 399.0 | 0.4000 | 0.6000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.5889 | 14.6 | 424.0 | 0.4000 | 0.6000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.5819 | 16.1 | 419.0 | 0.4000 | 0.6000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.5569 | 15.1 | 401.0 | 0.4000 | 0.6000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.5819 | 16.1 | 419.0 | 0.4000 | 0.6000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.5819 | 14.3 | 419.0 | 0.4000 | 0.6000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 0.5917 | 13.9 | 426.0 | 0.4000 | 0.6000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.5819 | 16.1 | 419.0 | 0.4000 | 0.6000 |
| `D5_UAVMule_FastRoute_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.5500 | 16.2 | 396.0 | 0.4000 | 0.6000 |
| `D6_ShortTtlCritical_5to10min__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.1000 | 8.1 | 24.0 | 0.0529 | 0.1034 |
| `D6_ShortTtlCritical_5to10min__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.1000 | 8.1 | 24.0 | 0.0529 | 0.1034 |
| `D6_ShortTtlCritical_5to10min__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.1000 | 8.1 | 24.0 | 0.0529 | 0.1034 |
| `D6_ShortTtlCritical_5to10min__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.1000 | 8.1 | 24.0 | 0.0529 | 0.1034 |
| `D6_ShortTtlCritical_5to10min__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.1000 | 8.1 | 24.0 | 0.0529 | 0.1034 |
| `D6_ShortTtlCritical_5to10min__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.1000 | 8.1 | 24.0 | 0.0529 | 0.1034 |
| `D6_ShortTtlCritical_5to10min__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.1000 | 8.1 | 24.0 | 0.0529 | 0.1034 |
| `D6_ShortTtlCritical_5to10min__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.1000 | 8.1 | 24.0 | 0.0529 | 0.1034 |
| `D6_ShortTtlCritical_5to10min__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.1000 | 8.1 | 24.0 | 0.0529 | 0.1034 |
| `D6_ShortTtlCritical_5to10min__TP10_Storm` | TP10 | ConnectivityONEReport | 0.1000 | 8.1 | 24.0 | 0.0529 | 0.1034 |
| `D6_ShortTtlCritical_5to10min__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.1000 | 8.1 | 24.0 | 0.0529 | 0.1034 |
| `D6_ShortTtlCritical_5to10min__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.1000 | 8.1 | 24.0 | 0.0529 | 0.1034 |
| `D7_HighLoad_TrafficStorm__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.1542 | 6.0 | 37.0 | 0.0333 | 0.0696 |
| `D7_HighLoad_TrafficStorm__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.1542 | 6.0 | 37.0 | 0.0333 | 0.0696 |
| `D7_HighLoad_TrafficStorm__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.1542 | 6.0 | 37.0 | 0.0333 | 0.0696 |
| `D7_HighLoad_TrafficStorm__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.1542 | 6.0 | 37.0 | 0.0333 | 0.0696 |
| `D7_HighLoad_TrafficStorm__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.1542 | 6.0 | 37.0 | 0.0333 | 0.0696 |
| `D7_HighLoad_TrafficStorm__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.1542 | 6.0 | 37.0 | 0.0333 | 0.0696 |
| `D7_HighLoad_TrafficStorm__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.1542 | 6.0 | 37.0 | 0.0333 | 0.0696 |
| `D7_HighLoad_TrafficStorm__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.1542 | 6.0 | 37.0 | 0.0333 | 0.0696 |
| `D7_HighLoad_TrafficStorm__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.1542 | 6.0 | 37.0 | 0.0333 | 0.0696 |
| `D7_HighLoad_TrafficStorm__TP10_Storm` | TP10 | ConnectivityONEReport | 0.1542 | 6.0 | 37.0 | 0.0333 | 0.0696 |
| `D7_HighLoad_TrafficStorm__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.1542 | 6.0 | 37.0 | 0.0333 | 0.0696 |
| `D7_HighLoad_TrafficStorm__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.1542 | 6.0 | 37.0 | 0.0333 | 0.0696 |
| `D8_InfrastructureReturns_BackboneLinks__TP01_Baseline` | TP01 | ConnectivityONEReport | 5.1153 | 18.1 | 3683.0 | 0.4459 | 0.4747 |
| `D8_InfrastructureReturns_BackboneLinks__TP02_LowLoad` | TP02 | ConnectivityONEReport | 5.1750 | 18.4 | 3726.0 | 0.4468 | 0.4794 |
| `D8_InfrastructureReturns_BackboneLinks__TP03_ManySmall` | TP03 | ConnectivityONEReport | 5.2597 | 17.7 | 3787.0 | 0.4563 | 0.4858 |
| `D8_InfrastructureReturns_BackboneLinks__TP04_FewLarge` | TP04 | ConnectivityONEReport | 5.1319 | 18.3 | 3695.0 | 0.4475 | 0.4810 |
| `D8_InfrastructureReturns_BackboneLinks__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 5.1153 | 18.1 | 3683.0 | 0.4459 | 0.4747 |
| `D8_InfrastructureReturns_BackboneLinks__TP06_OneToMany` | TP06 | ConnectivityONEReport | 5.1514 | 18.4 | 3709.0 | 0.4484 | 0.4826 |
| `D8_InfrastructureReturns_BackboneLinks__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 5.1333 | 17.8 | 3696.0 | 0.4497 | 0.4826 |
| `D8_InfrastructureReturns_BackboneLinks__TP08_HubTarget` | TP08 | ConnectivityONEReport | 5.1514 | 18.4 | 3709.0 | 0.4484 | 0.4826 |
| `D8_InfrastructureReturns_BackboneLinks__TP09_Bimodal` | TP09 | ConnectivityONEReport | 5.1153 | 18.1 | 3683.0 | 0.4459 | 0.4747 |
| `D8_InfrastructureReturns_BackboneLinks__TP10_Storm` | TP10 | ConnectivityONEReport | 5.2861 | 18.5 | 3806.0 | 0.4491 | 0.4858 |
| `D8_InfrastructureReturns_BackboneLinks__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 5.1514 | 18.4 | 3709.0 | 0.4484 | 0.4826 |
| `D8_InfrastructureReturns_BackboneLinks__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 5.1153 | 18.0 | 3683.0 | 0.4415 | 0.4810 |
| `D9_Critical_1minTTL__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0500 | 51.7 | 36.0 | 0.0663 | 0.1406 |
| `D9_Critical_1minTTL__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0500 | 51.7 | 36.0 | 0.0663 | 0.1406 |
| `D9_Critical_1minTTL__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0500 | 51.7 | 36.0 | 0.0663 | 0.1406 |
| `D9_Critical_1minTTL__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0500 | 51.7 | 36.0 | 0.0663 | 0.1406 |
| `D9_Critical_1minTTL__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0500 | 51.7 | 36.0 | 0.0663 | 0.1406 |
| `D9_Critical_1minTTL__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0500 | 51.7 | 36.0 | 0.0663 | 0.1406 |
| `D9_Critical_1minTTL__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0500 | 51.7 | 36.0 | 0.0663 | 0.1406 |
| `D9_Critical_1minTTL__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0500 | 51.7 | 36.0 | 0.0663 | 0.1406 |
| `D9_Critical_1minTTL__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0500 | 51.7 | 36.0 | 0.0663 | 0.1406 |
| `D9_Critical_1minTTL__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0500 | 51.7 | 36.0 | 0.0663 | 0.1406 |
| `D9_Critical_1minTTL__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0500 | 51.7 | 36.0 | 0.0663 | 0.1406 |
| `D9_Critical_1minTTL__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0500 | 51.7 | 36.0 | 0.0663 | 0.1406 |
| `R10_TinyRange_5m__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0069 | 14.7 | 5.0 | 0.1389 | 0.2500 |
| `R10_TinyRange_5m__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0069 | 14.7 | 5.0 | 0.1389 | 0.2500 |
| `R10_TinyRange_5m__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0069 | 14.7 | 5.0 | 0.1389 | 0.2500 |
| `R10_TinyRange_5m__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0069 | 14.7 | 5.0 | 0.1389 | 0.2500 |
| `R10_TinyRange_5m__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0069 | 14.7 | 5.0 | 0.1389 | 0.2500 |
| `R10_TinyRange_5m__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0069 | 14.7 | 5.0 | 0.1389 | 0.2500 |
| `R10_TinyRange_5m__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0069 | 14.7 | 5.0 | 0.1389 | 0.2500 |
| `R10_TinyRange_5m__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0069 | 14.7 | 5.0 | 0.1389 | 0.2500 |
| `R10_TinyRange_5m__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0069 | 14.7 | 5.0 | 0.1389 | 0.2500 |
| `R10_TinyRange_5m__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0069 | 14.7 | 5.0 | 0.1389 | 0.2500 |
| `R10_TinyRange_5m__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0069 | 14.7 | 5.0 | 0.1389 | 0.2500 |
| `R10_TinyRange_5m__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0069 | 14.7 | 5.0 | 0.1389 | 0.2500 |
| `R11_SpeedExtremeLow__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R11_SpeedExtremeLow__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R11_SpeedExtremeLow__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R11_SpeedExtremeLow__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R11_SpeedExtremeLow__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R11_SpeedExtremeLow__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R11_SpeedExtremeLow__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R11_SpeedExtremeLow__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R11_SpeedExtremeLow__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R11_SpeedExtremeLow__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R11_SpeedExtremeLow__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R11_SpeedExtremeLow__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R12_SpeedExtremeHigh__TP01_Baseline` | TP01 | ConnectivityONEReport | 2.5611 | 1.0 | 1844.0 | 0.8974 | 0.9487 |
| `R12_SpeedExtremeHigh__TP02_LowLoad` | TP02 | ConnectivityONEReport | 2.6097 | 1.0 | 1879.0 | 0.9141 | 0.9744 |
| `R12_SpeedExtremeHigh__TP03_ManySmall` | TP03 | ConnectivityONEReport | 2.6250 | 1.0 | 1890.0 | 0.9179 | 0.9744 |
| `R12_SpeedExtremeHigh__TP04_FewLarge` | TP04 | ConnectivityONEReport | 2.5181 | 1.0 | 1813.0 | 0.8949 | 0.9744 |
| `R12_SpeedExtremeHigh__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 2.5611 | 1.0 | 1844.0 | 0.8974 | 0.9487 |
| `R12_SpeedExtremeHigh__TP06_OneToMany` | TP06 | ConnectivityONEReport | 2.4667 | 1.0 | 1776.0 | 0.8885 | 0.9551 |
| `R12_SpeedExtremeHigh__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 2.5722 | 1.0 | 1852.0 | 0.9231 | 0.9808 |
| `R12_SpeedExtremeHigh__TP08_HubTarget` | TP08 | ConnectivityONEReport | 2.4667 | 1.0 | 1776.0 | 0.8885 | 0.9551 |
| `R12_SpeedExtremeHigh__TP09_Bimodal` | TP09 | ConnectivityONEReport | 2.5306 | 1.0 | 1822.0 | 0.9051 | 0.9744 |
| `R12_SpeedExtremeHigh__TP10_Storm` | TP10 | ConnectivityONEReport | 2.5806 | 1.0 | 1858.0 | 0.9000 | 0.9744 |
| `R12_SpeedExtremeHigh__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 2.4667 | 1.0 | 1776.0 | 0.8885 | 0.9551 |
| `R12_SpeedExtremeHigh__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 2.4792 | 0.9 | 1785.0 | 0.8897 | 0.9744 |
| `R1_Rural_RandomWaypoint__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R1_Rural_RandomWaypoint__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0000 | — | 0.0 | — | — |
| `R2_VillagesTrails_ThreeClusters__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.3764 | 29.1 | 271.0 | 0.2317 | 0.2857 |
| `R2_VillagesTrails_ThreeClusters__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.3597 | 27.8 | 259.0 | 0.2302 | 0.2929 |
| `R2_VillagesTrails_ThreeClusters__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.3625 | 27.9 | 261.0 | 0.2349 | 0.3000 |
| `R2_VillagesTrails_ThreeClusters__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.3708 | 29.1 | 267.0 | 0.2333 | 0.3071 |
| `R2_VillagesTrails_ThreeClusters__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.3764 | 29.1 | 271.0 | 0.2317 | 0.2857 |
| `R2_VillagesTrails_ThreeClusters__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.3597 | 27.8 | 259.0 | 0.2302 | 0.2929 |
| `R2_VillagesTrails_ThreeClusters__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.4056 | 31.8 | 292.0 | 0.2444 | 0.3143 |
| `R2_VillagesTrails_ThreeClusters__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.3597 | 27.8 | 259.0 | 0.2302 | 0.2929 |
| `R2_VillagesTrails_ThreeClusters__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.3764 | 29.1 | 271.0 | 0.2317 | 0.2857 |
| `R2_VillagesTrails_ThreeClusters__TP10_Storm` | TP10 | ConnectivityONEReport | 0.3736 | 30.1 | 269.0 | 0.2286 | 0.2929 |
| `R2_VillagesTrails_ThreeClusters__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.3597 | 27.8 | 259.0 | 0.2302 | 0.2929 |
| `R2_VillagesTrails_ThreeClusters__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.3583 | 28.0 | 258.0 | 0.2302 | 0.2929 |
| `R3_WildlifeTracking__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0014 | 85.5 | 1.0 | 1.0000 | 1.0000 |
| `R3_WildlifeTracking__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0014 | 85.5 | 1.0 | 1.0000 | 1.0000 |
| `R3_WildlifeTracking__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0014 | 85.5 | 1.0 | 1.0000 | 1.0000 |
| `R3_WildlifeTracking__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0014 | 85.5 | 1.0 | 1.0000 | 1.0000 |
| `R3_WildlifeTracking__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0014 | 85.5 | 1.0 | 1.0000 | 1.0000 |
| `R3_WildlifeTracking__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0014 | 85.5 | 1.0 | 1.0000 | 1.0000 |
| `R3_WildlifeTracking__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0014 | 85.5 | 1.0 | 1.0000 | 1.0000 |
| `R3_WildlifeTracking__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0014 | 85.5 | 1.0 | 1.0000 | 1.0000 |
| `R3_WildlifeTracking__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0014 | 85.5 | 1.0 | 1.0000 | 1.0000 |
| `R3_WildlifeTracking__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0014 | 85.5 | 1.0 | 1.0000 | 1.0000 |
| `R3_WildlifeTracking__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0014 | 85.5 | 1.0 | 1.0000 | 1.0000 |
| `R3_WildlifeTracking__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0014 | 85.5 | 1.0 | 1.0000 | 1.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0597 | 79.7 | 43.0 | 0.6667 | 1.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0597 | 79.7 | 43.0 | 0.6667 | 1.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0597 | 79.7 | 43.0 | 0.6667 | 1.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0597 | 79.7 | 43.0 | 0.6667 | 1.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0597 | 79.7 | 43.0 | 0.6667 | 1.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0597 | 79.7 | 43.0 | 0.6667 | 1.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0597 | 79.7 | 43.0 | 0.6667 | 1.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0597 | 79.7 | 43.0 | 0.6667 | 1.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0597 | 79.7 | 43.0 | 0.6667 | 1.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0347 | 60.8 | 25.0 | 0.6667 | 1.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0597 | 79.7 | 43.0 | 0.6667 | 1.0000 |
| `R4_ParkRangers_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0597 | 79.7 | 43.0 | 0.6667 | 1.0000 |
| `R5_MountainRescue__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0125 | 15.0 | 3.0 | 0.3000 | 0.5000 |
| `R5_MountainRescue__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0125 | 15.0 | 3.0 | 0.3000 | 0.5000 |
| `R5_MountainRescue__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0125 | 15.0 | 3.0 | 0.3000 | 0.5000 |
| `R5_MountainRescue__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0125 | 15.0 | 3.0 | 0.3000 | 0.5000 |
| `R5_MountainRescue__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0125 | 15.0 | 3.0 | 0.3000 | 0.5000 |
| `R5_MountainRescue__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0125 | 15.0 | 3.0 | 0.3000 | 0.5000 |
| `R5_MountainRescue__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0125 | 15.0 | 3.0 | 0.3000 | 0.5000 |
| `R5_MountainRescue__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0125 | 15.0 | 3.0 | 0.3000 | 0.5000 |
| `R5_MountainRescue__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0125 | 15.0 | 3.0 | 0.3000 | 0.5000 |
| `R5_MountainRescue__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0125 | 15.0 | 3.0 | 0.3000 | 0.5000 |
| `R5_MountainRescue__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0125 | 15.0 | 3.0 | 0.3000 | 0.5000 |
| `R5_MountainRescue__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0125 | 15.0 | 3.0 | 0.3000 | 0.5000 |
| `R6_SparseLongRange__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0250 | 573.1 | 18.0 | 0.1250 | 0.2500 |
| `R6_SparseLongRange__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0250 | 573.1 | 18.0 | 0.1250 | 0.2500 |
| `R6_SparseLongRange__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0250 | 573.1 | 18.0 | 0.1250 | 0.2500 |
| `R6_SparseLongRange__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0250 | 573.1 | 18.0 | 0.1250 | 0.2500 |
| `R6_SparseLongRange__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0250 | 573.1 | 18.0 | 0.1250 | 0.2500 |
| `R6_SparseLongRange__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0250 | 573.1 | 18.0 | 0.1250 | 0.2500 |
| `R6_SparseLongRange__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0250 | 573.0 | 18.0 | 0.1250 | 0.2500 |
| `R6_SparseLongRange__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0250 | 573.1 | 18.0 | 0.1250 | 0.2500 |
| `R6_SparseLongRange__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0250 | 573.1 | 18.0 | 0.1250 | 0.2500 |
| `R6_SparseLongRange__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0250 | 573.1 | 18.0 | 0.1250 | 0.2500 |
| `R6_SparseLongRange__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0250 | 573.1 | 18.0 | 0.1250 | 0.2500 |
| `R6_SparseLongRange__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0250 | 573.1 | 18.0 | 0.1250 | 0.2500 |
| `R7_SparseTinyBuffer__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0194 | 20.9 | 14.0 | 0.0915 | 0.1471 |
| `R7_SparseTinyBuffer__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0194 | 20.9 | 14.0 | 0.0915 | 0.1471 |
| `R7_SparseTinyBuffer__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0194 | 20.9 | 14.0 | 0.0915 | 0.1471 |
| `R7_SparseTinyBuffer__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0194 | 20.9 | 14.0 | 0.0915 | 0.1471 |
| `R7_SparseTinyBuffer__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0194 | 20.9 | 14.0 | 0.0915 | 0.1471 |
| `R7_SparseTinyBuffer__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0194 | 20.9 | 14.0 | 0.0915 | 0.1471 |
| `R7_SparseTinyBuffer__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0194 | 20.9 | 14.0 | 0.0915 | 0.1471 |
| `R7_SparseTinyBuffer__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0194 | 20.9 | 14.0 | 0.0915 | 0.1471 |
| `R7_SparseTinyBuffer__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0194 | 20.9 | 14.0 | 0.0915 | 0.1471 |
| `R7_SparseTinyBuffer__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0194 | 21.0 | 14.0 | 0.0915 | 0.1471 |
| `R7_SparseTinyBuffer__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0194 | 20.9 | 14.0 | 0.0915 | 0.1471 |
| `R7_SparseTinyBuffer__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0194 | 20.9 | 14.0 | 0.0915 | 0.1471 |
| `R8_IntermittentPower__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0194 | 16.0 | 14.0 | 0.1029 | 0.2500 |
| `R8_IntermittentPower__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0194 | 16.0 | 14.0 | 0.1029 | 0.2500 |
| `R8_IntermittentPower__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0194 | 16.0 | 14.0 | 0.1029 | 0.2500 |
| `R8_IntermittentPower__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0194 | 16.0 | 14.0 | 0.1029 | 0.2500 |
| `R8_IntermittentPower__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0194 | 16.0 | 14.0 | 0.1029 | 0.2500 |
| `R8_IntermittentPower__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0194 | 16.0 | 14.0 | 0.1029 | 0.2500 |
| `R8_IntermittentPower__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0194 | 16.0 | 14.0 | 0.1029 | 0.2500 |
| `R8_IntermittentPower__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0194 | 16.0 | 14.0 | 0.1029 | 0.2500 |
| `R8_IntermittentPower__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0194 | 16.0 | 14.0 | 0.1029 | 0.2500 |
| `R8_IntermittentPower__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0194 | 16.0 | 14.0 | 0.1029 | 0.2500 |
| `R8_IntermittentPower__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0194 | 16.0 | 14.0 | 0.1029 | 0.2500 |
| `R8_IntermittentPower__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0194 | 16.0 | 14.0 | 0.1029 | 0.2500 |
| `R9_ExtremeRange_200m__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.8250 | 314.4 | 594.0 | 0.5385 | 0.6859 |
| `R9_ExtremeRange_200m__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.8250 | 314.4 | 594.0 | 0.5385 | 0.6859 |
| `R9_ExtremeRange_200m__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.8250 | 314.4 | 594.0 | 0.5385 | 0.6859 |
| `R9_ExtremeRange_200m__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.8250 | 314.4 | 594.0 | 0.5385 | 0.6859 |
| `R9_ExtremeRange_200m__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.8250 | 314.4 | 594.0 | 0.5385 | 0.6859 |
| `R9_ExtremeRange_200m__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.8250 | 314.4 | 594.0 | 0.5385 | 0.6859 |
| `R9_ExtremeRange_200m__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.8250 | 314.4 | 594.0 | 0.5385 | 0.6859 |
| `R9_ExtremeRange_200m__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.8250 | 314.4 | 594.0 | 0.5385 | 0.6859 |
| `R9_ExtremeRange_200m__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.8250 | 314.4 | 594.0 | 0.5385 | 0.6859 |
| `R9_ExtremeRange_200m__TP10_Storm` | TP10 | ConnectivityONEReport | 0.8250 | 314.4 | 594.0 | 0.5385 | 0.6859 |
| `R9_ExtremeRange_200m__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.8250 | 314.4 | 594.0 | 0.5385 | 0.6859 |
| `R9_ExtremeRange_200m__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.8250 | 314.4 | 594.0 | 0.5385 | 0.6859 |
| `S1_StrongCommunities_SeparateClusters__TP01_Baseline` | TP01 | ConnectivityONEReport | 11.2347 | 22.9 | 8089.0 | 0.2435 | 0.2661 |
| `S1_StrongCommunities_SeparateClusters__TP02_LowLoad` | TP02 | ConnectivityONEReport | 11.0306 | 23.0 | 7942.0 | 0.2429 | 0.2661 |
| `S1_StrongCommunities_SeparateClusters__TP03_ManySmall` | TP03 | ConnectivityONEReport | 9.4181 | 22.5 | 6781.0 | 0.2419 | 0.2661 |
| `S1_StrongCommunities_SeparateClusters__TP04_FewLarge` | TP04 | ConnectivityONEReport | 11.1917 | 22.6 | 8058.0 | 0.2432 | 0.2661 |
| `S1_StrongCommunities_SeparateClusters__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 11.2347 | 22.9 | 8089.0 | 0.2435 | 0.2661 |
| `S1_StrongCommunities_SeparateClusters__TP06_OneToMany` | TP06 | ConnectivityONEReport | 10.8944 | 22.3 | 7844.0 | 0.2437 | 0.2661 |
| `S1_StrongCommunities_SeparateClusters__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 11.0778 | 22.9 | 7976.0 | 0.2432 | 0.2661 |
| `S1_StrongCommunities_SeparateClusters__TP08_HubTarget` | TP08 | ConnectivityONEReport | 10.8944 | 22.3 | 7844.0 | 0.2437 | 0.2661 |
| `S1_StrongCommunities_SeparateClusters__TP09_Bimodal` | TP09 | ConnectivityONEReport | 10.9417 | 22.8 | 7878.0 | 0.2439 | 0.2661 |
| `S1_StrongCommunities_SeparateClusters__TP10_Storm` | TP10 | ConnectivityONEReport | 11.2000 | 23.0 | 8064.0 | 0.2434 | 0.2661 |
| `S1_StrongCommunities_SeparateClusters__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 10.8944 | 22.3 | 7844.0 | 0.2437 | 0.2661 |
| `S1_StrongCommunities_SeparateClusters__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 11.1417 | 23.0 | 8022.0 | 0.2434 | 0.2661 |
| `S2_WeakCommunities_HighMixing__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.8681 | 9.1 | 625.0 | 0.1778 | 0.2500 |
| `S2_WeakCommunities_HighMixing__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.8681 | 9.1 | 625.0 | 0.1778 | 0.2500 |
| `S2_WeakCommunities_HighMixing__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.8292 | 9.1 | 597.0 | 0.1684 | 0.2421 |
| `S2_WeakCommunities_HighMixing__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.8681 | 9.1 | 625.0 | 0.1778 | 0.2500 |
| `S2_WeakCommunities_HighMixing__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.8681 | 9.1 | 625.0 | 0.1778 | 0.2500 |
| `S2_WeakCommunities_HighMixing__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.8958 | 9.4 | 645.0 | 0.1839 | 0.2674 |
| `S2_WeakCommunities_HighMixing__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.8194 | 9.0 | 590.0 | 0.1699 | 0.2453 |
| `S2_WeakCommunities_HighMixing__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.8958 | 9.4 | 645.0 | 0.1839 | 0.2674 |
| `S2_WeakCommunities_HighMixing__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.8681 | 9.1 | 625.0 | 0.1778 | 0.2500 |
| `S2_WeakCommunities_HighMixing__TP10_Storm` | TP10 | ConnectivityONEReport | 0.8375 | 9.3 | 603.0 | 0.1706 | 0.2500 |
| `S2_WeakCommunities_HighMixing__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.8958 | 9.4 | 645.0 | 0.1839 | 0.2674 |
| `S2_WeakCommunities_HighMixing__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.8681 | 9.1 | 625.0 | 0.1778 | 0.2500 |
| `S3_PeriodicMeetings_RegularRhythm__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.1556 | 16.3 | 112.0 | 0.0922 | 0.1362 |
| `S3_PeriodicMeetings_RegularRhythm__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.1556 | 16.3 | 112.0 | 0.0922 | 0.1362 |
| `S3_PeriodicMeetings_RegularRhythm__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.1681 | 18.7 | 121.0 | 0.0947 | 0.1510 |
| `S3_PeriodicMeetings_RegularRhythm__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.1556 | 16.3 | 112.0 | 0.0922 | 0.1362 |
| `S3_PeriodicMeetings_RegularRhythm__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.1556 | 16.3 | 112.0 | 0.0922 | 0.1362 |
| `S3_PeriodicMeetings_RegularRhythm__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.1556 | 16.3 | 112.0 | 0.0922 | 0.1362 |
| `S3_PeriodicMeetings_RegularRhythm__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.1556 | 16.3 | 112.0 | 0.0922 | 0.1362 |
| `S3_PeriodicMeetings_RegularRhythm__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.1556 | 16.3 | 112.0 | 0.0922 | 0.1362 |
| `S3_PeriodicMeetings_RegularRhythm__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.1556 | 16.3 | 112.0 | 0.0922 | 0.1362 |
| `S3_PeriodicMeetings_RegularRhythm__TP10_Storm` | TP10 | ConnectivityONEReport | 0.1556 | 16.3 | 112.0 | 0.0922 | 0.1362 |
| `S3_PeriodicMeetings_RegularRhythm__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.1556 | 16.3 | 112.0 | 0.0922 | 0.1362 |
| `S3_PeriodicMeetings_RegularRhythm__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.1556 | 16.3 | 112.0 | 0.0922 | 0.1362 |
| `S4_RandomMixing_NoHotspots__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0958 | 23.4 | 69.0 | 0.0451 | 0.0802 |
| `S4_RandomMixing_NoHotspots__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0958 | 23.4 | 69.0 | 0.0451 | 0.0802 |
| `S4_RandomMixing_NoHotspots__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0958 | 23.4 | 69.0 | 0.0451 | 0.0802 |
| `S4_RandomMixing_NoHotspots__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0958 | 23.4 | 69.0 | 0.0451 | 0.0802 |
| `S4_RandomMixing_NoHotspots__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0958 | 23.4 | 69.0 | 0.0451 | 0.0802 |
| `S4_RandomMixing_NoHotspots__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0958 | 23.4 | 69.0 | 0.0451 | 0.0802 |
| `S4_RandomMixing_NoHotspots__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0958 | 23.4 | 69.0 | 0.0451 | 0.0802 |
| `S4_RandomMixing_NoHotspots__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0958 | 23.4 | 69.0 | 0.0451 | 0.0802 |
| `S4_RandomMixing_NoHotspots__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0958 | 23.4 | 69.0 | 0.0451 | 0.0802 |
| `S4_RandomMixing_NoHotspots__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0958 | 23.3 | 69.0 | 0.0451 | 0.0802 |
| `S4_RandomMixing_NoHotspots__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0958 | 23.4 | 69.0 | 0.0451 | 0.0802 |
| `S4_RandomMixing_NoHotspots__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0958 | 23.4 | 69.0 | 0.0451 | 0.0802 |
| `S5_TwoLayer_StudentsStaff__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.4278 | 7.3 | 308.0 | 0.1063 | 0.1706 |
| `S5_TwoLayer_StudentsStaff__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.4417 | 7.1 | 318.0 | 0.1081 | 0.1807 |
| `S5_TwoLayer_StudentsStaff__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.4417 | 7.1 | 318.0 | 0.1081 | 0.1807 |
| `S5_TwoLayer_StudentsStaff__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.4278 | 7.3 | 308.0 | 0.1063 | 0.1706 |
| `S5_TwoLayer_StudentsStaff__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.4278 | 7.3 | 308.0 | 0.1063 | 0.1706 |
| `S5_TwoLayer_StudentsStaff__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.4278 | 7.3 | 308.0 | 0.1063 | 0.1706 |
| `S5_TwoLayer_StudentsStaff__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.4375 | 7.4 | 315.0 | 0.1081 | 0.1774 |
| `S5_TwoLayer_StudentsStaff__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.4278 | 7.3 | 308.0 | 0.1063 | 0.1706 |
| `S5_TwoLayer_StudentsStaff__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.4278 | 7.3 | 308.0 | 0.1063 | 0.1706 |
| `S5_TwoLayer_StudentsStaff__TP10_Storm` | TP10 | ConnectivityONEReport | 0.4181 | 7.3 | 301.0 | 0.1016 | 0.1723 |
| `S5_TwoLayer_StudentsStaff__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.4278 | 7.3 | 308.0 | 0.1063 | 0.1706 |
| `S5_TwoLayer_StudentsStaff__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.4278 | 7.3 | 308.0 | 0.1063 | 0.1706 |
| `S6_FamilyGroups_SmallPersistent__TP01_Baseline` | TP01 | ConnectivityONEReport | 5.7222 | 16.4 | 4120.0 | 0.0627 | 0.0732 |
| `S6_FamilyGroups_SmallPersistent__TP02_LowLoad` | TP02 | ConnectivityONEReport | 5.7347 | 16.0 | 4129.0 | 0.0627 | 0.0732 |
| `S6_FamilyGroups_SmallPersistent__TP03_ManySmall` | TP03 | ConnectivityONEReport | 5.6931 | 16.2 | 4099.0 | 0.0627 | 0.0732 |
| `S6_FamilyGroups_SmallPersistent__TP04_FewLarge` | TP04 | ConnectivityONEReport | 5.6167 | 14.7 | 4044.0 | 0.0627 | 0.0732 |
| `S6_FamilyGroups_SmallPersistent__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 5.7222 | 16.4 | 4120.0 | 0.0627 | 0.0732 |
| `S6_FamilyGroups_SmallPersistent__TP06_OneToMany` | TP06 | ConnectivityONEReport | 5.6208 | 14.3 | 4047.0 | 0.0627 | 0.0732 |
| `S6_FamilyGroups_SmallPersistent__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 5.7069 | 16.2 | 4109.0 | 0.0627 | 0.0732 |
| `S6_FamilyGroups_SmallPersistent__TP08_HubTarget` | TP08 | ConnectivityONEReport | 5.6208 | 14.3 | 4047.0 | 0.0627 | 0.0732 |
| `S6_FamilyGroups_SmallPersistent__TP09_Bimodal` | TP09 | ConnectivityONEReport | 5.6222 | 16.7 | 4048.0 | 0.0627 | 0.0732 |
| `S6_FamilyGroups_SmallPersistent__TP10_Storm` | TP10 | ConnectivityONEReport | 5.4903 | 17.5 | 3953.0 | 0.0627 | 0.0732 |
| `S6_FamilyGroups_SmallPersistent__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 5.6208 | 14.3 | 4047.0 | 0.0627 | 0.0732 |
| `S6_FamilyGroups_SmallPersistent__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 5.6972 | 17.2 | 4102.0 | 0.0627 | 0.0732 |
| `T10_HighRateLowSpeed_Congestion__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0542 | 10.1 | 39.0 | 0.0453 | 0.0976 |
| `T10_HighRateLowSpeed_Congestion__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0542 | 10.1 | 39.0 | 0.0453 | 0.0976 |
| `T10_HighRateLowSpeed_Congestion__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0542 | 10.1 | 39.0 | 0.0453 | 0.0976 |
| `T10_HighRateLowSpeed_Congestion__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0542 | 10.1 | 39.0 | 0.0453 | 0.0976 |
| `T10_HighRateLowSpeed_Congestion__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0542 | 10.1 | 39.0 | 0.0453 | 0.0976 |
| `T10_HighRateLowSpeed_Congestion__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0542 | 10.1 | 39.0 | 0.0453 | 0.0976 |
| `T10_HighRateLowSpeed_Congestion__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0542 | 10.1 | 39.0 | 0.0453 | 0.0976 |
| `T10_HighRateLowSpeed_Congestion__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0542 | 10.1 | 39.0 | 0.0453 | 0.0976 |
| `T10_HighRateLowSpeed_Congestion__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0542 | 10.1 | 39.0 | 0.0453 | 0.0976 |
| `T10_HighRateLowSpeed_Congestion__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0542 | 10.1 | 39.0 | 0.0453 | 0.0976 |
| `T10_HighRateLowSpeed_Congestion__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0542 | 10.1 | 39.0 | 0.0453 | 0.0976 |
| `T10_HighRateLowSpeed_Congestion__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0542 | 10.1 | 39.0 | 0.0453 | 0.0976 |
| `T11_TTL_1min__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.4236 | 9.1 | 305.0 | 0.5011 | 0.7126 |
| `T11_TTL_1min__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.4222 | 9.1 | 304.0 | 0.5011 | 0.7126 |
| `T11_TTL_1min__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.4278 | 9.2 | 308.0 | 0.5011 | 0.6782 |
| `T11_TTL_1min__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.4264 | 9.2 | 307.0 | 0.5011 | 0.6782 |
| `T11_TTL_1min__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.4236 | 9.1 | 305.0 | 0.5011 | 0.7126 |
| `T11_TTL_1min__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.4361 | 8.6 | 314.0 | 0.4851 | 0.6322 |
| `T11_TTL_1min__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.4236 | 9.1 | 305.0 | 0.5011 | 0.7126 |
| `T11_TTL_1min__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.4361 | 8.6 | 314.0 | 0.4851 | 0.6322 |
| `T11_TTL_1min__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.4236 | 9.1 | 305.0 | 0.5011 | 0.7126 |
| `T11_TTL_1min__TP10_Storm` | TP10 | ConnectivityONEReport | 0.4694 | 8.8 | 338.0 | 0.5494 | 0.7241 |
| `T11_TTL_1min__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.4361 | 8.6 | 314.0 | 0.4851 | 0.6322 |
| `T11_TTL_1min__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.4236 | 9.1 | 305.0 | 0.5011 | 0.7126 |
| `T12_TTL_Infinite_Buffer200M__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0486 | 14.8 | 35.0 | 0.0571 | 0.1250 |
| `T12_TTL_Infinite_Buffer200M__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0486 | 14.8 | 35.0 | 0.0571 | 0.1250 |
| `T12_TTL_Infinite_Buffer200M__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0486 | 14.8 | 35.0 | 0.0571 | 0.1250 |
| `T12_TTL_Infinite_Buffer200M__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0486 | 14.8 | 35.0 | 0.0571 | 0.1250 |
| `T12_TTL_Infinite_Buffer200M__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0486 | 14.8 | 35.0 | 0.0571 | 0.1250 |
| `T12_TTL_Infinite_Buffer200M__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0486 | 14.8 | 35.0 | 0.0571 | 0.1250 |
| `T12_TTL_Infinite_Buffer200M__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0486 | 14.8 | 35.0 | 0.0571 | 0.1250 |
| `T12_TTL_Infinite_Buffer200M__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0486 | 14.8 | 35.0 | 0.0571 | 0.1250 |
| `T12_TTL_Infinite_Buffer200M__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0486 | 14.8 | 35.0 | 0.0571 | 0.1250 |
| `T12_TTL_Infinite_Buffer200M__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0486 | 14.8 | 35.0 | 0.0571 | 0.1250 |
| `T12_TTL_Infinite_Buffer200M__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0486 | 14.8 | 35.0 | 0.0571 | 0.1250 |
| `T12_TTL_Infinite_Buffer200M__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0486 | 14.8 | 35.0 | 0.0571 | 0.1250 |
| `T13_Buffer_256k__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0125 | 4.8 | 9.0 | 0.1154 | 0.2083 |
| `T13_Buffer_256k__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0125 | 4.8 | 9.0 | 0.1154 | 0.2083 |
| `T13_Buffer_256k__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0125 | 4.8 | 9.0 | 0.1154 | 0.2083 |
| `T13_Buffer_256k__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0125 | 4.8 | 9.0 | 0.1154 | 0.2083 |
| `T13_Buffer_256k__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0125 | 4.8 | 9.0 | 0.1154 | 0.2083 |
| `T13_Buffer_256k__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0125 | 4.8 | 9.0 | 0.1154 | 0.2083 |
| `T13_Buffer_256k__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0125 | 4.8 | 9.0 | 0.1154 | 0.2083 |
| `T13_Buffer_256k__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0125 | 4.8 | 9.0 | 0.1154 | 0.2083 |
| `T13_Buffer_256k__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0125 | 4.8 | 9.0 | 0.1154 | 0.2083 |
| `T13_Buffer_256k__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0125 | 4.8 | 9.0 | 0.1154 | 0.2083 |
| `T13_Buffer_256k__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0125 | 4.8 | 9.0 | 0.1154 | 0.2083 |
| `T13_Buffer_256k__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0125 | 4.8 | 9.0 | 0.1154 | 0.2083 |
| `T14_Buffer_200M__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.1528 | 13.2 | 110.0 | 0.1014 | 0.1689 |
| `T14_Buffer_200M__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.1528 | 13.2 | 110.0 | 0.1014 | 0.1689 |
| `T14_Buffer_200M__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.1583 | 13.9 | 114.0 | 0.1053 | 0.2178 |
| `T14_Buffer_200M__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.1528 | 13.2 | 110.0 | 0.1014 | 0.1689 |
| `T14_Buffer_200M__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.1528 | 13.2 | 110.0 | 0.1014 | 0.1689 |
| `T14_Buffer_200M__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.1528 | 13.2 | 110.0 | 0.1014 | 0.1689 |
| `T14_Buffer_200M__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.1528 | 13.2 | 110.0 | 0.1014 | 0.1689 |
| `T14_Buffer_200M__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.1528 | 13.2 | 110.0 | 0.1014 | 0.1689 |
| `T14_Buffer_200M__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.1528 | 13.2 | 110.0 | 0.1014 | 0.1689 |
| `T14_Buffer_200M__TP10_Storm` | TP10 | ConnectivityONEReport | 0.1528 | 12.8 | 110.0 | 0.1014 | 0.1867 |
| `T14_Buffer_200M__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.1528 | 13.2 | 110.0 | 0.1014 | 0.1689 |
| `T14_Buffer_200M__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.1528 | 13.2 | 110.0 | 0.1014 | 0.1689 |
| `T15_TransmitSpeed_256k__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.2917 | 4.0 | 210.0 | 0.2253 | 0.3610 |
| `T15_TransmitSpeed_256k__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.2889 | 4.1 | 208.0 | 0.2242 | 0.3415 |
| `T15_TransmitSpeed_256k__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.3056 | 4.1 | 220.0 | 0.2207 | 0.3220 |
| `T15_TransmitSpeed_256k__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.2889 | 4.1 | 208.0 | 0.2242 | 0.3415 |
| `T15_TransmitSpeed_256k__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.2917 | 4.0 | 210.0 | 0.2253 | 0.3610 |
| `T15_TransmitSpeed_256k__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.3208 | 4.0 | 231.0 | 0.2323 | 0.3756 |
| `T15_TransmitSpeed_256k__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.3208 | 4.0 | 231.0 | 0.2404 | 0.3659 |
| `T15_TransmitSpeed_256k__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.3208 | 4.0 | 231.0 | 0.2323 | 0.3756 |
| `T15_TransmitSpeed_256k__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.2917 | 4.0 | 210.0 | 0.2253 | 0.3610 |
| `T15_TransmitSpeed_256k__TP10_Storm` | TP10 | ConnectivityONEReport | 0.2861 | 4.0 | 206.0 | 0.2160 | 0.3220 |
| `T15_TransmitSpeed_256k__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.3208 | 4.0 | 231.0 | 0.2323 | 0.3756 |
| `T15_TransmitSpeed_256k__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.2875 | 4.1 | 207.0 | 0.2230 | 0.3366 |
| `T1_ManySmallMsgs_HighRate__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0667 | 16.0 | 48.0 | 0.0802 | 0.1364 |
| `T1_ManySmallMsgs_HighRate__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0583 | 16.4 | 42.0 | 0.0758 | 0.1562 |
| `T1_ManySmallMsgs_HighRate__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0583 | 16.4 | 42.0 | 0.0758 | 0.1562 |
| `T1_ManySmallMsgs_HighRate__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0583 | 16.4 | 42.0 | 0.0758 | 0.1562 |
| `T1_ManySmallMsgs_HighRate__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0667 | 16.0 | 48.0 | 0.0802 | 0.1364 |
| `T1_ManySmallMsgs_HighRate__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0583 | 16.4 | 42.0 | 0.0758 | 0.1562 |
| `T1_ManySmallMsgs_HighRate__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0583 | 16.4 | 42.0 | 0.0758 | 0.1562 |
| `T1_ManySmallMsgs_HighRate__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0583 | 16.4 | 42.0 | 0.0758 | 0.1562 |
| `T1_ManySmallMsgs_HighRate__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0667 | 16.0 | 48.0 | 0.0802 | 0.1364 |
| `T1_ManySmallMsgs_HighRate__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0583 | 16.4 | 42.0 | 0.0758 | 0.1562 |
| `T1_ManySmallMsgs_HighRate__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0583 | 16.4 | 42.0 | 0.0758 | 0.1562 |
| `T1_ManySmallMsgs_HighRate__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0583 | 16.4 | 42.0 | 0.0758 | 0.1562 |
| `T2_FewHugeMsgs_LowRate__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0694 | 13.8 | 50.0 | 0.0546 | 0.1073 |
| `T2_FewHugeMsgs_LowRate__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0694 | 13.8 | 50.0 | 0.0546 | 0.1073 |
| `T2_FewHugeMsgs_LowRate__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0694 | 13.8 | 50.0 | 0.0546 | 0.1073 |
| `T2_FewHugeMsgs_LowRate__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0694 | 13.8 | 50.0 | 0.0546 | 0.1073 |
| `T2_FewHugeMsgs_LowRate__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0694 | 13.8 | 50.0 | 0.0546 | 0.1073 |
| `T2_FewHugeMsgs_LowRate__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0694 | 13.8 | 50.0 | 0.0546 | 0.1073 |
| `T2_FewHugeMsgs_LowRate__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0694 | 13.8 | 50.0 | 0.0546 | 0.1073 |
| `T2_FewHugeMsgs_LowRate__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0694 | 13.8 | 50.0 | 0.0546 | 0.1073 |
| `T2_FewHugeMsgs_LowRate__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0694 | 13.8 | 50.0 | 0.0546 | 0.1073 |
| `T2_FewHugeMsgs_LowRate__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0694 | 13.8 | 50.0 | 0.0546 | 0.1073 |
| `T2_FewHugeMsgs_LowRate__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0694 | 13.8 | 50.0 | 0.0546 | 0.1073 |
| `T2_FewHugeMsgs_LowRate__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0694 | 13.8 | 50.0 | 0.0546 | 0.1073 |
| `T3_MixedBimodal_SmallAndLarge__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0569 | 20.2 | 41.0 | 0.0513 | 0.0962 |
| `T3_MixedBimodal_SmallAndLarge__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0569 | 20.2 | 41.0 | 0.0513 | 0.0962 |
| `T3_MixedBimodal_SmallAndLarge__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0569 | 20.2 | 41.0 | 0.0513 | 0.0962 |
| `T3_MixedBimodal_SmallAndLarge__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0569 | 20.2 | 41.0 | 0.0513 | 0.0962 |
| `T3_MixedBimodal_SmallAndLarge__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0569 | 20.2 | 41.0 | 0.0513 | 0.0962 |
| `T3_MixedBimodal_SmallAndLarge__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0569 | 20.2 | 41.0 | 0.0513 | 0.0962 |
| `T3_MixedBimodal_SmallAndLarge__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0569 | 20.2 | 41.0 | 0.0513 | 0.0962 |
| `T3_MixedBimodal_SmallAndLarge__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0569 | 20.2 | 41.0 | 0.0513 | 0.0962 |
| `T3_MixedBimodal_SmallAndLarge__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0569 | 20.2 | 41.0 | 0.0513 | 0.0962 |
| `T3_MixedBimodal_SmallAndLarge__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0569 | 20.2 | 41.0 | 0.0513 | 0.0962 |
| `T3_MixedBimodal_SmallAndLarge__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0569 | 20.2 | 41.0 | 0.0513 | 0.0962 |
| `T3_MixedBimodal_SmallAndLarge__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0569 | 12.9 | 41.0 | 0.0586 | 0.1319 |
| `T4_VeryShortTtl_5to10min__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0229 | 11.7 | 11.0 | 0.0809 | 0.1562 |
| `T4_VeryShortTtl_5to10min__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0229 | 11.7 | 11.0 | 0.0809 | 0.1562 |
| `T4_VeryShortTtl_5to10min__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0229 | 11.7 | 11.0 | 0.0809 | 0.1562 |
| `T4_VeryShortTtl_5to10min__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0229 | 11.7 | 11.0 | 0.0809 | 0.1562 |
| `T4_VeryShortTtl_5to10min__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0229 | 11.7 | 11.0 | 0.0809 | 0.1562 |
| `T4_VeryShortTtl_5to10min__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0229 | 11.7 | 11.0 | 0.0809 | 0.1562 |
| `T4_VeryShortTtl_5to10min__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0229 | 11.7 | 11.0 | 0.0809 | 0.1562 |
| `T4_VeryShortTtl_5to10min__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0229 | 11.7 | 11.0 | 0.0809 | 0.1562 |
| `T4_VeryShortTtl_5to10min__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0229 | 11.7 | 11.0 | 0.0809 | 0.1562 |
| `T4_VeryShortTtl_5to10min__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0229 | 11.7 | 11.0 | 0.0809 | 0.1562 |
| `T4_VeryShortTtl_5to10min__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0229 | 11.7 | 11.0 | 0.0809 | 0.1562 |
| `T4_VeryShortTtl_5to10min__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0229 | 11.7 | 11.0 | 0.0809 | 0.1562 |
| `T5_VeryLongTtl_6to24h__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0833 | 23.2 | 60.0 | 0.0871 | 0.1875 |
| `T5_VeryLongTtl_6to24h__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0833 | 23.2 | 60.0 | 0.0871 | 0.1875 |
| `T5_VeryLongTtl_6to24h__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0833 | 23.2 | 60.0 | 0.0871 | 0.1875 |
| `T5_VeryLongTtl_6to24h__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0833 | 23.2 | 60.0 | 0.0871 | 0.1875 |
| `T5_VeryLongTtl_6to24h__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0833 | 23.2 | 60.0 | 0.0871 | 0.1875 |
| `T5_VeryLongTtl_6to24h__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0833 | 23.2 | 60.0 | 0.0871 | 0.1875 |
| `T5_VeryLongTtl_6to24h__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0833 | 23.2 | 60.0 | 0.0871 | 0.1875 |
| `T5_VeryLongTtl_6to24h__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0833 | 23.2 | 60.0 | 0.0871 | 0.1875 |
| `T5_VeryLongTtl_6to24h__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0833 | 23.2 | 60.0 | 0.0871 | 0.1875 |
| `T5_VeryLongTtl_6to24h__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0833 | 23.2 | 60.0 | 0.0871 | 0.1875 |
| `T5_VeryLongTtl_6to24h__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0833 | 23.2 | 60.0 | 0.0871 | 0.1875 |
| `T5_VeryLongTtl_6to24h__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0833 | 23.2 | 60.0 | 0.0871 | 0.1875 |
| `T6_UniformSources_RandomFromTo__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0458 | 10.7 | 33.0 | 0.0469 | 0.0946 |
| `T6_UniformSources_RandomFromTo__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0458 | 10.7 | 33.0 | 0.0469 | 0.0946 |
| `T6_UniformSources_RandomFromTo__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0458 | 10.7 | 33.0 | 0.0469 | 0.0946 |
| `T6_UniformSources_RandomFromTo__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0458 | 10.7 | 33.0 | 0.0469 | 0.0946 |
| `T6_UniformSources_RandomFromTo__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0458 | 10.7 | 33.0 | 0.0469 | 0.0946 |
| `T6_UniformSources_RandomFromTo__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0458 | 10.7 | 33.0 | 0.0469 | 0.0946 |
| `T6_UniformSources_RandomFromTo__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0500 | 10.8 | 36.0 | 0.0486 | 0.0987 |
| `T6_UniformSources_RandomFromTo__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0458 | 10.7 | 33.0 | 0.0469 | 0.0946 |
| `T6_UniformSources_RandomFromTo__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0458 | 10.7 | 33.0 | 0.0469 | 0.0946 |
| `T6_UniformSources_RandomFromTo__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0458 | 10.7 | 33.0 | 0.0469 | 0.0946 |
| `T6_UniformSources_RandomFromTo__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0458 | 10.7 | 33.0 | 0.0469 | 0.0946 |
| `T6_UniformSources_RandomFromTo__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0458 | 10.7 | 33.0 | 0.0469 | 0.0946 |
| `T7_TargetedToHubs_FewDestinations__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0597 | 16.9 | 43.0 | 0.0553 | 0.1382 |
| `T7_TargetedToHubs_FewDestinations__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0597 | 16.9 | 43.0 | 0.0553 | 0.1382 |
| `T7_TargetedToHubs_FewDestinations__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0597 | 16.9 | 43.0 | 0.0553 | 0.1382 |
| `T7_TargetedToHubs_FewDestinations__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0597 | 16.9 | 43.0 | 0.0553 | 0.1382 |
| `T7_TargetedToHubs_FewDestinations__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0597 | 16.9 | 43.0 | 0.0553 | 0.1382 |
| `T7_TargetedToHubs_FewDestinations__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0597 | 16.9 | 43.0 | 0.0553 | 0.1382 |
| `T7_TargetedToHubs_FewDestinations__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0597 | 16.9 | 43.0 | 0.0553 | 0.1382 |
| `T7_TargetedToHubs_FewDestinations__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0597 | 16.9 | 43.0 | 0.0553 | 0.1382 |
| `T7_TargetedToHubs_FewDestinations__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0597 | 16.9 | 43.0 | 0.0553 | 0.1382 |
| `T7_TargetedToHubs_FewDestinations__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0597 | 16.9 | 43.0 | 0.0553 | 0.1382 |
| `T7_TargetedToHubs_FewDestinations__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0597 | 16.9 | 43.0 | 0.0553 | 0.1382 |
| `T7_TargetedToHubs_FewDestinations__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0597 | 16.9 | 43.0 | 0.0553 | 0.1382 |
| `T8_BurstTraffic_TimeWindows__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0625 | 18.9 | 45.0 | 0.0626 | 0.1351 |
| `T8_BurstTraffic_TimeWindows__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0625 | 18.9 | 45.0 | 0.0626 | 0.1351 |
| `T8_BurstTraffic_TimeWindows__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0625 | 18.9 | 45.0 | 0.0626 | 0.1351 |
| `T8_BurstTraffic_TimeWindows__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0625 | 18.9 | 45.0 | 0.0626 | 0.1351 |
| `T8_BurstTraffic_TimeWindows__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0625 | 18.9 | 45.0 | 0.0626 | 0.1351 |
| `T8_BurstTraffic_TimeWindows__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0625 | 18.9 | 45.0 | 0.0626 | 0.1351 |
| `T8_BurstTraffic_TimeWindows__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0625 | 18.9 | 45.0 | 0.0626 | 0.1351 |
| `T8_BurstTraffic_TimeWindows__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0625 | 18.9 | 45.0 | 0.0626 | 0.1351 |
| `T8_BurstTraffic_TimeWindows__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0625 | 18.9 | 45.0 | 0.0626 | 0.1351 |
| `T8_BurstTraffic_TimeWindows__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0625 | 18.9 | 45.0 | 0.0626 | 0.1351 |
| `T8_BurstTraffic_TimeWindows__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0625 | 18.9 | 45.0 | 0.0626 | 0.1351 |
| `T8_BurstTraffic_TimeWindows__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0625 | 18.9 | 45.0 | 0.0626 | 0.1351 |
| `T9_BufferStress_SmallBufferHighTraffic__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.0444 | 9.2 | 32.0 | 0.0570 | 0.1136 |
| `T9_BufferStress_SmallBufferHighTraffic__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.0444 | 9.2 | 32.0 | 0.0570 | 0.1136 |
| `T9_BufferStress_SmallBufferHighTraffic__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.0444 | 9.2 | 32.0 | 0.0570 | 0.1136 |
| `T9_BufferStress_SmallBufferHighTraffic__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.0444 | 9.2 | 32.0 | 0.0570 | 0.1136 |
| `T9_BufferStress_SmallBufferHighTraffic__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.0444 | 9.2 | 32.0 | 0.0570 | 0.1136 |
| `T9_BufferStress_SmallBufferHighTraffic__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.0444 | 9.2 | 32.0 | 0.0570 | 0.1136 |
| `T9_BufferStress_SmallBufferHighTraffic__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.0444 | 9.2 | 32.0 | 0.0570 | 0.1136 |
| `T9_BufferStress_SmallBufferHighTraffic__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.0444 | 9.2 | 32.0 | 0.0570 | 0.1136 |
| `T9_BufferStress_SmallBufferHighTraffic__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.0444 | 9.2 | 32.0 | 0.0570 | 0.1136 |
| `T9_BufferStress_SmallBufferHighTraffic__TP10_Storm` | TP10 | ConnectivityONEReport | 0.0444 | 9.2 | 32.0 | 0.0570 | 0.1136 |
| `T9_BufferStress_SmallBufferHighTraffic__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.0444 | 9.2 | 32.0 | 0.0570 | 0.1136 |
| `T9_BufferStress_SmallBufferHighTraffic__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.0444 | 9.2 | 32.0 | 0.0570 | 0.1136 |
| `U1_CBD_Commuting_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 3.0417 | 183.8 | 2190.0 | 0.3423 | 0.6155 |
| `U1_CBD_Commuting_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 2.9361 | 182.4 | 2114.0 | 0.3155 | 0.5942 |
| `U1_CBD_Commuting_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 2.7736 | 176.7 | 1997.0 | 0.3007 | 0.5608 |
| `U1_CBD_Commuting_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 2.7569 | 178.5 | 1985.0 | 0.2928 | 0.5569 |
| `U1_CBD_Commuting_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 3.0417 | 183.8 | 2190.0 | 0.3423 | 0.6155 |
| `U1_CBD_Commuting_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 3.1125 | 165.4 | 2241.0 | 0.3406 | 0.6113 |
| `U1_CBD_Commuting_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 2.8847 | 187.3 | 2077.0 | 0.3068 | 0.5757 |
| `U1_CBD_Commuting_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 3.1125 | 165.4 | 2241.0 | 0.3406 | 0.6113 |
| `U1_CBD_Commuting_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 2.8181 | 160.1 | 2029.0 | 0.2847 | 0.5399 |
| `U1_CBD_Commuting_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 3.0125 | 187.5 | 2169.0 | 0.3090 | 0.5966 |
| `U1_CBD_Commuting_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 3.1125 | 165.4 | 2241.0 | 0.3406 | 0.6113 |
| `U1_CBD_Commuting_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 2.7958 | 188.9 | 2013.0 | 0.2836 | 0.5611 |
| `U2_SparseSuburb_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.6569 | 134.1 | 473.0 | 0.4431 | 0.7200 |
| `U2_SparseSuburb_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.6569 | 134.1 | 473.0 | 0.4431 | 0.7200 |
| `U2_SparseSuburb_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.6569 | 134.1 | 473.0 | 0.4431 | 0.7200 |
| `U2_SparseSuburb_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.6569 | 134.1 | 473.0 | 0.4431 | 0.7200 |
| `U2_SparseSuburb_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.6569 | 134.1 | 473.0 | 0.4431 | 0.7200 |
| `U2_SparseSuburb_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.6875 | 153.7 | 495.0 | 0.5633 | 0.9306 |
| `U2_SparseSuburb_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.6542 | 150.1 | 471.0 | 0.5333 | 0.7917 |
| `U2_SparseSuburb_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.6875 | 153.7 | 495.0 | 0.5633 | 0.9306 |
| `U2_SparseSuburb_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.6569 | 134.1 | 473.0 | 0.4431 | 0.7200 |
| `U2_SparseSuburb_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 0.6833 | 151.3 | 492.0 | 0.4587 | 0.7436 |
| `U2_SparseSuburb_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.6875 | 153.7 | 495.0 | 0.5633 | 0.9306 |
| `U2_SparseSuburb_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.6778 | 132.0 | 488.0 | 0.4708 | 0.7200 |
| `U3_MicroMobility_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 9.8028 | 191.2 | 7058.0 | 0.2817 | 0.5240 |
| `U3_MicroMobility_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 10.0125 | 183.2 | 7209.0 | 0.2790 | 0.5259 |
| `U3_MicroMobility_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 10.0167 | 181.1 | 7212.0 | 0.2939 | 0.5670 |
| `U3_MicroMobility_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 10.3667 | 190.0 | 7464.0 | 0.3089 | 0.5777 |
| `U3_MicroMobility_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 9.8028 | 191.2 | 7058.0 | 0.2817 | 0.5240 |
| `U3_MicroMobility_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 9.9806 | 184.9 | 7186.0 | 0.2833 | 0.5322 |
| `U3_MicroMobility_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 10.0333 | 187.8 | 7224.0 | 0.3079 | 0.5601 |
| `U3_MicroMobility_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 9.9806 | 184.9 | 7186.0 | 0.2833 | 0.5322 |
| `U3_MicroMobility_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 9.8764 | 181.4 | 7111.0 | 0.2962 | 0.5632 |
| `U3_MicroMobility_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 9.9681 | 187.4 | 7177.0 | 0.2594 | 0.4959 |
| `U3_MicroMobility_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 9.9806 | 184.9 | 7186.0 | 0.2833 | 0.5322 |
| `U3_MicroMobility_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 9.9653 | 183.2 | 7175.0 | 0.2839 | 0.5374 |
| `U4_CongestionHotspot_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 1.7472 | 161.4 | 1258.0 | 0.2849 | 0.5234 |
| `U4_CongestionHotspot_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 1.8500 | 224.6 | 1332.0 | 0.3073 | 0.5678 |
| `U4_CongestionHotspot_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 1.7917 | 205.1 | 1290.0 | 0.2716 | 0.5405 |
| `U4_CongestionHotspot_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 1.7417 | 220.0 | 1254.0 | 0.2904 | 0.5706 |
| `U4_CongestionHotspot_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 1.7472 | 161.4 | 1258.0 | 0.2849 | 0.5234 |
| `U4_CongestionHotspot_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 1.7028 | 176.6 | 1226.0 | 0.2583 | 0.5144 |
| `U4_CongestionHotspot_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 1.7722 | 241.6 | 1276.0 | 0.2898 | 0.5410 |
| `U4_CongestionHotspot_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 1.7028 | 176.6 | 1226.0 | 0.2583 | 0.5144 |
| `U4_CongestionHotspot_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 1.7472 | 161.4 | 1258.0 | 0.2849 | 0.5234 |
| `U4_CongestionHotspot_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 1.7792 | 217.7 | 1281.0 | 0.2911 | 0.5690 |
| `U4_CongestionHotspot_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 1.7028 | 176.6 | 1226.0 | 0.2583 | 0.5144 |
| `U4_CongestionHotspot_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 1.8056 | 176.7 | 1300.0 | 0.2905 | 0.5833 |
| `U5_WorkdayShort_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 1.6917 | 208.5 | 1218.0 | 0.2635 | 0.5469 |
| `U5_WorkdayShort_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 1.7639 | 215.9 | 1270.0 | 0.2993 | 0.5644 |
| `U5_WorkdayShort_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 1.7653 | 244.4 | 1271.0 | 0.3071 | 0.5976 |
| `U5_WorkdayShort_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 1.7639 | 215.9 | 1270.0 | 0.2993 | 0.5644 |
| `U5_WorkdayShort_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 1.6917 | 208.5 | 1218.0 | 0.2635 | 0.5469 |
| `U5_WorkdayShort_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 1.7681 | 189.7 | 1273.0 | 0.2896 | 0.5571 |
| `U5_WorkdayShort_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 1.6972 | 211.3 | 1222.0 | 0.3000 | 0.5763 |
| `U5_WorkdayShort_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 1.7681 | 189.7 | 1273.0 | 0.2896 | 0.5571 |
| `U5_WorkdayShort_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 1.6917 | 208.5 | 1218.0 | 0.2635 | 0.5469 |
| `U5_WorkdayShort_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 1.7236 | 259.6 | 1241.0 | 0.2811 | 0.5461 |
| `U5_WorkdayShort_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 1.7681 | 189.7 | 1273.0 | 0.2896 | 0.5571 |
| `U5_WorkdayShort_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 1.8694 | 219.3 | 1346.0 | 0.2967 | 0.5738 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 1.7931 | 218.7 | 1291.0 | 0.3214 | 0.6250 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 1.7931 | 218.7 | 1291.0 | 0.3214 | 0.6250 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 1.8375 | 245.8 | 1323.0 | 0.3497 | 0.6754 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 1.7931 | 218.7 | 1291.0 | 0.3214 | 0.6250 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 1.7931 | 218.7 | 1291.0 | 0.3214 | 0.6250 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 1.6611 | 219.4 | 1196.0 | 0.3188 | 0.6333 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 1.5639 | 222.7 | 1126.0 | 0.2807 | 0.5848 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 1.6611 | 219.4 | 1196.0 | 0.3188 | 0.6333 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 1.7931 | 218.7 | 1291.0 | 0.3214 | 0.6250 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 1.5944 | 242.6 | 1148.0 | 0.3065 | 0.6212 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 1.6611 | 219.4 | 1196.0 | 0.3188 | 0.6333 |
| `U6_OfficeWaitHeavyTail_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 1.6611 | 219.4 | 1196.0 | 0.3188 | 0.6333 |
| `U7_HighTimeVariance_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 3.2931 | 206.0 | 2371.0 | 0.2729 | 0.5386 |
| `U7_HighTimeVariance_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 3.3833 | 191.2 | 2436.0 | 0.2743 | 0.5420 |
| `U7_HighTimeVariance_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 3.6528 | 203.2 | 2630.0 | 0.3139 | 0.6014 |
| `U7_HighTimeVariance_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 3.4861 | 203.1 | 2510.0 | 0.3152 | 0.6089 |
| `U7_HighTimeVariance_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 3.2931 | 206.0 | 2371.0 | 0.2729 | 0.5386 |
| `U7_HighTimeVariance_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 3.3972 | 207.1 | 2446.0 | 0.3014 | 0.5761 |
| `U7_HighTimeVariance_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 3.4750 | 209.4 | 2502.0 | 0.3157 | 0.6136 |
| `U7_HighTimeVariance_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 3.3972 | 207.1 | 2446.0 | 0.3014 | 0.5761 |
| `U7_HighTimeVariance_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 3.2931 | 206.0 | 2371.0 | 0.2729 | 0.5386 |
| `U7_HighTimeVariance_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 3.3389 | 207.7 | 2404.0 | 0.2793 | 0.5329 |
| `U7_HighTimeVariance_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 3.3972 | 207.1 | 2446.0 | 0.3014 | 0.5761 |
| `U7_HighTimeVariance_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 3.3972 | 206.4 | 2446.0 | 0.2774 | 0.5312 |
| `V1_TaxiLow_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.6236 | 6.1 | 449.0 | 0.9000 | 1.0000 |
| `V1_TaxiLow_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.5778 | 6.7 | 416.0 | 1.0000 | 1.0000 |
| `V1_TaxiLow_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.5708 | 6.2 | 411.0 | 1.0000 | 1.0000 |
| `V1_TaxiLow_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.5778 | 6.7 | 416.0 | 1.0000 | 1.0000 |
| `V1_TaxiLow_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.6236 | 6.1 | 449.0 | 0.9000 | 1.0000 |
| `V1_TaxiLow_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.9208 | 6.5 | 663.0 | 1.0000 | 1.0000 |
| `V1_TaxiLow_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.4931 | 5.8 | 355.0 | 0.9000 | 1.0000 |
| `V1_TaxiLow_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.9208 | 6.5 | 663.0 | 1.0000 | 1.0000 |
| `V1_TaxiLow_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 1.0097 | 7.1 | 727.0 | 1.0000 | 1.0000 |
| `V1_TaxiLow_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 0.5778 | 5.8 | 416.0 | 0.9000 | 1.0000 |
| `V1_TaxiLow_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.9208 | 6.5 | 663.0 | 1.0000 | 1.0000 |
| `V1_TaxiLow_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.5778 | 6.7 | 416.0 | 1.0000 | 1.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 27.4278 | 5.3 | 19748.0 | 0.9969 | 1.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 27.5694 | 5.4 | 19850.0 | 0.9908 | 1.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 26.3125 | 5.4 | 18945.0 | 0.9908 | 1.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 26.9889 | 5.5 | 19432.0 | 0.9846 | 1.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 27.4278 | 5.3 | 19748.0 | 0.9969 | 1.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 26.6639 | 5.3 | 19198.0 | 0.9877 | 1.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 26.0861 | 5.3 | 18782.0 | 0.9938 | 1.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 26.6639 | 5.3 | 19198.0 | 0.9877 | 1.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 26.7208 | 5.3 | 19239.0 | 0.9785 | 1.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 28.0389 | 5.5 | 20188.0 | 0.9785 | 1.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 26.6639 | 5.3 | 19198.0 | 0.9877 | 1.0000 |
| `V2_TaxiHigh_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 26.7681 | 5.3 | 19273.0 | 0.9846 | 1.0000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 0.7806 | 8.7 | 562.0 | 0.4643 | 0.5714 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 0.9736 | 9.6 | 701.0 | 0.4167 | 0.5000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 0.6375 | 7.6 | 459.0 | 0.4167 | 0.5000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 0.8861 | 9.0 | 638.0 | 0.4444 | 0.5000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 0.7806 | 8.7 | 562.0 | 0.4643 | 0.5714 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 0.9375 | 8.6 | 675.0 | 0.3889 | 0.5000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 0.7500 | 9.1 | 540.0 | 0.4167 | 0.5000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 0.9375 | 8.6 | 675.0 | 0.3889 | 0.5000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 0.7806 | 8.7 | 562.0 | 0.4643 | 0.5714 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 1.0139 | 9.5 | 730.0 | 0.4167 | 0.5000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 0.9375 | 8.6 | 675.0 | 0.3889 | 0.5000 |
| `V3_BusOnlyCarriers_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 0.7750 | 9.0 | 558.0 | 0.4167 | 0.5000 |
| `V4_CarOwnership_0_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 4.4444 | 281.7 | 3200.0 | 0.3847 | 0.6853 |
| `V4_CarOwnership_0_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 4.5042 | 291.5 | 3243.0 | 0.3905 | 0.6646 |
| `V4_CarOwnership_0_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 4.4903 | 278.4 | 3233.0 | 0.3867 | 0.6804 |
| `V4_CarOwnership_0_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 4.5042 | 291.5 | 3243.0 | 0.3905 | 0.6646 |
| `V4_CarOwnership_0_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 4.4444 | 281.7 | 3200.0 | 0.3847 | 0.6853 |
| `V4_CarOwnership_0_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 4.4500 | 276.1 | 3204.0 | 0.3731 | 0.6729 |
| `V4_CarOwnership_0_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 4.3542 | 284.5 | 3135.0 | 0.3768 | 0.6849 |
| `V4_CarOwnership_0_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 4.4500 | 276.1 | 3204.0 | 0.3731 | 0.6729 |
| `V4_CarOwnership_0_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 4.4444 | 281.7 | 3200.0 | 0.3847 | 0.6853 |
| `V4_CarOwnership_0_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 4.3833 | 289.2 | 3156.0 | 0.3725 | 0.6660 |
| `V4_CarOwnership_0_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 4.4500 | 276.1 | 3204.0 | 0.3731 | 0.6729 |
| `V4_CarOwnership_0_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 4.5097 | 290.1 | 3247.0 | 0.3562 | 0.6507 |
| `V5_CarOwnership_100_HelsinkiMedium__TP01_Baseline` | TP01 | ConnectivityONEReport | 2.8944 | 179.8 | 2084.0 | 0.1514 | 0.3772 |
| `V5_CarOwnership_100_HelsinkiMedium__TP02_LowLoad` | TP02 | ConnectivityONEReport | 2.9250 | 199.4 | 2106.0 | 0.1520 | 0.3463 |
| `V5_CarOwnership_100_HelsinkiMedium__TP03_ManySmall` | TP03 | ConnectivityONEReport | 2.9069 | 181.3 | 2093.0 | 0.1452 | 0.3485 |
| `V5_CarOwnership_100_HelsinkiMedium__TP04_FewLarge` | TP04 | ConnectivityONEReport | 2.8778 | 180.2 | 2072.0 | 0.1488 | 0.3560 |
| `V5_CarOwnership_100_HelsinkiMedium__TP05_CriticalTTL` | TP05 | ConnectivityONEReport | 2.8944 | 179.8 | 2084.0 | 0.1514 | 0.3772 |
| `V5_CarOwnership_100_HelsinkiMedium__TP06_OneToMany` | TP06 | ConnectivityONEReport | 2.8042 | 180.9 | 2019.0 | 0.1413 | 0.3549 |
| `V5_CarOwnership_100_HelsinkiMedium__TP07_BurstWindow` | TP07 | ConnectivityONEReport | 2.9431 | 173.3 | 2119.0 | 0.1384 | 0.3268 |
| `V5_CarOwnership_100_HelsinkiMedium__TP08_HubTarget` | TP08 | ConnectivityONEReport | 2.8042 | 180.9 | 2019.0 | 0.1413 | 0.3549 |
| `V5_CarOwnership_100_HelsinkiMedium__TP09_Bimodal` | TP09 | ConnectivityONEReport | 2.8403 | 180.1 | 2045.0 | 0.1558 | 0.3348 |
| `V5_CarOwnership_100_HelsinkiMedium__TP10_Storm` | TP10 | ConnectivityONEReport | 2.7542 | 201.4 | 1983.0 | 0.1543 | 0.3750 |
| `V5_CarOwnership_100_HelsinkiMedium__TP11_ManyToOne` | TP11 | ConnectivityONEReport | 2.8042 | 180.9 | 2019.0 | 0.1413 | 0.3549 |
| `V5_CarOwnership_100_HelsinkiMedium__TP12_GroupToGroup` | TP12 | ConnectivityONEReport | 2.8403 | 197.6 | 2045.0 | 0.1291 | 0.3011 |
