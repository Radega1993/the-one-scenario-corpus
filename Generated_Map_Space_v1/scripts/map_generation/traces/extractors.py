"""Extensible parameter extractors for real traces."""

from __future__ import annotations

import csv
import gzip
import io
import re
import tarfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Protocol, TextIO

from map_generation.config import resolve_repo_path


class ExtractorError(ValueError):
    """Parameter extraction failed."""


class ParameterExtractor(Protocol):
    name: str

    def extract(self, entry: dict[str, Any], *, dry_run: bool = True) -> dict[str, Any]:
        ...


class MetadataOnlyExtractor:
    name = "metadata_only_v1"

    def extract(self, entry: dict[str, Any], *, dry_run: bool = True) -> dict[str, Any]:
        return {
            "extractor": self.name,
            "trace_id": entry.get("trace_id"),
            "generation_role": entry.get("generation_role"),
            "status": "metadata_only",
            "produces_map": False,
        }


class StaticParametersExtractor:
    name = "static_parameters_v1"

    def extract(self, entry: dict[str, Any], *, dry_run: bool = True) -> dict[str, Any]:
        params = dict(entry.get("static_parameters") or {})
        if not params:
            raise ExtractorError(f"{entry.get('trace_id')}: static_parameters empty")
        out = dict(params)
        out["extractor"] = self.name
        out["trace_id"] = entry.get("trace_id")
        return out


class StandardEventsContactSummaryExtractor:
    """Parse The ONE StandardEventsReader CONN up/down events (.tsv or .one.gz)."""

    name = "standard_events_contact_summary_v1"

    def extract(self, entry: dict[str, Any], *, dry_run: bool = True) -> dict[str, Any]:
        path = resolve_repo_path(entry["events_path"])
        if not path.is_file():
            raise ExtractorError(f"events file missing: {path}")
        return summarize_standard_events(path, trace_id=str(entry.get("trace_id") or ""))


class RollernetContactsExtractor:
    """Parse RollerNet contacts.dat from the iMote tar.gz."""

    name = "rollernet_contacts_v1"

    def extract(self, entry: dict[str, Any], *, dry_run: bool = True) -> dict[str, Any]:
        archive = resolve_repo_path(entry.get("archive_path") or "")
        member = entry.get("contacts_member") or "imote-traces-RollerNet/contacts.dat"
        if not archive.is_file():
            raise ExtractorError(f"RollerNet archive missing: {archive}")
        with tarfile.open(archive, "r:gz") as tf:
            try:
                fobj = tf.extractfile(member)
            except KeyError as exc:
                raise ExtractorError(f"member missing in archive: {member}") from exc
            if fobj is None:
                raise ExtractorError(f"cannot read member: {member}")
            text = io.TextIOWrapper(fobj, encoding="utf-8", errors="replace")
            return summarize_rollernet_contacts(text, trace_id=str(entry.get("trace_id") or ""))


class SassyEncountersExtractor:
    name = "sassy_encounters_v1"

    def extract(self, entry: dict[str, Any], *, dry_run: bool = True) -> dict[str, Any]:
        path = resolve_repo_path(entry.get("dsn_path") or "")
        if not path.is_file():
            raise ExtractorError(f"Sassy dsn file missing: {path}")
        opener = gzip.open if path.suffix == ".gz" or path.name.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8", errors="replace") as f:
            return summarize_sassy_dsn(f, trace_id=str(entry.get("trace_id") or ""))


class LocshareEncountersExtractor:
    name = "locshare_encounters_v1"

    def extract(self, entry: dict[str, Any], *, dry_run: bool = True) -> dict[str, Any]:
        archives = entry.get("archive_paths") or []
        if not archives:
            raise ExtractorError(f"{entry.get('trace_id')}: archive_paths required")
        all_rows: list[dict[str, str]] = []
        for ap in archives:
            path = resolve_repo_path(ap)
            if not path.is_file():
                raise ExtractorError(f"LocShare archive missing: {path}")
            with tarfile.open(path, "r:gz") as tf:
                for m in tf.getmembers():
                    if not m.isfile() or not m.name.endswith("-encounters.csv"):
                        continue
                    fobj = tf.extractfile(m)
                    if fobj is None:
                        continue
                    text = io.TextIOWrapper(fobj, encoding="utf-8", errors="replace")
                    reader = csv.DictReader(text)
                    for row in reader:
                        all_rows.append({(k or "").strip().lower(): (v or "").strip() for k, v in row.items()})
        if not all_rows:
            raise ExtractorError(f"{entry.get('trace_id')}: no encounters.csv found in archives")
        return summarize_locshare_encounters(all_rows, trace_id=str(entry.get("trace_id") or ""))


class GpsTraceSummaryExtractor:
    """Parse GPS traces with explicitly configured columns (no silent guessing)."""

    name = "gps_trace_summary_v1"

    def extract(self, entry: dict[str, Any], *, dry_run: bool = True) -> dict[str, Any]:
        cols = entry.get("gps_columns")
        if not cols:
            raise ExtractorError(
                f"{entry.get('trace_id')}: gps_trace_summary_v1 requires configured gps_columns"
            )
        path = entry.get("gps_path")
        if not path:
            raise ExtractorError(f"{entry.get('trace_id')}: gps_path required")
        gps_path = resolve_repo_path(path)
        if not gps_path.is_file():
            raise ExtractorError(f"GPS file missing: {gps_path}")
        max_rows = int(entry.get("gps_max_rows") or 2_000_000)
        return summarize_gps_file(
            gps_path,
            cols=dict(cols),
            trace_id=str(entry.get("trace_id") or ""),
            max_rows=max_rows,
        )


EXTRACTORS: dict[str, ParameterExtractor] = {
    MetadataOnlyExtractor.name: MetadataOnlyExtractor(),
    StaticParametersExtractor.name: StaticParametersExtractor(),
    StandardEventsContactSummaryExtractor.name: StandardEventsContactSummaryExtractor(),
    RollernetContactsExtractor.name: RollernetContactsExtractor(),
    SassyEncountersExtractor.name: SassyEncountersExtractor(),
    LocshareEncountersExtractor.name: LocshareEncountersExtractor(),
    GpsTraceSummaryExtractor.name: GpsTraceSummaryExtractor(),
}


def get_extractor(name: str) -> ParameterExtractor:
    if name not in EXTRACTORS:
        raise ExtractorError(f"Unknown parameter_extractor: {name}")
    return EXTRACTORS[name]


def extract_for_entry(entry: dict[str, Any], *, dry_run: bool = True) -> dict[str, Any]:
    name = entry.get("parameter_extractor") or "metadata_only_v1"
    return get_extractor(name).extract(entry, dry_run=dry_run)


# Process-level cache: large StandardEvents / encounter files are expensive to re-parse
# during repeated planner dry-runs and tests.
_EXTRACT_CACHE: dict[tuple[Any, ...], dict[str, Any]] = {}


def extract_for_entry_cached(entry: dict[str, Any], *, dry_run: bool = True) -> dict[str, Any]:
    """Cache extraction by extractor name + primary input path + mtime."""
    name = entry.get("parameter_extractor") or "metadata_only_v1"
    path_keys = []
    for key in ("events_path", "archive_path", "dsn_path", "gps_path"):
        if entry.get(key):
            path_keys.append(str(entry.get(key)))
    for ap in entry.get("archive_paths") or []:
        path_keys.append(str(ap))
    mtimes: list[float] = []
    for pk in path_keys:
        p = resolve_repo_path(pk)
        mtimes.append(p.stat().st_mtime if p.is_file() else -1.0)
    cache_key = (name, entry.get("trace_id"), tuple(path_keys), tuple(mtimes), bool(dry_run))
    if cache_key in _EXTRACT_CACHE:
        return dict(_EXTRACT_CACHE[cache_key])
    out = extract_for_entry(entry, dry_run=dry_run)
    _EXTRACT_CACHE[cache_key] = dict(out)
    return dict(out)


def _open_text_maybe_gzip(path: Path) -> TextIO:
    if path.suffix == ".gz" or path.name.endswith(".one.gz") or path.name.endswith(".csv.gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")  # type: ignore[return-value]
    return path.open(encoding="utf-8", errors="replace")


def summarize_standard_events(path: Path, *, trace_id: str = "") -> dict[str, Any]:
    nodes: set[str] = set()
    ups = 0
    downs = 0
    t_min: float | None = None
    t_max: float | None = None
    open_contacts: dict[tuple[str, str], float] = {}
    durations: list[float] = []
    degree: Counter[str] = Counter()

    with _open_text_maybe_gzip(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 5 or parts[1] != "CONN":
                continue
            try:
                t = float(parts[0])
            except ValueError:
                continue
            a, b, state = parts[2], parts[3], parts[4].lower()
            nodes.add(a)
            nodes.add(b)
            t_min = t if t_min is None else min(t_min, t)
            t_max = t if t_max is None else max(t_max, t)
            key = (a, b) if a <= b else (b, a)
            if state == "up":
                ups += 1
                open_contacts[key] = t
                degree[a] += 1
                degree[b] += 1
            elif state == "down":
                downs += 1
                start = open_contacts.pop(key, None)
                if start is not None and t >= start:
                    durations.append(t - start)

    contacts = min(ups, downs) if ups and downs else ups
    duration = int(t_max - t_min) if t_min is not None and t_max is not None else 0
    n = len(nodes)
    dens = (2.0 * contacts) / (n * (n - 1)) if n > 1 and contacts else 0.0
    return {
        "extractor": StandardEventsContactSummaryExtractor.name,
        "trace_id": trace_id,
        "n_nodes": n,
        "events": ups + downs,
        "contacts": contacts,
        "ups": ups,
        "downs": downs,
        "up_down_balanced": ups == downs,
        "duration_seconds": duration,
        "contact_duration_count": len(durations),
        "contact_duration_mean_s": (sum(durations) / len(durations)) if durations else 0.0,
        "mean_degree_events": (sum(degree.values()) / n) if n else 0.0,
        "density_proxy": dens,
        "geometry_rule": "none_automatic; map via configured target_generators only",
    }


def summarize_rollernet_contacts(f: TextIO, *, trace_id: str = "") -> dict[str, Any]:
    # Format: id1 id2 start end seq duration
    nodes: set[str] = set()
    durations: list[int] = []
    t_min: int | None = None
    t_max: int | None = None
    n_contacts = 0
    for line in f:
        parts = line.split()
        if len(parts) < 6:
            continue
        a, b = parts[0], parts[1]
        try:
            start, end, dur = int(parts[2]), int(parts[3]), int(parts[5])
        except ValueError:
            continue
        nodes.add(a)
        nodes.add(b)
        n_contacts += 1
        durations.append(dur)
        t_min = start if t_min is None else min(t_min, start)
        t_max = end if t_max is None else max(t_max, end)
    n = len(nodes)
    duration = int((t_max or 0) - (t_min or 0))
    # Corridor parameterization hints from temporal span / density (not road geometry).
    length_m = 4000
    if duration > 0:
        # Scale corridor length mildly with duration hours (bounded).
        hours = duration / 3600.0
        length_m = int(min(8000, max(2000, 3000 + hours * 50)))
    return {
        "extractor": RollernetContactsExtractor.name,
        "trace_id": trace_id,
        "n_nodes": n,
        "contacts": n_contacts,
        "duration_seconds": duration,
        "contact_duration_mean_s": (sum(durations) / len(durations)) if durations else 0.0,
        "length_m": length_m,
        "width_m": 600,
        "branch_prob": 0.1,
        "branch_length_m": 200,
        "geometry_rule": "parameterize corridor generator only",
    }


def summarize_sassy_dsn(f: TextIO, *, trace_id: str = "") -> dict[str, Any]:
    nodes: set[str] = set()
    durations: list[float] = []
    t_min: float | None = None
    t_max: float | None = None
    n_enc = 0
    reader = csv.reader(f)
    header = next(reader, None)
    for row in reader:
        if len(row) < 4:
            continue
        a, b = row[0].strip(), row[1].strip()
        try:
            start, end = float(row[2]), float(row[3])
        except ValueError:
            continue
        nodes.add(a)
        nodes.add(b)
        n_enc += 1
        if end >= start:
            durations.append(end - start)
        t_min = start if t_min is None else min(t_min, start)
        t_max = end if t_max is None else max(t_max, end)
    n = len(nodes)
    n_clusters = max(3, min(8, int(round(n / 12)) or 3))
    nodes_per = max(4, n // n_clusters) if n_clusters else 8
    return {
        "extractor": SassyEncountersExtractor.name,
        "trace_id": trace_id,
        "n_nodes": n,
        "contacts": n_enc,
        "duration_seconds": int((t_max or 0) - (t_min or 0)),
        "contact_duration_mean_s": (sum(durations) / len(durations)) if durations else 0.0,
        "n_clusters": n_clusters,
        "nodes_per_cluster": nodes_per,
        "intra_density": 0.7,
        "inter_gap_m": 200,
        "inter_bridge_count": 2,
        "geometry_rule": "parameterize clustered_communities only",
    }


def summarize_locshare_encounters(rows: list[dict[str, str]], *, trace_id: str = "") -> dict[str, Any]:
    nodes: set[str] = set()
    t_min: float | None = None
    t_max: float | None = None
    n_enc = 0
    for row in rows:
        # Common keys: starttime/endtime/userid1/userid2 or similar
        keys = row
        a = keys.get("userid1") or keys.get("user1") or keys.get("id1") or keys.get("a")
        b = keys.get("userid2") or keys.get("user2") or keys.get("id2") or keys.get("b")
        start_s = keys.get("starttime") or keys.get("start") or keys.get("start_time")
        end_s = keys.get("endtime") or keys.get("end") or keys.get("end_time")
        if not a or not b:
            # fallback: first two numeric-ish fields
            vals = list(keys.values())
            if len(vals) < 4:
                continue
            a, b, start_s, end_s = vals[0], vals[1], vals[2], vals[3]
        nodes.add(a)
        nodes.add(b)
        n_enc += 1
        try:
            start = float(start_s)
            end = float(end_s)
        except (TypeError, ValueError):
            continue
        t_min = start if t_min is None else min(t_min, start)
        t_max = end if t_max is None else max(t_max, end)
    n = len(nodes)
    n_buildings = max(6, min(15, n // 4 or 6))
    return {
        "extractor": LocshareEncountersExtractor.name,
        "trace_id": trace_id,
        "n_nodes": n,
        "contacts": n_enc,
        "duration_seconds": int((t_max or 0) - (t_min or 0)),
        "n_buildings": n_buildings,
        "building_spacing_m": 60,
        "ring_roads": 1,
        "path_density": 0.6,
        "quad_size_m": 300,
        "n_clusters": max(3, min(8, n // 10 or 3)),
        "nodes_per_cluster": max(4, n // max(3, n // 10 or 3)),
        "intra_density": 0.6,
        "inter_gap_m": 200,
        "inter_bridge_count": 2,
        "geometry_rule": "parameterize campus_compact / clustered_communities only",
    }


_POINT_RE = re.compile(r"POINT\s*\(\s*([+-]?\d+(?:\.\d+)?)\s+([+-]?\d+(?:\.\d+)?)\s*\)", re.I)


def summarize_gps_file(
    path: Path,
    *,
    cols: dict[str, Any],
    trace_id: str = "",
    max_rows: int = 2_000_000,
) -> dict[str, Any]:
    delimiter = cols.get("delimiter") or ","
    id_col = cols.get("id")
    lat_col = cols.get("lat")
    lon_col = cols.get("lon")
    geom = cols.get("geometry")
    ts_col = cols.get("timestamp")
    ts_cols = cols.get("timestamp_columns")
    ts_fmt = cols.get("timestamp_format")
    has_header = bool(cols.get("has_header", True if lat_col or id_col else False))

    entities: set[str] = set()
    lats: list[float] = []
    lons: list[float] = []
    times: list[float] = []
    n_rows = 0

    with path.open(encoding="utf-8", errors="replace") as f:
        if geom == "wkt_point_lat_lon":
            # Roma-style: id;timestamp;POINT(lat lon) — no CSV header
            for line in f:
                if n_rows >= max_rows:
                    break
                line = line.strip()
                if not line:
                    continue
                parts = line.split(delimiter)
                if len(parts) < 3:
                    continue
                entities.add(parts[0].strip())
                # timestamp
                try:
                    if ts_fmt:
                        ts_raw = parts[1].strip()
                        # Normalize +01 / -03 → +0100 / -0300 for %z
                        if re.search(r"[+-]\d{2}$", ts_raw):
                            ts_raw = ts_raw + "00"
                        dt = datetime.strptime(ts_raw, ts_fmt)
                        times.append(dt.timestamp())
                except ValueError:
                    pass
                m = _POINT_RE.search(parts[2])
                if not m:
                    continue
                lat, lon = float(m.group(1)), float(m.group(2))
                lats.append(lat)
                lons.append(lon)
                n_rows += 1
        else:
            reader = csv.DictReader(f, delimiter=delimiter) if has_header else None
            if reader is None:
                raise ExtractorError(f"{trace_id}: non-WKT GPS requires header + named columns")
            for row in reader:
                if n_rows >= max_rows:
                    break
                if id_col and id_col in row:
                    entities.add(str(row[id_col]).strip())
                try:
                    lat = float(row[lat_col])
                    lon = float(row[lon_col])
                except (KeyError, TypeError, ValueError):
                    continue
                lats.append(lat)
                lons.append(lon)
                # timestamp
                try:
                    if ts_cols and len(ts_cols) >= 2:
                        raw = f"{row[ts_cols[0]]} {row[ts_cols[1]]}"
                        if ts_fmt:
                            times.append(datetime.strptime(raw.strip(), ts_fmt).timestamp())
                    elif ts_col and ts_fmt:
                        times.append(datetime.strptime(str(row[ts_col]).strip(), ts_fmt).timestamp())
                except (KeyError, ValueError, TypeError):
                    pass
                n_rows += 1

    if not lats:
        raise ExtractorError(f"{trace_id}: no GPS coordinates parsed from {path}")
    south, north = min(lats), max(lats)
    west, east = min(lons), max(lons)
    duration = int(max(times) - min(times)) if len(times) >= 2 else 0
    # rough extent in meters
    lat_m = (north - south) * 111_320.0
    lon_m = (east - west) * 111_320.0 * max(0.2, abs(__import__("math").cos(__import__("math").radians((south + north) / 2))))
    return {
        "extractor": GpsTraceSummaryExtractor.name,
        "trace_id": trace_id,
        "n_entities": len(entities),
        "n_points": n_rows,
        "duration_seconds": duration,
        "bbox": {"south": south, "north": north, "west": west, "east": east},
        "extent_m": {"lat_m": round(lat_m, 1), "lon_m": round(lon_m, 1)},
        "candidate_geographic_anchor": "configured_target_osm_anchors",
        "produces_map": False,
        "geometry_rule": "osm_anchor_support only; no direct road geometry from GPS",
    }


def _nearest_discrete(options: list[Any] | None, val: Any) -> Any:
    if isinstance(options, list) and options and isinstance(val, (int, float)):
        return min(options, key=lambda x: abs(float(x) - float(val)))
    return val


def map_extracted_to_generator_params(
    generator_id: str,
    extracted: dict[str, Any],
    generator_spec: dict[str, Any],
) -> dict[str, Any]:
    """Pick discrete defaults from generator spec, overlaying compatible extracted keys.

    Mapping contract is documented in
    ``scenarios/analysis/data/trace_statistic_to_generator_parameter_v2.csv``.
    Contact/GPS statistics never invent street geometry; they only snap discrete
    generator knobs that change expected topology counts (nodes/edges/clusters).
    """
    params: dict[str, Any] = {}
    discrete = (generator_spec.get("parameters") or {}) if generator_spec else {}
    for key, values in discrete.items():
        if isinstance(values, list) and values:
            params[key] = values[len(values) // 2]
    for key, val in extracted.items():
        if key in params and isinstance(val, (int, float, bool, str)):
            params[key] = _nearest_discrete(discrete.get(key), val)

    if generator_id == "clustered_communities" and "n_nodes" in extracted:
        n = max(1, int(extracted["n_nodes"]))
        if "n_clusters" in extracted:
            n_clusters = int(extracted["n_clusters"])
        else:
            n_clusters = max(3, min(8, int(round(n / 12.0)) or 3))
        if "n_clusters" in discrete:
            n_clusters = int(_nearest_discrete(discrete.get("n_clusters"), n_clusters))
        params["n_clusters"] = n_clusters
        npc = int(extracted.get("nodes_per_cluster") or max(4, n // max(n_clusters, 1)))
        if "nodes_per_cluster" in discrete:
            npc = int(_nearest_discrete(discrete.get("nodes_per_cluster"), npc))
        params["nodes_per_cluster"] = max(4, npc)
        if "density_proxy" in extracted and "intra_density" in params:
            dens = float(extracted["density_proxy"])
            # Contact density is not edge density; map into a bounded intra_density band.
            target = 0.4 + min(0.5, dens * 2.0)
            params["intra_density"] = _nearest_discrete(discrete.get("intra_density"), target)

    if generator_id == "conference_event_compact" and "n_nodes" in extracted:
        n = max(1, int(extracted["n_nodes"]))
        # Minimal documented rule: more agents → more halls / rooms (contacts ≠ floorplan).
        hall_guess = max(2, min(8, int(round(n / 16.0)) or 2))
        rooms_guess = max(4, min(16, int(round(n**0.5)) or 4))
        if "hall_count" in params:
            params["hall_count"] = _nearest_discrete(discrete.get("hall_count"), hall_guess)
        if "rooms_per_hall" in params:
            params["rooms_per_hall"] = _nearest_discrete(discrete.get("rooms_per_hall"), rooms_guess)

    if generator_id == "corridor":
        for k in ("length_m", "width_m", "branch_prob", "branch_length_m"):
            if k in extracted and k in params:
                params[k] = _nearest_discrete(discrete.get(k), extracted[k])

    if generator_id == "campus_compact" and "n_buildings" in extracted:
        if "n_buildings" in params:
            params["n_buildings"] = _nearest_discrete(discrete.get("n_buildings"), extracted["n_buildings"])

    if generator_id == "sparse_rural" and "n_nodes" in extracted:
        if "n_nodes" in params:
            params["n_nodes"] = _nearest_discrete(discrete.get("n_nodes"), extracted["n_nodes"])

    if generator_id == "disrupted_grid" and "n_nodes" in extracted:
        n = max(1, int(extracted["n_nodes"]))
        side = max(5, int(round(n**0.5)))
        for k in ("grid_rows", "grid_cols"):
            if k in params:
                params[k] = _nearest_discrete(discrete.get(k), side)

    if generator_id == "partitioned_bridge" and "n_nodes" in extracted:
        n = max(1, int(extracted["n_nodes"]))
        n_part = int(params.get("n_partitions") or extracted.get("n_partitions") or 3)
        if "n_partitions" in discrete:
            n_part = int(_nearest_discrete(discrete.get("n_partitions"), n_part))
            params["n_partitions"] = n_part
        npc = max(8, n // max(n_part, 1))
        if "nodes_per_partition" in params:
            params["nodes_per_partition"] = _nearest_discrete(discrete.get("nodes_per_partition"), npc)

    return params
