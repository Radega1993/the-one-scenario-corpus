#!/usr/bin/env python3
"""
Post-process spatial occupancy CSVs from The ONE (SpatialOccupancyReport).

Generates:
  - figures/spatial_heatmaps/{scenario}.png (roads WKT + optional GUI underlay + occupancy)
  - data/spatial_occupancy_metrics.csv
  - data/spatial_coverage_timeseries.csv (long format)
  - figures/spatial_occupancy_curves_by_family.png (requires manifest for family / endTime)
  - reports/spatial_occupancy_analysis_summary.md

Example:
  python3 scenarios/analysis/scripts/validation/analyze_spatial_occupancy.py \\
    --reports-dir reports --corpus corpus_v1 \\
    --manifest scenarios/corpus_v1/manifest.csv

  # Solo escenarios concretos (fusiona con metrics/timeseries existentes):
  python3 scenarios/analysis/scripts/validation/analyze_spatial_occupancy.py \\
    --manifest scenarios/corpus_v1/manifest.csv --reports-dir reports \\
    --name-regex 'S1_StrongCommunities_SeparateClusters__TP(03|11)'
"""

from __future__ import annotations

import argparse
import csv
import re
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402

_ANALYSIS = Path(__file__).resolve().parents[2]
if str(_ANALYSIS) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS))

from lib.map_context import MapContext, build_map_context  # noqa: E402
from lib.paths import ANALYSIS_DIR, REPO_ROOT  # noqa: E402
from lib.spatial_coverage import (  # noqa: E402
    coverage_title_parts,
    enrich_timeseries_from_positions,
    masks_for_scenario,
    metrics_for_scenario,
    visited_mask_from_grid,
    zoom_extent_from_masks,
)


def _load_spatial_io():
    spec = importlib.util.spec_from_file_location(
        "spatial_occupancy_io", ANALYSIS_DIR / "lib" / "spatial_occupancy_io.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def load_manifest(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "scenario_name" not in df.columns:
        raise ValueError("manifest must contain scenario_name")
    return df


def parse_end_time_from_settings(settings_path: Path) -> float | None:
    if not settings_path.is_file():
        return None
    for line in settings_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == "Scenario.endTime":
            try:
                return float(v.strip())
            except ValueError:
                return None
    return None


def scenario_list_from_corpus(corpus_dir: Path) -> list[str]:
    return sorted({p.stem for p in corpus_dir.rglob("*.settings")})


def _world_size_from_summary(summary_path: Path | None) -> tuple[float, float] | None:
    if summary_path is None or not summary_path.is_file():
        return None
    try:
        with summary_path.open(newline="", encoding="utf-8") as f:
            row = next(csv.DictReader(f), None)
        if not row:
            return None
        wx = float(row.get("world_x", "nan"))
        wy = float(row.get("world_y", "nan"))
        if wx == wx and wy == wy and wx > 0 and wy > 0:
            return wx, wy
    except (OSError, StopIteration, ValueError, TypeError):
        return None
    return None


def _grid_to_matrix(df: pd.DataFrame) -> tuple[np.ndarray, int, int]:
    ni = int(df["cell_i"].max()) + 1
    nj = int(df["cell_j"].max()) + 1
    mat = np.zeros((nj, ni), dtype=float)
    for _, row in df.iterrows():
        i, j = int(row["cell_i"]), int(row["cell_j"])
        if 0 <= i < ni and 0 <= j < nj:
            mat[j, i] = float(row["visit_count"])
    return mat, ni, nj


def _extent_full(wx: float, wy: float) -> tuple[float, float, float, float]:
    return (0.0, wx, 0.0, wy)


def _extent_crop(
    extent_full: tuple[float, float, float, float],
    ni: int,
    nj: int,
    i0: int,
    i1: int,
    j0: int,
    j1: int,
) -> tuple[float, float, float, float]:
    x0, x1, y0, y1 = extent_full
    wx = x1 - x0
    wy = y1 - y0
    return (
        x0 + (i0 / ni) * wx,
        x0 + (i1 / ni) * wx,
        y0 + (j0 / nj) * wy,
        y0 + (j1 / nj) * wy,
    )


def draw_map_layers(
    ax,
    extent: tuple[float, float, float, float],
    ctx: MapContext,
    *,
    show_roads: bool = True,
    show_underlay: bool = True,
    underlay_alpha: float = 0.42,
) -> None:
    if show_roads and ctx.roads_sim:
        for line in ctx.roads_sim:
            xs = [p[0] for p in line]
            ys = [p[1] for p in line]
            ax.plot(xs, ys, color="#888888", linewidth=0.35, alpha=0.85, zorder=0)
    if show_underlay and ctx.underlay is not None and ctx.underlay.path.is_file():
        try:
            img = plt.imread(str(ctx.underlay.path))
            ax.imshow(
                img,
                extent=extent,
                origin="upper",
                aspect="equal",
                alpha=underlay_alpha,
                zorder=1,
            )
        except Exception:
            pass
    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])


def draw_occupancy(
    ax,
    mat: np.ndarray,
    extent: tuple[float, float, float, float],
    title: str,
    *,
    log_scale: bool = True,
) -> None:
    vmax = float(np.nanmax(mat)) if mat.size else 0.0
    if log_scale and vmax > 1.0 and np.any(mat > 0):
        masked = np.ma.masked_where(mat <= 0.0, mat)
        vmin_log = max(1.0, float(masked.min()))
        im = ax.imshow(
            masked,
            origin="lower",
            aspect="equal",
            cmap="inferno",
            extent=extent,
            interpolation="nearest",
            norm=LogNorm(vmin=vmin_log, vmax=max(vmax, vmin_log + 1.0)),
            zorder=2,
            alpha=0.88,
        )
        cbar_label = "visit_count (log, 0 transparent)"
    else:
        im = ax.imshow(
            mat,
            origin="lower",
            aspect="equal",
            cmap="viridis",
            extent=extent,
            interpolation="nearest",
            zorder=2,
            alpha=0.88,
        )
        cbar_label = "visit_count"
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    plt.colorbar(im, ax=ax, label=cbar_label, shrink=0.85)


def _coverage_title_note(
    metrics: dict[str, float | int | str | None] | None,
    summary_csv: Path | None = None,
) -> str:
    parts = coverage_title_parts(metrics) if metrics else []
    if not parts and summary_csv and summary_csv.is_file():
        try:
            with summary_csv.open(newline="", encoding="utf-8") as f:
                sr = next(csv.DictReader(f), None)
            if sr and sr.get("final_coverage_pct"):
                parts = [f"world {float(sr['final_coverage_pct']):.1f}%"]
        except (OSError, ValueError, TypeError):
            pass
    if not parts:
        return ""
    return " | " + " · ".join(parts)


def heatmap_for_scenario(
    grid_csv: Path,
    out_png: Path,
    *,
    summary_csv: Path | None = None,
    settings_path: Path | None = None,
    metrics: dict[str, float | int | str | None] | None = None,
    masks=None,
    layout: str = "dual",
    zoom_mode: str = "roads",
    log_scale: bool = True,
    show_roads: bool = True,
    show_underlay: bool = True,
) -> None:
    df = pd.read_csv(grid_csv)
    mat, ni, nj = _grid_to_matrix(df)

    wx_wy = _world_size_from_summary(summary_csv)
    ctx = build_map_context(
        settings_path,
        world_x=wx_wy[0] if wx_wy else None,
        world_y=wx_wy[1] if wx_wy else None,
        load_roads=show_roads,
    )
    if ctx.world_x is None or ctx.world_y is None:
        if wx_wy:
            wx, wy = wx_wy
        else:
            wx = float(df["center_x"].max()) * 2 if "center_x" in df.columns else float(ni)
            wy = float(df["center_y"].max()) * 2 if "center_y" in df.columns else float(nj)
    else:
        wx, wy = ctx.world_x, ctx.world_y

    extent = _extent_full(wx, wy)
    title = grid_csv.stem.replace("_spatial_occupancy_grid", "")
    out_png.parent.mkdir(parents=True, exist_ok=True)

    visited_arr = visited_mask_from_grid(df, ni)
    visited_idx = np.argwhere(visited_arr)
    if visited_idx.size == 0:
        fig, ax = plt.subplots(figsize=(7, 5))
        draw_map_layers(ax, extent, ctx, show_roads=show_roads, show_underlay=show_underlay)
        ax.text(
            0.5,
            0.5,
            "Sin visitas en la rejilla",
            transform=ax.transAxes,
            ha="center",
            va="center",
        )
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(out_png, dpi=130)
        plt.close(fig)
        return

    if masks is not None:
        i0, i1, j0, j1 = zoom_extent_from_masks(masks, visited_arr, zoom_mode)
    else:
        pad = 2
        i0 = max(int(visited_idx[:, 0].min()) - pad, 0)
        i1 = min(int(visited_idx[:, 0].max()) + pad + 1, ni)
        j0 = max(int(visited_idx[:, 1].min()) - pad, 0)
        j1 = min(int(visited_idx[:, 1].max()) + pad + 1, nj)
    mat_zoom = mat[j0:j1, i0:i1]
    ext_zoom = _extent_crop(extent, ni, nj, i0, i1, j0, j1)

    cov_note = _coverage_title_note(metrics, summary_csv)
    zoom_labels = {
        "visited": "Zoom — celdas visitadas",
        "map_bbox": "Zoom — bbox mapa (roads.wkt)",
        "roads": "Zoom — celdas road network",
    }
    zoom_title = zoom_labels.get(zoom_mode, zoom_labels["visited"])

    if layout == "full":
        fig, ax = plt.subplots(figsize=(8, 7))
        draw_map_layers(ax, extent, ctx, show_roads=show_roads, show_underlay=show_underlay)
        draw_occupancy(ax, mat, extent, title + cov_note, log_scale=log_scale)
    elif layout == "zoom":
        fig, ax = plt.subplots(figsize=(8, 7))
        draw_map_layers(ax, ext_zoom, ctx, show_roads=show_roads, show_underlay=show_underlay)
        draw_occupancy(ax, mat_zoom, ext_zoom, title + " — zoom" + cov_note, log_scale=log_scale)
    else:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        draw_map_layers(axes[0], extent, ctx, show_roads=show_roads, show_underlay=show_underlay)
        draw_occupancy(
            axes[0],
            mat,
            extent,
            "Mundo completo (worldSize)" + cov_note,
            log_scale=log_scale,
        )
        draw_map_layers(axes[1], ext_zoom, ctx, show_roads=show_roads, show_underlay=False)
        draw_occupancy(
            axes[1],
            mat_zoom,
            ext_zoom,
            zoom_title,
            log_scale=log_scale,
        )
        fig.suptitle(title, fontsize=10)

    fig.tight_layout()
    fig.savefig(out_png, dpi=130)
    plt.close(fig)


def resolve_settings_path(
    scenario: str,
    meta_row: dict | None,
    corpus_dir: Path | None,
) -> Path | None:
    if meta_row and meta_row.get("settings_file"):
        p = Path(str(meta_row["settings_file"]))
        if not p.is_absolute():
            p = REPO_ROOT / p
        if p.is_file():
            return p
    if corpus_dir and corpus_dir.is_dir():
        matches = list(corpus_dir.rglob(f"{scenario}.settings"))
        if matches:
            return matches[0]
    return None


def main() -> int:
    spatial_occupancy_io = _load_spatial_io()

    ap = argparse.ArgumentParser(description="Analyze spatial occupancy CSVs from The ONE.")
    ap.add_argument("--reports-dir", type=str, default="reports", help="Directory with report CSVs (repo-relative)")
    ap.add_argument("--corpus", type=str, default="corpus_v1", help="Corpus folder name under scenarios/ or 'none'")
    ap.add_argument(
        "--manifest",
        type=str,
        default=None,
        help="manifest.csv (default: scenarios/<corpus>/manifest.csv if present)",
    )
    ap.add_argument("--output-data", type=str, default=str(ANALYSIS_DIR / "data"))
    ap.add_argument("--output-figures", type=str, default=str(ANALYSIS_DIR / "figures"))
    ap.add_argument("--families", type=str, default=None, help="Comma-separated family ids to include (optional)")
    ap.add_argument(
        "--name-regex",
        type=str,
        default=None,
        metavar="REGEX",
        help="Solo escenarios cuyo scenario_name coincida (re.search). Fusiona CSVs existentes.",
    )
    ap.add_argument(
        "--heatmap-layout",
        type=str,
        default="dual",
        choices=("dual", "full", "zoom"),
        help="Heatmap layout: dual panels (default), full world only, or zoom only",
    )
    ap.add_argument("--heatmap-linear", action="store_true", help="Linear color scale instead of log")
    ap.add_argument("--heatmap-no-roads", action="store_true", help="Do not draw WKT road layer")
    ap.add_argument("--heatmap-no-underlay", action="store_true", help="Do not draw GUI underlay PNG")
    ap.add_argument(
        "--settings-corpus",
        type=str,
        default=None,
        help="Corpus dir to find .settings if manifest lacks settings_file (default: --corpus)",
    )
    ap.add_argument(
        "--skip-heatmaps",
        action="store_true",
        help="Only update metrics CSV; do not render PNG heatmaps",
    )
    ap.add_argument(
        "--zoom-mode",
        type=str,
        default="roads",
        choices=("visited", "map_bbox", "roads"),
        help="Right panel zoom: visited cells, map bbox, or road-network cells (default: roads)",
    )
    ap.add_argument(
        "--primary-metric",
        type=str,
        default="coverage_road_cells_pct",
        help="Primary coverage metric for documentation (default: coverage_road_cells_pct)",
    )
    args = ap.parse_args()

    reports_dir = (REPO_ROOT / args.reports_dir).resolve()
    out_data = Path(args.output_data)
    if not out_data.is_absolute():
        out_data = (REPO_ROOT / out_data).resolve()
    out_fig = Path(args.output_figures)
    if not out_fig.is_absolute():
        out_fig = (REPO_ROOT / out_fig).resolve()
    out_data.mkdir(parents=True, exist_ok=True)
    out_fig.mkdir(parents=True, exist_ok=True)
    heat_dir = out_fig / "spatial_heatmaps"
    heat_dir.mkdir(parents=True, exist_ok=True)

    if args.manifest:
        mf = Path(args.manifest)
        if not mf.is_absolute():
            mf = (REPO_ROOT / mf).resolve()
    else:
        mf = (REPO_ROOT / "scenarios" / args.corpus / "manifest.csv").resolve()

    corpus_name = args.settings_corpus or args.corpus
    corpus_dir = (REPO_ROOT / "scenarios" / corpus_name).resolve() if corpus_name.lower() != "none" else None

    scenarios: list[str] = []
    meta: pd.DataFrame | None = None
    if mf.is_file():
        meta = load_manifest(mf)
        scenarios = meta["scenario_name"].astype(str).tolist()
    elif args.corpus.lower() != "none" and corpus_dir and corpus_dir.is_dir():
        scenarios = scenario_list_from_corpus(corpus_dir)
    else:
        print(f"Warning: corpus dir not found: {corpus_dir}", file=sys.stderr)

    if not scenarios:
        print("No scenarios to process (provide --manifest or a valid --corpus).", file=sys.stderr)
        return 1

    subset_filter = bool(args.name_regex)
    if args.name_regex:
        rx = re.compile(args.name_regex)
        scenarios = [s for s in scenarios if rx.search(s)]
        if not scenarios:
            print(f"No scenarios match --name-regex: {args.name_regex!r}", file=sys.stderr)
            return 1
        print(f"Filtered to {len(scenarios)} scenario(s) via --name-regex")

    fam_filter: set[str] | None = None
    if args.families:
        fam_filter = {x.strip() for x in args.families.split(",") if x.strip()}

    metrics_rows: list[dict] = []
    ts_parts: list[pd.DataFrame] = []
    processed = 0
    skipped = 0
    ts_replay_ok = 0
    ts_replay_missing = 0

    meta_by_name: dict[str, dict] = {}
    if meta is not None:
        for _, row in meta.iterrows():
            meta_by_name[str(row["scenario_name"])] = row.to_dict()

    for scenario in scenarios:
        if fam_filter is not None and meta is not None:
            row0 = meta_by_name.get(scenario)
            if not row0 or str(row0.get("family", "")) not in fam_filter:
                continue
        paths = spatial_occupancy_io.find_spatial_artifacts(reports_dir, scenario)
        g = paths["grid"]
        if g is None:
            skipped += 1
            continue

        mrow = meta_by_name.get(scenario) if meta is not None else None
        settings_path = resolve_settings_path(scenario, mrow, corpus_dir)
        summary = paths["summary"]

        wx = wy = gs = None
        time_bin_size = 300.0
        if summary is not None and summary.is_file():
            try:
                with summary.open(newline="", encoding="utf-8") as f:
                    sr0 = next(csv.DictReader(f), None)
                if sr0:
                    wx = float(sr0.get("world_x", "nan"))
                    wy = float(sr0.get("world_y", "nan"))
                    gs = int(float(sr0.get("grid_size", "50")))
                    time_bin_size = float(sr0.get("time_bin_size", "300"))
            except (OSError, ValueError, TypeError):
                pass

        metrics: dict[str, float | int | str | None] = {}
        masks = None
        if wx and wy and gs:
            masks, _map_name = masks_for_scenario(
                settings_path, world_x=wx, world_y=wy, grid_size=gs
            )
            metrics = metrics_for_scenario(
                g,
                settings_path,
                scenario_name=scenario,
                world_x=wx,
                world_y=wy,
                grid_size=gs,
            )

        if not args.skip_heatmaps:
            heatmap_for_scenario(
                g,
                heat_dir / f"{scenario}.png",
                summary_csv=summary,
                settings_path=settings_path,
                metrics=metrics,
                masks=masks,
                layout=args.heatmap_layout,
                zoom_mode=args.zoom_mode,
                log_scale=not args.heatmap_linear,
                show_roads=not args.heatmap_no_roads,
                show_underlay=not args.heatmap_no_underlay,
            )

        row_m: dict = {"scenario": scenario}
        if meta is not None and scenario in meta_by_name:
            m = meta_by_name[scenario]
            row_m["family"] = m.get("family", "")
            row_m["scenario_base"] = m.get("scenario_base", "")
            row_m["traffic_profile_id"] = m.get("traffic_profile_id", "")
            row_m["Scenario.endTime"] = m.get("Scenario.endTime", "")

        ctx = build_map_context(settings_path, load_roads=False)
        row_m["map_dataset"] = ctx.dataset or metrics.get("map_name", "")

        if summary is not None and summary.is_file():
            with summary.open(newline="", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for sr in r:
                    row_m.update(
                        {
                            "final_coverage_pct": sr.get("final_coverage_pct", ""),
                            "cells_visited_pct": sr.get("final_coverage_pct", ""),
                            "time_to_50pct": sr.get("time_to_50pct", ""),
                            "time_to_80pct": sr.get("time_to_80pct", ""),
                            "time_to_90pct": sr.get("time_to_90pct", ""),
                        }
                    )
        for key, val in metrics.items():
            if key != "scenario_name":
                row_m[key] = val
        if metrics.get("coverage_world_pct") is not None:
            row_m["final_coverage_pct"] = metrics["coverage_world_pct"]
            row_m["cells_visited_pct"] = metrics["coverage_world_pct"]
        if metrics.get("grid_size") is not None:
            row_m["grid_size"] = metrics["grid_size"]
        if metrics.get("world_width") is not None:
            row_m["world_x"] = metrics["world_width"]
        if metrics.get("world_height") is not None:
            row_m["world_y"] = metrics["world_height"]
        metrics_rows.append(row_m)

        ts = paths["coverage_timeseries"]
        node_pos = paths.get("node_positions")
        if ts is not None and ts.is_file():
            df_ts = pd.read_csv(ts)
            if "coverage_pct" in df_ts.columns and "coverage_world_pct" not in df_ts.columns:
                df_ts = df_ts.rename(columns={"coverage_pct": "coverage_world_pct"})
            if masks is not None and node_pos is not None and node_pos.is_file():
                et = None
                if meta is not None and scenario in meta_by_name:
                    try:
                        et = float(meta_by_name[scenario].get("Scenario.endTime", "") or 0)
                    except (TypeError, ValueError):
                        et = None
                df_ts = enrich_timeseries_from_positions(
                    df_ts,
                    node_pos,
                    masks,
                    time_bin_size=time_bin_size,
                    end_time=et if et and et > 0 else None,
                )
                ts_replay_ok += 1
            else:
                ts_replay_missing += 1
            df_ts.insert(0, "scenario", scenario)
            ts_parts.append(df_ts)
        processed += 1

    metrics_path = out_data / "spatial_occupancy_metrics.csv"
    metrics_df = pd.DataFrame(metrics_rows)
    if subset_filter and metrics_path.is_file() and not metrics_df.empty:
        old = pd.read_csv(metrics_path)
        updated = set(metrics_df["scenario"].astype(str))
        old = old[~old["scenario"].astype(str).isin(updated)]
        metrics_df = pd.concat([old, metrics_df], ignore_index=True)
    metrics_df.to_csv(metrics_path, index=False)

    ts_path = out_data / "spatial_coverage_timeseries.csv"
    if ts_parts:
        ts_new = pd.concat(ts_parts, ignore_index=True)
        if subset_filter and ts_path.is_file():
            old_ts = pd.read_csv(ts_path)
            updated = set(ts_new["scenario"].astype(str))
            old_ts = old_ts[~old_ts["scenario"].astype(str).isin(updated)]
            ts_new = pd.concat([old_ts, ts_new], ignore_index=True)
        ts_new.to_csv(ts_path, index=False)

    fam_curves: dict[str, list[np.ndarray]] = {}
    ts_for_curves: pd.DataFrame | None = None
    if ts_path.is_file():
        ts_for_curves = pd.read_csv(ts_path)
    elif ts_parts:
        ts_for_curves = pd.concat(ts_parts, ignore_index=True)

    if ts_for_curves is not None and meta is not None and not ts_for_curves.empty:
        ts_all = ts_for_curves
        end_map: dict[str, float] = {}
        fam_map: dict[str, str] = {}
        for scen, mr in meta_by_name.items():
            et = mr.get("Scenario.endTime")
            try:
                end_map[scen] = float(et) if et is not None and str(et) != "" else float("nan")
            except (TypeError, ValueError):
                end_map[scen] = float("nan")
            fam_map[scen] = str(mr.get("family", "unknown"))

        grid = np.linspace(0, 1, 101)
        for scen, gdf in ts_all.groupby("scenario"):
            gdf = gdf.sort_values("time_bin_end")
            et = end_map.get(scen, float("nan"))
            if not (et > 0) and scen in meta_by_name:
                sp = REPO_ROOT / str(meta_by_name[scen].get("settings_file", ""))
                et2 = parse_end_time_from_settings(sp)
                et = float(et2) if et2 else float("nan")
            if not (et > 0):
                continue
            tn = gdf["time_bin_end"].to_numpy(dtype=float) / et
            cov_col = (
                "coverage_road_cells_pct"
                if "coverage_road_cells_pct" in gdf.columns
                else "coverage_world_pct"
                if "coverage_world_pct" in gdf.columns
                else "coverage_pct"
            )
            cov = gdf[cov_col].to_numpy(dtype=float)
            if len(tn) < 2:
                continue
            yi = np.interp(grid, tn, cov, left=cov[0], right=cov[-1])
            fam = fam_map.get(scen, "unknown")
            fam_curves.setdefault(fam, []).append(yi)

        if fam_curves:
            fig, ax = plt.subplots(figsize=(8, 5))
            for fam, arrs in sorted(fam_curves.items()):
                if fam_filter is not None and fam not in fam_filter:
                    continue
                stack = np.vstack(arrs)
                mean = stack.mean(axis=0)
                p25 = np.percentile(stack, 25, axis=0)
                p75 = np.percentile(stack, 75, axis=0)
                ax.plot(grid, mean, label=fam)
                ax.fill_between(grid, p25, p75, alpha=0.2)
            ax.set_xlabel("time / Scenario.endTime")
            ax.set_ylabel("coverage_road_cells_pct (or world fallback)")
            ax.set_title("Spatial coverage by family (mean ± p25–p75)")
            ax.legend(fontsize=8, ncol=2)
            ax.set_xlim(0, 1)
            fig.tight_layout()
            fig.savefig(out_fig / "spatial_occupancy_curves_by_family.png", dpi=140)
            plt.close(fig)

    from lib.report_paths import SPATIAL_OCCUPANCY_ANALYSIS_SUMMARY

    report_path = SPATIAL_OCCUPANCY_ANALYSIS_SUMMARY
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        "\n".join(
            [
                "# Spatial occupancy analysis (generated)",
                "",
                f"- Reports directory: `{reports_dir}`",
                f"- Scenarios processed: {processed}",
                f"- Skipped (missing grid CSV): {skipped}",
                f"- Timeseries replay (NodePositionReport): {ts_replay_ok} ok, {ts_replay_missing} world-only",
                f"- Primary metric: `{args.primary_metric}`",
                f"- Zoom mode: `{args.zoom_mode}`",
                f"- Metrics: `{out_data / 'spatial_occupancy_metrics.csv'}`",
                f"- Long timeseries: `{out_data / 'spatial_coverage_timeseries.csv'}`",
                f"- Heatmaps: `{heat_dir}` (WKT roads + optional underlay PNG, log scale, dual layout)",
                f"- Family curves: `{out_fig / 'spatial_occupancy_curves_by_family.png'}`",
                "",
                "Methodology: [spatial_occupancy_report.md](spatial_occupancy_report.md).",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote metrics and figures; summary: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
