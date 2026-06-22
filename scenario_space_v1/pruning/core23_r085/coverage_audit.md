# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **295**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 67 | 0.31 |
| HelsinkiDowntown | 21,600 | 48 | 0.22 |
| KallioCommunityCompact | 14,400 | 54 | 0.38 |
| KumpulaCampus | 7,200 | 20 | 0.28 |
| ManhattanMidtownGrid | 21,600 | 62 | 0.29 |
| NuuksioSparseTrails | 14,400 | 44 | 0.31 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 60 | 0.42 |
| ClusterMovement | 7,200 | 22 | 0.31 |
| MapRouteMovement | 28,800 | 98 | 0.34 |
| ShortestPathMapBasedMovement | 43,200 | 110 | 0.25 |
| WorkingDayMovement | 7,200 | 5 | 0.07 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 54 | 0.27 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 93 | 0.46 |
| pedestrian_transit | 20,160 | 74 | 0.37 |
| pedestrian_vehicle | 20,160 | 21 | 0.10 |
| single_homogeneous | 20,160 | 53 | 0.26 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 17 | 0.20 |
| 120 | 8,400 | 23 | 0.27 |
| 150 | 8,400 | 27 | 0.32 |
| 200 | 8,400 | 36 | 0.43 |
| 250 | 8,400 | 32 | 0.38 |
| 30 | 8,400 | 21 | 0.25 |
| 300 | 8,400 | 54 | 0.64 |
| 40 | 8,400 | 27 | 0.32 |
| 50 | 8,400 | 14 | 0.17 |
| 60 | 8,400 | 17 | 0.20 |
| 70 | 8,400 | 19 | 0.23 |
| 80 | 8,400 | 8 | 0.10 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 50 | 0.30 |
| 151-200 | 8,400 | 36 | 0.43 |
| 61-100 | 25,200 | 44 | 0.17 |
| <=60 | 33,600 | 79 | 0.24 |
| >200 | 16,800 | 86 | 0.51 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 105 | 0.36 |
| medium | 2,400 | 17 | 0.71 |
| very_low | 69,600 | 173 | 0.25 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 33 | 0.20 |
| 100 | 16,800 | 57 | 0.34 |
| 20 | 16,800 | 35 | 0.21 |
| 200 | 16,800 | 99 | 0.59 |
| 5 | 16,800 | 38 | 0.23 |
| 50 | 16,800 | 33 | 0.20 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 102 | 0.40 |
| 20M | 25,200 | 56 | 0.22 |
| 50M | 25,200 | 72 | 0.29 |
| 5M | 25,200 | 65 | 0.26 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 22 | 0.31 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 26 | 0.36 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 19 | 0.26 |
| HelsinkiDowntown|BusMovement | 7,200 | 27 | 0.38 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 16 | 0.22 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 5 | 0.07 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 27 | 0.38 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 27 | 0.38 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 20 | 0.28 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 33 | 0.46 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 19 | 0.26 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 10 | 0.14 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 26 | 0.36 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 18 | 0.25 |

