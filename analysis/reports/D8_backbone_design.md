# D8 Emergency Backbone — design note

## Problem (pre-fix)

`D8_InfrastructureReturns_BackboneLinks` did not provide a useful benchmark for DTN protocol comparison:

1. **Missing backbone in corpus** — `ExternalEventsQueue` was stripped when traffic profiles were applied; `D8_backbone_events.txt` was absent.
2. **CONN on `bt0`** — partitions are ~800–1027 m apart with `bt0.transmitRange = 10 m`. Forced `CONN up` without interface id was torn down in the same simulation tick.
3. **Permanent mesh** — when `bb0` was added, 15 simultaneous `up` events at t=21600 with no `down` created a persistent cross-partition mesh, not intermittent infrastructure.
4. **Flat delivery ~49%** — consistent with intra-partition traffic only (~50% of random destinations land in the same partition).

## What D8 simulates now

`D8_EmergencyBackbone_IntermittentBridges` models **partial restoration of emergency communication** after a disaster:

- Two civilian/refugee clusters (partition A: hosts 0–39, partition B: hosts 40–79) remain **disconnected during the first 6 hours**.
- From **t = 21600 s**, **temporary backbone windows** appear via scheduled `CONN` events on logical interface `bb0`.
- Windows rotate across gateway pairs (0↔40, 5↔45, 10↔50, 15↔55, 0↔50, 10↔40) with **600 s up** and **1200 s gap** between windows.
- Each window ends with an explicit `down` event — links are **not permanent**.

## Implementation in The ONE

| Mechanism | Setting / file |
|-----------|----------------|
| Local shelter contact | `bt0`, `transmitRange = 10 m`, `ClusterMovement` |
| Backbone (logical) | `bb0`, `transmitRange = 0` (no proximity scan) |
| Scheduled links | `ExternalEventsQueue` → `D8_emergency_backbone_events.txt` |
| Event format | `time CONN hostA hostB up\|down bb0` |

### Why `bb0.transmitRange = 0`

In [`NetworkInterface.setHost()`](../../src/core/NetworkInterface.java), `transmitRange > 0` attaches a `ConnectivityGrid` optimizer. `SimpleBroadcastInterface.update()` then tears down out-of-range connections. With `transmitRange = 0`, `optimizer = null` and forced `bb0` links persist until a `down` event.

### Host addressing

Use numeric global indices in event files: `0–39` (group `a`), `40–79` (group `b`). The parser also accepts `a0`/`b0` forms but numeric ids are preferred.

### Traffic

Base scenario uses `Events1.hosts = 0, 80` (mixed intra/inter destinations). TP12 uses `hosts = 0, 40` / `tohosts = 40, 80` for explicit A→B traffic. Cross-partition delivery can be analysed post-sim from message destinations if needed.

## Limitations

- **Not physical radio** — `CONN` events are an abstraction; no path loss, no mobility of backbone nodes.
- **No native time-varying range** — The ONE settings cannot change `transmitRange` at runtime; external events are the standard workaround.
- **ConnectivityONEReport** does not tag interface id — validation infers inter-partition contacts from host indices.
- **Epidemic baseline** — delivery improvement depends on gateways being reached within `bb0` windows via intra-cluster `bt0` epidemic spread.

## Interpreting KPIs

| Metric | Expected behaviour |
|--------|------------------|
| `inter_partition_contacts_before` | ≈ 0 |
| `inter_partition_contacts_after` | ≥ 10 (base/TP01) |
| `max_inter_partition_uptime_s` | ≤ 900 s (window + margin) |
| `delivery_ratio` | > 0.55 for base/TP01 (up from ~0.49) but < 0.95 (still hard) |
| `latency_avg` | May increase for inter-partition messages delivered late via windows |
| `overhead_ratio` | Higher when windows are sparse — protocols that predict contacts should win |

## Reproducibility

```bash
python3 scenarios/setup/generate_d8_emergency_backbone_events.py
python3 scenarios/setup/regenerate_d8_corpus.py
```

## Files

- Base: `scenarios/base_scenarios/05_disaster/D8_EmergencyBackbone_IntermittentBridges.settings`
- Events: `scenarios/corpus_v1/05_disaster/D8_emergency_backbone_events.txt`
- Generator: `scenarios/setup/generate_d8_emergency_backbone_events.py`
- Corpus regen: `scenarios/setup/regenerate_d8_corpus.py`
- Validation: `scenarios/analysis/scripts/validation/validate_d8_backbone.py`
