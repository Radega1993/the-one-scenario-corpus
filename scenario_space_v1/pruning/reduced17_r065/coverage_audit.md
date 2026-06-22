# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **61**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 16 | 0.07 |
| HelsinkiDowntown | 21,600 | 13 | 0.06 |
| KallioCommunityCompact | 14,400 | 13 | 0.09 |
| KumpulaCampus | 7,200 | 3 | 0.04 |
| ManhattanMidtownGrid | 21,600 | 7 | 0.03 |
| NuuksioSparseTrails | 14,400 | 9 | 0.06 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 14 | 0.10 |
| ClusterMovement | 7,200 | 10 | 0.14 |
| MapRouteMovement | 28,800 | 21 | 0.07 |
| ShortestPathMapBasedMovement | 43,200 | 14 | 0.03 |
| WorkingDayMovement | 7,200 | 2 | 0.03 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 8 | 0.04 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 18 | 0.09 |
| pedestrian_transit | 20,160 | 18 | 0.09 |
| pedestrian_vehicle | 20,160 | 2 | 0.01 |
| single_homogeneous | 20,160 | 15 | 0.07 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 3 | 0.04 |
| 120 | 8,400 | 6 | 0.07 |
| 150 | 8,400 | 5 | 0.06 |
| 200 | 8,400 | 10 | 0.12 |
| 250 | 8,400 | 3 | 0.04 |
| 30 | 8,400 | 5 | 0.06 |
| 300 | 8,400 | 7 | 0.08 |
| 40 | 8,400 | 5 | 0.06 |
| 50 | 8,400 | 2 | 0.02 |
| 60 | 8,400 | 4 | 0.05 |
| 70 | 8,400 | 8 | 0.10 |
| 80 | 8,400 | 3 | 0.04 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 11 | 0.07 |
| 151-200 | 8,400 | 10 | 0.12 |
| 61-100 | 25,200 | 14 | 0.06 |
| <=60 | 33,600 | 16 | 0.05 |
| >200 | 16,800 | 10 | 0.06 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 25 | 0.09 |
| medium | 2,400 | 2 | 0.08 |
| very_low | 69,600 | 34 | 0.05 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 5 | 0.03 |
| 100 | 16,800 | 14 | 0.08 |
| 20 | 16,800 | 5 | 0.03 |
| 200 | 16,800 | 15 | 0.09 |
| 5 | 16,800 | 11 | 0.07 |
| 50 | 16,800 | 11 | 0.07 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 0 | 0.00 |
| 20M | 25,200 | 0 | 0.00 |
| 50M | 25,200 | 0 | 0.00 |
| 5M | 25,200 | 61 | 0.24 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 10 | 0.14 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 6 | 0.08 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 0 | 0.00 |
| HelsinkiDowntown|BusMovement | 7,200 | 10 | 0.14 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 1 | 0.01 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 2 | 0.03 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 7 | 0.10 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 6 | 0.08 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 3 | 0.04 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 4 | 0.06 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 3 | 0.04 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 0 | 0.00 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 5 | 0.07 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 4 | 0.06 |

