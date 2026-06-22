# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **339**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 85 | 0.39 |
| HelsinkiDowntown | 21,600 | 50 | 0.23 |
| KallioCommunityCompact | 14,400 | 64 | 0.44 |
| KumpulaCampus | 7,200 | 26 | 0.36 |
| ManhattanMidtownGrid | 21,600 | 65 | 0.30 |
| NuuksioSparseTrails | 14,400 | 49 | 0.34 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 67 | 0.47 |
| ClusterMovement | 7,200 | 30 | 0.42 |
| MapRouteMovement | 28,800 | 117 | 0.41 |
| ShortestPathMapBasedMovement | 43,200 | 121 | 0.28 |
| WorkingDayMovement | 7,200 | 4 | 0.06 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 59 | 0.29 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 117 | 0.58 |
| pedestrian_transit | 20,160 | 88 | 0.44 |
| pedestrian_vehicle | 20,160 | 27 | 0.13 |
| single_homogeneous | 20,160 | 48 | 0.24 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 24 | 0.29 |
| 120 | 8,400 | 16 | 0.19 |
| 150 | 8,400 | 44 | 0.52 |
| 200 | 8,400 | 36 | 0.43 |
| 250 | 8,400 | 42 | 0.50 |
| 30 | 8,400 | 30 | 0.36 |
| 300 | 8,400 | 47 | 0.56 |
| 40 | 8,400 | 23 | 0.27 |
| 50 | 8,400 | 25 | 0.30 |
| 60 | 8,400 | 14 | 0.17 |
| 70 | 8,400 | 16 | 0.19 |
| 80 | 8,400 | 22 | 0.26 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 60 | 0.36 |
| 151-200 | 8,400 | 36 | 0.43 |
| 61-100 | 25,200 | 62 | 0.25 |
| <=60 | 33,600 | 92 | 0.27 |
| >200 | 16,800 | 89 | 0.53 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 135 | 0.47 |
| medium | 2,400 | 6 | 0.25 |
| very_low | 69,600 | 198 | 0.28 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 30 | 0.18 |
| 100 | 16,800 | 80 | 0.48 |
| 20 | 16,800 | 45 | 0.27 |
| 200 | 16,800 | 100 | 0.60 |
| 5 | 16,800 | 39 | 0.23 |
| 50 | 16,800 | 45 | 0.27 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 123 | 0.49 |
| 20M | 25,200 | 62 | 0.25 |
| 50M | 25,200 | 71 | 0.28 |
| 5M | 25,200 | 83 | 0.33 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 30 | 0.42 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 36 | 0.50 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 19 | 0.26 |
| HelsinkiDowntown|BusMovement | 7,200 | 30 | 0.42 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 16 | 0.22 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 4 | 0.06 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 36 | 0.50 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 28 | 0.39 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 26 | 0.36 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 37 | 0.51 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 16 | 0.22 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 12 | 0.17 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 29 | 0.40 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 20 | 0.28 |

