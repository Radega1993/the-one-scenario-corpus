#!/usr/bin/env python3
"""GMS-v1 map generation CLI for map_space_revised_v2."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent
PACK_ROOT = SCRIPTS_DIR.parent
SCENARIOS_DIR = PACK_ROOT.parent
REPO_ROOT = SCENARIOS_DIR.parent
SETUP_DIR = SCENARIOS_DIR / "setup"

for p in (SCRIPTS_DIR, SETUP_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

DEFAULT_CONFIG = PACK_ROOT / "config" / "map_design_space.yaml"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")


def _is_revised_v2_config(path: Path) -> bool:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return isinstance(data, dict) and "map_design_space_revised_v2" in data


def run_dry_run(*, config_path: Path, seed: int, target_total: int, write_plan: bool) -> int:
    from map_generation.planner import run_dry_run

    plan = run_dry_run(
        design_space_path=config_path,
        global_seed=int(seed),
        target_total=int(target_total),
        write_plan=bool(write_plan),
    )
    logger.info(
        "GMS dry-run: candidates=%s seed=%s config_hash=%s critical=%s",
        len(plan.candidates),
        plan.seed,
        plan.config_hash,
        len(plan.critical_errors),
    )
    for src, n in plan.counts_by("source_type").items():
        logger.info("  source_type %s: %s", src, n)
    for issue in plan.issues:
        log_fn = logger.error if issue.severity == "CRITICAL" else logger.warning
        log_fn("[%s] %s: %s", issue.severity, issue.code, issue.message)
    return 1 if plan.critical_errors else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate map_space_revised_v2 (GMS-v1) candidates.")
    parser.add_argument("--design-space", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--config", type=Path, default=None, help="Alias for --design-space.")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--acquire-osm", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write-plan", action="store_true")
    parser.add_argument("--estimate-only", action="store_true", help="Alias for dry-run + write-plan.")
    parser.add_argument("--source", choices=["synthetic", "osm", "all"], default="all")
    parser.add_argument("--target-total", type=int, default=1600)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-downloads", type=int, default=0)
    parser.add_argument("--osm-timeout", type=int, default=180)
    parser.add_argument("--osm-pause", type=float, default=10.0)
    args = parser.parse_args()

    if args.config is not None:
        args.design_space = args.config

    if not _is_revised_v2_config(args.design_space):
        parser.error(f"Expected map_design_space_revised_v2 config, got {args.design_space}")

    target = int(args.target_total)
    if target <= 0:
        parser.error("--target-total must be > 0")

    if args.dry_run or args.estimate_only:
        raise SystemExit(
            run_dry_run(
                config_path=args.design_space,
                seed=int(args.seed),
                target_total=target,
                write_plan=True if (args.write_plan or args.dry_run or args.estimate_only) else False,
            )
        )

    mode_count = sum(bool(x) for x in (args.plan_only, args.acquire_osm, args.build, args.generate))
    if mode_count == 0:
        parser.error("Specify one of: --dry-run, --plan-only, --acquire-osm, --build, --generate")

    from map_generation.executor import run_revised_generation

    raise SystemExit(
        run_revised_generation(
            config_path=args.design_space,
            seed=int(args.seed),
            target_total=target,
            source=str(args.source),
            force=bool(args.force),
            max_osm_downloads=int(args.max_downloads),
            osm_timeout=int(args.osm_timeout),
            osm_pause=float(args.osm_pause),
            plan_only=bool(args.plan_only),
            acquire_osm=bool(args.acquire_osm),
            build=bool(args.build),
            generate=bool(args.generate),
        )
    )


if __name__ == "__main__":
    main()
