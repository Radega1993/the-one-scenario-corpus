## Scenario D2 — D2_PartitionedCity_MuleBridge

### 1. Overview

- **Scenario ID:** D2  
- **Name:** D2_PartitionedCity_MuleBridge  
- **Family:** Disaster  
- **Settings file:** `corpus_v1/05_disaster/D2_PartitionedCity_MuleBridge.settings`

**Objective**

Two spatially partitioned city sectors connected mainly by one mobile mule node.

### 2. Scenario configuration (core features)

Values below come from `analysis/data/features.csv` (raw) and the mapping to the 23-core subset.

| Feature | Value | Comment |
|---------|-------|---------|
| world_area | 40000000 | Total simulation area (m^2) |
| aspect_ratio | 0.4 | min(width,height)/max(width,height) |
| N | 71 | Total nodes |
| nrofHostGroups | 3 | Number of host groups |
| speed_mean | 0.75 | Mean configured speed (m/s) |
| wait_mean | 135 | Mean pause/wait time (s) |
| mm_WDM | 0 | WorkingDayMovement enabled (1/0) |
| mm_RWP | 1 | RandomWaypoint enabled (1/0) |
| mm_MapRoute | 0 | MapRouteMovement enabled (1/0) |
| mm_Cluster | 1 | ClusterMovement enabled (1/0) |
| mm_Bus | 0 | BusMovement enabled (1/0) |
| mm_Linear | 0 | LinearMovement enabled (1/0) |
| transmitRange | 10 | Interface range (m) |
| bufferSize | 50000000 | Node buffer (bytes) |
| transmitSpeed | 2000000 | Interface speed (bytes/s) |
| msgTtl | 10000 | Message TTL |
| event_interval_mean | 120 | Mean Events1 interval |
| event_size_mean | 85000 | Mean Events1 size (bytes) |
| nrof_event_generators | 1 | Number of event generators |
| pattern_burst | 0 | Burst windows in traffic (1/0) |
| pattern_hub_target | 0 | Hub-target traffic pattern (1/0) |
| workDayLength | — | Not used in this scenario |
| ownCarProb | — | Not used in this scenario |
| clusterRange_mean | 450 | Mean cluster radius if ClusterMovement |

### 3. Mobility model

- **World size:** `10000, 4000`  
- **Base speed range:** `Not recorded`  
- **Base wait range:** `Not recorded`

Two large ClusterMovement partitions and one fast RandomWaypoint mule.

**DTN implication**

This mobility design creates a constrained-contact disaster regime where connectivity depends on temporal bridges, dense local clusters, or opportunistic relays rather than stable end-to-end paths.

### 4. Traffic pattern

- `Events.nrof = 1`  
- `Events1.interval = 60, 180`  
- `Events1.size = 20k, 150k`  
- `Group.msgTtl = Not recorded`

Traffic is configured as emergency-oriented load with timing/size parameters aligned to this disaster narrative.

**DTN implication**

Under Epidemic routing, these parameters amplify trade-offs between urgency and congestion: short opportunities improve fast deliveries in contact windows but can sharply increase redundancy or message expiration when partitions persist.

### 5. Expected network behavior

- Contact opportunities are heterogeneous and depend on movement structure (clusters/partitions/routes).  
- Delivery is limited when temporal bridges are weak or TTL is very short.  
- Overhead rises quickly when flooding meets dense local contacts.  
- Delay can be bimodal: near-instant inside local contact islands, very high across partitions.

### 6. Role in the corpus

This scenario represents a specific **disaster communication regime** inside the corpus, contributing diversity relative to Urban/Campus/Social baselines and complementing other Disaster scenarios with a distinct structural stressor.

### 7. Distinguishing characteristics

- Disaster-focused configuration with explicit structural constraints.  
- Mobility/traffic coupling designed to stress store-carry-forward behavior.  
- Relevant for evaluating robustness under disrupted or intermittent connectivity.

### 8. Correlation with other scenarios (core 23)

Using the **23-core feature space** (`analysis/data/correlation_pearson_core23.csv`):

- **Most similar (top 3):**
  - D8_InfrastructureReturns_BackboneLinks — r ≈ **0.76**
  - S1_StrongCommunities_SeparateClusters — r ≈ **0.56**
  - D1_ShelterHotspots_Clusters — r ≈ **0.51**
- **Most different (top 3)** (smallest |r|):
  - R1_Rural_RandomWaypoint — r ≈ **0.00**
  - C3_Hackathon_24h — r ≈ **0.00**
  - T14_Buffer_200M — r ≈ **0.00**

Full pairwise correlations are available in `analysis/reports/correlation_core23_report.txt` and `analysis/data/correlation_pearson_core23.csv`.

**Interpretation**

The nearest scenarios share the same main structural levers (movement model family, host-group structure, and traffic scale), while near-zero correlations typically correspond to scenarios governed by orthogonal drivers (e.g., extreme range/speed, map routing, or different TTL/load regimes).

### 9. Cluster assignment

In the **Ward k=7 clustering** on the 23-core feature space (`cluster_assignments_core23.csv`), this scenario belongs to:

- **Cluster 2**.

### 10. Simulation outputs (optional)

If routing simulations have been run and metrics were extracted (`analysis/data/output_metrics.csv`):

| Metric | Value |
|--------|-------|
| delivery_ratio | 0.4429 |
| latency_mean | 3829.9325 |
| overhead_ratio | 68.589 |
| drop_ratio | 20.07608695652174 |

**Interpretation**

These outputs are consistent with the scenario's disaster constraints: delivery reflects bridge availability and TTL feasibility; overhead reflects replication pressure in local contacts; missing latency/overhead entries indicate no successful deliveries in the analyzed run.
