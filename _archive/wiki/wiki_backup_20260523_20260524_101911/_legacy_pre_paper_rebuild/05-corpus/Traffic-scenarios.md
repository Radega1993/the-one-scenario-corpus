## Traffic scenarios (15)

This page summarizes the **Traffic** family scenarios and links to the full per-scenario documentation pages (EN). These scenarios focus on message and resource diversity: size (small/large/mixed), rate, TTL (short/long/infinite), buffer, transmit speed, and patterns (uniform, burst, hub-target).

### Index

| ID | Scenario (page) | Settings file | Core idea |
|----|-----------------|---------------|-----------|
| T1 | [T1_ManySmallMsgs_HighRate](scenarios-en/traffic/T1_ManySmallMsgs_HighRate) | `corpus_v1/07_traffic/T1_ManySmallMsgs_HighRate.settings` | Many small msgs, high rate |
| T2 | [T2_FewHugeMsgs_LowRate](scenarios-en/traffic/T2_FewHugeMsgs_LowRate) | `corpus_v1/07_traffic/T2_FewHugeMsgs_LowRate.settings` | Few huge msgs, low rate |
| T3 | [T3_MixedBimodal_SmallAndLarge](scenarios-en/traffic/T3_MixedBimodal_SmallAndLarge) | `corpus_v1/07_traffic/T3_MixedBimodal_SmallAndLarge.settings` | Mixed small + large |
| T4 | [T4_VeryShortTtl_5to10min](scenarios-en/traffic/T4_VeryShortTtl_5to10min) | `corpus_v1/07_traffic/T4_VeryShortTtl_5to10min.settings` | Very short TTL (5–10 min) |
| T5 | [T5_VeryLongTtl_6to24h](scenarios-en/traffic/T5_VeryLongTtl_6to24h) | `corpus_v1/07_traffic/T5_VeryLongTtl_6to24h.settings` | Very long TTL (6–24 h) |
| T6 | [T6_UniformSources_RandomFromTo](scenarios-en/traffic/T6_UniformSources_RandomFromTo) | `corpus_v1/07_traffic/T6_UniformSources_RandomFromTo.settings` | Uniform random sources |
| T7 | [T7_TargetedToHubs_FewDestinations](scenarios-en/traffic/T7_TargetedToHubs_FewDestinations) | `corpus_v1/07_traffic/T7_TargetedToHubs_FewDestinations.settings` | Hub-target traffic |
| T8 | [T8_BurstTraffic_TimeWindows](scenarios-en/traffic/T8_BurstTraffic_TimeWindows) | `corpus_v1/07_traffic/T8_BurstTraffic_TimeWindows.settings` | Burst traffic windows |
| T9 | [T9_BufferStress_SmallBufferHighTraffic](scenarios-en/traffic/T9_BufferStress_SmallBufferHighTraffic) | `corpus_v1/07_traffic/T9_BufferStress_SmallBufferHighTraffic.settings` | Buffer stress |
| T10 | [T10_HighRateLowSpeed_Congestion](scenarios-en/traffic/T10_HighRateLowSpeed_Congestion) | `corpus_v1/07_traffic/T10_HighRateLowSpeed_Congestion.settings` | Congestion regime |
| T11 | [T11_TTL_1min](scenarios-en/traffic/T11_TTL_1min) | `corpus_v1/07_traffic/T11_TTL_1min.settings` | Extreme 1-min TTL |
| T12 | [T12_TTL_Infinite_Buffer200M](scenarios-en/traffic/T12_TTL_Infinite_Buffer200M) | `corpus_v1/07_traffic/T12_TTL_Infinite_Buffer200M.settings` | Infinite TTL, 200 MB buffer |
| T13 | [T13_Buffer_256k](scenarios-en/traffic/T13_Buffer_256k) | `corpus_v1/07_traffic/T13_Buffer_256k.settings` | Tiny buffer (256 KB) |
| T14 | [T14_Buffer_200M](scenarios-en/traffic/T14_Buffer_200M) | `corpus_v1/07_traffic/T14_Buffer_200M.settings` | Large buffer (200 MB) |
| T15 | [T15_TransmitSpeed_256k](scenarios-en/traffic/T15_TransmitSpeed_256k) | `corpus_v1/07_traffic/T15_TransmitSpeed_256k.settings` | Low transmit speed (256 kbps) |
