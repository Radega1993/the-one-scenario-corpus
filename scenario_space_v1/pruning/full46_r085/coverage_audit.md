# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **546**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 129 | 0.60 |
| HelsinkiDowntown | 21,600 | 88 | 0.41 |
| KallioCommunityCompact | 14,400 | 93 | 0.65 |
| KumpulaCampus | 7,200 | 41 | 0.57 |
| ManhattanMidtownGrid | 21,600 | 119 | 0.55 |
| NuuksioSparseTrails | 14,400 | 76 | 0.53 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 111 | 0.77 |
| ClusterMovement | 7,200 | 44 | 0.61 |
| MapRouteMovement | 28,800 | 186 | 0.65 |
| ShortestPathMapBasedMovement | 43,200 | 199 | 0.46 |
| WorkingDayMovement | 7,200 | 6 | 0.08 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 101 | 0.50 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 187 | 0.93 |
| pedestrian_transit | 20,160 | 138 | 0.68 |
| pedestrian_vehicle | 20,160 | 46 | 0.23 |
| single_homogeneous | 20,160 | 74 | 0.37 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 27 | 0.32 |
| 120 | 8,400 | 42 | 0.50 |
| 150 | 8,400 | 70 | 0.83 |
| 200 | 8,400 | 67 | 0.80 |
| 250 | 8,400 | 64 | 0.76 |
| 30 | 8,400 | 44 | 0.52 |
| 300 | 8,400 | 72 | 0.86 |
| 40 | 8,400 | 37 | 0.44 |
| 50 | 8,400 | 25 | 0.30 |
| 60 | 8,400 | 35 | 0.42 |
| 70 | 8,400 | 33 | 0.39 |
| 80 | 8,400 | 30 | 0.36 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 112 | 0.67 |
| 151-200 | 8,400 | 67 | 0.80 |
| 61-100 | 25,200 | 90 | 0.36 |
| <=60 | 33,600 | 141 | 0.42 |
| >200 | 16,800 | 136 | 0.81 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 211 | 0.73 |
| medium | 2,400 | 15 | 0.62 |
| very_low | 69,600 | 320 | 0.46 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 50 | 0.30 |
| 100 | 16,800 | 135 | 0.80 |
| 20 | 16,800 | 65 | 0.39 |
| 200 | 16,800 | 161 | 0.96 |
| 5 | 16,800 | 58 | 0.35 |
| 50 | 16,800 | 77 | 0.46 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 191 | 0.76 |
| 20M | 25,200 | 102 | 0.40 |
| 50M | 25,200 | 131 | 0.52 |
| 5M | 25,200 | 122 | 0.48 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 44 | 0.61 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 51 | 0.71 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 34 | 0.47 |
| HelsinkiDowntown|BusMovement | 7,200 | 54 | 0.75 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 28 | 0.39 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 6 | 0.08 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 55 | 0.76 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 38 | 0.53 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 41 | 0.57 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 57 | 0.79 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 37 | 0.51 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 25 | 0.35 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 43 | 0.60 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 33 | 0.46 |

