#!/usr/bin/env python3
"""
Build executable The ONE .settings for scenario_space_v1.

Aligned with: scenarios/the_one_settings_reference_node_mobility_messages.md
- Structural scenarios only (placeholder traffic, no Traffic Profiles).
- Validity rules R001–R015 from reference Part H.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data"
SCENARIOS_DIR = REPO_ROOT / "scenarios"

SPEED_REGIME_RANGES = {
    "pedestrian_slow": "0.3, 1.0",
    "pedestrian_normal": "0.5, 1.5",
    "pedestrian_fast": "0.8, 2.0",
    "vehicle_slow": "3.0, 8.0",
    "vehicle_normal": "7.0, 15.0",
}

WAIT_REGIME_RANGES = {
    "low_pause": "0, 60",
    "normal_pause": "30, 240",
    "high_pause": "300, 1800",
}

MAP_ALLOWED_MODELS = {
    "HelsinkiDowntown": ["WorkingDayMovement", "ShortestPathMapBasedMovement", "BusMovement"],
    "KumpulaCampus": ["ShortestPathMapBasedMovement"],
    "ManhattanMidtownGrid": ["ShortestPathMapBasedMovement", "MapRouteMovement", "BusMovement"],
    "NuuksioSparseTrails": ["ShortestPathMapBasedMovement", "MapRouteMovement"],
    "HelsinkiDisrupted": ["ShortestPathMapBasedMovement", "MapRouteMovement", "ClusterMovement"],
    "KallioCommunityCompact": ["ShortestPathMapBasedMovement", "MapRouteMovement"],
}

MAP_ASSETS: dict[str, dict[str, str]] = {
    "HelsinkiDowntown": {
        "wdm_route": "A_bus.wkt",
        "vehicle_route": "A_bus.wkt",
        "bus_route": "A_bus.wkt",
    },
    "ManhattanMidtownGrid": {
        "vehicle_route": "A_vehicle_route.wkt",
        "bus_route": "A_vehicle_route.wkt",
    },
    "NuuksioSparseTrails": {"vehicle_route": "A_ranger_patrol.wkt"},
    "HelsinkiDisrupted": {
        "vehicle_route": "A_emergency_route.wkt",
        "bus_route": "B_mule_route.wkt",
    },
    "KallioCommunityCompact": {
        "vehicle_route": "A_community_route.wkt",
        "bus_route": "A_community_route.wkt",
    },
}

GROUP_STRUCTURE_NGROUPS = {
    "single_homogeneous": 1,
    "pedestrian_transit": 2,
    "pedestrian_vehicle": 2,
    "pedestrian_shortestpath_heterogeneous": 2,
    "cluster_nomadic": 2,
    "single_group": 1,
    "two_balanced_groups": 2,
    "four_communities": 2,
    "hub_and_spokes": 2,
    "partitioned_groups": 2,
}

# Reference Part G / C.5 — placeholder traffic (not a Traffic Profile)
PLACEHOLDER_MSG_TTL = 300
PLACEHOLDER_EVENTS = {
    "interval": "60, 120",
    "size": "50k, 150k",
    "prefix": "M",
}


@dataclass
class BuilderContext:
    maps_assets_root: Path | None = None
    scenario_prefix: str = "SV1_"
    placeholder_events: dict[str, str] = field(default_factory=lambda: dict(PLACEHOLDER_EVENTS))
    header_tag: str = "scenario_space_v1"


_builder_ctx = BuilderContext()


def set_builder_context(ctx: BuilderContext) -> None:
    global _builder_ctx
    _builder_ctx = ctx


def get_builder_context() -> BuilderContext:
    return _builder_ctx


def _map_dir(map_id: str) -> Path:
    if _builder_ctx.maps_assets_root is not None:
        return _builder_ctx.maps_assets_root / map_id
    return DATA_DIR / map_id


def _map_rel_prefix(map_id: str) -> str:
    if _builder_ctx.maps_assets_root is not None:
        try:
            rel = (_builder_ctx.maps_assets_root / map_id).relative_to(REPO_ROOT)
            return str(rel).replace("\\", "/")
        except ValueError:
            return f"scenarios/structural_scenario_space_v1/assets/{map_id}"
    return f"data/{map_id}"


@dataclass
class ScenarioParam:
    """Parameter combination for one structural scenario."""

    map_id: str
    movement_model: str
    n_hosts: int
    end_time: int
    group_structure: str
    transmit_range: int
    buffer_size: str
    router: str
    rng_seed: int
    scenario_index: int
    param_id: str
    movement_model_id: str = ""
    speed_regime: str = "pedestrian_normal"
    wait_regime: str = "normal_pause"
    scenario_prefix: str = ""

    @property
    def candidate_id(self) -> str:
        return f"C{self.scenario_index:05d}"

    @property
    def scenario_name(self) -> str:
        prefix = self.scenario_prefix or _builder_ctx.scenario_prefix
        return f"{prefix}{self.candidate_id}"

    @property
    def effective_group_structure(self) -> str:
        from structural_scenario_v1_common import GROUP_STRUCTURE_TO_BUILDER

        return GROUP_STRUCTURE_TO_BUILDER.get(self.group_structure, self.group_structure)


def load_maps_index() -> dict[str, dict[str, Any]]:
    """Load map specs from data/*/metadata.json (legacy mode)."""
    index: dict[str, dict[str, Any]] = {}
    for map_dir in sorted(DATA_DIR.iterdir()):
        if not map_dir.is_dir():
            continue
        meta_path = map_dir / "metadata.json"
        if not meta_path.is_file():
            continue
        with meta_path.open(encoding="utf-8") as f:
            meta = json.load(f)
        map_id = meta.get("name", map_dir.name)
        ws = meta.get("world_size", [1000, 1000])
        index[map_id] = {
            "world_size_x": int(ws[0]),
            "world_size_y": int(ws[1]),
            "wkt_path": f"data/{map_id}/roads.wkt",
            "allowed_movement_models": MAP_ALLOWED_MODELS.get(map_id, []),
        }
    return index


def infer_allowed_movement_models(map_id: str, row: dict[str, str], map_dir: Path | None = None) -> list[str]:
    """Derive allowed movement models from manifest row and installed assets."""
    models = ["ShortestPathMapBasedMovement"]
    d = map_dir or (DATA_DIR / map_id)
    arch = row.get("archetype", "")
    wdm_arches = {
        "dense_urban_irregular",
        "campus_compact",
        "compact_residential",
        "conference_event_compact",
    }
    if arch in wdm_arches and (d / "A_homes.wkt").is_file():
        models.append("WorkingDayMovement")
    if any((d / f).is_file() for f in ("A_bus.wkt", "A_vehicle_route.wkt")):
        models.append("BusMovement")
        models.append("MapRouteMovement")
    if arch in ("industrial_disrupted", "clustered_communities", "compact_residential"):
        models.append("ClusterMovement")
    return sorted(set(models))


def load_maps_from_manifest(manifest_path: Path) -> tuple[dict[str, dict], dict[str, dict[str, Any]]]:
    """Load maps from manifest_maps_selected.csv for scenario generation."""
    import csv

    maps_yaml_style: dict[str, dict] = {}
    maps_index: dict[str, dict[str, Any]] = {}
    features_path = manifest_path.parent.parent.parent / "analysis" / "data" / "map_space_v1_features.csv"
    features_by_id: dict[str, dict[str, str]] = {}
    if features_path.is_file():
        with features_path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                features_by_id[row.get("map_id", "")] = row

    with manifest_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            map_id = row["map_id"]
            wx = int(float(row.get("world_size_x", 0) or 0))
            wy = int(float(row.get("world_size_y", 0) or 0))
            allowed = infer_allowed_movement_models(map_id, row)
            feats = features_by_id.get(map_id, {})
            maps_index[map_id] = {
                "world_size_x": wx,
                "world_size_y": wy,
                "wkt_path": f"data/{map_id}/roads.wkt",
                "allowed_movement_models": allowed,
                "map_archetype": row.get("archetype", ""),
                "source_type": row.get("source_type", ""),
                "anchor_id": row.get("anchor_id", ""),
                "generator_type": row.get("generator_type", ""),
                "road_density": feats.get("road_density", ""),
                "gridness_score": feats.get("gridness_score", ""),
                "partition_score": feats.get("partition_score", ""),
            }
            maps_yaml_style[map_id] = {
                "id": map_id,
                "wkt_path": f"data/{map_id}/roads.wkt",
                "world_size_x": wx,
                "world_size_y": wy,
                "allowed_movement_models": allowed,
                "map_archetype": row.get("archetype", ""),
                "source_type": row.get("source_type", ""),
                "anchor_id": row.get("anchor_id", ""),
            }
    return maps_yaml_style, maps_index


def load_structural_maps_manifest(
    manifest_path: Path,
    spec: dict[str, Any],
    assets_root: Path,
    features_by_id: dict[str, dict[str, str]] | None = None,
) -> tuple[dict[str, dict], dict[str, dict[str, Any]]]:
    """Load 75-map manifest with structural asset paths and YAML compatibility."""
    import csv

    from structural_scenario_v1_common import infer_allowed_movement_ids, movement_class

    features_by_id = features_by_id or {}
    maps_yaml_style: dict[str, dict] = {}
    maps_index: dict[str, dict[str, Any]] = {}
    with manifest_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            map_id = row["map_id"]
            wx = int(float(row.get("world_size_x", 0) or 0))
            wy = int(float(row.get("world_size_y", 0) or 0))
            rel = f"scenarios/structural_scenario_space_v1/assets/{map_id}"
            allowed_ids = infer_allowed_movement_ids(map_id, row, spec, assets_root)
            allowed_classes = [movement_class(m) for m in allowed_ids]
            feats = features_by_id.get(map_id, row)
            maps_index[map_id] = {
                "world_size_x": wx,
                "world_size_y": wy,
                "wkt_path": f"{rel}/roads.wkt",
                "allowed_movement_models": allowed_classes,
                "allowed_movement_ids": allowed_ids,
                "map_archetype": row.get("archetype", ""),
                "source_type": row.get("source_type", ""),
                "anchor_id": row.get("anchor_id", ""),
                "generator_type": row.get("generator_type", ""),
                "road_density": feats.get("road_density", ""),
                "gridness_score": feats.get("gridness_score", ""),
                "partition_score": feats.get("partition_score", ""),
            }
            maps_yaml_style[map_id] = dict(maps_index[map_id], id=map_id)
    return maps_yaml_style, maps_index


def resolve_route_rel(map_id: str, movement_model: str) -> str | None:
    """Return repo-relative route path or None."""
    map_dir = _map_dir(map_id)
    if not map_dir.is_dir():
        return None

    assets = MAP_ASSETS.get(map_id, {})
    prefix = _map_rel_prefix(map_id)
    if movement_model == "WorkingDayMovement":
        rel = assets.get("wdm_route", "A_bus.wkt")
        return f"{prefix}/{rel}" if (map_dir / rel).is_file() else None

    key = "bus_route" if movement_model == "BusMovement" else "vehicle_route"
    rel = assets.get(key)
    if rel and (map_dir / rel).is_file():
        return f"{prefix}/{rel}"

    for p in sorted(map_dir.glob("*.wkt")):
        name = p.name.lower()
        if name == "roads.wkt":
            continue
        if any(tok in name for tok in ("route", "bus", "patrol", "shuttle", "mule")):
            return f"{prefix}/{p.name}"
    return None


def has_bus_route(map_id: str) -> bool:
    return resolve_route_rel(map_id, "BusMovement") is not None


def is_candidate_runnable(param: ScenarioParam, maps_index: dict[str, dict]) -> tuple[bool, str]:
    """Check reference validity rules before writing .settings."""
    if param.n_hosts < 1:
        return False, "n_hosts must be positive"

    if param.map_id not in maps_index:
        return False, f"unknown map {param.map_id}"

    allowed = maps_index[param.map_id].get("allowed_movement_models", [])
    if allowed and param.movement_model not in allowed:
        return False, f"{param.movement_model} not allowed on {param.map_id}"

    if param.movement_model == "RandomWaypoint":
        return True, ""

    if param.movement_model == "ClusterMovement":
        wx = maps_index[param.map_id]["world_size_x"]
        wy = maps_index[param.map_id]["world_size_y"]
        if wx <= 0 or wy <= 0:
            return False, "invalid world_size"
    else:
        map_dir = _map_dir(param.map_id)
        if not map_dir.is_dir():
            return False, "map data directory missing"

        if param.movement_model == "WorkingDayMovement":
            for fname in ("A_homes.wkt", "A_offices.wkt", "A_meetingspots.wkt"):
                if not (map_dir / fname).is_file():
                    return False, f"POI missing: {fname}"
            if resolve_route_rel(param.map_id, "WorkingDayMovement") is None:
                return False, "WDM route missing"

        if param.movement_model in ("MapRouteMovement", "BusMovement", "ShortestPathMapBasedMovement"):
            if param.movement_model != "ShortestPathMapBasedMovement":
                if resolve_route_rel(param.map_id, param.movement_model) is None:
                    return False, f"route missing for {param.movement_model}"
            elif not (map_dir / "roads.wkt").is_file():
                return False, "roads.wkt missing"

    struct = param.effective_group_structure
    n_groups = GROUP_STRUCTURE_NGROUPS.get(struct, 1)
    if n_groups > 1 and param.n_hosts < 2:
        return False, "multi-group structure needs n_hosts >= 2"

    if struct == "pedestrian_transit" and not has_bus_route(param.map_id):
        if param.movement_model in ("BusMovement", "WorkingDayMovement"):
            pass
        elif param.movement_model == "MapRouteMovement":
            pass
        else:
            return False, "pedestrian_transit needs bus or vehicle route"

    return True, ""


def _split_hosts(n: int, n_groups: int) -> list[int]:
    base = n // n_groups
    rem = n % n_groups
    return [base + (1 if i < rem else 0) for i in range(n_groups)]


def _wdm_group_block(map_id: str, route_rel: str, *, prefix: str = "Group") -> str:
    p = prefix
    mp = _map_rel_prefix(map_id)
    return f"""
{p}.movementModel = WorkingDayMovement
{p}.routeFile = {route_rel}
{p}.homeLocationsFile = {mp}/A_homes.wkt
{p}.officeLocationsFile = {mp}/A_offices.wkt
{p}.meetingSpotsFile = {mp}/A_meetingspots.wkt
{p}.speed = 0.5, 1.5
{p}.waitTime = 0, 120
{p}.busControlSystemNr = -1
{p}.timeDiffSTD = 1200
{p}.workDayLength = 28800
{p}.nrOfOffices = 10
{p}.officeSize = 50
{p}.officeWaitTimeParetoCoeff = 1.4
{p}.officeMinWaitTime = 300
{p}.officeMaxWaitTime = 900
{p}.nrOfMeetingSpots = 10
{p}.minGroupSize = 1
{p}.maxGroupSize = 5
{p}.minWaitTime = 300
{p}.maxWaitTime = 1800
{p}.eveningActivityControlSystemNr = -1
{p}.shoppingControlSystemNr = -1
{p}.nrOfShops = 15
{p}.shopSize = 25
{p}.shoppingWaitTimeParetoCoeff = 1.4
{p}.shoppingMinWaitTime = 60
{p}.shoppingMaxWaitTime = 600
{p}.minAfterShoppingStopTime = 60
{p}.maxAfterShoppingStopTime = 600
{p}.probGoShoppingAfterWork = 0.3
{p}.ownCarProb = 0.0
"""


def _spmbm_block(*, prefix: str = "Group", speed: str = "0.5, 2.0", wait: str = "0, 600") -> str:
    return f"""
{prefix}.movementModel = ShortestPathMapBasedMovement
{prefix}.speed = {speed}
{prefix}.waitTime = {wait}
"""


def _bus_block(route_rel: str, *, prefix: str = "Group") -> str:
    return f"""
{prefix}.movementModel = BusMovement
{prefix}.routeFile = {route_rel}
{prefix}.routeType = 1
{prefix}.busControlSystemNr = -1
{prefix}.speed = 7, 10
{prefix}.waitTime = 10, 30
"""


def _map_route_block(route_rel: str, *, prefix: str = "Group") -> str:
    return f"""
{prefix}.movementModel = MapRouteMovement
{prefix}.routeFile = {route_rel}
{prefix}.routeType = 1
{prefix}.speed = 5, 14
{prefix}.waitTime = 5, 60
"""


def _cluster_block(world_x: int, world_y: int, *, prefix: str = "Group") -> str:
    cx, cy = world_x // 2, world_y // 2
    cr = max(50, min(world_x, world_y) // 4)
    return f"""
{prefix}.movementModel = ClusterMovement
{prefix}.clusterCenter = {cx}, {cy}
{prefix}.clusterRange = {cr}
{prefix}.speed = 0.5, 1.5
{prefix}.waitTime = 30, 240
"""


def _group_tail(gi: int, param: ScenarioParam) -> str:
    return f"""
Group{gi}.bufferSize = {param.buffer_size}
Group{gi}.router = {param.router}
Group{gi}.nrofInterfaces = 1
Group{gi}.interface1 = bt0
"""


def _random_waypoint_block(*, prefix: str = "Group", speed: str = "0.5, 1.5", wait: str = "30, 240") -> str:
    return f"""
{prefix}.movementModel = RandomWaypoint
{prefix}.speed = {speed}
{prefix}.waitTime = {wait}
"""


def _speed_wait(param: ScenarioParam, vehicle: bool = False) -> tuple[str, str]:
    speed = SPEED_REGIME_RANGES.get(
        param.speed_regime,
        SPEED_REGIME_RANGES["vehicle_normal" if vehicle else "pedestrian_normal"],
    )
    wait = WAIT_REGIME_RANGES.get(param.wait_regime, WAIT_REGIME_RANGES["normal_pause"])
    return speed, wait


def build_host_groups(param: ScenarioParam, maps_index: dict) -> tuple[str, int]:
    """Return (group block text, total_hosts for Events1.hosts)."""
    struct = param.effective_group_structure
    n = param.n_hosts
    model = param.movement_model
    map_id = param.map_id
    wx = maps_index[map_id]["world_size_x"]
    wy = maps_index[map_id]["world_size_y"]
    route_bus = resolve_route_rel(map_id, "BusMovement")
    route_vehicle = resolve_route_rel(map_id, "MapRouteMovement") or route_bus

    lines: list[str] = []

    # WDM on Helsinki: U1-style bus-first layout (reference F.2 / R013)
    if model == "RandomWaypoint":
        speed, wait = _speed_wait(param)
        lines.append(f"Scenario.nrofHostGroups = 1")
        lines.append(_random_waypoint_block(prefix="Group1", speed=speed, wait=wait).strip())
        lines.append("Group1.groupID = a")
        lines.append(f"Group1.nrofHosts = {n}")
        lines.append(_group_tail(1, param).strip())
        return "\n".join(lines) + "\n", n

    if model == "WorkingDayMovement":
        route_wdm = resolve_route_rel(map_id, "WorkingDayMovement")
        assert route_wdm
        n_ped = max(1, n - 1)
        lines.append("Scenario.nrofHostGroups = 2")
        lines.append("Group.busControlSystemNr = -1")
        lines.append(_bus_block(route_wdm, prefix="Group1").strip())
        lines.append("Group1.groupID = b")
        lines.append("Group1.nrofHosts = 1")
        lines.append(_group_tail(1, param).strip())
        lines.append(_wdm_group_block(map_id, route_wdm, prefix="Group2").strip())
        lines.append("Group2.groupID = p")
        lines.append(f"Group2.nrofHosts = {n_ped}")
        lines.append(_group_tail(2, param).strip())
        return "\n".join(lines) + "\n", 1 + n_ped

    n_groups = GROUP_STRUCTURE_NGROUPS.get(struct, 1)
    hosts = _split_hosts(n, n_groups)
    lines.append(f"Scenario.nrofHostGroups = {n_groups}")

    if struct == "single_homogeneous":
        gi = 1
        lines.append(f"Group{gi}.groupID = a")
        lines.append(f"Group{gi}.nrofHosts = {hosts[0]}")
        speed, wait = _speed_wait(param)
        lines.append(
            _movement_defaults(model, map_id, wx, wy, speed=speed, wait=wait).replace("Group.", f"Group{gi}.")
        )
        lines.append(_group_tail(gi, param).strip())

    elif struct == "pedestrian_transit" and route_bus:
        lines.append(_bus_block(route_bus, prefix="Group1").strip())
        lines.append("Group1.groupID = b")
        lines.append("Group1.nrofHosts = 1")
        lines.append(_group_tail(1, param).strip())
        lines.append(_spmbm_block(prefix="Group2", speed="0.5, 1.5", wait="0, 120").strip())
        lines.append("Group2.groupID = p")
        lines.append(f"Group2.nrofHosts = {max(1, n - 1)}")
        lines.append(_group_tail(2, param).strip())

    elif struct == "pedestrian_vehicle" and route_vehicle:
        n_v = max(1, n // 5)
        n_p = max(1, n - n_v)
        veh_model = "MapRouteMovement" if model == "MapRouteMovement" else "BusMovement"
        veh_route = resolve_route_rel(map_id, veh_model) or route_vehicle
        if veh_model == "BusMovement":
            lines.append(_bus_block(veh_route, prefix="Group1").strip())
        else:
            lines.append(_map_route_block(veh_route, prefix="Group1").strip())
        lines.append("Group1.groupID = v")
        lines.append(f"Group1.nrofHosts = {n_v}")
        lines.append(_group_tail(1, param).strip())
        lines.append(_spmbm_block(prefix="Group2").strip())
        lines.append("Group2.groupID = p")
        lines.append(f"Group2.nrofHosts = {n_p}")
        lines.append(_group_tail(2, param).strip())

    elif struct == "pedestrian_shortestpath_heterogeneous":
        lines.append(_spmbm_block(prefix="Group1", speed="0.5, 1.0", wait="0, 120").strip())
        lines.append("Group1.groupID = a")
        lines.append(f"Group1.nrofHosts = {hosts[0]}")
        lines.append(_group_tail(1, param).strip())
        lines.append(_spmbm_block(prefix="Group2", speed="1.0, 2.0", wait="30, 300").strip())
        lines.append("Group2.groupID = b")
        lines.append(f"Group2.nrofHosts = {hosts[1]}")
        lines.append(_group_tail(2, param).strip())

    elif struct == "cluster_nomadic":
        lines.append(_cluster_block(wx, wy, prefix="Group1").strip())
        lines.append("Group1.groupID = c")
        lines.append(f"Group1.nrofHosts = {hosts[0]}")
        lines.append(_group_tail(1, param).strip())
        lines.append(_spmbm_block(prefix="Group2", speed="0.8, 1.8", wait="0, 300").strip())
        lines.append("Group2.groupID = n")
        lines.append(f"Group2.nrofHosts = {hosts[1]}")
        lines.append(_group_tail(2, param).strip())

    else:
        # Fallback: single group with declared movement model
        lines.append(f"Group1.groupID = a")
        lines.append(f"Group1.nrofHosts = {n}")
        lines.append(_movement_defaults(model, map_id, wx, wy).replace("Group.", "Group1."))
        lines.append(_group_tail(1, param).strip())
        lines.append("Scenario.nrofHostGroups = 1")

    total = sum(
        int(line.split("=")[1].strip())
        for line in lines
        if ".nrofHosts" in line
    )
    return "\n".join(lines) + "\n", total


def _movement_defaults(
    model: str,
    map_id: str,
    wx: int,
    wy: int,
    *,
    speed: str | None = None,
    wait: str | None = None,
) -> str:
    speed = speed or "0.5, 2.0"
    wait = wait or "0, 600"
    route = resolve_route_rel(map_id, model)
    if model == "ShortestPathMapBasedMovement":
        return _spmbm_block(speed=speed, wait=wait)
    if model == "RandomWaypoint":
        return _random_waypoint_block(speed=speed, wait=wait)
    if model == "MapRouteMovement" and route:
        return _map_route_block(route)
    if model == "BusMovement" and route:
        return _bus_block(route)
    if model == "ClusterMovement":
        return _cluster_block(wx, wy)
    return _spmbm_block(speed=speed, wait=wait)


def build_settings_content(param: ScenarioParam, maps_index: dict[str, dict]) -> str:
    """Full .settings text for one candidate."""
    m = maps_index[param.map_id]
    wx, wy = m["world_size_x"], m["world_size_y"]
    map_file = m["wkt_path"]
    ctx = get_builder_context()
    pe = ctx.placeholder_events

    group_block, total_hosts = build_host_groups(param, maps_index)

    map_section = ""
    if param.movement_model != "RandomWaypoint":
        map_section = f"""
MapBasedMovement.nrofMapFiles = 1
MapBasedMovement.mapFile1 = {map_file}
"""

    header = f"""# {ctx.header_tag} structural candidate
# Reference: the_one_settings_reference_node_mobility_messages.md (placeholder traffic)
# candidate_id: {param.candidate_id} | param_id: {param.param_id}
# map: {param.map_id} | movement: {param.movement_model} | hosts: {param.n_hosts}
# group_structure: {param.group_structure}

Scenario.name = {param.scenario_name}
Scenario.simulateConnections = true
Scenario.updateInterval = 0.1
Scenario.endTime = {param.end_time}

MovementModel.rngSeed = {param.rng_seed}
MovementModel.worldSize = {wx}, {wy}
{map_section}
Group.bufferSize = {param.buffer_size}
Group.router = {param.router}
Group.nrofInterfaces = 1
Group.interface1 = bt0
bt0.type = SimpleBroadcastInterface
bt0.transmitSpeed = 2.4M
bt0.transmitRange = {param.transmit_range}
Group.msgTtl = {PLACEHOLDER_MSG_TTL}
"""

    default_mm = ""
    if param.movement_model not in ("WorkingDayMovement", "RandomWaypoint"):
        sp, wt = _speed_wait(param)
        default_mm = _movement_defaults(param.movement_model, param.map_id, wx, wy, speed=sp, wait=wt)

    traffic = f"""
# Placeholder traffic (NOT a Traffic Profile — Part C.5)
Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = {pe['interval']}
Events1.size = {pe['size']}
Events1.hosts = 0, {total_hosts}
Events1.prefix = {pe['prefix']}

Report.nrofReports = 2
Report.reportDir = reports/
Report.report1 = MessageStatsReport
Report.report2 = ContactTimesReport
"""

    parts = [header]
    if default_mm.strip():
        parts.append(default_mm)
    parts.append(group_block)
    parts.append(traffic)
    return "".join(parts)


def write_settings_file(param: ScenarioParam, content: str, settings_root: Path) -> Path:
    """Write .settings flat under settings/ (map is inside the file, not the folder)."""
    settings_root.mkdir(parents=True, exist_ok=True)
    path = settings_root / f"{param.scenario_name}.settings"
    path.write_text(content, encoding="utf-8")
    return path
