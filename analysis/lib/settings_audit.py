"""
Structured extraction from The ONE .settings files for corpus audit.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from lib.map_context import infer_map_dataset, load_settings_flat

WKT_PATH_RE = re.compile(r"data/[^\s,]+\.wkt", re.I)
GROUP_NUM_RE = re.compile(r"^Group(\d+)\.(.+)$")
EVENT_NUM_RE = re.compile(r"^Events(\d+)\.(.+)$")

WDM_KEYS = (
    "workDayLength",
    "timeDiffSTD",
    "probGoShoppingAfterWork",
    "nrOfMeetingSpots",
    "nrOfOffices",
    "officeSize",
    "nrOfShops",
    "ownCarProb",
    "officeWaitTimeParetoCoeff",
    "officeMinWaitTime",
    "officeMaxWaitTime",
)

def parse_scenario_name(name: str) -> tuple[str, str]:
    m = re.search(r"__(TP\d{2}_[A-Za-z0-9]+)$", name)
    if m:
        return name[: m.start()], m.group(1).split("_", 1)[0]
    return name, ""

def _collect_group_fields(kv: dict[str, str]) -> dict[str, Any]:
    n_groups = 0
    try:
        n_groups = int(kv.get("Scenario.nrofHostGroups", "0") or "0")
    except ValueError:
        pass

    per_group: dict[int, dict[str, str]] = {}
    for key, val in kv.items():
        m = GROUP_NUM_RE.match(key)
        if m:
            gi = int(m.group(1))
            per_group.setdefault(gi, {})[m.group(2)] = val

    movement_models: list[str] = []
    hosts_per_group: list[int] = []
    speeds: list[str] = []
    waits: list[str] = []
    ranges: list[str] = []
    speeds_tx: list[str] = []
    buffers: list[str] = []
    ttls: list[str] = []
    routes: list[str] = []
    active_times: list[str] = []

    for gi in sorted(per_group.keys()):
        g = per_group[gi]
        mm = g.get("movementModel", kv.get("Group.movementModel", ""))
        if mm:
            movement_models.append(f"G{gi}:{mm}")
        nh = g.get("nrofHosts", kv.get("Group.nrofHosts", ""))
        if nh:
            try:
                hosts_per_group.append(int(str(nh).split(",")[0].strip()))
            except ValueError:
                pass
        if g.get("speed") or kv.get("Group.speed"):
            speeds.append(g.get("speed", kv.get("Group.speed", "")))
        if g.get("waitTime") or kv.get("Group.waitTime"):
            waits.append(g.get("waitTime", kv.get("Group.waitTime", "")))
        if g.get("transmitRange") or kv.get("Group.transmitRange"):
            ranges.append(g.get("transmitRange", kv.get("Group.transmitRange", "")))
        if g.get("transmitSpeed") or kv.get("Group.transmitSpeed"):
            speeds_tx.append(g.get("transmitSpeed", kv.get("Group.transmitSpeed", "")))
        if g.get("bufferSize") or kv.get("Group.bufferSize"):
            buffers.append(g.get("bufferSize", kv.get("Group.bufferSize", "")))
        if g.get("msgTtl") or kv.get("Group.msgTtl"):
            ttls.append(g.get("msgTtl", kv.get("Group.msgTtl", "")))
        if g.get("routeFile"):
            routes.append(g.get("routeFile"))
        if g.get("activeTimes"):
            active_times.append(g.get("activeTimes"))

    total_hosts = sum(hosts_per_group) if hosts_per_group else None
    if total_hosts is None and "Group.nrofHosts" in kv:
        try:
            total_hosts = int(kv["Group.nrofHosts"].split(",")[0].strip())
        except ValueError:
            total_hosts = None

    wdm: dict[str, str] = {}
    for wk in WDM_KEYS:
        if wk in kv:
            wdm[wk] = kv[wk]
        for gi, g in per_group.items():
            if wk in g:
                wdm[f"G{gi}.{wk}"] = g[wk]

    return {
        "nrof_host_groups": n_groups or len(per_group),
        "movement_models": "|".join(movement_models) if movement_models else kv.get("Group.movementModel", ""),
        "n_hosts": total_hosts,
        "hosts_per_group": ",".join(str(x) for x in hosts_per_group) if hosts_per_group else "",
        "speed": "|".join(dict.fromkeys(speeds)) if speeds else kv.get("Group.speed", ""),
        "wait_time": "|".join(dict.fromkeys(waits)) if waits else kv.get("Group.waitTime", ""),
        "buffer_size": "|".join(dict.fromkeys(buffers)) if buffers else kv.get("Group.bufferSize", ""),
        "msg_ttl": "|".join(dict.fromkeys(ttls)) if ttls else kv.get("Group.msgTtl", ""),
        "transmit_range": "|".join(dict.fromkeys(ranges)) if ranges else kv.get("Group.transmitRange", ""),
        "transmit_speed": "|".join(dict.fromkeys(speeds_tx)) if speeds_tx else kv.get("Group.transmitSpeed", ""),
        "route_files": "|".join(dict.fromkeys(routes)) if routes else kv.get("Group.routeFile", ""),
        "active_times": "|".join(active_times) if active_times else "",
        "wdm_params": "|".join(f"{k}={v}" for k, v in sorted(wdm.items())) if wdm else "",
    }

def _collect_events(kv: dict[str, str]) -> dict[str, str]:
    try:
        n_ev = int(kv.get("Events.nrof", "0") or "0")
    except ValueError:
        n_ev = 0

    blocks: list[str] = []
    for i in range(1, max(n_ev, 1) + 3):
        parts = []
        for suf in ("hosts", "tohosts", "interval", "size", "time", "class"):
            k = f"Events{i}.{suf}"
            if k in kv:
                parts.append(f"{suf}={kv[k]}")
        if parts:
            blocks.append(f"E{i}:{'|'.join(parts)}")

    return {
        "events_nrof": n_ev,
        "events_summary": ";".join(blocks) if blocks else "",
    }

def audit_settings_file(
    path: Path,
    *,
    family: str = "",
    scenario_base: str = "",
    tp: str = "",
) -> dict[str, Any]:
    kv = load_settings_flat(path)
    scenario = kv.get("Scenario.name", path.stem)
    base, tp_id = parse_scenario_name(scenario)
    if not scenario_base:
        scenario_base = base
    if not tp:
        tp = tp_id

    world_raw = kv.get("MovementModel.worldSize", "")
    wx = wy = ""
    if world_raw:
        parts = [p.strip() for p in world_raw.split(",")]
        if len(parts) >= 2:
            wx, wy = parts[0], parts[1]

    map_file = kv.get("MapBasedMovement.mapFile1", "")
    if not map_file:
        for k, v in kv.items():
            if "mapFile" in k and ".wkt" in v:
                map_file = v
                break

    dataset = infer_map_dataset(kv)
    wkt_paths = sorted(set(WKT_PATH_RE.findall("\n".join(f"{k}={v}" for k, v in kv.items()))))

    grp = _collect_group_fields(kv)
    ev = _collect_events(kv)

    row: dict[str, Any] = {
        "scenario": scenario,
        "family": family,
        "scenario_base": scenario_base,
        "tp": tp,
        "settings_path": str(path),
        "scenario_end_time": kv.get("Scenario.endTime", ""),
        "world_x": wx,
        "world_y": wy,
        "map_file": map_file,
        "map_dataset": dataset or "",
        "router": kv.get("Group.router", ""),
        "simulate_connections": kv.get("Scenario.simulateConnections", ""),
        "wkt_paths": ";".join(wkt_paths),
    }
    row.update(grp)
    row.update(ev)
    return row

def audit_from_manifest(manifest_rows: list[dict[str, str]], repo_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for mr in manifest_rows:
        sp = Path(mr.get("settings_file", ""))
        if not sp.is_absolute():
            sp = repo_root / sp
        if not sp.is_file():
            continue
        rows.append(
            audit_settings_file(
                sp,
                family=str(mr.get("family", "")),
                scenario_base=str(mr.get("scenario_base", "")),
                tp=str(mr.get("traffic_profile_id", mr.get("tp", ""))),
            )
        )
    return rows

def audit_corpus_dir(corpus_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for p in sorted(corpus_dir.rglob("*.settings")):
        family = p.parent.name if p.parent else ""
        rows.append(audit_settings_file(p, family=family))
    return rows