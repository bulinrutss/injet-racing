#!/usr/bin/env python3
"""Substitui MOD4 por módulo MP1584 (plaquinha 4 pinos IN± OUT±)."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MOD4_REFS = frozenset({"U2", "C3", "C4", "C5", "C6", "C7", "L1", "R7", "R8"})


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gen = _load("gen", ROOT / "_gen_kicad_prodv6.py")
layout = _load("layout", ROOT / "prodv6_layout.py")


def _render(nodes: list) -> str:
    return "\n".join(gen.fmt_pcb(n, 1) for n in nodes)


def _fp_ref(block: str) -> str | None:
    m = re.search(r'\(property "Reference" "([^"]+)"', block)
    return m.group(1) if m else None


def _is_mod4_segment(block: str) -> bool:
    if "(segment" not in block:
        return False
    if not any(n in block for n in ('"+12V_PROT"', '"+5V"', '"+3V3"', '"VREF+"', '"SW"', '"BST"', '"FB"')):
        return False
    m = re.search(r"\(start ([\d.-]+) ([\d.-]+)\)", block)
    if not m:
        return False
    x, y = float(m.group(1)), float(m.group(2))
    return 26 <= x <= 80 and 36 <= y <= 120


def main() -> None:
    pcb = ROOT / "injet-racing-prodv6.kicad_pcb"
    text = pcb.read_text(encoding="utf-8")

    zone_anchor = '\t(zone\n\t\t(net "GND")\n\t\t(layer "F.Cu")'
    zidx = text.find(zone_anchor)
    if zidx < 0:
        raise SystemExit("ancora zone GND nao encontrada")

    pre_zone = text[:zidx]
    post_zone = text[zidx:]

    seg_start = pre_zone.find("\t(segment\n")
    if seg_start < 0:
        fp_region, seg_region = pre_zone, ""
    else:
        fp_region, seg_region = pre_zone[:seg_start], pre_zone[seg_start:]

    fp_parts = re.split(r"(?<=\n)\t\(footprint ", fp_region)
    fp_head = fp_parts[0]
    fps = ["\t(footprint " + p for p in fp_parts[1:]]
    kept_fps = [fp for fp in fps if _fp_ref(fp) not in MOD4_REFS]

    seg_parts = re.split(r"(?<=\n)\t\(segment\n", seg_region)
    seg_head = seg_parts[0] if seg_parts else ""
    segs = ["\t(segment\n" + p for p in seg_parts[1:] if p.strip()]
    kept_segs = [s for s in segs if not _is_mod4_segment(s)]

    new_fps = _render(layout.buck_footprints())
    new_segs = _render(layout.buck_traces())

    out = (
        fp_head
        + "".join(kept_fps)
        + "\n"
        + new_fps
        + "\n"
        + seg_head
        + "".join(kept_segs)
        + new_segs
        + "\n"
        + post_zone
    )
    pcb.write_text(out, encoding="utf-8")
    print(f"  MP1584 discreto: -{len(fps) - len(kept_fps)} fp, -{len(segs) - len(kept_segs)} trilhas")
    print("  Rode: python _review_routes.py")


if __name__ == "__main__":
    main()
