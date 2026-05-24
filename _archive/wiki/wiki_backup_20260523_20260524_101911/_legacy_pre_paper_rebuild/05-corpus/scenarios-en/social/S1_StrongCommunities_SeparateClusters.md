## Scenario S1 — S1_StrongCommunities_SeparateClusters

### 1. Overview

- **Scenario ID:** S1
- **Name:** S1_StrongCommunities_SeparateClusters
- **Family:** Social
- **Settings file:** `corpus_v1/06_social/S1_StrongCommunities_SeparateClusters.settings`

**Objective**

Strong communities with separate clusters. Few inter-community links; routing depends on bridge nodes and opportunistic relays across clusters.

### 2. Scenario configuration (core features)

Values below come from `analysis/data/features.csv` (raw) and the mapping to the 23-core subset.

| Feature | Value | Comment |
|---------|-------|---------|
| world_area | 48000000 |  |
| aspect_ratio | 0.75 |  |
| N | 110 |  |
| nrofHostGroups | 4 |  |
| speed_mean | 0.7 |  |
| wait_mean | 180 |  |
| mm_WDM | 0 |  |
| mm_RWP | 0 |  |
| mm_MapRoute | 0 |  |
| mm_Cluster | 1 |  |
| mm_Bus | 0 |  |
| mm_Linear | 0 |  |
| transmitRange | 10 |  |
| bufferSize | 50000000 |  |
| transmitSpeed | 2000000 |  |
| msgTtl | 10000 |  |
| event_interval_mean | 120 |  |
| event_size_mean | 70000 |  |
| nrof_event_generators | 1 |  |
| pattern_burst | 0 |  |
| pattern_hub_target | 0 |  |
| workDayLength | Not recorded | Not used in this scenario |
| ownCarProb | Not recorded | Not used in this scenario |
| clusterRange_mean | 200 | Mean cluster radius if ClusterMovement |

### 3. Mobility model

Social scenarios use movement models that create community structure: ClusterMovement (S1, S6), RandomWaypoint with mixing parameters (S2, S3, S4), or two-layer configurations (S5).

**DTN implication**

Social scenarios stress **community structure**, **bridge nodes**, and **temporal patterns** (periodic vs random). Delivery depends on inter-community relays; protocols must exploit or tolerate sparse cross-cluster contacts.

### 4. Traffic pattern

MessageEventGenerator with interval and size tuned per scenario. Uniform or hub-target patterns.

**DTN implication**

Traffic interacts with community structure: messages within clusters benefit from local density; cross-cluster delivery requires patience or bridge exploitation.

### 5. Expected network behavior

- Contact opportunities driven by community structure and mixing.
- Delivery sensitive to bridge presence and TTL.
- Overhead can rise with flooding in dense local clusters.
- Latency varies: low within clusters, high across partitions.

### 6. Role in the corpus

This scenario represents a **social communication regime** contributing diversity in community structure, mixing, and temporal patterns relative to Urban/Campus/Rural baselines.

### 7. Distinguishing characteristics

- Social-focused configuration with explicit community or layer structure.
- Tests protocol behaviour under structured vs random mixing.
- Complements other Social scenarios with a distinct lever (cluster size, mixing, periodicity, layers).

### 8. Correlation with other scenarios (core 23)

Using the **23-core feature space** (`analysis/data/correlation_pearson_core23.csv`):

- **Most similar (top 3):**
  - D1_ShelterHotspots_Clusters — r ≈ **0.81**
  - S6_FamilyGroups_SmallPersistent — r ≈ **0.63**
  - D2_PartitionedCity_MuleBridge — r ≈ **0.56**
- **Most different (top 3)** (smallest |r|):
  - S4_RandomMixing_NoHotspots — r ≈ **0.00**
  - U7_HighTimeVariance_HelsinkiMedium — r ≈ **0.01**
  - U5_WorkdayShort_HelsinkiMedium — r ≈ **0.02**

Full pairwise correlations are available in `analysis/reports/correlation_core23_report.txt` and `analysis/data/correlation_pearson_core23.csv`.

**Interpretation**

Similar scenarios share structural levers (ClusterMovement, density, mixing). Near-zero correlations correspond to scenarios governed by orthogonal drivers.

### 9. Cluster assignment

In the **Ward k=7 clustering** on the 23-core feature space (`cluster_assignments_core23.csv`), this scenario belongs to:

- **Cluster 2**.

### 10. Simulation outputs (optional)

If routing simulations have been run and metrics were extracted (`analysis/data/output_metrics.csv`):

| Metric | Value |
|--------|-------|
| delivery_ratio | 0.2322 |
| latency_mean | 930.2812 |
| overhead_ratio | 110.7412 |
| drop_ratio | 15.55464480874317 |

**Interpretation**

Social scenarios show varied delivery depending on community structure and bridge availability; high mixing (S2) can improve delivery; strong clusters (S1, S6) may limit cross-cluster reach.
