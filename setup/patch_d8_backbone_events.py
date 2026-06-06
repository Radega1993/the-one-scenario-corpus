#!/usr/bin/env python3
"""Ensure D8 corpus settings include ExternalEventsQueue backbone at t=6h."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
D8_DIR = REPO / "scenarios" / "corpus_v1" / "05_disaster"
BACKBONE = D8_DIR / "D8_backbone_events.txt"

BACKBONE_BLOCK = """
# Infrastructure return: forced backbone links after 6 hours
Events{n}.class = ExternalEventsQueue
Events{n}.nrofPreload = 50
Events{n}.filePath = scenarios/corpus_v1/05_disaster/D8_backbone_events.txt
"""


def _parse_events_nrof(text: str) -> int:
    m = re.search(r"^Events\.nrof\s*=\s*(\d+)\s*$", text, flags=re.MULTILINE)
    if not m:
        raise ValueError("No Events.nrof found")
    return int(m.group(1))


def _last_events_index(text: str) -> int:
    nums = [int(x) for x in re.findall(r"^Events(\d+)\.", text, flags=re.MULTILINE)]
    return max(nums) if nums else 0


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if re.search(r"^Events\d+\.class\s*=\s*ExternalEventsQueue\s*$", text, flags=re.MULTILINE):
        return False

    nrof = _parse_events_nrof(text)
    last_idx = _last_events_index(text)
    new_idx = last_idx + 1
    new_nrof = nrof + 1

    text = re.sub(
        r"^Events\.nrof\s*=\s*\d+\s*$",
        f"Events.nrof = {new_nrof}",
        text,
        count=1,
        flags=re.MULTILINE,
    )

    # Append backbone block before Report section
    insert = BACKBONE_BLOCK.format(n=new_idx)
    text = re.sub(
        r"(^\s*Report\.nrofReports)",
        insert + r"\1",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    path.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    if not BACKBONE.is_file():
        raise SystemExit(f"Missing {BACKBONE}")
    n = 0
    for p in sorted(D8_DIR.glob("D8_InfrastructureReturns_BackboneLinks__*.settings")):
        if patch_file(p):
            print(f"Patched {p.relative_to(REPO)}")
            n += 1
        else:
            print(f"Skip (already patched) {p.relative_to(REPO)}")
    print(f"Done: {n} files patched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
