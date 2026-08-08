#!/usr/bin/env python3
"""Anexa MOD9 (relés Q20–Q22) — só footprints + marcadores Dwgs.User; sem trilhas."""
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
    if '(property "Reference" "Q20"' in text:
        print("  MOD9 ja presente — nada a fazer")
        return

    fps = "\n".join(gen.fmt_pcb(fp, 1) for fp in layout.relay_footprints())

    anchor = '\t(footprint "MountingHole:MountingHole_3.2mm_M3"'
    if anchor not in text:
        raise SystemExit("ancora MountingHole nao encontrada")
    text = text.replace(anchor, fps + "\n\t" + anchor, 1)

    mod9_draw = "\n".join(
        gen.fmt_pcb(x, 1)
        for x in [
            layout._gr_rect(*layout.MOD9_IO["body"], width=0.2),
            layout._gr_text("MOD9", layout.MOD9_IO["body"][0] + 1, layout.MOD9_IO["body"][1] + 1, 0.7),
            layout._gr_text("CN1 17-19", 128, layout.MOD9_IO["port_n_y"] - 1, 0.55),
            layout._gr_text("->U1", layout.MOD9_IO["port_w_x"] + 1, layout.MOD9_IO["port_w_y"], 0.55),
            layout._gr_text("+12V_PROT", layout.MOD9_IO["port_e_x"] - 14, layout.MOD9_IO["port_e_y"], 0.55),
        ]
    )
    old = '\t(gr_text "MOD9 RELAY"\n\t\t(at 97 130 0)'
    if old in text:
        close = "\t\t)\n\t)\n"
        idx = text.find(old)
        end = text.find(close, idx)
        if end >= 0:
            end += len(close)
            text = text[:idx] + mod9_draw + text[end:]

    pcb.write_text(text, encoding="utf-8")
    print("  MOD9 footprints anexados (sem trilhas — rotear manual no KiCad)")
    print("  Posicoes: prodv6_layout.py POS_REL")
    print("  Nao rode _gen_kicad_prodv6.py sobre este PCB")


if __name__ == "__main__":
    main()
