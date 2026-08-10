#!/usr/bin/env python3
"""Anexa CN3 (PCIe-6 REL) ao leste MOD8 — footprint only; rotas depois."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


gen = _load("gen", ROOT / "_gen_kicad_prodv6.py")
layout = _load("layout", ROOT / "prodv6_layout.py")


def main() -> None:
    pcb = ROOT / "injet-racing-prodv6.kicad_pcb"
    text = pcb.read_text(encoding="utf-8")
    if '(property "Reference" "CN3"' in text:
        print("  CN3 ja presente — nada a fazer")
        return

    fp = gen.fmt_pcb(layout.cn3_footprint(), 1)
    anchor = '\t(footprint "Injet:CN2"\n\t\t(layer "F.Cu")\n\t\t(uuid "33eb5b82'
    if anchor not in text:
        anchor = '\t(footprint "MountingHole:MountingHole_3.2mm_M3"'
    text = text.replace(anchor, fp + "\n\t" + anchor, 1)

    m8 = layout.MOD8_IO
    m9 = layout.MOD9_IO
    markers = "\n".join(
        gen.fmt_pcb(x, 1)
        for x in [
            layout._gr_text("CN3", m8["port_cn3_x"], m8["port_cn3_y"], 0.55),
            layout._gr_text("->CN3", m9["port_e_x"] - 2, m9["port_e_y"], 0.55),
        ]
    )
    old_cn1 = '\t(gr_text "CN1 17-19"\n\t\t(at 128 117'
    if old_cn1 in text:
        text = text.replace(old_cn1, markers.split("\n")[1] + '\n\t(gr_text "CN1 17-19"\n\t\t(at 128 117', 1)
    elif markers not in text:
        zone = '\t(zone\n\t\t(net "GND")\n\t\t(layer "F.Cu")'
        text = text.replace(zone, markers + "\n\t" + zone, 1)

    pcb.write_text(text, encoding="utf-8")
    print(f"  CN3 PCIe-6 REL @ {layout.CN3_AT} rot {layout.CN3_ROT}")
    print("  Pads: 1=RL_MAIN 2=RL_PUMP 3=RL_IAC 4=GND 5-6=NC")
    print("  Rotas RLx.4 -> CN3 + GRL -> U1 = pendente (KiCad)")


if __name__ == "__main__":
    main()
