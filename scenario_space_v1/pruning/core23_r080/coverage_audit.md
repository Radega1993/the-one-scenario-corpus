# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **194**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 47 | 0.22 |
| HelsinkiDowntown | 21,600 | 32 | 0.15 |
| KallioCommunityCompact | 14,400 | 35 | 0.24 |
| KumpulaCampus | 7,200 | 10 | 0.14 |
| ManhattanMidtownGrid | 21,600 | 40 | 0.19 |
| NuuksioSparseTrails | 14,400 | 30 | 0.21 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 41 | 0.28 |
| ClusterMovement | 7,200 | 16 | 0.22 |
| MapRouteMovement | 28,800 | 62 | 0.22 |
| ShortestPathMapBasedMovement | 43,200 | 71 | 0.16 |
| WorkingDayMovement | 7,200 | 4 | 0.06 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 37 | 0.18 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 59 | 0.29 |
| pedestrian_transit | 20,160 | 44 | 0.22 |
| pedestrian_vehicle | 20,160 | 17 | 0.08 |
| single_homogeneous | 20,160 | 37 | 0.18 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 18 | 0.21 |
| 120 | 8,400 | 15 | 0.18 |
| 150 | 8,400 | 19 | 0.23 |
| 200 | 8,400 | 19 | 0.23 |
| 250 | 8,400 | 25 | 0.30 |
| 30 | 8,400 | 17 | 0.20 |
| 300 | 8,400 | 31 | 0.37 |
| 40 | 8,400 | 15 | 0.18 |
| 50 | 8,400 | 10 | 0.12 |
| 60 | 8,400 | 9 | 0.11 |
| 70 | 8,400 | 11 | 0.13 |
| 80 | 8,400 | 5 | 0.06 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 34 | 0.20 |
| 151-200 | 8,400 | 19 | 0.23 |
| 61-100 | 25,200 | 34 | 0.13 |
| <=60 | 33,600 | 51 | 0.15 |
| >200 | 16,800 | 56 | 0.33 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 64 | 0.22 |
| medium | 2,400 | 9 | 0.38 |
| very_low | 69,600 | 121 | 0.17 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 25 | 0.15 |
| 100 | 16,800 | 37 | 0.22 |
| 20 | 16,800 | 21 | 0.12 |
| 200 | 16,800 | 66 | 0.39 |
| 5 | 16,800 | 25 | 0.15 |
| 50 | 16,800 | 20 | 0.12 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 67 | 0.27 |
| 20M | 25,200 | 31 | 0.12 |
| 50M | 25,200 | 44 | 0.17 |
| 5M | 25,200 | 52 | 0.21 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 16 | 0.22 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 19 | 0.26 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 12 | 0.17 |
| HelsinkiDowntown|BusMovement | 7,200 | 16 | 0.22 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 12 | 0.17 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 4 | 0.06 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 19 | 0.26 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 16 | 0.22 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 10 | 0.14 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 25 | 0.35 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 8 | 0.11 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 7 | 0.10 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 16 | 0.22 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 14 | 0.19 |

