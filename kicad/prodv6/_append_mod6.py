#!/usr/bin/env python3
"""Anexa MOD6 (sensores IAT/CLT/MAP/TPS/VBAT) ao .kicad_pcb sem apagar edições KiCad."""
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
    if '(property "Reference" "C24"' in text:
        print("  MOD6 ja presente — nada a fazer")
        return

    fps = "\n".join(gen.fmt_pcb(fp, 1) for fp in layout.sens_footprints())
    segs = "\n".join(gen.fmt_pcb(s, 1) for s in layout.sens_traces())

    anchor = '\t(embedded_fonts no)\n\t)\n\t(gr_rect\n\t\t(start 10 124)'
    if anchor not in text:
        raise SystemExit("ancora pos-U8 gr_rect MOD3 nao encontrada")
    text = text.replace(
        anchor,
        '\t(embedded_fonts no)\n\t)\n' + fps + '\n\t(gr_rect\n\t\t(start 10 124)',
        1,
    )

    zanchor = '\t(zone\n\t\t(net "GND")\n\t\t(layer "F.Cu")'
    if zanchor not in text:
        raise SystemExit("ancora zone GND nao encontrada")
    text = text.replace(zanchor, segs + "\n" + zanchor, 1)

    # Marcadores MOD6 (substituir label legado)
    mod6_draw = "\n".join(gen.fmt_pcb(x, 1) for x in [
        layout._gr_rect(*layout.MOD6_IO["body"], width=0.2),
        layout._gr_text("MOD6", layout.MOD6_IO["body"][0] + 1, layout.MOD6_IO["body"][1] + 1, 0.7),
        layout._gr_text("CN1 sens", 38, layout.MOD6_IO["port_n_y"], 0.55),
        layout._gr_text("->U1", layout.MOD6_IO["port_e_x"] - 4, 82, 0.55),
    ])
    old = '\t(gr_text "MOD6 SENS"\n\t\t(at 36 73 0)'
    if old in text:
        close = '\t\t)\n\t)\n'
        idx = text.find(old)
        end = text.find(close, idx)
        if end >= 0:
            end += len(close)
            text = text[:idx] + mod6_draw + text[end:]

    pcb.write_text(text, encoding="utf-8")
    print("  MOD6 footprints + trilhas anexados")
    print("  Rode: python _review_routes.py")


if __name__ == "__main__":
    main()
