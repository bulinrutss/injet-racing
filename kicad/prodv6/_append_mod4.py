#!/usr/bin/env python3
"""Anexa MOD4 (buck MP1584) ao .kicad_pcb sem apagar edições KiCad."""
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


def _render(nodes: list) -> str:
    return "\n".join(gen.fmt_pcb(n, 1) for n in nodes)


def _render_list(items: list) -> str:
    return "\n".join(_render([x]) if not isinstance(x, list) else _render(x) for x in items)


def main() -> None:
    pcb = ROOT / "injet-racing-prodv6.kicad_pcb"
    text = pcb.read_text(encoding="utf-8")
    if '(footprint "Injet:MP1584"' in text:
        print("  MOD4 ja presente — nada a fazer")
        return

    fps = "\n".join(gen.fmt_pcb(fp, 1) for fp in layout.buck_footprints())
    segs = "\n".join(gen.fmt_pcb(s, 1) for s in layout.buck_traces())

    # Footprints antes dos desenhos Dwgs.User (MOD3)
    anchor = '\t(gr_rect\n\t\t(start 10 124)'
    if anchor not in text:
        raise SystemExit("ancora MOD3 gr_rect nao encontrada")
    text = text.replace(anchor, fps + "\n" + anchor, 1)

    # Trilhas antes da zone GND
    zanchor = '\t(zone\n\t\t(net "GND")\n\t\t(layer "F.Cu")'
    if zanchor not in text:
        raise SystemExit("ancora zone GND nao encontrada")
    text = text.replace(zanchor, segs + "\n" + zanchor, 1)

    # Atualizar marcadores MOD4 no Dwgs.User
    old = '\t(gr_text "+12V_PROT"\n\t\t(at 43 56.5)'
    if old in text:
        text = text.replace(old, '\t(gr_text "+12V_PROT"\n\t\t(at 43 57)', 1)
    # Inserir MOD4 rect + label após MOD3 ->CN2
    mod4_draw = "\n".join(gen.fmt_pcb(x, 1) for x in [
        layout._gr_rect(*layout.MOD4_IO["body"], width=0.2),
        layout._gr_text("MOD4", layout.MOD4_IO["body"][0] + 1, layout.MOD4_IO["body"][1] + 1, 0.7),
        layout._gr_text("+12V_PROT", 43, 57, 0.65),
        layout._gr_text("->+5V", 72, 42, 0.65),
    ])
    cn2_anchor = '\t(gr_text "->CN2"'
    text = text.replace(cn2_anchor, cn2_anchor, 1)  # no-op; insert after ->CN2 block
    insert_after = '\t(gr_text "->CN2"\n\t\t(at 46 146)\n\t\t(layer "Dwgs.User")'
    idx = text.find(insert_after)
    if idx >= 0:
        # fechar bloco ->CN2 completo antes de inserir MOD4
        close = '\t\t)\n\t)\n'
        end = text.find(close, idx)
        if end >= 0:
            end += len(close)
            text = text[:end] + "\n" + mod4_draw + text[end:]

    # +12V_PROT label at MOD4 IN (replace or add)
    if '+12V_PROT"\n\t\t(at 43 57)' not in text and '+12V_PROT"\n\t\t(at 43 56.5)' not in text:
        pass  # mod4_draw may need +12V_PROT - add via mod_io full regen later

    pcb.write_text(text, encoding="utf-8")
    print("  MOD4 footprints + trilhas anexados")
    print("  Rode: python _patch_fp_shapes.py  (C3/C5/C6)")


if __name__ == "__main__":
    main()
