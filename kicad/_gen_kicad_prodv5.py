#!/usr/bin/env python3
"""
INJET RACING ECU — KiCad prodv5 (STM32 JL-32F4XX / Black Board real)

Parte de injet-racing-prodv4.kicad_pcb:
  - Footprint Injet:MCU → Injet:JL32F4XX (STM32F407VET6)
  - Pads L1/R3… renomeados para 3V3, PA0, PE9… (pinout da placa da foto)
  - Nets alinhadas ao esquemático prod (gpio_map)

Uso: python _gen_kicad_prodv5.py
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from sexpdata import Symbol, loads

ROOT = Path(__file__).resolve().parent
SRC_PCB = ROOT / "injet-racing-prodv4.kicad_pcb"
PROJECT = "injet-racing-prodv5"
GENERATOR = "injet-racing-gen"
GENERATOR_VERSION = "1.0-prodv5-jl32"

S = Symbol

# Mapeamento pads abstratos (v2–v4) → nome silkscreen JL-32F4XX / Black Board
OLD_PAD_TO_GPIO: dict[str, str] = {
    "L1": "3V3",
    "L2": "VREF+",
    "L3": "PE2",
    "L4": "PE3",
    "L5": "PE4",
    "L6": "PE5",
    "L7": "PE6",
    "L8": "PC13",
    "L9": "PC1",
    "L10": "PB0",
    "L11": "PB8",
    "L12": "PB9",
    "L13": "PE9",
    "L14": "PE11",
    "L15": "PE13",
    "L16": "PE14",
    "L17": "PD12",
    "L18": "PD8",
    "L19": "PD9",
    "L20": "PD10",
    "R1": "5V",
    "R2": "GND",
    "R3": "PA0",
    "R4": "PA1",
    "R5": "PA2",
    "R6": "PA3",
    "R7": "PA4",
    "R8": "PA5",
    "R9": "PA7",
    "R10": "PA6",
    "R11": "PC0",
    "R12": "PC2",
    "R13": "PC3",
    "R14": "PA13",
    "R15": "PA14",
    "R16": "PC4",
    "R17": "PC5",
    "R18": "PB1",
    "R19": "PB10",
    "R20": "PB11",
}

# GPIO usados na ECU → net (igual _schematic_prod_complete.py gpio_map + power)
GPIO_NETS: dict[str, str] = {
    "5V": "+5V",
    "3V3": "+3V3",
    "GND": "GND",
    "VREF+": "VREF",
    "PA0": "IAT",
    "PA1": "CLT",
    "PA2": "MAP",
    "PA3": "TPS",
    "PA4": "VM",
    "PA5": "IP",
    "PA6": "UN",
    "PC0": "RI_PULSE",
    "PC1": "VBAT",
    "PB0": "RPM_OUT",
    "PB8": "CAN_RX",
    "PB9": "CAN_TX",
    "PE9": "GINJ1",
    "PE11": "GINJ2",
    "PE13": "GINJ3",
    "PE14": "GINJ4",
    "PD8": "GRL1",
    "PD9": "GRL2",
    "PD10": "GRL3",
    "PD12": "GHEAT",
    "PA13": "SWDIO",
    "PA14": "SWCLK",
}

# Trilhas/pads ainda com net legada → net correta (PA4 = VM, não DAC_VM)
NET_RENAME: dict[str, str] = {
    "DAC_VM": "VM",
}


def _is_sym(node: Any, name: str) -> bool:
    return isinstance(node, list) and len(node) >= 1 and node[0] == S(name)


def _uid() -> str:
    return str(uuid.uuid4())


def _net_name(node: list | None) -> str | None:
    if node is None:
        return None
    if len(node) == 2:
        return str(node[1])
    if len(node) >= 3:
        return str(node[2])
    return ""


def _set_net(node: list, net: str) -> None:
    for i, sub in enumerate(node):
        if _is_sym(sub, "net"):
            if len(sub) == 2:
                node[i] = [S("net"), net]
            else:
                node[i] = [S("net"), sub[1], net]
            return
    insert_at = len(node)
    for i, sub in enumerate(node):
        if _is_sym(sub, "uuid"):
            insert_at = i
            break
    node.insert(insert_at, [S("net"), net])


def _rename_nets_tree(tree: list) -> int:
    changed = 0

    def walk(node: Any) -> None:
        nonlocal changed
        if not isinstance(node, list):
            return
        if _is_sym(node, "net"):
            cur = _net_name(node)
            if cur and cur in NET_RENAME:
                new = NET_RENAME[cur]
                if len(node) == 2:
                    node[1] = new
                elif len(node) >= 3:
                    node[2] = new
                changed += 1
        for child in node:
            walk(child)

    walk(tree)
    return changed


def _set_property(fp: list, key: str, value: str) -> None:
    for sub in fp:
        if _is_sym(sub, "property") and len(sub) > 2 and sub[1] == key:
            sub[2] = value
            return


def _add_fp_text(fp: list, text: str, at_x: float, at_y: float, layer: str = "F.SilkS", size: float = 1.0) -> None:
    fp.append([
        S("fp_text"), S("user"), text,
        [S("at"), at_x, at_y],
        [S("layer"), layer],
        [S("uuid"), _uid()],
        [S("effects"),
         [S("font"), [S("size"), size, size]],
         [S("justify"), S("left")]],
    ])


def _convert_mcu_footprint(fp: list) -> tuple[int, int]:
    """Renomeia footprint e pads; retorna (pads_renomeados, nets_atualizadas)."""
    if len(fp) > 1:
        fp[1] = "Injet:JL32F4XX"
    _set_property(fp, "Value", "JL-32F4XX STM32F407VET6")
    _set_property(fp, "Reference", "U1")

    renamed = nets_upd = 0
    has_silk = any(_is_sym(s, "fp_text") for s in fp)

    for sub in fp:
        if not _is_sym(sub, "pad"):
            continue
        old_pin = str(sub[1])
        gpio = OLD_PAD_TO_GPIO.get(old_pin, old_pin)
        if gpio != old_pin:
            sub[1] = gpio
            renamed += 1
        want_net = GPIO_NETS.get(gpio)
        if want_net:
            cur = None
            for psub in sub:
                if _is_sym(psub, "net"):
                    cur = _net_name(psub)
            if cur != want_net:
                _set_net(sub, want_net)
                nets_upd += 1

    if not has_silk:
        _add_fp_text(fp, "JL-32F4XX", -2, -52, size=1.2)
        _add_fp_text(fp, "STM32F407VET6", -2, -54.5, size=0.9)
        _add_fp_text(fp, "L=chicote ECU", -2, -57, size=0.8)
        _add_fp_text(fp, "R=GPIO", 54, -52, size=0.8)

    return renamed, nets_upd


def _update_generator_meta(tree: list) -> None:
    for i, sub in enumerate(tree):
        if _is_sym(sub, "generator"):
            tree[i] = [S("generator"), GENERATOR]
        elif _is_sym(sub, "generator_version"):
            tree[i] = [S("generator_version"), GENERATOR_VERSION]


def _fmt_atom(val: Any) -> str:
    if isinstance(val, Symbol):
        return str(val)
    if isinstance(val, float):
        return f"{val:g}"
    from sexpdata import dumps
    return dumps([val])[1:-1]


def fmt_pcb(node: Any, depth: int = 0) -> str:
    tab = "\t"
    pad = tab * depth
    if not isinstance(node, list):
        return _fmt_atom(node)
    if not node:
        return f"{pad}()"
    head = _fmt_atom(node[0])
    inline: list[Any] = []
    nested: list[list] = []
    for child in node[1:]:
        (nested if isinstance(child, list) else inline).append(child)
    if not nested:
        parts = [head] + [_fmt_atom(c) for c in inline]
        return f"{pad}({' '.join(parts)})"
    first = head + (" " + " ".join(_fmt_atom(c) for c in inline) if inline else "")
    lines = [f"{pad}({first}"]
    for child in nested:
        lines.append(fmt_pcb(child, depth + 1))
    lines.append(f"{pad})")
    return "\n".join(lines)


def _copy_project_files() -> None:
    for ext, transform in (
        ("kicad_pro", lambda t: t.replace("prodv4", PROJECT)),
        ("kicad_sch", lambda t: t.replace("prodv4", PROJECT).replace("ProdV4-2L", "ProdV5-JL32").replace(
            "STM32F407 Black Board", "JL-32F4XX STM32F407VET6"
        )),
        ("kicad_prl", lambda t: t.replace("prodv4", PROJECT)),
    ):
        src = ROOT / f"injet-racing-prodv4.{ext}"
        dst = ROOT / f"{PROJECT}.{ext}"
        if src.exists():
            dst.write_text(transform(src.read_text(encoding="utf-8")), encoding="utf-8")


def main() -> None:
    if not SRC_PCB.exists():
        raise SystemExit(f"Base v4 não encontrada: {SRC_PCB}")

    print(f"Lendo base: {SRC_PCB.name}")
    tree = loads(SRC_PCB.read_text(encoding="utf-8"))

    mcu_found = False
    pads_renamed = nets_on_pads = 0
    for item in tree:
        if _is_sym(item, "footprint") and len(item) > 1 and str(item[1]) in ("Injet:MCU", "Injet:JL32F4XX"):
            mcu_found = True
            r, n = _convert_mcu_footprint(item)
            pads_renamed += r
            nets_on_pads += n

    if not mcu_found:
        raise SystemExit("Footprint MCU não encontrado no prodv4")

    nets_renamed = _rename_nets_tree(tree)
    _update_generator_meta(tree)

    dst = ROOT / f"{PROJECT}.kicad_pcb"
    dst.write_text(fmt_pcb(tree) + "\n", encoding="utf-8")
    _copy_project_files()

    n_seg = sum(1 for x in tree if _is_sym(x, "segment"))
    n_via = sum(1 for x in tree if _is_sym(x, "via"))
    print(f"  wrote {dst.name} ({dst.stat().st_size // 1024} KB)")
    print(f"  footprint: Injet:JL32F4XX - {pads_renamed} pads renomeados (L/R -> GPIO)")
    print(f"  nets nos pads: {nets_on_pads} - nets DAC_VM->VM: {nets_renamed}")
    print(f"  layout preservado: {n_seg} segmentos, {n_via} vias")
    print(f"  wrote {PROJECT}.kicad_pro / .kicad_sch")
    print(f"\nAbrir no KiCad: {PROJECT}.kicad_pro")
    print("Pinout ECU / JL-32F4XX (gpio_map prod):")
    for gpio in sorted(GPIO_NETS):
        if gpio not in ("5V", "3V3", "GND", "VREF+"):
            print(f"    {gpio:6s} -> {GPIO_NETS[gpio]}")


if __name__ == "__main__":
    main()
