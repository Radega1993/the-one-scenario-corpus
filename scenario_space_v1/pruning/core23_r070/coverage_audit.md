# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **97**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 25 | 0.12 |
| HelsinkiDowntown | 21,600 | 17 | 0.08 |
| KallioCommunityCompact | 14,400 | 17 | 0.12 |
| KumpulaCampus | 7,200 | 5 | 0.07 |
| ManhattanMidtownGrid | 21,600 | 17 | 0.08 |
| NuuksioSparseTrails | 14,400 | 16 | 0.11 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 19 | 0.13 |
| ClusterMovement | 7,200 | 9 | 0.12 |
| MapRouteMovement | 28,800 | 30 | 0.10 |
| ShortestPathMapBasedMovement | 43,200 | 37 | 0.09 |
| WorkingDayMovement | 7,200 | 2 | 0.03 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 16 | 0.08 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 32 | 0.16 |
| pedestrian_transit | 20,160 | 22 | 0.11 |
| pedestrian_vehicle | 20,160 | 6 | 0.03 |
| single_homogeneous | 20,160 | 21 | 0.10 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 8 | 0.10 |
| 120 | 8,400 | 8 | 0.10 |
| 150 | 8,400 | 8 | 0.10 |
| 200 | 8,400 | 8 | 0.10 |
| 250 | 8,400 | 14 | 0.17 |
| 30 | 8,400 | 8 | 0.10 |
| 300 | 8,400 | 14 | 0.17 |
| 40 | 8,400 | 6 | 0.07 |
| 50 | 8,400 | 8 | 0.10 |
| 60 | 8,400 | 4 | 0.05 |
| 70 | 8,400 | 3 | 0.04 |
| 80 | 8,400 | 8 | 0.10 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 16 | 0.10 |
| 151-200 | 8,400 | 8 | 0.10 |
| 61-100 | 25,200 | 19 | 0.08 |
| <=60 | 33,600 | 26 | 0.08 |
| >200 | 16,800 | 28 | 0.17 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 32 | 0.11 |
| medium | 2,400 | 5 | 0.21 |
| very_low | 69,600 | 60 | 0.09 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 12 | 0.07 |
| 100 | 16,800 | 17 | 0.10 |
| 20 | 16,800 | 13 | 0.08 |
| 200 | 16,800 | 27 | 0.16 |
| 5 | 16,800 | 11 | 0.07 |
| 50 | 16,800 | 17 | 0.10 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 34 | 0.13 |
| 20M | 25,200 | 19 | 0.08 |
| 50M | 25,200 | 23 | 0.09 |
| 5M | 25,200 | 21 | 0.08 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 9 | 0.12 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 12 | 0.17 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 4 | 0.06 |
| HelsinkiDowntown|BusMovement | 7,200 | 9 | 0.12 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 6 | 0.08 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 2 | 0.03 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 8 | 0.11 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 9 | 0.12 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 5 | 0.07 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 10 | 0.14 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 4 | 0.06 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 3 | 0.04 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 6 | 0.08 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 10 | 0.14 |

