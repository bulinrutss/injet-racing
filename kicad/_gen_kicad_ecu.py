#!/usr/bin/env python3
"""
Gera projeto KiCad hierárquico — INJET RACING ECU Fase 1
Baseado em modulo/esquema-eletrico.md

Uso: python _gen_kicad_ecu.py
Saída: injet-racing-ecu.kicad_pro + folhas .kicad_sch
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = "injet-racing-ecu"
KICAD_VERSION = 20250114  # KiCad 9 / 10
GENERATOR = "injet-racing-gen"
GENERATOR_VERSION = "1.3"

# Pinos por lib_id — KiCad 10 exige (pin "N" (uuid ...)) em cada instância
PIN_NUMBERS: dict[str, list[str]] = {
    "Device:R": ["1", "2"],
    "Device:C": ["1", "2"],
    "Device:D": ["1", "2"],
    "Device:Fuse": ["1", "2"],
    "Device:Q_PMOS": ["1", "2", "3"],
    "Device:Q_NMOS": ["1", "2", "3"],
    "power:GND": ["1"],
    "power:+12V": ["1"],
    "power:+5V": ["1"],
    "power:+3V3": ["1"],
    "Injet:MP1584": ["1", "2", "3", "4"],
    "Injet:BLACK_BOARD": [str(i) for i in range(1, 25)],
    "Injet:MCP6004": ["1", "2", "3"],
    "Injet:AD8628": ["1", "2", "3", "4"],
    "Injet:REF3033": ["1", "2", "3"],
    "Injet:PC817": ["1", "2", "3", "4"],
    "Injet:SN65HVD230": ["1", "2", "3", "4", "5", "6"],
    "Injet:Relay": ["1", "2", "3", "4"],
    "Injet:CN_ATX24": [str(i) for i in range(1, 25)],
    "Injet:CN_PCIE6": [str(i) for i in range(1, 7)],
}


def uid() -> str:
    return str(uuid.uuid4())


def S(name: str) -> Any:
    from sexpdata import Symbol
    return Symbol(name)


def fmt(sexp: list) -> str:
    from kicad_sch_api.core.formatter import ExactFormatter
    return ExactFormatter().format(sexp)


# ---------------------------------------------------------------------------
# Primitivas de desenho
# ---------------------------------------------------------------------------

def pt(x: float, y: float) -> list:
    return [x, y]


def at(x: float, y: float, angle: float = 0) -> list:
    return [S("at"), x, y, angle]


def at2(x: float, y: float) -> list:
    return [S("at"), x, y]


def stroke_sheet() -> list:
    return [S("stroke"), [S("width"), 0.1524], [S("type"), S("solid")]]


def stroke(w: float = 0.254) -> list:
    return [S("stroke"), [S("width"), w], [S("type"), S("default")]]


def fill_sheet() -> list:
    return [S("fill"), [S("color"), 0, 0, 0, 0.0]]


def prop_sheet(name: str, value: str, x: float, y: float, justify: str) -> list:
    jx, jy = justify.split()
    return [
        S("property"), name, value, at(x, y),
        [S("effects"), [S("font"), [S("size"), 1.27, 1.27]], [S("justify"), S(jx), S(jy)]],
    ]


def sheet_pin(name: str, ptype: str, x: float, y: float) -> list:
    return [
        S("pin"), name, S(ptype), at(x, y),
        [S("uuid"), uid()],
        [S("effects"), [S("font"), [S("size"), 1.27, 1.27]], [S("justify"), S("right")]],
    ]


def font_effects(size: float = 1.27, hide: bool = False) -> list:
    eff: list = [S("effects"), [S("font"), [S("size"), size, size]]]
    if hide:
        eff.append([S("hide"), S("yes")])
    return eff


def prop(name: str, value: str, x: float, y: float, hide: bool = False) -> list:
    return [S("property"), name, value, at(x, y), font_effects(hide=hide)]


def wire_pts(points: list[tuple[float, float]]) -> list:
    xy = [[S("xy"), x, y] for x, y in points]
    return [S("wire"), [S("pts"), *xy], stroke(), [S("uuid"), uid()]]


def wire_h(x1: float, x2: float, y: float) -> list:
    return wire_pts([(x1, y), (x2, y)])


def wire_v(x: float, y1: float, y2: float) -> list:
    return wire_pts([(x, y1), (x, y2)])


def junction(x: float, y: float) -> list:
    return [S("junction"), at2(x, y), [S("diameter"), 0], [S("color"), 0, 0, 0, 0], [S("uuid"), uid()]]


def label_local(text: str, x: float, y: float, rot: int = 0) -> list:
    return [S("label"), text, at(x, y, rot), font_effects(), [S("uuid"), uid()]]


def label_global(text: str, x: float, y: float, shape: str = "input", rot: int = 0) -> list:
    """Global label — KiCad 10: (property ...) é filho direto, sem (properties ...)."""
    return [
        S("global_label"), text, [S("shape"), S(shape)], at(x, y, rot),
        font_effects(), [S("uuid"), uid()],
        [S("property"), "Intersheet References", "${INTERSHEET_REFS}",
         at(x, y, rot), font_effects(1.27, hide=True)],
    ]


def label_hier(text: str, x: float, y: float, shape: str = "passive", rot: int = 0) -> list:
    return [S("hierarchical_label"), text, [S("shape"), S(shape)], at(x, y, rot), font_effects(), [S("uuid"), uid()]]


def text_note(t: str, x: float, y: float, size: float = 1.5) -> list:
    return [S("text"), t, at(x, y), [S("effects"), [S("font"), [S("size"), size, size]]], [S("uuid"), uid()]]


def no_connect(x: float, y: float) -> list:
    return [S("no_connect"), at2(x, y), [S("uuid"), uid()]]


# ---------------------------------------------------------------------------
# Biblioteca de símbolos mínima (embutida em cada folha)
# ---------------------------------------------------------------------------

def pin(num: str, name: str, x: float, y: float, angle: int, ptype: str = "passive") -> list:
    return [
        S("pin"), S(ptype), S("line"), at(x, y, angle), [S("length"), 2.54],
        [S("name"), name, font_effects()], [S("number"), num, font_effects()]
    ]


def lib_sym(name: str, ref: str, body: list, pins: list, fp: str = "") -> list:
    """Unidades internas usam só o nome curto (R_0_1), não Device:R_0_1 — exigência KiCad."""
    base = name.split(":")[-1]
    return [
        S("symbol"), name,
        [S("exclude_from_sim"), S("no")], [S("in_bom"), S("yes")], [S("on_board"), S("yes")],
        prop("Reference", ref, 0, 5.08), prop("Value", base, 0, -5.08),
        prop("Footprint", fp, 0, 0, hide=True),
        [S("symbol"), f"{base}_0_1"] + body,
        [S("symbol"), f"{base}_1_1"] + pins,
    ]


def build_lib_symbols() -> list:
    syms = []

    def rect_sym(lid, ref, w, h, pins_def, fp=""):
        body = [[S("rectangle"), [S("start"), -w, h], [S("end"), w, -h], stroke(), [S("fill"), [S("type"), S("background")]]]]
        pins = [pin(n, nm, x, y, ang, pt) for n, nm, x, y, ang, pt in pins_def]
        syms.append(lib_sym(lid, ref, body, pins, fp))

    # Passivos
    syms.append(lib_sym("Device:R", "R",
        [[S("rectangle"), [S("start"), -1.016, 2.54], [S("end"), 1.016, -2.54], stroke(), [S("fill"), [S("type"), S("none")]]]],
        [pin("1", "~", -3.81, 0, 0), pin("2", "~", 3.81, 0, 180)], "Resistor_THT:R_AXIAL-0.4W"))
    syms.append(lib_sym("Device:C", "C",
        [[S("rectangle"), [S("start"), -2.032, 0.762], [S("end"), 2.032, -0.762], stroke(), [S("fill"), [S("type"), S("none")]]]],
        [pin("1", "~", -3.81, 0, 0), pin("2", "~", 3.81, 0, 180)], "Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm"))
    syms.append(lib_sym("Device:D", "D",
        [[S("polyline"), [S("pts"), [S("xy"), -1.27, 1.27], [S("xy"), -1.27, -1.27], [S("xy"), 1.27, 0], [S("xy"), -1.27, 1.27]],
          stroke(), [S("fill"), [S("type"), S("none")]]]],
        [pin("1", "K", -3.81, 0, 0), pin("2", "A", 3.81, 0, 180)], "Diode_THT:D_DO-41"))
    syms.append(lib_sym("Device:Fuse", "F",
        [[S("rectangle"), [S("start"), -3.81, 1.27], [S("end"), 3.81, -1.27], stroke(), [S("fill"), [S("type"), S("none")]]]],
        [pin("1", "~", -5.08, 0, 0), pin("2", "~", 5.08, 0, 180)], "Fuse:Fuse_BelFuse-0ZRN_OptiFuse_OptiReset"))

    # MOSFETs
    syms.append(lib_sym("Device:Q_PMOS", "Q",
        [[S("circle"), [S("center"), 0, 0], [S("radius"), 2.54], stroke(), [S("fill"), [S("type"), S("none")]]]],
        [pin("1", "G", -5.08, 0, 0), pin("2", "S", 0, 5.08, 270), pin("3", "D", 0, -5.08, 90)], ""))
    syms.append(lib_sym("Device:Q_NMOS", "Q",
        [[S("circle"), [S("center"), 0, 0], [S("radius"), 2.54], stroke(), [S("fill"), [S("type"), S("none")]]]],
        [pin("1", "G", -5.08, 0, 0), pin("2", "D", 0, -5.08, 90), pin("3", "S", 0, 5.08, 270)], ""))

    # Power flags
    for pname, pref in [("power:GND", "GND"), ("power:+12V", "V12"), ("power:+5V", "V5"), ("power:+3V3", "V3")]:
        if "GND" in pname:
            body = [[S("polyline"), [S("pts"), [S("xy"), 0, 0], [S("xy"), 0, -1.27], [S("xy"), 1.27, -1.27],
                     [S("xy"), 0, -2.54], [S("xy"), -1.27, -1.27], [S("xy"), 0, -1.27]],
                    stroke(), [S("fill"), [S("type"), S("none")]]]]
        else:
            body = [[S("text"), pref, at(0, 1.905), font_effects()]]
        syms.append(lib_sym(pname, pref, body,
                            [pin("1", pname.split(":")[1], 0, 0, 270, "power_in")], ""))

    # MP1584 module
    rect_sym("Injet:MP1584", "U", 12.7, 10.16, [
        ("1", "VIN+", -12.7, 5.08, 0, "power_in"), ("2", "VIN-", -12.7, 0, 0, "power_in"),
        ("3", "VOUT+", 12.7, 5.08, 180, "power_out"), ("4", "VOUT-", 12.7, 0, 180, "power_in"),
    ], "Converter_DCDC:Converter_DCDC_MP1584")

    # Black Board
    bb_pins = [
        ("1", "5V", -20.32, 15.24, 0, "power_in"), ("2", "3V3", -20.32, 10.16, 0, "power_out"),
        ("3", "GND", -20.32, 5.08, 0, "power_in"), ("4", "VREF+", -20.32, 0, 0, "power_in"),
    ]
    gpios = [
        "PA0", "PA1", "PA2", "PA3", "PA4", "PA5", "PA6", "PC0", "PC1",
        "PB0", "PB8", "PB9", "PE9", "PE11", "PE13", "PE14",
        "PD8", "PD9", "PD10", "PD12",
    ]
    for i, g in enumerate(gpios):
        y = 15.24 - i * 2.54
        bb_pins.append((str(5 + i), g, 20.32, y, 180, "bidirectional"))
    rect_sym("Injet:BLACK_BOARD", "U1", 20.32, 27.94, bb_pins, "")

    # ICs
    rect_sym("Injet:MCP6004", "U", 7.62, 5.08, [
        ("1", "V+", -7.62, 2.54, 0, "power_in"), ("2", "V-", -7.62, -2.54, 0, "power_in"),
        ("3", "OUT", 7.62, 0, 180, "output"),
    ], "Package_DIP:DIP-8_W7.62mm")
    rect_sym("Injet:AD8628", "U", 7.62, 5.08, [
        ("1", "V+", -7.62, 2.54, 0, "power_in"), ("2", "IN-", -7.62, 0, 0, "input"),
        ("3", "IN+", -7.62, -2.54, 0, "input"), ("4", "OUT", 7.62, 0, 180, "output"),
    ], "Package_SO:SOIC-8_3.9x4.9mm")
    rect_sym("Injet:REF3033", "U", 5.08, 5.08, [
        ("1", "VIN", -5.08, 2.54, 0, "power_in"), ("2", "GND", -5.08, -2.54, 0, "power_in"),
        ("3", "VOUT", 5.08, 0, 180, "power_out"),
    ], "Package_TO_SOT_SMD:SOT-23")
    rect_sym("Injet:PC817", "U", 7.62, 5.08, [
        ("1", "A", -7.62, 2.54, 0, "passive"), ("2", "K", -7.62, -2.54, 0, "passive"),
        ("3", "E", 7.62, -2.54, 180, "passive"), ("4", "C", 7.62, 2.54, 180, "passive"),
    ], "Package_DIP:DIP-4_W7.62mm")
    rect_sym("Injet:SN65HVD230", "U", 10.16, 7.62, [
        ("1", "VCC", -10.16, 5.08, 0, "power_in"), ("2", "GND", -10.16, 0, 0, "power_in"),
        ("3", "TXD", -10.16, -5.08, 0, "input"), ("4", "RXD", 10.16, 5.08, 180, "output"),
        ("5", "CANH", 10.16, 0, 180, "bidirectional"), ("6", "CANL", 10.16, -5.08, 180, "bidirectional"),
    ], "Package_SO:SOIC-8_3.9x4.9mm")
    rect_sym("Injet:Relay", "RL", 7.62, 7.62, [
        ("1", "COIL+", -7.62, 2.54, 0, "passive"), ("2", "COIL-", -7.62, -2.54, 0, "passive"),
        ("3", "COM", 7.62, 2.54, 180, "passive"), ("4", "NO", 7.62, -2.54, 180, "passive"),
    ], "Relay_THT:Relay_SPDT_SANYOU_SRD_Series")

    # Conectores
    rect_sym("Injet:CN_ATX24", "CN1", 5.08, 30.48, [
        (str(i), f"P{i}", -5.08, 30.48 - i * 2.54, 0, "passive") for i in range(1, 25)
    ], "Connector_PinHeader_2.54mm:PinHeader_2x12_P2.54mm")
    rect_sym("Injet:CN_PCIE6", "CN2", 5.08, 7.62, [
        (str(i), f"P{i}", 5.08, 7.62 - i * 2.54, 180, "passive") for i in range(1, 7)
    ], "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm")

    return [S("lib_symbols")] + syms


@dataclass
class SchDoc:
    title: str
    page: str
    items: list = field(default_factory=list)
    sheet_uuid: str = field(default_factory=uid)
    instance_path: str = "/"

    def add(self, *els):
        self.items.extend(els)

    def sym(self, lib_id: str, ref: str, value: str, x: float, y: float, rot: int = 0,
            fp: str = "") -> tuple[float, float]:
        """Coloca símbolo (formato KiCad 10: lib_id, dnp, pin uuids)."""
        props = [
            prop("Reference", ref, 0, 5.08), prop("Value", value, 0, -5.08),
            prop("Footprint", fp, 0, 0, hide=True),
        ]
        pin_els = [[S("pin"), n, [S("uuid"), uid()]] for n in PIN_NUMBERS.get(lib_id, ["1"])]
        self.items.append([
            S("symbol"),
            [S("lib_id"), lib_id],
            at(x, y, rot),
            [S("unit"), 1],
            [S("exclude_from_sim"), S("no")],
            [S("in_bom"), S("yes")],
            [S("on_board"), S("yes")],
            [S("dnp"), S("no")],
            [S("fields_autoplaced"), S("yes")],
            [S("uuid"), uid()],
            *props,
            *pin_els,
            [S("instances"), [S("project"), PROJECT,
             [S("path"), self.instance_path, [S("reference"), ref], [S("unit"), 1]]]],
        ])
        return x, y

    def to_sexp(self, root_path: str = "/", *, lib_symbols: bool = True) -> list:
        lib = build_lib_symbols() if lib_symbols else [S("lib_symbols")]
        return [
            S("kicad_sch"), [S("version"), KICAD_VERSION], [S("generator"), GENERATOR],
            [S("generator_version"), GENERATOR_VERSION],
            [S("uuid"), self.sheet_uuid], [S("paper"), "A3"],
            [S("title_block"), [S("title"), self.title], [S("date"), "2026-08-05"],
             [S("rev"), "Fase1"], [S("company"), "INJET RACING"], [S("comment"), 1, self.page]],
            lib,
            *self.items,
            [S("sheet_instances"), [S("path"), root_path, [S("page"), self.page]]],
            [S("embedded_fonts"), S("no")],
        ]


def place_r(doc: SchDoc, ref: str, val: str, x: float, y: float, rot: int = 0) -> None:
    doc.sym("Device:R", ref, val, x, y, rot)


def place_c(doc: SchDoc, ref: str, val: str, x: float, y: float, rot: int = 0) -> None:
    doc.sym("Device:C", ref, val, x, y, rot)


def place_d(doc: SchDoc, ref: str, val: str, x: float, y: float, rot: int = 0) -> None:
    doc.sym("Device:D", ref, val, x, y, rot)


def place_gnd(doc: SchDoc, x: float, y: float) -> None:
    doc.sym("power:GND", "#PWR", "GND", x, y + 2.54)


def place_v12(doc: SchDoc, x: float, y: float) -> None:
    doc.sym("power:+12V", "#PWR", "+12V", x, y - 2.54)


def place_v5(doc: SchDoc, x: float, y: float) -> None:
    doc.sym("power:+5V", "#PWR", "+5V", x, y - 2.54)


def place_v33(doc: SchDoc, x: float, y: float) -> None:
    doc.sym("power:+3V3", "#PWR", "+3V3", x, y - 2.54)


def net_bus(doc: SchDoc, x: float, y1: float, y2: float, name: str) -> None:
    doc.add(wire_v(x, y1, y2), label_global(name, x, (y1 + y2) / 2))


# ---------------------------------------------------------------------------
# Folhas
# ---------------------------------------------------------------------------

def sheet_power() -> SchDoc:
    d = SchDoc("Alimentação 12V → 5V + proteção", "2")
    d.add(text_note("12V bateria → fusível → IRF9540 (anti-reversa) → TVS → bulk → MP1584 → +5V\n"
                    "Black Board alimentada em +5V (LDO interno gera +3V3)", 20, 20, 1.8))

    # BAT+ entrada hierárquica
    d.add(label_hier("+12V_BAT", 30, 40, "input"), wire_h(30, 50, 40), junction(50, 40))

    # Fusível
    d.sym("Device:Fuse", "F1", "5A", 60, 40)
    d.add(wire_h(50, 57.5, 40), wire_h(62.5, 75, 40))

    # IRF9540 P-MOS
    d.sym("Device:Q_PMOS", "Q1", "IRF9540", 85, 40)
    d.add(wire_h(75, 82.5, 40), wire_h(87.5, 110, 40))
    place_r(d, "R1", "100k", 85, 55)
    place_d(d, "D1", "15V Zener", 95, 55)
    d.add(wire_v(85, 47.5, 52.5), wire_h(85, 95, 62.5), wire_v(95, 52.5, 62.5), wire_h(95, 110, 62.5))
    place_gnd(d, 110, 62.5)

    # +12V_PROT label
    d.add(label_global("+12V_PROT", 115, 40, "output"), wire_h(110, 130, 40))

    # TVS + bulk
    place_d(d, "D2", "TVS 33V", 140, 50)
    place_c(d, "C1", "220uF", 140, 35)
    place_c(d, "C2", "100nF", 155, 35)
    d.add(wire_h(130, 150, 40), wire_v(140, 40, 32.5), wire_v(140, 47.5, 50), wire_h(130, 165, 40))
    place_gnd(d, 140, 50)
    place_gnd(d, 155, 35)

    # MP1584
    d.sym("Injet:MP1584", "U2", "MP1584", 185, 40)
    d.add(wire_h(165, 172.5, 40), wire_h(165, 172.5, 35), wire_h(197.5, 220, 35))
    place_c(d, "C3", "100uF", 175, 25)
    place_c(d, "C4", "100nF", 190, 25)
    place_c(d, "C5", "220uF", 210, 25)
    place_c(d, "C6", "100nF", 225, 25)
    d.add(wire_v(185, 32.5, 25), wire_h(175, 230, 25))
    place_gnd(d, 200, 25)

    # Saídas hierárquicas
    d.add(label_hier("+5V", 230, 35, "output"), wire_h(220, 230, 35))
    d.add(label_hier("+12V_PROT", 230, 40, "output"), wire_h(130, 230, 40))
    d.add(label_hier("GND", 200, 15, "passive"), wire_h(200, 230, 15))

    # Black Board alimentação (nota + conexão lógica via hierárquico na raiz)
    d.add(text_note("U1 Black Board: pin 5V ← +5V buck | pin 3V3 → barra ECU (folha MCU)", 160, 55, 1.4))
    return d


def sheet_mcu() -> SchDoc:
    d = SchDoc("MCU — STM32F407 Black Board + REF3033", "3")
    d.add(text_note("Placa comercial Black Board — cristal/decoupling/LDO já onboard", 20, 15, 1.6))

    # Entradas hierárquicas
    for name, x, y in [("+5V", 30, 30), ("GND", 30, 20), ("VREF_IN", 30, 10)]:
        d.add(label_hier(name, x, y, "input"))

    # Black Board
    d.sym("Injet:BLACK_BOARD", "U1", "STM32F407 Black Board", 80, 50)
    d.add(wire_h(35, 60, 30), wire_h(35, 60, 20), wire_h(60, 70, 30), wire_h(60, 70, 20))
    place_v5(d, 35, 30)
    place_gnd(d, 35, 20)

    # REF3033
    d.sym("Injet:REF3033", "U8", "REF3033", 80, 15)
    place_c(d, "C10", "100nF", 65, 15)
    place_c(d, "C11", "10uF", 95, 15)
    d.add(wire_h(35, 75, 10), wire_h(75, 85, 15), wire_h(95, 110, 15))
    place_gnd(d, 80, 22)
    d.add(label_hier("VREF+", 115, 15, "output"), wire_h(110, 115, 15))

    # Barra +3V3 distribuição
    place_c(d, "C12", "10uF", 120, 35)
    place_c(d, "C13", "100nF", 135, 35)
    d.add(wire_h(100, 140, 35), label_hier("+3V3", 145, 35, "output"))
    place_v33(d, 120, 35)

    # Saídas GPIO hierárquicas (lado direito do U1 — nets nomeadas)
    gpios = [
        "PA0", "PA1", "PA2", "PA3", "PA4", "PA5", "PA6", "PC0", "PC1",
        "PB0", "PB8", "PB9", "PE9", "PE11", "PE13", "PE14",
        "PD8", "PD9", "PD10", "PD12",
    ]
    x_out = 150
    y0 = 80
    for i, g in enumerate(gpios):
        y = y0 - i * 5
        d.add(label_hier(g, x_out, y, "bidirectional"), wire_h(100, x_out - 5, 65.24 - i * 2.54))

    d.add(text_note("USB = gravação bancada only", 20, 100, 1.3))
    return d


def sheet_sensors() -> SchDoc:
    d = SchDoc("Sensores — IAT CLT MAP TPS VBat", "4")
    rails = [("+3V3", 25, 130), ("+5V", 25, 120), ("+12V_PROT", 25, 110), ("GND", 25, 100)]
    for n, x, y in rails:
        d.add(label_hier(n, x, y, "passive"))

    # IAT PA0
    d.add(label_hier("PA0", 180, 130, "bidirectional"))
    place_r(d, "R10", "2.26k", 60, 130)
    place_c(d, "C20", "100nF", 100, 130)
    d.add(wire_h(30, 57.5, 130), wire_h(62.5, 97.5, 130), wire_h(102.5, 175, 130))
    d.add(label_local("IAT→CN1-8", 110, 125))
    place_gnd(d, 100, 130)

    # CLT PA1
    d.add(label_hier("PA1", 180, 115, "bidirectional"))
    place_r(d, "R11", "2.26k", 60, 115)
    place_c(d, "C21", "100nF", 100, 115)
    d.add(wire_h(30, 57.5, 115), wire_h(62.5, 97.5, 115), wire_h(102.5, 175, 115))
    d.add(label_local("CLT→CN1-9", 110, 110))
    place_gnd(d, 100, 115)

    # MAP PA2 — divisor 10k/18k
    d.add(label_hier("PA2", 180, 95, "bidirectional"))
    place_r(d, "R12", "10k", 60, 95)
    place_r(d, "R13", "18k", 80, 105)
    place_c(d, "C22", "100nF", 100, 95)
    d.add(wire_h(30, 57.5, 95), wire_h(62.5, 77.5, 95), wire_v(80, 95, 102.5),
          wire_h(80, 80, 105), wire_h(102.5, 175, 95))
    d.add(label_local("MAP sig CN1-10", 110, 90))
    d.add(label_local("MAP +5V CN1-6", 40, 120))
    place_gnd(d, 80, 105)

    # TPS PA3
    d.add(label_hier("PA3", 180, 75, "bidirectional"))
    place_c(d, "C23", "100nF", 100, 75)
    d.add(wire_h(30, 97.5, 75), wire_h(102.5, 175, 75))
    d.add(label_local("TPS A→+3V3 B→GND wiper→PA3", 50, 70))

    # VBat PC1 — 100k/10k
    d.add(label_hier("PC1", 180, 55, "bidirectional"))
    place_r(d, "R14", "100k 1%", 60, 55)
    place_r(d, "R15", "10k 1%", 80, 65)
    place_c(d, "C24", "100nF", 100, 55)
    d.add(wire_h(30, 57.5, 55), wire_h(62.5, 77.5, 55), wire_v(80, 55, 62.5),
          wire_h(102.5, 175, 55))
    place_gnd(d, 80, 65)

    d.sym("Injet:CN_ATX24", "CN1", "ATX-24", 30, 50)
    d.add(text_note("CN1: pin6=+5V pin7=+3V3 pin8-11=sensores pin12=RPM", 20, 30, 1.3))
    return d


def sheet_rpm() -> SchDoc:
    d = SchDoc("RPM — opto PC817 (negativo bobina)", "5")
    d.add(label_hier("PB0", 150, 60, "bidirectional"))
    d.add(label_hier("+3V3", 25, 70, "passive"))
    d.add(label_hier("GND", 25, 50, "passive"))

    d.sym("Injet:PC817", "U3", "PC817", 80, 60)
    place_r(d, "R20", "10k 2W", 40, 75)
    place_r(d, "R21", "10k 2W", 40, 65)
    place_r(d, "R22", "4k7", 100, 70)
    place_d(d, "D3", "1N4148", 55, 55)
    place_c(d, "C25", "1nF", 120, 60)
    d.add(wire_h(30, 37.5, 75), wire_h(42.5, 72.5, 65), wire_h(72.5, 55, 55),
          wire_h(87.5, 97.5, 70), wire_h(102.5, 145, 60))
    d.add(label_local("COIL- CN1-12", 30, 80))
    place_gnd(d, 55, 55)
    place_gnd(d, 25, 50)
    place_v33(d, 25, 70)
    return d


def sheet_injectors() -> SchDoc:
    d = SchDoc("Injetores — 4× IRLZ44N low-side", "6")
    d.add(label_hier("+12V_PROT", 25, 100, "passive"))
    d.add(label_hier("GND", 25, 30, "passive"))
    pins = [("PE9", 140, 90), ("PE11", 140, 70), ("PE13", 140, 50), ("PE14", 140, 30)]
    for i, (sig, xo, yo) in enumerate(pins):
        ref_q = f"Q{10+i}"
        ref_rg = f"R{30+i}"
        ref_rd = f"R{40+i}"
        ref_d = f"D{10+i}"
        y = 90 - i * 20
        d.add(label_hier(sig, xo, yo, "bidirectional"))
        d.sym("Device:Q_NMOS", ref_q, "IRLZ44N", 90, y)
        place_r(d, ref_rg, "100R", 70, y)
        place_r(d, ref_rd, "10k", 90, y + 12)
        place_d(d, ref_d, "1N4007", 105, y - 8)
        d.add(wire_h(30, 87.5, y + 5), wire_h(72.5, 87.5, y), wire_h(92.5, 135, y))
        d.add(wire_v(90, y + 7.5, y + 9.5), wire_h(90, 90, y + 12), wire_h(105, 110, y - 8))
        place_gnd(d, 90, y + 12)
        d.add(label_local(f"INJ{i+1} CN1-{13+i}", 115, y - 5))
    return d


def sheet_relays() -> SchDoc:
    d = SchDoc("Relés — bomba / principal / IAC", "7")
    d.add(label_hier("+12V_PROT", 25, 90, "passive"))
    d.add(label_hier("GND", 25, 30, "passive"))
    relays = [("PD8", "RL1", "Principal"), ("PD9", "RL2", "Bomba"), ("PD10", "RL3", "IAC")]
    for i, (sig, rl, name) in enumerate(relays):
        y = 80 - i * 22
        d.add(label_hier(sig, 150, y, "bidirectional"))
        d.sym("Device:Q_NMOS", f"Q{20+i}", "2N7000", 85, y)
        d.sym("Injet:Relay", rl, f"12V 30A {name}", 110, y)
        place_r(d, f"R{50+i}", "1k", 65, y)
        place_r(d, f"R{55+i}", "10k", 85, y + 12)
        place_d(d, f"D{20+i}", "1N4007", 100, y - 6)
        d.add(wire_h(30, 82.5, y + 5), wire_h(67.5, 82.5, y), wire_h(87.5, 145, y))
        place_gnd(d, 85, y + 12)
    return d


def sheet_lambda() -> SchDoc:
    d = SchDoc("Lambda LSU 4.2 — MCP6004 + AD8628", "8")
    for n, y in [("+5V", 130), ("+3V3", 120), ("+12V_PROT", 110), ("GND", 100)]:
        d.add(label_hier(n, 25, y, "passive"))
    for g, y in [("PA4", 90), ("PA5", 80), ("PA6", 70), ("PC0", 60), ("PD12", 50)]:
        d.add(label_hier(g, 170, y, "bidirectional"))

    d.sym("Injet:MCP6004", "U4", "MCP6004", 70, 115)
    d.sym("Injet:AD8628", "U5", "AD8628", 70, 85)
    place_r(d, "R70", "61R9 1%", 100, 80)
    place_r(d, "R71", "6k8 1%", 100, 70)
    place_r(d, "R76", "10k", 55, 120)
    place_r(d, "R77", "10k", 55, 125)
    place_r(d, "R78", "1k", 55, 85)
    place_c(d, "C30", "220nF", 115, 80)
    place_c(d, "C31", "220nF", 115, 70)
    place_c(d, "C32", "100nF", 45, 130)
    place_c(d, "C33", "10uF", 45, 125)

    d.sym("Device:Q_NMOS", "Q30", "IRLZ44N", 130, 105)
    place_r(d, "R80", "100R", 110, 105)
    place_r(d, "R81", "10k", 130, 118)
    place_d(d, "D30", "1N4007", 145, 98)
    d.add(label_local("Heater H+/H- CN2", 140, 100))

    d.sym("Injet:CN_PCIE6", "CN2", "PCIe-6 Lambda", 30, 60)
    d.add(text_note("LSU 4.2 · R_ESR=6k8 · Ip shunt 61R9 · Vm=PA4 DAC", 20, 40, 1.3))
    return d


def sheet_can() -> SchDoc:
    d = SchDoc("CAN — SN65HVD230", "9")
    d.add(label_hier("PB8", 140, 65, "bidirectional"))
    d.add(label_hier("PB9", 140, 55, "bidirectional"))
    d.add(label_hier("+3V3", 25, 70, "passive"))
    d.add(label_hier("GND", 25, 50, "passive"))

    d.sym("Injet:SN65HVD230", "U6", "SN65HVD230", 80, 60)
    place_c(d, "C40", "100nF", 55, 70)
    place_c(d, "C41", "10uF", 55, 65)
    place_r(d, "R90", "120", 110, 45)
    d.add(wire_h(30, 70, 70), wire_h(30, 70, 50), wire_h(90, 135, 65), wire_h(90, 135, 55))
    d.add(label_global("CANH", 120, 50, "bidirectional"))
    d.add(label_global("CANL", 120, 40, "bidirectional"))
    d.add(label_local("→ CN1 pin20/21", 115, 35))
    place_gnd(d, 25, 50)
    place_v33(d, 25, 70)
    return d


def sheet_root(root_uuid: str, children: list) -> SchDoc:
    d = SchDoc("INJET RACING ECU — Fase 1 (TBI batch-fire)", "1")
    d.sheet_uuid = root_uuid
    d.add(text_note("Esquematico hierarquico — ver modulo/esquema-eletrico.md", 20, 15, 2))

    sw, sh = 40.0, 30.0
    for idx, (name, fname, x, y, pins) in enumerate(children):
        sh_uuid = uid()
        pin_els = []
        for i, (pname, pshape, _px, _py) in enumerate(pins):
            # pinos no lado direito da folha
            pin_els.append(sheet_pin(pname, pshape, x + sw, y + 8 + i * 6))

        d.items.append([
            S("sheet"), at2(x, y), [S("size"), sw, sh],
            [S("exclude_from_sim"), S("no")], [S("in_bom"), S("yes")],
            [S("on_board"), S("yes")], [S("dnp"), S("no")], [S("fields_autoplaced"), S("yes")],
            stroke_sheet(), fill_sheet(), [S("uuid"), sh_uuid],
            prop_sheet("Sheetname", name, x, y + sh - 0.7116, "left bottom"),
            prop_sheet("Sheetfile", fname, x, y + sh + 0.7116, "left top"),
            *pin_els,
            [S("instances"), [S("project"), PROJECT,
             [S("path"), f"/{root_uuid}", [S("page"), str(idx + 2)]]]],
        ])
    return d


def build_root_sheets() -> list[tuple]:
    """Metadados das folhas filhas para o root."""
    power_pins = [
        ("+12V_BAT", "input", 42, 52), ("+5V", "output", 42, 48),
        ("+12V_PROT", "output", 42, 44), ("GND", "passive", 42, 40),
    ]
    mcu_pins = ([("+5V", "input", 42, 52), ("GND", "input", 42, 48), ("+3V3", "output", 42, 44),
                 ("VREF+", "output", 42, 40)] +
                [(g, "bidirectional", 42, 36 - i * 0.01) for i, g in enumerate([
                    "PA0", "PA1", "PA2", "PA3", "PA4", "PA5", "PA6", "PC0", "PC1",
                    "PB0", "PB8", "PB9", "PE9", "PE11", "PE13", "PE14", "PD8", "PD9", "PD10", "PD12"])])
    # Simplified root — fewer visible pins on sheet boxes; nets connected inside children
    return [
        ("Alimentação", "sheets/power.kicad_sch", 30, 40, power_pins[:4]),
        ("MCU Black Board", "sheets/mcu.kicad_sch", 90, 40, [("+5V", "input", 42, 50), ("+3V3", "output", 42, 46), ("GND", "passive", 42, 42)]),
        ("Sensores", "sheets/sensors.kicad_sch", 150, 40, [("+3V3", "passive", 42, 50), ("+5V", "passive", 42, 46), ("+12V_PROT", "passive", 42, 42)]),
        ("RPM", "sheets/rpm.kicad_sch", 210, 40, [("PB0", "bidirectional", 42, 48), ("+3V3", "passive", 42, 44)]),
        ("Injetores", "sheets/injectors.kicad_sch", 30, 85, [("+12V_PROT", "passive", 42, 50), ("GND", "passive", 42, 46)]),
        ("Relés", "sheets/relays.kicad_sch", 90, 85, [("+12V_PROT", "passive", 42, 50), ("GND", "passive", 42, 46)]),
        ("Lambda", "sheets/lambda.kicad_sch", 150, 85, [("+5V", "passive", 42, 50), ("+12V_PROT", "passive", 42, 46), ("GND", "passive", 42, 42)]),
        ("CAN", "sheets/can.kicad_sch", 210, 85, [("+3V3", "passive", 42, 50), ("GND", "passive", 42, 46)]),
    ]


def write_kicad_pro(path: Path) -> None:
    data = {
        "board": {"design_settings": {}, "layer_presets": []},
        "boards": [],
        "cvpcb": {"equivalence_files": []},
        "libraries": {
            "pinned_footprint_libs": [],
            "pinned_symbol_libs": [],
        },
        "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1},
        "net_settings": {"classes": [], "meta": {"version": 3}, "net_auto_assign": True, "netclass_assignments": []},
        "pcbnew": {"last_paths": {"gencad": "", "idf": "", "netlist": "", "specctra_dsn": "", "step": "", "vrml": ""},
                   "page_layout_descr_file": ""},
        "schematic": {
            "legacy_lib_dir": "",
            "legacy_lib_list": [],
        },
        "sheets": [["", f"{PROJECT}.kicad_sch"]],
        "text_variables": {},
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def apply_instance_path(doc: SchDoc, path: str) -> None:
    """Corrige path hierárquico nos símbolos já colocados."""
    def walk(node):
        if not isinstance(node, list):
            return
        if len(node) >= 1 and node[0] == S("project"):
            for child in node[1:]:
                if isinstance(child, list) and len(child) >= 2 and child[0] == S("path"):
                    child[1] = path
        for child in node:
            walk(child)
    for item in doc.items:
        walk(item)


def main() -> None:
    sheets_dir = ROOT / "sheets"
    sheets_dir.mkdir(exist_ok=True)

    root_uuid = uid()
    root_path = f"/{root_uuid}"

    builders = {
        "power.kicad_sch": sheet_power,
        "mcu.kicad_sch": sheet_mcu,
        "sensors.kicad_sch": sheet_sensors,
        "rpm.kicad_sch": sheet_rpm,
        "injectors.kicad_sch": sheet_injectors,
        "relays.kicad_sch": sheet_relays,
        "lambda.kicad_sch": sheet_lambda,
        "can.kicad_sch": sheet_can,
    }

    page = 2
    for fname, fn in builders.items():
        doc = fn()
        child_path = f"{root_path}/{doc.sheet_uuid}"
        apply_instance_path(doc, child_path)
        path = sheets_dir / fname
        path.write_text(fmt(doc.to_sexp(child_path)) + "\n", encoding="utf-8")
        print(f"  wrote {path.relative_to(ROOT)}")
        page += 1

    root = sheet_root(root_uuid, build_root_sheets())
    root_path_file = ROOT / f"{PROJECT}.kicad_sch"
    root_path_file.write_text(fmt(root.to_sexp("/", lib_symbols=False)) + "\n", encoding="utf-8")
    print(f"  wrote {root_path_file.relative_to(ROOT)}")

    pro_path = ROOT / f"{PROJECT}.kicad_pro"
    write_kicad_pro(pro_path)
    print(f"  wrote {pro_path.relative_to(ROOT)}")

    # PCB vazio
    pcb = ROOT / f"{PROJECT}.kicad_pcb"
    if not pcb.exists():
        pcb.write_text(fmt([
            S("kicad_pcb"), [S("version"), 20240108], [S("generator"), GENERATOR],
            [S("general"), [S("thickness"), 1.6]],
        ]) + "\n", encoding="utf-8")
        print(f"  wrote {pcb.relative_to(ROOT)} (empty)")

    print("\nAbrir no KiCad: injet-racing-ecu.kicad_pro")


if __name__ == "__main__":
    main()
