# external_traces/

Reproducible staging area for **real external DTN/OppNet traces** used as design
anchors and conceptual references for **SMS-v1** (Selected Map Space) and
**TPSC-v1** (Traffic-Profiled Scenario Corpus).

These traces are **not** part of the redistributable simulation corpus.
They must stay separated from:

- `scenarios/corpus_v1/`
- `scenarios/selected_map_space_v1/`
- `scenarios/structural_scenario_space_v1/` / pruned settings trees

Source platform for the current downloads: [IEEE DataPort](https://ieee-dataport.org/)
(CRAWDAD collection + derived ONE packages).

## Layout

| Path | Role |
|------|------|
| `raw/crawdad/` | Downloaded CRAWDAD / IEEE DataPort packages (gitignored payloads) |
| `processed/crawdad/` | Per-package metadata manifests |
| `processed/the_one/` | ONE `StandardEventsReader` normalized copies (when available) |
| `registry/` | Inventory CSV/MD of registered real traces |
| `scripts/` | Ingest / validation / registration helpers |
| `reports/` | Validation + ingest reports (tracked) |

Local download drop zone (non-canonical): `scenarios/map_space_v1/external_traces/`.

## Policy: no redistribution of raw traces

Many CRAWDAD / IEEE DataPort datasets are licensed for research use but **not**
for republication inside a public git repository. This tree therefore:

1. Stores **metadata, checksums, scripts, and inventories** in git.
2. Keeps **raw archives / TSV** under `raw/` (ignored).
3. Ignores heavy processed tables (`*.tsv`, `*.csv`, archives) while keeping
   `metadata.yaml` and `checksums.sha256`.

## Relation to SMS-v1 / TPSC-v1

Real traces justify **families of scenarios** and help parameterize
`trace_reference_synthetic` maps / anchors (e.g. Haggle / RollerNet / DieselNet).
They do **not** automatically redefine the declared **15 map archetypes**.

Revised map-generation policy (roles, extractors, dry-run plan):

- [`scenarios/analysis/config/trace_to_map_generation_policy_v1.yaml`](../analysis/config/trace_to_map_generation_policy_v1.yaml)
- [`scenarios/analysis/reports/trace_to_map_generation_review_v1.md`](../analysis/reports/trace_to_map_generation_review_v1.md)
- [`scenarios/analysis/reports/map_generation_architecture_v2.md`](../analysis/reports/map_generation_architecture_v2.md)

## Ingest all packages from the staging folder

```bash
cd /path/to/the-one
source venv/bin/activate

python scenarios/external_traces/scripts/ingest_map_space_v1_external_traces.py
```

## Validate a StandardEventsReader trace

```bash
python scenarios/external_traces/scripts/validate_standard_events_trace.py \
  --trace scenarios/external_traces/processed/the_one/uoi_haggle_20160828/haggle_one_cambridge_city_complete/events.tsv \
  --mapping scenarios/external_traces/processed/the_one/uoi_haggle_20160828/haggle_one_cambridge_city_complete/id_mapping.tsv \
  --out scenarios/external_traces/reports/uoi_haggle_cambridge_city_complete_validation.md
```

## Currently registered

See [`registry/real_trace_inventory_v1.md`](registry/real_trace_inventory_v1.md)
(**18** packages as of the IEEE DataPort ingest).

Validated ONE StandardEventsReader package:

- `haggle_one_cambridge_city_complete` (52 nodes, 10873 contacts, 987529 s)
