"""Canonical map definitions for the benchmark corpus.

Each entry specifies the OSM bounding box (or synthetic parameters),
target CRS for metre-based coordinates, and POI generation hints.
"""
from __future__ import annotations

MAP_DEFS: dict[str, dict] = {
    "HelsinkiDowntown": {
        "bbox": (60.165, 60.178, 24.925, 24.955),  # (south, north, west, east)
        "crs": "EPSG:3067",
        "family": "01_urban",
        "network_type": "drive",
        "description": "Helsinki city centre (Kluuvi / Kamppi / Esplanadi). Dense street grid with tram lines.",
        "poi_density": {"homes": 80, "offices": 40, "meetingspots": 25, "bus_routes": 3},
    },
    "KumpulaCampus": {
        "bbox": (60.2025, 60.2115, 24.958, 24.978),
        "crs": "EPSG:3067",
        "family": "02_campus",
        "network_type": "all",
        "description": "University of Helsinki Kumpula campus. Compact area with pedestrian paths and internal roads.",
        "poi_density": {"homes": 30, "offices": 20, "meetingspots": 15, "bus_routes": 1},
    },
    "ManhattanMidtownGrid": {
        "bbox": (40.748, 40.766, -73.993, -73.968),
        "crs": "EPSG:32618",
        "family": "03_vehicles",
        "network_type": "drive",
        "description": "Midtown Manhattan (34th-59th St). Regular grid ideal for vehicle routing benchmarks.",
        "poi_density": {"homes": 60, "offices": 50, "meetingspots": 30, "bus_routes": 2},
    },
    "NuuksioSparseTrails": {
        "bbox": (60.310, 60.335, 24.490, 24.535),
        "crs": "EPSG:3067",
        "family": "04_rural",
        "network_type": "all",
        "description": "Nuuksio National Park. Sparse trail network in forested area — rural/wildlife scenarios.",
        "poi_density": {"homes": 10, "offices": 5, "meetingspots": 8, "bus_routes": 1},
    },
    "HelsinkiDisrupted": {
        "bbox": (60.180, 60.196, 24.965, 24.995),
        "crs": "EPSG:3067",
        "family": "05_disaster",
        "network_type": "all",
        "description": "Kalasatama / Soernainen industrial harbour. Mixed-use area suitable for disaster/disruption modelling.",
        "poi_density": {"homes": 40, "offices": 25, "meetingspots": 15, "bus_routes": 2},
    },
    "KallioCommunityCompact": {
        "bbox": (60.179, 60.189, 24.938, 24.957),
        "crs": "EPSG:3067",
        "family": "06_social",
        "network_type": "all",
        "description": "Kallio residential neighbourhood. Dense, compact community — social/cluster scenarios.",
        "poi_density": {"homes": 70, "offices": 20, "meetingspots": 30, "bus_routes": 2},
    },
    "ControlCompactGrid": {
        "synthetic": True,
        "grid_size": (12, 10),
        "block_m": 150,
        "margin_m": 100,
        "crs": "local",
        "family": "07_stress_controls",
        "description": "Synthetic rectangular grid (12x10 blocks, 150 m spacing). Controlled baseline with no geographic bias.",
        "poi_density": {"homes": 50, "offices": 30, "meetingspots": 20, "bus_routes": 1},
    },
}

WORLD_SIZE_MARGIN_M = 200
