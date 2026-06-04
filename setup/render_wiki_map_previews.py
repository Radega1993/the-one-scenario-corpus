#!/usr/bin/env python3
"""Render road-network preview PNGs for wiki and analysis figures."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from map_geometry import (  # noqa: E402
    ACTIVE_MAPS,
    ANALYSIS_DATA,
    REPO_ROOT,
    WKT_DIR,
    load_map_metadata,
    list_poi_wkt_files,
    list_route_wkt_files,
    load_road_graph,
    parse_linestrings,
    parse_points,
    resolve_route_path_polyline,
    threshold_for_family,
    transform_points,
    vertex_distances,
    world_size_from_metadata,
    wkt_to_sim_coords,
)
from route_semantic_config import ROUTE_COLORS  # noqa: E402

WIKI_OUT = REPO_ROOT / "scenarios" / ".wiki-clone" / "assets" / "maps"
FIG_OUT = REPO_ROOT / "scenarios" / "analysis" / "figures" / "maps"
PAPER_FIG_OUT = REPO_ROOT / "scenarios" / "analysis" / "figures" / "paper" / "maps"

MAP_META = {
    "HelsinkiDowntown": ("01_urban", "OSM"),
    "KumpulaCampus": ("02_campus", "OSM"),
    "ManhattanMidtownGrid": ("03_vehicles", "OSM"),
    "NuuksioSparseTrails": ("04_rural", "OSM"),
    "HelsinkiDisrupted": ("05_disaster", "OSM"),
    "KallioCommunityCompact": ("06_social", "OSM"),
}

def load_bus_validation() -> dict[tuple[str, str], dict]:
    p = ANALYSIS_DATA / "bus_route_validation.csv"
    out: dict[tuple[str, str], dict] = {}
    if not p.is_file():
        return out
    with p.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[(row["map_name"], row["route_file"])] = row
    return out

def load_poi_validation() -> dict[tuple[str, str], dict]:
    p = ANALYSIS_DATA / "map_poi_validation.csv"
    out: dict[tuple[str, str], dict] = {}
    if not p.is_file():
        return out
    with p.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[(row["map_name"], row["poi_file"])] = row
    return out

def render_map(
    map_name: str,
    *,
    validation_overlay: bool = False,
    paper_ready: bool = False,
    bus_val: dict,
    poi_val: dict,
) -> None:
    family, source = MAP_META.get(map_name, ("", "OSM"))
    map_dir = WKT_DIR / map_name
    meta = load_map_metadata(map_dir)
    wx, wy = world_size_from_metadata(meta)
    thresh = threshold_for_family(family)

    rg, _, _ = load_road_graph(map_name)
    raw_roads = parse_linestrings(map_dir / "roads.wkt")
    sim_roads = wkt_to_sim_coords(raw_roads)

    fig, ax = plt.subplots(figsize=(7.5, 6.5), dpi=120)
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")

    for line in sim_roads:
        xs, ys = zip(*line)
        ax.plot(xs, ys, color="#2c5282", linewidth=0.6, alpha=0.85)

    if wx > 0 and wy > 0:
        ax.add_patch(
            Rectangle((0, 0), wx, wy, fill=False, edgecolor="#a0aec0", linestyle="--", linewidth=1.2)
        )
    min_x, min_y, max_x, max_y = rg.bbox
    if max_x > min_x:
        ax.add_patch(
            Rectangle(
                (min_x, min_y),
                max_x - min_x,
                max_y - min_y,
                fill=False,
                edgecolor="#cbd5e0",
                linestyle=":",
                linewidth=0.8,
            )
        )

    route_warnings: list[str] = []
    for route_path in list_route_wkt_files(map_dir):
        raw = parse_linestrings(route_path)
        if not raw:
            continue
        stops = wkt_to_sim_coords(raw)[0]
        fname = route_path.name
        color = ROUTE_COLORS.get(fname, "#c05621")
        label_stem = route_path.stem

        resolved, failed_segs = resolve_route_path_polyline(rg, stops)
        if resolved and len(resolved) >= 2:
            rx, ry = zip(*resolved)
            ax.plot(rx, ry, color=color, linewidth=2.0, linestyle="-", label=f"{label_stem} (path)", zorder=3)
        if len(stops) >= 2:
            sx, sy = zip(*stops)
            ax.plot(
                sx,
                sy,
                color=color,
                linewidth=0.9,
                linestyle=":",
                alpha=0.55,
                label=f"{label_stem} (stops)",
                marker="o",
                markersize=3,
                zorder=2,
            )
        if failed_segs:
            for i, j in failed_segs:
                ax.plot(
                    [stops[i][0], stops[j][0]],
                    [stops[i][1], stops[j][1]],
                    color="#e53e3e",
                    linewidth=2.5,
                    linestyle="-",
                    zorder=4,
                )
            route_warnings.append(f"{label_stem}: {len(failed_segs)} unresolved segment(s)")
        if validation_overlay and not paper_ready:
            dists = vertex_distances(rg, stops)
            bad = [stops[i] for i, d in enumerate(dists) if d > thresh]
            if bad:
                bx, by = zip(*bad)
                ax.scatter(bx, by, c="red", s=40, zorder=5, label=f"{label_stem} warn")

    for poi_path in list_poi_wkt_files(map_dir):
        pts = transform_points(parse_points(poi_path))
        if not pts:
            continue
        color = {"A_homes.wkt": "#38a169", "A_offices.wkt": "#805ad5", "A_meetingspots.wkt": "#d69e2e"}.get(
            poi_path.name, "#718096"
        )
        label = poi_path.name.replace("A_", "").replace(".wkt", "")
        px, py = zip(*pts)
        ax.scatter(px, py, s=10, c=color, alpha=0.75, linewidths=0, label=label)
        if validation_overlay and not paper_ready:
            dists = vertex_distances(rg, pts)
            bad = [pts[i] for i, d in enumerate(dists) if d > thresh]
            if bad:
                bx, by = zip(*bad)
                ax.scatter(bx, by, facecolors="none", edgecolors="red", s=60, linewidths=1.5, zorder=6)

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x (m, sim-aligned)")
    ax.set_ylabel("y (m, sim-aligned)")
    if paper_ready:
        title = f"{map_name} — urban benchmark map\nworldSize {int(wx)}×{int(wy)} m · {source}"
    else:
        title = f"{map_name}\n{family} · worldSize {int(wx)}×{int(wy)} m · {source}"
        if route_warnings:
            title += "\nWARNING: " + "; ".join(route_warnings[:2])
    ax.set_title(title, fontsize=11, fontweight="bold")
    if validation_overlay and not paper_ready:
        ax.set_title(title + "\n(red = geometry warnings)", fontsize=10, fontweight="bold")
    ax.legend(loc="upper right", fontsize=6, framealpha=0.92)
    fig.text(
        0.5,
        0.01,
        "Solid route = resolved road-following path; dotted line = stop order reference.",
        ha="center",
        fontsize=8,
        color="#4a5568",
    )
    fig.tight_layout(rect=[0, 0.03, 1, 1])

    if paper_ready:
        PAPER_FIG_OUT.mkdir(parents=True, exist_ok=True)
        paper_path = PAPER_FIG_OUT / f"{map_name}_paper_ready.png"
        fig.savefig(paper_path, bbox_inches="tight")
        for out_dir in (WIKI_OUT, FIG_OUT):
            out_dir.mkdir(parents=True, exist_ok=True)
            fig.savefig(out_dir / f"{map_name}.png", bbox_inches="tight")
        print(f"Wrote {paper_path}, wiki asset, and {FIG_OUT / f'{map_name}.png'}")
    else:
        for out_dir in (WIKI_OUT, FIG_OUT):
            out_dir.mkdir(parents=True, exist_ok=True)
            fig.savefig(out_dir / f"{map_name}.png", bbox_inches="tight")
        val_name = f"{map_name}_validation.png"
        if validation_overlay:
            fig.savefig(FIG_OUT / val_name, bbox_inches="tight")
            print(f"Wrote {map_name} -> wiki + figures + {val_name}")
        else:
            print(f"Wrote {map_name} -> wiki + figures")
    plt.close(fig)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validation", action="store_true", help="Write *_validation.png with warning overlays")
    ap.add_argument("--paper-ready", action="store_true", help="Paper figure (no red warnings) + paper/maps/")
    ap.add_argument("--maps", type=str, default="")
    args = ap.parse_args()

    if args.validation and args.paper_ready:
        print("Use --validation or --paper-ready, not both")
        return 1

    bus_val = load_bus_validation()
    poi_val = load_poi_validation()
    maps = [m.strip() for m in args.maps.split(",") if m.strip()] or ACTIVE_MAPS
    for name in maps:
        render_map(
            name,
            validation_overlay=args.validation,
            paper_ready=args.paper_ready,
            bus_val=bus_val,
            poi_val=poi_val,
        )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())