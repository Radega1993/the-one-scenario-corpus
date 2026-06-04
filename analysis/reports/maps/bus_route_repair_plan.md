# Bus route repair plan

Generated: 2026-05-28T17:36:28

## Routes to repair

| Map | Route | Before | Strategy | Auto | Scenarios affected |
|-----|-------|--------|----------|------|-------------------|
| HelsinkiDowntown | A_bus.wkt | WARNING | A_graph_tour | yes | see route_usage_by_scenario.csv |
| HelsinkiDowntown | B_bus.wkt | WARNING | A_graph_tour | yes | see route_usage_by_scenario.csv |
| HelsinkiDowntown | C_bus.wkt | WARNING | A_graph_tour | yes | see route_usage_by_scenario.csv |
| KumpulaCampus | A_campus_shuttle.wkt | WARNING | A_graph_tour | yes | see route_usage_by_scenario.csv |
| ManhattanMidtownGrid | A_vehicle_route.wkt | FAIL | A_graph_tour | yes | see route_usage_by_scenario.csv |
| ManhattanMidtownGrid | B_vehicle_route.wkt | WARNING | A_graph_tour | yes | see route_usage_by_scenario.csv |
| NuuksioSparseTrails | A_ranger_patrol.wkt | WARNING | A_graph_tour | yes | see route_usage_by_scenario.csv |
| HelsinkiDisrupted | A_emergency_route.wkt | WARNING | A_graph_tour | yes | see route_usage_by_scenario.csv |
| HelsinkiDisrupted | B_mule_route.wkt | WARNING | A_graph_tour | yes | see route_usage_by_scenario.csv |
| KallioCommunityCompact | A_community_route.wkt | FAIL | A_graph_tour | yes | see route_usage_by_scenario.csv |
| KallioCommunityCompact | B_community_route.wkt | WARNING | A_graph_tour | yes | see route_usage_by_scenario.csv |

## Re-simulation

Repairing bus/taxi waypoints may change carrier trajectories. Re-run simulations for scenarios referencing repaired routes (urban, vehicles, R4, D5) before publishing new protocol KPIs.