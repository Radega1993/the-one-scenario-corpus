#!/usr/bin/env python3
"""Audit 02_campus .settings for KumpulaCampus; C4 rename and C6 cleanup."""

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
BASE_CAMPUS = SCENARIOS_DIR / "base_scenarios" / "02_campus"
CORPUS_CAMPUS = SCENARIOS_DIR / "corpus_v1" / "02_campus"

EXPECTED_WS = "1524, 1416"
EXPECTED_MAP = "data/KumpulaCampus/roads.wkt"
C4_OLD = "C4_Stadium_IngressEgress"
C4_NEW = "C4_CampusEvent_IngressEgress"
LINEAR_KEYS = (
    "Group.LinearMovement.startLocation",
    "Group.LinearMovement.endLocation",
    "Group.LinearMovement.initLocType",
    "Group.LinearMovement.targetType",
    "Group1.LinearMovement.startLocation",
    "Group1.LinearMovement.endLocation",
    "Group1.LinearMovement.initLocType",
    "Group1.LinearMovement.targetType",
)


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
    mm = kv.get("Group.movementModel", kv.get("Group1.movementModel", ""))

    for bad in ("HelsinkiMedium", "HelsinkiDowntown", "Manhattan"):
        if bad in map1 or any(bad in v for k, v in kv.items() if "File" in k):
            issues.append(f"wrong map ref: {bad}")

    if map1 and map1 != EXPECTED_MAP:
        issues.append(f"mapFile1={map1}")
    if ws.replace(" ", "") != EXPECTED_WS.replace(" ", ""):
        issues.append(f"worldSize={ws}")
    if any(k in kv for k in LINEAR_KEYS) and "ShortestPathMapBasedMovement" in mm:
        issues.append("residual LinearMovement keys with SPMM")

    route_files = [v for k, v in kv.items() if "routeFile" in k and v]
    if route_files:
        issues.append("unexpected routeFile in campus scenario")

    status = "PASS" if not issues else "FAIL"
    return {
        "settings_path": str(path.relative_to(SCENARIOS_DIR.parent)),
        "tree": tree,
        "scenario_name": scen,
        "map_file1": map1,
        "world_size": ws,
        "movement_model": mm,
        "end_time": kv.get("Scenario.endTime", ""),
        "has_residual_linear": any(k in kv for k in LINEAR_KEYS),
        "route_file_in_settings": bool(route_files),
        "issues": "; ".join(issues),
        "status": status,
    }


def rename_c4(apply: bool) -> list[str]:
    changed: list[str] = []
    patterns: list[tuple[Path, Path]] = [
        (BASE_CAMPUS / f"{C4_OLD}.settings", BASE_CAMPUS / f"{C4_NEW}.settings"),
    ]
    for tp in sorted(CORPUS_CAMPUS.glob(f"{C4_OLD}__TP*.settings")):
        patterns.append((tp, CORPUS_CAMPUS / tp.name.replace(C4_OLD, C4_NEW)))

    for old, new in patterns:
        if not old.is_file():
            continue
        text = old.read_text(encoding="utf-8")
        text = text.replace(f"Scenario.name = {C4_OLD}", f"Scenario.name = {C4_NEW}")
        text = text.replace(C4_OLD, C4_NEW)
        text = text.replace("Stadium ingress/egress", "Campus event ingress/egress")
        text = text.replace("# C4 - Stadium", "# C4 - Campus event ingress/egress")
        if apply:
            if new.exists():
                new.unlink()
            old.rename(new)
            new.write_text(text, encoding="utf-8")
        changed.append(str(new.relative_to(SCENARIOS_DIR.parent)))
    return changed


def cleanup_c6_linear(apply: bool) -> list[str]:
    changed: list[str] = []
    paths = [BASE_CAMPUS / "C6_EmergencyDrill_Evacuation.settings"]
    paths.extend(sorted(CORPUS_CAMPUS.glob("C6_EmergencyDrill_Evacuation__TP*.settings")))

    linear_prefixes = ("Group.LinearMovement.", "Group1.LinearMovement.")
    header_comment = (
        "# Evacuation: ShortestPathMapBasedMovement on campus graph "
        "(speed 2–4 m/s, waitTime 0–10 s). Legacy LinearMovement keys removed.\n"
    )

    for p in paths:
        if not p.is_file():
            continue
        lines_out: list[str] = []
        inserted = False
        for raw in p.read_text(encoding="utf-8").splitlines():
            stripped = raw.split("#", 1)[0].strip()
            if any(stripped.startswith(pref) for pref in linear_prefixes):
                continue
            if stripped.startswith("Group.LinearMovement.") or stripped.startswith("Group1.LinearMovement."):
                continue
            if stripped == "Group.movementModel = ShortestPathMapBasedMovement":
                if not inserted:
                    lines_out.append(header_comment.rstrip())
                    inserted = True
                lines_out.append(raw)
                continue
            if "Legacy LinearMovement keys removed" in raw:
                continue
            lines_out.append(raw)
        # Remove obsolete header comments about LinearMovement
        cleaned: list[str] = []
        for line in lines_out:
            if "Levers: LinearMovement" in line or "Free-space (LinearMovement)" in line:
                continue
            if line.strip() == "# Directional, fast movement (linear toward exit).":
                continue
            cleaned.append(line)
        new_text = "\n".join(cleaned) + "\n"
        if apply:
            p.write_text(new_text, encoding="utf-8")
        changed.append(str(p.relative_to(SCENARIOS_DIR.parent)))
    return changed


def update_manifests(apply: bool) -> None:
    for manifest in (
        SCENARIOS_DIR / "base_scenarios" / "manifest.csv",
        SCENARIOS_DIR / "corpus_v1" / "manifest.csv",
    ):
        if not manifest.is_file():
            continue
        text = manifest.read_text(encoding="utf-8")
        new_text = text.replace(C4_OLD, C4_NEW)
        if apply and new_text != text:
            manifest.write_text(new_text, encoding="utf-8")


def write_report(rows: list[dict], c4_renamed: list[str], c6_cleaned: list[str]) -> None:
    fails = [r for r in rows if r["status"] == "FAIL"]
    path = REPORTS / "KumpulaCampus_campus_settings_report.md"
    lines = [
        "# KumpulaCampus — campus settings audit",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"- Files audited: {len(rows)}",
        f"- FAIL: {len(fails)}",
        f"- C4 renamed: {len(c4_renamed)}",
        f"- C6 LinearMovement cleanup: {len(c6_cleaned)}",
        "",
        "## Movement model",
        "",
        "All campus scenarios use `ShortestPathMapBasedMovement` on `data/KumpulaCampus/roads.wkt`. "
        "No `routeFile` — shuttle WKT is optional for figures only.",
        "",
        "## C4 rename",
        "",
        f"`{C4_OLD}` → `{C4_NEW}`: mass campus event (auditorium / open day), not a sports stadium.",
        "",
        "## C6 evacuation",
        "",
        "Residual `Group.LinearMovement.*` keys removed (legacy 800×600 world). "
        "Evacuation represented by SPMM with speed 2–4 m/s and waitTime 0–10 s.",
        "",
    ]
    if fails:
        lines.extend(["## Failures", ""])
        for r in fails[:20]:
            lines.append(f"- `{r['settings_path']}`: {r['issues']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rename-c4", action="store_true")
    ap.add_argument("--cleanup-c6", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rows: list[dict] = []
    for root in (BASE_CAMPUS, CORPUS_CAMPUS):
        if root.is_dir():
            for sp in sorted(root.glob("*.settings")):
                rows.append(audit_file(sp))

    c4_renamed: list[str] = []
    c6_cleaned: list[str] = []
    if args.rename_c4:
        c4_renamed = rename_c4(apply=args.apply)
        update_manifests(apply=args.apply)
    if args.cleanup_c6:
        c6_cleaned = cleanup_c6_linear(apply=args.apply)

    if args.apply and (c4_renamed or c6_cleaned):
        rows = []
        for root in (BASE_CAMPUS, CORPUS_CAMPUS):
            if root.is_dir():
                for sp in sorted(root.glob("*.settings")):
                    rows.append(audit_file(sp))

    MAP_DATA.mkdir(parents=True, exist_ok=True)
    out_csv = MAP_DATA / "KumpulaCampus_campus_settings_audit.csv"
    if rows:
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    write_report(rows, c4_renamed, c6_cleaned)
    print(f"Wrote {out_csv} ({len(rows)} files)")
    if c4_renamed:
        print(f"C4 renamed: {len(c4_renamed)}")
    if c6_cleaned:
        print(f"C6 cleaned: {len(c6_cleaned)}")
    return 1 if any(r["status"] == "FAIL" for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
