# Nuuksio Sparse Trails — map and route review

## Summary

**NuuksioSparseTrails** (family `04_rural`) models a **sparse trail network** in Nuuksio National Park. Partial graph coverage is expected and acceptable for rural OppNet scenarios (R4).

## Route semantics

| Legacy | Semantic | Role |
|--------|----------|------|
| `A_bus.wkt` | `A_ranger_patrol.wkt` | Long patrol along main trail component |

The label **bus** is rejected for this family: there is no urban transit network. Corpus R4 scenarios reference `routeFile` → `A_ranger_patrol.wkt` after rename.

## Validation expectations

- Vertex distance threshold: **150 m** (trails are sparse).
- Route may cover only part of the map — **partial coverage OK**.
- Ranger route: fewer stops (≤10), graph-coherent tour on high-degree / peripheral trail nodes.

## Paper wording

> Rural scenarios use a sparse trail graph with a single ranger-style patrol route (waypoints on trails; movement between stops follows the trail network).