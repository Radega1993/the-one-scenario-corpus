# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **137**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 33 | 0.15 |
| HelsinkiDowntown | 21,600 | 23 | 0.11 |
| KallioCommunityCompact | 14,400 | 27 | 0.19 |
| KumpulaCampus | 7,200 | 6 | 0.08 |
| ManhattanMidtownGrid | 21,600 | 26 | 0.12 |
| NuuksioSparseTrails | 14,400 | 22 | 0.15 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 29 | 0.20 |
| ClusterMovement | 7,200 | 14 | 0.19 |
| MapRouteMovement | 28,800 | 47 | 0.16 |
| ShortestPathMapBasedMovement | 43,200 | 44 | 0.10 |
| WorkingDayMovement | 7,200 | 3 | 0.04 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 24 | 0.12 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 42 | 0.21 |
| pedestrian_transit | 20,160 | 32 | 0.16 |
| pedestrian_vehicle | 20,160 | 11 | 0.05 |
| single_homogeneous | 20,160 | 28 | 0.14 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 12 | 0.14 |
| 120 | 8,400 | 10 | 0.12 |
| 150 | 8,400 | 14 | 0.17 |
| 200 | 8,400 | 14 | 0.17 |
| 250 | 8,400 | 13 | 0.15 |
| 30 | 8,400 | 13 | 0.15 |
| 300 | 8,400 | 25 | 0.30 |
| 40 | 8,400 | 9 | 0.11 |
| 50 | 8,400 | 4 | 0.05 |
| 60 | 8,400 | 9 | 0.11 |
| 70 | 8,400 | 8 | 0.10 |
| 80 | 8,400 | 6 | 0.07 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 24 | 0.14 |
| 151-200 | 8,400 | 14 | 0.17 |
| 61-100 | 25,200 | 26 | 0.10 |
| <=60 | 33,600 | 35 | 0.10 |
| >200 | 16,800 | 38 | 0.23 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 46 | 0.16 |
| medium | 2,400 | 7 | 0.29 |
| very_low | 69,600 | 84 | 0.12 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 16 | 0.10 |
| 100 | 16,800 | 24 | 0.14 |
| 20 | 16,800 | 13 | 0.08 |
| 200 | 16,800 | 46 | 0.27 |
| 5 | 16,800 | 19 | 0.11 |
| 50 | 16,800 | 19 | 0.11 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 46 | 0.18 |
| 20M | 25,200 | 25 | 0.10 |
| 50M | 25,200 | 35 | 0.14 |
| 5M | 25,200 | 31 | 0.12 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 14 | 0.19 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 14 | 0.19 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 5 | 0.07 |
| HelsinkiDowntown|BusMovement | 7,200 | 15 | 0.21 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 5 | 0.07 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 3 | 0.04 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 15 | 0.21 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 12 | 0.17 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 6 | 0.08 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 14 | 0.19 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 7 | 0.10 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 5 | 0.07 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 11 | 0.15 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 11 | 0.15 |

