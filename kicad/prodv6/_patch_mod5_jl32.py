#!/usr/bin/env python3
"""Substitui U1 STM32F4VE + trilhas MOD5 (remove rotas antigas, aplica novas)."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MOD5_FP_REFS = frozenset({"U1"})


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


def _seg_endpoints(block: str) -> tuple[tuple[float, float], tuple[float, float]] | None:
    m = re.search(
        r"\(start ([\d.-]+) ([\d.-]+)\)\s+\(end ([\d.-]+) ([\d.-]+)\)",
        block,
    )
    if not m:
        return None
    return (
        (float(m.group(1)), float(m.group(2))),
        (float(m.group(3)), float(m.group(4))),
    )


def _is_mod5_segment(block: str) -> bool:
    """Remove trilhas MOD5; preserva tronco MOD4 em y=44.5 até x=78."""
    if "(segment" not in block:
        return False
    pts = _seg_endpoints(block)
    if not pts:
        return False
    nets = ('"+5V"', '"+3V3"', '"VREF+"')
    if not any(n in block for n in nets):
        return False
    (x1, y1), (x2, y2) = pts
    min_x, max_x = min(x1, x2), max(x1, x2)
    min_y, max_y = min(y1, y2), max(y1, y2)

    if '"+5V"' in block:
        if max_y <= 44.6 and max_x <= 78:
            return False
        return min_x >= 72 or max_x >= 72

    if '"+3V3"' in block or '"VREF+"' in block:
        return min_x >= 70 and min_y >= 45

    return False


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
    kept_fps = [fp for fp in fps if _fp_ref(fp) not in MOD5_FP_REFS]

    seg_parts = re.split(r"(?<=\n)\t\(segment\n", seg_region)
    seg_head = seg_parts[0] if seg_parts else ""
    segs = ["\t(segment\n" + p for p in seg_parts[1:] if p.strip()]
    kept_segs = [s for s in segs if not _is_mod5_segment(s)]

    new_u1 = _render([layout._black_board_socket(*layout.POS_MCU["U1"])])
    new_segs = _render(layout.mcu_traces())

    out = (
        fp_head
        + "".join(kept_fps)
        + "\n"
        + new_u1
        + "\n"
        + seg_head
        + "".join(kept_segs)
        + new_segs
        + "\n"
        + post_zone
    )
    pcb.write_text(out, encoding="utf-8")
    print("  MOD5: U1 + trilhas externas aplicados (rotas antigas removidas)")
    print("  Rode: python _patch_dwgs_user.py && python _review_routes.py")


if __name__ == "__main__":
    main()
