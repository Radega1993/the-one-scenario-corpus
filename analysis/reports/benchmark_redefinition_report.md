# Benchmark Redefinition Report

**Date:** 2026-05-26
**Scope:** corpus_v1 official benchmark restructuring

---

## 1. Summary

The corpus_v1 benchmark has been restructured into two tiers:

| Tier | Families | Scenarios | Description |
|------|----------|-----------|-------------|
| **Environmental benchmark** (core) | 01_urban, 02_campus, 03_vehicles, 04_rural, 05_disaster, 06_social | 540 | Real-world mobility families crossed with 12 traffic profiles |
| **Stress/control benchmark** (supplementary) | 07_stress_controls | 30 | Traffic-pattern laboratory with TP01_Baseline and TP10_Storm only |
| Deprecated | 07_stress_controls (archived TPs) | 150 | Former TP02-TP09, TP11, TP12 combinations moved to `_archive/deprecated_traffic_tp/` |

**Official active total: 570 scenarios.**

---

## 2. Environmental families vs. traffic profiles

### What is an environmental family?

An environmental family defines a **mobility context**: the physical environment (urban grid, campus, rural trails, disaster zone), the movement models used (WorkingDayMovement, ClusterMovement, MapRouteMovement, etc.), the node density, the map topology, and the spatial constraints that shape contact patterns.

The six environmental families are:

| Family | Mobility context | Base scenarios |
|--------|-----------------|----------------|
| 01_urban | Dense city streets, commuting patterns, public transport | 7 |
| 02_campus | Compact academic campus, pedestrian movement | 6 |
| 03_vehicles | Vehicle routing on road networks | 5 |
| 04_rural | Sparse trails, low density, long inter-contact times | 12 |
| 05_disaster | Post-disaster disrupted networks, evacuations | 9 |
| 06_social | Community clusters, social mixing | 6 |

### What is a traffic profile (TP)?

A traffic profile defines the **application-layer workload**: message size, creation rate, TTL, source/destination patterns, and buffer constraints. The 12 canonical profiles (TP01-TP12) systematically vary these parameters to stress-test routing protocols under different workload conditions.

Traffic profiles are **orthogonal** to mobility. The same TP can be applied to any environmental family, producing a controlled factorial design: 45 base scenarios x 12 TP = 540 environmental scenarios.

### Why the distinction matters

The factorial crossing of environment x traffic profile is the core experimental design of the benchmark. Each environmental family provides a distinct contact pattern (driven by mobility), while each TP provides a distinct workload (driven by application). Analysing delivery ratio, latency, and overhead across this matrix reveals how routing protocols respond to both dimensions independently.

---

## 3. Why stress/control scenarios are not part of the core benchmark

### The 07_stress_controls family

The former `07_traffic` family (now `07_stress_controls`) contains 15 base scenarios that were designed as **traffic-pattern laboratories**: T1_ManySmallMsgs, T2_FewHugeMsgs, T8_BurstTraffic, T9_BufferStress, etc. These scenarios use:

- **Synthetic grid map** (ControlCompactGrid): a regular 12x10 block grid with no geographic bias
- **ShortestPathMapBasedMovement**: uniform, predictable mobility
- **Deliberately extreme parameter values**: 1-minute TTL, 200 MB buffers, 256 kbps transmit speed limits

The purpose of these scenarios is to isolate the effect of a single traffic variable (message size, TTL, buffer, rate) on protocol performance. They serve as **controls** and **stress tests**, not as realistic deployment scenarios.

### Methodological reasons for separation

1. **Confounding with traffic profiles:** Each T* base scenario already encodes a specific traffic pattern (e.g., T1 = many small messages, T4 = very short TTL). Applying the 12 TPs on top of these creates **double parameterisation** of the same variables, producing confounding factors:
   - T1_ManySmallMsgs + TP03_ManySmall = redundant doubling of small-message stress
   - T4_VeryShortTtl + TP05_CriticalTTL = TTL stress applied twice
   - T9_BufferStress + TP10_Storm = extreme load on top of extreme load

   These combinations do not test meaningful new dimensions --- they amplify a single factor beyond any realistic scenario.

2. **Synthetic mobility:** ControlCompactGrid provides uniform, symmetric contact opportunities by design. This removes the environmental variation that is the primary research question. Including these scenarios in the core benchmark would dilute the signal from real-environment families.

3. **Statistical design:** The core benchmark follows a 6 (environments) x 12 (TPs) factorial design. Adding a 7th "environment" that is actually a traffic-variable laboratory breaks the factorial structure and makes ANOVA-style analysis invalid, since `07_stress_controls` does not represent an environmental condition.

4. **Paper clarity:** Separating stress/control scenarios simplifies reporting. The core benchmark answers "how do protocols perform across environments and workloads?". The stress/control supplement answers "what are the protocol limits under extreme conditions?".

---

## 4. Confounding factors when applying TP over traffic stress

When TP profiles are applied to `07_stress_controls` base scenarios, the following confounding problems arise:

| Base scenario | Conflicting TP | Problem |
|---------------|---------------|---------|
| T1_ManySmallMsgs_HighRate | TP03_ManySmall | Both specify high-rate small messages; effect cannot be attributed to either |
| T2_FewHugeMsgs_LowRate | TP04_FewLarge | Both specify large, infrequent messages |
| T4_VeryShortTtl_5to10min | TP05_CriticalTTL | Both reduce TTL to extreme values |
| T5_VeryLongTtl_6to24h | TP05_CriticalTTL | TTL direction contradicts between base and TP |
| T8_BurstTraffic_TimeWindows | TP07_BurstWindow | Both create bursty traffic patterns |
| T9_BufferStress_SmallBufferHighTraffic | TP10_Storm | Extreme load on extreme buffer stress |
| T7_TargetedToHubs_FewDestinations | TP08_HubTarget | Both concentrate traffic on few destinations |

For this reason, only two TPs are retained for `07_stress_controls`:

- **TP01_Baseline:** neutral workload, serves as the canonical control condition
- **TP10_Storm:** extreme load, tests protocol behaviour under maximum stress without variable conflict (Storm affects rate/size, which is compatible with buffer/TTL/topology stress bases)

---

## 5. Official benchmark for the paper

### Core environmental benchmark

| Metric | Value |
|--------|-------|
| Environmental families | 6 |
| Base scenarios per family | 7 + 6 + 5 + 12 + 9 + 6 = 45 |
| Traffic profiles per base | 12 |
| **Total core scenarios** | **540** |

### Supplementary stress/control benchmark

| Metric | Value |
|--------|-------|
| Family | 07_stress_controls |
| Base scenarios | 15 |
| Traffic profiles per base | 2 (TP01, TP10) |
| **Total stress scenarios** | **30** |

### Total

| Category | Count |
|----------|-------|
| Core (environmental) | 540 |
| Supplementary (stress/control) | 30 |
| **Official active total** | **570** |
| Deprecated (archived) | 150 |
| Historical total (before deprecation) | 720 |

---

## 6. Changes applied

### Directory structure

- `corpus_v1/07_traffic/` renamed to `corpus_v1/07_stress_controls/`
- 150 deprecated .settings files moved to `_archive/deprecated_traffic_tp/`
- 30 active .settings files remain in `corpus_v1/07_stress_controls/`

### Artefacts updated

- `manifest.csv` and `manifest_revision.csv`: family column and settings_file paths
- `benchmark_definition.csv`: new file with `benchmark_group`, `included_in_core`, `included_in_stress`, `deprecated` columns
- All active Python scripts, JSON configs, CSV data files, and Markdown reports: `07_traffic` replaced with `07_stress_controls`

### Artefacts NOT touched

- `_archive/wiki/` backups: historical, left as-is
- `_archive/reports/`, `_archive/data/`, `_archive/scripts/`: historical
- `_backup_pre_migration/`: historical backup from map migration
- Existing simulation results: not deleted

---

## 7. Taxonomy reference

| Term | Definition |
|------|-----------|
| **Environmental benchmark** | Core benchmark comprising 6 families with real-world mobility contexts, each crossed with 12 traffic profiles. Used for protocol comparison in the paper. |
| **Stress/control benchmark** | Supplementary benchmark comprising 15 traffic-pattern laboratory scenarios on synthetic grid, tested with TP01 (baseline) and TP10 (storm). Used to establish protocol limits. |
| **Traffic profile (TP)** | Application-layer workload definition (message size, rate, TTL, source/destination pattern). Applied to environmental families only. |
| **Environmental family** | Mobility context definition (map, movement model, node density, spatial constraints). |
| **Deprecated scenario** | Former TP02-TP12 (excluding TP10) combinations of stress/control bases. Archived, not deleted. |

---

## 8. Recommendations for analysis

1. **Primary analysis:** Use the 540 core environmental scenarios. Report results with 6 (family) x 12 (TP) factorial structure.
2. **Stress analysis:** Report `07_stress_controls` results separately, focusing on protocol behaviour under extreme single-variable stress (buffer limits, TTL extremes, transmit speed constraints).
3. **Do not mix:** Never pool environmental and stress/control results in the same statistical analysis (ANOVA, correlation, etc.).
4. **Citation:** When referencing the benchmark size, use "570 active scenarios (540 environmental + 30 stress/control)" rather than the historical 720.
