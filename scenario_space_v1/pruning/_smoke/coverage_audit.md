# Coverage audit — correlation-pruned subset vs full manifest

- Full manifest scenarios: **500**
- Selected scenarios: **10**

Counts by design-space dimension (full vs selected).

## map_id

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted | 500 | 10 | 2.00 |

## movement_model_primary

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| ClusterMovement | 500 | 10 | 2.00 |

## group_structure

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| cluster_nomadic | 96 | 3 | 3.12 |
| pedestrian_shortestpath_heterogeneous | 96 | 2 | 2.08 |
| pedestrian_transit | 96 | 3 | 3.12 |
| pedestrian_vehicle | 96 | 0 | 0.00 |
| single_homogeneous | 116 | 2 | 1.72 |

## n_hosts

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 30 | 500 | 10 | 2.00 |

## n_hosts_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 101-150 | 0 | 0 | 0.00 |
| 151-200 | 0 | 0 | 0.00 |
| 61-100 | 0 | 0 | 0.00 |
| <=60 | 500 | 10 | 2.00 |
| >200 | 0 | 0 | 0.00 |

## density_bin

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| high | 0 | 0 | 0.00 |
| low | 0 | 0 | 0.00 |
| medium | 0 | 0 | 0.00 |
| very_low | 500 | 10 | 2.00 |

## transmit_range_m

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 10 | 84 | 0 | 0.00 |
| 100 | 84 | 1 | 1.19 |
| 20 | 84 | 2 | 2.38 |
| 200 | 80 | 4 | 5.00 |
| 5 | 84 | 3 | 3.57 |
| 50 | 84 | 0 | 0.00 |

## buffer_size

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| 100M | 125 | 3 | 2.40 |
| 20M | 125 | 4 | 3.20 |
| 50M | 125 | 2 | 1.60 |
| 5M | 125 | 1 | 0.80 |

## scenario_class

| value | full | selected | retention % |
|-------|-----:|---------:|------------:|
| HelsinkiDisrupted|ClusterMovement | 500 | 10 | 2.00 |

