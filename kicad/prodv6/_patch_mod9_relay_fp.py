#!/usr/bin/env python3
"""Corrige footprints RL1–RL3 quebrados (fp_rect fora do bloco) no .kicad_pcb."""
from __future__ import annotations

import importlib.util
import re
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
    if '(footprint "Injet:RL1" fp_rect' not in text:
        print("  Nada a corrigir — RL footprints OK")
        return

    relay_by_ref: dict[str, list] = {}
    for fp in layout.relay_footprints():
        ref = fp[5][2]
        if ref in ("RL1", "RL2", "RL3"):
            relay_by_ref[ref] = fp

    for ref in ("RL1", "RL2", "RL3"):
        bad = rf'\t\(footprint "Injet:{ref}" fp_rect[\s\S]*?\n\t\)\n'
        m = re.search(bad, text)
        if not m:
            raise SystemExit(f"bloco quebrado {ref} nao encontrado")
        good = gen.fmt_pcb(relay_by_ref[ref], 1) + "\n"
        text = text[: m.start()] + good + text[m.end() :]

    pcb.write_text(text, encoding="utf-8")
    print("  RL1–RL3 footprints corrigidos")


if __name__ == "__main__":
    main()
