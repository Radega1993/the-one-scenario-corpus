# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **83**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 20 | 0.09 |
| HelsinkiDowntown | 21,600 | 13 | 0.06 |
| KallioCommunityCompact | 14,400 | 18 | 0.12 |
| KumpulaCampus | 7,200 | 7 | 0.10 |
| ManhattanMidtownGrid | 21,600 | 14 | 0.06 |
| NuuksioSparseTrails | 14,400 | 11 | 0.08 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 17 | 0.12 |
| ClusterMovement | 7,200 | 14 | 0.19 |
| MapRouteMovement | 28,800 | 26 | 0.09 |
| ShortestPathMapBasedMovement | 43,200 | 23 | 0.05 |
| WorkingDayMovement | 7,200 | 3 | 0.04 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 16 | 0.08 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 19 | 0.09 |
| pedestrian_transit | 20,160 | 25 | 0.12 |
| pedestrian_vehicle | 20,160 | 3 | 0.01 |
| single_homogeneous | 20,160 | 20 | 0.10 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 10 | 0.12 |
| 120 | 8,400 | 5 | 0.06 |
| 150 | 8,400 | 7 | 0.08 |
| 200 | 8,400 | 11 | 0.13 |
| 250 | 8,400 | 6 | 0.07 |
| 30 | 8,400 | 5 | 0.06 |
| 300 | 8,400 | 11 | 0.13 |
| 40 | 8,400 | 6 | 0.07 |
| 50 | 8,400 | 6 | 0.07 |
| 60 | 8,400 | 4 | 0.05 |
| 70 | 8,400 | 6 | 0.07 |
| 80 | 8,400 | 6 | 0.07 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 12 | 0.07 |
| 151-200 | 8,400 | 11 | 0.13 |
| 61-100 | 25,200 | 22 | 0.09 |
| <=60 | 33,600 | 21 | 0.06 |
| >200 | 16,800 | 17 | 0.10 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 34 | 0.12 |
| medium | 2,400 | 3 | 0.12 |
| very_low | 69,600 | 46 | 0.07 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 6 | 0.04 |
| 100 | 16,800 | 19 | 0.11 |
| 20 | 16,800 | 8 | 0.05 |
| 200 | 16,800 | 21 | 0.12 |
| 5 | 16,800 | 14 | 0.08 |
| 50 | 16,800 | 15 | 0.09 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 0 | 0.00 |
| 20M | 25,200 | 0 | 0.00 |
| 50M | 25,200 | 0 | 0.00 |
| 5M | 25,200 | 83 | 0.33 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 14 | 0.19 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 6 | 0.08 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 0 | 0.00 |
| HelsinkiDowntown|BusMovement | 7,200 | 9 | 0.12 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 1 | 0.01 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 3 | 0.04 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 10 | 0.14 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 8 | 0.11 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 7 | 0.10 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 8 | 0.11 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 6 | 0.08 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 0 | 0.00 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 4 | 0.06 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 7 | 0.10 |

