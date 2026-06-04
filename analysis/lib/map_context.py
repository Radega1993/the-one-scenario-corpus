"""
Resolve map dataset (HelsinkiMedium / Manhattan) and sim-aligned geometry from .settings.

Road WKT is transformed like MapBasedMovement.readMap(): mirror Y, then translate
so min bound is at origin — same coordinate system as host.getLocation() / occupancy grid.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from lib.paths import REPO_ROOT

LINESTRING_RE = re.compile(
    r"LINESTRING\s*\(([^)]+)\)",
    re.IGNORECASE,
)

# Parsed sim-aligned road geometry per roads.wkt path (large files; reuse across scenarios).
_ROADS_SIM_CACHE: dict[str, list[list[tuple[float, float]]]] = {}

@dataclass
class UnderlaySpec:
    path: Path
    offset_x: float
    offset_y: float
    scale: float
    rotate: float

@dataclass
class MapContext:
    dataset: str | None
    roads_path: Path | None
    roads_sim: list[list[tuple[float, float]]] | None
    underlay: UnderlaySpec | None
    world_x: float | None
    world_y: float | None

def load_settings_flat(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out

def _parse_csv_floats(value: str) -> list[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]

def infer_map_dataset(kv: dict[str, str]) -> str | None:
    """Return 'HelsinkiMedium', 'Manhattan', or None."""
    needles = (
        ("HelsinkiMedium", "HelsinkiMedium"),
        ("HelsinkiDowntown", "HelsinkiMedium"),
        ("Manhattan", "Manhattan"),
    )
    path_keys = (
        "MapBasedMovement.mapFile1",
        "Group.homeLocationsFile",
        "Group.officeLocationsFile",
        "Group.routeFile",
    )
    for key in path_keys:
        val = kv.get(key, "")
        for needle, name in needles:
            if needle in val:
                return name
    for raw_line in kv.values():
        if "HelsinkiMedium" in raw_line:
            return "HelsinkiMedium"
        if "Manhattan" in raw_line:
            return "Manhattan"
    scen = kv.get("Scenario.name", "")
    if "HelsinkiMedium" in scen:
        return "HelsinkiMedium"
    if "Manhattan" in scen:
        return "Manhattan"
    return None

def roads_wkt_path(dataset: str | None, repo_root: Path = REPO_ROOT) -> Path | None:
    if dataset == "HelsinkiMedium":
        return repo_root / "data" / "HelsinkiMedium" / "roads.wkt"
    if dataset == "Manhattan":
        return repo_root / "data" / "Manhattan" / "roads.wkt"
    return None

def roads_wkt_from_settings(kv: dict[str, str], repo_root: Path = REPO_ROOT) -> Path | None:
    """Prefer explicit MapBasedMovement.mapFile1 when available."""
    raw = kv.get("MapBasedMovement.mapFile1")
    if not raw:
        return None
    p = Path(raw)
    if not p.is_absolute():
        p = repo_root / p
    return p if p.is_file() else None

def underlay_from_settings(kv: dict[str, str], repo_root: Path = REPO_ROOT) -> UnderlaySpec | None:
    fn = kv.get("GUI.UnderlayImage.fileName")
    if fn:
        p = Path(fn)
        if not p.is_absolute():
            p = repo_root / p
        if not p.is_file():
            return None
    else:
        # Fallback for corpora that do not declare GUI.UnderlayImage.* in scenario settings.
        dataset = infer_map_dataset(kv)
        if dataset == "HelsinkiMedium":
            p = repo_root / "data" / "helsinki_underlay.png"
            if not p.is_file():
                return None
        else:
            return None
    off = _parse_csv_floats(kv.get("GUI.UnderlayImage.offset", "0, 0"))
    ox = off[0] if len(off) > 0 else 0.0
    oy = off[1] if len(off) > 1 else 0.0
    try:
        scale = float(kv.get("GUI.UnderlayImage.scale", "1"))
    except ValueError:
        scale = 1.0
    try:
        rotate = float(kv.get("GUI.UnderlayImage.rotate", "0"))
    except ValueError:
        rotate = 0.0
    return UnderlaySpec(path=p, offset_x=ox, offset_y=oy, scale=scale, rotate=rotate)

def parse_wkt_lines(path: Path) -> list[list[tuple[float, float]]]:
    """Parse LINESTRING entries from a WKT file (raw coordinates)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines: list[list[tuple[float, float]]] = []
    for m in LINESTRING_RE.finditer(text):
        pts: list[tuple[float, float]] = []
        for pair in m.group(1).split(","):
            pair = pair.strip()
            if not pair:
                continue
            parts = pair.split()
            if len(parts) < 2:
                continue
            try:
                pts.append((float(parts[0]), float(parts[1])))
            except ValueError:
                continue
        if len(pts) >= 2:
            lines.append(pts)
    return lines

def wkt_to_sim_coords(raw_lines: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    """
    Apply MapBasedMovement post-processing: mirror Y, translate to origin (min bound).
    """
    if not raw_lines:
        return []
    mirrored: list[list[tuple[float, float]]] = []
    all_x: list[float] = []
    all_y: list[float] = []
    for line in raw_lines:
        ml = [(x, -y) for x, y in line]
        mirrored.append(ml)
        for x, y in ml:
            all_x.append(x)
            all_y.append(y)
    if not all_x:
        return []
    min_x, min_y = min(all_x), min(all_y)
    return [[(x - min_x, y - min_y) for x, y in line] for line in mirrored]

def world_size_from_settings(kv: dict[str, str]) -> tuple[float, float] | None:
    raw = kv.get("MovementModel.worldSize")
    if not raw:
        return None
    try:
        parts = _parse_csv_floats(raw)
        if len(parts) >= 2:
            return parts[0], parts[1]
    except ValueError:
        pass
    return None

def build_map_context(
    settings_path: Path | None,
    *,
    repo_root: Path = REPO_ROOT,
    world_x: float | None = None,
    world_y: float | None = None,
    load_roads: bool = True,
) -> MapContext:
    kv: dict[str, str] = {}
    if settings_path and settings_path.is_file():
        kv = load_settings_flat(settings_path)
    dataset = infer_map_dataset(kv)
    wx, wy = world_size_from_settings(kv) if kv else None
    if world_x is not None and world_y is not None:
        wx, wy = world_x, world_y
    roads_path = roads_wkt_from_settings(kv, repo_root) if kv else None
    if roads_path is None:
        roads_path = roads_wkt_path(dataset, repo_root)
    roads_sim = None
    if load_roads and roads_path and roads_path.is_file():
        key = str(roads_path.resolve())
        if key not in _ROADS_SIM_CACHE:
            _ROADS_SIM_CACHE[key] = wkt_to_sim_coords(parse_wkt_lines(roads_path))
        roads_sim = _ROADS_SIM_CACHE[key]
    underlay = underlay_from_settings(kv, repo_root) if kv else None
    return MapContext(
        dataset=dataset,
        roads_path=roads_path,
        roads_sim=roads_sim,
        underlay=underlay,
        world_x=wx,
        world_y=wy,
    )