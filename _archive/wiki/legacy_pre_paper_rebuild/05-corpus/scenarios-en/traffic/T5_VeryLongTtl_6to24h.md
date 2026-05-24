## Scenario T5 — T5_VeryLongTtl_6to24h

### 1. Overview

- **Scenario ID:** T5
- **Name:** T5_VeryLongTtl_6to24h
- **Family:** Traffic
- **Settings file:** `corpus_v1/07_traffic/T5_VeryLongTtl_6to24h.settings`

**Objective**

Very long TTL (6–24 h). Patience-friendly; allows long store-carry-forward chains.

### 2. Scenario configuration (core features)

Values below come from `analysis/data/features.csv` (raw) and the mapping to the 23-core subset.

| Feature | Value | Comment |
|---------|-------|---------|
| world_area | 24750000 |  |
| aspect_ratio | 0.8182 |  |
| N | 40 |  |
| nrofHostGroups | 1 |  |
| speed_mean | 0.85 |  |
| wait_mean | 180 |  |
| mm_WDM | 0 |  |
| mm_RWP | 1 |  |
| mm_MapRoute | 0 |  |
| mm_Cluster | 0 |  |
| mm_Bus | 0 |  |
| mm_Linear | 0 |  |
| transmitRange | 14 |  |
| bufferSize | 52000000 |  |
| transmitSpeed | 1750000 |  |
| msgTtl | 1440 |  |
| event_interval_mean | 260 |  |
| event_size_mean | 90000 |  |
| nrof_event_generators | 1 |  |
| pattern_burst | 0 |  |
| pattern_hub_target | 0 |  |
| workDayLength | Not recorded | Not used in this scenario |
| ownCarProb | Not recorded | Not used in this scenario |
| clusterRange_mean | Not recorded | Mean cluster radius if ClusterMovement |

### 3. Mobility model

Traffic scenarios use shared RandomWaypoint mobility. The focus is on **message and resource levers** (size, rate, TTL, buffer, transmit speed) rather than mobility diversity.

**DTN implication**

Traffic scenarios stress **buffer management**, **TTL sensitivity**, **congestion**, and **transfer bottlenecks**. Same mobility across scenarios isolates protocol behaviour under different load and resource constraints.

### 4. Traffic pattern

MessageEventGenerator(s) with configurable interval, size, TTL, and pattern (uniform, burst, hub-target). One or two generators per scenario.

**DTN implication**

Event rate, size, and TTL interact: high rate + small buffer (T9) causes drops; short TTL (T4, T11) requires fast delivery; long TTL (T5, T12) tolerates patience.

### 5. Expected network behavior

- Delivery sensitive to TTL, buffer, and transmit speed.
- Overhead can spike with flooding or burst traffic.
- Latency varies: low when resources are ample, high under congestion or tiny buffer.
- Drop ratio high when buffer or TTL are stressed.

### 6. Role in the corpus

This scenario represents a **traffic/resource regime** contributing diversity in message size, rate, TTL, buffer, and transmit speed relative to mobility-focused families.

### 7. Distinguishing characteristics

- Traffic-focused configuration with shared mobility.
- Distinct lever (size, rate, TTL, buffer, transmit speed, pattern) per scenario.
- Complements other families by isolating traffic and resource effects.

### 8. Correlation with other scenarios (core 23)

Using the **23-core feature space** (`analysis/data/correlation_pearson_core23.csv`):

- **Most similar (top 3):**
  - D3_Aftershock_ErraticMobility — r ≈ **0.79**
  - S3_PeriodicMeetings_RegularRhythm — r ≈ **0.75**
  - T11_TTL_1min — r ≈ **0.71**
- **Most different (top 3)** (smallest |r|):
  - S5_TwoLayer_StudentsStaff — r ≈ **0.00**
  - T3_MixedBimodal_SmallAndLarge — r ≈ **0.00**
  - S2_WeakCommunities_HighMixing — r ≈ **0.02**

Full pairwise correlations are available in `analysis/reports/correlation_core23_report.txt` and `analysis/data/correlation_pearson_core23.csv`.

**Interpretation**

Similar scenarios share structural levers (event rate, size, TTL, buffer). Near-zero correlations correspond to scenarios governed by orthogonal drivers.

### 9. Cluster assignment

In the **Ward k=7 clustering** on the 23-core feature space (`cluster_assignments_core23.csv`), this scenario belongs to:

- **Cluster 7**.

### 10. Simulation outputs (optional)

If routing simulations have been run and metrics were extracted (`analysis/data/output_metrics.csv`):

| Metric | Value |
|--------|-------|
| delivery_ratio | 0.0932 |
| latency_mean | 24025.4 |
| overhead_ratio | 47.8 |
| drop_ratio | 0.0 |

**Interpretation**

Traffic scenarios show varied delivery depending on TTL, buffer, and transmit speed; short TTL or tiny buffer often yield low delivery or high drops.
