# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **100,800**
- Selected scenarios: **165**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 21,600 | 43 | 0.20 |
| HelsinkiDowntown | 21,600 | 24 | 0.11 |
| KallioCommunityCompact | 14,400 | 31 | 0.22 |
| KumpulaCampus | 7,200 | 16 | 0.22 |
| ManhattanMidtownGrid | 21,600 | 26 | 0.12 |
| NuuksioSparseTrails | 14,400 | 25 | 0.17 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| BusMovement | 14,400 | 37 | 0.26 |
| ClusterMovement | 7,200 | 25 | 0.35 |
| MapRouteMovement | 28,800 | 56 | 0.19 |
| ShortestPathMapBasedMovement | 43,200 | 43 | 0.10 |
| WorkingDayMovement | 7,200 | 4 | 0.06 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 20,160 | 32 | 0.16 |
| pedestrian_shortestpath_heterogeneous | 20,160 | 33 | 0.16 |
| pedestrian_transit | 20,160 | 49 | 0.24 |
| pedestrian_vehicle | 20,160 | 11 | 0.05 |
| single_homogeneous | 20,160 | 40 | 0.20 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100 | 8,400 | 15 | 0.18 |
| 120 | 8,400 | 12 | 0.14 |
| 150 | 8,400 | 20 | 0.24 |
| 200 | 8,400 | 20 | 0.24 |
| 250 | 8,400 | 18 | 0.21 |
| 30 | 8,400 | 12 | 0.14 |
| 300 | 8,400 | 19 | 0.23 |
| 40 | 8,400 | 10 | 0.12 |
| 50 | 8,400 | 10 | 0.12 |
| 60 | 8,400 | 7 | 0.08 |
| 70 | 8,400 | 12 | 0.14 |
| 80 | 8,400 | 10 | 0.12 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 16,800 | 32 | 0.19 |
| 151-200 | 8,400 | 20 | 0.24 |
| 61-100 | 25,200 | 37 | 0.15 |
| <=60 | 33,600 | 39 | 0.12 |
| >200 | 16,800 | 37 | 0.22 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 28,800 | 67 | 0.23 |
| medium | 2,400 | 3 | 0.12 |
| very_low | 69,600 | 95 | 0.14 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 16,800 | 14 | 0.08 |
| 100 | 16,800 | 42 | 0.25 |
| 20 | 16,800 | 14 | 0.08 |
| 200 | 16,800 | 44 | 0.26 |
| 5 | 16,800 | 25 | 0.15 |
| 50 | 16,800 | 26 | 0.15 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 25,200 | 0 | 0.00 |
| 20M | 25,200 | 0 | 0.00 |
| 50M | 25,200 | 0 | 0.00 |
| 5M | 25,200 | 165 | 0.65 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 7,200 | 25 | 0.35 |
| HelsinkiDisrupted|MapRouteMovement | 7,200 | 18 | 0.25 |
| HelsinkiDisrupted|ShortestPathMapBasedMovement | 7,200 | 0 | 0.00 |
| HelsinkiDowntown|BusMovement | 7,200 | 19 | 0.26 |
| HelsinkiDowntown|ShortestPathMapBasedMovement | 7,200 | 1 | 0.01 |
| HelsinkiDowntown|WorkingDayMovement | 7,200 | 4 | 0.06 |
| KallioCommunityCompact|MapRouteMovement | 7,200 | 18 | 0.25 |
| KallioCommunityCompact|ShortestPathMapBasedMovement | 7,200 | 13 | 0.18 |
| KumpulaCampus|ShortestPathMapBasedMovement | 7,200 | 16 | 0.22 |
| ManhattanMidtownGrid|BusMovement | 7,200 | 18 | 0.25 |
| ManhattanMidtownGrid|MapRouteMovement | 7,200 | 7 | 0.10 |
| ManhattanMidtownGrid|ShortestPathMapBasedMovement | 7,200 | 1 | 0.01 |
| NuuksioSparseTrails|MapRouteMovement | 7,200 | 13 | 0.18 |
| NuuksioSparseTrails|ShortestPathMapBasedMovement | 7,200 | 12 | 0.17 |

