# Validation — haggle_one_cambridge_city_complete

- **Validation date (UTC):** 2026-07-22T14:44:39.199257+00:00
- **Status:** **PASS**
- **Validated path:** `scenarios/external_traces/processed/the_one/uoi_haggle_20160828/haggle_one_cambridge_city_complete/events.tsv`
- **Mapping path:** `scenarios/external_traces/processed/the_one/uoi_haggle_20160828/haggle_one_cambridge_city_complete/id_mapping.tsv`

## Summary counts

| Metric | Value |
|--------|------:|
| Events | 21746 |
| Contacts (up events) | 10873 |
| Nodes | 52 |
| Duration (seconds) | 987529 |
| Duration (days) | 11.43 |
| Events up | 10873 |
| Events down | 10873 |
| Node ID range | 0–51 |
| Mapping rows | 52 |

## Expected contract

- Nodes: 52
- Contacts: 10873
- Events: 21746 (= 2 × contacts)
- Duration: 987529 s (~11.43 days)
- Schema: `time\taction\tfirst_node\tsecond_node\ttype` with `action=CONN`, `type∈{up,down}`

## Checksums (SHA256)

- `events.tsv`: `aedd7807b8f8138763a6be82db48e2c5e5e1f0c6305764a93a4e0d21364e6dbe`
- `id_mapping.tsv`: `2cbe99c52aa23dfdb4698f4b1cc47758c63416d5030285f51413636a57a27f3c`
- `metadata.yaml`: `fe5c642428f7da92b36d6dc98b82473fe95356e507cc2b669e43832ffb5b1abe`

## Errors

- none

## Warnings

- Original IDs 40 and 41 absent from mapping (expected: stationary devices that only saw external nodes).

## Notes

- This validation does **not** redistribute the raw CRAWDAD payload.
- Trace is a design/reference anchor for SMS-v1 / TPSC-v1, not an OSM map.
