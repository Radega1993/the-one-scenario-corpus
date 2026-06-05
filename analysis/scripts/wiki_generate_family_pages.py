#!/usr/bin/env python3
"""Generate wiki family pages with metrics tables and heatmap galleries."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[3]
WIKI = REPO / "scenarios" / ".wiki-clone"
HEATMAP_SRC = REPO / "scenarios" / "analysis" / "figures" / "spatial_heatmaps"
MANIFEST = REPO / "scenarios" / "corpus_v1" / "manifest.csv"
OUT_METRICS = REPO / "scenarios" / "analysis" / "data" / "output_metrics.csv"
SPA_METRICS = REPO / "scenarios" / "analysis" / "data" / "spatial_occupancy_metrics.csv"

def slug_anchor(base: str) -> str:
    """C1_Campus_ClassChange -> c1-campus-class-change."""
    short = base.split("_", 1)[0] + "_" + base.split("_", 1)[1] if "_" in base else base
    parts = short.lower().split("_")[1:]  # drop C1 prefix letter+num
    m = re.match(r"^([a-z]\d+)_(.*)$", base.lower())
    if m:
        parts = m.group(2).split("_")
    return "-".join(parts)

def copy_heatmaps(family_id: str, asset_subdir: str, bases: list[str]) -> int:
    dst_root = WIKI / "assets" / asset_subdir / "heatmaps"
    n = 0
    for base in bases:
        d = dst_root / base
        d.mkdir(parents=True, exist_ok=True)
        for src in HEATMAP_SRC.glob(f"{base}__*.png"):
            shutil.copy2(src, d / src.name)
            n += 1
    return n

def load_family_df(family_id: str) -> pd.DataFrame:
    manifest = pd.read_csv(MANIFEST)
    out = pd.read_csv(OUT_METRICS)
    spa = pd.read_csv(SPA_METRICS)
    df = manifest[manifest["family"] == family_id].copy()
    df = df.merge(out, left_on="scenario_name", right_on="scenario", how="left")
    df = df.merge(
        spa[["scenario", "coverage_road_cells_pct"]],
        left_on="scenario_name",
        right_on="scenario",
        how="left",
        suffixes=("", "_spa"),
    )
    return df

def section_table_and_gallery(df: pd.DataFrame, base: str, asset_subdir: str) -> list[str]:
    sub = df[df["scenario_base"] == base].sort_values("traffic_profile_id")
    lines: list[str] = []
    lines.append("### Traffic profiles and simulation results\n")
    lines.append(
        "| Scenario | TP | Hosts | TTL (min) | Event interval | Event size | "
        "Delivery | Latency (s) | Overhead | Drop % | Road coverage % |"
    )
    lines.append(
        "|----------|-----|------:|----------:|------------------|------------|"
        "----------:|------------:|---------:|-------:|----------------:|"
    )
    for _, r in sub.iterrows():
        ttl = int(r["Group.msgTtl_minutes"])
        dr = r["delivery_ratio"]
        lat = r["latency_mean"]
        oh = r["overhead_ratio"]
        drop = r["drop_ratio"]
        cov = r["coverage_road_cells_pct"]
        if pd.isna(dr):
            dr_s = lat_s = oh_s = drop_s = cov_s = "—"
        else:
            dr_s = f"{dr:.4f}"
            lat_s = f"{lat:.1f}"
            oh_s = f"{oh:.1f}"
            drop_s = f"{drop:.2f}"
            cov_s = f"{cov:.2f}" if not pd.isna(cov) else "—"
        lines.append(
            f"| `{r['scenario_name']}` | {r['traffic_profile_id']} | {int(r['n_hosts'])} | "
            f"{ttl} | {r['Events1.interval']} | {r['Events1.size']} | {dr_s} | {lat_s} | "
            f"{oh_s} | {drop_s} | {cov_s} |"
        )
    lines.append("")
    lines.append("### Spatial heatmaps\n")
    for _, r in sub.iterrows():
        sn = r["scenario_name"]
        tp, label = r["traffic_profile_id"], r["traffic_profile_name"]
        rel = f"assets/{asset_subdir}/heatmaps/{base}/{sn}.png"
        lines.append(f"**{tp} — {label}**\n")
        lines.append(f"![{sn}]({rel})\n")
    return lines

FAMILIES: dict[str, dict] = {
    "02_campus": {
        "wiki_file": "07-Campus-Family.md",
        "asset_subdir": "campus",
        "title": "Campus family (`02_campus`)",
        "intro": "Compact university-scale mobility on a single Kumpula OSM extract.",
        "role": "The campus family models **pedestrian-scale movement** on a compact university path network: class changes, long stays, events, and evacuation drills. It emphasises **local mixing** and repeated encounters over short spatial scales.",
        "map": "KumpulaCampus",
        "map_png": "assets/maps/KumpulaCampus.png",
        "map_type": "OSM campus-scale network",
        "world": "1524 × 1416 m",
        "models": "ShortestPathMapBasedMovement",
        "why_rows": [
            ("Spatial archetype", "Compact campus paths and internal roads"),
            ("Mobility compatibility", "Uniform SPMM on one connected graph"),
            ("Expected DTN/OppNet behaviour", "Moderate contacts in corridors; event scenarios change density"),
            ("Main limitation", "One Helsinki campus layout"),
        ],
        "movement": "- **ShortestPathMapBasedMovement** for all groups on `roads.wkt` with family-specific speed and `waitTime`.",
        "wkt": [
            ("`roads.wkt`", "Campus graph"),
            ("`A_campus_shuttle.wkt`", "Optional figure asset only (no `routeFile` in corpus)"),
        ],
        "wkt_canonical": "`scenarios/maps/wkt/KumpulaCampus/`. Runtime: `data/KumpulaCampus/`.",
        "base_count": 6,
        "corpus_count": 72,
        "finalize_cmd": "python3 scenarios/setup/regenerate_family_routes.py --map KumpulaCampus --apply --install",
        "report": "scenarios/analysis/reports/maps/KumpulaCampus_final_decision.md",
        "validation_png": "KumpulaCampus_validation.png",
        "paper_note": "The campus family isolates **pedestrian shortest-path mobility** on a single compact OSM extract. It complements urban and vehicle families by removing buses and workday POI cycles while keeping a realistic path network for opportunistic contacts.",
        "example_settings": "scenarios/corpus_v1/02_campus/C1_Campus_ClassChange__TP01_Baseline.settings",
        "bases": {
            "C1_Campus_ClassChange": {
                "title": "C1 — Campus Class Change",
                "purpose": "Traffic waves every ~50 minutes mimicking class-change intervals on the campus graph.",
                "lever": "SPMM, periodic mobility / class-change timing",
                "params": [("Hosts (TP01)", "60"), ("Movement", "ShortestPathMapBasedMovement")],
                "interp": "Heatmaps show corridor use between lecture buildings; coverage is moderate and stable across TPs except under storm/critical-TTL loads.",
            },
            "C2_ExamDay_LongStays": {
                "title": "C2 — Exam Day Long Stays",
                "purpose": "Few sessions, long stays — low mobility and long wait times (exam rooms).",
                "lever": "Low speed, very long `waitTime`",
                "params": [("Hosts (TP01)", "48"), ("Mobility pattern", "Long stays, slow movement")],
                "interp": "Spatial occupancy concentrates in fewer cells than C1; routing latency rises when nodes remain co-located for long intervals.",
            },
            "C3_Hackathon_24h": {
                "title": "C3 — Hackathon 24h",
                "purpose": "Sustained 24 h event density on the campus map.",
                "lever": "Extended `Scenario.endTime`, event-oriented host count",
                "params": [("Hosts (TP01)", "40")],
                "interp": "Prolonged activity fills core path cells; road coverage is among the highest in the family for baseline TP.",
            },
            "C4_CampusEvent_IngressEgress": {
                "title": "C4 — Campus Event Ingress/Egress",
                "purpose": "Two strong traffic peaks (arrival and departure) via timed event generators.",
                "lever": "`Events1` / `Events2` time windows for ingress + egress",
                "params": [("Hosts (TP01)", "80")],
                "interp": "Heatmaps show burst occupancy along main connectors during event windows; delivery ratio swings with TP07/TP10 burst profiles.",
            },
            "C5_Library_Quiet": {
                "title": "C5 — Library Quiet",
                "purpose": "Very low mobility and long stays — quiet study areas with rare but long contacts.",
                "lever": "Low speed, high `waitTime`",
                "params": [("Hosts (TP01)", "42")],
                "interp": "Low `coverage_road_cells_pct` reflects limited roaming; when contacts occur they can yield relatively high delivery under baseline traffic.",
            },
            "C6_EmergencyDrill_Evacuation": {
                "title": "C6 — Emergency Drill Evacuation",
                "purpose": "Fast directional evacuation movement (2–4 m/s, minimal wait).",
                "lever": "High SPMM speed, evacuation-oriented init",
                "params": [("Hosts (TP01)", "80"), ("Speed", "2–4 m/s")],
                "interp": "Heatmaps trace rapid sweep along evacuation paths; contacts are fleeting but spatial coverage along corridors increases versus C5.",
            },
        },
        "base_table": [
            ("`C1_Campus_ClassChange`", "Class-to-class waves", 60, "SPMM class-change timing", "c1-campus-class-change"),
            ("`C2_ExamDay_LongStays`", "Exam day, long stays", 48, "Long `waitTime`, low speed", "c2-exam-day-long-stays"),
            ("`C3_Hackathon_24h`", "24 h event", 40, "Extended simulation horizon", "c3-hackathon-24h"),
            ("`C4_CampusEvent_IngressEgress`", "Ingress/egress peaks", 80, "Dual event time windows", "c4-campus-event-ingress-egress"),
            ("`C5_Library_Quiet`", "Library quiet zone", 42, "Low mobility", "c5-library-quiet"),
            ("`C6_EmergencyDrill_Evacuation`", "Evacuation drill", 80, "Fast evacuation speeds", "c6-emergency-drill-evacuation"),
        ],
    },
    "03_vehicles": {
        "wiki_file": "08-Vehicles-Family.md",
        "asset_subdir": "vehicles",
        "title": "Vehicles family (`03_vehicles`)",
        "intro": "Vehicle-centric mobility on a single Midtown Manhattan OSM grid extract.",
        "role": "The vehicles family models **road-constrained carriers**: taxis (`MapRouteMovement`), buses on orthogonal routes, and optional car-ownership workday subsets. It targets **structured corridor mobility** and faster encounter dynamics on a grid-like drive network.",
        "map": "ManhattanMidtownGrid",
        "map_png": "assets/maps/ManhattanMidtownGrid.png",
        "map_type": "OSM urban grid / vehicle-oriented",
        "world": "2500 × 2366 m",
        "models": "MapRouteMovement, BusMovement, WorkingDayMovement",
        "why_rows": [
            ("Spatial archetype", "Regular urban grid for vehicle routing"),
            ("Mobility compatibility", "Route-based taxis/buses; POI workday in V4/V5"),
            ("Expected DTN/OppNet behaviour", "Repeated corridor contacts; axis-separated A/B routes"),
            ("Main limitation", "Single US grid; figure rotation is display-only"),
        ],
        "movement": (
            "- **MapRouteMovement:** taxis on `A_vehicle_route.wkt`.\n"
            "- **BusMovement:** V3 on `A_vehicle_route.wkt` / `B_vehicle_route.wkt`.\n"
            "- **WorkingDayMovement:** V4/V5 with POI files.\n"
            "- **Legacy:** `A_bus.wkt` / `B_bus.wkt` are not on disk; corpus uses `*_vehicle_route.wkt`."
        ),
        "wkt": [
            ("`roads.wkt`", "Drive network"),
            ("`A_vehicle_route.wkt`, `B_vehicle_route.wkt`", "Vehicle waypoints"),
            ("`A_homes.wkt`, `A_offices.wkt`, `A_meetingspots.wkt`", "V4/V5 POIs"),
        ],
        "wkt_canonical": "`scenarios/maps/wkt/ManhattanMidtownGrid/`. Runtime: `data/ManhattanMidtownGrid/`.",
        "base_count": 5,
        "corpus_count": 60,
        "finalize_cmd": "python3 scenarios/setup/regenerate_family_routes.py --map ManhattanMidtownGrid --apply --install",
        "report": "scenarios/analysis/reports/maps/ManhattanMidtownGrid_final_decision.md",
        "validation_png": "ManhattanMidtownGrid_validation.png",
        "paper_note": "The vehicle family uses one OSM Midtown grid for all scenarios. It separates **route-following vehicular mobility** from pedestrian urban and campus families, enabling comparison of grid-constrained DTN behaviour under identical topology.",
        "example_settings": "scenarios/corpus_v1/03_vehicles/V1_TaxiLow_ManhattanMidtownGrid__TP01_Baseline.settings",
        "bases": {
            "V1_TaxiLow_ManhattanMidtownGrid": {
                "title": "V1 — Taxi Low",
                "purpose": "Few taxis with high speed on a single vehicle route.",
                "lever": "Low `nrofHosts`, MapRouteMovement, high speed",
                "params": [("Hosts (TP01)", "5"), ("Model", "MapRouteMovement")],
                "interp": "Sparse taxis sample a narrow set of grid corridors; road coverage is low but contacts are fast when routes overlap.",
            },
            "V2_TaxiHigh_ManhattanMidtownGrid": {
                "title": "V2 — Taxi High",
                "purpose": "Many taxis with short stops — frequent corridor encounters.",
                "lever": "High taxi count, low `waitTime`",
                "params": [("Hosts (TP01)", "26")],
                "interp": "Higher host count increases visited road cells and delivery under baseline; storm TPs stress buffers along A/B routes.",
            },
            "V3_BusOnlyCarriers_ManhattanMidtownGrid": {
                "title": "V3 — Bus Only Carriers",
                "purpose": "Two bus groups on orthogonal vehicle routes (no pedestrians).",
                "lever": "BusMovement on `A_vehicle_route` / `B_vehicle_route`",
                "params": [("Hosts (TP01)", "9")],
                "interp": "Heatmaps highlight axis-aligned bus corridors; coverage is route-limited by design.",
            },
            "V4_CarOwnership_0_ManhattanMidtownGrid": {
                "title": "V4 — Car Ownership 0%",
                "purpose": "Working-day pedestrians with `ownCarProb=0` (bus-oriented).",
                "lever": "WDM + POIs, no private cars",
                "params": [("Hosts (TP01)", "81")],
                "interp": "Combines grid POI mobility with vehicle-family map — spatial pattern resembles urban commuter corridors but on Manhattan grid.",
            },
            "V5_CarOwnership_100_ManhattanMidtownGrid": {
                "title": "V5 — Car Ownership 100%",
                "purpose": "Full car ownership workday variant on the same grid.",
                "lever": "WDM, `ownCarProb=1`",
                "params": [("Hosts (TP01)", "82")],
                "interp": "Differs from V4 mainly in car-use parameters; heatmaps and KPI tables show how ownership shifts office/commute timing on fixed topology.",
            },
        },
        "base_table": [
            ("`V1_TaxiLow_ManhattanMidtownGrid`", "Few fast taxis", 5, "MapRouteMovement", "v1-taxi-low"),
            ("`V2_TaxiHigh_ManhattanMidtownGrid`", "Many taxis", 26, "High taxi density", "v2-taxi-high"),
            ("`V3_BusOnlyCarriers_ManhattanMidtownGrid`", "Bus-only carriers", 9, "A/B vehicle routes", "v3-bus-only-carriers"),
            ("`V4_CarOwnership_0_ManhattanMidtownGrid`", "WDM, no cars", 81, "`ownCarProb=0`", "v4-car-ownership-0"),
            ("`V5_CarOwnership_100_ManhattanMidtownGrid`", "WDM, full cars", 82, "`ownCarProb=1`", "v5-car-ownership-100"),
        ],
    },
    "04_rural": {
        "wiki_file": "09-Rural-Family.md",
        "asset_subdir": "rural",
        "title": "Rural family (`04_rural`)",
        "intro": "Sparse trail mobility on a single Nuuksio National Park OSM extract.",
        "role": "The rural family models **low-density trail networks**: sparse SPMM, inter-village routes, wildlife dispersion, ranger patrol, and resource/control extremes (R6–R12). It targets **low contact opportunities**, long delays, and partitions — as expected outcomes, not errors.",
        "map": "NuuksioSparseTrails",
        "map_png": "assets/maps/NuuksioSparseTrails.png",
        "map_type": "OSM sparse trail network",
        "world": "2848 × 2945 m",
        "models": "ShortestPathMapBasedMovement, MapRouteMovement",
        "why_rows": [
            ("Spatial archetype", "Sparse forest trails, large `worldSize`, low coverage"),
            ("Mobility compatibility", "SPMM, MapRoute villages/patrol"),
            ("Expected DTN/OppNet behaviour", "Low delivery and encounter rates by design"),
            ("Main limitation", "Single park extract; heatmaps may look sparse"),
        ],
        "movement": (
            "- **SPMM:** trail walking (R1, R5, R6–R12 controls).\n"
            "- **MapRouteMovement:** R2 village loops + inter-village patrol; R4 ranger patrol on `A_ranger_patrol.wkt`."
        ),
        "wkt": [
            ("`roads.wkt`", "Trail graph"),
            ("`A_ranger_patrol.wkt`", "R4 `routeFile`"),
            ("Village / patrol routes", "R2 map-aware routes on trails"),
        ],
        "wkt_canonical": "`scenarios/maps/wkt/NuuksioSparseTrails/`. Runtime: `data/NuuksioSparseTrails/`.",
        "base_count": 12,
        "corpus_count": 144,
        "method_note": "Low spatial coverage, low encounter rates, and low delivery ratios are **expected** in this family.",
        "finalize_cmd": "python3 scenarios/setup/regenerate_family_routes.py --map NuuksioSparseTrails --apply --install",
        "report": "scenarios/analysis/reports/maps/NuuksioSparseTrails_final_decision.md",
        "validation_png": "NuuksioSparseTrails_validation.png",
        "paper_note": "The rural family uses a sparse OSM trail map to represent **challenging DTN conditions** with infrequent contacts. Low KPIs should be interpreted as structural properties of sparse mobility, not misconfiguration.",
        "example_settings": "scenarios/corpus_v1/04_rural/R1_Rural_SparseSPMM__TP01_Baseline.settings",
        "bases": {
            "R1_Rural_SparseSPMM": {"title": "R1 — Rural Sparse SPMM", "purpose": "Large world, few hosts on sparse trails.", "lever": "Low `nrofHosts`, SPMM", "params": [("Hosts (TP01)", "25")], "interp": "Very low road-cell coverage; baseline delivery often near zero — structural sparsity."},
            "R2_VillagesTrails_InterVillage": {"title": "R2 — Villages Trails Inter-Village", "purpose": "Three village loops + inter-village patrol (map-aware).", "lever": "MapRouteMovement per village + patrol", "params": [("Hosts (TP01)", "36")], "interp": "Heatmaps show three trail clusters linked by patrol path; higher local coverage than R1."},
            "R3_WildlifeTracking": {"title": "R3 — Wildlife Tracking", "purpose": "Dispersed nodes with wide roaming on trails.", "lever": "SPMM dispersion", "params": [("Hosts (TP01)", "20")], "interp": "Diffuse, low-intensity occupancy across large bbox; contacts are rare."},
            "R4_ParkRangers_NuuksioSparseTrails": {"title": "R4 — Park Rangers", "purpose": "Few mules on long `A_ranger_patrol.wkt` route.", "lever": "MapRouteMovement, 3 hosts", "params": [("Hosts (TP01)", "3")], "interp": "Thin lines along patrol WKT; minimal coverage by design."},
            "R5_MountainRescue": {"title": "R5 — Mountain Rescue", "purpose": "Critical small messages, short TTL rescue narrative.", "lever": "Low `msgTtl`, small event sizes", "params": [("Hosts (TP01)", "26")], "interp": "SPMM rescue mobility; TP05/TP09 show TTL-sensitive delivery collapse."},
            "R6_SparseLongRange": {"title": "R6 — Sparse Long Range", "purpose": "Sparse nodes with extended radio range.", "lever": "`transmitRange` high", "params": [("Hosts (TP01)", "18")], "interp": "Low spatial coverage but routing can improve vs R1 when range compensates sparsity."},
            "R7_SparseTinyBuffer": {"title": "R7 — Sparse Tiny Buffer", "purpose": "Small buffers under moderate traffic — buffer stress.", "lever": "Small `bufferSize`", "params": [("Hosts (TP01)", "38")], "interp": "Drop ratios rise under TP04/TP10 while heatmaps stay sparse."},
            "R8_IntermittentPower": {"title": "R8 — Intermittent Power", "purpose": "Nodes active only in scheduled time windows.", "lever": "`activeTimes` windows", "params": [("Hosts (TP01)", "35")], "interp": "Temporal sparsity lowers effective contacts even when spatial paths are reused."},
            "R9_ExtremeRange_200m": {"title": "R9 — Extreme Range 200m", "purpose": "Quasi fully connected via 200 m range.", "lever": "`transmitRange=200`", "params": [("Hosts (TP01)", "40")], "interp": "Spatial coverage still trail-limited; delivery can be high despite low movement area."},
            "R10_TinyRange_5m": {"title": "R10 — Tiny Range 5m", "purpose": "Extreme partition — 5 m radio range.", "lever": "`transmitRange=5`", "params": [("Hosts (TP01)", "32")], "interp": "Near-zero delivery under most TPs; heatmaps unchanged but routing graph effectively disconnected."},
            "R11_SpeedExtremeLow": {"title": "R11 — Speed Extreme Low", "purpose": "Very slow movement on trails.", "lever": "Minimal SPMM speed", "params": [("Hosts (TP01)", "28")], "interp": "Low coverage growth over sim time; latency grows when contacts occur."},
            "R12_SpeedExtremeHigh": {"title": "R12 — Speed Extreme High", "purpose": "Very fast movement along trails.", "lever": "High SPMM speed", "params": [("Hosts (TP01)", "40")], "interp": "Broader spatial sampling along trails vs R11; contacts more frequent but still sparse globally."},
        },
        "base_table": [
            ("`R1_Rural_SparseSPMM`", "Sparse SPMM trails", 25, "Few hosts", "r1-rural-sparse-spmm"),
            ("`R2_VillagesTrails_InterVillage`", "Villages + patrol", 36, "MapRoute villages", "r2-villages-trails-inter-village"),
            ("`R3_WildlifeTracking`", "Wildlife dispersion", 20, "SPMM roam", "r3-wildlife-tracking"),
            ("`R4_ParkRangers_NuuksioSparseTrails`", "Ranger patrol", 3, "`A_ranger_patrol.wkt`", "r4-park-rangers-nuuksio-sparse-trails"),
            ("`R5_MountainRescue`", "Mountain rescue", 26, "Short TTL narrative", "r5-mountain-rescue"),
            ("`R6_SparseLongRange`", "Sparse + long range", 18, "High `transmitRange`", "r6-sparse-long-range"),
            ("`R7_SparseTinyBuffer`", "Tiny buffer stress", 38, "Small buffer", "r7-sparse-tiny-buffer"),
            ("`R8_IntermittentPower`", "Intermittent power", 35, "`activeTimes`", "r8-intermittent-power"),
            ("`R9_ExtremeRange_200m`", "200 m range", 40, "Quasi-connected", "r9-extreme-range-200m"),
            ("`R10_TinyRange_5m`", "5 m range", 32, "Partition stress", "r10-tiny-range-5m"),
            ("`R11_SpeedExtremeLow`", "Very slow", 28, "Low speed", "r11-speed-extreme-low"),
            ("`R12_SpeedExtremeHigh`", "Very fast", 40, "High speed", "r12-speed-extreme-high"),
        ],
    },
    "05_disaster": {
        "wiki_file": "10-Disaster-Family.md",
        "asset_subdir": "disaster",
        "title": "Disaster family (`05_disaster`)",
        "intro": "Degraded urban mobility on a single HelsinkiDisrupted OSM extract (Kalasatama / Sörnäinen).",
        "role": "The disaster family models **disrupted urban response**: shelter areas, partitions, emergency routes, UAV/mule carriers, and critical TTL controls. It targets **constrained mobility**, hotspots, and low connectivity as methodological outcomes.",
        "map": "HelsinkiDisrupted",
        "map_png": "assets/maps/HelsinkiDisrupted.png",
        "map_type": "OSM industrial / disrupted urban area",
        "world": "2067 × 2206 m",
        "models": "ShortestPathMapBasedMovement, MapRouteMovement",
        "why_rows": [
            ("Spatial archetype", "Industrial / harbour fabric, partial connectivity"),
            ("Mobility compatibility", "Shelter SPMM + MapRoute emergency/mule"),
            ("Expected DTN/OppNet behaviour", "Partitioning, low delivery, latency spikes"),
            ("Main limitation", "Synthetic disaster narrative, not post-disaster survey"),
        ],
        "movement": (
            "- **ShortestPathMapBasedMovement:** civilians near shelters (D1), erratic/disrupted movement (D3), triage classes (D4).\n"
            "- **MapRouteMovement:** D1 mule/emergency routes, D5 UAV on `A_emergency_route.wkt`.\n"
            "- **Partition / CONN events:** D2, D8 approximate infrastructure limits."
        ),
        "wkt": [
            ("`roads.wkt`", "Urban graph"),
            ("`A_emergency_route.wkt`", "D5 UAV / emergency waypoints"),
            ("`B_mule_route.wkt`", "D1 secondary mule route"),
        ],
        "wkt_canonical": "`scenarios/maps/wkt/HelsinkiDisrupted/`. Runtime: `data/HelsinkiDisrupted/`.",
        "base_count": 9,
        "corpus_count": 108,
        "method_note": "Low delivery, high latency, and partitioning can be **expected outcomes** and should not be read as map errors by default.",
        "finalize_cmd": "python3 scenarios/setup/regenerate_family_routes.py --map HelsinkiDisrupted --apply --install",
        "report": "scenarios/analysis/reports/maps/HelsinkiDisrupted_final_decision.md",
        "validation_png": "HelsinkiDisrupted_validation.png",
        "paper_note": "The disaster family uses one degraded urban OSM extract for all scenarios. It supports evaluation under **emergency mobility narratives** while holding map topology fixed; poor connectivity in partition/TTL scenarios is an intended stress dimension.",
        "example_settings": "scenarios/corpus_v1/05_disaster/D1_ShelterHotspots_EmergencyMobility__TP01_Baseline.settings",
        "bases": {
            "D1_ShelterHotspots_EmergencyMobility": {"title": "D1 — Shelter Hotspots Emergency Mobility", "purpose": "Shelter areas with civilians + emergency/mule MapRoute carriers.", "lever": "SPMM shelters + dual routes", "params": [("Hosts (TP01)", "80")], "interp": "Heatmaps cluster at shelter zones and emergency corridors; post-repair map-aware mobility."},
            "D2_PartitionedCity_MuleBridge": {"title": "D2 — Partitioned City Mule Bridge", "purpose": "Partitioned groups with mule bridge narrative.", "lever": "Group partitioning + mule SPMM", "params": [("Hosts (TP01)", "71")], "interp": "Low cross-partition delivery by design; spatial coverage split by partition."},
            "D3_Aftershock_ErraticMobility": {"title": "D3 — Aftershock Erratic Mobility", "purpose": "Erratic SPMM after disruption.", "lever": "High randomness in movement", "params": [("Hosts (TP01)", "54")], "interp": "Diffuse occupancy; unstable contact graphs across TPs."},
            "D4_MedicalTriage_TwoClasses": {"title": "D4 — Medical Triage Two Classes", "purpose": "Two mobility classes (triage priority).", "lever": "Dual group speeds/waits", "params": [("Hosts (TP01)", "50")], "interp": "Bimodal contact behaviour; KPI spread between student-like fast and staff-like slow layers."},
            "D5_UAVMule_FastRoute_HelsinkiDisrupted": {"title": "D5 — UAV Mule Fast Route", "purpose": "Fast UAV on `A_emergency_route.wkt` + slower civilians.", "lever": "MapRoute UAV high speed", "params": [("Hosts (TP01)", "62")], "interp": "Bright corridor along emergency WKT; UAV-dominated spatial replay."},
            "D6_ShortTtlCritical_5to10min": {"title": "D6 — Short TTL Critical", "purpose": "Critical messages with 5–10 minute TTL.", "lever": "`msgTtl` 5–10 min", "params": [("Hosts (TP01)", "54")], "interp": "TP05/TP09 drive delivery collapse; heatmaps similar to D3 but routing fails earlier."},
            "D7_HighLoad_TrafficStorm": {"title": "D7 — High Load Traffic Storm", "purpose": "Very high message generation to stress buffers.", "lever": "Tiny `Events1.interval`", "params": [("Hosts (TP01)", "70")], "interp": "High drop under storm/burst TPs despite moderate spatial coverage."},
            "D8_InfrastructureReturns_BackboneLinks": {"title": "D8 — Infrastructure Returns", "purpose": "Mid-simulation CONN-up events approximate returning backbone.", "lever": "ExternalEventsQueue CONN", "params": [("Hosts (TP01)", "80")], "interp": "Delivery jumps after mid-sim link events; spatial pattern shows shelter clusters."},
            "D9_Critical_1minTTL": {"title": "D9 — Critical 1 min TTL", "purpose": "Radical 1-minute TTL disaster control.", "lever": "`msgTtl` 1 min", "params": [("Hosts (TP01)", "44")], "interp": "Near-zero delivery except TP05; documents protocol failure mode under extreme TTL."},
        },
        "base_table": [
            ("`D1_ShelterHotspots_EmergencyMobility`", "Shelters + emergency routes", 80, "SPMM + MapRoute", "d1-shelter-hotspots-emergency-mobility"),
            ("`D2_PartitionedCity_MuleBridge`", "Partitioned city", 71, "Partitions", "d2-partitioned-city-mule-bridge"),
            ("`D3_Aftershock_ErraticMobility`", "Erratic mobility", 54, "SPMM erratic", "d3-aftershock-erratic-mobility"),
            ("`D4_MedicalTriage_TwoClasses`", "Medical triage", 50, "Two classes", "d4-medical-triage-two-classes"),
            ("`D5_UAVMule_FastRoute_HelsinkiDisrupted`", "UAV mule route", 62, "`A_emergency_route.wkt`", "d5-uavmule-fast-route-helsinki-disrupted"),
            ("`D6_ShortTtlCritical_5to10min`", "Short TTL critical", 54, "TTL 5–10 min", "d6-short-ttl-critical-5to10min"),
            ("`D7_HighLoad_TrafficStorm`", "Traffic storm", 70, "High event rate", "d7-high-load-traffic-storm"),
            ("`D8_InfrastructureReturns_BackboneLinks`", "Infrastructure returns", 80, "CONN events", "d8-infrastructure-returns-backbone-links"),
            ("`D9_Critical_1minTTL`", "1 min TTL", 44, "TTL 1 min", "d9-critical-1minttl"),
        ],
    },
    "06_social": {
        "wiki_file": "11-Social-Family.md",
        "asset_subdir": "social",
        "title": "Social family (`06_social`)",
        "intro": "Compact urban community mobility on a single KallioCommunityCompact OSM extract (Kallio, Helsinki).",
        "role": "The social family models **community structure and mixing** in a dense residential barrio: strong vs weak communities, periodic rhythms, controls, two-layer populations, and family-scale local routines.",
        "map": "KallioCommunityCompact",
        "map_png": "assets/maps/KallioCommunityCompact.png",
        "map_type": "OSM compact residential neighbourhood",
        "world": "1458 × 1529 m",
        "models": "ShortestPathMapBasedMovement, MapRouteMovement",
        "why_rows": [
            ("Spatial archetype", "Compact dense residential neighbourhood"),
            ("Mobility compatibility", "SPMM mixing; MapRoute community/family loops"),
            ("Expected DTN/OppNet behaviour", "Repeated local contacts; S1/S6 structured communities"),
            ("Main limitation", "Community geometry from routes/clusters, not map alone"),
        ],
        "movement": (
            "- **SPMM (S2–S5):** map-constrained paths on `roads.wkt`.\n"
            "- **MapRouteMovement (S1, S6):** community loops + bridge/civic routes (map-aware repair)."
        ),
        "wkt": [
            ("`roads.wkt`", "Neighbourhood streets"),
            ("`A_homes.wkt`, `A_offices.wkt`, `A_meetingspots.wkt`", "POIs"),
            ("Community / family routes", "Per-group `routeFile` on road graph"),
        ],
        "wkt_canonical": "`scenarios/maps/wkt/KallioCommunityCompact/`. Runtime: `data/KallioCommunityCompact/`.",
        "base_count": 6,
        "corpus_count": 72,
        "finalize_cmd": "python3 scenarios/setup/regenerate_family_routes.py --map KallioCommunityCompact --apply --install",
        "report": "scenarios/analysis/reports/maps/KallioCommunityCompact_final_decision.md",
        "validation_png": "KallioCommunityCompact_validation.png",
        "paper_note": "The social family uses a compact OSM residential map for **community-scale DTN** scenarios. MapRoute-based scenarios (S1, S6) impose community geometry on the road network; SPMM scenarios (S2–S5) vary mixing and rhythm on the same topology.",
        "example_settings": "scenarios/corpus_v1/06_social/S1_StrongCommunities_LimitedMixing__TP01_Baseline.settings",
        "bases": {
            "S1_StrongCommunities_LimitedMixing": {"title": "S1 — Strong Communities Limited Mixing", "purpose": "Four communities on road loops + bridge nodes on civic route.", "lever": "MapRoute per community, SPMM bridges", "params": [("Hosts (TP01)", "110")], "interp": "Four spatial clusters in heatmaps with thin bridges; limited mixing visible between lobes."},
            "S2_WeakCommunities_HighMixing": {"title": "S2 — Weak Communities High Mixing", "purpose": "High mixing, diffuse contacts across the barrio.", "lever": "SPMM high speed, short wait", "params": [("Hosts (TP01)", "80")], "interp": "More uniform road-cell coverage than S1; higher baseline delivery."},
            "S3_PeriodicMeetings_RegularRhythm": {"title": "S3 — Periodic Meetings Regular Rhythm", "purpose": "Regular meeting rhythm via wait/speed structure.", "lever": "Periodic wait/speed", "params": [("Hosts (TP01)", "50")], "interp": "Temporal structure shows in latency more than final coverage; heatmaps stable across TPs."},
            "S4_RandomMixing_NoHotspots": {"title": "S4 — Random Mixing No Hotspots", "purpose": "Control without explicit attractors.", "lever": "Uniform SPMM", "params": [("Hosts (TP01)", "60")], "interp": "Diffuse occupancy baseline for comparing structured S1/S6."},
            "S5_TwoLayer_StudentsStaff": {"title": "S5 — Two Layer Students Staff", "purpose": "Students vs staff mobility layers.", "lever": "Group1/2 speed and wait", "params": [("Hosts (TP01)", "75")], "interp": "Two effective speeds; KPI tables show class-dependent latency spread."},
            "S6_FamilyGroups_LocalRoutines": {"title": "S6 — Family Groups Local Routines", "purpose": "Twelve families on micro-routes + shared civic loop.", "lever": "MapRoute per family", "params": [("Hosts (TP01)", "46")], "interp": "Many small loops in heatmaps; local routines with occasional civic-route overlap."},
        },
        "base_table": [
            ("`S1_StrongCommunities_LimitedMixing`", "Strong communities", 110, "MapRoute loops + bridges", "s1-strong-communities-limited-mixing"),
            ("`S2_WeakCommunities_HighMixing`", "Weak communities", 80, "High SPMM mixing", "s2-weak-communities-high-mixing"),
            ("`S3_PeriodicMeetings_RegularRhythm`", "Periodic meetings", 50, "Regular rhythm", "s3-periodic-meetings-regular-rhythm"),
            ("`S4_RandomMixing_NoHotspots`", "Random mixing control", 60, "No hotspots", "s4-random-mixing-no-hotspots"),
            ("`S5_TwoLayer_StudentsStaff`", "Students + staff", 75, "Two layers", "s5-two-layer-students-staff"),
            ("`S6_FamilyGroups_LocalRoutines`", "Family groups", 46, "12 micro-routes", "s6-family-groups-local-routines"),
        ],
    },
}

def build_page(family_id: str, cfg: dict, df: pd.DataFrame) -> str:
    asset = cfg["asset_subdir"]
    lines: list[str] = []
    lines.append(f"# {cfg['title']}\n")
    lines.append(f"{cfg['intro']}\n")
    lines.append("## Role in the benchmark\n")
    lines.append(f"{cfg['role']}\n")
    lines.append("## Assigned map\n")
    lines.append("| Field | Value |")
    lines.append("|-------|--------|")
    lines.append(f"| Family ID | `{family_id}` |")
    lines.append(f"| Map | `{cfg['map']}` |")
    lines.append(f"| Map type | {cfg['map_type']} |")
    lines.append(f"| `worldSize` | {cfg['world']} |")
    lines.append(f"| Main movement models | {cfg['models']} |")
    lines.append("| Corpus role | Environmental corpus |")
    lines.append("")
    lines.append(f"![{cfg['map']} map]({cfg['map_png']})\n")
    lines.append("**Visual legend:** Blue lines = road/trail graph. Solid coloured routes = resolved graph paths. Dotted lines = stop-order references. Points = POIs.\n")
    if cfg.get("legacy_note"):
        lines.append(cfg["legacy_note"] + "\n")
    lines.append("## Why this map fits this family\n")
    lines.append("| Criterion | Justification |")
    lines.append("|-----------|---------------|")
    for a, b in cfg["why_rows"]:
        lines.append(f"| {a} | {b} |")
    lines.append("")
    if cfg.get("method_note"):
        lines.append("## Methodological note\n")
        lines.append(f"{cfg['method_note']}\n")
    lines.append("## Base scenarios\n")
    lines.append("| Base ID | Purpose | Hosts (TP01) | Main lever | Detail |")
    lines.append("|---------|---------|---------------:|------------|--------|")
    for bid, purpose, hosts, lever, anchor in cfg["base_table"]:
        short = bid.split("_", 1)[0].replace("`", "")
        link = f"[{short}](#{anchor})"
        lines.append(f"| {bid} | {purpose} | {hosts} | {lever} | {link} |")
    lines.append("")
    lines.append("## Movement models\n")
    lines.append(cfg["movement"] + "\n")
    lines.append("## WKT assets\n")
    lines.append("| File | Role |")
    lines.append("|------|------|")
    for f, r in cfg["wkt"]:
        lines.append(f"| {f} | {r} |")
    lines.append("")
    lines.append(f"Canonical: {cfg['wkt_canonical']}\n")
    lines.append("## Traffic profile expansion\n")
    lines.append(f"- **Base:** `scenarios/base_scenarios/{family_id}/` — {cfg['base_count']} scenarios.")
    lines.append(f"- **Corpus:** `scenarios/corpus_v1/{family_id}/` — × 12 TP → **{cfg['corpus_count']}** settings.\n")
    lines.append(
        "Routing and spatial metrics use overlays "
        "(`routing_contact_reports_overrides.txt`, `spatial_occupancy_reports_overrides.txt`) "
        "and CSVs under `scenarios/analysis/data/`.\n"
    )
    lines.append("## Scenario documentation\n")
    lines.append(
        "Each base has **12 traffic-profile variants**. Tables: manifest traffic params, "
        "**delivery / latency / overhead / drop** (`output_metrics.csv`), "
        "**`coverage_road_cells_pct`** (`spatial_occupancy_metrics.csv`). "
        "Heatmaps: analysis pipeline (`--zoom-mode roads`).\n"
    )
    anchors = {row[0].strip("`"): row[4] for row in cfg["base_table"]}
    for base, meta in cfg["bases"].items():
        anchor = anchors[base]
        lines.append(f"## {meta['title']} {{#{anchor}}}\n")
        lines.append(f"{meta['purpose']}\n")
        lines.append(f"**Main lever:** {meta['lever']}\n")
        if meta.get("params"):
            lines.append("| Parameter | Value |")
            lines.append("|-----------|-------|")
            for k, v in meta["params"]:
                lines.append(f"| {k} | {v} |")
            lines.append("")
        lines.extend(section_table_and_gallery(df, base, asset))
        lines.append("### Interpretation\n")
        lines.append(meta["interp"] + "\n")
    lines.append("## Validation status\n")
    lines.append("```bash")
    lines.append(cfg["finalize_cmd"])
    lines.append("```\n")
    lines.append(f"Report: `{cfg['report']}`  ")
    val_png = cfg.get("validation_png")
    if val_png:
        src = REPO / "scenarios" / "analysis" / "figures" / "maps" / val_png
        if src.is_file():
            lines.append(f"  \nQA figure (wiki): [validation](assets/{asset}/{val_png})\n")
        else:
            lines.append("\n")
    lines.append("## Notes for the paper\n")
    lines.append(f"{cfg['paper_note']}\n")
    lines.append("## Corpus size\n")
    lines.append(
        f"{cfg['base_count']} base × 12 TP = **{cfg['corpus_count']}** corpus settings in "
        f"`corpus_v1/{family_id}/` (plus {cfg['base_count']} base files in `base_scenarios/{family_id}/`).\n"
    )
    lines.append("## Data sources and reproduction\n")
    lines.append("| Artifact | Path |")
    lines.append("|----------|------|")
    lines.append("| Manifest | `scenarios/corpus_v1/manifest.csv` |")
    lines.append("| Routing KPIs | `scenarios/analysis/data/output_metrics.csv` |")
    lines.append("| Spatial occupancy | `scenarios/analysis/data/spatial_occupancy_metrics.csv` |")
    lines.append("| Per-run reports | `reports/{scenario}_*.csv` |")
    lines.append("")
    lines.append("**Simulate one scenario:**\n")
    lines.append("```bash")
    lines.append("python3 scenarios/analysis/run_all_scenarios.py \\")
    lines.append("  --corpus corpus_v1 \\")
    lines.append(f"  --settings {cfg['example_settings']} \\")
    lines.append("  --extra-settings scenarios/analysis/overlays/routing_contact_reports_overrides.txt \\")
    lines.append("  --extra-settings scenarios/analysis/overlays/spatial_occupancy_reports_overrides.txt \\")
    lines.append("  --jobs 1 --timeout 21600")
    lines.append("```\n")
    lines.append("**Regenerate spatial analysis:**\n")
    lines.append("```bash")
    lines.append("venv/bin/python scenarios/analysis/scripts/validation/analyze_spatial_occupancy.py \\")
    lines.append("  --reports-dir reports \\")
    lines.append("  --manifest scenarios/corpus_v1/manifest.csv \\")
    lines.append(f"  --families {family_id} \\")
    lines.append("  --zoom-mode roads")
    lines.append("```\n")
    lines.append(
        "**Regenerate this wiki page:** "
        "`venv/bin/python scenarios/analysis/scripts/wiki_generate_family_pages.py --family "
        f"{family_id}`\n"
    )
    lines.append(
        "See also: [Traffic Profiles](06-Traffic-Profiles.md) · "
        "[Spatial Occupancy](08-Spatial-Occupancy.md) · "
        "[Scenario Families](05-Scenario-Families.md)\n"
    )
    return "\n".join(lines)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--family",
        action="append",
        choices=list(FAMILIES.keys()),
        help="Family id(s) to generate; default all except 01_urban",
    )
    ap.add_argument("--skip-copy", action="store_true")
    args = ap.parse_args()
    families = args.family or [k for k in FAMILIES if k != "01_urban"]
    fig_maps = REPO / "scenarios" / "analysis" / "figures" / "maps"

    for family_id in families:
        cfg = FAMILIES[family_id]
        bases = list(cfg["bases"].keys())
        if not args.skip_copy:
            n = copy_heatmaps(family_id, cfg["asset_subdir"], bases)
            print(f"{family_id}: copied {n} heatmaps")
            val = cfg.get("validation_png")
            if val:
                src = fig_maps / val
                if src.is_file():
                    dst = WIKI / "assets" / cfg["asset_subdir"] / val
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
        df = load_family_df(family_id)
        page = build_page(family_id, cfg, df)
        out = WIKI / cfg["wiki_file"]
        out.write_text(page, encoding="utf-8")
        print(f"wrote {out} ({len(page.splitlines())} lines)")

if __name__ == "__main__":
    main()