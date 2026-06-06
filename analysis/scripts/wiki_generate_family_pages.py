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

# corpus_v1 vehicle settings/manifest use doubled map suffix; output_metrics uses canonical base names.
_VEHICLE_MANIFEST_SUFFIX = "_ManhattanMidtownGridMidtownGrid"
_VEHICLE_METRICS_SUFFIX = "_ManhattanMidtownGrid"


def manifest_base_key(family_id: str, canonical_base: str, manifest_bases: set[str]) -> str:
    """Resolve manifest scenario_base (may differ from display key for 03_vehicles)."""
    if family_id != "03_vehicles":
        return canonical_base
    doubled = canonical_base.replace(_VEHICLE_METRICS_SUFFIX, _VEHICLE_MANIFEST_SUFFIX)
    return doubled if doubled in manifest_bases else canonical_base


def manifest_bases_for_family(family_id: str) -> set[str]:
    manifest = pd.read_csv(MANIFEST)
    return set(manifest.loc[manifest["family"] == family_id, "scenario_base"].astype(str))


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
    if family_id == "03_vehicles":
        # output_metrics lists both canonical and manifest-style names; use manifest keys only.
        out = out[out["scenario"].str.contains(_VEHICLE_MANIFEST_SUFFIX, na=False)].copy()
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
    "01_urban": {
        "wiki_file": "09-Urban-Family.md",
        "asset_subdir": "urban",
        "title": "Urban family (`01_urban`)",
        "intro": "Dense pedestrian and commuter mobility on a single Helsinki city-centre OSM extract.",
        "role": "The urban family models **commuter-like mobility** in a dense downtown: homes, offices, meeting spots, and a bus line on a fixed street graph. It targets moderate-to-high contact opportunities, congestion along corridors, and workday timing structure — without swapping maps between urban scenarios.",
        "map": "HelsinkiDowntown",
        "map_png": "assets/maps/HelsinkiDowntown.png",
        "map_type": "OSM urban downtown",
        "world": "1713 × 1459 m",
        "models": "WorkingDayMovement, BusMovement",
        "why_rows": [
            ("Spatial archetype", "Dense urban downtown with homes, offices, meeting spots and connected streets"),
            ("Mobility compatibility", "WorkingDayMovement POIs and BusMovement on `A_bus.wkt`"),
            ("Expected DTN/OppNet behaviour", "Frequent co-location at offices and bus corridors; rush peaks from wait/speed levers"),
            ("Main limitation", "Single Finnish CBD extract; not globally representative"),
        ],
        "legacy_note": "> **Note:** Some analysis CSVs still label the dataset as `HelsinkiMedium` (legacy name). Runtime paths and WKT assets use **`data/HelsinkiDowntown/`.**",
        "movement": (
            "- **WorkingDayMovement:** pedestrians between home, office, and meeting POIs on `roads.wkt`.\n"
            "- **BusMovement:** bus host on `A_bus.wkt`; resolved paths follow the road graph.\n"
            "- `Group.routeFile = data/HelsinkiDowntown/A_bus.wkt` when `busControlSystemNr = -1`."
        ),
        "wkt": [
            ("`roads.wkt`", "Street graph (`mapFile1`)"),
            ("`A_homes.wkt`, `A_offices.wkt`, `A_meetingspots.wkt`", "POIs"),
            ("`A_bus.wkt`", "Primary bus route (in settings)"),
            ("`B_bus.wkt`, `C_bus.wkt`", "Optional extra routes"),
        ],
        "wkt_canonical": "`scenarios/maps/wkt/HelsinkiDowntown/`. Runtime: `data/HelsinkiDowntown/`.",
        "base_count": 7,
        "corpus_count": 84,
        "finalize_cmd": "python3 scenarios/setup/regenerate_family_routes.py --map HelsinkiDowntown --apply --install",
        "report": "scenarios/analysis/reports/maps/map_assets_final_validation.md",
        "validation_png": "HelsinkiDowntown_validation.png",
        "paper_note": "The urban family uses one Helsinki downtown OSM extract for all scenarios. Within-family differences reflect commuter density, office timing, buffer stress, and traffic profiles — not map swaps.",
        "example_settings": "scenarios/corpus_v1/01_urban/U1_CBD_Commuting_HelsinkiDowntown__TP01_Baseline.settings",
        "design_intent": (
            "All urban scenarios share the **same map** (`HelsinkiDowntown`: `roads.wkt`, homes, offices, meeting spots, bus route `A_bus.wkt`). "
            "Differences between U1–U7 come from **density, workday timing, buffer size, and corridor constraints** — not from swapping cities. "
            "Each base is expanded with **12 traffic profiles (TP01–TP12)** that vary message load, TTL, and traffic patterns without changing mobility.\n\n"
            "### Common mobility and communication model\n\n"
            "Every scenario has two node types:\n\n"
            "1. **Pedestrians** (`WorkingDayMovement`): home → office → meeting spots / shopping → home on the street graph. "
            "Many pedestrians use the bus (`busControlSystemNr = -1`).\n"
            "2. **One bus** (`BusMovement` on `A_bus.wkt`): acts as a **mobile ferry** linking parts of the map where pedestrians rarely meet directly.\n\n"
            "Communication is **opportunistic Bluetooth** (range 6–12 m depending on scenario). Contacts occur at offices, bus stops, and corridor choke points.\n\n"
            "### Research questions by scenario\n\n"
            "| Scenario | Primary research question |\n"
            "|----------|---------------------------|\n"
            "| **U1** | Reference CBD: routing in “normal” dense urban commuting |\n"
            "| **U2** | How does performance scale with **low node density**? |\n"
            "| **U3** | Can routing survive **micro-device buffer stress**? |\n"
            "| **U4** | Does routing work under **viario bottlenecks**? |\n"
            "| **U5** | What happens with a **short active window**? |\n"
            "| **U6** | Can protocols exploit **long office co-location**? |\n"
            "| **U7** | How does routing behave when **schedules are desynchronised**? |\n\n"
            "### Benchmark usage\n\n"
            "- **Main tier:** U1 TP01–TP08 for protocol comparison in typical urban conditions.\n"
            "- **Stress:** U3 (buffer), U4 (corridor), TP04/TP09/TP10 (load/TTL extremes).\n"
            "- **Controls:** TP12 (cross-group), TP05 (critical TTL).\n\n"
            "Per-scenario detail below; KPI tables and heatmaps follow the narrative in each section.\n"
        ),
        "bases": {
            "U1_CBD_Commuting_HelsinkiDowntown": {
                "title": "U1 — CBD Commuting",
                "narrative": "A concentrated **central business district** where many workers commute to a small set of large offices. Urban **reference scenario**.",
                "simulates": "12 large offices (`officeSize = 60`), sharper rush (`timeDiffSTD = 1200`), full 8 h workday, 81 hosts (80 pedestrians + 1 bus).",
                "routing": "Moderate delivery (~48% TP01), high road coverage (~65%), high mean latency (~3.5 h). Anchor for comparing other urban variants.",
                "lever": "`nrOfOffices=12`, `timeDiffSTD=1200`",
                "params": [("Hosts (TP01)", "81")],
                "interp": "Heatmaps show office and corridor hotspots. U1 is the baseline “city on a predictable schedule”.",
            },
            "U2_SparseUrban_HelsinkiDowntown": {
                "title": "U2 — Sparse Urban",
                "narrative": "The **same downtown map** with few people and few POIs — sparse suburb or small town on the Helsinki graph.",
                "simulates": "36 hosts, 4 offices, 6 meeting spots, BT range 12 m.",
                "routing": "Fewer contacts → lower delivery (~32% TP01), lower coverage (~46%). Tests graceful degradation under sparse networks.",
                "contrast": "Same map as U1, fewer opportunities — isolates the **density** lever.",
                "lever": "`nrofHosts=35`, `nrOfOffices=4`",
                "params": [("Hosts (TP01)", "36")],
                "interp": "Lower corridor saturation; coverage and delivery drop versus U1.",
            },
            "U3_MicroMobility_HelsinkiDowntown": {
                "title": "U3 — Micro Mobility",
                "narrative": "**Many small devices** (wearables, sensors) — high presence, tiny buffers, short messages.",
                "simulates": "151 hosts, `bufferSize = 2M`, restrictive TTL, BT range 9 m.",
                "routing": "Buffer stress: TP01 delivery ~11%, extreme overhead and drops. High coverage (~75%) but nodes cannot store epidemic floods.",
                "contrast": "U1 = dense city delivery; U3 = **IoT-scale buffer limits**.",
                "lever": "`nrofHosts=150`, `bufferSize=2M`",
                "params": [("Hosts (TP01)", "151")],
                "interp": "Primary **buffer-stress** scenario; drops rise under storm/large-message TPs.",
            },
            "U4_CongestionHotspot_HelsinkiDowntown": {
                "title": "U4 — Congestion Hotspot",
                "narrative": "**Traffic bottleneck** — road works or main corridor where all flow concentrates.",
                "simulates": "`okMaps = 1` (main roads only), 14 offices, BT range 5 m, buffer `44M`.",
                "routing": "Corridor hotspots; delivery ~36% baseline; overhead spikes under hub/burst TPs. **Spatial contention** stress.",
                "contrast": "U3 stresses buffers; U4 stresses **contact topology**.",
                "lever": "`okMaps=1`, `nrOfOffices=14`",
                "params": [("Hosts (TP01)", "81")],
                "interp": "Primary **corridor-contention** scenario.",
            },
            "U5_WorkdayShort_HelsinkiDowntown": {
                "title": "U5 — Workday Short",
                "narrative": "**Short working day** — half-day shifts or activity concentrated in a few hours.",
                "simulates": "`workDayLength = 14400` (4 h office activity); 12 h sim but work contacts end early. BT range 7 m.",
                "routing": "Low baseline delivery (~15%); shorter mean latency; late messages find few relays. **Temporal-window** stress.",
                "lever": "`workDayLength=14400`",
                "params": [("Hosts (TP01)", "81")],
                "interp": "Reduced active window lowers late-sim contacts.",
            },
            "U6_OfficeWaitHeavyTail_HelsinkiDowntown": {
                "title": "U6 — Office Wait Heavy Tail",
                "narrative": "Workers with **long, irregular office stays** (heavy-tailed Pareto waits).",
                "simulates": "Office waits 600–2400 s, Pareto coeff. 1.1; 6 offices; BT range 6 m; large buffer.",
                "routing": "Longer co-location → relatively better delivery (~36% baseline); lower road coverage (~58%). Tests **contact duration**.",
                "contrast": "U5 shortens the day; U6 changes **idle-time distribution** in offices.",
                "lever": "Pareto office waits (`officeMinWaitTime=600`, `officeMaxWaitTime=2400`, `officeWaitTimeParetoCoeff=1.1`)",
                "params": [("Hosts (TP01)", "81")],
                "interp": "Long office stays increase co-location duration.",
            },
            "U7_HighTimeVariance_HelsinkiDowntown": {
                "title": "U7 — High Time Variance",
                "narrative": "**Desynchronised schedules** — flex time, mixed remote/office, no clear rush hour.",
                "simulates": "High `timeDiffSTD` (5400 s in settings), ~8.25 h workday, BT range 11 m.",
                "routing": "Diffuse heatmaps; delivery ~39%; wide KPI spread. **Schedule-entropy** — hurts prediction-based protocols.",
                "contrast": "U1 = synchronised rush; U7 = **no clear peak**.",
                "lever": "`timeDiffSTD=3600` (high variance; see base settings)",
                "params": [("Hosts (TP01)", "81")],
                "interp": "Diffuse rush timing; KPI spread across TPs reflects timing uncertainty.",
            },
        },
        "base_table": [
            ("`U1_CBD_Commuting_HelsinkiDowntown`", "CBD commuting", 81, "`nrOfOffices=12`", "u1-cbd-commuting"),
            ("`U2_SparseUrban_HelsinkiDowntown`", "Sparse urban", 36, "Low density", "u2-sparse-urban"),
            ("`U3_MicroMobility_HelsinkiDowntown`", "Micro mobility", 151, "Many hosts, small buffers", "u3-micro-mobility"),
            ("`U4_CongestionHotspot_HelsinkiDowntown`", "Congestion hotspot", 81, "Corridor stress", "u4-congestion-hotspot"),
            ("`U5_WorkdayShort_HelsinkiDowntown`", "Short workday", 81, "`workDayLength=14400`", "u5-workday-short"),
            ("`U6_OfficeWaitHeavyTail_HelsinkiDowntown`", "Heavy-tail waits", 81, "Pareto office waits", "u6-office-wait-heavy-tail"),
            ("`U7_HighTimeVariance_HelsinkiDowntown`", "High time variance", 81, "`timeDiffSTD=3600`", "u7-high-time-variance"),
        ],
    },
    "02_campus": {
        "wiki_file": "10-Campus-Family.md",
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
        "design_intent": (
            "All campus scenarios share the **same map** (`KumpulaCampus`: `roads.wkt` on the University of Helsinki Kumpula extract). "
            "Differences between C1–C6 come from **pedestrian speed, dwell time, simulation horizon, host density, and timed traffic bursts** — "
            "not from swapping maps. Unlike the urban family there are **no buses, homes, or office POIs**: every node uses "
            "`ShortestPathMapBasedMovement` on the campus path graph. Each base is expanded with **12 traffic profiles (TP01–TP12)** "
            "that vary message load, TTL, and traffic patterns without changing mobility.\n\n"
            "### Common mobility and communication model\n\n"
            "Every scenario has a **single homogeneous group** of pedestrians on `roads.wkt`:\n\n"
            "1. **Movement** (`ShortestPathMapBasedMovement`): nodes pick random destinations on the graph, walk shortest paths, "
            "then pause for a scenario-specific `waitTime` before moving again.\n"
            "2. **Communication** (`SimpleBroadcastInterface` / `bt0`): opportunistic Bluetooth with family-tuned range (6–13 m) "
            "and transmit speed (~1.7–2.4 Mbit/s). Contacts happen when nodes co-locate on paths or at pause points.\n\n"
            "The campus family isolates **pedestrian graph mobility** at university scale (~1.1 × 1.0 km). "
            "It complements urban (commuter POI cycles + bus ferry) and vehicle families by removing structured workday "
            "schedules while keeping a realistic, connected path network for opportunistic routing benchmarks.\n\n"
            "### Research questions by scenario\n\n"
            "| Scenario | Primary research question |\n"
            "|----------|---------------------------|\n"
            "| **C1** | Reference campus day: does routing work with **periodic corridor mixing** (class changes)? |\n"
            "| **C2** | Can protocols exploit **long exam-room co-location** with very low movement? |\n"
            "| **C3** | How do relays behave over a **24 h horizon** with sustained desk-bound activity? |\n"
            "| **C4** | Can routing survive **ingress/egress bursts** when most activity is temporally concentrated? |\n"
            "| **C5** | What happens under **ultra-low mobility** (library quiet zone, rare contacts)? |\n"
            "| **C6** | How does routing change under **fast evacuation** (fleeting, high-speed corridor contacts)? |\n\n"
            "### Benchmark usage\n\n"
            "- **Main tier:** C1 TP01–TP08 for protocol comparison in typical campus conditions.\n"
            "- **Duration stress:** C3 (24 h sim, high baseline latency/overhead).\n"
            "- **Temporal stress:** C4 (dual peak windows), TP07/TP10 burst profiles.\n"
            "- **Mobility extremes:** C5 (static) vs C6 (evacuation speed) as a **slow/fast contrast pair**.\n"
            "- **Controls:** TP05 (critical TTL), TP12 (cross-group traffic).\n\n"
            "Per-scenario detail below; KPI tables and heatmaps follow the narrative in each section.\n"
        ),
        "bases": {
            "C1_Campus_ClassChange": {
                "title": "C1 — Campus Class Change",
                "narrative": "A **normal academic day** on campus: students and staff move between lecture buildings at regular intervals, "
                "creating recurring waves of corridor traffic. Campus **reference scenario**.",
                "simulates": "60 hosts, 12 h sim (`endTime = 43200`), speed 0.8–1.5 m/s, `waitTime` 60–300 s, BT range 10 m. "
                "Base traffic interval ~50 min (`Events1.interval = 2900–3100` s) mimics class-change message bursts.",
                "routing": "Very high delivery (~98% TP01), moderate mean latency (~21 min), road coverage ~91%. "
                "Periodic movement keeps the epidemic graph well mixed along main connectors.",
                "contrast": "C1 = steady pedestrian day; C4 = **temporal spikes**; C5/C2 = much lower mobility.",
                "lever": "SPMM speed/wait + ~50 min message interval",
                "params": [
                    ("Hosts (TP01)", "60"),
                    ("Simulation", "12 h"),
                    ("Speed", "0.8–1.5 m/s"),
                    ("Movement", "ShortestPathMapBasedMovement"),
                ],
                "interp": "Heatmaps show corridor use between lecture buildings; coverage is high and stable across TPs except under storm/critical-TTL loads.",
            },
            "C2_ExamDay_LongStays": {
                "title": "C2 — Exam Day Long Stays",
                "narrative": "**Exam day** — students spend long blocks in the same rooms with minimal movement between sessions.",
                "simulates": "48 hosts, speed 0.2–0.5 m/s, `waitTime` 600–1800 s (10–30 min pauses), BT range 13 m (widest in family). "
                "Base message interval 180–420 s; spatial occupancy concentrates in fewer cells than C1.",
                "routing": "Good delivery (~86% TP01) but **very high latency** (~92 min): nodes co-locate for long intervals, "
                "so copies spread slowly despite strong local mixing. Coverage ~82%.",
                "contrast": "C1 = moving corridors; C2 = **static exam rooms** with longer contact duration.",
                "lever": "Low speed, very long `waitTime`",
                "params": [
                    ("Hosts (TP01)", "48"),
                    ("Speed", "0.2–0.5 m/s"),
                    ("Mobility pattern", "Long stays, slow movement"),
                ],
                "interp": "Spatial occupancy concentrates in fewer cells than C1; routing latency rises when nodes remain co-located for long intervals.",
            },
            "C3_Hackathon_24h": {
                "title": "C3 — Hackathon 24h",
                "narrative": "A **24-hour hackathon** or overnight study event: participants stay at desks with very little roaming.",
                "simulates": "40 hosts, `endTime = 86400` (24 h), speed 0.1–0.4 m/s, `waitTime` 1200–3600 s. "
                "Two event generators: day phase (0–6 h, prefix `M`) and night phase (6–24 h, prefix `N`, faster intervals). "
                "Base `msgTtl = 3200` min in settings.",
                "routing": "Moderate delivery (~69% TP01), **extreme mean latency** (~3.2 h) and high overhead (~231) under baseline load. "
                "Prolonged co-location fills core paths (coverage ~86%) but relay chains are slow.",
                "contrast": "C2 = half-day exam; C3 = **multi-day desk-bound** activity with dual traffic phases.",
                "lever": "Extended `Scenario.endTime`, very low mobility",
                "params": [
                    ("Hosts (TP01)", "40"),
                    ("Simulation", "24 h"),
                    ("Speed", "0.1–0.4 m/s"),
                ],
                "interp": "Prolonged activity fills core path cells; road coverage is among the highest in the family for baseline TP.",
            },
            "C4_CampusEvent_IngressEgress": {
                "title": "C4 — Campus Event Ingress/Egress",
                "narrative": "A **campus event** (open day, concert, graduation): a crowd **arrives in a short window**, disperses, "
                "then **leaves in another burst**.",
                "simulates": "80 hosts, 3 h sim (`endTime = 10800`), speed 0.5–1.2 m/s. "
                "Dual timed generators: ingress `I` (0–900 s, interval 5–15 s) and egress `E` (6300–7200 s). "
                "Long quiet middle — most mobility and traffic are temporally concentrated.",
                "routing": "Strong delivery (~86% TP01), **low latency** (~24 min): dense corridor contacts during peaks carry copies quickly. "
                "Coverage ~80%. TP07 burst can reach 100% delivery.",
                "contrast": "C1 = steady 12 h day; C4 = **bimodal temporal stress** with idle middle.",
                "lever": "`Events1` / `Events2` time windows for ingress + egress",
                "params": [("Hosts (TP01)", "80"), ("Simulation", "3 h")],
                "interp": "Heatmaps show burst occupancy along main connectors during event windows; delivery ratio swings with TP07/TP10 burst profiles.",
            },
            "C5_Library_Quiet": {
                "title": "C5 — Library Quiet",
                "narrative": "**Library or quiet study zone** — people sit almost still for long periods with rare short walks.",
                "simulates": "42 hosts, speed 0.05–0.2 m/s (slowest in family), `waitTime` 900–2400 s, BT range **6 m** (shortest). "
                "12 h sim; nodes barely roam beyond a small set of path cells.",
                "routing": "Moderate delivery (~60% TP01), **very high latency** (~3.6 h), lowest family coverage (~73%). "
                "Contacts are rare but can be long when they occur; epidemic spread is slow and local.",
                "contrast": "C2 = exam rooms with wider radio; C5 = **quieter, shorter range, least roaming**. Opposite pole to C6.",
                "lever": "Very low speed, high `waitTime`, short `transmitRange`",
                "params": [
                    ("Hosts (TP01)", "42"),
                    ("Speed", "0.05–0.2 m/s"),
                    ("BT range", "6 m"),
                ],
                "interp": "Low `coverage_road_cells_pct` reflects limited roaming; when contacts occur they can yield relatively high delivery under baseline traffic.",
            },
            "C6_EmergencyDrill_Evacuation": {
                "title": "C6 — Emergency Drill Evacuation",
                "narrative": "**Emergency evacuation drill** — everyone moves quickly along corridors toward exits with almost no pauses.",
                "simulates": "80 hosts, 2 h sim (`endTime = 7200`), speed **2–4 m/s** (running pace), `waitTime` 0–10 s, "
                "`updateInterval = 0.5`. Fast SPMM on the same campus graph — no special exit POIs, but mobility mimics a directed surge.",
                "routing": "Very high delivery (~94% TP01), **very low latency** (~6 min): many fleeting corridor contacts at high speed "
                "create a fast-moving relay front. Coverage ~77%.",
                "contrast": "C5 = static library; C6 = **high-velocity sweep**. Tests routing under short contact duration, not sparse graphs.",
                "lever": "High SPMM speed, minimal `waitTime`",
                "params": [
                    ("Hosts (TP01)", "80"),
                    ("Speed", "2–4 m/s"),
                    ("Simulation", "2 h"),
                ],
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
        "wiki_file": "11-Vehicles-Family.md",
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
        "design_intent": (
            "All vehicle scenarios share the **same map** (`ManhattanMidtownGrid`: `roads.wkt` plus `A_vehicle_route.wkt` / "
            "`B_vehicle_route.wkt` on a Midtown Manhattan OSM grid). Differences between V1–V5 come from **movement model, "
            "carrier density, route assignment, and car-ownership policy** — not from swapping cities. Each base is expanded "
            "with **12 traffic profiles (TP01–TP12)** that vary message load, TTL, and traffic patterns without changing mobility.\n\n"
            "### Common mobility and communication model\n\n"
            "The family spans three mobility archetypes on one drive network:\n\n"
            "1. **Route-following taxis** (`MapRouteMovement`, V1/V2): nodes loop through waypoints on `A_vehicle_route.wkt` "
            "at road speed (8–17 m/s), with short stops. Contacts occur when taxis share corridor segments.\n"
            "2. **Scheduled bus mules** (`BusMovement`, V3 and V4/V5 bus groups): fixed routes on `A_vehicle_route` and/or "
            "`B_vehicle_route`; orthogonal A/B axes create predictable but axis-separated encounter patterns.\n"
            "3. **Commuter pedestrians** (`WorkingDayMovement`, V4/V5): home → office → meeting/shopping cycles on the grid "
            "POIs (`A_homes`, `A_offices`, `A_meetingspots`), with **`ownCarProb`** controlling bus vs car transfers.\n\n"
            "Communication is **opportunistic Bluetooth** (range 8–17 m depending on scenario). "
            "Road coverage in heatmaps stays **low for pure vehicular scenarios** (V1–V3: ~17–25%) because carriers "
            "sample narrow corridor subsets; V4/V5 reach ~48–62% as pedestrians roam POIs.\n\n"
            "### Research questions by scenario\n\n"
            "| Scenario | Primary research question |\n"
            "|----------|---------------------------|\n"
            "| **V1** | Can **sparse mobile carriers** (few fast taxis) sustain DTN on a grid corridor? |\n"
            "| **V2** | How does **high taxi density** change relay speed and delivery on the same route? |\n"
            "| **V3** | What does a **pure bus-mule network** look like with no pedestrians (orthogonal A/B routes)? |\n"
            "| **V4** | How does **bus-only commuting** (`ownCarProb=0`) perform on a vehicle-family grid? |\n"
            "| **V5** | How does **full car ownership** shift contact patterns and routing on identical topology? |\n\n"
            "### Benchmark usage\n\n"
            "- **Pure vehicular relay:** V2 TP01–TP08 (high taxi density) or V3 (bus-only mules).\n"
            "- **Density contrast:** V1 vs V2 on the **same A route** — isolates carrier count.\n"
            "- **Modality contrast:** V4 vs V5 — **bus-only vs car-only** commuters on fixed POIs.\n"
            "- **Bridge to urban family:** V4/V5 use WDM like U1–U7 but on the Manhattan grid instead of Helsinki CBD.\n"
            "- **Controls:** TP05 (critical TTL), TP04/TP10 (load extremes).\n\n"
            "Per-scenario detail below; KPI tables and heatmaps follow the narrative in each section.\n"
        ),
        "bases": {
            "V1_TaxiLow_ManhattanMidtownGrid": {
                "title": "V1 — Taxi Low",
                "narrative": "A **small taxi fleet** on a fixed grid corridor — few mobile carriers acting as intermittent DTN mules.",
                "simulates": "5 hosts, `MapRouteMovement` on `A_vehicle_route.wkt`, speed 8–14 m/s, `waitTime` 8–25 s, BT range 8 m, "
                "buffer 30M. 12 h sim; base message interval 35–55 s.",
                "routing": "Moderate delivery (~81% TP01), high mean latency (~74 min), **very low road coverage** (~18%). "
                "Sparse taxis meet rarely but move fast when routes overlap; low overhead (~2.5).",
                "contrast": "V1 = sparse mules; V2 = **same route, 26 taxis**. V3 = scheduled buses instead of taxis.",
                "lever": "Low `nrofHosts`, MapRouteMovement, high speed",
                "params": [
                    ("Hosts (TP01)", "5"),
                    ("Speed", "8–14 m/s"),
                    ("Model", "MapRouteMovement"),
                ],
                "interp": "Sparse taxis sample a narrow set of grid corridors; road coverage is low but contacts are fast when routes overlap.",
            },
            "V2_TaxiHigh_ManhattanMidtownGrid": {
                "title": "V2 — Taxi High",
                "narrative": "A **dense taxi fleet** on the same A-route — many carriers with very short stops, frequent corridor encounters.",
                "simulates": "26 hosts, same `MapRouteMovement` / `A_vehicle_route.wkt`, speed 11–17 m/s, `waitTime` 3–10 s, "
                "BT range 16 m, buffer 50M. Faster message interval (12–22 s).",
                "routing": "Very high delivery (~99% TP01), **low latency** (~7 min), coverage still ~18% (route-limited). "
                "Many overlapping taxis create a well-mixed epidemic graph along the corridor.",
                "contrast": "V1 = sparse; V2 = **density lever on identical topology**. Best pure-vehicular baseline in the family.",
                "lever": "High taxi count, low `waitTime`",
                "params": [
                    ("Hosts (TP01)", "26"),
                    ("Speed", "11–17 m/s"),
                    ("BT range", "16 m"),
                ],
                "interp": "Higher host count increases corridor encounters and delivery under baseline; storm TPs stress buffers along the A route.",
            },
            "V3_BusOnlyCarriers_ManhattanMidtownGrid": {
                "title": "V3 — Bus Only Carriers",
                "narrative": "**Bus-only DTN carriers** — no pedestrians, only scheduled mules on two orthogonal vehicle routes.",
                "simulates": "9 hosts in 2 groups: 4 buses on `A_vehicle_route` (system 0), 5 on `B_vehicle_route` (system 1), "
                "`BusMovement`, speed 7–10 m/s. Dual event generators (`M` intra-group, `B` background). BT range 10 m.",
                "routing": "Very high delivery (~96% TP01), moderate latency (~20 min), coverage ~25% (two axis-aligned corridors). "
                "Cross-route contacts happen at grid intersections; pure **mule-network** benchmark.",
                "contrast": "V2 = many taxis on one route; V3 = **fewer hosts, two orthogonal bus axes**, no POI mixing.",
                "lever": "BusMovement on `A_vehicle_route` / `B_vehicle_route`",
                "params": [
                    ("Hosts (TP01)", "9"),
                    ("Groups", "4 on A + 5 on B"),
                    ("Model", "BusMovement only"),
                ],
                "interp": "Heatmaps highlight axis-aligned bus corridors; coverage is route-limited by design.",
            },
            "V4_CarOwnership_0_ManhattanMidtownGrid": {
                "title": "V4 — Car Ownership 0%",
                "narrative": "A **public-transit city** on the Manhattan grid — all commuters use the bus (`ownCarProb = 0`).",
                "simulates": "81 hosts (80 pedestrians + 1 bus), `WorkingDayMovement` with POIs, 7 h workday (`workDayLength = 25200`), "
                "10 offices, BT range 17 m. Dual traffic phases: morning `M` (0–5 h) and afternoon `V` (5–12 h). "
                "`probGoShoppingAfterWork = 0.5–0.6`.",
                "routing": "Moderate delivery (~41% TP01), **high latency** (~3.1 h), coverage ~48%. "
                "Bus-mediated mixing plus office co-location; slower than pure vehicular V2/V3.",
                "contrast": "Same grid/POIs as V5 but **no private cars** — isolates the car-ownership lever.",
                "lever": "WDM + POIs, `ownCarProb=0`",
                "params": [
                    ("Hosts (TP01)", "81"),
                    ("Workday", "7 h"),
                    ("Car ownership", "0%"),
                ],
                "interp": "Combines grid POI mobility with vehicle-family map — spatial pattern resembles urban commuter corridors but on Manhattan grid.",
            },
            "V5_CarOwnership_100_ManhattanMidtownGrid": {
                "title": "V5 — Car Ownership 100%",
                "narrative": "A **car-centric commuter grid** — everyone drives (`ownCarProb = 1`); bus remains for WDM internals only.",
                "simulates": "82 hosts (80 pedestrians + 2 buses), `WorkingDayMovement`, 9 h workday (`workDayLength = 32400`), "
                "7 offices (more dispersed), 12 meeting spots, BT range 14 m, lower post-work shopping (`probGoShoppingAfterWork = 0.1–0.3`).",
                "routing": "Moderate delivery (~48% TP01), high latency (~3.5 h), **higher coverage** (~62%) than V4. "
                "Cars spread activity across more grid cells but contacts may be briefer than bus-stop mixing.",
                "contrast": "V4 = bus-only; V5 = **full car ownership** on identical map — modality A/B test.",
                "lever": "WDM, `ownCarProb=1`",
                "params": [
                    ("Hosts (TP01)", "82"),
                    ("Workday", "9 h"),
                    ("Car ownership", "100%"),
                ],
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
        "wiki_file": "12-Rural-Family.md",
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
        "design_intent": (
            "All rural scenarios share the **same map** (`NuuksioSparseTrails`: sparse OSM trail graph in Nuuksio National Park, "
            "`worldSize` ~2470 × 2565 m). Differences between R1–R12 come from **movement model, host density, route structure, "
            "and resource levers** (range, buffer, speed, active times) — not from swapping maps. Each base is expanded with "
            "**12 traffic profiles (TP01–TP12)** that vary message load, TTL, and traffic patterns without changing mobility.\n\n"
            "### Common mobility and communication model\n\n"
            "Two movement patterns dominate:\n\n"
            "1. **Trail walking** (`ShortestPathMapBasedMovement`): random destinations on `roads.wkt` with rural speed/wait "
            "(R1, R3, R5, R6–R12). Contacts occur when hikers meet on shared trail segments.\n"
            "2. **Fixed routes** (`MapRouteMovement`): village loops and patrol paths on dedicated WKT files "
            "(R2 village groups + inter-village patrol; R4 `A_ranger_patrol.wkt` mules).\n\n"
            "Communication is **opportunistic Bluetooth** (typically 10 m baseline; R6/R9 extend to 200 m, R10 shrinks to 5 m). "
            "The family targets **challenging DTN conditions** — long delays, partition risk, buffer stress — but KPIs **vary by scenario**: "
            "homogeneous SPMM on this connected trail graph can yield high delivery (R1, R12), while slow wildlife (R3), "
            "village isolation (R2), tiny buffers (R7), or critical TTL (R5 TP05) produce structurally hard cases.\n\n"
            "### Two scenario tiers\n\n"
            "| Tier | Scenarios | Purpose |\n"
            "|------|-----------|--------|\n"
            "| **Narrative (R1–R5)** | Sparse trails, villages, wildlife, rangers, rescue | Realistic rural use cases on Nuuksio |\n"
            "| **Resource extremes (R6–R12)** | Range, buffer, power, speed controls | Isolate one DTN resource axis on the same map |\n\n"
            "### Research questions by scenario\n\n"
            "| Scenario | Primary research question |\n"
            "|----------|---------------------------|\n"
            "| **R1** | Reference rural SPMM: how does epidemic routing behave on sparse trails with few hosts? |\n"
            "| **R2** | Can **inter-village patrol mules** bridge three isolated village loops? |\n"
            "| **R3** | What happens with **ultra-slow wildlife** tracking and long message TTL? |\n"
            "| **R4** | Can **3 ranger mules** on a long patrol route sustain DTN? |\n"
            "| **R5** | Can **critical rescue messages** (short TTL, small size) deliver in time? |\n"
            "| **R6** | Does **LoRa-like long range** (200 m, slow bitrate) compensate for sparse nodes? |\n"
            "| **R7** | Can routing survive **tiny buffers** (500 kB) under moderate trail traffic? |\n"
            "| **R8** | How does **intermittent power** (`activeTimes` windows) reduce effective contacts? |\n"
            "| **R9** | What is the upper bound when **200 m range** meets normal SPMM? |\n"
            "| **R10** | How does **5 m range** partition the trail graph? |\n"
            "| **R11** | How does **extreme low speed** (0.2–0.3 m/s) stretch latency? |\n"
            "| **R12** | How does **extreme high speed** (12–15 m/s) change contact frequency? |\n\n"
            "### Benchmark usage\n\n"
            "- **Narrative tier:** R1 TP01 (reference), R2 (multi-cluster), R3 (slow/delay stress).\n"
            "- **Critical TTL:** R5 + TP05; compare with D6 disaster family.\n"
            "- **Resource axis:** R9↔R10 (range), R11↔R12 (speed), R7 (buffer), R8 (temporal sparsity).\n"
            "- **Mule/patrol:** R4 (few carriers), R2 Group4 patrol connectors.\n"
            "- **Controls:** TP05 (critical TTL), TP04/TP10 (load extremes).\n\n"
            "Per-scenario detail below; KPI tables and heatmaps follow the narrative in each section.\n"
        ),
        "bases": {
            "R1_Rural_SparseSPMM": {
                "title": "R1 — Rural Sparse SPMM",
                "narrative": "**Reference rural trail walking** — few hikers on a large sparse trail network. Rural family baseline.",
                "simulates": "25 hosts, `ShortestPathMapBasedMovement` on `roads.wkt`, speed 0.4–1.0 m/s, `waitTime` 120–600 s, "
                "BT range 10 m, 12 h sim. Large `worldSize` (2470 × 2565 m).",
                "routing": "High delivery (~97% TP01), moderate latency (~25 min), **very high road coverage** (~97%) on this connected trail graph. "
                "Few hosts still mix well via epidemic relay along shared paths.",
                "contrast": "R1 = homogeneous SPMM reference; R2 = **clustered villages**; R3 = much slower wildlife.",
                "lever": "Low `nrofHosts`, SPMM on sparse trails",
                "params": [("Hosts (TP01)", "25"), ("Speed", "0.4–1.0 m/s"), ("BT range", "10 m")],
                "interp": "High trail coverage under baseline; delivery drops under TP04/TP05 load/TTL stress despite structural connectivity.",
            },
            "R2_VillagesTrails_InterVillage": {
                "title": "R2 — Villages Trails Inter-Village",
                "narrative": "**Three forest villages** linked by trails, plus rangers patrolling inter-village routes — clustered rural topology.",
                "simulates": "36 hosts in 4 groups: 11+11+11 on village loops (`R2_village_1/2/3.wkt`), 3 patrol on `R2_inter_village.wkt`, "
                "`MapRouteMovement`, speed 0.3–1.5 m/s depending on group.",
                "routing": "Moderate delivery (~72% TP01), **high latency** (~85 min), coverage ~59%. "
                "Intra-village mixing works; cross-village relay depends on patrol mules.",
                "contrast": "R1 = flat SPMM; R2 = **geographic clusters + connector mules**.",
                "lever": "MapRouteMovement per village + inter-village patrol",
                "params": [("Hosts (TP01)", "36"), ("Groups", "3 villages + 3 patrol")],
                "interp": "Heatmaps show three trail clusters linked by patrol path; cross-village latency dominates baseline KPIs.",
            },
            "R3_WildlifeTracking": {
                "title": "R3 — Wildlife Tracking",
                "narrative": "**Wildlife or sensor collars** — very slow, wide-ranging nodes with delay-tolerant data.",
                "simulates": "20 hosts, SPMM, speed 0.05–0.2 m/s, `waitTime` 600–2400 s, base `msgTtl = 10080` min, "
                "low message rate (interval 600–1200 s), small messages 10–50 kB.",
                "routing": "Low delivery (~41% TP01), **extreme latency** (~4.2 h), coverage ~75%. "
                "Contacts are rare; long TTL helps but slow movement limits relay chains.",
                "contrast": "R1 = normal hiking speed; R3 = **slowest narrative scenario** in the family.",
                "lever": "SPMM dispersion, very low speed, long TTL",
                "params": [("Hosts (TP01)", "20"), ("Speed", "0.05–0.2 m/s"), ("Base msgTtl", "10080 min")],
                "interp": "Diffuse, low-intensity occupancy; structurally hard case for latency-sensitive protocols.",
            },
            "R4_ParkRangers_NuuksioSparseTrails": {
                "title": "R4 — Park Rangers",
                "narrative": "**Park ranger patrol mules** — few carriers on a long fixed route through the park.",
                "simulates": "3 hosts, `MapRouteMovement` on `A_ranger_patrol.wkt`, speed 1.2–2.0 m/s, `waitTime` 60–300 s, BT range 10 m.",
                "routing": "Good delivery (~91% TP01) but **high latency** (~71 min), low coverage ~42% (thin patrol line). "
                "Very low overhead (~1.0) — minimal epidemic duplication with only 3 mules.",
                "contrast": "R4 = few scheduled mules; R2 patrol = **connectors between clusters**; R1 = many random walkers.",
                "lever": "MapRouteMovement, 3 hosts on long patrol WKT",
                "params": [("Hosts (TP01)", "3"), ("Route", "`A_ranger_patrol.wkt`")],
                "interp": "Thin lines along patrol WKT; high delivery despite low spatial coverage — mules revisit the same corridor.",
            },
            "R5_MountainRescue": {
                "title": "R5 — Mountain Rescue",
                "narrative": "**Mountain rescue operation** — critical small alerts that must reach teams before TTL expires.",
                "simulates": "26 hosts, SPMM, 4 h sim (`endTime = 14400`), base `msgTtl = 10` min, messages 1–5 kB, "
                "interval 25–70 s, BT range 12 m, speed 0.4–1.0 m/s.",
                "routing": "Moderate delivery (~76% TP01 under profile TTL override), latency ~52 min. "
                "**TP05 critical TTL collapses delivery** (~2%) — intended TTL stress test.",
                "contrast": "R5 = time-critical rescue; R3 = **delay-tolerant** wildlife. Compare with D6 disaster TTL scenarios.",
                "lever": "Low base `msgTtl`, small event sizes",
                "params": [("Hosts (TP01)", "26"), ("Base msgTtl", "10 min"), ("Simulation", "4 h")],
                "interp": "SPMM rescue mobility; TP05/TP09 show TTL-sensitive delivery collapse while heatmaps stay similar.",
            },
            "R6_SparseLongRange": {
                "title": "R6 — Sparse Long Range",
                "narrative": "**LoRa-like sparse network** — few nodes with extended 200 m radio on a large trail area.",
                "simulates": "18 hosts, SPMM, `transmitRange = 200` m, `transmitSpeed = 250` kbit/s, speed 0.3–0.8 m/s, "
                "`waitTime` 200–800 s.",
                "routing": "High delivery (~92% TP01), high latency (~68 min), coverage ~90%. "
                "Long range compensates for low node count — quasi-connected despite sparse movement.",
                "contrast": "R6 = sparse + long range; R9 = **more hosts, same 200 m**; R10 = **opposite (5 m)**.",
                "lever": "`transmitRange=200`, low `transmitSpeed`, few hosts",
                "params": [("Hosts (TP01)", "18"), ("BT range", "200 m"), ("Bitrate", "250 kbit/s")],
                "interp": "Long range lifts delivery vs density-matched short-range scenarios; spatial coverage still trail-limited.",
            },
            "R7_SparseTinyBuffer": {
                "title": "R7 — Sparse Tiny Buffer",
                "narrative": "**Resource-constrained sensors** — moderate trail traffic but only **500 kB buffers**.",
                "simulates": "38 hosts, SPMM, `bufferSize = 500k`, speed 0.4–1.0 m/s, BT range 12 m, moderate message load.",
                "routing": "Low delivery (~22% TP01), moderate latency (~54 min), high coverage ~97%. "
                "**Buffer stress** — epidemic floods exceed tiny storage despite good spatial mixing.",
                "contrast": "R1 = 50M buffers, high delivery; R7 = **same mobility, buffer bottleneck**.",
                "lever": "Small `bufferSize` (500 kB)",
                "params": [("Hosts (TP01)", "38"), ("Buffer", "500 kB")],
                "interp": "Drop ratios rise under TP04/TP10 while heatmaps stay dense — routing fails from storage, not geography.",
            },
            "R8_IntermittentPower": {
                "title": "R8 — Intermittent Power",
                "narrative": "**Solar/battery nodes** — devices active only 1 h every 2 h (`activeTimes` windows).",
                "simulates": "35 hosts, SPMM, `activeTimes = 0–3600, 7200–10800, …` (six 1 h windows in 12 h), "
                "speed 0.4–1.0 m/s, BT range 10 m.",
                "routing": "Good delivery (~80% TP01), high latency (~1.8 h), coverage ~94%. "
                "**Temporal sparsity** halves effective contact time without changing trail paths.",
                "contrast": "R8 = scheduled sleep; R3 = **always on but slow**; R11 = always on, very slow movement.",
                "lever": "`activeTimes` windows (1 h on / 1 h off)",
                "params": [("Hosts (TP01)", "35"), ("Active windows", "6 × 1 h in 12 h sim")],
                "interp": "Temporal sparsity lowers effective contacts even when spatial paths are reused.",
            },
            "R9_ExtremeRange_200m": {
                "title": "R9 — Extreme Range 200m",
                "narrative": "**Upper-bound range test** — 200 m Bluetooth on normal SPMM with more hosts.",
                "simulates": "40 hosts, SPMM, `transmitRange = 200` m, normal 2 Mbit/s, speed 0.5–1.2 m/s.",
                "routing": "Very high delivery (~97% TP01), low latency (~19 min), coverage ~98%. "
                "Quasi-fully-connected contact graph on the trail network — **range ceiling** benchmark.",
                "contrast": "R9 = range max with normal speed; R10 = **range min (5 m)** on same map.",
                "lever": "`transmitRange=200`",
                "params": [("Hosts (TP01)", "40"), ("BT range", "200 m")],
                "interp": "Spatial coverage still trail-limited in heatmaps; delivery near ceiling due to long-range mixing.",
            },
            "R10_TinyRange_5m": {
                "title": "R10 — Tiny Range 5m",
                "narrative": "**Extreme partition test** — 5 m radio range on slow trail walking.",
                "simulates": "32 hosts, SPMM, `transmitRange = 5` m, speed 0.2–0.5 m/s, `waitTime` 180–600 s.",
                "routing": "Moderate delivery (~86% TP01) on connected trails where co-location is tight; "
                "**TP05 drops to ~1.5%**. Partition stress under critical TTL, not always under baseline.",
                "contrast": "R10 = range floor; R9 = **range ceiling**. Heatmaps unchanged — failure is in contact graph.",
                "lever": "`transmitRange=5`",
                "params": [("Hosts (TP01)", "32"), ("BT range", "5 m")],
                "interp": "Baseline can still deliver on narrow trails; TP05/TP09 expose partition sensitivity under TTL pressure.",
            },
            "R11_SpeedExtremeLow": {
                "title": "R11 — Speed Extreme Low",
                "narrative": "**Extreme slow movement** — hikers or trackers at 0.2–0.3 m/s with long pauses.",
                "simulates": "28 hosts, SPMM, speed 0.2–0.3 m/s, `waitTime` 300–900 s, BT range 10 m.",
                "routing": "High delivery (~93% TP01), moderate latency (~41 min), coverage ~96%. "
                "Slow speed stretches encounter timing but trail co-location still enables epidemic spread.",
                "contrast": "R11 = speed floor; R12 = **speed ceiling (12–15 m/s)**.",
                "lever": "Minimal SPMM speed (0.2–0.3 m/s)",
                "params": [("Hosts (TP01)", "28"), ("Speed", "0.2–0.3 m/s")],
                "interp": "Low speed increases latency vs R12; coverage grows slowly over sim time.",
            },
            "R12_SpeedExtremeHigh": {
                "title": "R12 — Speed Extreme High",
                "narrative": "**Extreme fast movement** — vehicles or runners at 12–15 m/s along trails.",
                "simulates": "40 hosts, SPMM, speed 12–15 m/s, `waitTime` 5–30 s, BT range 10 m.",
                "routing": "Near-perfect delivery (~99.6% TP01), **very low latency** (~3 min), coverage ~99%. "
                "Fast sweeping samples almost all trail cells with frequent fleeting contacts.",
                "contrast": "R12 = speed max; R11 = **speed min**. Best-case rural relay on this map.",
                "lever": "High SPMM speed (12–15 m/s)",
                "params": [("Hosts (TP01)", "40"), ("Speed", "12–15 m/s")],
                "interp": "Broadest spatial sampling in the family; contacts frequent despite sparse global topology.",
            },
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
        "wiki_file": "13-Disaster-Family.md",
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
            "- **ClusterMovement + CONN events:** D2 mule bridge; D8 intermittent `bb0` via `ExternalEventsQueue`."
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
        "design_intent": (
            "All disaster scenarios share the **same map** (`HelsinkiDisrupted`: degraded OSM extract of Kalasatama / Sörnäinen, "
            "`worldSize` ~1711 × 1874 m). Differences between D1–D9 come from **mobility model, partitioning, carrier types, "
            "TTL policy, traffic load, and scheduled infrastructure events** — not from swapping cities. Each base is expanded "
            "with **12 traffic profiles (TP01–TP12)** that vary message load, TTL, and traffic patterns without changing mobility.\n\n"
            "### Common mobility and communication model\n\n"
            "Three mobility patterns appear across the family:\n\n"
            "1. **Shelter / street SPMM** (`ShortestPathMapBasedMovement`): civilians near shelters (D1), erratic movement (D3), "
            "triage classes (D4), TTL/load stress (D6–D9).\n"
            "2. **Fixed emergency carriers** (`MapRouteMovement`): responders/mules on `A_emergency_route.wkt` or `B_mule_route.wkt` (D1, D5).\n"
            "3. **Partitioned clusters** (`ClusterMovement` + optional bridges): isolated groups (D2 mule, D8 intermittent `bb0` CONN events).\n\n"
            "Communication is **opportunistic Bluetooth** on `bt0` (range 6–20 m depending on scenario). D8 adds logical interface "
            "`bb0` (`transmitRange = 0`) activated only by **`ExternalEventsQueue` CONN up/down** windows — modelling partial backbone restoration.\n\n"
            "Low delivery, high latency, partitioning, and buffer drops are **often intentional** stress outcomes, not misconfiguration.\n\n"
            "### Research questions by scenario\n\n"
            "| Scenario | Primary research question |\n"
            "|----------|---------------------------|\n"
            "| **D1** | Can **shelter hotspots + emergency mules** sustain DTN in a disrupted city? |\n"
            "| **D2** | Does a **single mobile mule** bridge two partitioned clusters? |\n"
            "| **D3** | How does **erratic post-disaster movement** affect contact stability? |\n"
            "| **D4** | Can routing distinguish **critical vs routine traffic** (two TTL classes)? |\n"
            "| **D5** | Can **fast UAV mules** on an emergency route improve delivery? |\n"
            "| **D6** | What happens with **5–10 minute critical TTL** messages? |\n"
            "| **D7** | Can protocols survive a **traffic storm** (tiny buffers, extreme event rate)? |\n"
            "| **D8** | Does **intermittent backbone restoration** (scheduled CONN windows) enable cross-partition relay? |\n"
            "| **D9** | What is the failure mode at **1-minute TTL** (radical disaster control)? |\n\n"
            "### Benchmark usage\n\n"
            "- **Reference disaster:** D1 TP01 (shelters + carriers).\n"
            "- **Partition / bridge:** D2 (mule) vs **D8** (intermittent infrastructure).\n"
            "- **TTL axis:** D6 → D9 (escalating TTL stress); TP05 on any base.\n"
            "- **Carrier stress:** D5 (UAV), D7 (buffer storm).\n"
            "- **Controls:** TP12 (cross-group), TP04/TP10 (load extremes).\n\n"
            "Per-scenario detail below; KPI tables and heatmaps follow the narrative in each section.\n"
        ),
        "bases": {
            "D1_ShelterHotspots_EmergencyMobility": {
                "title": "D1 — Shelter Hotspots Emergency Mobility",
                "narrative": "**Post-disaster shelters** — civilians cluster near three shelter zones while emergency responders and aid mules "
                "follow fixed routes between hotspots.",
                "simulates": "80 hosts: 70 civilians in 3 shelter SPMM groups + 4 on `A_emergency_route.wkt` + 6 mules on `B_mule_route.wkt`, "
                "12 h sim, BT range 10 m.",
                "routing": "Good delivery (~86% TP01), latency ~38 min, high coverage ~89%. Shelter clustering plus mule corridors create "
                "local mixing with emergency relay paths.",
                "contrast": "D1 = shelter + mule reference; D2 = **partitions without shelters**; D5 = **UAV instead of ground mules**.",
                "lever": "SPMM shelter groups + dual MapRoute carriers",
                "params": [("Hosts (TP01)", "80"), ("Groups", "3 shelters + emergency + mule")],
                "interp": "Heatmaps cluster at shelter zones and emergency corridors; map-aware mobility after route repair.",
            },
            "D2_PartitionedCity_MuleBridge": {
                "title": "D2 — Partitioned City Mule Bridge",
                "narrative": "**City cut in two** — two refugee clusters with a single fast mule roaming the full map as the only bridge.",
                "simulates": "71 hosts: 35+35 in `ClusterMovement` partitions (centres ~342/1369, x) + 1 mule SPMM (2–4 m/s), 12 h sim.",
                "routing": "Moderate delivery (~50% TP01), low latency (~10 min), **low coverage ~32%** (two lobes). "
                "Cross-partition delivery depends entirely on the lone mule.",
                "contrast": "D2 = continuous mule; D8 = **scheduled backbone windows** instead of always-on bridge.",
                "lever": "ClusterMovement partitions + single mule",
                "params": [("Hosts (TP01)", "71"), ("Partitions", "2 × 35 + 1 mule")],
                "interp": "Low cross-partition delivery by design; spatial coverage split between partition lobes.",
            },
            "D3_Aftershock_ErraticMobility": {
                "title": "D3 — Aftershock Erratic Mobility",
                "narrative": "**Aftershock chaos** — civilians move unpredictably with very wide speed and wait ranges after initial disruption.",
                "simulates": "54 hosts, SPMM, speed 0.1–3.5 m/s, `waitTime` 0–900 s, base `msgTtl = 30` min, BT range 8 m.",
                "routing": "High delivery (~94% TP01), latency ~43 min, coverage ~84%. Erratic movement still yields frequent contacts on the urban graph.",
                "contrast": "D3 = mobility randomness; D6/D9 = **TTL randomness** with calmer movement.",
                "lever": "Wide SPMM speed/wait ranges",
                "params": [("Hosts (TP01)", "54"), ("Speed", "0.1–3.5 m/s")],
                "interp": "Diffuse occupancy; unstable contact graphs under burst/storm TPs.",
            },
            "D4_MedicalTriage_TwoClasses": {
                "title": "D4 — Medical Triage Two Classes",
                "narrative": "**Medical triage** — small responder team sends critical short-TTL messages; civilians carry routine long-TTL traffic.",
                "simulates": "50 hosts: 10 medics (`msgTtl = 10` min) + 40 civilians (`msgTtl = 720` min), dual event generators (`C` critical, `R` routine).",
                "routing": "High delivery (~94% TP01), latency ~46 min, coverage ~86%. Two TTL classes create bimodal latency in KPI tables.",
                "contrast": "D4 = two message classes; D6 = **all critical TTL**; D9 = **extreme 1 min TTL**.",
                "lever": "Dual group `msgTtl` + dual generators",
                "params": [("Hosts (TP01)", "50"), ("Medics / civilians", "10 / 40")],
                "interp": "Bimodal contact behaviour; KPI spread between critical and routine traffic.",
            },
            "D5_UAVMule_FastRoute_HelsinkiDisrupted": {
                "title": "D5 — UAV Mule Fast Route",
                "narrative": "**UAV relay** — two fast aerial mules loop on `A_emergency_route.wkt` while civilians move on streets below.",
                "simulates": "62 hosts: 60 SPMM civilians + 2 UAV `MapRouteMovement` at 12–18 m/s, buffer 200M on UAV group.",
                "routing": "Very high delivery (~97% TP01), low latency (~19 min), coverage ~91%. Bright corridor along emergency WKT in heatmaps.",
                "contrast": "D5 = aerial fast carrier; D1/D2 = **ground mules**; D8 = **infrastructure link** not mobile UAV.",
                "lever": "MapRoute UAV high speed on `A_emergency_route.wkt`",
                "params": [("Hosts (TP01)", "62"), ("UAV speed", "12–18 m/s")],
                "interp": "UAV-dominated spatial replay along emergency route; strong baseline delivery.",
            },
            "D6_ShortTtlCritical_5to10min": {
                "title": "D6 — Short TTL Critical",
                "narrative": "**Critical alerts** — small messages with 5–10 minute TTL in a 4 h disaster window.",
                "simulates": "54 hosts, SPMM, `msgTtl = 7` min, messages 0.5–5 kB, interval 12–35 s, 4 h sim (`endTime = 14400`), BT range 8 m.",
                "routing": "High delivery (~95% TP01 under TP profile TTL), latency ~12 min. **TP05 collapses delivery** — TTL stress benchmark.",
                "contrast": "D6 = short TTL all hosts; D4 = **mixed classes**; D9 = **1 min radical TTL**.",
                "lever": "Base `msgTtl` 7 min, small event sizes",
                "params": [("Hosts (TP01)", "54"), ("Simulation", "4 h"), ("Base msgTtl", "7 min")],
                "interp": "TP05/TP09 drive delivery collapse; heatmaps similar to D3 but routing fails earlier.",
            },
            "D7_HighLoad_TrafficStorm": {
                "title": "D7 — High Load Traffic Storm",
                "narrative": "**Traffic storm** — extremely frequent message generation stresses tiny buffers during disaster response.",
                "simulates": "70 hosts, SPMM, `bufferSize = 16M`, `msgTtl = 15` min, event interval **2–8 s**, 4 h sim, BT range 6 m.",
                "routing": "High delivery (~96% TP01), low latency (~10 min), coverage ~81%. Drops rise under TP04/TP10 despite moderate spatial coverage.",
                "contrast": "D7 = **load/buffer** stress; D6/D9 = **TTL** stress; D3 = mobility stress.",
                "lever": "Tiny `Events1.interval` (2–8 s), small buffer",
                "params": [("Hosts (TP01)", "70"), ("Buffer", "16M"), ("Simulation", "4 h")],
                "interp": "High drop under storm/burst TPs despite moderate spatial coverage.",
            },
            "D8_EmergencyBackbone_IntermittentBridges": {
                "title": "D8 — Emergency Backbone Intermittent Bridges",
                "narrative": "**Partial infrastructure return** — two isolated refugee partitions stay disconnected for 6 h, then **intermittent "
                "backbone gateways** (`bb0` CONN up/down) open scheduled cross-partition windows.",
                "simulates": "80 hosts: 40+40 in `ClusterMovement` partitions, dual interfaces (`bt0` + logical `bb0`). "
                "`ExternalEventsQueue` from `D8_emergency_backbone_events.txt` — 600 s up windows from t=21600 s. Validated: "
                "**0 inter-partition contacts before backbone, 12 after**.",
                "routing": "High delivery (~98% TP01), latency ~57 min, **low coverage ~3.4%** (cluster-bound mobility). "
                "Intermittent bridges enable epidemic relay across partitions; TP05 drops to ~19%.",
                "contrast": "D8 = scheduled infrastructure; D2 = **single mobile mule**; old D8 design (~49% delivery) replaced by intermittent bridges.",
                "lever": "ExternalEventsQueue CONN up/down on `bb0`",
                "params": [
                    ("Hosts (TP01)", "80"),
                    ("Backbone start", "21600 s (6 h)"),
                    ("Inter-partition contacts post-backbone", "12"),
                ],
                "interp": "Two partition lobes in heatmaps; delivery enabled by sparse scheduled bridging, not permanent mesh.",
            },
            "D9_Critical_1minTTL": {
                "title": "D9 — Critical 1 min TTL",
                "narrative": "**Radical disaster control** — all messages expire after **1 minute**; tests protocol failure floor.",
                "simulates": "44 hosts, SPMM, `msgTtl = 1` min, BT range 20 m, speed 0.2–1.2 m/s, 12 h sim.",
                "routing": "Surprisingly high baseline delivery (~93% TP01) due to long profile TTL override in TPs; "
                "**native 1 min TTL** visible under TP05 (~3% delivery). Wide BT range compensates partially.",
                "contrast": "D9 = TTL floor; D6 = 7 min; D4 = **class-based TTL**.",
                "lever": "Base `msgTtl` 1 min",
                "params": [("Hosts (TP01)", "44"), ("Base msgTtl", "1 min"), ("BT range", "20 m")],
                "interp": "Near-zero delivery under native TTL (TP05); documents extreme TTL failure mode.",
            },
        },
        "base_table": [
            ("`D1_ShelterHotspots_EmergencyMobility`", "Shelters + emergency routes", 80, "SPMM + MapRoute", "d1-shelter-hotspots-emergency-mobility"),
            ("`D2_PartitionedCity_MuleBridge`", "Partitioned city", 71, "Partitions", "d2-partitioned-city-mule-bridge"),
            ("`D3_Aftershock_ErraticMobility`", "Erratic mobility", 54, "SPMM erratic", "d3-aftershock-erratic-mobility"),
            ("`D4_MedicalTriage_TwoClasses`", "Medical triage", 50, "Two classes", "d4-medical-triage-two-classes"),
            ("`D5_UAVMule_FastRoute_HelsinkiDisrupted`", "UAV mule route", 62, "`A_emergency_route.wkt`", "d5-uavmule-fast-route-helsinki-disrupted"),
            ("`D6_ShortTtlCritical_5to10min`", "Short TTL critical", 54, "TTL 5–10 min", "d6-short-ttl-critical-5to10min"),
            ("`D7_HighLoad_TrafficStorm`", "Traffic storm", 70, "High event rate", "d7-high-load-traffic-storm"),
            ("`D8_EmergencyBackbone_IntermittentBridges`", "Emergency backbone", 80, "Intermittent CONN", "d8-emergency-backbone-intermittent-bridges"),
            ("`D9_Critical_1minTTL`", "1 min TTL", 44, "TTL 1 min", "d9-critical-1minttl"),
        ],
    },
    "06_social": {
        "wiki_file": "14-Social-Family.md",
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
        "design_intent": (
            "All social scenarios share the **same map** (`KallioCommunityCompact`: compact residential OSM extract of Kallio, Helsinki, "
            "`worldSize` ~1124 × 1149 m). Differences between S1–S6 come from **community geometry, mixing intensity, mobility rhythm, "
            "and group structure** — not from swapping neighbourhoods. Each base is expanded with **12 traffic profiles (TP01–TP12)** "
            "that vary message load, TTL, and traffic patterns without changing mobility.\n\n"
            "### Common mobility and communication model\n\n"
            "Two movement styles structure the family:\n\n"
            "1. **Structured communities** (`MapRouteMovement` on per-group WKT loops): S1 (four communities + bridge route), "
            "S6 (twelve family micro-routes + shared civic loop). Contacts are **local by design** with thin cross-group connectors.\n"
            "2. **Free mixing** (`ShortestPathMapBasedMovement` on `roads.wkt`): S2–S5 — homogeneous or multi-group SPMM with levers "
            "for speed, wait, and periodic rhythm. Contacts spread across the barrio according to mixing parameters.\n\n"
            "Communication is **opportunistic Bluetooth** (range 10–13 m). The social family tests whether routing protocols can exploit "
            "**community structure** (clusters, bridges, family routines) or must cope with **high mixing** and **multi-layer populations** "
            "on a dense residential street graph.\n\n"
            "### Research questions by scenario\n\n"
            "| Scenario | Primary research question |\n"
            "|----------|---------------------------|\n"
            "| **S1** | Can messages cross **strong community boundaries** when only a few bridge nodes connect four clusters? |\n"
            "| **S2** | How does routing change under **weak communities** (high SPMM mixing, diffuse contacts)? |\n"
            "| **S3** | Can protocols exploit **quasi-periodic meeting rhythms** (narrow wait/speed bands)? |\n"
            "| **S4** | What is the **uniform-mixing control** baseline without explicit community geometry? |\n"
            "| **S5** | How do **two mobility layers** (fast students vs slow staff) affect delivery and latency? |\n"
            "| **S6** | Can **family micro-routines** plus a shared civic route sustain local DTN? |\n\n"
            "### Benchmark usage\n\n"
            "- **Structure contrast:** S1 (strong communities) vs S2 (high mixing) vs S4 (neutral control).\n"
            "- **Fine-grained structure:** S6 (12 families) vs S1 (4 communities).\n"
            "- **Rhythm / layers:** S3 (periodic), S5 (two-layer — best baseline delivery in family).\n"
            "- **Controls:** TP05 (critical TTL), TP12 (cross-group traffic).\n\n"
            "Per-scenario detail below; KPI tables and heatmaps follow the narrative in each section.\n"
        ),
        "bases": {
            "S1_StrongCommunities_LimitedMixing": {
                "title": "S1 — Strong Communities Limited Mixing",
                "narrative": "**Four tight-knit neighbourhoods** in Kallio with minimal cross-community contact — only a few **bridge nodes** "
                "on a shared civic route link the clusters.",
                "simulates": "110 hosts in 5 groups: communities A–D (24–28 hosts each) on `S1_community_1..4.wkt` loops, "
                "6 bridge nodes on `S1_bridge_route.wkt` (faster, shorter waits). `MapRouteMovement`, speed 0.5–1.8 m/s, BT range 10 m.",
                "routing": "Moderate delivery (~63% TP01), latency ~21 min, **low coverage ~32%** (four isolated lobes). "
                "Cross-community relay depends on bridge group; TP04/TP09 show heavy overhead under load.",
                "contrast": "S1 = partitioned communities; S2 = **same map, free mixing**; S6 = smaller family clusters.",
                "lever": "MapRoute per community + bridge route",
                "params": [
                    ("Hosts (TP01)", "110"),
                    ("Groups", "4 communities + 6 bridges"),
                ],
                "interp": "Four spatial clusters in heatmaps with thin bridges; limited mixing visible between lobes.",
            },
            "S2_WeakCommunities_HighMixing": {
                "title": "S2 — Weak Communities High Mixing",
                "narrative": "**Weak community ties** — residents move freely across the barrio with high speed and short pauses, "
                "creating a small-world mixing pattern.",
                "simulates": "80 hosts, homogeneous SPMM, speed 0.9–1.9 m/s, `waitTime` 40–180 s, buffer 25M, BT range 10 m.",
                "routing": "Good delivery (~86% TP01), latency ~19 min, **high coverage ~94%**. "
                "High baseline overhead/drops (~1393%) — epidemic stress on moderate buffers despite good mixing.",
                "contrast": "S2 = maximum barrio mixing; S1 = **same map, community walls**.",
                "lever": "SPMM high speed, short wait",
                "params": [
                    ("Hosts (TP01)", "80"),
                    ("Speed", "0.9–1.9 m/s"),
                    ("Buffer", "25M"),
                ],
                "interp": "Uniform road-cell coverage vs S1; higher baseline delivery but buffer/overhead stress under epidemic load.",
            },
            "S3_PeriodicMeetings_RegularRhythm": {
                "title": "S3 — Periodic Meetings Regular Rhythm",
                "narrative": "**Regular community meetings** — neighbours follow a quasi-periodic rhythm (similar wait/speed), "
                "synchronising encounter windows.",
                "simulates": "50 hosts, SPMM, narrow `waitTime` 240–300 s and speed 0.7–0.9 m/s, base `msgTtl = 120` min, "
                "BT range 11 m, buffer 38M.",
                "routing": "High delivery (~91% TP01), latency ~34 min, coverage ~87%. "
                "Temporal structure affects latency more than spatial coverage; rhythm enables predictable contact windows.",
                "contrast": "S3 = synchronised rhythm; S4 = **desynchronised uniform mixing**; S5 = two speed layers instead of one rhythm.",
                "lever": "Narrow wait/speed bands (periodic encounters)",
                "params": [
                    ("Hosts (TP01)", "50"),
                    ("Wait", "240–300 s"),
                    ("Base msgTtl", "120 min"),
                ],
                "interp": "Temporal structure shows in latency more than final coverage; heatmaps stable across TPs.",
            },
            "S4_RandomMixing_NoHotspots": {
                "title": "S4 — Random Mixing No Hotspots",
                "narrative": "**Control scenario** — random SPMM across the full neighbourhood with no POI attractors or community routes.",
                "simulates": "60 hosts, SPMM, speed 0.4–1.0 m/s, `waitTime` 120–500 s, buffer 18M, BT range 13 m.",
                "routing": "Moderate delivery (~58% TP01), latency ~41 min, coverage ~87%. "
                "Diffuse occupancy without hotspots — baseline for comparing structured S1/S6.",
                "contrast": "S4 = unstructured control; S1/S6 impose **explicit geometry** on the same streets.",
                "lever": "Uniform SPMM, no community WKT",
                "params": [
                    ("Hosts (TP01)", "60"),
                    ("Buffer", "18M"),
                    ("BT range", "13 m"),
                ],
                "interp": "Diffuse occupancy baseline for comparing structured S1/S6; moderate delivery without community bridges.",
            },
            "S5_TwoLayer_StudentsStaff": {
                "title": "S5 — Two Layer Students Staff",
                "narrative": "**Two-layer population** — fast-moving students and slow staff share the same barrio streets "
                "(school/community centre narrative).",
                "simulates": "75 hosts in 2 groups: 55 students (speed 1.6–3.0 m/s, wait 10–90 s) + 20 staff "
                "(speed 0.15–0.5 m/s, wait 220–720 s). SPMM, BT range 11 m, buffer 50M.",
                "routing": "Very high delivery (~99% TP01), **low latency** (~10 min), coverage ~94%. "
                "Students act as mobile relays; staff provide stable co-location anchors — best social-family baseline.",
                "contrast": "S5 = heterogeneous speeds; S3 = **single rhythm**; S2 = homogeneous fast mixing.",
                "lever": "Group1/2 speed and wait (students vs staff)",
                "params": [
                    ("Hosts (TP01)", "75"),
                    ("Students", "55 @ 1.6–3.0 m/s"),
                    ("Staff", "20 @ 0.15–0.5 m/s"),
                ],
                "interp": "Two effective mobility layers; KPI tables show class-dependent latency spread with strong baseline delivery.",
            },
            "S6_FamilyGroups_LocalRoutines": {
                "title": "S6 — Family Groups Local Routines",
                "narrative": "**Twelve families** with local daily routines on micro-routes, plus a **shared civic loop** "
                "for occasional cross-family contact.",
                "simulates": "46 hosts in 13 groups: 12 families (3–4 hosts each) on `S6_family_1..12.wkt`, "
                "4 civic hosts on `S6_shared_civic.wkt`. `MapRouteMovement`, speed 0.35–1.2 m/s, long family waits (300–900 s).",
                "routing": "Good delivery (~85% TP01), low latency (~12 min), **moderate coverage ~46%** (many small loops). "
                "Local mixing within families; civic route provides weak global connectivity.",
                "contrast": "S6 = fine-grained family structure; S1 = **four macro-communities**; S2 = no structure.",
                "lever": "MapRoute per family + shared civic WKT",
                "params": [
                    ("Hosts (TP01)", "46"),
                    ("Families", "12 micro-routes + civic loop"),
                ],
                "interp": "Many small loops in heatmaps; local routines with occasional civic-route overlap.",
            },
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
    if cfg.get("design_intent"):
        lines.append("## Design intent — what each scenario simulates\n")
        lines.append(cfg["design_intent"])
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
    manifest_bases = set(df["scenario_base"].astype(str))
    for base, meta in cfg["bases"].items():
        anchor = anchors[base]
        manifest_base = manifest_base_key(family_id, base, manifest_bases)
        lines.append(f"## {meta['title']} {{#{anchor}}}\n")
        if meta.get("narrative"):
            lines.append(f"**Narrative:** {meta['narrative']}\n")
        if meta.get("simulates"):
            lines.append(f"**What it simulates:** {meta['simulates']}\n")
        if meta.get("routing"):
            lines.append(f"**Expected routing behaviour:** {meta['routing']}\n")
        if meta.get("contrast"):
            lines.append(f"**Contrast:** {meta['contrast']}\n")
        if not meta.get("narrative") and meta.get("purpose"):
            lines.append(f"{meta['purpose']}\n")
        lines.append(f"**Main lever:** {meta['lever']}\n")
        if meta.get("params"):
            lines.append("| Parameter | Value |")
            lines.append("|-----------|-------|")
            for k, v in meta["params"]:
                lines.append(f"| {k} | {v} |")
            lines.append("")
        lines.extend(section_table_and_gallery(df, manifest_base, asset))
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
        help="Family id(s) to generate; default all six families",
    )
    ap.add_argument("--skip-copy", action="store_true")
    args = ap.parse_args()
    families = args.family or list(FAMILIES.keys())
    fig_maps = REPO / "scenarios" / "analysis" / "figures" / "maps"

    for family_id in families:
        cfg = FAMILIES[family_id]
        manifest_bases = manifest_bases_for_family(family_id)
        bases = [
            manifest_base_key(family_id, b, manifest_bases) for b in cfg["bases"].keys()
        ]
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