#!/usr/bin/env python3
"""Anexa MOD12 (aquecedor Q30 + R80/R81/D30) — só footprints + Dwgs.User; sem trilhas."""
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
    if '(property "Reference" "Q30"' in text:
        print("  MOD12 ja presente — nada a fazer")
        return

    fps = "\n".join(gen.fmt_pcb(fp, 1) for fp in layout.heater_footprints())

    anchor = '\t(footprint "MountingHole:MountingHole_3.2mm_M3"'
    if anchor not in text:
        raise SystemExit("ancora MountingHole nao encontrada")
    text = text.replace(anchor, fps + "\n\t" + anchor, 1)

    m12 = layout.MOD12_IO
    mod12_draw = "\n".join(
        gen.fmt_pcb(x, 1)
        for x in [
            layout._gr_rect(*m12["body"], width=0.2),
            layout._gr_text("MOD12", m12["body"][0] + 1, m12["body"][1] + 1, 0.7),
            layout._gr_text("CN2 1-2", m12["port_e_x"] - 10, m12["port_e_y"], 0.55),
            layout._gr_text("->U1", m12["port_w_x"] + 1, m12["port_w_y"], 0.55),
            layout._gr_text("+12V_PROT", m12["port_w_x"] + 1, m12["port_w_y"] - 4, 0.55),
        ]
    )
    if '\t(gr_text "MOD12"' not in text:
        # Inserir após bloco MOD11 (gr_text) se existir
        needle = '\t(gr_text "MOD11"\n\t\t(at 171.5 40 0)'
        if needle in text:
            close = "\t\t)\n\t)\n"
            idx = text.find(needle)
            end = text.find(close, idx)
            if end >= 0:
                end += len(close)
                text = text[:end] + mod12_draw + text[end:]
        else:
            text = text.replace("\t(gr_text \"MOD11\"", mod12_draw + "\n\t(gr_text \"MOD11\"", 1)

    pcb.write_text(text, encoding="utf-8")
    print("  MOD12 footprints anexados (sem trilhas — rotear manual no KiCad)")
    print("  Posicoes: prodv6_layout.py POS_HEAT")
    print("  Nao rode _gen_kicad_prodv6.py sobre este PCB")


if __name__ == "__main__":
    main()
