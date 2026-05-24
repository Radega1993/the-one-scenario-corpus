## Scenario V4 — V4_CarOwnership_0_HelsinkiMedium

### 1. Overview

- **Scenario ID:** V4
- **Name:** V4_CarOwnership_0_HelsinkiMedium
- **Family:** Vehicles
- **Settings file:** `corpus_v1/03_vehicles/V4_CarOwnership_0_HelsinkiMedium.settings`

**Objective**

Zero car ownership: pedestrians + bus. WorkingDayMovement baseline for vehicle family.

### 2. Scenario configuration (core features)

Values below come from `analysis/data/features.csv` (raw) and the mapping to the 23-core subset.

| Feature | Value | Comment |
|---------|-------|---------|
| world_area | 63033600 |  |
| aspect_ratio | 0.8933 |  |
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
| transmitRange | 12 |  |
| bufferSize | 40000000 |  |
| transmitSpeed | 2000000 |  |
| msgTtl | 7200 |  |
| event_interval_mean | 25 |  |
| event_size_mean | 70000 |  |
| nrof_event_generators | 1 |  |
| pattern_burst | 0 |  |
| pattern_hub_target | 0 |  |
| workDayLength | 25200 | Work day length (s) if WorkingDayMovement |
| ownCarProb | 0 | Car ownership probability if WDM |
| clusterRange_mean | Not recorded | Mean cluster radius if ClusterMovement |

### 3. Mobility model

Vehicle scenarios use MapRouteMovement (taxis), BusMovement (buses), or WorkingDayMovement with bus carriers (V6, V7). Helsinki map base.

**DTN implication**

Vehicle scenarios stress **speed**, **route structure**, and **carrier density**. Taxis (V1, V2) provide sparse or dense relays; buses (V3) concentrate traffic on routes; WDM+bus (V6, V7) mix pedestrian and vehicular mobility.

### 4. Traffic pattern

MessageEventGenerator with interval and size tuned per scenario. Uniform source–destination.

**DTN implication**

Event rate and TTL interact with vehicle speed and density: fast carriers (V2) can improve delivery; sparse carriers (V1) require patience.

### 5. Expected network behavior

- Contact opportunities driven by vehicle density and route overlap.
- Delivery sensitive to carrier count, speed, and range.
- Overhead typically lower than pedestrian flooding when carriers are few.
- Latency varies: low with dense fast carriers, high when sparse.

### 6. Role in the corpus

This scenario represents a **vehicular communication regime** contributing diversity in speed, carrier type, and density relative to Urban/Campus/Rural baselines.

### 7. Distinguishing characteristics

- Vehicle-focused configuration (taxis, buses, or WDM with cars).
- Tests protocol behaviour under vehicular relays and route-based mobility.
- Complements Urban (shared Helsinki map) with distinct mobility levers.

### 8. Correlation with other scenarios (core 23)

Using the **23-core feature space** (`analysis/data/correlation_pearson_core23.csv`):

- **Most similar (top 3):**
  - U6_OfficeWaitHeavyTail_HelsinkiMedium — r ≈ **0.96**
  - U1_CBD_Commuting_HelsinkiMedium — r ≈ **0.94**
  - U4_CongestionHotspot_HelsinkiMedium — r ≈ **0.94**
- **Most different (top 3)** (smallest |r|):
  - D5_UAVMule_FastRoute_HelsinkiMedium — r ≈ **-0.01**
  - C6_EmergencyDrill_Evacuation — r ≈ **0.03**
  - S6_FamilyGroups_SmallPersistent — r ≈ **-0.03**

Full pairwise correlations are available in `analysis/reports/correlation_core23_report.txt` and `analysis/data/correlation_pearson_core23.csv`.

**Interpretation**

Similar scenarios share structural levers (MapRoute, Bus, WDM, density). Near-zero correlations correspond to scenarios governed by orthogonal drivers.

### 9. Cluster assignment

In the **Ward k=7 clustering** on the 23-core feature space (`cluster_assignments_core23.csv`), this scenario belongs to:

- **Cluster 1**.

### 10. Simulation outputs (optional)

If routing simulations have been run and metrics were extracted (`analysis/data/output_metrics.csv`):

| Metric | Value |
|--------|-------|
| delivery_ratio | 0.2064 |
| latency_mean | 7249.5262 |
| overhead_ratio | 78.8841 |
| drop_ratio | 9.941216678058783 |

**Interpretation**

Vehicle scenarios show varied delivery: high with dense taxis (V2), moderate with buses (V3), lower with sparse taxis (V1) or WDM variants (V6, V7).
