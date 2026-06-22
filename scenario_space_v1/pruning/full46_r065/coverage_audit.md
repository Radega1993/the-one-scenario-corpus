# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **108**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 30 | 0.14 |
| HelsinkiDowntown | 21,600 | 18 | 0.08 |
| KallioCommunityCompact | 14,400 | 20 | 0.14 |
| KumpulaCampus | 7,200 | 7 | 0.10 |
| ManhattanMidtownGrid | 21,600 | 20 | 0.09 |
| NuuksioSparseTrails | 14,400 | 13 | 0.09 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 23 | 0.16 |
| ClusterMovement | 7,200 | 12 | 0.17 |
| MapRouteMovement | 28,800 | 36 | 0.12 |
| ShortestPathMapBasedMovement | 43,200 | 35 | 0.08 |
| WorkingDayMovement | 7,200 | 2 | 0.03 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 20 | 0.10 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 36 | 0.18 |
| pedestrian_transit | 20,160 | 27 | 0.13 |
| pedestrian_vehicle | 20,160 | 9 | 0.04 |
| single_homogeneous | 20,160 | 16 | 0.08 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 11 | 0.13 |
| 120 | 8,400 | 6 | 0.07 |
| 150 | 8,400 | 8 | 0.10 |
| 200 | 8,400 | 12 | 0.14 |
| 250 | 8,400 | 10 | 0.12 |
| 30 | 8,400 | 7 | 0.08 |
| 300 | 8,400 | 17 | 0.20 |
| 40 | 8,400 | 5 | 0.06 |
| 50 | 8,400 | 8 | 0.10 |
| 60 | 8,400 | 7 | 0.08 |
| 70 | 8,400 | 11 | 0.13 |
| 80 | 8,400 | 6 | 0.07 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 14 | 0.08 |
| 151-200 | 8,400 | 12 | 0.14 |
| 61-100 | 25,200 | 28 | 0.11 |
| <=60 | 33,600 | 27 | 0.08 |
| >200 | 16,800 | 27 | 0.16 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 40 | 0.14 |
| medium | 2,400 | 1 | 0.04 |
| very_low | 69,600 | 67 | 0.10 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 13 | 0.08 |
| 100 | 16,800 | 17 | 0.10 |
| 20 | 16,800 | 14 | 0.08 |
| 200 | 16,800 | 32 | 0.19 |
| 5 | 16,800 | 13 | 0.08 |
| 50 | 16,800 | 19 | 0.11 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 37 | 0.15 |
| 20M | 25,200 | 19 | 0.08 |
| 50M | 25,200 | 23 | 0.09 |
| 5M | 25,200 | 29 | 0.12 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 12 | 0.17 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 12 | 0.17 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 6 | 0.08 |
| HelsinkiDowntown|BusMovement | 7,200 | 13 | 0.18 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 3 | 0.04 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 2 | 0.03 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 12 | 0.17 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 8 | 0.11 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 7 | 0.10 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 10 | 0.14 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 6 | 0.08 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 4 | 0.06 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 6 | 0.08 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 7 | 0.10 |

