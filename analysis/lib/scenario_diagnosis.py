"""
Cross-audit settings + simulation metrics; assign problem flags and priority.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from lib.map_context import parse_wkt_lines, roads_wkt_path, wkt_to_sim_coords
from lib.paths import REPO_ROOT
from lib.spatial_occupancy_io import find_spatial_artifacts

_ROADS_BBOX_CACHE: dict[str, tuple[float, float, float, float]] = {}


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse flat nested YAML (no lists) without PyYAML dependency."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key, _, val = line.strip().partition(":")
        key = key.strip()
        val = val.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if not val:
            node: dict[str, Any] = {}
            parent[key] = node
            stack.append((indent, node))
        else:
            if val.replace(".", "", 1).isdigit():
                parent[key] = float(val) if "." in val else int(val)
            else:
                parent[key] = val
    return root


def load_thresholds(path: Path) -> dict[str, Any]:
    return _parse_simple_yaml(path.read_text(encoding="utf-8"))


def _roads_bbox(dataset: str | None, repo_root: Path = REPO_ROOT) -> tuple[float, float, float, float] | None:
    if not dataset:
        return None
    if dataset in _ROADS_BBOX_CACHE:
        return _ROADS_BBOX_CACHE[dataset]
    rp = roads_wkt_path(dataset, repo_root)
    if not rp or not rp.is_file():
        return None
    sim = wkt_to_sim_coords(parse_wkt_lines(rp))
    xs: list[float] = []
    ys: list[float] = []
    for line in sim:
        for x, y in line:
            xs.append(x)
            ys.append(y)
    if not xs:
        return None
    bb = (min(xs), min(ys), max(xs), max(ys))
    _ROADS_BBOX_CACHE[dataset] = bb
    return bb


def _point_in_bbox(x: float, y: float, bb: tuple[float, float, float, float], margin: float = 50.0) -> bool:
    x0, y0, x1, y1 = bb
    return (x0 - margin) <= x <= (x1 + margin) and (y0 - margin) <= y <= (y1 + margin)


def coverage_accessible_from_grid(
    grid_path: Path,
    dataset: str | None,
    *,
    repo_root: Path = REPO_ROOT,
) -> float | None:
    """Fraction of visited cells whose center lies in roads bbox (sim coords)."""
    if not grid_path.is_file():
        return None
    bb = _roads_bbox(dataset, repo_root)
    if not bb:
        return None
    df = pd.read_csv(grid_path)
    if "visit_count" not in df.columns:
        return None
    visited = df[df["visit_count"] > 0]
    if visited.empty:
        return 0.0
    if "center_x" not in df.columns or "center_y" not in df.columns:
        return None
    inside = 0
    for _, row in visited.iterrows():
        if _point_in_bbox(float(row["center_x"]), float(row["center_y"]), bb):
            inside += 1
    return inside / len(visited)


def _is_structural_partition(row: pd.Series) -> bool:
    tp = str(row.get("tp", ""))
    if tp == "TP12":
        return True
    ev = str(row.get("events_summary", ""))
    if "tohosts=" in ev and "hosts=0, 1" in ev.replace(" ", ""):
        return True
    if "GroupToGroup" in str(row.get("movement_models", "")):
        return True
    return False


def _assign_flags(row: pd.Series, th: dict[str, Any], corpus_helsinki_pct: float) -> list[str]:
    flags: list[str] = []
    dr = float(row.get("delivery_ratio") or 0)
    oh = float(row.get("overhead_ratio") or 0)
    drops = float(row.get("drop_ratio") or 0)
    enc = float(row.get("total_encounters") or 0)
    structural = _is_structural_partition(row)

    if dr <= th["delivery"]["zero_max"] and not structural:
        flags.append("ZERO_DELIVERY")
    if dr >= th["delivery"]["saturated_min"]:
        flags.append("SATURATED_DELIVERY")
    if oh > th["overhead"]["extreme_min"]:
        flags.append("EXTREME_OVERHEAD")
    if drops > th["drops"]["extreme_min"]:
        flags.append("EXTREME_DROPS")
    if enc <= th["contacts"]["zero_max"]:
        flags.append("ZERO_CONTACTS")
    if structural and dr <= th["delivery"]["zero_max"] and enc > 0:
        flags.append("STRUCTURAL_PARTITION_VALID")

    cwr = row.get("coverage_world_ratio")
    car = row.get("coverage_accessible_ratio")
    if cwr is not None and not pd.isna(cwr):
        if float(cwr) < th["spatial"]["map_underused_coverage_world_max"]:
            flags.append("MAP_UNDERUSED")
        if car is not None and not pd.isna(car) and float(cwr) > 0:
            ratio = float(car) / float(cwr)
            if ratio > th["spatial"]["map_too_large_accessible_ratio_min"]:
                flags.append("MAP_TOO_LARGE")

    wx = row.get("world_x")
    wy = row.get("world_y")
    dataset = row.get("map_dataset")
    if wx and wy and dataset:
        try:
            world_area = float(wx) * float(wy)
            bb = _roads_bbox(str(dataset))
            if bb:
                roads_area = (bb[2] - bb[0]) * (bb[3] - bb[1])
                if roads_area > 0 and world_area / roads_area > th["spatial"]["world_vs_roads_area_ratio_min"]:
                    if "MAP_TOO_LARGE" not in flags:
                        flags.append("MAP_TOO_LARGE")
        except (TypeError, ValueError):
            pass

    if corpus_helsinki_pct >= th["corpus"]["single_map_dependency_pct"]:
        flags.append("SINGLE_MAP_DEPENDENCY")

    if row.get("tp_not_differentiating"):
        flags.append("TP_NOT_DIFFERENTIATING")

    return flags


def _flag_set(val: Any) -> set[str]:
    if isinstance(val, list):
        return set(val)
    if isinstance(val, str):
        return {x.strip() for x in val.split(",") if x.strip()}
    return set()


def _priority(flags: list[str], th: dict[str, Any]) -> str:
    pr = th.get("priority", {})
    p0 = _flag_set(pr.get("p0_flags", []))
    p1 = _flag_set(pr.get("p1_flags", []))
    fs = set(flags) - {"STRUCTURAL_PARTITION_VALID", "SATURATED_DELIVERY"}
    if fs & p0:
        return "P0"
    if fs & p1:
        return "P1"
    if flags:
        return "P2"
    return ""


def enrich_spatial_from_reports(
    df: pd.DataFrame,
    reports_dir: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> pd.DataFrame:
    """Fill coverage_accessible_ratio from grid CSVs when missing."""
    if "coverage_accessible_ratio" not in df.columns:
        df["coverage_accessible_ratio"] = None
    for idx, row in df.iterrows():
        if pd.notna(row.get("coverage_accessible_ratio")):
            continue
        scenario = str(row["scenario"])
        paths = find_spatial_artifacts(reports_dir, scenario)
        grid = paths.get("grid")
        if grid and grid.is_file():
            car = coverage_accessible_from_grid(
                grid,
                str(row.get("map_dataset") or row.get("map_dataset_spatial") or ""),
                repo_root=repo_root,
            )
            if car is not None:
                df.at[idx, "coverage_accessible_ratio"] = car
    return df


def build_diagnosis_table(
    settings_audit: pd.DataFrame,
    output_metrics: pd.DataFrame,
    indirect: pd.DataFrame,
    spatial: pd.DataFrame | None,
    *,
    thresholds_path: Path,
    reports_dir: Path,
    repo_root: Path = REPO_ROOT,
) -> pd.DataFrame:
    th = load_thresholds(thresholds_path)

    base = settings_audit.copy()
    base = base.merge(output_metrics, on="scenario", how="left", suffixes=("", "_out"))
    base = base.merge(
        indirect[
            [
                "scenario",
                "total_encounters",
                "N_hosts",
                "contact_time_per_min",
                "ratio_contact_nodes",
            ]
        ],
        on="scenario",
        how="left",
    )

    if spatial is not None and not spatial.empty:
        sp_cols = [
            c
            for c in spatial.columns
            if c
            in (
                "scenario",
                "final_coverage_pct",
                "cells_visited_pct",
                "map_dataset",
                "world_x",
                "world_y",
            )
        ]
        sp = spatial[sp_cols].copy()
        sp = sp.rename(columns={"map_dataset": "map_dataset_spatial"})
        base = base.merge(sp, on="scenario", how="left")
        if "map_dataset_spatial" in base.columns:
            base["map_dataset"] = base["map_dataset"].fillna(base["map_dataset_spatial"])

    if "final_coverage_pct" in base.columns:
        base["coverage_world_ratio"] = base["final_coverage_pct"] / 100.0
    else:
        base["coverage_world_ratio"] = None

    base["coverage_accessible_ratio"] = None
    base = enrich_spatial_from_reports(base, reports_dir, repo_root=repo_root)

    corpus_helsinki_pct = float(settings_audit["map_dataset"].eq("HelsinkiMedium").mean() * 100)

    # TP differentiation per base
    tp_std = (
        base.groupby("scenario_base")["delivery_ratio"]
        .std()
        .rename("delivery_std_by_base")
    )
    base = base.merge(tp_std, on="scenario_base", how="left")
    std_max = th["traffic_profile"]["tp_not_differentiating_std_max"]
    base["tp_not_differentiating"] = base["delivery_std_by_base"].fillna(0) < std_max

    rows: list[dict[str, Any]] = []
    for _, row in base.iterrows():
        flags = _assign_flags(row, th, corpus_helsinki_pct)
        priority = _priority(flags, th)
        rows.append(
            {
                "scenario": row["scenario"],
                "family": row.get("family", ""),
                "scenario_base": row.get("scenario_base", ""),
                "tp": row.get("tp", ""),
                "map_dataset": row.get("map_dataset", ""),
                "movement_models": row.get("movement_models", ""),
                "n_hosts": row.get("n_hosts", ""),
                "delivery_ratio": row.get("delivery_ratio"),
                "overhead_ratio": row.get("overhead_ratio"),
                "drop_ratio": row.get("drop_ratio"),
                "total_encounters": row.get("total_encounters"),
                "coverage_world_ratio": row.get("coverage_world_ratio"),
                "coverage_accessible_ratio": row.get("coverage_accessible_ratio"),
                "delivery_std_by_base": row.get("delivery_std_by_base"),
                "problem_flags": "|".join(flags),
                "priority": priority,
                "recommended_action_hint": _action_hint(flags, row),
            }
        )

    return pd.DataFrame(rows)


def _action_hint(flags: list[str], row: pd.Series) -> str:
    if "STRUCTURAL_PARTITION_VALID" in flags:
        return "keep_diagnostic"
    if "ZERO_DELIVERY" in flags:
        return "redesign_mobility_or_traffic"
    if "MAP_TOO_LARGE" in flags or "MAP_UNDERUSED" in flags:
        return "change_map_or_worldSize"
    if "EXTREME_OVERHEAD" in flags or "EXTREME_DROPS" in flags:
        return "adjust_traffic"
    if "TP_NOT_DIFFERENTIATING" in flags:
        return "review_tp_overlay"
    if "ZERO_CONTACTS" in flags:
        return "stress_or_exclude"
    return "keep"


def write_diagnosis_report(df: pd.DataFrame, path: Path, thresholds_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = len(df)
    flagged = df[df["problem_flags"].astype(str).str.len() > 0]
    p0 = df[df["priority"] == "P0"]
    flag_counts: dict[str, int] = {}
    for fs in df["problem_flags"].fillna(""):
        for f in str(fs).split("|"):
            if f:
                flag_counts[f] = flag_counts.get(f, 0) + 1

    lines = [
        "# Scenario diagnosis (corpus_v2)",
        "",
        f"- Scenarios: **{n}**",
        f"- With any flag: **{len(flagged)}**",
        f"- Priority P0: **{len(p0)}**",
        f"- Thresholds: `{thresholds_path.name}`",
        "",
        "## Flag counts",
        "",
        "| flag | count |",
        "|------|------:|",
    ]
    for f, c in sorted(flag_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| `{f}` | {c} |")

    lines.extend(["", "## Top P0 examples (delivery=0, non-structural)", ""])
    zd = p0[p0["problem_flags"].str.contains("ZERO_DELIVERY", na=False)].head(10)
    if not zd.empty:
        lines.append("| scenario | delivery | overhead | flags |")
        lines.append("|----------|----------:|---------:|-------|")
        for _, r in zd.iterrows():
            lines.append(
                f"| `{r['scenario']}` | {r.get('delivery_ratio', '')} | "
                f"{r.get('overhead_ratio', '')} | `{r['problem_flags']}` |"
            )

    lines.extend(["", "## By family (P0 count)", "", "| family | P0 |", "|--------|---:|"])
    fam_p0 = df[df["priority"] == "P0"].groupby("family").size()
    for fam, c in fam_p0.sort_values(ascending=False).items():
        lines.append(f"| `{fam}` | {c} |")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `STRUCTURAL_PARTITION_VALID` marks intentional zero delivery (e.g. TP12 cross-group).",
            "- `MAP_UNDERUSED` uses `coverage_world_ratio` < threshold; WDM on large worlds often ~8–10%.",
            "- Full table: `data/scenario_diagnosis.csv`.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
