# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **69**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 16 | 0.07 |
| HelsinkiDowntown | 21,600 | 12 | 0.06 |
| KallioCommunityCompact | 14,400 | 12 | 0.08 |
| KumpulaCampus | 7,200 | 4 | 0.06 |
| ManhattanMidtownGrid | 21,600 | 13 | 0.06 |
| NuuksioSparseTrails | 14,400 | 12 | 0.08 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 15 | 0.10 |
| ClusterMovement | 7,200 | 7 | 0.10 |
| MapRouteMovement | 28,800 | 23 | 0.08 |
| ShortestPathMapBasedMovement | 43,200 | 22 | 0.05 |
| WorkingDayMovement | 7,200 | 2 | 0.03 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 10 | 0.05 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 22 | 0.11 |
| pedestrian_transit | 20,160 | 18 | 0.09 |
| pedestrian_vehicle | 20,160 | 4 | 0.02 |
| single_homogeneous | 20,160 | 15 | 0.07 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 6 | 0.07 |
| 120 | 8,400 | 8 | 0.10 |
| 150 | 8,400 | 6 | 0.07 |
| 200 | 8,400 | 6 | 0.07 |
| 250 | 8,400 | 4 | 0.05 |
| 30 | 8,400 | 5 | 0.06 |
| 300 | 8,400 | 14 | 0.17 |
| 40 | 8,400 | 5 | 0.06 |
| 50 | 8,400 | 4 | 0.05 |
| 60 | 8,400 | 4 | 0.05 |
| 70 | 8,400 | 3 | 0.04 |
| 80 | 8,400 | 4 | 0.05 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 14 | 0.08 |
| 151-200 | 8,400 | 6 | 0.07 |
| 61-100 | 25,200 | 13 | 0.05 |
| <=60 | 33,600 | 18 | 0.05 |
| >200 | 16,800 | 18 | 0.11 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 21 | 0.07 |
| medium | 2,400 | 3 | 0.12 |
| very_low | 69,600 | 45 | 0.06 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 14 | 0.08 |
| 100 | 16,800 | 9 | 0.05 |
| 20 | 16,800 | 8 | 0.05 |
| 200 | 16,800 | 18 | 0.11 |
| 5 | 16,800 | 10 | 0.06 |
| 50 | 16,800 | 10 | 0.06 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 21 | 0.08 |
| 20M | 25,200 | 14 | 0.06 |
| 50M | 25,200 | 18 | 0.07 |
| 5M | 25,200 | 16 | 0.06 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 7 | 0.10 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 6 | 0.08 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 3 | 0.04 |
| HelsinkiDowntown|BusMovement | 7,200 | 7 | 0.10 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 3 | 0.04 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 2 | 0.03 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 8 | 0.11 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 4 | 0.06 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 4 | 0.06 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 8 | 0.11 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 3 | 0.04 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 2 | 0.03 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 6 | 0.08 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 6 | 0.08 |

