#!/usr/bin/env python3
"""Anexa MOD5 (Black Board socket + barra +3V3 + REF3033) ao .kicad_pcb."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MOD5_REFS = frozenset({"U1", "C10", "C11", "C12", "U8"})


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
    if '(footprint "Injet:BLACK_BOARD"' in text:
        print("  MOD5 ja presente — nada a fazer")
        return

    fps = "\n".join(gen.fmt_pcb(fp, 1) for fp in layout.mcu_footprints())
    segs = "\n".join(gen.fmt_pcb(s, 1) for s in layout.mcu_traces())

    anchor = '\t(zone\n\t\t(net "GND")\n\t\t(layer "F.Cu")'
    zidx = text.find(anchor)
    if zidx < 0:
        raise SystemExit("ancora zone GND nao encontrada")

    pre = text[:zidx]
    seg_start = pre.rfind("\t(segment\n")
    if seg_start < 0:
        raise SystemExit("ancora segment nao encontrada")

    text = pre[:seg_start] + fps + "\n" + pre[seg_start:] + segs + "\n" + text[zidx:]
    pcb.write_text(text, encoding="utf-8")
    print("  MOD5 footprints + trilhas anexados")
    print("  Rode: python _patch_dwgs_user.py && python _review_routes.py")


if __name__ == "__main__":
    main()
