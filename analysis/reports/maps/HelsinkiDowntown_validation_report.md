# HelsinkiDowntown — validation report

Generated: 2026-05-28T17:49:25

## Blocking errors

- None

## Acceptable warnings

- POI points in 30–75 m band: documented in poi_report
- Bus routes WARNING: 3

## Methodological decisions

- Single OSM downtown extract for all `01_urban` scenarios (2093×1838 m).
- `A_bus.wkt` used in settings for WDM+bus integration; `B_bus`/`C_bus` optional assets.
- U2 renamed to SparseUrban (density lever, not geographic suburb).

## Actions applied

See `finalize_helsinki_downtown.py --apply` logs and correction CSVs.

- Settings audit FAIL count: 0