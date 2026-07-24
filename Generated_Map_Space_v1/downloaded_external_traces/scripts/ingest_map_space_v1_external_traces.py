#!/usr/bin/env python3
"""Ingest IEEE DataPort / CRAWDAD packages from map_space_v1/external_traces into
scenarios/external_traces/{raw,processed,registry}.

Uses hardlinks when possible to avoid duplicating multi-GB payloads.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

SCENARIOS = Path(__file__).resolve().parents[2]
SRC_ROOT = SCENARIOS / "map_space_v1" / "external_traces"
RAW_ROOT = SCENARIOS / "external_traces" / "raw" / "crawdad"
PROC_ROOT = SCENARIOS / "external_traces" / "processed" / "crawdad"
REGISTRY_CSV = SCENARIOS / "external_traces" / "registry" / "real_trace_inventory_v1.csv"
REGISTER = SCENARIOS / "external_traces" / "scripts" / "register_real_trace.py"

# Packages already handled as ONE StandardEventsReader derived package
SKIP_DIRS = {"haggle-one-cambridge-city-complete"}

PACKAGES: list[dict] = [
    {
        "src": "cambridge/haggle (v. 2009-05-29) ",
        "dataset_id": "cambridge_haggle_20090529",
        "trace_id": "cambridge_haggle_20090529",
        "dataset_family": "cambridge/haggle",
        "source_dataset": "cambridge/haggle",
        "source_version": "2009-05-29",
        "format": "CRAWDAD iMote Bluetooth archives (tar.gz)",
        "doi": "10.15783/C70011",
        "archetypes": "dense_urban_irregular;conference_event_compact;clustered_communities;campus_compact",
        "anchor_ids": "cambridge_haggle;haggle_contacts_only;infocom_event_compact;infocom_2006_trace",
        "used_in_sms_v1": "true",
        "notes": "Canonical cambridge/haggle release used as source of haggle-one-cambridge-city-complete.",
    },
    {
        "src": "cambridge/haggle (v. 2006-01-31) ",
        "dataset_id": "cambridge_haggle_20060131",
        "trace_id": "cambridge_haggle_20060131",
        "dataset_family": "cambridge/haggle",
        "source_dataset": "cambridge/haggle",
        "source_version": "2006-01-31",
        "format": "CRAWDAD iMote Bluetooth archives (tar.gz)",
        "doi": "10.15783/C70011",
        "archetypes": "dense_urban_irregular;conference_event_compact;clustered_communities",
        "anchor_ids": "cambridge_haggle;haggle_contacts_only",
        "used_in_sms_v1": "true",
        "notes": "Earlier cambridge/haggle snapshot; DOI listed under IEEE DataPort CRAWDAD family cambridge/haggle.",
    },
    {
        "src": "cambridge/haggle (v. 2006-09-15)",
        "dataset_id": "cambridge_haggle_20060915",
        "trace_id": "cambridge_haggle_20060915",
        "dataset_family": "cambridge/haggle",
        "source_dataset": "cambridge/haggle",
        "source_version": "2006-09-15",
        "format": "CRAWDAD iMote Bluetooth archives (tar.gz)",
        "doi": "10.15783/C70011",
        "archetypes": "dense_urban_irregular;conference_event_compact;clustered_communities",
        "anchor_ids": "cambridge_haggle;haggle_contacts_only",
        "used_in_sms_v1": "true",
        "notes": "Intermediate cambridge/haggle snapshot prior to 2009-05-29 release.",
    },
    {
        "src": "upmc-rollernet",
        "dataset_id": "upmc_rollernet_20090202",
        "trace_id": "upmc_rollernet_20090202",
        "dataset_family": "upmc/rollernet",
        "source_dataset": "upmc/rollernet/imote",
        "source_version": "2009-02-02",
        "format": "CRAWDAD iMote Bluetooth contacts (tar.gz)",
        "doi": "10.15783/C7ZK53",
        "archetypes": "corridor_linear",
        "anchor_ids": "rollernet_trace",
        "used_in_sms_v1": "true",
        "notes": "RollerNet Paris tour contacts; SMS-v1 rollernet_trace anchor.",
    },
    {
        "src": "umass/diesel (v. 2008-09-14)",
        "dataset_id": "umass_diesel_20080914",
        "trace_id": "umass_diesel_20080914",
        "dataset_family": "umass/diesel",
        "source_dataset": "umass/diesel",
        "source_version": "2008-09-14",
        "format": "CRAWDAD DieselNet bus DTN archives (tar.gz)",
        "doi": "10.15783/C7488P",
        "archetypes": "bus_route_urban_suburban",
        "anchor_ids": "dieselnet_amherst",
        "used_in_sms_v1": "true",
        "notes": "Latest local DieselNet package; primary bus-route DTN reference.",
    },
    {
        "src": "umass/diesel (v. 2007-12-02)",
        "dataset_id": "umass_diesel_20071202",
        "trace_id": "umass_diesel_20071202",
        "dataset_family": "umass/diesel",
        "source_dataset": "umass/diesel",
        "source_version": "2007-12-02",
        "format": "CRAWDAD DieselNet bus DTN archives (tar.gz)",
        "doi": "10.15783/C7488P",
        "archetypes": "bus_route_urban_suburban",
        "anchor_ids": "dieselnet_amherst",
        "used_in_sms_v1": "true",
        "notes": "Intermediate DieselNet package.",
    },
    {
        "src": "umass/diesel (v. 2006-01-17)",
        "dataset_id": "umass_diesel_20060117",
        "trace_id": "umass_diesel_20060117",
        "dataset_family": "umass/diesel",
        "source_dataset": "umass/diesel",
        "source_version": "2006-01-17",
        "format": "CRAWDAD DieselNet bus DTN archives (tar.gz)",
        "doi": "10.15783/C7488P",
        "archetypes": "bus_route_urban_suburban",
        "anchor_ids": "dieselnet_amherst",
        "used_in_sms_v1": "true",
        "notes": "Earliest local DieselNet package (Spring 2005 transfers).",
    },
    {
        "src": "epfl-mobility",
        "dataset_id": "epfl_mobility_20090224",
        "trace_id": "epfl_mobility_20090224",
        "dataset_family": "epfl/mobility",
        "source_dataset": "epfl/mobility",
        "source_version": "2009-02-24",
        "format": "CRAWDAD taxi GPS mobility (cabspottingdata.tar.gz)",
        "doi": "10.15783/C7J010",
        "archetypes": "dense_urban_irregular;urban_grid",
        "anchor_ids": "sf_cabspotting_downtown",
        "used_in_sms_v1": "true",
        "notes": "San Francisco cabspotting mobility traces.",
    },
    {
        "src": "roma-taxi",
        "dataset_id": "roma_taxi_20140717",
        "trace_id": "roma_taxi_20140717",
        "dataset_family": "roma/taxi",
        "source_dataset": "roma/taxi",
        "source_version": "2014-07-17",
        "format": "CRAWDAD taxi GPS trajectories (tar.gz/txt)",
        "doi": "10.15783/C7QC7M",
        "archetypes": "dense_urban_irregular;urban_grid",
        "anchor_ids": "",
        "used_in_sms_v1": "false",
        "notes": "Rome taxi mobility; design reference, no dedicated SMS-v1 anchor_id yet.",
    },
    {
        "src": "oviedo-asturies-er",
        "dataset_id": "oviedo_asturies_er_20160808",
        "trace_id": "oviedo_asturies_er_20160808",
        "dataset_family": "oviedo/asturies-er",
        "source_dataset": "oviedo/asturies-er",
        "source_version": "2016-08-08",
        "format": "CRAWDAD emergency-related mobility + The ONE .one.gz contacts",
        "doi": "10.15783/C7302B",
        "archetypes": "rural_roads;corridor_linear",
        "anchor_ids": "",
        "used_in_sms_v1": "false",
        "notes": "Includes precomputed ONE contact files (.one.gz) at multiple ranges.",
    },
    {
        "src": "coppe-ufrj-RioBuses",
        "dataset_id": "coppe_ufrj_riobuses_20180319",
        "trace_id": "coppe_ufrj_riobuses_20180319",
        "dataset_family": "coppe-ufrj/RioBuses",
        "source_dataset": "coppe-ufrj/RioBuses",
        "source_version": "2018-03-19",
        "format": "CRAWDAD Rio bus GPS mobility (zip/txt)",
        "doi": "10.15783/C7B64B",
        "archetypes": "bus_route_urban_suburban",
        "anchor_ids": "",
        "used_in_sms_v1": "false",
        "notes": "Rio de Janeiro bus mobility; large payload (~1.4G).",
    },
    {
        "src": "dartmouth/wardriving",
        "dataset_id": "dartmouth_wardriving_20060602",
        "trace_id": "dartmouth_wardriving_20060602",
        "dataset_family": "dartmouth/wardriving",
        "source_dataset": "dartmouth/wardriving",
        "source_version": "2006-06-02",
        "format": "CRAWDAD WiFi wardrive/warwalk + AP locations",
        "doi": "10.15783/C7TG66",
        "archetypes": "campus_compact;suburban_low_density",
        "anchor_ids": "",
        "used_in_sms_v1": "false",
        "notes": "AP location estimation / campus WiFi coverage reference.",
    },
    {        "src": "st_andrews/sassy",
        "dataset_id": "st_andrews_sassy_20110603",
        "trace_id": "st_andrews_sassy_20110603",
        "dataset_family": "st_andrews/sassy",
        "source_dataset": "st_andrews/sassy",
        "source_version": "2011-06-03",
        "format": "CRAWDAD social encounter CSV.gz",
        "doi": "10.15783/C7S59X",
        "archetypes": "clustered_communities;campus_compact",
        "anchor_ids": "haggle_contacts_only",
        "used_in_sms_v1": "true",
        "notes": "St Andrews social sensing encounters.",
    },
    {
        "src": "st_andrews/locshare",
        "dataset_id": "st_andrews_locshare_20111012",
        "trace_id": "st_andrews_locshare_20111012",
        "dataset_family": "st_andrews/locshare",
        "source_dataset": "st_andrews/locshare",
        "source_version": "2011-10-12",
        "format": "CRAWDAD privacy study encounters + sensors (tar.gz)",
        "doi": "10.15783/C7WW2F",
        "archetypes": "clustered_communities;campus_compact",
        "anchor_ids": "haggle_contacts_only",
        "used_in_sms_v1": "true",
        "notes": "St Andrews / London privacy study with encounters.",
    },
    {
        "src": "microsoft-vanlan",
        "dataset_id": "microsoft_vanlan_20070914",
        "trace_id": "microsoft_vanlan_20070914",
        "dataset_family": "microsoft/vanlan",
        "source_dataset": "microsoft/vanlan",
        "source_version": "2007-09-14",
        "format": "CRAWDAD vehicular WiFi basestation connectivity",
        "doi": "10.15783/C7FG6S",
        "archetypes": "corridor_linear;urban_grid",
        "anchor_ids": "",
        "used_in_sms_v1": "false",
        "notes": "VanLAN urban vehicle–basestation WiFi connectivity.",
    },
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def link_or_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def mirror_tree(src_dir: Path, dst_dir: Path) -> list[Path]:
    files: list[Path] = []
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    for path in sorted(src_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(src_dir)
        out = dst_dir / rel
        link_or_copy(path, out)
        files.append(out)
    return files


def write_checksums(files: list[Path], out: Path, base: Path) -> None:
    lines = []
    for f in files:
        if f.name in {"checksums.sha256"}:
            continue
        digest = sha256_file(f)
        rel = f.relative_to(base).as_posix()
        lines.append(f"{digest}  {rel}")
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def file_stats(files: list[Path]) -> dict:
    return {
        "n_files": len(files),
        "total_bytes": sum(f.stat().st_size for f in files),
        "filenames": [f.name for f in files],
    }


def ingest_one(pkg: dict) -> dict:
    src = SRC_ROOT / pkg["src"]
    if not src.is_dir():
        raise FileNotFoundError(src)
    raw_dir = RAW_ROOT / pkg["dataset_id"]
    proc_dir = PROC_ROOT / pkg["dataset_id"]
    print(f"[ingest] {pkg['trace_id']} <- {src}")
    files = mirror_tree(src, raw_dir)

    meta = {
        "dataset_id": pkg["dataset_id"],
        "trace_id": pkg["trace_id"],
        "dataset_family": pkg["dataset_family"],
        "source_dataset": pkg["source_dataset"],
        "source_version": pkg["source_version"],
        "derived_format": pkg["format"],
        "source_repository": "CRAWDAD / IEEE DataPort",
        "source_doi": pkg["doi"],
        "ieee_dataport": "https://ieee-dataport.org/",
        "redistribution_policy": "do_not_redistribute_raw_trace",
        "usage_in_project": "design_anchor_and_trace_reference",
        "local_status": "downloaded",
        "sms_v1_archetypes": [x for x in pkg["archetypes"].split(";") if x],
        "sms_v1_anchor_ids_supported": [x for x in pkg["anchor_ids"].split(";") if x],
        "used_in_sms_v1": pkg["used_in_sms_v1"] == "true",
        "notes": pkg["notes"],
        "raw_path": str(raw_dir.relative_to(SCENARIOS)),
        "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
        "file_inventory": file_stats(files),
    }
    meta_path = raw_dir / "metadata.yaml"
    meta_path.write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")
    files_with_meta = files + [meta_path]
    write_checksums(files_with_meta, raw_dir / "checksums.sha256", raw_dir)

    # processed: metadata pointer only (payloads stay under raw/)
    if proc_dir.exists():
        shutil.rmtree(proc_dir)
    proc_dir.mkdir(parents=True, exist_ok=True)
    proc_meta = dict(meta)
    proc_meta["processed_role"] = "package_manifest_only"
    proc_meta["note_processed"] = (
        "Raw CRAWDAD/IEEE DataPort archives are not rewritten here. "
        "Conversion to The ONE StandardEventsReader (when applicable) is a separate step."
    )
    (proc_dir / "metadata.yaml").write_text(
        yaml.safe_dump(proc_meta, sort_keys=False), encoding="utf-8"
    )
    write_checksums([proc_dir / "metadata.yaml"], proc_dir / "checksums.sha256", proc_dir)

    # register
    cmd = [
        sys.executable,
        str(REGISTER),
        "--trace-id",
        pkg["trace_id"],
        "--dataset-family",
        pkg["dataset_family"],
        "--source-dataset",
        pkg["source_dataset"],
        "--source-version",
        pkg["source_version"],
        "--format",
        pkg["format"],
        "--nodes",
        "",
        "--contacts",
        "",
        "--duration-seconds",
        "",
        "--source-repository",
        "CRAWDAD / IEEE DataPort",
        "--doi",
        pkg["doi"],
        "--local-status",
        "downloaded",
        "--used-in-sms-v1",
        pkg["used_in_sms_v1"],
        "--archetypes",
        pkg["archetypes"],
        "--anchor-ids",
        pkg["anchor_ids"],
        "--redistribution",
        "do_not_redistribute_raw_trace",
    ]
    # register script requires nodes/contacts/duration - pass 0 placeholders for raw packages
    cmd[cmd.index("--nodes") + 1] = "0"
    cmd[cmd.index("--contacts") + 1] = "0"
    cmd[cmd.index("--duration-seconds") + 1] = "0"
    subprocess.run(cmd, check=True)
    return {"trace_id": pkg["trace_id"], "n_files": len(files), "raw_dir": str(raw_dir)}


def main() -> int:
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    PROC_ROOT.mkdir(parents=True, exist_ok=True)
    results = []
    for pkg in PACKAGES:
        results.append(ingest_one(pkg))
    summary = {
        "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
        "n_packages": len(results),
        "packages": results,
        "skipped_source_dirs": sorted(SKIP_DIRS),
        "note": "haggle_one_cambridge_city_complete already ingested under processed/the_one/",
    }
    out = SCENARIOS / "external_traces" / "reports" / "ieee_dataport_ingest_summary_v1.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
