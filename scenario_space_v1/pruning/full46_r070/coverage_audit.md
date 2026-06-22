# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **148**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 39 | 0.18 |
| HelsinkiDowntown | 21,600 | 25 | 0.12 |
| KallioCommunityCompact | 14,400 | 25 | 0.17 |
| KumpulaCampus | 7,200 | 11 | 0.15 |
| ManhattanMidtownGrid | 21,600 | 30 | 0.14 |
| NuuksioSparseTrails | 14,400 | 18 | 0.12 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 33 | 0.23 |
| ClusterMovement | 7,200 | 16 | 0.22 |
| MapRouteMovement | 28,800 | 49 | 0.17 |
| ShortestPathMapBasedMovement | 43,200 | 47 | 0.11 |
| WorkingDayMovement | 7,200 | 3 | 0.04 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 23 | 0.11 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 54 | 0.27 |
| pedestrian_transit | 20,160 | 37 | 0.18 |
| pedestrian_vehicle | 20,160 | 11 | 0.05 |
| single_homogeneous | 20,160 | 23 | 0.11 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 8 | 0.10 |
| 120 | 8,400 | 13 | 0.15 |
| 150 | 8,400 | 12 | 0.14 |
| 200 | 8,400 | 19 | 0.23 |
| 250 | 8,400 | 19 | 0.23 |
| 30 | 8,400 | 11 | 0.13 |
| 300 | 8,400 | 18 | 0.21 |
| 40 | 8,400 | 8 | 0.10 |
| 50 | 8,400 | 12 | 0.14 |
| 60 | 8,400 | 12 | 0.14 |
| 70 | 8,400 | 7 | 0.08 |
| 80 | 8,400 | 9 | 0.11 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 25 | 0.15 |
| 151-200 | 8,400 | 19 | 0.23 |
| 61-100 | 25,200 | 24 | 0.10 |
| <=60 | 33,600 | 43 | 0.13 |
| >200 | 16,800 | 37 | 0.22 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 57 | 0.20 |
| medium | 2,400 | 2 | 0.08 |
| very_low | 69,600 | 89 | 0.13 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 13 | 0.08 |
| 100 | 16,800 | 34 | 0.20 |
| 20 | 16,800 | 26 | 0.15 |
| 200 | 16,800 | 41 | 0.24 |
| 5 | 16,800 | 16 | 0.10 |
| 50 | 16,800 | 18 | 0.11 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 50 | 0.20 |
| 20M | 25,200 | 28 | 0.11 |
| 50M | 25,200 | 35 | 0.14 |
| 5M | 25,200 | 35 | 0.14 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 16 | 0.22 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 15 | 0.21 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 8 | 0.11 |
| HelsinkiDowntown|BusMovement | 7,200 | 17 | 0.24 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 5 | 0.07 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 3 | 0.04 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 16 | 0.22 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 9 | 0.12 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 11 | 0.15 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 16 | 0.22 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 10 | 0.14 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 4 | 0.06 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 8 | 0.11 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 10 | 0.14 |

