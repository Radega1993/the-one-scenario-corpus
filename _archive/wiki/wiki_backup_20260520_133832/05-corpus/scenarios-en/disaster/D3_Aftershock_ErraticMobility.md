## Scenario D3 — D3_Aftershock_ErraticMobility

### 1. Overview

- **Scenario ID:** D3  
- **Name:** D3_Aftershock_ErraticMobility  
- **Family:** Disaster  
- **Settings file:** `corpus_v1/05_disaster/D3_Aftershock_ErraticMobility.settings`

**Objective**

Erratic post-aftershock mobility with broad speed and waiting-time variability under short TTL.

### 2. Scenario configuration (core features)

Values below come from `analysis/data/features.csv` (raw) and the mapping to the 23-core subset.

| Feature | Value | Comment |
|---------|-------|---------|
| world_area | 36960000 | Total simulation area (m^2) |
| aspect_ratio | 0.8485 | min(width,height)/max(width,height) |
| N | 54 | Total nodes |
| nrofHostGroups | 1 | Number of host groups |
| speed_mean | 1.8 | Mean configured speed (m/s) |
| wait_mean | 450 | Mean pause/wait time (s) |
| mm_WDM | 0 | WorkingDayMovement enabled (1/0) |
| mm_RWP | 1 | RandomWaypoint enabled (1/0) |
| mm_MapRoute | 0 | MapRouteMovement enabled (1/0) |
| mm_Cluster | 0 | ClusterMovement enabled (1/0) |
| mm_Bus | 0 | BusMovement enabled (1/0) |
| mm_Linear | 0 | LinearMovement enabled (1/0) |
| transmitRange | 8 | Interface range (m) |
| bufferSize | 50000000 | Node buffer (bytes) |
| transmitSpeed | 2000000 | Interface speed (bytes/s) |
| msgTtl | 30 | Message TTL |
| event_interval_mean | 70 | Mean Events1 interval |
| event_size_mean | 62500 | Mean Events1 size (bytes) |
| nrof_event_generators | 1 | Number of event generators |
| pattern_burst | 0 | Burst windows in traffic (1/0) |
| pattern_hub_target | 0 | Hub-target traffic pattern (1/0) |
| workDayLength | — | Not used in this scenario |
| ownCarProb | — | Not used in this scenario |
| clusterRange_mean | — | Mean cluster radius if ClusterMovement |

### 3. Mobility model

- **World size:** `6600, 5600`  
- **Base speed range:** `0.1, 3.5`  
- **Base wait range:** `0, 900`

Single RandomWaypoint group with very wide speed and wait ranges.

**DTN implication**

This mobility design creates a constrained-contact disaster regime where connectivity depends on temporal bridges, dense local clusters, or opportunistic relays rather than stable end-to-end paths.

### 4. Traffic pattern

- `Events.nrof = 1`  
- `Events1.interval = 20, 120`  
- `Events1.size = 5k, 120k`  
- `Group.msgTtl = 30`

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
  - S3_PeriodicMeetings_RegularRhythm — r ≈ **0.83**
  - T5_VeryLongTtl_6to24h — r ≈ **0.79**
  - D6_ShortTtlCritical_5to10min — r ≈ **0.75**
- **Most different (top 3)** (smallest |r|):
  - T7_TargetedToHubs_FewDestinations — r ≈ **-0.01**
  - T2_FewHugeMsgs_LowRate — r ≈ **-0.01**
  - S2_WeakCommunities_HighMixing — r ≈ **0.01**

Full pairwise correlations are available in `analysis/reports/correlation_core23_report.txt` and `analysis/data/correlation_pearson_core23.csv`.

**Interpretation**

The nearest scenarios share the same main structural levers (movement model family, host-group structure, and traffic scale), while near-zero correlations typically correspond to scenarios governed by orthogonal drivers (e.g., extreme range/speed, map routing, or different TTL/load regimes).

### 9. Cluster assignment

In the **Ward k=7 clustering** on the 23-core feature space (`cluster_assignments_core23.csv`), this scenario belongs to:

- **Cluster 7**.

### 10. Simulation outputs (optional)

If routing simulations have been run and metrics were extracted (`analysis/data/output_metrics.csv`):

| Metric | Value |
|--------|-------|
| delivery_ratio | 0.0 |
| latency_mean | Not recorded |
| overhead_ratio | Not recorded |
| drop_ratio | 1.0288 |

**Interpretation**

These outputs are consistent with the scenario's disaster constraints: delivery reflects bridge availability and TTL feasibility; overhead reflects replication pressure in local contacts; missing latency/overhead entries indicate no successful deliveries in the analyzed run.
