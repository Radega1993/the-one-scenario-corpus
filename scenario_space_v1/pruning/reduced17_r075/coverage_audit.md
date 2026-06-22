# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **110**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 27 | 0.12 |
| HelsinkiDowntown | 21,600 | 15 | 0.07 |
| KallioCommunityCompact | 14,400 | 21 | 0.15 |
| KumpulaCampus | 7,200 | 12 | 0.17 |
| ManhattanMidtownGrid | 21,600 | 18 | 0.08 |
| NuuksioSparseTrails | 14,400 | 17 | 0.12 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 21 | 0.15 |
| ClusterMovement | 7,200 | 19 | 0.26 |
| MapRouteMovement | 28,800 | 37 | 0.13 |
| ShortestPathMapBasedMovement | 43,200 | 30 | 0.07 |
| WorkingDayMovement | 7,200 | 3 | 0.04 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 20 | 0.10 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 24 | 0.12 |
| pedestrian_transit | 20,160 | 32 | 0.16 |
| pedestrian_vehicle | 20,160 | 8 | 0.04 |
| single_homogeneous | 20,160 | 26 | 0.13 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 9 | 0.11 |
| 120 | 8,400 | 10 | 0.12 |
| 150 | 8,400 | 8 | 0.10 |
| 200 | 8,400 | 15 | 0.18 |
| 250 | 8,400 | 12 | 0.14 |
| 30 | 8,400 | 8 | 0.10 |
| 300 | 8,400 | 13 | 0.15 |
| 40 | 8,400 | 8 | 0.10 |
| 50 | 8,400 | 8 | 0.10 |
| 60 | 8,400 | 6 | 0.07 |
| 70 | 8,400 | 9 | 0.11 |
| 80 | 8,400 | 4 | 0.05 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 18 | 0.11 |
| 151-200 | 8,400 | 15 | 0.18 |
| 61-100 | 25,200 | 22 | 0.09 |
| <=60 | 33,600 | 30 | 0.09 |
| >200 | 16,800 | 25 | 0.15 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 43 | 0.15 |
| medium | 2,400 | 4 | 0.17 |
| very_low | 69,600 | 63 | 0.09 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 7 | 0.04 |
| 100 | 16,800 | 31 | 0.18 |
| 20 | 16,800 | 9 | 0.05 |
| 200 | 16,800 | 28 | 0.17 |
| 5 | 16,800 | 17 | 0.10 |
| 50 | 16,800 | 18 | 0.11 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 0 | 0.00 |
| 20M | 25,200 | 0 | 0.00 |
| 50M | 25,200 | 0 | 0.00 |
| 5M | 25,200 | 110 | 0.44 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 19 | 0.26 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 8 | 0.11 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 0 | 0.00 |
| HelsinkiDowntown|BusMovement | 7,200 | 11 | 0.15 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 1 | 0.01 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 3 | 0.04 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 13 | 0.18 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 8 | 0.11 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 12 | 0.17 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 10 | 0.14 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 8 | 0.11 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 0 | 0.00 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 8 | 0.11 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 9 | 0.12 |

