#!/usr/bin/env python3
"""Restaura contornos/rótulos Dwgs.User (MOD3, MOD4, zonas) no .kicad_pcb."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gen = _load("gen", ROOT / "_gen_kicad_prodv6.py")
layout = _load("layout", ROOT / "prodv6_layout.py")


def main() -> None:
    pcb = ROOT / "injet-racing-prodv6.kicad_pcb"
    text = pcb.read_text(encoding="utf-8")

    if 'gr_text "MOD3"' in text:
        print("  Dwgs.User markers ja presentes — removendo bloco antigo")
        import re
        text = re.sub(
            r"\t\(gr_rect\n\t\t\(start 10 124\)[\s\S]*?\t\(gr_text \"OUT\+\"[\s\S]*?\)\n\t\)\n",
            "",
            text,
            count=1,
        )

    markers = "\n".join(
        gen.fmt_pcb(x, 1)
        for x in layout.mod_io_markers() + layout.zone_markers()
    )

    anchor = "\t(segment\n"
    idx = text.find(anchor)
    if idx < 0:
        raise SystemExit("ancora segment nao encontrada")
    text = text[:idx] + markers + "\n" + text[idx:]
    pcb.write_text(text, encoding="utf-8")
    print("  Dwgs.User: MOD3/MOD4 + zonas + IN± OUT± inseridos")


if __name__ == "__main__":
    main()
