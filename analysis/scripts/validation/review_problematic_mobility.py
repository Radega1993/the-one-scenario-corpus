#!/usr/bin/env python3
"""Generate problematic_mobility_scenarios_review.md (pre-repair diagnosis)."""

from __future__ import annotations

import csv
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_ANALYSIS = Path(__file__).resolve().parents[2]
_REPO = _ANALYSIS.parent.parent
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

ARCHIVE = sorted((_ANALYSIS.parent / "_archive").glob("settings_backup_*"))
ARCHIVE_DIR = ARCHIVE[-1] if ARCHIVE else None

SCENARIOS = [
    {
        "id": "S1",
        "old": "S1_StrongCommunities_SeparateClusters",
        "new": "S1_StrongCommunities_LimitedMixing",
        "map": "KallioCommunityCompact",
        "family": "06_social",
    },
    {
        "id": "S6",
        "old": "S6_FamilyGroups_SmallPersistent",
        "new": "S6_FamilyGroups_LocalRoutines",
        "map": "KallioCommunityCompact",
        "family": "06_social",
    },
    {
        "id": "D1",
        "old": "D1_ShelterHotspots_Clusters",
        "new": "D1_ShelterHotspots_EmergencyMobility",
        "map": "HelsinkiDisrupted",
        "family": "05_disaster",
    },
    {
        "id": "R2",
        "old": "R2_VillagesTrails_ThreeClusters",
        "new": "R2_VillagesTrails_InterVillage",
        "map": "NuuksioSparseTrails",
        "family": "04_rural",
    },
]

def load_kv(path: Path) -> dict[str, str]:
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

def summarize_base(path: Path) -> dict:
    kv = load_kv(path)
    groups = int(kv.get("Scenario.nrofHostGroups", "0"))
    mm: list[str] = []
    hosts = 0
    for i in range(1, groups + 1):
        gk = f"Group{i}."
        mm.append(kv.get(f"Group{i}.movementModel", kv.get("Group.movementModel", "?")))
        hosts += int(kv.get(f"Group{i}.nrofHosts", kv.get("Group.nrofHosts", "0") or "0"))
    return {
        "world_size": kv.get("MovementModel.worldSize", ""),
        "movement": " | ".join(mm),
        "hosts": hosts,
        "transmit_range": kv.get("bt0.transmitRange", ""),
        "cluster": sum(1 for k, v in kv.items() if ".clusterCenter" in k),
    }

def spatial_row(name: str) -> dict:
    p = _ANALYSIS / "data" / "spatial_occupancy_metrics.csv"
    if not p.is_file():
        return {}
    import pandas as pd

    df = pd.read_csv(p)
    col = "scenario" if "scenario" in df.columns else None
    if not col:
        return {}
    m = df[df[col].astype(str).str.contains(name, na=False)]
    if m.empty:
        return {}
    r = m.iloc[-1]
    return {
        k: r.get(k)
        for k in (
            "coverage_world_pct",
            "coverage_map_bbox_pct",
            "coverage_road_cells_pct",
        )
        if k in r
    }

def main() -> int:
    out = _ANALYSIS / "reports" / "problematic_mobility_scenarios_review.md"
    lines = [
        "# Problematic mobility scenarios — review",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "Backup: `" + (str(ARCHIVE_DIR.relative_to(_REPO)) if ARCHIVE_DIR else "n/a") + "`",
        "",
        "## Decision",
        "",
        "All four scenarios are **repaired and kept in the environmental core** (`corpus_v1`). "
        "`ClusterMovement` was replaced with map-aware models (`MapRouteMovement`, `ShortestPathMapBasedMovement`).",
        "",
    ]
    for sc in SCENARIOS:
        old_path = None
        if ARCHIVE_DIR:
            old_path = ARCHIVE_DIR / "base_scenarios" / sc["family"] / f"{sc['old']}.settings"
        summ = summarize_base(old_path) if old_path else {}
        sp = spatial_row(sc["old"])
        lines += [
            f"## {sc['id']}: `{sc['old']}` → `{sc['new']}`",
            "",
            f"- **Map:** `{sc['map']}`",
            f"- **worldSize:** {summ.get('world_size', '—')}",
            f"- **Hosts:** {summ.get('hosts', '—')}",
            f"- **Movement (legacy):** {summ.get('movement', '—')}",
            f"- **ClusterMovement groups:** {summ.get('cluster', '—')}",
            f"- **transmitRange:** {summ.get('transmit_range', '—')}",
            "",
            "**Spatial metrics (legacy name, if simulated):**",
        ]
        if sp:
            lines.append(
                f"- world {sp.get('coverage_world_pct', '—')}% · "
                f"map bbox {sp.get('coverage_map_bbox_pct', '—')}% · "
                f"road cells {sp.get('coverage_road_cells_pct', '—')}%"
            )
        else:
            lines.append("- (no row in `spatial_occupancy_metrics.csv`)")
        lines += [
            "",
            "**Weakness:** nodes moved in circular clusters off the road network; heatmaps showed isolated blobs; "
            "map was largely decorative for protocol evaluation.",
            "",
            "**S1 note:** TP03/08/10/11 previously hit simulation timeouts (~10400s) under spatial overlay.",
            "",
        ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())