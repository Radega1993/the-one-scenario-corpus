# base_scenarios validation

- **Expected count:** 45
- **Found:** 45
- **OK:** 0
- **Fail:** 45

Detail: `scenarios/analysis/data/base_scenarios_validation.csv`

## Failures
- `U1_CBD_Commuting_HelsinkiDowntown`: worldSize_mismatch:got=1713,1459,exp=1793,1538
- `U2_SparseUrban_HelsinkiDowntown`: worldSize_mismatch:got=1713,1459,exp=1793,1538; no_corpus_v1_TP_variants
- `U3_MicroMobility_HelsinkiDowntown`: worldSize_mismatch:got=1713,1459,exp=1793,1538
- `U4_CongestionHotspot_HelsinkiDowntown`: worldSize_mismatch:got=1713,1459,exp=1793,1538
- `U5_WorkdayShort_HelsinkiDowntown`: worldSize_mismatch:got=1713,1459,exp=1793,1538
- `U6_OfficeWaitHeavyTail_HelsinkiDowntown`: worldSize_mismatch:got=1713,1459,exp=1793,1538
- `U7_HighTimeVariance_HelsinkiDowntown`: worldSize_mismatch:got=1713,1459,exp=1793,1538
- `C1_Campus_ClassChange`: worldSize_mismatch:got=1148,1036,exp=1227,1116
- `C2_ExamDay_LongStays`: worldSize_mismatch:got=1148,1036,exp=1227,1116
- `C3_Hackathon_24h`: worldSize_mismatch:got=1148,1036,exp=1227,1116
- `C4_CampusEvent_IngressEgress`: worldSize_mismatch:got=1148,1036,exp=1227,1116; no_corpus_v1_TP_variants
- `C5_Library_Quiet`: worldSize_mismatch:got=1148,1036,exp=1227,1116
- `C6_EmergencyDrill_Evacuation`: worldSize_mismatch:got=1148,1036,exp=1227,1116
- `V1_TaxiLow_ManhattanMidtownGridMidtownGrid`: worldSize_mismatch:got=2120,1986,exp=2199,2066; no_corpus_v1_TP_variants
- `V2_TaxiHigh_ManhattanMidtownGridMidtownGrid`: worldSize_mismatch:got=2120,1986,exp=2199,2066; no_corpus_v1_TP_variants
- `V3_BusOnlyCarriers_ManhattanMidtownGridMidtownGrid`: worldSize_mismatch:got=2120,1986,exp=2199,2066; no_corpus_v1_TP_variants
- `V4_CarOwnership_0_ManhattanMidtownGridMidtownGrid`: worldSize_mismatch:got=2120,1986,exp=2199,2066; no_corpus_v1_TP_variants
- `V5_CarOwnership_100_ManhattanMidtownGridMidtownGrid`: worldSize_mismatch:got=2120,1986,exp=2199,2066; no_corpus_v1_TP_variants
- `R10_TinyRange_5m`: worldSize_mismatch:got=2470,2565,exp=2550,2644
- `R11_SpeedExtremeLow`: worldSize_mismatch:got=2470,2565,exp=2550,2644
- `R12_SpeedExtremeHigh`: worldSize_mismatch:got=2470,2565,exp=2550,2644
- `R1_Rural_SparseSPMM`: worldSize_mismatch:got=2470,2565,exp=2550,2644; no_corpus_v1_TP_variants
- `R2_VillagesTrails_InterVillage`: worldSize_mismatch:got=2470,2565,exp=2550,2644
- `R3_WildlifeTracking`: worldSize_mismatch:got=2470,2565,exp=2550,2644
- `R4_ParkRangers_NuuksioSparseTrails`: worldSize_mismatch:got=2470,2565,exp=2550,2644
- `R5_MountainRescue`: worldSize_mismatch:got=2470,2565,exp=2550,2644
- `R6_SparseLongRange`: worldSize_mismatch:got=2470,2565,exp=2550,2644
- `R7_SparseTinyBuffer`: worldSize_mismatch:got=2470,2565,exp=2550,2644
- `R8_IntermittentPower`: worldSize_mismatch:got=2470,2565,exp=2550,2644
- `R9_ExtremeRange_200m`: worldSize_mismatch:got=2470,2565,exp=2550,2644
- `D1_ShelterHotspots_EmergencyMobility`: worldSize_mismatch:got=1711,1874,exp=1790,1953
- `D2_PartitionedCity_MuleBridge`: worldSize_mismatch:got=1711,1874,exp=1790,1953
- `D3_Aftershock_ErraticMobility`: worldSize_mismatch:got=1711,1874,exp=1790,1953
- `D4_MedicalTriage_TwoClasses`: worldSize_mismatch:got=1711,1874,exp=1790,1953
- `D5_UAVMule_FastRoute_HelsinkiDisrupted`: worldSize_mismatch:got=1711,1874,exp=1790,1953
- `D6_ShortTtlCritical_5to10min`: worldSize_mismatch:got=1711,1874,exp=1790,1953
- `D7_HighLoad_TrafficStorm`: worldSize_mismatch:got=1711,1874,exp=1790,1953
- `D8_InfrastructureReturns_BackboneLinks`: worldSize_mismatch:got=1711,1874,exp=1790,1953
- `D9_Critical_1minTTL`: worldSize_mismatch:got=1711,1874,exp=1790,1953
- `S1_StrongCommunities_LimitedMixing`: worldSize_mismatch:got=1124,1149,exp=1203,1228
- `S2_WeakCommunities_HighMixing`: worldSize_mismatch:got=1124,1149,exp=1203,1228
- `S3_PeriodicMeetings_RegularRhythm`: worldSize_mismatch:got=1124,1149,exp=1203,1228
- `S4_RandomMixing_NoHotspots`: worldSize_mismatch:got=1124,1149,exp=1203,1228
- `S5_TwoLayer_StudentsStaff`: worldSize_mismatch:got=1124,1149,exp=1203,1228
- `S6_FamilyGroups_LocalRoutines`: worldSize_mismatch:got=1124,1149,exp=1203,1228
