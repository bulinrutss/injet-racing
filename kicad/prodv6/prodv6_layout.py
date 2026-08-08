"""Mapa de zonas e passo 3 — alimentação +12V (prodv6)."""
from __future__ import annotations

import uuid
from typing import Any

from sexpdata import Symbol

S = Symbol
BOARD_W, BOARD_H = 240.0, 160.0

CN1_AT = (12.0, 8.0)
CN2_AT = (200.0, 8.0)

# Reserva de área (x1,y1,x2,y2) — outros módulos
ZONE_RESERVE = {
    "MOD4_BUCK_LDO": (24, 36, 78, 58),
    "MOD5_MCU": (74, 56, 154, 112),
    "MOD6_SENS": (14, 48, 58, 98),
    "MOD7_RPM": (52, 16, 108, 38),  # PCB real: cluster y≈20–34, stub leste
    "MOD10_CAN": (118, 18, 158, 38),
    "MOD11_LAMBDA": (158, 24, 218, 78),
    "MOD12_HEATER": (162, 24, 212, 38),
    "MOD8_INJ": (148, 82, 218, 128),
    "MOD9_RELAY": (118, 118, 188, 148),
}

# Passo 3 — proteção (canto inf-esq, abaixo dos sensores reservados)
POS_PWR = {
    "F1": (14.0, 136.0),
    "Q1": (24.0, 148.0),
    "R1": (22.0, 126.0),
    "D1": (40.0, 126.0),
    "D2": (32.0, 136.0),
    "C1": (42.0, 152.0),
    "C2": (42.0, 138.0),  # ≥6 mm acima de C1 (courtyard r=5.5 → topo C1 em y≈146.5)
}

# --- Portas I/O entre módulos (corredor sem componentes, trilhas alinhadas) ---
MOD3_IO = {
    "body": (10, 124, 54, 156),
    "port_in": (8, 112, 22, 124),
    "port_out_n": (42, 108, 54, 124),
    "port_out_e": (44, 144, 205, 152),
}
PORT_IN_X = 16.0
PORT_BUS_Y = 148.0
PORT_SPLIT_X = 48.0
PORT_OUT_N_Y = 118.0

# Entrada reservada no MOD4 — alinhada com saída norte do MOD3
MOD4_IO_IN = {"at": (48.0, 58.0), "net": "+12V_PROT", "from": "MOD3"}

# Passo 4 — módulo MP1584 (plaquinha D-SUN: 4 furos nos cantos)
# KiCad Y↑: origem U2 = canto **topo-esq** da plaquinha.
# Foto: IN-/OUT- **topo** (GND) · IN+/OUT+ **base** (+12V / +5V)
MOD4_IO = {
    "body": (26, 36, 76, 58),
    "port_in_y": 58.0,
    "port_out_y": 43.0,
    "port_x_in": 48.0,
    "port_x_out": 78.0,
}
POS_BUCK = {
    "U2": (48.0, 52.0),
    "C3": (30.0, 50.0),
    "C4": (30.0, 38.0),
    "C5": (68.0, 50.0),
    "C6": (68.0, 38.0),
}
BUCK_W = 17.0
BUCK_H = 12.0

# Passo 5 — STM32F4VE (headers laterais 2×24 — jl32_pinout.py)
MOD5_IO = {
    "body": (72, 46, 156, 114),
    "port_5v_in": (78.0, 44.5),
    "port_3v3_out": (156.0, 46.0),
    "corridor_w_x": 72.0,
    "corridor_e_5v_x": 146.0,
    "corridor_e_3v3_x": 150.0,
    "corridor_e_vref_x": 153.0,
    "corridor_n_y": 44.0,
    "bus_south_y": 46.0,
    "pin_x_lo": 86.0,
    "pin_x_ri": 138.54,
}
POS_MCU = {
    "U1": (86.0, 108.0),
    "C10": (142.0, 64.0),
    "C11": (142.0, 72.0),
    "C12": (142.0, 96.0),
    "U8": (148.0, 88.0),
}

# Passo 6 — sensores (IAT CLT MAP TPS VBAT) · esquema §3
MOD6_IO = {
    "body": (14, 48, 58, 98),
    "port_n_y": 14.0,
    "port_e_x": 132.0,
    "bus_w_x": 14.0,
    "bus_e_x": 56.0,
}
POS_SENS = {
    "R10": (16.0, 94.0),
    "C20": (26.0, 94.0),
    "R18": (34.0, 94.0),
    "R11": (16.0, 86.0),
    "C21": (26.0, 86.0),
    "R19": (34.0, 86.0),
    "R12": (16.0, 78.0),
    "R13": (22.0, 78.0),
    "C22": (26.0, 78.0),
    "R16": (34.0, 78.0),
    "C23": (26.0, 70.0),
    "R17": (34.0, 70.0),
    "R14": (16.0, 62.0),
    "R15": (24.0, 54.0),
    "C24": (26.0, 62.0),
}
CN1_SENS = {
    6: (32.0, 14.0),
    7: (36.0, 14.0),
    8: (40.0, 14.0),
    9: (44.0, 14.0),
    10: (48.0, 14.0),
    11: (52.0, 14.0),
}
U1_AT_PCB = (86.0, 108.0)  # origem footprint BLACK_BOARD no .kicad_pcb
# Destinos J2 esquerda — ver jl32_pinout.U1_SENS_PAD
U1_SENS = {
    "IAT": (86.0, 67.36),    # L16O PC9
    "CLT": (86.0, 64.82),    # L17O PC7
    "MAP": (86.0, 77.52),    # L12O PC11
    "TPS": (88.54, 64.82),   # L17I PC8
    "VBAT": (88.54, 62.28),  # L18I PC6
}
MOD6_CORRIDOR = {
    "IAT": 86.0,
    "CLT": 86.0,
    "MAP": 86.0,
    "TPS": 88.54,
    "VBAT": 88.54,
}
BB_PITCH = 2.54
BB_COL_LO = 0.0
BB_COL_LI = 2.54
BB_COL_RO = 50.0
BB_COL_RI = 52.54
BB_W = BB_COL_RI + 2.54


def _jl32_import():
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "jl32", Path(__file__).resolve().parent / "jl32_pinout.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _jl32_row_y(row: int) -> float:
    return -row * BB_PITCH


def _jl32_abs(row: int, col_x: float) -> tuple[float, float]:
    ox, oy = POS_MCU["U1"]
    return (ox + col_x, oy + _jl32_row_y(row))


def _jl32_power_5v() -> tuple[float, float]:
    return _jl32_abs(0, BB_COL_RO)


def _jl32_power_3v3_left() -> tuple[float, float]:
    return _jl32_abs(0, BB_COL_LO)


def _jl32_power_3v3_right() -> tuple[float, float]:
    return _jl32_abs(2, BB_COL_RO)


def _jl32_vref() -> tuple[float, float]:
    jl = _jl32_import()
    return _jl32_abs(jl.VREF_ROW, jl.VREF_COL)


def _mod_pads() -> dict[str, tuple[float, float, str]]:
    """Pads absolutos — topo=GND, base=+ (como plaquinha D-SUN)."""
    ox, oy = POS_BUCK["U2"]
    w, h = BUCK_W, BUCK_H
    return {
        "IN-": (ox, oy, "GND"),
        "IN+": (ox, oy - h, "+12V_PROT"),
        "OUT-": (ox + w, oy, "GND"),
        "OUT+": (ox + w, oy - h, "+5V"),
    }


def _uid() -> str:
    return str(uuid.uuid4())


def _gr_rect(x1, y1, x2, y2, layer="Dwgs.User", width=0.15, dash=False, fill=False) -> list:
    return [
        S("gr_rect"),
        [S("start"), x1, y1], [S("end"), x2, y2],
        [S("stroke"), [S("width"), width], [S("type"), S("dash") if dash else S("solid")]],
        [S("layer"), layer],
        [S("fill"), S("yes") if fill else S("no")],
        [S("uuid"), _uid()],
    ]


def _gr_text(txt: str, x: float, y: float, size: float = 0.9) -> list:
    return [
        S("gr_text"), txt,
        [S("at"), x, y],
        [S("layer"), "Dwgs.User"],
        [S("uuid"), _uid()],
        [S("effects"), [S("font"), [S("size"), size, size]], [S("justify"), S("left")]],
    ]


def _gr_line(x1, y1, x2, y2, width=0.1, dash=True) -> list:
    return [
        S("gr_line"),
        [S("start"), x1, y1], [S("end"), x2, y2],
        [S("stroke"), [S("width"), width], [S("type"), S("dash") if dash else S("solid")]],
        [S("layer"), "Dwgs.User"],
        [S("uuid"), _uid()],
    ]


def _prop(key: str, val: str, layer: str = "F.SilkS", hide: bool = False) -> list:
    p = [
        S("property"), key, val,
        [S("at"), 0, -3 if key == "Reference" else 3, 0],
        [S("layer"), layer],
        [S("uuid"), _uid()],
        [S("effects"), [S("font"), [S("size"), 1, 1]]],
    ]
    if hide:
        p.insert(4, [S("hide"), S("yes")])
    return p


def _pad(num: str, x: float, y: float, net: str, od: float = 1.55, drill: float = 0.85) -> list:
    el = [
        S("pad"), num, S("thru_hole"), S("circle"),
        [S("at"), x, y],
        [S("size"), od, od],
        [S("drill"), drill],
        [S("layers"), "*.Cu", "*.Mask"],
        [S("remove_unused_layers"), S("no")],
        [S("uuid"), _uid()],
    ]
    if net:
        el.insert(-1, [S("net"), net])
    return el


def _fp_line(x1, y1, x2, y2, layer="F.CrtYd", w=0.05) -> list:
    return [
        S("fp_line"),
        [S("start"), x1, y1], [S("end"), x2, y2],
        [S("stroke"), [S("width"), w], [S("type"), S("solid")]],
        [S("layer"), layer],
        [S("uuid"), _uid()],
    ]


def _fp_circle(cx: float, cy: float, r: float, layer="F.CrtYd") -> list:
    return [
        S("fp_circle"),
        [S("center"), cx, cy],
        [S("end"), cx + r, cy],
        [S("stroke"), [S("width"), 0.05], [S("type"), S("solid")]],
        [S("layer"), layer],
        [S("fill"), S("no")],
        [S("uuid"), _uid()],
    ]


def _crt_capsule_h(x0: float, x1: float, r: float, layers=("F.CrtYd", "F.Fab")) -> list:
    out: list = []
    for layer in layers:
        w = 0.1 if layer == "F.Fab" else 0.05
        out.append(_fp_line(x0, r, x1, r, layer, w))
        out.append(_fp_line(x0, -r, x1, -r, layer, w))
        out.append(_fp_circle(x0, 0, r, layer))
        out.append(_fp_circle(x1, 0, r, layer))
    return out


def _crt_capsule_v(y0: float, y1: float, r: float, layers=("F.CrtYd", "F.Fab")) -> list:
    out: list = []
    for layer in layers:
        w = 0.1 if layer == "F.Fab" else 0.05
        out.append(_fp_line(r, y0, r, y1, layer, w))
        out.append(_fp_line(-r, y0, -r, y1, layer, w))
        out.append(_fp_circle(0, y0, r, layer))
        out.append(_fp_circle(0, y1, r, layer))
    return out


def _crt_to220(layers=("F.CrtYd", "F.Fab")) -> list:
    """TO-220 — pads G/D/S em y=0, corpo acima (+y)."""
    out: list = []
    w_body, h_body, tab_w, tab_h = 5.5, 14.5, 2.5, 3.0
    y_pin = 1.27
    for layer in layers:
        w = 0.1 if layer == "F.Fab" else 0.05
        out.append(_fp_line(-w_body, y_pin, w_body, y_pin, layer, w))
        out.append(_fp_line(w_body, y_pin, w_body, y_pin - h_body, layer, w))
        out.append(_fp_line(w_body, y_pin - h_body, -w_body, y_pin - h_body, layer, w))
        out.append(_fp_line(-w_body, y_pin - h_body, -w_body, y_pin, layer, w))
        out.append(_fp_line(-tab_w, y_pin, -tab_w, y_pin + tab_h, layer, w))
        out.append(_fp_line(-tab_w, y_pin + tab_h, tab_w, y_pin + tab_h, layer, w))
        out.append(_fp_line(tab_w, y_pin + tab_h, tab_w, y_pin, layer, w))
    return out


def _crt_radial(cx: float, cy: float, r: float, layers=("F.CrtYd", "F.Fab")) -> list:
    return [_fp_circle(cx, cy, r, layer) for layer in layers]


def _fp_rect(x1, y1, x2, y2, layer="F.CrtYd") -> list:
    return [
        S("fp_rect"),
        [S("start"), x1, y1], [S("end"), x2, y2],
        [S("stroke"), [S("width"), 0.05], [S("type"), S("solid")]],
        [S("layer"), layer],
        [S("fill"), S("no")],
        [S("uuid"), _uid()],
    ]


def _footprint(name: str, ref: str, val: str, ox: float, oy: float, extras: list) -> list:
    return [
        S("footprint"), name,
        [S("layer"), "F.Cu"],
        [S("uuid"), _uid()],
        [S("at"), ox, oy],
        _prop("Reference", ref),
        _prop("Value", val, "F.Fab"),
        _prop("Datasheet", "", hide=True),
        _prop("Description", "", hide=True),
        [S("duplicate_pad_numbers_are_jumpers"), S("no")],
        *extras,
        [S("embedded_fonts"), S("no")],
    ]


def _xy(v) -> float:
    if isinstance(v, (tuple, list)):
        return float(v[0])
    return float(v)


def _segment(x1, y1, x2, y2, net: str, layer: str = "F.Cu", width: float = 0.8) -> list:
    return [
        S("segment"),
        [S("start"), _xy(x1), _xy(y1)], [S("end"), _xy(x2), _xy(y2)],
        [S("width"), width],
        [S("layer"), layer],
        [S("net"), net],
        [S("uuid"), _uid()],
    ]


def _via(x: float, y: float, net: str) -> list:
    return [
        S("via"),
        [S("at"), x, y],
        [S("size"), 0.8],
        [S("drill"), 0.4],
        [S("layers"), "F.Cu", "B.Cu"],
        [S("net"), net],
        [S("uuid"), _uid()],
    ]


def _axial(ref: str, val: str, prefix: str, net_a: str, net_b: str, ox: float, oy: float, span: float = 8.0) -> list:
    return _footprint(
        f"Injet:{prefix}", ref, val, ox, oy,
        [*_crt_capsule_h(0, span, 1.75), _pad("A", 0, 0, net_a), _pad("B", span, 0, net_b)],
    )


def _cap(ref: str, val: str, ox: float, oy: float, net: str, wide: bool = False) -> list:
    span = 10.0 if wide else 4.0
    od = 2.3 if wide else 1.55
    r = 5.5 if wide else 2.5
    body = _crt_radial(span / 2, 0, r) if wide else _crt_capsule_h(0, span, 1.4)
    return _footprint(
        f"Injet:{ref}", ref, val, ox, oy,
        [*body, _pad("A", 0, 0, net, od=od), _pad("B", span, 0, "GND", od=od)],
    )


def _diode(ref: str, val: str, ox: float, oy: float, net_a: str, net_k: str) -> list:
    return _footprint(
        f"Injet:{ref}", ref, val, ox, oy,
        [*_crt_capsule_v(0, 6, 1.5), _pad("A", 0, 6, net_a), _pad("K", 0, 0, net_k)],
    )


def _qrev(ox: float, oy: float) -> list:
    return _footprint(
        "Injet:QREV", "Q1", "IRF9540", ox, oy,
        [
            *_crt_to220(),
            _pad("G", 0, 0, "QG", od=2.15, drill=1.05),
            _pad("D", 2.54, 0, "+12V_IN", od=2.15, drill=1.05),
            _pad("S", 5.08, 0, "+12V_PROT", od=2.15, drill=1.05),
        ],
    )


def power_footprints() -> list:
    p = POS_PWR
    return [
        _axial("F1", "5A", "F1", "+12V_BAT", "+12V_IN", *p["F1"]),
        _qrev(*p["Q1"]),
        _footprint("Injet:R1", "R1", "100k", *p["R1"], [
            *_crt_capsule_v(0, 6, 1.5), _pad("B", 0, 0, "GND"), _pad("A", 0, 6, "QG"),
        ]),
        _diode("D1", "15V Zener", *p["D1"], "QG", "GND"),
        _diode("D2", "TVS 33V", *p["D2"], "+12V_PROT", "GND"),
        _cap("C1", "220uF", *p["C1"], "+12V_PROT", wide=True),
        _cap("C2", "100nF", *p["C2"], "+12V_PROT", wide=False),
    ]


def power_traces() -> list:
    ox, oy = CN1_AT
    qx, qy = POS_PWR["Q1"]
    fx, fy = POS_PWR["F1"]
    cn1_1 = (ox + 0, oy + 6)
    cn1_2 = (ox + 4, oy + 6)
    f1_a = (fx + 0, fy + 0)
    f1_b = (fx + 8, fy + 0)
    q1_d = (qx + 2.54, qy + 0)
    q1_g = (qx + 0, qy + 0)
    q1_s = (qx + 5.08, qy + 0)
    r1_a = (POS_PWR["R1"][0], POS_PWR["R1"][1] + 6)
    d1_a = (POS_PWR["D1"][0], POS_PWR["D1"][1] + 6)
    c1_a = (POS_PWR["C1"][0], POS_PWR["C1"][1])
    c2_a = (POS_PWR["C2"][0], POS_PWR["C2"][1])
    d2_a = (POS_PWR["D2"][0], POS_PWR["D2"][1] + 6)
    cn2_1 = (CN2_AT[0] + 0, CN2_AT[1] + 6)
    in_y = 136.0
    bus_y = PORT_BUS_Y
    split_x = PORT_SPLIT_X
    out_n_y = PORT_OUT_N_Y
    w12 = 1.2

    segs = [
        # IN: CN1 → corredor x=16 (porta IN) → F1.A
        _segment(*cn1_1, *cn1_2, "+12V_BAT", width=w12),
        _segment(cn1_2[0], cn1_2[1], PORT_IN_X, in_y, "+12V_BAT", "B.Cu", w12),
        _segment(PORT_IN_X, in_y, f1_a[0], f1_a[1], "+12V_BAT", "B.Cu", w12),
        # interno MOD3 (sem cobre através do F1)
        _segment(f1_b[0], f1_b[1], q1_d[0], f1_b[1], "+12V_IN", "B.Cu", w12),
        _segment(q1_d[0], f1_b[1], q1_d[0], q1_d[1], "+12V_IN", "B.Cu", w12),
        _segment(q1_g[0], q1_g[1], q1_g[0], r1_a[1], "QG", width=0.6),
        _segment(q1_g[0], r1_a[1], r1_a[0], r1_a[1], "QG", width=0.6),
        _segment(r1_a[0], r1_a[1], d1_a[0], d1_a[1], "QG", width=0.6),
        # barramento interno +12V_PROT até junção de portas
        _segment(q1_s[0], q1_s[1], q1_s[0], bus_y, "+12V_PROT", "B.Cu", w12),
        _segment(q1_s[0], bus_y, split_x, bus_y, "+12V_PROT", "B.Cu", w12),
        _segment(c1_a[0], c1_a[1], c1_a[0], bus_y, "+12V_PROT", "B.Cu", w12),
        _segment(c2_a[0], c2_a[1], c2_a[0], bus_y, "+12V_PROT", "B.Cu", w12),
        _segment(d2_a[0], d2_a[1], d2_a[0], bus_y, "+12V_PROT", "B.Cu", w12),
        # OUT-N → MOD4 (B.Cu x=48 sobe)
        _segment(split_x, bus_y, split_x, out_n_y, "+12V_PROT", "B.Cu", w12),
        # OUT-E → CN2 / futuros módulos (corredor sul y=148)
        _segment(split_x, bus_y, 200.0, bus_y, "+12V_PROT", "B.Cu", w12),
        _segment(200.0, bus_y, cn2_1[0], cn2_1[1], "+12V_PROT", "B.Cu", w12),
    ]
    return segs


def _mp1584_module(ox: float, oy: float) -> list:
    """Plaquinha buck 4 pinos — origem topo-esq; − topo / + base."""
    w, h = BUCK_W, BUCK_H
    return _footprint(
        "Injet:MP1584", "U2", "MP1584", ox, oy,
        [
            *_crt_dcdc_module_tl(w, h),
            _pad("1", 0, -h, "+12V_PROT", od=2.0, drill=1.0),
            _pad("2", 0, 0, "GND", od=2.0, drill=1.0),
            _pad("3", w, -h, "+5V", od=2.0, drill=1.0),
            _pad("4", w, 0, "GND", od=2.0, drill=1.0),
        ],
    )


def _crt_dcdc_module_tl(w: float, h: float, layers=("F.CrtYd", "F.Fab")) -> list:
    """Retângulo plaquinha — origem no canto topo-esq, Y desce na base."""
    out: list = []
    for layer in layers:
        lw = 0.1 if layer == "F.Fab" else 0.05
        out.append(_fp_line(0, 0, w, 0, layer, lw))
        out.append(_fp_line(w, 0, w, -h, layer, lw))
        out.append(_fp_line(w, -h, 0, -h, layer, lw))
        out.append(_fp_line(0, -h, 0, 0, layer, lw))
    return out


def _crt_dcdc_module(w: float, h: float, layers=("F.CrtYd", "F.Fab")) -> list:
    out: list = []
    for layer in layers:
        lw = 0.1 if layer == "F.Fab" else 0.05
        out.append(_fp_line(0, 0, w, 0, layer, lw))
        out.append(_fp_line(w, 0, w, h, layer, lw))
        out.append(_fp_line(w, h, 0, h, layer, lw))
        out.append(_fp_line(0, h, 0, 0, layer, lw))
    return out


def buck_footprints() -> list:
    p = POS_BUCK
    return [
        _mp1584_module(*p["U2"]),
        _cap("C3", "100uF", *p["C3"], "+12V_PROT", wide=True),
        _cap("C4", "100nF", *p["C4"], "+12V_PROT", wide=False),
        _cap("C5", "220uF", *p["C5"], "+5V", wide=True),
        _cap("C6", "100nF", *p["C6"], "+5V", wide=False),
    ]


def _tap_cap_a(ox: float, oy: float, bus_x: float, bus_y: float, net: str,
               layer: str = "B.Cu", width: float = 1.0) -> list:
    """Pad A em (ox,oy). Bus deslocado — não cruza pad B (GND zone)."""
    segs = []
    if abs(bus_x - ox) > 0.01:
        segs.append(_segment(bus_x, bus_y, ox, bus_y, net, layer, width))
    if abs(bus_y - oy) > 0.01:
        segs.append(_segment(ox, bus_y, ox, oy, net, layer, width))
    return segs


def buck_traces() -> list:
    pads = _mod_pads()
    in_p = (pads["IN+"][0], pads["IN+"][1])
    out_p = (pads["OUT+"][0], pads["OUT+"][1])
    px_in = MOD4_IO["port_x_in"]
    px_out = MOD4_IO["port_x_out"]
    bus12_x = 46.0
    in_y = in_p[1]
    bus5_y = 44.5
    w12, w5 = 1.2, 1.0

    return [
        # +12V_PROT: MOD3 → C3/C4 → IN+ (baixo-esq da plaquinha)
        _segment(px_in, PORT_OUT_N_Y, bus12_x, PORT_OUT_N_Y, "+12V_PROT", "B.Cu", w12),
        _segment(bus12_x, PORT_OUT_N_Y, bus12_x, in_y, "+12V_PROT", "B.Cu", w12),
        *_tap_cap_a(POS_BUCK["C3"][0], POS_BUCK["C3"][1], bus12_x, 52.5, "+12V_PROT", width=w12),
        *_tap_cap_a(POS_BUCK["C4"][0], POS_BUCK["C4"][1], bus12_x, 41.0, "+12V_PROT", width=w12),
        _segment(bus12_x, in_y, in_p[0], in_p[1], "+12V_PROT", "B.Cu", w12),
        # +5V: OUT+ (baixo-dir) → C5/C6 → porta leste
        _segment(out_p[0], out_p[1], out_p[0], bus5_y, "+5V", "B.Cu", w5),
        _segment(out_p[0], bus5_y, px_out, bus5_y, "+5V", "B.Cu", w5),
        _segment(POS_BUCK["C5"][0], bus5_y, POS_BUCK["C5"][0], POS_BUCK["C5"][1], "+5V", "B.Cu", w5),
        _segment(POS_BUCK["C6"][0], bus5_y, POS_BUCK["C6"][0], POS_BUCK["C6"][1], "+5V", "B.Cu", w5),
    ]


def _black_board_socket(ox: float, oy: float) -> list:
    """Socket STM32F4VE — J2 29f + J3 24f (silk inferior V33)."""
    jl = _jl32_import()
    h = BB_PITCH * (len(jl.JL32_LEFT) - 1)
    pads: list = []
    for row, (lo, li) in enumerate(jl.JL32_LEFT):
        y = _jl32_row_y(row)
        pads.append(_pad(f"L{row}O", BB_COL_LO, y, jl.gpio_net(lo), od=1.55, drill=0.85))
        pads.append(_pad(f"L{row}I", BB_COL_LI, y, jl.gpio_net(li), od=1.55, drill=0.85))
    for row, (ro, ri) in enumerate(jl.JL32_RIGHT):
        y = _jl32_row_y(row)
        pads.append(_pad(f"R{row}O", BB_COL_RO, y, jl.gpio_net(ro), od=1.55, drill=0.85))
        pads.append(_pad(f"R{row}I", BB_COL_RI, y, jl.gpio_net(ri), od=1.55, drill=0.85))
    return _footprint(
        "Injet:BLACK_BOARD", "U1", "STM32F4VE", ox, oy,
        [*_crt_dcdc_module_tl(BB_W, h), *pads],
    )


def _ref3033(ox: float, oy: float) -> list:
    return _footprint(
        "Injet:U8", "U8", "REF3033", ox, oy,
        [
            *_crt_capsule_h(0, 3.5, 1.0),
            _pad("1", 0, 0, "+3V3", od=1.2, drill=0.65),
            _pad("2", 1.75, -2.5, "GND", od=1.2, drill=0.65),
            _pad("3", 3.5, 0, "VREF+", od=1.2, drill=0.65),
        ],
    )


def mcu_footprints() -> list:
    p = POS_MCU
    return [
        _black_board_socket(*p["U1"]),
        _cap("C11", "10uF", *p["C11"], "+3V3", wide=False),
        _cap("C10", "100nF", *p["C10"], "+3V3", wide=False),
        _cap("C12", "10uF", *p["C12"], "VREF+", wide=False),
        _ref3033(*p["U8"]),
    ]


def mcu_traces() -> list:
    """MOD5 — rotas só fora do socket (O|N|S|E); stubs curtos nos pads de power."""
    jl = _jl32_import()
    cx_w = MOD5_IO["corridor_w_x"]
    cx_e5 = MOD5_IO["corridor_e_5v_x"]
    cx_e33 = MOD5_IO["corridor_e_3v3_x"]
    cx_ev = MOD5_IO["corridor_e_vref_x"]
    y_s = MOD5_IO["bus_south_y"]
    px_out = MOD5_IO["port_3v3_out"][0]
    port5_x, port5_y = MOD5_IO["port_5v_in"]
    pvref = _jl32_vref()
    ux, uy = POS_MCU["U8"]
    w5, w33 = 1.0, 1.0
    vref_y = pvref[1] - 1.27

    segs: list = []

    def tie_row(row: int, net: str, w: float, lo: float, li: float) -> None:
        a, b = _jl32_abs(row, lo), _jl32_abs(row, li)
        segs.append(_segment(a[0], a[1], b[0], b[1], net, "B.Cu", w))

    def col_tie(rows: tuple[int, ...], net: str, w: float, col: float) -> None:
        for i in range(len(rows) - 1):
            a, b = _jl32_abs(rows[i], col), _jl32_abs(rows[i + 1], col)
            segs.append(_segment(a[0], a[1], b[0], b[1], net, "B.Cu", w))

    def stub_from_w(row: int, col: float, net: str, w: float) -> None:
        p = _jl32_abs(row, col)
        segs.append(_segment(cx_w, p[1], p[0], p[1], net, "B.Cu", w))

    def stub_from_e(row: int, col: float, net: str, w: float, cx_e: float) -> None:
        p = _jl32_abs(row, col)
        segs.append(_segment(p[0], p[1], cx_e, p[1], net, "B.Cu", w))

    y5_hi = _jl32_abs(jl.RIGHT_5V_ROWS[0], BB_COL_RO)[1]

    # +5V IN — J3 dir. rows 0–1: corredor N/E dedicado (x=146)
    for row in jl.RIGHT_5V_ROWS:
        tie_row(row, "+5V", w5, BB_COL_RO, BB_COL_RI)
    col_tie(jl.RIGHT_5V_ROWS, "+5V", w5, BB_COL_RO)
    col_tie(jl.RIGHT_5V_ROWS, "+5V", w5, BB_COL_RI)
    segs += [
        _segment(port5_x, port5_y, cx_e5, port5_y, "+5V", "B.Cu", w5),
        _segment(cx_e5, port5_y, cx_e5, y5_hi, "+5V", "B.Cu", w5),
    ]
    stub_from_e(jl.RIGHT_5V_ROWS[0], BB_COL_RO, "+5V", w5, cx_e5)
    stub_from_e(jl.RIGHT_5V_ROWS[1], BB_COL_RO, "+5V", w5, cx_e5)

    # +3V3 OUT — J2 esq. rows 0–1 + J3 dir. rows 2–3 → barra sul y=46 (corredor x=150)
    for row in jl.LEFT_3V3_ROWS:
        tie_row(row, "+3V3", w33, BB_COL_LO, BB_COL_LI)
    for row in jl.RIGHT_3V3_ROWS:
        tie_row(row, "+3V3", w33, BB_COL_RO, BB_COL_RI)
    col_tie(jl.LEFT_3V3_ROWS, "+3V3", w33, BB_COL_LO)
    col_tie(jl.RIGHT_3V3_ROWS, "+3V3", w33, BB_COL_RO)
    stub_from_w(jl.LEFT_3V3_ROWS[0], BB_COL_LO, "+3V3", w33)
    stub_from_e(jl.RIGHT_3V3_ROWS[0], BB_COL_RO, "+3V3", w33, cx_e33)
    segs += [
        _segment(cx_w, _jl32_abs(jl.LEFT_3V3_ROWS[0], BB_COL_LO)[1], cx_w, y_s, "+3V3", "B.Cu", w33),
        _segment(cx_e33, _jl32_abs(jl.RIGHT_3V3_ROWS[-1], BB_COL_RO)[1], cx_e33, y_s, "+3V3", "B.Cu", w33),
        _segment(cx_w, y_s, cx_e33, y_s, "+3V3", "B.Cu", w33),
        _segment(cx_e33, y_s, px_out, y_s, "+3V3", "B.Cu", w33),
        _segment(POS_MCU["C10"][0], y_s, POS_MCU["C10"][0], POS_MCU["C10"][1], "+3V3", "B.Cu", w33),
        _segment(POS_MCU["C11"][0], y_s, POS_MCU["C11"][0], POS_MCU["C11"][1], "+3V3", "B.Cu", w33),
        _segment(ux, uy, ux, y_s, "+3V3", "B.Cu", 0.5),
    ]

    # VREF+ → UR+ (J3 row10 RO): corredor x=153 — não compartilha tronco com +5V/+3V3
    segs += [
        _segment(ux + 3.5, uy, cx_ev, uy, "VREF+", "B.Cu", 0.5),
        _segment(cx_ev, uy, cx_ev, vref_y, "VREF+", "B.Cu", 0.5),
        _segment(cx_ev, vref_y, pvref[0], vref_y, "VREF+", "B.Cu", 0.5),
        _segment(pvref[0], vref_y, pvref[0], pvref[1], "VREF+", "B.Cu", 0.5),
        _segment(pvref[0], pvref[1], POS_MCU["C12"][0], pvref[1], "VREF+", "B.Cu", 0.5),
        _segment(POS_MCU["C12"][0], pvref[1], POS_MCU["C12"][0], POS_MCU["C12"][1], "VREF+", "B.Cu", 0.5),
    ]
    return segs


def _axial_v(ref: str, val: str, net_a: str, net_b: str, ox: float, oy: float, span: float = 6.0) -> list:
    return _footprint(
        f"Injet:{ref}", ref, val, ox, oy,
        [*_crt_capsule_v(0, span, 1.5), _pad("A", 0, 0, net_a), _pad("B", 0, span, net_b)],
    )


def sens_footprints() -> list:
    p = POS_SENS
    return [
        _axial("R10", "2.26k", "R", "+3V3", "IAT", *p["R10"], span=6.0),
        _cap("C20", "100nF", *p["C20"], "IAT", wide=False),
        _axial("R18", "1k", "R", "IAT", "IAT", *p["R18"], span=6.0),
        _axial("R11", "2.26k", "R", "+3V3", "CLT", *p["R11"], span=6.0),
        _cap("C21", "100nF", *p["C21"], "CLT", wide=False),
        _axial("R19", "1k", "R", "CLT", "CLT", *p["R19"], span=6.0),
        _axial("R12", "10k", "R", "MAP", "MAP", *p["R12"], span=6.0),
        _axial_v("R13", "18k", "MAP", "GND", *p["R13"], span=6.0),
        _cap("C22", "100nF", *p["C22"], "MAP", wide=False),
        _axial("R16", "1k", "R", "MAP", "MAP", *p["R16"], span=6.0),
        _cap("C23", "100nF", *p["C23"], "TPS", wide=False),
        _axial("R17", "1k", "R", "TPS", "TPS", *p["R17"], span=6.0),
        _axial("R14", "100k", "R", "+12V_PROT", "VBAT", *p["R14"], span=6.0),
        _axial_v("R15", "10k", "VBAT", "GND", *p["R15"], span=6.0),
        _cap("C24", "100nF", *p["C24"], "VBAT", wide=False),
    ]


def sens_traces() -> list:
    """MOD6 — referencia gerador; U1 sensores -> J2 oeste (L12/L16-L18). Nao aplicar sobre PCB manual."""
    p = POS_SENS
    bx = MOD6_IO["bus_w_x"]
    ex = MOD6_IO["bus_e_x"]
    ny = MOD6_IO["port_n_y"]
    px = MOD6_CORRIDOR
    w_sig = 0.5
    w33 = 0.8
    w5 = 1.0
    w12 = 1.0
    cn = CN1_SENS
    u1 = U1_SENS

    def pad_a(ref: str) -> tuple[float, float]:
        ox, oy = p[ref]
        return (ox, oy)

    def pad_b(ref: str, span: float = 6.0) -> tuple[float, float]:
        ox, oy = p[ref]
        return (ox + span, oy)

    def cap_a(ref: str) -> tuple[float, float]:
        return p[ref]

    # Nós ADC (pad B dos divisores / caps)
    iat_n = pad_b("R18")
    clt_n = pad_b("R19")
    map_n = pad_b("R12")
    tps_n = pad_b("R17")
    vbat_n = pad_b("R14")

    segs: list = [
        # +3V3 — CN1-7 + pull-ups R10/R11 + tie MOD5 barra
        _segment(cn[7][0], cn[7][1], bx, ny, "+3V3", "B.Cu", w33),
        _segment(bx, ny, bx, 94.0, "+3V3", "B.Cu", w33),
        _segment(bx, 94.0, pad_a("R10")[0], pad_a("R10")[1], "+3V3", "F.Cu", w33),
        _segment(bx, 86.0, pad_a("R11")[0], pad_a("R11")[1], "+3V3", "B.Cu", w33),
        _segment(bx, 94.0, bx, 105.46, "+3V3", "B.Cu", w33),
        _segment(bx, 105.46, 88.54, 105.46, "+3V3", "B.Cu", w33),
        # +5V — CN1-6 → tronco buck y=111
        _segment(cn[6][0], cn[6][1], cn[6][0], 111.0, "+5V", "B.Cu", w5),
        _segment(cn[6][0], 111.0, 68.0, 111.0, "+5V", "B.Cu", w5),
        # +12V_PROT — tap MOD3/MOD4 (48,118) → R14
        _segment(48.0, 118.0, bx, 118.0, "+12V_PROT", "B.Cu", w12),
        _segment(bx, 118.0, bx, pad_a("R14")[1], "+12V_PROT", "B.Cu", w12),
        _segment(bx, pad_a("R14")[1], pad_a("R14")[0], pad_a("R14")[1], "+12V_PROT", "F.Cu", w12),
        # IAT — CN1-8 → R18 → nó; R10 pull-up; C20 só pad A
        _segment(cn[8][0], cn[8][1], pad_a("R18")[0], ny, "IAT", "B.Cu", w_sig),
        _segment(pad_a("R18")[0], ny, pad_a("R18")[0], pad_a("R18")[1], "IAT", "B.Cu", w_sig),
        _segment(pad_b("R10")[0], pad_b("R10")[1], iat_n[0], iat_n[1], "IAT", "F.Cu", w_sig),
        _segment(iat_n[0], iat_n[1], cap_a("C20")[0], cap_a("C20")[1], "IAT", "F.Cu", w_sig),
        _segment(iat_n[0], iat_n[1], ex, iat_n[1], "IAT", "F.Cu", w_sig),
        _segment(ex, iat_n[1], px["IAT"], iat_n[1], "IAT", "B.Cu", w_sig),
        _segment(px["IAT"], iat_n[1], u1["IAT"][0], iat_n[1], "IAT", "B.Cu", w_sig),
        _segment(u1["IAT"][0], iat_n[1], u1["IAT"][0], u1["IAT"][1], "IAT", "B.Cu", w_sig),
        # CLT
        _segment(cn[9][0], cn[9][1], pad_a("R19")[0], ny, "CLT", "B.Cu", w_sig),
        _segment(pad_a("R19")[0], ny, pad_a("R19")[0], pad_a("R19")[1], "CLT", "B.Cu", w_sig),
        _segment(pad_b("R11")[0], pad_b("R11")[1], clt_n[0], clt_n[1], "CLT", "F.Cu", w_sig),
        _segment(clt_n[0], clt_n[1], cap_a("C21")[0], cap_a("C21")[1], "CLT", "F.Cu", w_sig),
        _segment(clt_n[0], clt_n[1], ex, clt_n[1], "CLT", "F.Cu", w_sig),
        _segment(ex, clt_n[1], px["CLT"], clt_n[1], "CLT", "B.Cu", w_sig),
        _segment(px["CLT"], clt_n[1], u1["CLT"][0], clt_n[1], "CLT", "B.Cu", w_sig),
        _segment(u1["CLT"][0], clt_n[1], u1["CLT"][0], u1["CLT"][1], "CLT", "F.Cu", w_sig),
        # MAP — CN1-10 → R16 → R12 divisor; R13 vertical (pad A topo)
        _segment(cn[10][0], cn[10][1], pad_a("R16")[0], ny, "MAP", "B.Cu", w_sig),
        _segment(pad_a("R16")[0], ny, pad_a("R16")[0], pad_a("R16")[1], "MAP", "B.Cu", w_sig),
        _segment(pad_b("R16")[0], pad_b("R16")[1], pad_a("R12")[0], pad_a("R12")[1], "MAP", "F.Cu", w_sig),
        _segment(map_n[0], map_n[1], cap_a("C22")[0], cap_a("C22")[1], "MAP", "F.Cu", w_sig),
        _segment(map_n[0], map_n[1], p["R13"][0], p["R13"][1], "MAP", "F.Cu", w_sig),
        _segment(map_n[0], map_n[1], ex, map_n[1], "MAP", "F.Cu", w_sig),
        _segment(ex, map_n[1], px["MAP"], map_n[1], "MAP", "B.Cu", w_sig),
        _segment(px["MAP"], map_n[1], u1["MAP"][0], map_n[1], "MAP", "B.Cu", w_sig),
        _segment(u1["MAP"][0], map_n[1], u1["MAP"][0], u1["MAP"][1], "MAP", "B.Cu", w_sig),
        # TPS — CN1-11 → R17 → C23
        _segment(cn[11][0], cn[11][1], pad_a("R17")[0], ny, "TPS", "B.Cu", w_sig),
        _segment(pad_a("R17")[0], ny, pad_a("R17")[0], pad_a("R17")[1], "TPS", "B.Cu", w_sig),
        _segment(tps_n[0], tps_n[1], cap_a("C23")[0], cap_a("C23")[1], "TPS", "F.Cu", w_sig),
        _segment(tps_n[0], tps_n[1], ex, tps_n[1], "TPS", "F.Cu", w_sig),
        _segment(ex, tps_n[1], px["TPS"], tps_n[1], "TPS", "B.Cu", w_sig),
        _segment(px["TPS"], tps_n[1], u1["TPS"][0], tps_n[1], "TPS", "B.Cu", w_sig),
        _segment(u1["TPS"][0], tps_n[1], u1["TPS"][0], u1["TPS"][1], "TPS", "F.Cu", w_sig),
        # VBAT — R14/R15/C24
        _segment(vbat_n[0], vbat_n[1], cap_a("C24")[0], cap_a("C24")[1], "VBAT", "F.Cu", w_sig),
        _segment(vbat_n[0], vbat_n[1], p["R15"][0], p["R15"][1], "VBAT", "F.Cu", w_sig),
        _segment(vbat_n[0], vbat_n[1], ex, vbat_n[1], "VBAT", "F.Cu", w_sig),
        _segment(ex, vbat_n[1], px["VBAT"], vbat_n[1], "VBAT", "B.Cu", w_sig),
        _segment(px["VBAT"], vbat_n[1], u1["VBAT"][0], vbat_n[1], "VBAT", "B.Cu", w_sig),
        _segment(u1["VBAT"][0], vbat_n[1], u1["VBAT"][0], u1["VBAT"][1], "VBAT", "F.Cu", w_sig),
    ]
    return segs


# Passo 7 — RPM opto PC817 (esquema rpm.kicad_sch / §4.3 protoflow)
MOD7_IO = {
    "body": (52, 16, 108, 38),  # contorno Dwgs.User alinhado ao cluster PCB
    "port_n_y": 20.0,       # CN1 pad 12 @ (56, 20) — PCB real CN1 @ (12, 14)
    "port_e_x": 150.5,      # stub B.Cu existente → U1 R17O
    "port_e_y": 65.5,
}
CN1_AT_PCB = (12.0, 14.0)  # origem CN1 no .kicad_pcb (≠ CN1_AT gerador 12,8)
CN1_RPM = (CN1_AT_PCB[0] + 44, CN1_AT_PCB[1] + 6)  # pad 12 → (56, 20)
U1_RPM = (136.0, 64.82)    # R17O = PE8 (jl32_pinout)

# Origem footprint @ KiCad (at x y [rot]) — espelha injet-racing-prodv6.kicad_pcb manual
POS_RPM = {
    "R20": (77.5, 31.5),    # rot 90° no PCB
    "R21": (77.5, 20.0),
    "U7": (89.19, 26.73),   # origem pin 1 (ânodo LED)
    "D3": (83.5, 25.5),     # A=GND, K=RPM_IN (anti-paralelo LED)
    "R22": (104.0, 26.5),   # rot -90° no PCB
    "C25": (104.0, 21.0),   # rot 180° no PCB
}


def _crt_dip4(w: float = 7.62, h: float = 2.54, layers=("F.CrtYd", "F.Fab")) -> list:
    out: list = []
    pad_r = 1.0
    for layer in layers:
        lw = 0.1 if layer == "F.Fab" else 0.05
        out.append(_fp_line(0, -pad_r, w, -pad_r, layer, lw))
        out.append(_fp_line(w, -pad_r, w, h + pad_r, layer, lw))
        out.append(_fp_line(w, h + pad_r, 0, h + pad_r, layer, lw))
        out.append(_fp_line(0, h + pad_r, 0, -pad_r, layer, lw))
        out.append(_fp_circle(0, 0, pad_r, layer))
        out.append(_fp_circle(0, h, pad_r, layer))
        out.append(_fp_circle(w, h, pad_r, layer))
        out.append(_fp_circle(w, 0, pad_r, layer))
    return out


def _pc817(ox: float, oy: float) -> list:
    """DIP-4 — pin1 Ânodo, pin2 K, pin3 E, pin4 C (origem pin1)."""
    return _footprint(
        "Injet:PC817", "U7", "PC817", ox, oy,
        [
            *_crt_dip4(),
            _pad("1", 0, 0, "RPM_IN"),
            _pad("2", 0, 2.54, "GND"),
            _pad("3", 7.62, 2.54, "GND"),
            _pad("4", 7.62, 0, "RPM_IN"),
        ],
    )


def rpm_footprints() -> list:
    p = POS_RPM
    return [
        _axial("R20", "10k 2W", "R", "RPM_IN", "RPM_IN", *p["R20"], span=6.0),
        _axial("R21", "10k 2W", "R", "RPM_IN", "RPM_IN", *p["R21"], span=6.0),
        _pc817(*p["U7"]),
        # anti-paralelo LED: A→GND (cátodo LED), K→RPM_IN (ânodo/bobina)
        _diode("D3", "1N4148", *p["D3"], "GND", "RPM_IN"),
        _axial("R22", "4k7", "R", "RPM_IN", "+3V3", *p["R22"], span=6.0),
        _cap("C25", "1nF", *p["C25"], "RPM_IN", wide=False),
    ]


# Passo 8 — drivers injetores IRLZ44N ×4 (esquema §5)
MOD8_IO = {
    "body": (148, 82, 218, 128),
    "port_w_x": 148.0,
    "port_w_y": 105.0,
    "port_n_y": 82.0,
    "port_e_x": 218.0,
    "port_e_y": 105.0,
}
CN1_INJ = {
    "INJ1": (CN1_AT_PCB[0] + 0, CN1_AT_PCB[1] + 0),
    "INJ2": (CN1_AT_PCB[0] + 4, CN1_AT_PCB[1] + 0),
    "INJ3": (CN1_AT_PCB[0] + 8, CN1_AT_PCB[1] + 0),
    "INJ4": (CN1_AT_PCB[0] + 12, CN1_AT_PCB[1] + 0),
}

# PCB manual KiCad 2026-08-07 — origem @ (at x y [rot])
POS_INJ: dict[str, tuple[float, float]] = {
    "Q10": (163.5, 112.0),
    "R30": (166.0, 91.0),
    "R40": (167.5, 100.0),
    "D10": (174.0, 106.0),
    "Q11": (180.5, 112.0),
    "R31": (183.0, 91.0),
    "R41": (184.5, 100.0),
    "D11": (191.0, 106.0),
    "Q12": (197.5, 112.0),
    "R32": (200.0, 91.0),
    "R42": (201.5, 100.0),
    "D12": (208.0, 106.0),
    "Q13": (214.5, 112.0),
    "R33": (217.0, 91.0),
    "R43": (218.5, 100.0),
    "D13": (225.0, 106.0),
}
# Rotacoes no PCB: R30–R33 rot 180° · R40–R43 rot -90°


def _irlz44n(ref: str, ox: float, oy: float, net_g: str, net_d: str) -> list:
    return _footprint(
        f"Injet:{ref}", ref, "IRLZ44N", ox, oy,
        [
            *_crt_to220(),
            _pad("G", 0, 0, net_g, od=2.15, drill=1.05),
            _pad("D", 2.54, 0, net_d, od=2.15, drill=1.05),
            _pad("S", 5.08, 0, "GND", od=2.15, drill=1.05),
        ],
    )


def inj_footprints() -> list:
    p = POS_INJ
    ch = [
        ("INJ1", "GINJ1", "Q10", "R30", "R40", "D10"),
        ("INJ2", "GINJ2", "Q11", "R31", "R41", "D11"),
        ("INJ3", "GINJ3", "Q12", "R32", "R42", "D12"),
        ("INJ4", "GINJ4", "Q13", "R33", "R43", "D13"),
    ]
    out: list = []
    for inj, ginj, q, rg, rpd, d in ch:
        out.append(_irlz44n(q, *p[q], ginj, inj))
        out.append(_axial(rg, "100R", "R", ginj, ginj, *p[rg], span=6.0))
        out.append(_axial(rpd, "10k", "R", ginj, "GND", *p[rpd], span=6.0))
        out.append(_diode(d, "1N4007", *p[d], inj, "+12V_PROT"))
    return out


# Passo 9 — drivers relé 2N7000 ×3 + SRD 12V (esquema §6)
MOD9_IO = {
    "body": (118, 118, 188, 148),
    "port_w_x": 118.0,
    "port_w_y": 133.0,
    "port_n_y": 118.0,
    "port_e_x": 188.0,
    "port_e_y": 133.0,
}
CN1_REL = {
    "RL_PUMP": (CN1_AT_PCB[0] + 16, CN1_AT_PCB[1]),
    "RL_MAIN": (CN1_AT_PCB[0] + 20, CN1_AT_PCB[1]),
    "RL_IAC": (CN1_AT_PCB[0] + 24, CN1_AT_PCB[1]),
}

# 3 colunas — zona MOD9_RELAY (118–188, 118–148); RL base ≤ y≈147
POS_REL: dict[str, tuple[float, float]] = {
    # RL1 main — PD8 / GRL1
    "Q20": (122.0, 128.0),
    "R50": (122.0, 120.0),
    "R55": (122.0, 124.0),
    "D20": (130.0, 126.0),
    "RL1": (120.0, 132.0),
    # RL2 bomba — PD9 / GRL2
    "Q21": (142.0, 128.0),
    "R51": (142.0, 120.0),
    "R56": (142.0, 124.0),
    "D21": (150.0, 126.0),
    "RL2": (140.0, 132.0),
    # RL3 IAC — PD10 / GRL3
    "Q22": (162.0, 128.0),
    "R52": (162.0, 120.0),
    "R57": (162.0, 124.0),
    "D22": (170.0, 126.0),
    "RL3": (160.0, 132.0),
}


def _crt_to92(layers=("F.CrtYd", "F.Fab")) -> list:
    out: list = []
    for layer in layers:
        w = 0.1 if layer == "F.Fab" else 0.05
        out.append(_fp_line(-2.5, 0, 2.5, 0, layer, w))
        out.append(_fp_line(0, 0, 1.27, 2.2, layer, w))
        out.append(_fp_line(1.27, 2.2, 2.54, 0, layer, w))
        out.append(_fp_line(2.54, 0, -2.5, 0, layer, w))
    return out


def _2n7000(ref: str, ox: float, oy: float, net_g: str, net_d: str) -> list:
    return _footprint(
        f"Injet:{ref}", ref, "2N7000", ox, oy,
        [
            *_crt_to92(),
            _pad("S", 0, 0, "GND", od=1.45, drill=0.8),
            _pad("G", 1.27, 1.8, net_g, od=1.45, drill=0.8),
            _pad("D", 2.54, 0, net_d, od=1.45, drill=0.8),
        ],
    )


def _relay_srd(
    ref: str, ox: float, oy: float,
    coil_p: str, coil_m: str, com: str, no: str,
) -> list:
    """SRD-12V — pin1 COIL+ · pin2 COIL− · pin3 COM · pin4 NO."""
    w, h = 19.05, 15.24
    return _footprint(
        f"Injet:{ref}", ref, "12V 30A", ox, oy,
        [
            _fp_rect(0, 0, w, h),
            _fp_rect(0, 0, w, h, layer="F.Fab"),
            _pad("1", 2.54, 2.54, coil_p, od=1.55, drill=0.85),
            _pad("2", 2.54, h - 2.54, coil_m, od=1.55, drill=0.85),
            _pad("3", w - 2.54, 2.54, com, od=1.55, drill=0.85),
            _pad("4", w - 2.54, h - 2.54, no, od=1.55, drill=0.85),
        ],
    )


def relay_footprints() -> list:
    p = POS_REL
    ch = [
        ("RL1", "GRL1", "Q20", "R50", "R55", "D20", "RL_MAIN"),
        ("RL2", "GRL2", "Q21", "R51", "R56", "D21", "RL_PUMP"),
        ("RL3", "GRL3", "Q22", "R52", "R57", "D22", "RL_IAC"),
    ]
    out: list = []
    for coil, grl, q, rg, rpd, d, out_net in ch:
        out.append(_2n7000(q, *p[q], grl, coil))
        out.append(_axial(rg, "1k", "R", grl, grl, *p[rg], span=6.0))
        out.append(_axial(rpd, "10k", "R", grl, "GND", *p[rpd], span=6.0))
        out.append(_diode(d, "1N4007", *p[d], coil, "+12V_PROT"))
        out.append(_relay_srd(
            coil, *p[coil],
            "+12V_PROT", coil, "+12V_PROT", out_net,
        ))
    return out


# Passo 10 — CAN SN65HVD230 (esquema §8)
MOD10_IO = {
    "body": (118, 18, 158, 38),
    "port_w_x": 118.0,
    "port_w_y": 28.0,
    "port_n_y": 18.0,
    "port_e_x": 158.0,
    "port_e_y": 28.0,
}
CN1_CAN = {
    "CANH": (CN1_AT_PCB[0] + 32, CN1_AT_PCB[1]),
    "CANL": (CN1_AT_PCB[0] + 36, CN1_AT_PCB[1]),
}

# Footprint Injet:CAN — pads TX(0,0) RX(6,0) VCC(0,6) GND(6,6) H(12,6) L(18,6)
POS_CAN: dict[str, tuple[float, float]] = {
    "U6": (126.0, 20.0),
    "C40": (120.0, 26.0),
    "C41": (120.0, 18.0),
}


def _crt_can_module(layers=("F.CrtYd", "F.Fab")) -> list:
    out: list = []
    for layer in layers:
        w = 0.1 if layer == "F.Fab" else 0.05
        out.append(_fp_line(0, 0, 18, 0, layer, w))
        out.append(_fp_line(18, 0, 18, 6, layer, w))
        out.append(_fp_line(18, 6, 0, 6, layer, w))
        out.append(_fp_line(0, 6, 0, 0, layer, w))
    return out


def _can_module(ox: float, oy: float) -> list:
    """Módulo SN65HVD230 6 pads — ref prodv5 Injet:CAN."""
    return _footprint(
        "Injet:CAN", "U6", "SN65HVD230", ox, oy,
        [
            *_crt_can_module(),
            _pad("TX", 0, 0, "CAN_TX", od=1.8, drill=0.9),
            _pad("RX", 6, 0, "CAN_RX", od=1.8, drill=0.9),
            _pad("VCC", 0, 6, "+3V3", od=1.8, drill=0.9),
            _pad("GND", 6, 6, "GND", od=1.8, drill=0.9),
            _pad("H", 12, 6, "CANH", od=1.8, drill=0.9),
            _pad("L", 18, 6, "CANL", od=1.8, drill=0.9),
        ],
    )


def can_footprints() -> list:
    p = POS_CAN
    return [
        _can_module(*p["U6"]),
        _cap("C40", "100nF", *p["C40"], "+3V3", wide=False),
        _cap("C41", "10uF", *p["C41"], "+3V3", wide=True),
    ]


# Passo 11 — lambda MCP6004 + AD8628 (esquema §7)
# Posições = PCB manual KiCad 2026-08-08 (usuário moveu peças)
MOD11_IO = {
    "body": (158.62, 22.62, 218.62, 76.62),
    "port_w_x": 158.0,
    "port_w_y": 50.0,
    "port_n_y": 24.0,
    "port_e_x": 218.0,
    "port_e_y": 50.0,
}

POS_LAMBDA: dict[str, tuple[float, float]] = {
    "U4": (183.19, 45.88),
    "C32": (180.12, 38.62),
    "C33": (164.50, 41.00),
    "R76": (171.12, 59.50),
    "R77": (171.50, 68.50),
    "U5": (200.50, 47.00),
    "R78": (204.50, 53.00),
    "C30": (206.50, 59.00),
    "R70": (192.50, 67.00),
    "R71": (192.50, 73.00),
    "C31": (210.50, 65.00),
}


def _crt_dip14(layers=("F.CrtYd", "F.Fab")) -> list:
    """DIP-14 — origem pin1 topo-esq; pin7 base-esq · pin14 topo-dir."""
    w, h = 7.62, 15.24
    pad_r = 1.0
    out: list = []
    for layer in layers:
        lw = 0.1 if layer == "F.Fab" else 0.05
        out.append(_fp_line(0, -pad_r, w, -pad_r, layer, lw))
        out.append(_fp_line(w, -pad_r, w, h + pad_r, layer, lw))
        out.append(_fp_line(w, h + pad_r, 0, h + pad_r, layer, lw))
        out.append(_fp_line(0, h + pad_r, 0, -pad_r, layer, lw))
        for y in (0.0, h):
            out.append(_fp_circle(0, y, pad_r, layer))
            out.append(_fp_circle(w, y, pad_r, layer))
    return out


def _mcp6004(ox: float, oy: float) -> list:
    """MCP6004 DIP-14 — pads power/VM pré-nomeados; sinais internos = rotear."""
    pitch = 2.54
    left = [(str(i + 1), 0.0, i * pitch) for i in range(7)]
    right = [(str(i + 8), 7.62, (6 - i) * pitch) for i in range(7)]
    nets = {"1": "VM", "2": "VM", "4": "GND", "5": "VM", "14": "+5V"}
    pads = [_pad(num, x, y, nets.get(num, "")) for num, x, y in left + right]
    return _footprint(
        "Injet:U6004", "U4", "MCP6004", ox, oy,
        [*_crt_dip14(), *pads],
    )


def _pad_smd(num: str, x: float, y: float, net: str, layer: str = "B.Cu") -> list:
    el = [
        S("pad"), num, S("smd"), S("rect"),
        [S("at"), x, y],
        [S("size"), 1.15, 1.15],
        [S("layers"), layer],
        [S("uuid"), _uid()],
    ]
    if net:
        el.insert(-1, [S("net"), net])
    return el


def _footprint_b(name: str, ref: str, val: str, ox: float, oy: float, extras: list) -> list:
    return [
        S("footprint"), name,
        [S("layer"), "B.Cu"],
        [S("uuid"), _uid()],
        [S("at"), ox, oy],
        _prop("Reference", ref),
        _prop("Value", val, "F.Fab"),
        _prop("Datasheet", "", hide=True),
        _prop("Description", "", hide=True),
        [S("duplicate_pad_numbers_are_jumpers"), S("no")],
        *extras,
        [S("embedded_fonts"), S("no")],
    ]


def _crt_soic8(layers=("B.CrtYd", "B.Fab")) -> list:
    out: list = []
    for layer in layers:
        w = 0.1 if layer == "B.Fab" else 0.05
        out.append(_fp_line(0, 0, 5.4, 0, layer, w))
        out.append(_fp_line(5.4, 0, 5.4, 3.81, layer, w))
        out.append(_fp_line(5.4, 3.81, 0, 3.81, layer, w))
        out.append(_fp_line(0, 3.81, 0, 0, layer, w))
    return out


def _ad8628(ox: float, oy: float) -> list:
    """AD8628 SOIC-8 — montagem B.Cu (pads só em B.Cu)."""
    pitch = 1.27
    left = [(str(i + 1), 0.0, i * pitch) for i in range(4)]
    right = [(str(8 - i), 5.4, i * pitch) for i in range(4)]
    nets = {"2": "VM", "3": "VM", "4": "GND", "5": "VM", "6": "VM"}
    pads = [_pad_smd(num, x, y, nets.get(num, "")) for num, x, y in left + right]
    return _footprint_b(
        "Injet:U8628", "U5", "AD8628", ox, oy,
        [*_crt_soic8(), *pads],
    )


def _cap_v(ref: str, val: str, ox: float, oy: float, net: str, span: float = 6.0) -> list:
    return _footprint(
        f"Injet:{ref}", ref, val, ox, oy,
        [
            *_crt_capsule_v(0, span, 1.4),
            _pad("A", 0, span, net),
            _pad("B", 0, 0, "GND"),
        ],
    )


def lambda_footprints() -> list:
    p = POS_LAMBDA
    return [
        _mcp6004(*p["U4"]),
        _ad8628(*p["U5"]),
        _axial("R76", "10k", "R", "+3V3", "VM", *p["R76"], span=4.0),
        _axial("R77", "10k", "R", "VM", "GND", *p["R77"], span=4.0),
        _axial("R70", "61R9", "R", "IP", "IP", *p["R70"], span=8.0),
        _axial("R71", "6k8", "R", "UN", "RI_PULSE", *p["R71"], span=8.0),
        _axial_v("R78", "1k", "UN", "RI_PULSE", *p["R78"], span=4.0),
        _cap("C32", "100nF", *p["C32"], "+5V", wide=False),
        _cap("C33", "10uF", *p["C33"], "+5V", wide=True),
        _cap_v("C30", "220nF", *p["C30"], "IP"),
        _cap_v("C31", "220nF", *p["C31"], "UN"),
    ]


# Passo 12 — aquecedor λ IRLZ44N (esquema §7 · CN2 H+/H−)
MOD12_IO = {
    "body": (162, 24, 212, 38),
    "port_w_x": 162.0,
    "port_w_y": 31.0,
    "port_e_x": 212.0,
    "port_e_y": 31.0,
}

POS_HEAT: dict[str, tuple[float, float]] = {
    "R80": (174.0, 30.0),
    "Q30": (188.0, 30.0),
    "R81": (188.0, 24.0),
    "D30": (198.0, 28.0),
}


def heater_footprints() -> list:
    p = POS_HEAT
    return [
        _irlz44n("Q30", *p["Q30"], "GHEAT", "H-"),
        _axial("R80", "100R", "R", "GHEAT", "GHEAT", *p["R80"], span=6.0),
        _axial_v("R81", "10k", "GHEAT", "GND", *p["R81"], span=6.0),
        _diode("D30", "1N4007", *p["D30"], "H-", "+12V_PROT"),
    ]


def rpm_traces() -> list:
    """Referência gerador — NÃO aplicar sobre PCB manual (como MOD6)."""
    p = POS_RPM
    cn = CN1_RPM
    u1 = U1_RPM
    px = MOD7_IO["port_e_x"]
    py = MOD7_IO["port_e_y"]
    w_sig = 0.5
    w33 = 0.8

    def pa(ref: str) -> tuple[float, float]:
        return p[ref]

    def pb(ref: str, span: float = 6.0) -> tuple[float, float]:
        ox, oy = p[ref]
        return (ox + span, oy)

    u7_c = (p["U7"][0] + 7.62, p["U7"][1])
    node_led = pb("R21")
    node_out = u7_c

    return [
        # CN1-12 → R20 → R21 → U7-1 (RPM_IN bobina)
        _segment(cn[0], cn[1], pa("R20")[0], MOD7_IO["port_n_y"], "RPM_IN", "F.Cu", w_sig),
        _segment(pa("R20")[0], MOD7_IO["port_n_y"], pa("R20")[0], pa("R20")[1], "RPM_IN", "F.Cu", w_sig),
        _segment(pb("R20")[0], pb("R20")[1], pa("R21")[0], pa("R21")[1], "RPM_IN", "F.Cu", w_sig),
        _segment(pb("R21")[0], pb("R21")[1], p["U7"][0], p["U7"][1], "RPM_IN", "F.Cu", w_sig),
        # D3 paralelo K LED (K→RPM_IN nó, A→GND)
        _segment(p["D3"][0], p["D3"][1] + 6, node_led[0], node_led[1], "RPM_IN", "F.Cu", w_sig),
        # Coletor → R22 pull-up + C25 + corredor leste → stub U1
        _segment(node_out[0], node_out[1], pa("R22")[0], pa("R22")[1], "RPM_IN", "F.Cu", w_sig),
        _segment(pb("R22")[0], pb("R22")[1], pa("C25")[0], pa("C25")[1], "RPM_IN", "F.Cu", w_sig),
        _segment(node_out[0], node_out[1], px, node_out[1], "RPM_IN", "B.Cu", w_sig),
        _segment(px, node_out[1], px, py, "RPM_IN", "B.Cu", w_sig),
        _segment(px, py, u1[0], u1[1], "RPM_IN", "B.Cu", w_sig),
        # +3V3 stub R22 pad A
        _segment(pa("R22")[0], pa("R22")[1], pa("R22")[0], 105.46, "+3V3", "B.Cu", w33),
    ]


def mod_io_markers() -> list:
    """Contorno dos módulos + rótulos curtos nas portas e pinos da plaquinha."""
    m3 = MOD3_IO
    m4 = MOD4_IO
    pads = _mod_pads()
    out = [
        _gr_rect(*m3["body"], width=0.2),
        _gr_text("MOD3", m3["body"][0] + 1, m3["body"][1] + 1, 0.7),
        _gr_text("+12V_BAT", 9, 114, 0.65),
        _gr_text("->MOD4", 43, 110, 0.65),
        _gr_text("->CN2", 46, 146, 0.65),
        _gr_rect(*m4["body"], width=0.2),
        _gr_text("MOD4", m4["body"][0] + 1, m4["body"][1] + 1, 0.7),
        _gr_text("+12V_PROT", 43, 57, 0.65),
        _gr_text("->+5V", 72, 44.5, 0.65),
        _gr_text("IN-", pads["IN-"][0] - 5.5, pads["IN-"][1] + 0.3, 0.55),
        _gr_text("IN+", pads["IN+"][0] - 5.5, pads["IN+"][1] - 0.3, 0.55),
        _gr_text("OUT-", pads["OUT-"][0] + 1.5, pads["OUT-"][1] + 0.3, 0.55),
        _gr_text("OUT+", pads["OUT+"][0] + 1.5, pads["OUT+"][1] - 0.3, 0.55),
        _gr_rect(*MOD5_IO["body"], width=0.2),
        _gr_text("MOD5", MOD5_IO["body"][0] + 1, MOD5_IO["body"][1] + 1, 0.7),
        _gr_text("+5V IN", 75, 44.5, 0.65),
        _gr_text("->+3V3", 152, MOD5_IO["bus_south_y"], 0.65),
        _gr_text("3V3 esq", *_jl32_power_3v3_left()[:2], 0.55),
        _gr_text("5V dir", *_jl32_power_5v()[:2], 0.55),
        _gr_text("3V3 dir", *_jl32_power_3v3_right()[:2], 0.55),
        _gr_text("GND esq", *_jl32_abs(3, BB_COL_LO)[:2], 0.55),
        _gr_text("UR+", *_jl32_vref()[:2], 0.55),
        _gr_text("W x=72", MOD5_IO["corridor_w_x"] - 2, 48, 0.45),
        _gr_text("5V x=146", MOD5_IO["corridor_e_5v_x"] - 4, 50, 0.45),
        _gr_text("3V3 x=150", MOD5_IO["corridor_e_3v3_x"] - 4, 52, 0.45),
        _gr_text("VREF x=153", MOD5_IO["corridor_e_vref_x"] - 4, 54, 0.45),
        _gr_text("STM32F4VE", POS_MCU["U1"][0] + 8, POS_MCU["U1"][1] - 24, 0.6),
        _gr_rect(*MOD6_IO["body"], width=0.2),
        _gr_text("MOD6", MOD6_IO["body"][0] + 1, MOD6_IO["body"][1] + 1, 0.7),
        _gr_text("CN1 sens", 38, MOD6_IO["port_n_y"], 0.55),
        _gr_text("->U1", MOD6_IO["port_e_x"] - 4, 82, 0.55),
        _gr_rect(*MOD7_IO["body"], width=0.2),
        _gr_text("MOD7", MOD7_IO["body"][0] + 1, MOD7_IO["body"][1] + 1, 0.7),
        _gr_text("CN1-12", 52, MOD7_IO["port_n_y"], 0.55),
        _gr_text("->U1", MOD7_IO["port_e_x"] - 8, MOD7_IO["port_e_y"], 0.55),
        _gr_rect(*MOD8_IO["body"], width=0.2),
        _gr_text("MOD8", MOD8_IO["body"][0] + 1, MOD8_IO["body"][1] + 1, 0.7),
        _gr_text("CN1 13-16", 168, MOD8_IO["port_n_y"] - 1, 0.55),
        _gr_text("->U1", MOD8_IO["port_w_x"] + 1, MOD8_IO["port_w_y"], 0.55),
        _gr_text("+12V_PROT", MOD8_IO["port_e_x"] - 14, MOD8_IO["port_e_y"], 0.55),
        _gr_rect(*MOD9_IO["body"], width=0.2),
        _gr_text("MOD9", MOD9_IO["body"][0] + 1, MOD9_IO["body"][1] + 1, 0.7),
        _gr_text("CN1 17-19", 128, MOD9_IO["port_n_y"] - 1, 0.55),
        _gr_text("->U1", MOD9_IO["port_w_x"] + 1, MOD9_IO["port_w_y"], 0.55),
        _gr_text("+12V_PROT", MOD9_IO["port_e_x"] - 14, MOD9_IO["port_e_y"], 0.55),
        _gr_rect(*MOD10_IO["body"], width=0.2),
        _gr_text("MOD10", MOD10_IO["body"][0] + 1, MOD10_IO["body"][1] + 1, 0.7),
        _gr_text("CN1 20-21", 132, MOD10_IO["port_n_y"] - 1, 0.55),
        _gr_text("->U1", MOD10_IO["port_w_x"] + 1, MOD10_IO["port_w_y"], 0.55),
        _gr_text("+3V3", MOD10_IO["port_w_x"] + 1, MOD10_IO["port_w_y"] - 4, 0.55),
        _gr_rect(*MOD11_IO["body"], width=0.2),
        _gr_text("MOD11", MOD11_IO["body"][0] + 1, MOD11_IO["body"][1] + 1, 0.7),
        _gr_text("CN2", MOD11_IO["port_e_x"] - 8, MOD11_IO["port_n_y"], 0.55),
        _gr_text("->U1", MOD11_IO["port_w_x"] + 1, MOD11_IO["port_w_y"], 0.55),
        _gr_text("+5V", MOD11_IO["port_w_x"] + 1, MOD11_IO["port_w_y"] - 4, 0.55),
        _gr_rect(*MOD12_IO["body"], width=0.2),
        _gr_text("MOD12", MOD12_IO["body"][0] + 1, MOD12_IO["body"][1] + 1, 0.7),
        _gr_text("CN2 1-2", MOD12_IO["port_e_x"] - 10, MOD12_IO["port_e_y"], 0.55),
        _gr_text("->U1", MOD12_IO["port_w_x"] + 1, MOD12_IO["port_w_y"], 0.55),
        _gr_text("+12V_PROT", MOD12_IO["port_w_x"] + 1, MOD12_IO["port_w_y"] - 4, 0.55),
    ]
    return out


def zone_markers() -> list:
    out = []
    for name, (x1, y1, x2, y2) in ZONE_RESERVE.items():
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        label = name.replace("_", " ")
        out.append([
            S("gr_rect"),
            [S("start"), x1, y1], [S("end"), x2, y2],
            [S("stroke"), [S("width"), 0.15], [S("type"), S("dash")]],
            [S("layer"), "Dwgs.User"],
            [S("fill"), S("no")],
            [S("uuid"), _uid()],
        ])
        out.append([
            S("gr_text"), label,
            [S("at"), cx, cy],
            [S("layer"), "Dwgs.User"],
            [S("uuid"), _uid()],
            [S("effects"), [S("font"), [S("size"), 1.0, 1.0]], [S("justify"), S("left")]],
        ])
    out.append([
        S("gr_text"), "MOD3 +12V PROT",
        [S("at"), 32, 122],
        [S("layer"), "Dwgs.User"],
        [S("uuid"), _uid()],
        [S("effects"), [S("font"), [S("size"), 1.0, 1.0]], [S("justify"), S("left")]],
    ])
    return out
