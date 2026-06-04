#!/usr/bin/env python3
"""Validate geometry for map-aware repaired scenarios (S1, S6, D1, R2)."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
_SCENARIOS = _SETUP.parent
_REPO = _SCENARIOS.parent
_ANALYSIS = _SCENARIOS / "analysis"
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import (  # noqa: E402
    RoadGraph,
    parse_linestrings,
    points_inside_world_size,
    threshold_for_family,
    vertex_distances,
    wkt_to_sim_coords,
)

REPAIRED_BASES = [
    "S1_StrongCommunities_LimitedMixing",
    "S6_FamilyGroups_LocalRoutines",
    "D1_ShelterHotspots_EmergencyMobility",
    "R2_VillagesTrails_InterVillage",
]

FAMILY_MAP = {
    "S1": ("06_social", "KallioCommunityCompact"),
    "S6": ("06_social", "KallioCommunityCompact"),
    "D1": ("05_disaster", "HelsinkiDisrupted"),
    "R2": ("04_rural", "NuuksioSparseTrails"),
}

def load_kv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out

def parse_world_size(ws: str) -> tuple[float, float]:
    parts = [p.strip() for p in ws.split(",")]
    return float(parts[0]), float(parts[1])

def route_stops_sim(route_path: Path, roads_path: Path) -> list[tuple[float, float]]:
    raw = parse_linestrings(route_path)
    if not raw or not raw[0]:
        return []
    roads_lines = parse_linestrings(roads_path)
    from map_geometry import SimTransform

    tf = SimTransform.from_raw_lines(roads_lines)
    return [tf.raw_to_sim(x, y) for x, y in raw[0]]

def validate_settings(path: Path) -> dict:
    kv = load_kv(path)
    scen = kv.get("Scenario.name", path.stem)
    prefix = scen.split("_")[0]
    family, map_name = FAMILY_MAP.get(prefix[:2], ("", ""))
    if prefix.startswith("S"):
        family, map_name = FAMILY_MAP["S1"]
    issues: list[str] = []
    cluster = sum(1 for k, v in kv.items() if k.endswith(".movementModel") and v == "ClusterMovement")
    if cluster:
        issues.append(f"ClusterMovement groups={cluster}")
    wx, wy = parse_world_size(kv.get("MovementModel.worldSize", "0,0"))
    roads = _REPO / kv.get("MapBasedMovement.mapFile1", "")
    rg = RoadGraph.from_roads_wkt(roads) if roads.is_file() else None
    route_keys = [k for k in kv if re.match(r"^Group\d*\.routeFile$", k)]
    for rk in route_keys:
        rf = _REPO / kv[rk]
        if not rf.is_file():
            issues.append(f"missing {rk}")
            continue
        stops = route_stops_sim(rf, roads)
        if not points_inside_world_size(stops, wx, wy):
            issues.append(f"{rk} outside worldSize")
        if rg and stops:
            dists = vertex_distances(rg, stops)
            thresh = threshold_for_family(family)
            over = sum(1 for d in dists if d > thresh)
            if over > max(1, len(dists) // 5):
                issues.append(f"{rk}: {over}/{len(dists)} stops >{thresh}m from graph")
    status = "PASS" if not issues else "FAIL"
    return {
        "scenario_name": scen,
        "settings_path": str(path.relative_to(_REPO)),
        "map_name": map_name,
        "world_size": kv.get("MovementModel.worldSize", ""),
        "cluster_groups": cluster,
        "route_files": len(route_keys),
        "issues": "; ".join(issues),
        "status": status,
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", choices=("base", "corpus", "both"), default="base")
    args = ap.parse_args()
    paths: list[Path] = []
    for base in REPAIRED_BASES:
        fam = "06_social" if base.startswith("S") else "05_disaster" if base.startswith("D") else "04_rural"
        bp = _SCENARIOS / "base_scenarios" / fam / f"{base}.settings"
        if bp.is_file() and args.tree in ("base", "both"):
            paths.append(bp)
        if args.tree in ("corpus", "both"):
            paths.extend(sorted((_SCENARIOS / "corpus_v1" / fam).glob(f"{base}__*.settings")))
    rows = [validate_settings(p) for p in paths[:4] if "base" in str(p) or args.tree == "corpus"]
    if args.tree == "both":
        rows = [validate_settings(_SCENARIOS / "base_scenarios" / (
            "06_social" if b.startswith("S") else "05_disaster" if b.startswith("D") else "04_rural"
        ) / f"{b}.settings") for b in REPAIRED_BASES]
    out_csv = _ANALYSIS / "data" / "problematic_scenarios_geometry_validation.csv"
    out_md = _ANALYSIS / "reports" / "problematic_scenarios_geometry_validation.md"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    lines = [
        "# Geometry validation — repaired mobility scenarios",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "| Scenario | Status | Issues |",
        "|----------|--------|--------|",
    ]
    for r in rows:
        lines.append(f"| {r['scenario_name']} | {r['status']} | {r['issues'] or '—'} |")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_csv} and {out_md}")
    return 0 if all(r["status"] == "PASS" for r in rows) else 1

if __name__ == "__main__":
    raise SystemExit(main())