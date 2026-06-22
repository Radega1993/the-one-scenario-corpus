# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **209**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 52 | 0.24 |
| HelsinkiDowntown | 21,600 | 32 | 0.15 |
| KallioCommunityCompact | 14,400 | 38 | 0.26 |
| KumpulaCampus | 7,200 | 14 | 0.19 |
| ManhattanMidtownGrid | 21,600 | 47 | 0.22 |
| NuuksioSparseTrails | 14,400 | 26 | 0.18 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 47 | 0.33 |
| ClusterMovement | 7,200 | 18 | 0.25 |
| MapRouteMovement | 28,800 | 73 | 0.25 |
| ShortestPathMapBasedMovement | 43,200 | 68 | 0.16 |
| WorkingDayMovement | 7,200 | 3 | 0.04 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 40 | 0.20 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 71 | 0.35 |
| pedestrian_transit | 20,160 | 51 | 0.25 |
| pedestrian_vehicle | 20,160 | 19 | 0.09 |
| single_homogeneous | 20,160 | 28 | 0.14 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 17 | 0.20 |
| 120 | 8,400 | 16 | 0.19 |
| 150 | 8,400 | 22 | 0.26 |
| 200 | 8,400 | 27 | 0.32 |
| 250 | 8,400 | 26 | 0.31 |
| 30 | 8,400 | 12 | 0.14 |
| 300 | 8,400 | 23 | 0.27 |
| 40 | 8,400 | 12 | 0.14 |
| 50 | 8,400 | 15 | 0.18 |
| 60 | 8,400 | 14 | 0.17 |
| 70 | 8,400 | 11 | 0.13 |
| 80 | 8,400 | 14 | 0.17 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 38 | 0.23 |
| 151-200 | 8,400 | 27 | 0.32 |
| 61-100 | 25,200 | 42 | 0.17 |
| <=60 | 33,600 | 53 | 0.16 |
| >200 | 16,800 | 49 | 0.29 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 84 | 0.29 |
| medium | 2,400 | 2 | 0.08 |
| very_low | 69,600 | 123 | 0.18 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 22 | 0.13 |
| 100 | 16,800 | 47 | 0.28 |
| 20 | 16,800 | 31 | 0.18 |
| 200 | 16,800 | 59 | 0.35 |
| 5 | 16,800 | 23 | 0.14 |
| 50 | 16,800 | 27 | 0.16 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 73 | 0.29 |
| 20M | 25,200 | 39 | 0.15 |
| 50M | 25,200 | 46 | 0.18 |
| 5M | 25,200 | 51 | 0.20 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 18 | 0.25 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 23 | 0.32 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 11 | 0.15 |
| HelsinkiDowntown|BusMovement | 7,200 | 20 | 0.28 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 9 | 0.12 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 3 | 0.04 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 24 | 0.33 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 14 | 0.19 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 14 | 0.19 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 27 | 0.38 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 12 | 0.17 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 8 | 0.11 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 14 | 0.19 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 12 | 0.17 |

