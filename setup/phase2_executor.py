#!/usr/bin/env python3
"""
Phase 2 Executor: analysis tasks for scenario_space_v1 (optional).

NOTE: .settings generation is now in:
  scenarios/setup/generate_scenario_space_v1.py
  scenarios/setup/scenario_space_settings_builder.py

Run brute-force generation:
  python3 scenarios/setup/generate_scenario_space_v1.py --generate --sampling full --force

This script retains validity/features/pruning helpers; Task 9 (corpus_v2) is removed.
"""

import csv
import json
import sys
import argparse
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Set
import numpy as np
import pandas as pd
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
SCENARIOS_DIR = REPO_ROOT / "scenarios"
MANIFEST_FILE = SCENARIOS_DIR / "scenario_space_v1" / "manifest_candidates.csv"
DESIGN_SPACE_FILE = SCENARIOS_DIR / "analysis" / "config" / "scenario_design_space_v1.yaml"
DATA_DIR = REPO_ROOT / "data"
OUTPUT_DIR = SCENARIOS_DIR / "scenario_space_v1"
PHASE2_DIR = OUTPUT_DIR / "phase2_outputs"

# Create phase2 output directory
PHASE2_DIR.mkdir(parents=True, exist_ok=True)

# Allowed movement models per map (from scenario_design_space_v1.yaml)
MAP_ALLOWED_MODELS = {
    "HelsinkiDowntown": ["WorkingDayMovement", "ShortestPathMapBasedMovement", "BusMovement"],
    "KumpulaCampus": ["ShortestPathMapBasedMovement"],
    "ManhattanMidtownGrid": ["ShortestPathMapBasedMovement", "MapRouteMovement", "BusMovement"],
    "NuuksioSparseTrails": ["ShortestPathMapBasedMovement", "MapRouteMovement"],
    "HelsinkiDisrupted": ["ShortestPathMapBasedMovement", "MapRouteMovement", "ClusterMovement"],
    "KallioCommunityCompact": ["ShortestPathMapBasedMovement", "MapRouteMovement"],
}

# Map → family directory (mirrors base_scenarios layout)
MAP_FAMILY = {
    "HelsinkiDowntown": "01_urban",
    "ManhattanMidtownGrid": "01_urban",
    "KumpulaCampus": "02_campus",
    "NuuksioSparseTrails": "04_rural",
    "HelsinkiDisrupted": "05_disaster",
    "KallioCommunityCompact": "06_social",
}

# Route / POI files per map (from data/ and base_scenarios conventions)
MAP_ASSETS = {
    "HelsinkiDowntown": {
        "wdm_route": "A_bus.wkt",
        "vehicle_route": "A_bus.wkt",
        "bus_route": "A_bus.wkt",
    },
    "ManhattanMidtownGrid": {
        "vehicle_route": "A_vehicle_route.wkt",
        "bus_route": "A_vehicle_route.wkt",
    },
    "NuuksioSparseTrails": {
        "vehicle_route": "A_ranger_patrol.wkt",
    },
    "HelsinkiDisrupted": {
        "vehicle_route": "A_emergency_route.wkt",
        "bus_route": "B_mule_route.wkt",
    },
    "KallioCommunityCompact": {
        "vehicle_route": "A_community_route.wkt",
        "bus_route": "A_community_route.wkt",
    },
}

GROUP_STRUCTURE_NGROUPS = {
    "single_homogeneous": 1,
    "pedestrian_transit": 2,
    "pedestrian_vehicle": 2,
    "pedestrian_shortestpath_heterogeneous": 2,
    "cluster_nomadic": 2,
}


def _format_size(val: int) -> str:
    """The ONE size syntax: 50k, 1M, etc."""
    if val >= 1_000_000:
        return f"{val // 1_000_000}M"
    if val >= 1_000:
        return f"{val // 1_000}k"
    return str(val)


@dataclass
class CandidateRow:
    """Single row from manifest"""
    candidate_id: str
    param_id: str
    map_id: str
    movement_model: str
    n_hosts: int
    end_time_s: int
    end_time_hours: float
    group_structure: str
    transmit_range_m: int
    buffer_size: str
    router: str
    rng_seed: int
    scenario_index: int


class Phase2Executor:
    """Orchestrates Phase 2 tasks 4-10"""
    
    def __init__(self, *, seed: int = 42):
        self.manifest_df = None
        self.design_space = None
        self.maps_index: Dict[str, dict] = {}
        self.validity_results = {}
        self.settings_files_created = []
        self.features_df = None
        self.pruned_indices = []
        self.rng_seed = seed
        np.random.seed(seed)
        
    def load_manifest(self):
        """Task 4 prep: Load manifest"""
        logger.info("Loading manifest_candidates.csv...")
        self.manifest_df = pd.read_csv(MANIFEST_FILE)
        logger.info(f"Loaded {len(self.manifest_df)} candidates")
        return self.manifest_df
    
    def load_design_space(self):
        """Build map index from data/*/metadata.json (no PyYAML required)."""
        logger.info("Loading map specs from data/*/metadata.json...")
        self.maps_index = {}
        for map_dir in sorted(DATA_DIR.iterdir()):
            if not map_dir.is_dir():
                continue
            meta_path = map_dir / "metadata.json"
            if not meta_path.is_file():
                continue
            with meta_path.open(encoding="utf-8") as f:
                meta = json.load(f)
            map_id = meta.get("name", map_dir.name)
            ws = meta.get("world_size", [1000, 1000])
            self.maps_index[map_id] = {
                "id": map_id,
                "world_size_x": int(ws[0]),
                "world_size_y": int(ws[1]),
                "wkt_path": f"data/{map_id}/roads.wkt",
                "allowed_movement_models": MAP_ALLOWED_MODELS.get(map_id, []),
            }
        logger.info(f"Loaded {len(self.maps_index)} map specs")
        self.design_space = {"maps_index": self.maps_index}
        return self.design_space

    def get_map_spec(self, map_id: str) -> dict:
        """Return normalized map spec (world size + wkt path)."""
        if not self.maps_index:
            self.load_design_space()
        m = self.maps_index[map_id]
        return {
            "world_x": m["world_size_x"],
            "world_y": m["world_size_y"],
            "map_file": m["wkt_path"],
        }

    def _map_data_dir(self, map_id: str) -> Path:
        return DATA_DIR / map_id

    def _resolve_route_file(self, map_id: str, movement_model: str) -> Path | None:
        """Resolve route WKT for MapRouteMovement / BusMovement / WDM."""
        map_dir = self._map_data_dir(map_id)
        if not map_dir.is_dir():
            return None

        assets = MAP_ASSETS.get(map_id, {})
        if movement_model == "WorkingDayMovement":
            rel = assets.get("wdm_route", "A_bus.wkt")
            p = map_dir / rel
            return p if p.is_file() else None

        key = "bus_route" if movement_model == "BusMovement" else "vehicle_route"
        rel = assets.get(key)
        if rel:
            p = map_dir / rel
            if p.is_file():
                return p

        # Fallback: first non-roads route-like WKT in map dir
        for p in sorted(map_dir.glob("*.wkt")):
            name = p.name.lower()
            if name == "roads.wkt":
                continue
            if any(tok in name for tok in ("route", "bus", "patrol", "shuttle", "mule")):
                return p
        return None
    
    # ========== TASK 4: VALIDITY CONSTRAINTS ==========
    
    def task_4_validity_constraints(self):
        """
        Task 4: Verify POI/route files exist for each candidate
        - Check WorkingDayMovement POI files
        - Check MapRouteMovement/BusMovement route files
        - Check ClusterMovement cluster bounds
        """
        logger.info("\n" + "="*60)
        logger.info("TASK 4: Validity Constraints")
        logger.info("="*60)
        
        self.load_manifest()
        self.load_design_space()

        validity_results = []
        invalid_count = 0
        
        for idx, row in self.manifest_df.iterrows():
            candidate = CandidateRow(**row.to_dict())
            status, reason = self._validate_candidate(candidate)
            
            validity_results.append({
                'candidate_id': candidate.candidate_id,
                'map_id': candidate.map_id,
                'movement_model': candidate.movement_model,
                'validity_status': status,
                'invalid_reason': reason if status == 'INVALID' else ''
            })
            
            if status == 'INVALID':
                invalid_count += 1
            
            if (idx + 1) % 500 == 0:
                logger.info(f"  Validated {idx+1}/{len(self.manifest_df)}...")
        
        # Save validity results
        validity_df = pd.DataFrame(validity_results)
        validity_csv = PHASE2_DIR / "task4_validity_results.csv"
        validity_df.to_csv(validity_csv, index=False)
        
        logger.info(f"\n✓ Task 4 Complete: {len(validity_results)} candidates checked")
        logger.info(f"  Valid: {len(validity_results) - invalid_count}")
        logger.info(f"  Invalid: {invalid_count}")
        logger.info(f"  Saved to: {validity_csv}")
        
        # Filter manifest to only valid candidates
        valid_mask = validity_df['validity_status'] == 'VALID'
        self.manifest_df = self.manifest_df[valid_mask.values].reset_index(drop=True)
        logger.info(f"  Proceeding with {len(self.manifest_df)} valid candidates to Task 5")
        
        return validity_df
    
    def _validate_candidate(self, candidate: CandidateRow) -> Tuple[str, str]:
        """Validate single candidate, return (status, reason)."""
        map_dir = self._map_data_dir(candidate.map_id)
        if not map_dir.is_dir():
            return ("INVALID", f"Map data directory missing: {map_dir}")

        if candidate.movement_model == "WorkingDayMovement":
            for fname in ("A_homes.wkt", "A_offices.wkt", "A_meetingspots.wkt"):
                if not (map_dir / fname).is_file():
                    return ("INVALID", f"POI file missing: {fname}")
            route = self._resolve_route_file(candidate.map_id, "WorkingDayMovement")
            if route is None:
                return ("INVALID", "WDM route file missing (expected A_bus.wkt or equivalent)")

        if candidate.movement_model in ("MapRouteMovement", "BusMovement"):
            route = self._resolve_route_file(candidate.map_id, candidate.movement_model)
            if route is None:
                return ("INVALID", f"No route file for {candidate.movement_model}")

        allowed = self.maps_index.get(candidate.map_id, {}).get("allowed_movement_models", [])
        if allowed and candidate.movement_model not in allowed:
            return ("INVALID", f"{candidate.movement_model} not allowed on {candidate.map_id}")

        if candidate.n_hosts < 1:
            return ("INVALID", "n_hosts must be positive")

        return ("VALID", "")
    
    # ========== TASK 5: GENERATE .SETTINGS FILES ==========
    
    def task_5_generate_settings(self):
        """
        Task 5: Generate .settings files from valid candidates
        - Create scenarios/scenario_space_v1/settings/{map_id}/SV1_*.settings
        - One .settings per candidate
        - Template-based generation
        """
        logger.info("\n" + "="*60)
        logger.info("TASK 5: Generate .settings Files")
        logger.info("="*60)
        
        # Ensure we have valid manifest
        if self.manifest_df is None or len(self.manifest_df) == 0:
            logger.warning("No valid candidates. Run Task 4 first.")
            return
        
        self.load_design_space()
        
        settings_dir = OUTPUT_DIR / "settings"
        settings_dir.mkdir(parents=True, exist_ok=True)
        
        created_count = 0
        failed_count = 0
        
        for idx, row in self.manifest_df.iterrows():
            candidate = CandidateRow(**row.to_dict())
            
            try:
                settings_content = self._generate_settings_content(candidate)
                settings_file = self._write_settings_file(candidate, settings_content, settings_dir)
                created_count += 1
                
                if (idx + 1) % 500 == 0:
                    logger.info(f"  Created {created_count} .settings files...")
                
            except Exception as e:
                logger.error(f"  Failed {candidate.candidate_id}: {e}")
                failed_count += 1
        
        logger.info(f"\n✓ Task 5 Complete: {created_count} .settings files created")
        logger.info(f"  Failed: {failed_count}")
        logger.info(f"  Output directory: {settings_dir}")
        
        self.settings_files_created = list(settings_dir.glob("**/*.settings"))
        
        return created_count
    
    def _generate_settings_content(self, candidate: CandidateRow) -> str:
        """Generate .settings file content"""
        
        map_spec = self.get_map_spec(candidate.map_id)
        world_x, world_y = map_spec["world_x"], map_spec["world_y"]
        map_file = map_spec["map_file"]
        
        # Get group structure details
        group_struct = self._parse_group_structure(candidate)
        
        # Header
        content = f"""# Scenario space v1: {candidate.candidate_id}
# Generated by: scenario_space_v1.py Phase 2 Task 5
# Map: {candidate.map_id} | Movement: {candidate.movement_model} | Hosts: {candidate.n_hosts}
# Design space parameter_id: {candidate.param_id}

Scenario.name = SV1_{candidate.candidate_id}
Scenario.simulateConnections = true
Scenario.updateInterval = 0.1
Scenario.endTime = {candidate.end_time_s}

MovementModel.rngSeed = {candidate.rng_seed}
MovementModel.worldSize = {world_x}, {world_y}
"""
        
        # Map configuration
        content += f"""
MapBasedMovement.nrofMapFiles = 1
MapBasedMovement.mapFile1 = {map_file}
"""
        
        # Default group parameters
        content += f"""
Group.bufferSize = {candidate.buffer_size}
Group.nrofInterfaces = 1
Group.interface1 = bt0
bt0.type = SimpleBroadcastInterface
bt0.transmitSpeed = 1M
bt0.transmitRange = {candidate.transmit_range_m}
Group.msgTtl = 7200
"""
        
        # Movement model specifics
        if candidate.movement_model == 'WorkingDayMovement':
            content += self._settings_working_day_movement(candidate, map_spec)
        elif candidate.movement_model == 'ShortestPathMapBasedMovement':
            content += self._settings_shortest_path(candidate)
        elif candidate.movement_model == 'MapRouteMovement':
            content += self._settings_map_route(candidate, map_spec)
        elif candidate.movement_model == 'BusMovement':
            content += self._settings_bus_movement(candidate, map_spec)
        elif candidate.movement_model == 'ClusterMovement':
            content += self._settings_cluster_movement(candidate, world_x, world_y)
        
        # Host groups
        content += self._generate_host_groups(candidate, group_struct)
        
        # Events (placeholder baseline)
        content += """
Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = 60, 120
Events1.size = 50k, 150k
Events1.hosts = 0, %d
Events1.prefix = M
""" % candidate.n_hosts
        
        # Reports
        content += """
Report.nrofReports = 2
Report.reportDir = reports/
Report.report1 = MessageStatsReport
Report.report2 = ContactTimesReport
"""
        
        return content
    
    def _settings_working_day_movement(self, candidate: CandidateRow, map_spec: Dict) -> str:
        """WorkingDayMovement group config."""
        route = self._resolve_route_file(candidate.map_id, "WorkingDayMovement")
        route_rel = str(route.relative_to(REPO_ROOT)).replace("\\", "/") if route else f"data/{candidate.map_id}/A_bus.wkt"
        speed_min, speed_max = 0.5, 1.5
        wait_min, wait_max = 0, 300

        return f"""
Group.movementModel = WorkingDayMovement
Group.speed = {speed_min}, {speed_max}
Group.waitTime = {wait_min}, {wait_max}
Group.homeLocationsFile = data/{candidate.map_id}/A_homes.wkt
Group.officeLocationsFile = data/{candidate.map_id}/A_offices.wkt
Group.meetingSpotsFile = data/{candidate.map_id}/A_meetingspots.wkt
Group.routeFile = {route_rel}
Group.nrOfOffices = 10
Group.officeSize = 50
"""
    
    def _settings_shortest_path(self, candidate: CandidateRow) -> str:
        """ShortestPathMapBasedMovement group config"""
        speed_min, speed_max = 0.5, 2.0
        wait_min, wait_max = 0, 600
        
        return f"""
Group.movementModel = ShortestPathMapBasedMovement
Group.speed = {speed_min}, {speed_max}
Group.waitTime = {wait_min}, {wait_max}
"""
    
    def _settings_map_route(self, candidate: CandidateRow, map_spec: Dict) -> str:
        """MapRouteMovement group config."""
        speed_min, speed_max = 5, 14
        wait_min, wait_max = 5, 60
        route = self._resolve_route_file(candidate.map_id, "MapRouteMovement")
        route_rel = str(route.relative_to(REPO_ROOT)).replace("\\", "/") if route else f"data/{candidate.map_id}/A_vehicle_route.wkt"

        return f"""
Group.movementModel = MapRouteMovement
Group.routeFile = {route_rel}
Group.routeType = 1
Group.speed = {speed_min}, {speed_max}
Group.waitTime = {wait_min}, {wait_max}
"""
    
    def _settings_bus_movement(self, candidate: CandidateRow, map_spec: Dict) -> str:
        """BusMovement group config."""
        speed_min, speed_max = 7, 10
        wait_min, wait_max = 10, 45
        route = self._resolve_route_file(candidate.map_id, "BusMovement")
        route_rel = str(route.relative_to(REPO_ROOT)).replace("\\", "/") if route else f"data/{candidate.map_id}/A_bus.wkt"

        return f"""
Group.movementModel = BusMovement
Group.routeFile = {route_rel}
Group.busControlSystemNr = 1
Group.speed = {speed_min}, {speed_max}
Group.waitTime = {wait_min}, {wait_max}
"""
    
    def _settings_cluster_movement(self, candidate: CandidateRow, world_x: int, world_y: int) -> str:
        """ClusterMovement group config"""
        speed_min, speed_max = 0.5, 2.0
        wait_min, wait_max = 0, 600
        cluster_x = world_x // 2
        cluster_y = world_y // 2
        cluster_range = min(world_x, world_y) // 4
        
        return f"""
Group.movementModel = ClusterMovement
Group.clusterCenter = {cluster_x}, {cluster_y}
Group.clusterRange = {cluster_range}
Group.speed = {speed_min}, {speed_max}
Group.waitTime = {wait_min}, {wait_max}
"""
    
    def _parse_group_structure(self, candidate: CandidateRow) -> Dict:
        """Map group_structure id to number of host groups."""
        n_groups = GROUP_STRUCTURE_NGROUPS.get(candidate.group_structure, 1)
        return {"type": candidate.group_structure, "n_groups": n_groups}
    
    def _generate_host_groups(self, candidate: CandidateRow, group_struct: Dict) -> str:
        """Generate host group configuration"""
        
        n_groups = group_struct['n_groups']
        hosts_per_group = candidate.n_hosts // n_groups
        remainder = candidate.n_hosts % n_groups
        
        content = f"\nScenario.nrofHostGroups = {n_groups}\n"
        
        group_ids = ['a', 'b', 'c', 'd', 'e', 'f'][:n_groups]
        
        for gi, group_id in enumerate(group_ids):
            n_hosts_in_group = hosts_per_group + (1 if gi < remainder else 0)
            
            content += f"""
Group{gi+1}.groupID = {group_id}
Group{gi+1}.nrofHosts = {n_hosts_in_group}
Group{gi+1}.movementModel = {candidate.movement_model}
Group{gi+1}.speed = 0.5, 2.0
Group{gi+1}.waitTime = 0, 600
Group{gi+1}.bufferSize = {candidate.buffer_size}
Group{gi+1}.router = {candidate.router}
Group{gi+1}.nrofInterfaces = 1
Group{gi+1}.interface1 = bt0
"""
        
        return content
    
    def _write_settings_file(self, candidate: CandidateRow, content: str, base_dir: Path) -> Path:
        """Write .settings flat (map is inside the file)."""
        base_dir.mkdir(parents=True, exist_ok=True)
        filename = f"SV1_{candidate.candidate_id}.settings"
        filepath = base_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath
    
    # ========== TASK 6: STATIC FEATURE EXTRACTION ==========
    
    def task_6_static_features(self):
        """
        Task 6: Extract static features from .settings without simulation
        """
        logger.info("\n" + "="*60)
        logger.info("TASK 6: Static Feature Extraction")
        logger.info("="*60)
        
        if not self.manifest_df is None:
            logger.info(f"Extracting features from {len(self.manifest_df)} candidates...")
            
            features = []
            for idx, row in self.manifest_df.iterrows():
                candidate = CandidateRow(**row.to_dict())
                feature_row = self._extract_features(candidate)
                features.append(feature_row)
                
                if (idx + 1) % 500 == 0:
                    logger.info(f"  Extracted {idx+1}/{len(self.manifest_df)}...")
            
            self.features_df = pd.DataFrame(features)
            features_csv = PHASE2_DIR / "task6_static_features.csv"
            self.features_df.to_csv(features_csv, index=False)
            
            logger.info(f"\n✓ Task 6 Complete: {len(features)} feature vectors")
            logger.info(f"  Columns: {len(self.features_df.columns)}")
            logger.info(f"  Saved to: {features_csv}")
            
            return self.features_df
        else:
            logger.error("No manifest loaded. Run Tasks 4-5 first.")
            return None
    
    def _extract_features(self, candidate: CandidateRow) -> Dict:
        """Extract static features from candidate"""
        return {
            'candidate_id': candidate.candidate_id,
            'map_id': candidate.map_id,
            'movement_model': candidate.movement_model,
            'n_hosts': candidate.n_hosts,
            'end_time_s': candidate.end_time_s,
            'end_time_hours': candidate.end_time_hours,
            'transmit_range_m': candidate.transmit_range_m,
            'buffer_size_mb': int(candidate.buffer_size.rstrip('M')),
            'router': candidate.router,
            'group_structure': candidate.group_structure,
        }
    
    # ========== TASK 7: FEATURE ANALYSIS ==========
    
    def task_7_feature_analysis(self):
        """
        Task 7: Analyze feature distributions and redundancy
        """
        logger.info("\n" + "="*60)
        logger.info("TASK 7: Feature Analysis & Diversity")
        logger.info("="*60)
        
        if self.features_df is None:
            logger.error("No features loaded. Run Task 6 first.")
            return
        
        # Summary stats
        logger.info(f"Feature space: {len(self.features_df)} scenarios × {len(self.features_df.columns)} features")
        logger.info("\nFeature distributions:")
        
        numeric_cols = ['n_hosts', 'end_time_s', 'transmit_range_m', 'buffer_size_mb']
        for col in numeric_cols:
            if col in self.features_df.columns:
                stats = self.features_df[col].describe()
                logger.info(f"  {col}: mean={stats['mean']:.1f}, std={stats['std']:.1f}, min={stats['min']}, max={stats['max']}")
        
        # Categorical distribution
        logger.info("\nCategorical distributions:")
        for col in ['map_id', 'movement_model', 'group_structure']:
            if col in self.features_df.columns:
                dist = self.features_df[col].value_counts()
                logger.info(f"  {col}: {dict(dist)}")
        
        logger.info(f"\n✓ Task 7 Complete: Feature analysis done")
        
        return self.features_df
    
    # ========== TASK 8: PRUNING ==========
    
    def task_8_pruning(self, n_pruned: int = 750):
        """
        Task 8: Select representative scenarios via k-medoids
        """
        logger.info("\n" + "="*60)
        logger.info(f"TASK 8: Pruning & Selection (target: {n_pruned} scenarios)")
        logger.info("="*60)
        
        if self.features_df is None:
            logger.error("No features loaded. Run Task 6 first.")
            return
        
        # For now, use stratified sampling: ensure all (map, model) pairs represented
        # Then fill remaining slots randomly
        
        pruned_indices = []
        grouped = self.features_df.groupby(['map_id', 'movement_model'])
        
        logger.info(f"Found {len(grouped)} (map, model) combinations")
        
        # Take ~min(5, len(group)) from each (map, model) pair
        samples_per_group = max(1, n_pruned // len(grouped))
        
        for (map_id, model), group_indices in grouped:
            available_indices = group_indices.index.tolist()
            n_sample = min(samples_per_group, len(available_indices))
            sampled = np.random.choice(available_indices, size=n_sample, replace=False)
            pruned_indices.extend(sampled.tolist())
        
        # Fill remaining slots
        all_indices = set(self.features_df.index)
        pruned_set = set(pruned_indices)
        remaining_indices = list(all_indices - pruned_set)
        
        n_remaining_slots = n_pruned - len(pruned_indices)
        if n_remaining_slots > 0 and len(remaining_indices) > 0:
            additional = np.random.choice(remaining_indices, size=min(n_remaining_slots, len(remaining_indices)), replace=False)
            pruned_indices.extend(additional.tolist())
        
        pruned_indices = sorted(pruned_indices)[:n_pruned]
        
        self.pruned_indices = pruned_indices
        pruned_df = self.features_df.iloc[pruned_indices]
        
        pruned_csv = PHASE2_DIR / "task8_pruned_indices.csv"
        pruned_df.to_csv(pruned_csv, index=False)
        
        logger.info(f"\n✓ Task 8 Complete: {len(pruned_indices)} scenarios selected")
        logger.info(f"  Saved to: {pruned_csv}")
        
        return pruned_indices
    
    # ========== TASK 9: TRAFFIC PROFILES ==========
    
    def task_9_traffic_profiles(self, n_profiles: int = 6):
        """
        Task 9: Apply traffic profiles to pruned scenarios
        Create N variants per scenario with different message generation patterns
        """
        logger.info("\n" + "="*60)
        logger.info(f"TASK 9: Apply Traffic Profiles ({n_profiles} profiles)")
        logger.info("="*60)
        
        if len(self.pruned_indices) == 0:
            logger.error("No pruned indices. Run Task 8 first.")
            return
        
        corpus_v2_dir = SCENARIOS_DIR / "corpus_v2"
        corpus_v2_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Creating corpus_v2 with {len(self.pruned_indices)} base scenarios × {n_profiles} profiles")
        logger.info(f"  Total output: {len(self.pruned_indices) * n_profiles} .settings files")
        
        corpus_v2_manifest = []
        created_count = 0
        
        traffic_profiles = self._define_traffic_profiles(n_profiles)
        
        for pruned_idx in self.pruned_indices:
            base_candidate = self.manifest_df.iloc[pruned_idx]
            candidate = CandidateRow(**base_candidate.to_dict())
            
            for profile in traffic_profiles:
                try:
                    settings_content = self._generate_settings_with_profile(candidate, profile)
                    settings_file = self._write_corpus_v2_settings(candidate, profile, settings_content, corpus_v2_dir)
                    
                    corpus_v2_manifest.append({
                        'family': self._classify_family(candidate.map_id),
                        'base_scenario': candidate.candidate_id,
                        'scenario_name': f"CV2_{candidate.candidate_id}_{profile['id']}",
                        'traffic_profile_id': profile['id'],
                        'traffic_profile_name': profile['name'],
                        'settings_file': settings_file.relative_to(SCENARIOS_DIR),
                        'map_id': candidate.map_id,
                        'n_hosts': candidate.n_hosts,
                        'movement_model': candidate.movement_model,
                    })
                    
                    created_count += 1
                    
                except Exception as e:
                    logger.error(f"  Failed {candidate.candidate_id} + {profile['id']}: {e}")
        
        # Save corpus_v2 manifest
        manifest_csv = corpus_v2_dir / "manifest.csv"
        manifest_df = pd.DataFrame(corpus_v2_manifest)
        manifest_df.to_csv(manifest_csv, index=False)
        
        logger.info(f"\n✓ Task 9 Complete: {created_count} .settings files created")
        logger.info(f"  corpus_v2 directory: {corpus_v2_dir}")
        logger.info(f"  Manifest: {manifest_csv}")
        
        return created_count
    
    def _define_traffic_profiles(self, n_profiles: int) -> List[Dict]:
        """Define traffic profile templates"""
        profiles = [
            {
                'id': 'TP01',
                'name': 'Baseline',
                'interval': (60, 120),
                'size': (50000, 150000),
                'msg_ttl': 7200,
                'description': 'Moderate message rate, moderate size'
            },
            {
                'id': 'TP02',
                'name': 'LowLoad',
                'interval': (300, 600),
                'size': (10000, 50000),
                'msg_ttl': 7200,
                'description': 'Low message rate, small messages'
            },
            {
                'id': 'TP03',
                'name': 'ManySmall',
                'interval': (30, 60),
                'size': (5000, 20000),
                'msg_ttl': 3600,
                'description': 'High rate, small messages'
            },
            {
                'id': 'TP04',
                'name': 'FewLarge',
                'interval': (300, 600),
                'size': (500000, 1000000),
                'msg_ttl': 14400,
                'description': 'Low rate, large messages'
            },
            {
                'id': 'TP05',
                'name': 'RealTime',
                'interval': (10, 30),
                'size': (100000, 200000),
                'msg_ttl': 600,
                'description': 'High rate, short TTL'
            },
            {
                'id': 'TP06',
                'name': 'DelayTolerant',
                'interval': (600, 1200),
                'size': (50000, 100000),
                'msg_ttl': 86400,
                'description': 'Low rate, long TTL'
            },
        ]
        
        return profiles[:n_profiles]
    
    def _generate_settings_with_profile(self, candidate: CandidateRow, profile: Dict) -> str:
        """Generate .settings with specific traffic profile"""
        
        map_spec = self.get_map_spec(candidate.map_id)
        world_x, world_y = map_spec["world_x"], map_spec["world_y"]
        map_file = map_spec["map_file"]
        
        group_struct = self._parse_group_structure(candidate)
        
        if self.design_space is None:
            self.load_design_space()
        
        # Base content (same as Task 5)
        content = f"""# corpus_v2: {candidate.candidate_id} + {profile['id']}_{profile['name']}
# {profile['description']}
# Generated by: Phase 2 Task 9
# Design space parameter_id: {candidate.param_id}

Scenario.name = CV2_{candidate.candidate_id}_{profile['id']}
Scenario.simulateConnections = true
Scenario.updateInterval = 0.1
Scenario.endTime = {candidate.end_time_s}

MovementModel.rngSeed = {candidate.rng_seed}
MovementModel.worldSize = {world_x}, {world_y}

MapBasedMovement.nrofMapFiles = 1
MapBasedMovement.mapFile1 = {map_file}

Group.bufferSize = {candidate.buffer_size}
Group.nrofInterfaces = 1
Group.interface1 = bt0
bt0.type = SimpleBroadcastInterface
bt0.transmitSpeed = 1M
bt0.transmitRange = {candidate.transmit_range_m}
Group.msgTtl = {profile['msg_ttl']}
"""
        
        # Movement model specifics
        if candidate.movement_model == 'WorkingDayMovement':
            content += self._settings_working_day_movement(candidate, map_spec)
        elif candidate.movement_model == 'ShortestPathMapBasedMovement':
            content += self._settings_shortest_path(candidate)
        elif candidate.movement_model == 'MapRouteMovement':
            content += self._settings_map_route(candidate, map_spec)
        elif candidate.movement_model == 'BusMovement':
            content += self._settings_bus_movement(candidate, map_spec)
        elif candidate.movement_model == 'ClusterMovement':
            content += self._settings_cluster_movement(candidate, world_x, world_y)
        
        # Host groups
        content += self._generate_host_groups(candidate, group_struct)
        
        # Traffic profile
        interval_min, interval_max = profile['interval']
        size_min, size_max = profile['size']
        
        content += f"""
Events.nrof = 1
Events1.class = MessageEventGenerator
Events1.interval = {interval_min}, {interval_max}
Events1.size = {_format_size(size_min)}, {_format_size(size_max)}
Events1.hosts = 0, {candidate.n_hosts}
Events1.prefix = M

Report.nrofReports = 2
Report.reportDir = reports/
Report.report1 = MessageStatsReport
Report.report2 = ContactTimesReport
"""
        
        return content
    
    def _write_corpus_v2_settings(self, candidate: CandidateRow, profile: Dict, content: str, base_dir: Path) -> Path:
        """Write corpus_v2 .settings file under family subdirectory."""
        family_dir_name = MAP_FAMILY.get(candidate.map_id, "99_mixed")
        family_dir = base_dir / family_dir_name
        family_dir.mkdir(parents=True, exist_ok=True)

        filename = f"CV2_{candidate.candidate_id}_{profile['id']}.settings"
        filepath = family_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath

    def _classify_family(self, map_id: str) -> str:
        """Classify map to family label (urban, campus, ...)."""
        folder = MAP_FAMILY.get(map_id, "99_mixed")
        return folder.split("_", 1)[-1] if "_" in folder else folder
    
    # ========== TASK 10: FINAL DOCUMENTATION ==========
    
    def task_10_final_documentation(self):
        """
        Task 10: Generate final documentation and validation
        """
        logger.info("\n" + "="*60)
        logger.info("TASK 10: Final Documentation & Validation")
        logger.info("="*60)
        
        # Count results
        corpus_v2_dir = SCENARIOS_DIR / "corpus_v2"
        if corpus_v2_dir.exists():
            settings_files = list(corpus_v2_dir.glob("**/*.settings"))
            logger.info(f"corpus_v2 created: {len(settings_files)} .settings files")
        
        # Create summary report
        settings_count = len(list((SCENARIOS_DIR / "scenario_space_v1" / "settings").glob("**/*.settings")))
        corpus_settings = list(corpus_v2_dir.glob("**/*.settings")) if corpus_v2_dir.exists() else []

        summary = f"""
# Phase 2 Execution Summary

**Generated**: {pd.Timestamp.now().isoformat()}

## Tasks Completed

- [x] Task 4: Validity Constraints
- [x] Task 5: Generate .settings Files
- [x] Task 6: Static Feature Extraction
- [x] Task 7: Feature Analysis & Diversity
- [x] Task 8: Pruning & Selection
- [x] Task 9: Apply Traffic Profiles
- [x] Task 10: Final Documentation

## Output Summary

- Candidates in manifest: {len(pd.read_csv(MANIFEST_FILE))}
- Valid after Task 4: {len(self.manifest_df) if self.manifest_df is not None else 'n/a'}
- Features extracted: {len(self.features_df) if self.features_df is not None else 0}
- Pruned scenarios: {len(self.pruned_indices)}
- scenario_space_v1 .settings: {settings_count}
- corpus_v2 scenarios: {len(corpus_settings)} (target: {len(self.pruned_indices)} × 6 traffic profiles)

## Outputs Location

- Phase 2 data: {PHASE2_DIR}
- Structural .settings: {SCENARIOS_DIR / 'scenario_space_v1' / 'settings'}
- corpus_v2: {corpus_v2_dir}

## Next Steps

1. Smoke-test a sample with The ONE (`run_all_scenarios.py --corpus corpus_v2 --name-regex 'CV2_C00001'`)
2. Run full simulation batch when validated
3. Extract dynamic features and compare diversity vs corpus_v1
"""
        
        summary_file = PHASE2_DIR / "PHASE2_SUMMARY.md"
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        logger.info(f"\n✓ Task 10 Complete: Documentation generated")
        logger.info(f"  Summary: {summary_file}")
        
        return summary_file
    
    # ========== ORCHESTRATION ==========
    
    def execute_all_tasks(self, *, n_pruned: int = 750, n_profiles: int = 6):
        """Execute all Phase 2 tasks sequentially."""
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 2 EXECUTION: Tasks 4-10")
        logger.info("=" * 80)

        try:
            self.task_4_validity_constraints()
            self.task_5_generate_settings()
            self.task_6_static_features()
            self.task_7_feature_analysis()
            self.task_8_pruning(n_pruned=n_pruned)
            self.task_9_traffic_profiles(n_profiles=n_profiles)
            self.task_10_final_documentation()
            
            logger.info("\n" + "="*80)
            logger.info("✅ PHASE 2 COMPLETE: All tasks executed successfully")
            logger.info("="*80)
            logger.info(f"Outputs in: {PHASE2_DIR}")
            
        except Exception as e:
            logger.error(f"\n❌ PHASE 2 FAILED: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


TASK_METHODS = {
    4: "task_4_validity_constraints",
    5: "task_5_generate_settings",
    6: "task_6_static_features",
    7: "task_7_feature_analysis",
    8: "task_8_pruning",
    9: "task_9_traffic_profiles",
    10: "task_10_final_documentation",
}


def main():
    parser = argparse.ArgumentParser(description="Phase 2 Executor: Tasks 4-10")
    parser.add_argument("--all", action="store_true", help="Execute all tasks (default)")
    parser.add_argument("--task", type=int, choices=list(TASK_METHODS), help="Execute specific task")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no file writing)")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed for pruning (default: 42)")
    parser.add_argument("--n-pruned", type=int, default=750, help="Target pruned scenarios (default: 750)")
    parser.add_argument("--n-profiles", type=int, default=6, help="Traffic profiles per base (default: 6)")

    args = parser.parse_args()

    executor = Phase2Executor(seed=args.seed)

    if args.task:
        method_name = TASK_METHODS[args.task]
        method = getattr(executor, method_name)
        if args.task == 8:
            method(n_pruned=args.n_pruned)
        elif args.task == 9:
            method(n_profiles=args.n_profiles)
        else:
            method()
    else:
        executor.execute_all_tasks(n_pruned=args.n_pruned, n_profiles=args.n_profiles)


if __name__ == '__main__':
    main()
