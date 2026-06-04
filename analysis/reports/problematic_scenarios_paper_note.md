# Paper note — mobility repair (S1, S6, D1, R2)

## English (methods / limitations)

Four environmental scenarios originally used `ClusterMovement` as the primary mobility model while still displaying a road map overlay. Because cluster centers are not constrained to the road network, spatial occupancy heatmaps showed isolated circular blobs and low interpretability of map-aware exploration metrics.

We revised these scenarios to use map-constrained models (`MapRouteMovement` and `ShortestPathMapBasedMovement`) with routes and POIs derived from each family’s `roads.wkt` graph. Narrative intent was preserved: strong communities with limited mixing (S1), small family routines (S6), shelter-centric emergency mobility (D1), and inter-village trail connectivity (R2). Traffic profiles (TP01–TP12) were not changed; only structural mobility and scenario identifiers were updated.

Validation included geometry checks (routes inside `worldSize`, near the road graph), traffic-profile consistency, and planned re-simulation of the 48 affected runs. Primary spatial reporting uses `coverage_road_cells_pct`; `coverage_world_pct` remains for transparency.

**Limitations:** route-based mobility still discretizes space; visited cells do not equal contact opportunities or delivery performance. Rural scenarios may remain low-coverage relative to urban maps by design.

## Español (breve)

Cuatro escenarios usaban `ClusterMovement` como movilidad principal pese al mapa viario, generando manchas circulares poco interpretables. Se reemplazó por movilidad map-aware (`MapRouteMovement`, `ShortestPathMapBasedMovement`) manteniendo la narrativa y sin modificar los perfiles de tráfico TP01–TP12.