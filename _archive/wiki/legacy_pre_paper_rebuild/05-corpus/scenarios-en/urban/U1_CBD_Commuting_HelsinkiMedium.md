## Scenario U1 — U1_CBD_Commuting_HelsinkiMedium

### 1. Overview

- **Scenario ID:** U1
- **Name:** U1_CBD_Commuting_HelsinkiMedium
- **Family:** Urban
- **Settings file:** `corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiMedium.settings`

**Objective**

CBD commuting with concentrated offices and morning/evening rush peaks. WorkingDayMovement baseline for urban DTN.

### 2. Scenario configuration (core features)

Values below come from `analysis/data/features.csv` (raw) and the mapping to the 23-core subset.

| Feature | Value | Comment |
|---------|-------|---------|
| world_area | 63746480 |  |
| aspect_ratio | 0.8833 |  |
| N | 81 |  |
| nrofHostGroups | 2 |  |
| speed_mean | 8.5 |  |
| wait_mean | 20 |  |
| mm_WDM | 1 |  |
| mm_RWP | 0 |  |
| mm_MapRoute | 0 |  |
| mm_Cluster | 0 |  |
| mm_Bus | 1 |  |
| mm_Linear | 0 |  |
| transmitRange | 10 |  |
| bufferSize | 43000000 |  |
| transmitSpeed | 2400000 |  |
| msgTtl | 9500 |  |
| event_interval_mean | 40 |  |
| event_size_mean | 100000 |  |
| nrof_event_generators | 1 |  |
| pattern_burst | 0 |  |
| pattern_hub_target | 0 |  |
| workDayLength | 28800 | Work day length (s) if WorkingDayMovement |
| ownCarProb | 0 | Car ownership probability if WDM |
| clusterRange_mean | Not recorded | Mean cluster radius if ClusterMovement |

### 3. Mobility model

WorkingDayMovement over Helsinki map with bus carriers. Urban density, office clustering, and activity schedules vary by scenario lever.

**DTN implication**

Urban scenarios stress **contact frequency**, **temporal structure** (rush peaks, workday length), and **resource sharing** (buffer, transmit speed). Sparse (U5) vs dense (U7, U8) and short workday (U9) vs high variance (U12) create distinct connectivity regimes.

### 4. Traffic pattern

MessageEventGenerator with interval and size tuned per scenario. Uniform source–destination, single generator.

**DTN implication**

Event rate and TTL interact with mobility: short TTL (U7) favours fast relays; long TTL (U5) tolerates sparse contacts. Buffer and transmit speed affect congestion under high load.

### 5. Expected network behavior

- Contact opportunities driven by office clustering, workday length, and time variance.
- Delivery sensitive to density, range, and TTL.
- Overhead rises with flooding in dense contact windows.
- Latency typically moderate; sparse scenarios show higher delay.

### 6. Role in the corpus

This scenario represents an **urban communication regime** contributing diversity in connectivity, temporal structure, and resource stress relative to Campus/Rural/Disaster baselines.

### 7. Distinguishing characteristics

- Urban-focused configuration with WorkingDayMovement and bus carriers.
- Distinct lever (density, workday length, time variance, range, buffer) per scenario.
- Complements other Urban scenarios and Vehicles (shared Helsinki map).

### 8. Correlation with other scenarios (core 23)

Using the **23-core feature space** (`analysis/data/correlation_pearson_core23.csv`):

- **Most similar (top 3):**
  - U4_CongestionHotspot_HelsinkiMedium — r ≈ **0.95**
  - V4_CarOwnership_0_HelsinkiMedium — r ≈ **0.94**
  - U6_OfficeWaitHeavyTail_HelsinkiMedium — r ≈ **0.90**
- **Most different (top 3)** (smallest |r|):
  - C6_EmergencyDrill_Evacuation — r ≈ **0.00**
  - R2_VillagesTrails_ThreeClusters — r ≈ **-0.03**
  - V1_TaxiLow_HelsinkiMedium — r ≈ **0.04**

Full pairwise correlations are available in `analysis/reports/correlation_core23_report.txt` and `analysis/data/correlation_pearson_core23.csv`.

**Interpretation**

Similar scenarios share structural levers (WDM, density, range, TTL). Near-zero correlations correspond to scenarios governed by orthogonal drivers.

### 9. Cluster assignment

In the **Ward k=7 clustering** on the 23-core feature space (`cluster_assignments_core23.csv`), this scenario belongs to:

- **Cluster 1**.

### 10. Simulation outputs (optional)

If routing simulations have been run and metrics were extracted (`analysis/data/output_metrics.csv`):

| Metric | Value |
|--------|-------|
| delivery_ratio | 0.2262 |
| latency_mean | 8446.5668 |
| overhead_ratio | 72.9003 |
| drop_ratio | 9.371838687628161 |

**Interpretation**

Urban scenarios typically show moderate delivery and overhead; sparse (U5) or short-TTL (U7) variants stress protocol behaviour under constrained connectivity.
