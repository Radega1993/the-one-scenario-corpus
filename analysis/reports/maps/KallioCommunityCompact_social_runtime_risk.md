# KallioCommunityCompact — social runtime risk

Generated as part of social map finalization.

## High-contact scenarios

### S1 — Strong communities (4 clusters, 110 hosts)

- **Movement:** ClusterMovement ×4, no inter-cluster bridge in base design.
- **Router:** EpidemicRouter on all groups.
- **Risk:** Dense clusters + epidemic forwarding → very high intra-cluster contacts and message copies, especially under TP03/TP06/TP07/TP09/TP10 (shorter intervals, larger messages, more hosts).
- **Interpretation:** Stress benchmark for community isolation and overload — not a map geometry error.

### S6 — Family groups (12 microclusters)

- **Movement:** ClusterMovement ×12, `clusterRange=16` (tight microclusters).
- **Risk:** Frequent intra-cluster pairwise contact; persistent family-scale structure.
- **Interpretation:** Tests long-lived small communities; timeouts under heavy TP are protocol/TP limits, not WKT defects.

## Map-based scenarios (S2–S5)

- SPMM on compact Kallio graph: moderate path diversity, realistic urban mixing.
- S4 explicitly avoids POI/cluster attractors — control for “no hotspots”.
- S5 two-layer (students vs staff) increases heterogeneity without cluster geometry.

## Recommendations

1. **Keep EpidemicRouter** as the social-family stress benchmark unless methodology explicitly requires another router.
2. Document simulation **timeouts** as Traffic Profile / protocol limitations when they occur under TP stress — not as map misconfiguration.
3. **Do not** reduce `nrofHosts` or `clusterRange` without methodological justification; changes would break cross-scenario comparability.
4. Community routes (`A_community_route.wkt`, `B_community_route.wkt`) are **figure assets only** — no `routeFile` in settings; they do not affect runtime mobility.

## Excluded from runtime scope

- Assigning `routeFile` to social scenarios.
- Modifying `Events*` traffic profile blocks during map finalization.
