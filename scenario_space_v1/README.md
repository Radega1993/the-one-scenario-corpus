# scenario_space_v1: structural scenario design space

**Status:** Brute-force generator + reference-aligned `.settings` builder (2026-06-13)

Structural candidates for diversity analysis **before** Traffic Profiles. Aligned with [`the_one_settings_reference_node_mobility_messages.md`](../the_one_settings_reference_node_mobility_messages.md).

## Migración map_space_v1 (Fases 0–2b)

Trazabilidad del pipeline de mapas (auditoría, diseño, generación, validación) documentada en [`migration/`](migration/README.md).

| Track | Directorio | Estado |
|-------|------------|--------|
| Mapas | [`../map_space_v1/`](../map_space_v1/) | 26 candidatos validados |
| Estructural | Este directorio | 100.800 candidatos (6 mapas legacy) — congelado |

Índice maestro: [`migration/00_INDEX.md`](migration/00_INDEX.md)

## Generate all valid combinations (brute force)

```bash
python3 scenarios/setup/generate_scenario_space_v1.py --generate --sampling full --force
```

This writes:
- `manifest.csv` — one row per runnable candidate (~100,800 valid combinations)
- `settings/SV1_C*.settings` — executable The ONE files (map configured inside each file)

## Other modes

```bash
# Size estimate only
python3 scenarios/setup/generate_scenario_space_v1.py --estimate-only

# Preview without writing
python3 scenarios/setup/generate_scenario_space_v1.py --dry-run --max-settings 20

# Cap output
python3 scenarios/setup/generate_scenario_space_v1.py --generate --sampling full --max-settings 5000 --force

# Manifest only (no .settings)
python3 scenarios/setup/generate_scenario_space_v1.py --generate --manifest-only --max-settings 1000
```

## Design space

| Dimension | Values |
|-----------|--------|
| Maps | 6 (HelsinkiDowntown, KumpulaCampus, ManhattanMidtownGrid, NuuksioSparseTrails, HelsinkiDisrupted, KallioCommunityCompact) |
| Movement models | 5 (filtered per map) |
| Node population | 12 values (30–300) |
| Duration | 5 values (2h–24h) |
| Group structure | 5 types |
| Transmit range | 6 values |
| Buffer size | 4 values |
| Router | EpidemicRouter |

**Valid brute-force size:** ~100,800 combinations (after map×model filter + file validity).

## Placeholder traffic (not TP)

Per reference Part C.5:

- `Events1.interval = 60, 120`
- `Events1.size = 50k, 150k`
- `Group.msgTtl = 300` minutes

## Scripts

| File | Role |
|------|------|
| `scenarios/setup/generate_scenario_space_v1.py` | Enumerate design space, write manifest + settings |
| `scenarios/setup/scenario_space_settings_builder.py` | Build `.settings` content from parameters |
| `scenarios/analysis/config/scenario_design_space_v1.yaml` | Discrete parameter ranges |

## Note on corpus_v2

`corpus_v2/` was an experimental TP overlay corpus; it has been **removed**. Use `corpus_v1/` for the paper benchmark (540 scenarios).

## Archive

Outputs obsoletos (era 3K, seed stability runs): [`_archive/`](_archive/README.md)
