# KumpulaCampus — campus settings audit

Generated: 2026-05-28T17:59:12

- Files audited: 78
- FAIL: 0
- C4 renamed: 0
- C6 LinearMovement cleanup: 13

## Movement model

All campus scenarios use `ShortestPathMapBasedMovement` on `data/KumpulaCampus/roads.wkt`. No `routeFile` — shuttle WKT is optional for figures only.

## C4 rename

`C4_Stadium_IngressEgress` → `C4_CampusEvent_IngressEgress`: mass campus event (auditorium / open day), not a sports stadium.

## C6 evacuation

Residual `Group.LinearMovement.*` keys removed (legacy 800×600 world). Evacuation represented by SPMM with speed 2–4 m/s and waitTime 0–10 s.
