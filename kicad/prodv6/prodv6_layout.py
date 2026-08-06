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
    "MOD7_RPM": (58, 48, 88, 72),
    "MOD10_CAN": (118, 18, 158, 38),
    "MOD11_LAMBDA": (158, 24, 218, 78),
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

# Passo 4 — buck MP1584 (+5V; +3V3 vem da Black Board, sem LDO na ECU)
MOD4_IO = {
    "body": (26, 36, 76, 58),
    "port_in_y": 58.0,
    "port_out_y": 43.0,
    "port_x_in": 48.0,
    "port_x_out": 78.0,
}
POS_BUCK = {
    "U2": (48.0, 40.0),
    "C3": (30.0, 50.0),
    "C4": (30.0, 38.0),
    "C5": (68.0, 50.0),
    "C6": (68.0, 38.0),
}
BUCK_W = 17.0
BUCK_H = 12.0


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


def _segment(x1, y1, x2, y2, net: str, layer: str = "F.Cu", width: float = 0.8) -> list:
    return [
        S("segment"),
        [S("start"), x1, y1], [S("end"), x2, y2],
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


def _crt_dcdc_module(w: float, h: float, layers=("F.CrtYd", "F.Fab")) -> list:
    out: list = []
    for layer in layers:
        lw = 0.1 if layer == "F.Fab" else 0.05
        out.append(_fp_line(0, 0, w, 0, layer, lw))
        out.append(_fp_line(w, 0, w, h, layer, lw))
        out.append(_fp_line(w, h, 0, h, layer, lw))
        out.append(_fp_line(0, h, 0, 0, layer, lw))
    return out


def _mp1584(ox: float, oy: float) -> list:
    w, h = BUCK_W, BUCK_H
    return _footprint(
        "Injet:MP1584", "U2", "MP1584", ox, oy,
        [
            *_crt_dcdc_module(w, h),
            _pad("1", 0, 2.54, "+12V_PROT", od=2.0, drill=1.0),
            _pad("2", 0, 0, "GND", od=2.0, drill=1.0),
            _pad("3", w, 2.54, "+5V", od=2.0, drill=1.0),
            _pad("4", w, 0, "GND", od=2.0, drill=1.0),
        ],
    )


def buck_footprints() -> list:
    p = POS_BUCK
    return [
        _mp1584(*p["U2"]),
        _cap("C3", "100uF", *p["C3"], "+12V_PROT", wide=True),
        _cap("C4", "100nF", *p["C4"], "+12V_PROT", wide=False),
        _cap("C5", "220uF", *p["C5"], "+5V", wide=True),
        _cap("C6", "100nF", *p["C6"], "+5V", wide=False),
    ]


def _tap_cap_a(ox: float, oy: float, bus_x: float, bus_y: float, net: str,
               layer: str = "B.Cu", width: float = 1.0) -> list:
    """Pad A em (ox,oy). Bus deslocado em bus_y — não cruza pad B (corpo do cap)."""
    return [
        _segment(bus_x, bus_y, ox, bus_y, net, layer, width),
        _segment(ox, bus_y, ox, oy, net, layer, width),
    ]


def buck_traces() -> list:
    ux, uy = POS_BUCK["U2"]
    vin = (ux + 0, uy + 2.54)
    vout = (ux + BUCK_W, uy + 2.54)
    px_in = MOD4_IO["port_x_in"]
    px_out = MOD4_IO["port_x_out"]
    bus12_x = 46.0
    bus5_y = 44.5
    w12, w5 = 1.2, 1.0

    return [
        # IN +12V: desvia x=46 (evita GND U2 pad2 em x=48,y=40)
        _segment(px_in, PORT_OUT_N_Y, bus12_x, PORT_OUT_N_Y, "+12V_PROT", "B.Cu", w12),
        _segment(bus12_x, PORT_OUT_N_Y, bus12_x, 52.5, "+12V_PROT", "B.Cu", w12),
        *_tap_cap_a(POS_BUCK["C3"][0], POS_BUCK["C3"][1], bus12_x, 52.5, "+12V_PROT", width=w12),
        *_tap_cap_a(POS_BUCK["C4"][0], POS_BUCK["C4"][1], bus12_x, 41.0, "+12V_PROT", width=w12),
        _segment(bus12_x, vin[1], vin[0], vin[1], "+12V_PROT", "B.Cu", w12),
        # OUT +5V: bus em y=44.5 — stub vertical só no pad A de cada cap
        _segment(vout[0], vout[1], vout[0], bus5_y, "+5V", "B.Cu", w5),
        _segment(vout[0], bus5_y, px_out, bus5_y, "+5V", "B.Cu", w5),
        _segment(POS_BUCK["C5"][0], bus5_y, POS_BUCK["C5"][0], POS_BUCK["C5"][1], "+5V", "B.Cu", w5),
        _segment(POS_BUCK["C6"][0], bus5_y, POS_BUCK["C6"][0], POS_BUCK["C6"][1], "+5V", "B.Cu", w5),
    ]


def mod_io_markers() -> list:
    """Contorno dos módulos + rótulos curtos nas portas."""
    m3 = MOD3_IO
    m4 = MOD4_IO
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
