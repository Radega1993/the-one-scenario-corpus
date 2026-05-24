## Scenario {{ID}} — {{Name}}

### 1. Overview

- **Scenario ID:** {{ID}}  
- **Name:** {{Name}}  
- **Family:** {{Family}}  
- **Settings file:** `{{SettingsPath}}`

**Objective**

Short description of what the scenario models and why it exists in the corpus.

### 2. Scenario configuration (core features)

Summary of the 23 core features for this scenario.

| Feature | Value | Comment |
|---------|-------|---------|
| world_area | {{value}} | e.g. 4 km² (Wx×Wy) |
| aspect_ratio | {{value}} | Shape of the map (0–1] |
| N | {{value}} | Number of nodes |
| nrofHostGroups | {{value}} | Number of groups |
| speed_mean | {{value}} | Mean speed (m/s) |
| wait_mean | {{value}} | Mean wait time (s) |
| mm_WDM | {{0/1}} | WorkingDayMovement present |
| mm_RWP | {{0/1}} | RandomWaypoint present |
| mm_MapRoute | {{0/1}} | MapRoute present |
| mm_Cluster | {{0/1}} | ClusterMovement present |
| mm_Bus | {{0/1}} | BusMovement present |
| mm_Linear | {{0/1}} | LinearMovement present |
| transmitRange | {{value}} | Transmission range (m) |
| bufferSize | {{value}} | Buffer size (bytes) |
| transmitSpeed | {{value}} | Transmission speed (bytes/s) |
| msgTtl | {{value}} | Message TTL (s or h) |
| event_interval_mean | {{value}} | Mean inter-message time |
| event_size_mean | {{value}} | Mean message size (bytes) |
| nrof_event_generators | {{value}} | Number of generators |
| pattern_burst | {{0/1}} | Time-window / burst traffic |
| pattern_hub_target | {{0/1}} | Hub-target traffic |
| workDayLength | {{value}} | Work day length (s or h) |
| ownCarProb | {{value}} | Car ownership probability |

### 3. Mobility model

Describe the mobility model in human terms:

- Movement model(s): e.g. WorkingDayMovement with homes, offices, shops, leisure spots; RandomWaypoint in rural area; MapRoute on Helsinki map with buses, etc.
- How nodes move during the day (commuting, random walks, groups, clusters).

### 4. Traffic pattern

Explain how messages are generated:

- Who generates messages (which groups / nodes).
- Interval/rate (e.g. every 30–60 s).
- Destinations: random nodes, hubs, specific groups.
- One or two streams (Events1 / Events2).

### 5. Distinguishing characteristics

Bullet list of what makes this scenario different from the rest of the corpus, e.g.:

- High node density in CBD.
- Short TTL and small buffers (stress on congestion).
- Presence of buses as data mules.

### 6. Correlation with other scenarios (core 23)

Top similar and dissimilar scenarios using the 23-core feature space:

- **Most similar (top 3):**
  - {{Scenario}} — r = {{value}}
  - {{Scenario}} — r = {{value}}
  - {{Scenario}} — r = {{value}}
- **Most different (top 3):**
  - {{Scenario}} — r = {{value}}
  - {{Scenario}} — r = {{value}}
  - {{Scenario}} — r = {{value}}

Reference: `analysis/reports/correlation_core23_report.txt`.

### 7. Cluster assignment

- Cluster (Ward, k=7): {{cluster_id}}  
- Short description of the cluster (e.g. urban WDM with medium density, rural extreme, traffic stress).

Reference: `analysis/reports/clustering_report.txt`.

### 8. PCA position (optional)

If available, record the 2D PCA coordinates used in figures:

- PC1 = {{value}}
- PC2 = {{value}}

This helps visualise where the scenario lies in the diversity map.

### 9. Additional non-core parameters (optional but useful)

List any parameters that are important for interpreting the scenario but are not in the 23-core feature set, e.g.:

- `nrOfOffices = {{value}}`
- `nrOfMeetingSpots = {{value}}`
- `probGoShoppingAfterWork = {{value}}`
- `clusterRange_mean = {{value/NaN}}`

### 10. Simulation outputs (optional)

If routing simulations have been run, summarise per-scenario metrics, for example:

| Metric | Value |
|--------|-------|
| delivery_ratio | {{value}} |
| latency_mean | {{value}} |
| overhead_ratio | {{value}} |

Reference: `analysis/data/output_metrics.csv`.

