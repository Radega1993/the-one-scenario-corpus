#!/usr/bin/env python3
"""
Generate corpus_v3 plan and review reports from diagnosis + settings audit.

Does not copy or modify corpus_v2 settings.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO_ROOT = BASE.parent.parent

if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from lib.paths import DATA_DIR, REPORTS_ANALYSIS_DIR, REPO_ROOT as ROOT  # noqa: E402

MAP_PROFILES = [
    ("MAP01", "HelsinkiMedium", "Full WDM stack; worldSize = roads bbox + margin"),
    ("MAP02", "HelsinkiMedium", "Cropped world to roads bbox (urban benchmark)"),
    ("MAP03", "Manhattan", "Manhattan WKT; medium density grid"),
    ("MAP04", "Manhattan", "Cropped Manhattan core"),
    ("MAP05", "Synthetic_campus", "Single building cluster; no external WKT dependency"),
    ("MAP06", "Synthetic_rural", "Three-cluster RWP; large sparse world"),
    ("MAP07", "HelsinkiMedium", "Bus-only mobility overlay"),
    ("MAP08", "HelsinkiMedium", "Disaster shelters + erratic subset"),
    ("MAP09", "HelsinkiMedium", "Partition / mule bridge layout"),
    ("MAP10", "HelsinkiMedium", "Stress: tiny buffer + storm traffic only"),
]

STRESS_TP = {"TP10", "TP11", "TP12"}
EXTREME_TP = {"TP12"}


def _repo_path(s: str, repo: Path) -> Path:
    p = Path(s)
    return p if p.is_absolute() else repo / p


def _base_action(
    base_df,
    *,
    family: str,
    map_dataset: str,
    zero_frac: float,
    p0_frac: float,
    tp_diff: bool,
) -> tuple[str, str, str]:
    """Return (recommended_action, new_map_profile, benchmark_split)."""
    if zero_frac > 0.5 and p0_frac > 0.3:
        return "redesign_mobility", "MAP02", "diagnostic"
    if family in ("01_urban", "03_vehicles", "05_disaster") and map_dataset == "HelsinkiMedium":
        if p0_frac > 0.4:
            return "change_map", "MAP03", "main"
        return "adjust", "MAP02", "main"
    if family == "04_rural" and "RandomWaypoint" in str(base_df["movement_models"].iloc[0]):
        return "keep", "MAP06", "main"
    if family == "02_campus":
        if p0_frac > 0.35:
            return "adjust", "MAP05", "main"
        return "keep", "MAP05", "main"
    if family == "07_traffic":
        return "stress_only", "MAP10", "stress"
    if tp_diff:
        return "adjust", "MAP01", "main"
    return "keep", "MAP01", "main"


def build_corpus_v3_plan(diagnosis, settings_audit, repo: Path):
    import pandas as pd

    bases = diagnosis.groupby("scenario_base", as_index=False).agg(
        family=("family", "first"),
        map_dataset=("map_dataset", "first"),
        delivery_mean=("delivery_ratio", "mean"),
        delivery_std=("delivery_std_by_base", "first"),
        p0_count=("priority", lambda s: (s == "P0").sum()),
        n_tp=("tp", "count"),
    )
    sa = settings_audit.groupby("scenario_base").first().reset_index()
    bases = bases.merge(sa[["scenario_base", "movement_models"]], on="scenario_base", how="left")

    plan_rows = []
    for _, b in bases.iterrows():
        base = b["scenario_base"]
        sub = diagnosis[diagnosis["scenario_base"] == base]
        pf = sub["problem_flags"].fillna("")
        zero_n = pf.str.contains("ZERO_DELIVERY").sum()
        zero_frac = zero_n / max(len(sub), 1)
        p0_frac = b["p0_count"] / max(b["n_tp"], 1)
        tp_diff = bool((b.get("delivery_std") or 0) < 0.02)

        action, map_prof, split = _base_action(
            sub,
            family=str(b["family"]),
            map_dataset=str(b["map_dataset"]),
            zero_frac=zero_frac,
            p0_frac=p0_frac,
            tp_diff=tp_diff,
        )

        if str(b["family"]) == "07_traffic":
            split = "stress"
        elif zero_frac > 0.8 and pf.str.contains("STRUCTURAL_PARTITION_VALID").any():
            split = "diagnostic"

        for _, row in sub.iterrows():
            tp = str(row["tp"])
            old_sc = row["scenario"]
            new_sc = f"{base}__{tp}_v3"
            row_split = split
            row_action = action
            if tp in STRESS_TP and split == "main":
                row_split = "stress"
            if tp == "TP12":
                row_split = "diagnostic"
                row_action = "keep" if "STRUCTURAL_PARTITION_VALID" in str(row["problem_flags"]) else row_action
            if "EXTREME_OVERHEAD" in str(row["problem_flags"]) and tp == "TP04":
                row_action = "adjust"

            plan_rows.append(
                {
                    "scenario_base": base,
                    "family": b["family"],
                    "old_scenario": old_sc,
                    "new_scenario": new_sc,
                    "tp": tp,
                    "recommended_action": row_action,
                    "new_map_profile": map_prof,
                    "benchmark_split": row_split,
                    "status": "pending",
                    "priority_base": sub["priority"].mode().iloc[0] if not sub["priority"].mode().empty else "",
                    "problem_flags_sample": row["problem_flags"],
                }
            )

    return pd.DataFrame(plan_rows)


def write_map_profiles(maps_dir: Path, plan_csv_path: Path) -> None:
    import pandas as pd

    maps_dir.mkdir(parents=True, exist_ok=True)
    rows = [{"map_profile_id": m[0], "dataset": m[1], "description": m[2]} for m in MAP_PROFILES]
    pd.DataFrame(rows).to_csv(plan_csv_path, index=False)

    lines = [
        "# Map profiles (corpus_v3 specification)",
        "",
        "Synthetic profiles are **design targets** for v3 rebuild; no new OSM import in v1.",
        "",
        "| ID | dataset | description |",
        "|----|---------|-------------|",
    ]
    for m in MAP_PROFILES:
        lines.append(f"| **{m[0]}** | `{m[1]}` | {m[2]} |")
    lines.extend(
        [
            "",
            f"Plan CSV: `{plan_csv_path.relative_to(REPO_ROOT) if plan_csv_path.is_relative_to(REPO_ROOT) else plan_csv_path}`",
            "",
        ]
    )
    (maps_dir / "map_profiles.md").write_text("\n".join(lines), encoding="utf-8")


def write_mobility_review(diagnosis, settings_audit, path: Path) -> None:
    import pandas as pd

    by_base = (
        diagnosis.groupby(["family", "scenario_base"])
        .agg(
            delivery_mean=("delivery_ratio", "mean"),
            p0=("priority", lambda s: (s == "P0").sum()),
            flags=("problem_flags", lambda s: "|".join(s.dropna().unique()[:3])),
        )
        .reset_index()
    )
    mm = settings_audit.groupby("scenario_base")["movement_models"].first()

    lines = [
        "# Mobility realism review",
        "",
        "Per **scenario_base** (mobility from corpus_v1, unchanged in v2 except TP overlays).",
        "",
        "## Summary by family",
        "",
    ]
    for fam in sorted(diagnosis["family"].unique()):
        sub = by_base[by_base["family"] == fam]
        lines.append(f"### `{fam}` ({len(sub)} bases)")
        lines.append("")
        lines.append("| base | movement | mean delivery | P0 count |")
        lines.append("|------|----------|--------------:|---------:|")
        for _, r in sub.head(12).iterrows():
            mm_s = str(mm.get(r["scenario_base"], ""))[:60]
            lines.append(
                f"| `{r['scenario_base']}` | `{mm_s}` | {r['delivery_mean']:.3f} | {int(r['p0'])} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Findings",
            "",
            "- **WorkingDayMovement + HelsinkiMedium** dominates urban/vehicle/disaster bases; spatial coverage ~8–10% of world is expected but flags **MAP_UNDERUSED** vs full grid.",
            "- **Campus** bases use MapRoute/MovementSwitch; fewer map-dependency issues but **TP04_FewLarge** drives extreme overhead.",
            "- **Rural RWP** bases are the main non-Helsinki mobility diversity in v1; recommend **MAP06** cropped synthetic worlds for v3 main benchmark.",
            "- v3 should **decouple** mobility template, map profile, and TP overlay (see `corpus_v3_design.md`).",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_traffic_review(diagnosis, path: Path) -> None:
    import pandas as pd

    tp_agg = (
        diagnosis.groupby("tp")
        .agg(
            delivery_mean=("delivery_ratio", "mean"),
            delivery_std=("delivery_ratio", "std"),
            overhead_mean=("overhead_ratio", "mean"),
            drops_mean=("drop_ratio", "mean"),
            n=("scenario", "count"),
        )
        .reset_index()
        .sort_values("tp")
    )

    lines = [
        "# Traffic profile review",
        "",
        "Aggregated over all 720 scenarios (12 TP × 60 bases).",
        "",
        "| TP | mean delivery | std delivery | mean overhead | mean drops | n |",
        "|----|--------------:|-------------:|--------------:|-----------:|--:|",
    ]
    for _, r in tp_agg.iterrows():
        lines.append(
            f"| `{r['tp']}` | {r['delivery_mean']:.4f} | {r['delivery_std']:.4f} | "
            f"{r['overhead_mean']:.1f} | {r['drops_mean']:.1f} | {int(r['n'])} |"
        )

    diff_bases = diagnosis.groupby("scenario_base")["delivery_ratio"].std()
    low_diff = (diff_bases < 0.02).sum()
    lines.extend(
        [
            "",
            "## Differentiation",
            "",
            f"- Bases with delivery std < 0.02 across TP: **{low_diff}** / {len(diff_bases)} → flag `TP_NOT_DIFFERENTIATING`.",
            "- **TP04_FewLarge** and **TP10_Storm** show highest overhead/drops variance; keep in **stress** split, not main benchmark.",
            "- **TP12_GroupToGroup** intentionally zero cross-group delivery; label **diagnostic** / `STRUCTURAL_PARTITION_VALID`.",
            "- v3 main benchmark should use **TP01–TP08** with verified std ≥ 0.05 per base after rebuild.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_realism_rules(thresholds_path: Path, out_path: Path) -> None:
    text = thresholds_path.read_text(encoding="utf-8")
    lines = [
        "# Realism rules (pre-execution)",
        "",
        "Flags applied in `diagnose_scenarios.py` using thresholds below.",
        "",
        "```yaml",
        text.strip(),
        "```",
        "",
        "## Interpretation",
        "",
        "| Flag | Meaning |",
        "|------|---------|",
        "| `ZERO_DELIVERY` | No delivered messages; not explained by partition |",
        "| `STRUCTURAL_PARTITION_VALID` | TP12 / cross-group traffic; zero delivery expected |",
        "| `SATURATED_DELIVERY` | delivery ≥ 0.95 |",
        "| `EXTREME_OVERHEAD` | overhead > 100 |",
        "| `EXTREME_DROPS` | drop_ratio > 50 |",
        "| `ZERO_CONTACTS` | No encounters |",
        "| `MAP_UNDERUSED` | coverage_world_ratio < 0.12 |",
        "| `MAP_TOO_LARGE` | Accessible/world coverage ratio high or world >> roads |",
        "| `SINGLE_MAP_DEPENDENCY` | Corpus >90% HelsinkiMedium |",
        "| `TP_NOT_DIFFERENTIATING` | Per-base delivery std < 0.02 |",
        "",
        "Adjust thresholds in `data/realism_thresholds.yaml` after reviewing distributions.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_corpus_v3_design(plan_df, path: Path) -> None:
    main_bases = plan_df[plan_df["benchmark_split"] == "main"]["scenario_base"].nunique()
    stress_bases = plan_df[plan_df["benchmark_split"] == "stress"]["scenario_base"].nunique()
    lines = [
        "# Corpus v3 design",
        "",
        "## Goals",
        "",
        "1. **~40–50 main benchmark bases** with diversified maps (not only HelsinkiMedium).",
        "2. **Stress** subset (TP10, small buffers, critical TTL) clearly tagged.",
        "3. **Diagnostic / extreme** (TP12 partition, ZERO_CONTACTS controls) separated.",
        "4. Explicit separation: mobility (v1 base) / map profile / TP / protocol overlays.",
        "",
        "## Proposed splits (from plan generator)",
        "",
        f"- Main-tagged base×TP rows: **{len(plan_df[plan_df['benchmark_split'] == 'main'])}**",
        f"- Stress-tagged: **{len(plan_df[plan_df['benchmark_split'] == 'stress'])}**",
        f"- Diagnostic-tagged: **{len(plan_df[plan_df['benchmark_split'] == 'diagnostic'])}**",
        f"- Unique bases in main split: **{main_bases}**",
        f"- Unique bases in stress split: **{stress_bases}**",
        "",
        "## Map profiles",
        "",
        "See [`scenarios/maps/map_profiles.md`](../../maps/map_profiles.md) and `data/map_profile_plan.csv`.",
        "",
        "## Actions",
        "",
        "| Action | When |",
        "|--------|------|",
        "| `keep` | Base behaves; minor TP tuning only |",
        "| `adjust` | TP differentiation or traffic parameters |",
        "| `redesign_mobility` | >50% TP with non-structural ZERO_DELIVERY |",
        "| `change_map` | Helsinki-only urban/vehicle/disaster with spatial P0/P1 |",
        "| `stress_only` | Traffic family T* bases |",
        "| `exclude_main` | Do not include in main benchmark (manual filter in v3 build) |",
        "",
        "Implementation status: **proposal only** (`corpus_v3/` not populated).",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_recommendation(plan_df, diagnosis, path: Path) -> None:
    p0_bases = (
        diagnosis[diagnosis["priority"] == "P0"]
        .groupby("scenario_base")
        .size()
        .sort_values(ascending=False)
        .head(15)
    )
    change_map = plan_df[plan_df["recommended_action"] == "change_map"]["scenario_base"].unique()

    lines = [
        "# Corpus v3 recommendation (executive summary)",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Executive summary",
        "",
        "Corpus v2 (720 scenarios) was audited without modifying settings. Cross-metrics diagnosis shows:",
        "",
        "- **HelsinkiMedium** dominates (>90% bases) → diversify via MAP02–MAP04 in v3.",
        "- **MAP_UNDERUSED** on WDM urban scenarios is often structural (large `worldSize`); v3 should crop to roads bbox.",
        "- **TP04_FewLarge** and storm/critical TTL profiles belong in **stress**, not main benchmark.",
        "- **TP12** cross-group scenarios are valid **diagnostic** controls (zero delivery with contacts).",
        "",
        "## P0 correction priority",
        "",
        "| scenario_base | P0 scenario count |",
        "|---------------|------------------:|",
    ]
    for base, c in p0_bases.items():
        lines.append(f"| `{base}` | {c} |")

    lines.extend(
        [
            "",
            "## Map change candidates",
            "",
            ", ".join(f"`{b}`" for b in change_map[:20]),
            (" …" if len(change_map) > 20 else ""),
            "",
            "## Acceptance checklist",
            "",
            "- [x] `settings_audit.csv` / `.md` for 720 scenarios",
            "- [x] `scenario_diagnosis.csv` / `.md` with flags and priority",
            "- [x] `corpus_v3_plan.csv` with `status=pending` (no settings copied)",
            "- [x] Map profiles MAP01–MAP10 documented",
            "- [x] Mobility and traffic review reports",
            "- [x] `realism_rules.md` + `realism_thresholds.yaml`",
            "- [ ] Full spatial metrics on 720 scenarios (requires re-sim with SpatialOccupancyReport; 98 grids available today)",
            "- [ ] `corpus_v3/` settings generation (future work)",
            "",
            "## Next steps",
            "",
            "1. Build `scenarios/corpus_v3/` from `corpus_v3_plan.csv` (filter `benchmark_split=main`).",
            "2. Apply map profiles (crop worldSize, swap WKT paths).",
            "3. Re-run simulations and `diagnose_scenarios.py` to validate TP differentiation.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--diagnosis", default=str(DATA_DIR / "scenario_diagnosis.csv"))
    ap.add_argument("--settings-audit", default=str(DATA_DIR / "settings_audit.csv"))
    ap.add_argument("--thresholds", default=str(DATA_DIR / "realism_thresholds.yaml"))
    ap.add_argument("--repo-root", default=str(ROOT))
    args = ap.parse_args()

    import pandas as pd

    repo = Path(args.repo_root).resolve()
    diagnosis = pd.read_csv(_repo_path(args.diagnosis, repo))
    settings_audit = pd.read_csv(_repo_path(args.settings_audit, repo))
    th_path = _repo_path(args.thresholds, repo)

    plan_df = build_corpus_v3_plan(diagnosis, settings_audit, repo)
    plan_path = repo / "scenarios/analysis/data/corpus_v3_plan.csv"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_df.to_csv(plan_path, index=False)

    maps_dir = repo / "scenarios/maps"
    map_plan_csv = repo / "scenarios/analysis/data/map_profile_plan.csv"
    write_map_profiles(maps_dir, map_plan_csv)

    reports = repo / "scenarios/analysis/reports"
    write_mobility_review(diagnosis, settings_audit, reports / "mobility_realism_review.md")
    write_traffic_review(diagnosis, reports / "traffic_profile_review.md")
    write_realism_rules(th_path, reports / "realism_rules.md")
    write_corpus_v3_design(plan_df, reports / "corpus_v3_design.md")
    write_recommendation(plan_df, diagnosis, reports / "corpus_v3_recommendation.md")

    print(f"Wrote {plan_path} ({len(plan_df)} rows)")
    print(f"Wrote reports under {reports}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
