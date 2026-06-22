#!/usr/bin/env python3
"""
generate_scenario_space_v1.py

Generate structural scenario candidates and .settings files for scenario_space_v1.

Reference: scenarios/the_one_settings_reference_node_mobility_messages.md

Usage:
    # Estimate design space size
    python3 scenarios/setup/generate_scenario_space_v1.py --estimate-only

    # Brute-force full valid grid + write all .settings (N ≈ 100,800)
    python3 scenarios/setup/generate_scenario_space_v1.py --generate --sampling full --force

    # Cap output (e.g. first 5000 valid combinations)
    python3 scenarios/setup/generate_scenario_space_v1.py --generate --sampling full --max-settings 5000 --force
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterator

import yaml

# Allow import from scenarios/setup/
_SETUP = Path(__file__).resolve().parent
if str(_SETUP) not in sys.path:
    sys.path.insert(0, str(_SETUP))

from scenario_space_settings_builder import (  # noqa: E402
    ScenarioParam,
    build_settings_content,
    is_candidate_runnable,
    load_maps_from_manifest,
    load_maps_index,
    write_settings_file,
)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

REPO_ROOT = _SETUP.parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "scenarios" / "scenario_space_v1"
DEFAULT_DESIGN_SPACE = REPO_ROOT / "scenarios" / "analysis" / "config" / "scenario_design_space_v1.yaml"


class DesignSpace:
    """Load discrete parameter ranges from YAML."""

    def __init__(self, yaml_path: Path, maps_manifest: Path | None = None):
        logger.info("Loading design space from %s", yaml_path)
        with yaml_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.spec = data["design_space_v1"]
        if maps_manifest and maps_manifest.is_file():
            logger.info("Loading maps from manifest %s", maps_manifest)
            self.maps, self.maps_index = load_maps_from_manifest(maps_manifest)
        else:
            self.maps = {m["id"]: m for m in self.spec["maps"]}
            self.maps_index = load_maps_index()
        self.models = {m["model_name"]: m for m in self.spec["movement_models"]}
        self.node_populations = self.spec["node_population"]["discrete_values"]
        self.end_times = [d["value"] for d in self.spec["simulation_duration"]["discrete_values"]]
        self.group_structures = [g["structure_id"] for g in self.spec["group_structure"]["types"]]
        self.transmit_ranges = self.spec["network_parameters"]["transmit_range"]["discrete_values"]
        self.buffer_sizes = self.spec["network_parameters"]["buffer_size"]["discrete_values"]
        self.routers = self.spec["network_parameters"]["router"]["discrete_values"]

    def is_valid_map_model_pair(self, map_id: str, model_name: str) -> bool:
        allowed = self.maps.get(map_id, {}).get("allowed_movement_models", [])
        return model_name in allowed

    def estimate_space_size(self) -> dict:
        n_maps = len(self.maps)
        n_models = len(self.models)
        dims = (
            len(self.node_populations)
            * len(self.end_times)
            * len(self.group_structures)
            * len(self.transmit_ranges)
            * len(self.buffer_sizes)
            * len(self.routers)
        )
        valid_pairs = sum(
            1
            for map_id in self.maps
            for model_name in self.models
            if self.is_valid_map_model_pair(map_id, model_name)
        )
        brute = n_maps * n_models * dims
        valid_total = valid_pairs * dims
        breakdown_by_map = {}
        for map_id in self.maps:
            n_vm = sum(
                1 for model_name in self.models if self.is_valid_map_model_pair(map_id, model_name)
            )
            breakdown_by_map[map_id] = {
                "valid_models": n_vm,
                "total_combinations": n_vm * dims,
            }
        breakdown_by_model = {}
        for model_name in self.models:
            n_vm = sum(
                1 for map_id in self.maps if self.is_valid_map_model_pair(map_id, model_name)
            )
            breakdown_by_model[model_name] = {
                "valid_maps": n_vm,
                "total_combinations": n_vm * dims,
            }
        return {
            "n_maps": n_maps,
            "n_models": n_models,
            "n_node_populations": len(self.node_populations),
            "n_end_times": len(self.end_times),
            "n_group_structures": len(self.group_structures),
            "n_transmit_ranges": len(self.transmit_ranges),
            "n_buffer_sizes": len(self.buffer_sizes),
            "n_routers": len(self.routers),
            "total_brute_force": brute,
            "valid_map_model_pairs": valid_pairs,
            "total_valid_combinations": valid_total,
            "breakdown_by_map": breakdown_by_map,
            "breakdown_by_model": breakdown_by_model,
        }


class CandidateGenerator:
    """Enumerate or sample the design space."""

    def __init__(self, design_space: DesignSpace, seed: int = 42):
        self.ds = design_space
        self.seed = seed
        random.seed(seed)
        self._counter = 0
        self._param_counter = 0

    def _make_param(
        self,
        map_id: str,
        model_name: str,
        n_hosts: int,
        end_time: int,
        group_struct: str,
        transmit_range: int,
        buffer_size: str,
        router: str,
    ) -> ScenarioParam:
        p = ScenarioParam(
            map_id=map_id,
            movement_model=model_name,
            n_hosts=n_hosts,
            end_time=end_time,
            group_structure=group_struct,
            transmit_range=transmit_range,
            buffer_size=buffer_size,
            router=router,
            rng_seed=1000 + self._counter,
            scenario_index=self._counter,
            param_id=f"P{self._param_counter:05d}",
        )
        self._counter += 1
        self._param_counter += 1
        return p

    def iter_candidates(
        self,
        sampling: str,
        max_count: int,
    ) -> Iterator[ScenarioParam]:
        """Yield runnable candidates. max_count=0 means unlimited."""
        if sampling == "full":
            yield from self._iter_full_grid(max_count)
        elif sampling == "random":
            yield from self._iter_random(max_count or 3000)
        elif sampling == "stratified":
            yield from self._iter_stratified(max_count or 3000)
        else:
            raise ValueError(f"Unknown sampling: {sampling}")

    def _iter_full_grid(self, max_count: int) -> Iterator[ScenarioParam]:
        """Brute-force Cartesian product over all valid map×model pairs."""
        for map_id in sorted(self.ds.maps):
            for model_name in sorted(self.ds.models):
                if not self.ds.is_valid_map_model_pair(map_id, model_name):
                    continue
                for n_hosts in self.ds.node_populations:
                    for end_time in self.ds.end_times:
                        for group_struct in self.ds.group_structures:
                            for transmit_range in self.ds.transmit_ranges:
                                for buffer_size in self.ds.buffer_sizes:
                                    for router in self.ds.routers:
                                        param = self._make_param(
                                            map_id,
                                            model_name,
                                            n_hosts,
                                            end_time,
                                            group_struct,
                                            transmit_range,
                                            buffer_size,
                                            router,
                                        )
                                        ok, _ = is_candidate_runnable(param, self.ds.maps_index)
                                        if not ok:
                                            continue
                                        yield param
                                        if max_count > 0 and self._counter >= max_count:
                                            return

    def _iter_random(self, max_count: int) -> Iterator[ScenarioParam]:
        attempts = 0
        limit = max_count * 20
        while self._counter < max_count and attempts < limit:
            attempts += 1
            map_id = random.choice(list(self.ds.maps.keys()))
            allowed = [
                m
                for m in self.ds.models
                if self.ds.is_valid_map_model_pair(map_id, m)
            ]
            if not allowed:
                continue
            param = self._make_param(
                map_id,
                random.choice(allowed),
                random.choice(self.ds.node_populations),
                random.choice(self.ds.end_times),
                random.choice(self.ds.group_structures),
                random.choice(self.ds.transmit_ranges),
                random.choice(self.ds.buffer_sizes),
                random.choice(self.ds.routers),
            )
            ok, _ = is_candidate_runnable(param, self.ds.maps_index)
            if ok:
                yield param

    def _iter_stratified(self, max_count: int) -> Iterator[ScenarioParam]:
        per_map = max(1, max_count // len(self.ds.maps))
        for map_id in sorted(self.ds.maps):
            allowed = [
                m
                for m in self.ds.models
                if self.ds.is_valid_map_model_pair(map_id, m)
            ]
            if not allowed:
                continue
            n = 0
            for model_name in allowed:
                for n_hosts in self.ds.node_populations:
                    if n >= per_map:
                        break
                    param = self._make_param(
                        map_id,
                        model_name,
                        n_hosts,
                        random.choice(self.ds.end_times),
                        random.choice(self.ds.group_structures),
                        random.choice(self.ds.transmit_ranges),
                        random.choice(self.ds.buffer_sizes),
                        random.choice(self.ds.routers),
                    )
                    ok, _ = is_candidate_runnable(param, self.ds.maps_index)
                    if ok:
                        yield param
                        n += 1
                if n >= per_map:
                    break
            if self._counter >= max_count:
                return


def write_outputs(
    candidates: list[ScenarioParam],
    output_dir: Path,
    maps_index: dict,
    *,
    write_settings: bool,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    settings_root = output_dir / "settings"

    manifest_path = output_dir / "manifest.csv"
    fieldnames = [
        "candidate_id",
        "param_id",
        "scenario_name",
        "settings_file",
        "map_id",
        "map_archetype",
        "source_type",
        "anchor_id",
        "generator_type",
        "road_density",
        "gridness_score",
        "partition_score",
        "movement_model",
        "n_hosts",
        "end_time_s",
        "end_time_hours",
        "group_structure",
        "transmit_range_m",
        "buffer_size",
        "router",
        "rng_seed",
        "scenario_index",
    ]

    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, cand in enumerate(candidates):
            settings_rel = ""
            if write_settings:
                content = build_settings_content(cand, maps_index)
                path = write_settings_file(cand, content, settings_root)
                settings_rel = str(path.relative_to(REPO_ROOT / "scenarios")).replace("\\", "/")
            if (i + 1) % 5000 == 0:
                logger.info("  Written %d / %d", i + 1, len(candidates))
            writer.writerow(
                {
                    "candidate_id": cand.candidate_id,
                    "param_id": cand.param_id,
                    "scenario_name": cand.scenario_name,
                    "settings_file": settings_rel,
                    "map_id": cand.map_id,
                    "map_archetype": maps_index.get(cand.map_id, {}).get("map_archetype", ""),
                    "source_type": maps_index.get(cand.map_id, {}).get("source_type", ""),
                    "anchor_id": maps_index.get(cand.map_id, {}).get("anchor_id", ""),
                    "generator_type": maps_index.get(cand.map_id, {}).get("generator_type", ""),
                    "road_density": maps_index.get(cand.map_id, {}).get("road_density", ""),
                    "gridness_score": maps_index.get(cand.map_id, {}).get("gridness_score", ""),
                    "partition_score": maps_index.get(cand.map_id, {}).get("partition_score", ""),
                    "movement_model": cand.movement_model,
                    "n_hosts": cand.n_hosts,
                    "end_time_s": cand.end_time,
                    "end_time_hours": f"{cand.end_time / 3600:.1f}",
                    "group_structure": cand.group_structure,
                    "transmit_range_m": cand.transmit_range,
                    "buffer_size": cand.buffer_size,
                    "router": cand.router,
                    "rng_seed": cand.rng_seed,
                    "scenario_index": cand.scenario_index,
                }
            )

    logger.info("Manifest: %s (%d rows)", manifest_path, len(candidates))
    if write_settings:
        logger.info("Settings: %s (%d files)", settings_root, len(candidates))


def estimate_only(args: argparse.Namespace, ds: DesignSpace) -> None:
    est = ds.estimate_space_size()
    print("\n" + "=" * 70)
    print("DESIGN SPACE SIZE ESTIMATION")
    print("=" * 70)
    print(f"Valid map-model pairs: {est['valid_map_model_pairs']}")
    print(f"Total valid combinations (brute force): {est['total_valid_combinations']:,}")
    print(f"Brute-force (no map-model filter): {est['total_brute_force']:,}")
    for map_id, b in sorted(est["breakdown_by_map"].items()):
        print(f"  {map_id:28s} {b['total_combinations']:>9,}")
    print("=" * 70)
    out = Path(args.output_dir) / "scenario_space_v1_size_estimate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(est, f, indent=2)
    logger.info("Saved %s", out)


def dry_run(args: argparse.Namespace, ds: DesignSpace) -> None:
    gen = CandidateGenerator(ds, seed=args.seed)
    samples = list(gen.iter_candidates(args.sampling, args.max_settings))
    print(f"\nWould generate {len(samples)} runnable candidates")
    for cand in samples[:10]:
        print(
            f"  {cand.candidate_id} | {cand.map_id:22s} | {cand.movement_model:28s} | "
            f"hosts={cand.n_hosts:3d} | {cand.end_time/3600:.1f}h | {cand.group_structure}"
        )
    if len(samples) > 10:
        print(f"  ... and {len(samples) - 10} more")


def generate(args: argparse.Namespace, ds: DesignSpace) -> None:
    est = ds.estimate_space_size()
    expected = est["total_valid_combinations"]
    if args.max_settings == 0:
        logger.info("Brute-force mode: generating all runnable combinations (~%s)", f"{expected:,}")
    elif args.max_settings > 100_000 and not args.force:
        logger.error("Use --force for max-settings > 100000")
        sys.exit(1)

    gen = CandidateGenerator(ds, seed=args.seed)
    logger.info("Enumerating candidates (sampling=%s)...", args.sampling)
    candidates = list(gen.iter_candidates(args.sampling, args.max_settings))
    logger.info("Runnable candidates: %d", len(candidates))

    if not candidates:
        logger.error("No runnable candidates produced")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    write_outputs(
        candidates,
        output_dir,
        ds.maps_index,
        write_settings=not args.manifest_only,
    )

    print(f"\nGenerated {len(candidates)} scenarios in {output_dir}")
    if not args.manifest_only:
        print(f"  .settings → {output_dir / 'settings'}/SV1_*.settings")


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate scenario_space_v1 (brute force + .settings)")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--estimate-only", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--generate", action="store_true")

    ap.add_argument("--design-space", type=Path, default=DEFAULT_DESIGN_SPACE)
    ap.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument(
        "--max-settings",
        type=int,
        default=0,
        help="Cap candidates (0 = unlimited, for --sampling full)",
    )
    ap.add_argument(
        "--sampling",
        choices=["full", "stratified", "random"],
        default="full",
        help="full = brute-force grid (default)",
    )
    ap.add_argument(
        "--maps-manifest",
        type=Path,
        default=None,
        help="Selected maps manifest (e.g. map_space_v1/selected_maps/manifest_maps_selected.csv)",
    )
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--force", action="store_true", help="Allow very large generation")
    ap.add_argument(
        "--manifest-only",
        action="store_true",
        help="Write manifest only, skip .settings files",
    )

    args = ap.parse_args()
    if not args.design_space.is_file():
        logger.error("Design space not found: %s", args.design_space)
        sys.exit(1)

    ds = DesignSpace(args.design_space, maps_manifest=args.maps_manifest)

    if args.estimate_only:
        estimate_only(args, ds)
    elif args.dry_run:
        dry_run(args, ds)
    else:
        generate(args, ds)


if __name__ == "__main__":
    main()
