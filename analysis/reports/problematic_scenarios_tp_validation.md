# Traffic profile validation — repaired scenarios (48 runs)

Generated after regenerating `S1`, `S6`, `D1`, `R2` with TP01–TP12 from new map-aware base settings.

## Scope

| scenario_base | Family | TP variants |
|---------------|--------|-------------|
| `S1_StrongCommunities_LimitedMixing` | 06_social | 12 |
| `S6_FamilyGroups_LocalRoutines` | 06_social | 12 |
| `D1_ShelterHotspots_EmergencyMobility` | 05_disaster | 12 |
| `R2_VillagesTrails_InterVillage` | 04_rural | 12 |

## Command

```bash
scenarios/analysis/.venv/bin/python scenarios/analysis/scripts/validation/validate_traffic_profiles.py \
  --manifest scenarios/analysis/data/problematic_repair_manifest.csv \
  --skip-metrics
```

## Checks

- `Events.hosts` / `Events.tohosts` within `[0, n_hosts)`
- TP06 OneToMany, TP08 HubTarget, TP11 ManyToOne, TP12 GroupToGroup host ranges
- `Group.msgTtl` matches canonical TP definitions
- Traffic profile blocks match `lib/traffic_profile_generator.py`

## Result

Settings validation: **48/48 OK** for the repair manifest subset (see `reports/validation/tp_validation_report.md` when run on subset).

Corpus-wide manifest restored to **540** environmental scenarios via `scenarios/setup/fix_manifest_after_mobility_repair.py`.