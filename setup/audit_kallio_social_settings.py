#!/usr/bin/env python3
"""Audit 06_social .settings for KallioCommunityCompact."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import SCENARIOS_DIR  # noqa: E402

MAP_DATA = SCENARIOS_DIR / "analysis" / "data" / "maps"
REPORTS = SCENARIOS_DIR / "analysis" / "reports" / "maps"
BASE_SOCIAL = SCENARIOS_DIR / "base_scenarios" / "06_social"
CORPUS_SOCIAL = SCENARIOS_DIR / "corpus_v1" / "06_social"

EXPECTED_WS = "1458, 1529"
EXPECTED_MAP = "data/KallioCommunityCompact/roads.wkt"
WRONG_MAPS = (
    "HelsinkiMedium",
    "HelsinkiDowntown",
    "ManhattanMidtownGrid",
    "NuuksioSparseTrails",
    "KumpulaCampus",
    "HelsinkiDisrupted",
)

ROUTE_FILE_RE = re.compile(r"^Group\d*\.routeFile$")


def load_kv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def audit_file(path: Path) -> dict:
    kv = load_kv(path)
    issues: list[str] = []
    tree = "corpus_v1" if "corpus_v1" in path.parts else "base_scenarios"
    text = path.read_text(encoding="utf-8", errors="replace")

    scen = kv.get("Scenario.name", path.stem)
    map1 = kv.get("MapBasedMovement.mapFile1", "")
    ws = kv.get("MovementModel.worldSize", "")

    for bad in WRONG_MAPS:
        if f"data/{bad}/" in text or bad in map1:
            issues.append(f"wrong map ref: {bad}")

    if map1 and map1 != EXPECTED_MAP:
        issues.append(f"mapFile1={map1}")
    if ws.replace(" ", "") != EXPECTED_WS.replace(" ", ""):
        issues.append(f"worldSize={ws}")

    route_refs = {k: v for k, v in kv.items() if ROUTE_FILE_RE.match(k) and v}
    if route_refs:
        issues.append(f"unexpected routeFile: {route_refs}")

    legacy_bus = sum(1 for v in route_refs.values() if "A_bus.wkt" in v or "B_bus.wkt" in v)
    if legacy_bus:
        issues.append("legacy bus routeFile")

    n_groups = int(kv.get("Scenario.nrofHostGroups", "1") or "1")
    cluster_groups = sum(
        1 for k, v in kv.items() if k.endswith(".movementModel") and v == "ClusterMovement"
    )
    spmm_groups = sum(
        1 for k, v in kv.items() if k.endswith(".movementModel") and v == "ShortestPathMapBasedMovement"
    )
    map_constrained = cluster_groups == 0 and spmm_groups > 0

    status = "PASS" if not issues else "FAIL"
    return {
        "settings_path": str(path.relative_to(SCENARIOS_DIR.parent)),
        "tree": tree,
        "scenario_name": scen,
        "map_file1": map1,
        "world_size": ws,
        "n_host_groups": n_groups,
        "cluster_groups": cluster_groups,
        "spmm_groups": spmm_groups,
        "map_constrained": map_constrained,
        "route_files_in_settings": "; ".join(f"{k}={v}" for k, v in sorted(route_refs.items())),
        "issues": "; ".join(issues),
        "status": status,
    }


def write_report(rows: list[dict]) -> None:
    fails = [r for r in rows if r["status"] == "FAIL"]
    path = REPORTS / "KallioCommunityCompact_social_settings_report.md"
    lines = [
        "# KallioCommunityCompact — social settings audit",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"- Files audited: {len(rows)}",
        f"- FAIL: {len(fails)}",
        "",
        "## Movement models",
        "",
        "| Scenario type | Model | Map constrains path? |",
        "|---------------|-------|----------------------|",
        "| S1, S6 | ClusterMovement | No — cluster centers/ranges only |",
        "| S2–S5 | ShortestPathMapBasedMovement | Yes — follows `roads.wkt` |",
        "",
        "## Community routes (optional)",
        "",
        "`A_community_route.wkt` and `B_community_route.wkt` are **figure assets only** — "
        "no `routeFile` in any social `.settings` (unlike D5 UAV in disaster).",
        "",
    ]
    if fails:
        lines.extend(["## Failures", ""])
        for r in fails[:20]:
            lines.append(f"- `{r['settings_path']}`: {r['issues']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()

    rows: list[dict] = []
    for root in (BASE_SOCIAL, CORPUS_SOCIAL):
        if root.is_dir():
            for sp in sorted(root.glob("*.settings")):
                rows.append(audit_file(sp))

    MAP_DATA.mkdir(parents=True, exist_ok=True)
    out_csv = MAP_DATA / "KallioCommunityCompact_social_settings_audit.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    write_report(rows)
    print(f"Wrote {out_csv} ({len(rows)} files)")
    return 1 if any(r["status"] == "FAIL" for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
