# D8 backbone validation

Scenarios validated: **13** | PASS: **13** | FAIL: **0**

Data: [`D8_backbone_validation.csv`](../data/D8_backbone_validation.csv)

| Scenario | TP | Inter pre | Inter post | Delivery | Status |
|----------|-----|-----------|------------|----------|--------|
| `D8_EmergencyBackbone_IntermittentBridges` | base | 0 | 12 | 0.9267 | PASS |
| `D8_EmergencyBackbone_IntermittentBridges__TP01_Baseline` | TP01 | 0 | 12 | 0.9815 | PASS |
| `D8_EmergencyBackbone_IntermittentBridges__TP02_LowLoad` | TP02 | 0 | 12 | 0.9688 | PASS |
| `D8_EmergencyBackbone_IntermittentBridges__TP03_ManySmall` | TP03 | 0 | 12 | 0.9737 | PASS |
| `D8_EmergencyBackbone_IntermittentBridges__TP04_FewLarge` | TP04 | 0 | 12 | 0.6257 | PASS |
| `D8_EmergencyBackbone_IntermittentBridges__TP05_CriticalTTL` | TP05 | 0 | 12 | 0.1893 | PASS |
| `D8_EmergencyBackbone_IntermittentBridges__TP06_OneToMany` | TP06 | 0 | 12 | 0.9608 | PASS |
| `D8_EmergencyBackbone_IntermittentBridges__TP07_BurstWindow` | TP07 | 0 | 12 | 1.0000 | PASS |
| `D8_EmergencyBackbone_IntermittentBridges__TP08_HubTarget` | TP08 | 0 | 12 | 0.8082 | PASS |
| `D8_EmergencyBackbone_IntermittentBridges__TP09_Bimodal` | TP09 | 0 | 12 | 0.7216 | PASS |
| `D8_EmergencyBackbone_IntermittentBridges__TP10_Storm` | TP10 | 0 | 12 | 0.5512 | PASS |
| `D8_EmergencyBackbone_IntermittentBridges__TP11_ManyToOne` | TP11 | 0 | 12 | 0.9608 | PASS |
| `D8_EmergencyBackbone_IntermittentBridges__TP12_GroupToGroup` | TP12 | 0 | 12 | 0.9632 | PASS |
