## Rural scenarios (12)

This page summarizes the **Rural** family scenarios and links to the full per-scenario documentation pages (EN). These scenarios cover complementary DTN regimes under sparse rural conditions: baseline RandomWaypoint, village clusters, wildlife tracking, park rangers on routes, mountain rescue, extreme range (200 m / 5 m), buffer stress, intermittent power, and extreme speed (low/high).

### Index

| ID | Scenario (page) | Settings file | Core idea |
|----|-----------------|---------------|-----------|
| R1 | [R1_Rural_RandomWaypoint](scenarios-en/rural/R1_Rural_RandomWaypoint) | `corpus_v1/04_rural/R1_Rural_RandomWaypoint.settings` | Large world, few nodes, RandomWaypoint baseline |
| R2 | [R2_VillagesTrails_ThreeClusters](scenarios-en/rural/R2_VillagesTrails_ThreeClusters) | `corpus_v1/04_rural/R2_VillagesTrails_ThreeClusters.settings` | Three village clusters, ClusterMovement |
| R3 | [R3_WildlifeTracking](scenarios-en/rural/R3_WildlifeTracking) | `corpus_v1/04_rural/R3_WildlifeTracking.settings` | Very low speed, long TTL, low event rate |
| R4 | [R4_ParkRangers_HelsinkiMedium](scenarios-en/rural/R4_ParkRangers_HelsinkiMedium) | `corpus_v1/04_rural/R4_ParkRangers_HelsinkiMedium.settings` | MapRouteMovement mules on long route |
| R5 | [R5_MountainRescue](scenarios-en/rural/R5_MountainRescue) | `corpus_v1/04_rural/R5_MountainRescue.settings` | Critical small messages, short TTL |
| R6 | [R6_SparseLongRange](scenarios-en/rural/R6_SparseLongRange) | `corpus_v1/04_rural/R6_SparseLongRange.settings` | Sparse + transmitRange 200 m (LoRa-like) |
| R7 | [R7_SparseTinyBuffer](scenarios-en/rural/R7_SparseTinyBuffer) | `corpus_v1/04_rural/R7_SparseTinyBuffer.settings` | Tiny buffer (500k), buffer stress |
| R8 | [R8_IntermittentPower](scenarios-en/rural/R8_IntermittentPower) | `corpus_v1/04_rural/R8_IntermittentPower.settings` | activeTimes: nodes sleep part of the time |
| R9 | [R9_ExtremeRange_200m](scenarios-en/rural/R9_ExtremeRange_200m) | `corpus_v1/04_rural/R9_ExtremeRange_200m.settings` | transmitRange 200 m, quasi fully connected |
| R10 | [R10_TinyRange_5m](scenarios-en/rural/R10_TinyRange_5m) | `corpus_v1/04_rural/R10_TinyRange_5m.settings` | transmitRange 5 m, very sparse graph |
| R11 | [R11_SpeedExtremeLow](scenarios-en/rural/R11_SpeedExtremeLow) | `corpus_v1/04_rural/R11_SpeedExtremeLow.settings` | Speed 0.2–0.3 m/s, minimum speed |
| R12 | [R12_SpeedExtremeHigh](scenarios-en/rural/R12_SpeedExtremeHigh) | `corpus_v1/04_rural/R12_SpeedExtremeHigh.settings` | Speed 12–15 m/s, maximum speed |
