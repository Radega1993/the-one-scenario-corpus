# Real trace inventory v1

## 1. What this inventory is

`real_trace_inventory_v1.csv` lists **external real traces** downloaded from
[IEEE DataPort](https://ieee-dataport.org/) (CRAWDAD collection and derived
packages) and registered for design, validation, or `trace_reference_synthetic`
anchoring.

Each row is a provenance + status record, **not** a redistributable dataset.

## 2. Not part of the redistributable corpus

These traces are **not** members of:

- `scenarios/corpus_v1/`
- SMS-v1 selected maps (`scenarios/selected_map_space_v1/`)
- SSS-v1 / pruned structural `.settings` trees

Do not mix licensed CRAWDAD / IEEE DataPort payloads into generated scenario packs.

## 3. How they are used

Typical uses:

- design anchors for SMS-v1 archetypes / anchors,
- conceptual validation of contact / mobility structure,
- sources that parametrize `trace_reference_synthetic` generators,
- literature-facing DTN/OppNet evidence (Haggle, RollerNet, DieselNet, Cabspotting, …).

## 4. Provenance

Traces come primarily from the CRAWDAD collection now hosted on
[IEEE DataPort](https://ieee-dataport.org/). Always record DOI / version /
local status in the CSV.

## 5. Licensing and redistribution

SMS-v1 / TPSC-v1 **do not** redistribute licensed payloads. The repository
keeps metadata, checksums, scripts, and inventories; raw files live under
`scenarios/external_traces/raw/` (gitignored).

## 6. Local storage policy

| Path | Role |
|------|------|
| `scenarios/map_space_v1/external_traces/` | Staging download folder (legacy / local drop zone) |
| `scenarios/external_traces/raw/crawdad/` | Canonical raw packages (ignored) |
| `scenarios/external_traces/processed/` | Metadata (+ ONE-normalized copies when available) |
| `scenarios/external_traces/registry/` | Inventory CSV/MD |

Ingest script:

```bash
python scenarios/external_traces/scripts/ingest_map_space_v1_external_traces.py
```

## 7. Field notes

- For raw CRAWDAD packages not yet converted to The ONE `StandardEventsReader`,
  `nodes` / `contacts` / `duration_seconds` are recorded as `0` (= not measured
  in ONE event units yet).
- The only currently **validated ONE StandardEventsReader** package is
  `haggle_one_cambridge_city_complete`.

## Registered traces (16)

| trace_id | family | version | DOI | SMS-v1 | status |
|----------|--------|---------|-----|--------|--------|
| `haggle_one_cambridge_city_complete` | uoi/haggle | 2009-05-29 | 10.15783/C70011 | yes | downloaded_and_validated |
| `cambridge_haggle_20090529` | cambridge/haggle | 2009-05-29 | 10.15783/C70011 | yes | downloaded |
| `cambridge_haggle_20060915` | cambridge/haggle | 2006-09-15 | 10.15783/C70011 | yes | downloaded |
| `cambridge_haggle_20060131` | cambridge/haggle | 2006-01-31 | 10.15783/C70011 | yes | downloaded |
| `upmc_rollernet_20090202` | upmc/rollernet | 2009-02-02 | 10.15783/C7ZK53 | yes | downloaded |
| `umass_diesel_20080914` | umass/diesel | 2008-09-14 | 10.15783/C7488P | yes | downloaded |
| `umass_diesel_20071202` | umass/diesel | 2007-12-02 | 10.15783/C7488P | yes | downloaded |
| `umass_diesel_20060117` | umass/diesel | 2006-01-17 | 10.15783/C7488P | yes | downloaded |
| `epfl_mobility_20090224` | epfl/mobility | 2009-02-24 | 10.15783/C7J010 | yes | downloaded |
| `roma_taxi_20140717` | roma/taxi | 2014-07-17 | 10.15783/C7QC7M | no | downloaded |
| `oviedo_asturies_er_20160808` | oviedo/asturies-er | 2016-08-08 | 10.15783/C7302B | no | downloaded |
| `coppe_ufrj_riobuses_20180319` | coppe-ufrj/RioBuses | 2018-03-19 | 10.15783/C7B64B | no | downloaded |
| `dartmouth_wardriving_20060602` | dartmouth/wardriving | 2006-06-02 | 10.15783/C7TG66 | no | downloaded |
| `st_andrews_sassy_20110603` | st_andrews/sassy | 2011-06-03 | 10.15783/C7S59X | yes | downloaded |
| `st_andrews_locshare_20111012` | st_andrews/locshare | 2011-10-12 | 10.15783/C7WW2F | yes | downloaded |
| `microsoft_vanlan_20070914` | microsoft/vanlan | 2007-09-14 | 10.15783/C7FG6S | no | downloaded |

> Note: `dartmouth_campus_*` packages were removed (README-only incomplete downloads). Wardriving is retained.

Machine-readable table: [`real_trace_inventory_v1.csv`](real_trace_inventory_v1.csv).  
Ingest summary: [`../reports/ieee_dataport_ingest_summary_v1.json`](../reports/ieee_dataport_ingest_summary_v1.json).
