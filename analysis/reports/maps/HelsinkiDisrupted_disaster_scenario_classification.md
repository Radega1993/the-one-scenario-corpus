# HelsinkiDisrupted — disaster scenario classification

Generated: 2026-05-28T18:21:16

- Base scenarios: 9
- `disaster_realistic`: 4
- `disaster_bridge_or_mule`: 2
- `disaster_critical_ttl`: 2
- `disaster_stress_control`: 1

## Methodological note

HelsinkiDisrupted is used as a degraded urban disaster map. Low delivery, high latency, and structural partitioning can be expected outcomes in specific scenarios and should not be interpreted as configuration errors by default.

## Narrative scenarios

| ID | Movement | Routes | Notes |
|----|----------|--------|-------|
| D1_ShelterHotspots_Clusters | ClusterMovement | — | Shelter hotspots via ClusterMovement groups |
| D3_Aftershock_ErraticMobility | ShortestPathMapBasedMovement | — | Erratic SPMM after aftershock |
| D4_MedicalTriage_TwoClasses | ShortestPathMapBasedMovement | — | Medical vs civilian groups; short TTL for med class |
| D8_InfrastructureReturns_BackboneLinks | ClusterMovement | — | Infrastructure return via clusters (no route WKT in settings) |
| D2_PartitionedCity_MuleBridge | ClusterMovement | — | Two partitions + SPMM mule bridge (no B_mule_route in settings) |
| D5_UAVMule_FastRoute_HelsinkiDisrupted | MapRouteMovement | A_emergency | UAV on A_emergency_route; civilians SPMM on streets |

## TTL / stress controls

| ID | Category | Lever |
|----|----------|-------|
| D6_ShortTtlCritical_5to10min | disaster_critical_ttl | TTL/load — msgTtl 7 min; endTime 14400 — critical comms window |
| D9_Critical_1minTTL | disaster_critical_ttl | TTL/load — msgTtl 1 min — extreme critical control |
| D7_HighLoad_TrafficStorm | disaster_stress_control | TTL/load — 70 hosts, 16M buffer — load/congestion stress |
