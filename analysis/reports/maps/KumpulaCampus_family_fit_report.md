# KumpulaCampus — family fit (02_campus)

Generated as part of campus map finalization.

## Why this map fits 02_campus

| Criterion | KumpulaCampus |
|-----------|---------------|
| Geographic scale | Compact university campus (~1.1 km × 1.0 km sim window) |
| Network | OSM `all` — internal roads + pedestrian paths (4059 segments) |
| POI density | 30 homes, 20 offices, 15 meeting spots — sufficient for class/exam/social scenarios |
| Coverage | ~51% road length / worldSize area — high for a bounded campus |
| vs urban | No bus-integrated WDM; SPMM only; smaller, pedestrian-dominant |

## Scenario mapping

| Scenario | Methodological role on this map |
|----------|-----------------------------------|
| C1 ClassChange | Frequent between-class movement, moderate speed/wait |
| C2 ExamDay | Long stays, low speed, exam-day static behavior |
| C3 Hackathon 24h | 86400 s horizon, very long waits, slow persistent nodes |
| C4 CampusEvent | Two traffic peaks (ingress/egress) — renamed from Stadium; auditorium-scale event |
| C5 Library_Quiet | Low speed, long waits, sparse movement |
| C6 EmergencyDrill | Fast SPMM evacuation (high speed, low wait); no LinearMovement |

## C4 naming decision

`C4_Stadium_IngressEgress` → **`C4_CampusEvent_IngressEgress`**: the OSM extract has no sports stadium polygon; the scenario models a **mass campus event** (lecture hall, open day, graduation) with bimodal message load, not athletic ingress/egress.

## Shuttle asset

`A_campus_shuttle.wkt` is an **optional documentation route** (not referenced in `.settings`). Figures show resolved path (solid) vs stop order (dotted).

## Difference from HelsinkiDowntown (01_urban)

- Urban: dense CBD, WorkingDayMovement + bus integration, 2093×1838 m.
- Campus: single institution footprint, SPMM only, shuttle for visualization only.
