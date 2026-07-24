# Real traces and SMS-v1 anchor rationale (v1)

**Status:** living inventory pointer  
**Canonical registry:** [`../../external_traces/registry/real_trace_inventory_v1.md`](../../external_traces/registry/real_trace_inventory_v1.md)  
**Source platform:** [IEEE DataPort](https://ieee-dataport.org/) (CRAWDAD collection)

## Purpose

Document how **external real DTN/OppNet traces** relate to SMS-v1 anchors and
archetypes without mixing licensed payloads into the redistributable corpus.

## Scope boundary

- Real traces live under `scenarios/external_traces/` (raw payloads gitignored).
- They are **design / reference** artifacts, not OSM map categories.
- They do **not** redefine the declared 15 archetypes by themselves.

## Downloaded real traces

All packages below were staged from local IEEE DataPort downloads under
`scenarios/map_space_v1/external_traces/` and ingested into the canonical tree.

| trace_id | family | DOI | SMS-v1 anchors / notes | status |
|----------|--------|-----|------------------------|--------|
| `haggle_one_cambridge_city_complete` | uoi/haggle | 10.15783/C70011 | `cambridge_haggle`, `haggle_contacts_only`, INFOCOM anchors; **ONE validated** | downloaded_and_validated |
| `cambridge_haggle_20090529` | cambridge/haggle | 10.15783/C70011 | source package for ONE conversion | downloaded |
| `cambridge_haggle_20060915` | cambridge/haggle | 10.15783/C70011 | earlier snapshot | downloaded |
| `cambridge_haggle_20060131` | cambridge/haggle | 10.15783/C70011 | earlier snapshot | downloaded |
| `upmc_rollernet_20090202` | upmc/rollernet | 10.15783/C7ZK53 | `rollernet_trace` / `corridor_linear` | downloaded |
| `umass_diesel_20080914` | umass/diesel | 10.15783/C7488P | `dieselnet_amherst` / bus routes | downloaded |
| `umass_diesel_20071202` | umass/diesel | 10.15783/C7488P | DieselNet intermediate | downloaded |
| `umass_diesel_20060117` | umass/diesel | 10.15783/C7488P | DieselNet earliest local | downloaded |
| `epfl_mobility_20090224` | epfl/mobility | 10.15783/C7J010 | `sf_cabspotting_downtown` | downloaded |
| `roma_taxi_20140717` | roma/taxi | 10.15783/C7QC7M | urban taxi mobility (no SMS anchor yet) | downloaded |
| `oviedo_asturies_er_20160808` | oviedo/asturies-er | 10.15783/C7302B | includes `.one.gz` contacts | downloaded |
| `coppe_ufrj_riobuses_20180319` | coppe-ufrj/RioBuses | 10.15783/C7B64B | bus mobility (large) | downloaded |
| `dartmouth_wardriving_20060602` | dartmouth/wardriving | 10.15783/C7TG66 | WiFi AP / wardrive | downloaded |
| `st_andrews_sassy_20110603` | st_andrews/sassy | 10.15783/C7S59X | social encounters | downloaded |
| `st_andrews_locshare_20111012` | st_andrews/locshare | 10.15783/C7WW2F | privacy/encounters | downloaded |
| `microsoft_vanlan_20070914` | microsoft/vanlan | 10.15783/C7FG6S | vehicular WiFi | downloaded |

### Highlight: `haggle_one_cambridge_city_complete`

| Field | Value |
|-------|-------|
| Origin | `cambridge/haggle/imote/content` (v. 2009-05-29) |
| Format | The ONE `StandardEventsReader` |
| Nodes / contacts / duration | 52 / 10873 / 987529 s (~11.43 days) |
| Status | **downloaded and validated** |
| Redistribution | raw trace **not** redistributed |

## Relation to declared anchors

SMS-v1 already documents anchors such as `cambridge_haggle`, `haggle_contacts_only`,
`rollernet_trace`, `dieselnet_amherst`, and `sf_cabspotting_downtown`. Downloaded
IEEE DataPort packages supply the concrete CRAWDAD evidence for those families.
They do not replace the 15-archetype contract.

## Policy reminder

Do not commit CRAWDAD / IEEE DataPort raw tables into the public repository.
Keep checksums + metadata + validation reports tracked; keep payloads local under
`scenarios/external_traces/raw/`.
