#!/usr/bin/env python3
"""Audit routeFile and POI usage across active scenario trees."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import ACTIVE_MAPS, ANALYSIS_DATA, REPO_ROOT, SCENARIOS_DIR  # noqa: E402

REPORTS_DIR = SCENARIOS_DIR / "analysis" / "reports" / "maps"
GROUP_RE = re.compile(r"^Group(\d+)\.(.+)$")
POI_KEYS = ("homeLocationsFile", "officeLocationsFile", "meetingSpotsFile")
TREES = (
    ("base_scenarios", SCENARIOS_DIR / "base_scenarios"),
    ("corpus_v1", SCENARIOS_DIR / "corpus_v1"),
)

def load_settings_flat(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out

def infer_family(path: Path) -> str:
    for part in path.parts:
        if re.match(r"0[1-6]_.*", part):
            return part
    return ""

def infer_map_name(kv: dict[str, str]) -> str:
    raw = kv.get("MapBasedMovement.mapFile1", "")
    for name in ACTIVE_MAPS:
        if name in raw:
            return name
    return ""

def load_validation_status() -> dict[tuple[str, str], str]:
    p = ANALYSIS_DATA / "bus_route_validation.csv"
    out: dict[tuple[str, str], str] = {}
    if not p.is_file():
        return out
    with p.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row.get("map_name", ""), row.get("route_file", ""))
            out[key] = row.get("status", "")
    return out

def collect_rows() -> list[dict]:
    val = load_validation_status()
    rows: list[dict] = []
    for tree_name, root in TREES:
        if not root.is_dir():
            continue
        for sp in sorted(root.rglob("*.settings")):
            kv = load_settings_flat(sp)
            scen = kv.get("Scenario.name", sp.stem)
            family = infer_family(sp)
            map_name = infer_map_name(kv)
            per_group: dict[int, dict[str, str]] = defaultdict(dict)
            for key, value in kv.items():
                m = GROUP_RE.match(key)
                if m:
                    per_group[int(m.group(1))][m.group(2)] = value
            if not per_group and kv.get("Group.movementModel"):
                per_group[0]["movementModel"] = kv["Group.movementModel"]
                for pk in ("routeFile",) + POI_KEYS:
                    if kv.get(f"Group.{pk}"):
                        per_group[0][pk] = kv[f"Group.{pk}"]
            for gi, g in sorted(per_group.items()):
                mm = g.get("movementModel", kv.get("Group.movementModel", ""))
                rf = g.get("routeFile", kv.get("Group.routeFile", ""))
                if rf or mm in ("BusMovement", "MapRouteMovement", "WorkingDayMovement"):
                    exists = (REPO_ROOT / rf).is_file() if rf else ""
                    rf_name = Path(rf).name if rf else ""
                    vstat = val.get((map_name, rf_name), "") if rf else ""
                    notes = []
                    if rf and not exists:
                        notes.append("missing route file")
                    poi_used = any(g.get(k) or kv.get(f"Group.{k}") for k in POI_KEYS)
                    if mm == "WorkingDayMovement" and not poi_used:
                        notes.append("WDM without explicit POI keys in group")
                    rows.append(
                        {
                            "scenario_name": scen,
                            "tree": tree_name,
                            "family": family,
                            "map_name": map_name,
                            "group_id": gi,
                            "movement_model": mm,
                            "route_file": rf,
                            "route_file_exists": bool(exists) if rf else "",
                            "route_validation_status": vstat,
                            "uses_poi_files": poi_used,
                            "settings_path": str(sp.relative_to(REPO_ROOT)),
                            "notes": "; ".join(notes),
                        }
                    )
    return rows

def write_report(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    bus = [r for r in rows if r["movement_model"] in ("BusMovement", "MapRouteMovement") and r.get("route_file")]
    wdm = [r for r in rows if r["movement_model"] == "WorkingDayMovement"]
    spmm = [r for r in rows if r["movement_model"] == "ShortestPathMapBasedMovement"]
    cluster = [r for r in rows if r["movement_model"] == "ClusterMovement"]
    roads_only = len(
        {
            r["scenario_name"]
            for r in rows
            if r["movement_model"] == "ShortestPathMapBasedMovement" and not r.get("route_file")
        }
    )
    lines = [
        "# Route usage by scenario",
        "",
        f"Generated: {ts}",
        "",
        "## Summary",
        "",
        f"- Rows with routeFile: **{len(bus)}**",
        f"- WorkingDayMovement rows: **{len(wdm)}**",
        f"- ShortestPathMapBasedMovement rows: **{len(spmm)}**",
        f"- ClusterMovement rows: **{len(cluster)}**",
        f"- Scenarios relying mainly on roads.wkt (SPMM, no route): **{roads_only}** distinct scenario names (approx.)",
        "",
        "## Bus / MapRoute carriers",
        "",
        "Scenarios using `BusMovement` or `MapRouteMovement` reference `GroupN.routeFile` (`*_bus.wkt`). "
        "Movement between stops uses the road graph (Dijkstra), not the straight chord in preview figures.",
        "",
        "## ClusterMovement",
        "",
        "Cluster scenarios use `roads.wkt` for map bounds and optional cluster areas; "
        "community structure is parameter-driven, not from bus routes.",
        "",
        "## Missing files",
        "",
    ]
    missing = [r for r in bus if r.get("notes") == "missing route file"]
    if missing:
        for r in missing[:20]:
            lines.append(f"- `{r['scenario_name']}` → `{r['route_file']}`")
    else:
        lines.append("- None detected.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-csv", type=str, default=str(ANALYSIS_DATA / "route_usage_by_scenario.csv"))
    ap.add_argument("--output-report", type=str, default=str(REPORTS_DIR / "route_usage_by_scenario_report.md"))
    args = ap.parse_args()

    rows = collect_rows()
    out = Path(args.output_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    write_report(rows, Path(args.output_report))
    print(f"Wrote {out} ({len(rows)} rows)")
    print(f"Wrote {args.output_report}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())