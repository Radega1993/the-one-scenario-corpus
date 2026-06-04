"""Semantic route naming and policy per map/family."""

from __future__ import annotations

MAP_FAMILY: dict[str, str] = {
    "HelsinkiDowntown": "01_urban",
    "KumpulaCampus": "02_campus",
    "ManhattanMidtownGrid": "03_vehicles",
    "NuuksioSparseTrails": "04_rural",
    "HelsinkiDisrupted": "05_disaster",
    "KallioCommunityCompact": "06_social",
}

# (current_filename, recommended_filename, semantic_label)
ROUTE_SEMANTIC_ROWS: list[tuple[str, str, str, str]] = [
    # map_name, current, recommended, label
    ("HelsinkiDowntown", "A_bus.wkt", "A_bus.wkt", "urban_bus"),
    ("HelsinkiDowntown", "B_bus.wkt", "B_bus.wkt", "urban_bus"),
    ("HelsinkiDowntown", "C_bus.wkt", "C_bus.wkt", "urban_bus"),
    ("KumpulaCampus", "A_bus.wkt", "A_campus_shuttle.wkt", "campus_shuttle"),
    ("ManhattanMidtownGrid", "A_bus.wkt", "A_vehicle_route.wkt", "vehicle_route"),
    ("ManhattanMidtownGrid", "B_bus.wkt", "B_vehicle_route.wkt", "vehicle_route"),
    ("NuuksioSparseTrails", "A_bus.wkt", "A_ranger_patrol.wkt", "ranger_patrol"),
    ("HelsinkiDisrupted", "A_bus.wkt", "A_emergency_route.wkt", "emergency_route"),
    ("HelsinkiDisrupted", "B_bus.wkt", "B_mule_route.wkt", "mule_route"),
    ("KallioCommunityCompact", "A_bus.wkt", "A_community_route.wkt", "community_route"),
    ("KallioCommunityCompact", "B_bus.wkt", "B_community_route.wkt", "community_route"),
]

ROUTE_COLORS: dict[str, str] = {
    "A_bus.wkt": "#c05621",
    "B_bus.wkt": "#dd6b20",
    "C_bus.wkt": "#ed8936",
    "A_campus_shuttle.wkt": "#2b6cb0",
    "B_campus_shuttle.wkt": "#3182ce",
    "A_vehicle_route.wkt": "#805ad5",
    "B_vehicle_route.wkt": "#6b46c1",
    "A_ranger_patrol.wkt": "#276749",
    "B_rescue_route.wkt": "#38a169",
    "A_emergency_route.wkt": "#c53030",
    "B_mule_route.wkt": "#e53e3e",
    "A_community_route.wkt": "#d69e2e",
    "B_community_route.wkt": "#b7791f",
    "A_control_route.wkt": "#718096",
    "B_control_route.wkt": "#4a5568",
}

# Target route files to generate per map (semantic names)
FAMILY_ROUTE_TARGETS: dict[str, list[str]] = {}
for _map, _cur, _rec, _ in ROUTE_SEMANTIC_ROWS:
    FAMILY_ROUTE_TARGETS.setdefault(_map, []).append(_rec)

SETTINGS_PATH_RENAMES: dict[str, str] = {
    f"data/{m}/{cur}": f"data/{m}/{rec}"
    for m, cur, rec, _ in ROUTE_SEMANTIC_ROWS
    if cur != rec
}

LEGACY_ROUTE_GLOBS = ("*_bus.wkt", "*_shuttle.wkt", "*_patrol.wkt", "*_route.wkt", "*_mule*.wkt", "*_emergency*.wkt", "*_community*.wkt", "*_control*.wkt", "*_rescue*.wkt")