#!/usr/bin/env python3
"""Anexa MOD7b (condicionador VR FUT-05) — só footprints + Dwgs.User; sem trilhas."""
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
    if '(property "Reference" "U9"' in text or '(property "Reference" "CN4"' in text:
        print("  MOD7b ja presente — nada a fazer")
        return

    fps = "\n".join(gen.fmt_pcb(fp, 1) for fp in layout.vr_footprints())

    anchor = '\t(footprint "MountingHole:MountingHole_3.2mm_M3"'
    if anchor not in text:
        raise SystemExit("ancora MountingHole nao encontrada")
    text = text.replace(anchor, fps + "\n\t" + anchor, 1)

    m = layout.MOD7B_IO
    markers = "\n".join(
        gen.fmt_pcb(x, 1)
        for x in [
            layout._gr_rect(*m["body"], width=0.2),
            layout._gr_text("MOD7b VR", m["body"][0] + 1, m["body"][1] + 1, 0.7),
            layout._gr_text("CN4", m["port_cn4_x"], m["port_cn4_y"], 0.55),
            layout._gr_text("VR+/VR-", m["body"][0] + 1, m["body"][1] + 4, 0.55),
            layout._gr_text("->PE7", m["port_e_x"] - 10, m["port_e_y"], 0.55),
        ]
    )
    zone = '\t(zone\n\t\t(net "GND")\n\t\t(layer "F.Cu")'
    if zone in text:
        text = text.replace(zone, markers + "\n\t" + zone, 1)
    else:
        text = text.replace(anchor, markers + "\n\t" + anchor, 1)

    pcb.write_text(text, encoding="utf-8")
    print("  MOD7b footprints anexados (sem trilhas)")
    print(f"  CN4 PCIe-6 VR @ {layout.CN4_AT} rot {layout.CN4_ROT}")
    print("  Pads CN4: 1=VR+ 2=VR- 3=GND 4-6=NC")
    print("  U9 LM393 · R90 47k · R91 100k · R92 4k7 · D40/D41 1N4148 · C40 10nF · C41 1nF")
    print("  Posicoes: prodv6_layout.py POS_VR")
    print("  Nao rode _gen_kicad_prodv6.py sobre este PCB")
    print("  Se KiCad estiver aberto: feche/reabra o PCB para ver as pecas")


if __name__ == "__main__":
    main()
