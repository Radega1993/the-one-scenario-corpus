# Traffic scenarios

**English** | [Español](Traffic-scenarios-es)

---

Message and resource extremes: many small / few huge messages, bimodal, short/long TTL, uniform sources, targeted to hubs, burst, buffer stress, high rate + low speed; radical: TTL 1min, TTL infinite + buffer 200M, buffer 256k/200M, transmitSpeed 256k.

| ID | Scenario name |
|----|----------------|
| T1 | T1_ManySmallMsgs_HighRate |
| T2 | T2_FewHugeMsgs_LowRate |
| T3 | T3_MixedBimodal_SmallAndLarge |
| T4 | T4_VeryShortTtl_5to10min |
| T5 | T5_VeryLongTtl_6to24h |
| T6 | T6_UniformSources_RandomFromTo |
| T7 | T7_TargetedToHubs_FewDestinations |
| T8 | T8_BurstTraffic_TimeWindows |
| T9 | T9_BufferStress_SmallBufferHighTraffic |
| T10 | T10_HighRateLowSpeed_Congestion |
| T11 | T11_TTL_1min |
| T12 | T12_TTL_Infinite_Buffer200M |
| T13 | T13_Buffer_256k |
| T14 | T14_Buffer_200M |
| T15 | T15_TransmitSpeed_256k |

**Folder:** `corpus_v1/07_traffic/`  
**See:** [Scenario catalog](Scenario-catalog) | [Corpus overview](Corpus-overview)
