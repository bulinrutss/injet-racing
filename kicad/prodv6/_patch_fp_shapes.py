#!/usr/bin/env python3
"""Substitui fp_rect genérico por contorno do componente (F.CrtYd + F.Fab)."""
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
fmt = gen.fmt_pcb

FP_SHAPES = {
    "Injet:QREV": layout._crt_to220,
    "Injet:F1": lambda: layout._crt_capsule_h(0, 8, 1.75),
    "Injet:R1": lambda: layout._crt_capsule_v(0, 6, 1.5),
    "Injet:D1": lambda: layout._crt_capsule_v(0, 6, 1.5),
    "Injet:D2": lambda: layout._crt_capsule_v(0, 6, 1.5),
    "Injet:C1": lambda: layout._crt_radial(5, 0, 5.5),
    "Injet:C2": lambda: layout._crt_capsule_h(0, 4, 1.4),
    "Injet:C3": lambda: layout._crt_radial(5, 0, 5.5),
    "Injet:C4": lambda: layout._crt_capsule_h(0, 4, 1.4),
    "Injet:C5": lambda: layout._crt_radial(5, 0, 5.5),
    "Injet:C6": lambda: layout._crt_capsule_h(0, 4, 1.4),
}


def _render_shapes(shapes: list) -> str:
    return "\n" + "\n".join(fmt(s, 2) for s in shapes)


def _find_balanced_end(text: str, start: int) -> int:
    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i + 1
    raise ValueError(f"unbalanced at {start}")


def _replace_fp_rect(text: str, fp_name: str, new_body: str) -> tuple[str, bool]:
    marker = f'(footprint "{fp_name}"'
    fp_start = text.find(marker)
    if fp_start < 0:
        return text, False
    rect_start = text.find("(fp_rect", fp_start)
    if rect_start < 0:
        return text, False
    rect_end = _find_balanced_end(text, rect_start)
    return text[:rect_start] + new_body + text[rect_end:], True


def patch(text: str) -> str:
    for fp_name, fn in FP_SHAPES.items():
        body = _render_shapes(fn())
        text, ok = _replace_fp_rect(text, fp_name, body)
        print(f"  {'ok' if ok else 'aviso'}: {fp_name}")
    return text


def main() -> None:
    pcb = ROOT / "injet-racing-prodv6.kicad_pcb"
    text = pcb.read_text(encoding="utf-8")
    pcb.write_text(patch(text), encoding="utf-8")
    print(f"  {pcb.name} atualizado")


if __name__ == "__main__":
    main()
