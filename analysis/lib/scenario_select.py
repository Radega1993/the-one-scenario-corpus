"""Select .settings paths from a corpus by family, TP, base, regex, or explicit list."""

from __future__ import annotations

import re
from pathlib import Path

# Scenario file names: BaseName__TP07_BurstWindow.settings
_TP_IN_NAME = re.compile(r"__(TP\d{2})_", re.I)


def tp_from_path(path: Path) -> str | None:
    m = _TP_IN_NAME.search(path.stem)
    return m.group(1).upper() if m else None


def family_from_path(path: Path, corpus_dir: Path) -> str | None:
    try:
        rel = path.relative_to(corpus_dir)
        parts = rel.parts
        if len(parts) >= 2:
            return parts[0]
    except ValueError:
        pass
    return None


def scenario_base_from_path(path: Path) -> str | None:
    stem = path.stem
    m = _TP_IN_NAME.search(stem)
    if m:
        return stem[: m.start()].rstrip("_")
    return stem


def list_families(corpus_dir: Path) -> list[str]:
    if not corpus_dir.is_dir():
        return []
    return sorted(
        d.name
        for d in corpus_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def collect_corpus_settings(corpus_dir: Path) -> list[Path]:
    return sorted(corpus_dir.glob("**/*.settings"))


def normalize_tp(tp: str) -> str:
    tp = tp.strip().upper()
    if tp.startswith("TP"):
        return tp
    if tp.isdigit():
        return f"TP{int(tp):02d}"
    return tp


def select_scenario_paths(
    corpus_dir: Path,
    repo_root: Path,
    *,
    explicit_settings: list[Path] | None = None,
    families: list[str] | None = None,
    traffic_profiles: list[str] | None = None,
    scenario_bases: list[str] | None = None,
    name_regex: str | None = None,
) -> list[Path]:
    """
    Build ordered list of .settings to run.

    - explicit_settings: if set, start from these files only; else all under corpus_dir.
    - families / traffic_profiles / scenario_bases: OR within each dimension, AND across dimensions.
    - name_regex: optional extra filter on full posix path.
    """
    if explicit_settings:
        paths = []
        for raw in explicit_settings:
            p = Path(raw)
            if not p.is_absolute():
                p = repo_root / p
            if p.is_file():
                paths.append(p.resolve())
            else:
                raise FileNotFoundError(str(p))
    else:
        paths = [p.resolve() for p in collect_corpus_settings(corpus_dir)]

    if families:
        fam_set = {f.strip() for f in families if f.strip()}
        paths = [p for p in paths if family_from_path(p, corpus_dir) in fam_set]

    if traffic_profiles:
        tp_set = {normalize_tp(t) for t in traffic_profiles if t.strip()}
        paths = [p for p in paths if tp_from_path(p) in tp_set]

    if scenario_bases:
        base_set = {b.strip() for b in scenario_bases if b.strip()}
        paths = [p for p in paths if scenario_base_from_path(p) in base_set]

    if name_regex:
        rx = re.compile(name_regex)
        paths = [p for p in paths if rx.search(p.as_posix())]

    return sorted(paths)


def parse_select_file(path: Path, repo_root: Path) -> dict[str, list[str]]:
    """
    Parse a selection file. Lines:
      path/to.scenario.settings
      family:01_urban
      tp:TP07
      base:U1_CBD_Commuting_HelsinkiMedium
      regex:U2_.*Manhattan
    """
    settings: list[str] = []
    families: list[str] = []
    tps: list[str] = []
    bases: list[str] = []
    regexes: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" in line and not line.endswith(".settings"):
            key, val = line.split(":", 1)
            key, val = key.strip().lower(), val.strip()
            if key in ("family", "familia", "fam"):
                families.append(val)
            elif key in ("tp", "traffic_profile", "perfil"):
                tps.append(val)
            elif key in ("base", "scenario_base"):
                bases.append(val)
            elif key in ("regex", "name_regex"):
                regexes.append(val)
            continue
        p = Path(line)
        if not p.is_absolute():
            p = repo_root / p
        if p.is_file():
            settings.append(str(p))
    out: dict[str, list[str]] = {
        "settings": settings,
        "families": families,
        "traffic_profiles": tps,
        "scenario_bases": bases,
    }
    if regexes:
        out["name_regex"] = "|".join(f"(?:{r})" for r in regexes)
    return out
