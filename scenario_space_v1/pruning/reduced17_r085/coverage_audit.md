# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **257**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 65 | 0.30 |
| HelsinkiDowntown | 21,600 | 39 | 0.18 |
| KallioCommunityCompact | 14,400 | 49 | 0.34 |
| KumpulaCampus | 7,200 | 24 | 0.33 |
| ManhattanMidtownGrid | 21,600 | 42 | 0.19 |
| NuuksioSparseTrails | 14,400 | 38 | 0.26 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 55 | 0.38 |
| ClusterMovement | 7,200 | 37 | 0.51 |
| MapRouteMovement | 28,800 | 85 | 0.30 |
| ShortestPathMapBasedMovement | 43,200 | 75 | 0.17 |
| WorkingDayMovement | 7,200 | 5 | 0.07 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 55 | 0.27 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 50 | 0.25 |
| pedestrian_transit | 20,160 | 79 | 0.39 |
| pedestrian_vehicle | 20,160 | 12 | 0.06 |
| single_homogeneous | 20,160 | 61 | 0.30 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 20 | 0.24 |
| 120 | 8,400 | 22 | 0.26 |
| 150 | 8,400 | 30 | 0.36 |
| 200 | 8,400 | 37 | 0.44 |
| 250 | 8,400 | 28 | 0.33 |
| 30 | 8,400 | 22 | 0.26 |
| 300 | 8,400 | 29 | 0.35 |
| 40 | 8,400 | 14 | 0.17 |
| 50 | 8,400 | 13 | 0.15 |
| 60 | 8,400 | 10 | 0.12 |
| 70 | 8,400 | 14 | 0.17 |
| 80 | 8,400 | 18 | 0.21 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 52 | 0.31 |
| 151-200 | 8,400 | 37 | 0.44 |
| 61-100 | 25,200 | 52 | 0.21 |
| <=60 | 33,600 | 59 | 0.18 |
| >200 | 16,800 | 57 | 0.34 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 106 | 0.37 |
| medium | 2,400 | 4 | 0.17 |
| very_low | 69,600 | 147 | 0.21 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 25 | 0.15 |
| 100 | 16,800 | 70 | 0.42 |
| 20 | 16,800 | 24 | 0.14 |
| 200 | 16,800 | 67 | 0.40 |
| 5 | 16,800 | 31 | 0.18 |
| 50 | 16,800 | 40 | 0.24 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 0 | 0.00 |
| 20M | 25,200 | 0 | 0.00 |
| 50M | 25,200 | 0 | 0.00 |
| 5M | 25,200 | 257 | 1.02 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 37 | 0.51 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 28 | 0.39 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 0 | 0.00 |
| HelsinkiDowntown|BusMovement | 7,200 | 30 | 0.42 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 4 | 0.06 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 5 | 0.07 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 24 | 0.33 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 25 | 0.35 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 24 | 0.33 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 25 | 0.35 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 14 | 0.19 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 3 | 0.04 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 19 | 0.26 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 19 | 0.26 |

