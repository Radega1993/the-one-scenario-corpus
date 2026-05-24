## Escenarios Traffic (15)

Esta página resume los escenarios de la familia **Traffic** y enlaza a la documentación detallada de cada uno (ES). Estos escenarios se centran en diversidad de mensajes y recursos: tamaño (pequeño/grande/mixto), tasa, TTL (corto/largo/infinito), buffer, velocidad de transmisión y patrones (uniforme, burst, hub-target).

### Índice

| ID | Escenario (página) | Fichero settings | Idea core |
|----|-------------------|------------------|-----------|
| T1 | [T1_ManySmallMsgs_HighRate](scenarios-es/traffic/T1_ManySmallMsgs_HighRate-es) | `corpus_v1/07_traffic/T1_ManySmallMsgs_HighRate.settings` | Muchos mensajes pequeños, alta tasa |
| T2 | [T2_FewHugeMsgs_LowRate](scenarios-es/traffic/T2_FewHugeMsgs_LowRate-es) | `corpus_v1/07_traffic/T2_FewHugeMsgs_LowRate.settings` | Pocos mensajes grandes, baja tasa |
| T3 | [T3_MixedBimodal_SmallAndLarge](scenarios-es/traffic/T3_MixedBimodal_SmallAndLarge-es) | `corpus_v1/07_traffic/T3_MixedBimodal_SmallAndLarge.settings` | Mezcla pequeño + grande |
| T4 | [T4_VeryShortTtl_5to10min](scenarios-es/traffic/T4_VeryShortTtl_5to10min-es) | `corpus_v1/07_traffic/T4_VeryShortTtl_5to10min.settings` | TTL muy corto (5–10 min) |
| T5 | [T5_VeryLongTtl_6to24h](scenarios-es/traffic/T5_VeryLongTtl_6to24h-es) | `corpus_v1/07_traffic/T5_VeryLongTtl_6to24h.settings` | TTL muy largo (6–24 h) |
| T6 | [T6_UniformSources_RandomFromTo](scenarios-es/traffic/T6_UniformSources_RandomFromTo-es) | `corpus_v1/07_traffic/T6_UniformSources_RandomFromTo.settings` | Fuentes uniformes aleatorias |
| T7 | [T7_TargetedToHubs_FewDestinations](scenarios-es/traffic/T7_TargetedToHubs_FewDestinations-es) | `corpus_v1/07_traffic/T7_TargetedToHubs_FewDestinations.settings` | Tráfico hub-target |
| T8 | [T8_BurstTraffic_TimeWindows](scenarios-es/traffic/T8_BurstTraffic_TimeWindows-es) | `corpus_v1/07_traffic/T8_BurstTraffic_TimeWindows.settings` | Ventanas de tráfico burst |
| T9 | [T9_BufferStress_SmallBufferHighTraffic](scenarios-es/traffic/T9_BufferStress_SmallBufferHighTraffic-es) | `corpus_v1/07_traffic/T9_BufferStress_SmallBufferHighTraffic.settings` | Estrés de buffer |
| T10 | [T10_HighRateLowSpeed_Congestion](scenarios-es/traffic/T10_HighRateLowSpeed_Congestion-es) | `corpus_v1/07_traffic/T10_HighRateLowSpeed_Congestion.settings` | Régimen de congestión |
| T11 | [T11_TTL_1min](scenarios-es/traffic/T11_TTL_1min-es) | `corpus_v1/07_traffic/T11_TTL_1min.settings` | TTL extremo de 1 min |
| T12 | [T12_TTL_Infinite_Buffer200M](scenarios-es/traffic/T12_TTL_Infinite_Buffer200M-es) | `corpus_v1/07_traffic/T12_TTL_Infinite_Buffer200M.settings` | TTL infinito, buffer 200 MB |
| T13 | [T13_Buffer_256k](scenarios-es/traffic/T13_Buffer_256k-es) | `corpus_v1/07_traffic/T13_Buffer_256k.settings` | Buffer pequeño (256 KB) |
| T14 | [T14_Buffer_200M](scenarios-es/traffic/T14_Buffer_200M-es) | `corpus_v1/07_traffic/T14_Buffer_200M.settings` | Buffer grande (200 MB) |
| T15 | [T15_TransmitSpeed_256k](scenarios-es/traffic/T15_TransmitSpeed_256k-es) | `corpus_v1/07_traffic/T15_TransmitSpeed_256k.settings` | Baja velocidad de transmisión (256 kbps) |
