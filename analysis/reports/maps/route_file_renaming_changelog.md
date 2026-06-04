# Route file renaming changelog

Date: 2026-05-28T17:34:26
Mode: apply

## File renames

- `KumpulaCampus/A_bus.wkt` → `KumpulaCampus/A_campus_shuttle.wkt`
- `ManhattanMidtownGrid/A_bus.wkt` → `ManhattanMidtownGrid/A_vehicle_route.wkt`
- `ManhattanMidtownGrid/B_bus.wkt` → `ManhattanMidtownGrid/B_vehicle_route.wkt`
- `NuuksioSparseTrails/A_bus.wkt` → `NuuksioSparseTrails/A_ranger_patrol.wkt`
- `HelsinkiDisrupted/A_bus.wkt` → `HelsinkiDisrupted/A_emergency_route.wkt`
- `HelsinkiDisrupted/B_bus.wkt` → `HelsinkiDisrupted/B_mule_route.wkt`
- `KallioCommunityCompact/A_bus.wkt` → `KallioCommunityCompact/A_community_route.wkt`
- `KallioCommunityCompact/B_bus.wkt` → `KallioCommunityCompact/B_community_route.wkt`
- `/A_bus.wkt` → `/A_control_route.wkt`

## Settings updates

- `scenarios/base_scenarios/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/base_scenarios/03_vehicles/V2_TaxiHigh_ManhattanMidtownGrid.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/base_scenarios/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/base_scenarios/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid.settings`: `data/ManhattanMidtownGrid/B_bus.wkt` → `data/ManhattanMidtownGrid/B_vehicle_route.wkt`
- `scenarios/base_scenarios/03_vehicles/V4_CarOwnership_0_ManhattanMidtownGrid.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/base_scenarios/03_vehicles/V4_CarOwnership_0_ManhattanMidtownGrid.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/base_scenarios/03_vehicles/V4_CarOwnership_0_ManhattanMidtownGrid.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/base_scenarios/03_vehicles/V5_CarOwnership_100_ManhattanMidtownGrid.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/base_scenarios/03_vehicles/V5_CarOwnership_100_ManhattanMidtownGrid.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/base_scenarios/03_vehicles/V5_CarOwnership_100_ManhattanMidtownGrid.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/base_scenarios/04_rural/R4_ParkRangers_NuuksioSparseTrails.settings`: `data/NuuksioSparseTrails/A_bus.wkt` → `data/NuuksioSparseTrails/A_ranger_patrol.wkt`
- `scenarios/base_scenarios/05_disaster/D5_UAVMule_FastRoute_HelsinkiDisrupted.settings`: `data/HelsinkiDisrupted/A_bus.wkt` → `data/HelsinkiDisrupted/A_emergency_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid__TP01_Baseline.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid__TP02_LowLoad.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid__TP03_ManySmall.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid__TP04_FewLarge.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid__TP05_CriticalTTL.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid__TP06_OneToMany.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid__TP07_BurstWindow.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid__TP08_HubTarget.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid__TP09_Bimodal.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid__TP10_Storm.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid__TP11_ManyToOne.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid__TP12_GroupToGroup.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V2_TaxiHigh_ManhattanMidtownGrid__TP01_Baseline.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V2_TaxiHigh_ManhattanMidtownGrid__TP02_LowLoad.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V2_TaxiHigh_ManhattanMidtownGrid__TP03_ManySmall.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V2_TaxiHigh_ManhattanMidtownGrid__TP04_FewLarge.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V2_TaxiHigh_ManhattanMidtownGrid__TP05_CriticalTTL.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V2_TaxiHigh_ManhattanMidtownGrid__TP06_OneToMany.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V2_TaxiHigh_ManhattanMidtownGrid__TP07_BurstWindow.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V2_TaxiHigh_ManhattanMidtownGrid__TP08_HubTarget.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V2_TaxiHigh_ManhattanMidtownGrid__TP09_Bimodal.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V2_TaxiHigh_ManhattanMidtownGrid__TP10_Storm.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V2_TaxiHigh_ManhattanMidtownGrid__TP11_ManyToOne.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V2_TaxiHigh_ManhattanMidtownGrid__TP12_GroupToGroup.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP01_Baseline.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP01_Baseline.settings`: `data/ManhattanMidtownGrid/B_bus.wkt` → `data/ManhattanMidtownGrid/B_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP02_LowLoad.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP02_LowLoad.settings`: `data/ManhattanMidtownGrid/B_bus.wkt` → `data/ManhattanMidtownGrid/B_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP03_ManySmall.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP03_ManySmall.settings`: `data/ManhattanMidtownGrid/B_bus.wkt` → `data/ManhattanMidtownGrid/B_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP04_FewLarge.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP04_FewLarge.settings`: `data/ManhattanMidtownGrid/B_bus.wkt` → `data/ManhattanMidtownGrid/B_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP05_CriticalTTL.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP05_CriticalTTL.settings`: `data/ManhattanMidtownGrid/B_bus.wkt` → `data/ManhattanMidtownGrid/B_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP06_OneToMany.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP06_OneToMany.settings`: `data/ManhattanMidtownGrid/B_bus.wkt` → `data/ManhattanMidtownGrid/B_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP07_BurstWindow.settings`: `data/ManhattanMidtownGrid/A_bus.wkt` → `data/ManhattanMidtownGrid/A_vehicle_route.wkt`
- `scenarios/corpus_v1/03_vehicles/V3_BusOnlyCarriers_ManhattanMidtownGrid__TP07_BurstWindow.settings`: `data/ManhattanMidtownGrid/B_bus.wkt` → `data/ManhattanMidtownGrid/B_vehicle_route.wkt`
- … and 106 more substitutions

Total settings files touched: 91
Disk rename operations: 9