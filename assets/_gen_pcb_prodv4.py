# -*- coding: utf-8 -*-
"""
INJET RACING ECU — PCB prodv4 (fibra 2 faces, só trilhas)

Base: prodv3 + correções KiCad DRC (pad nets, stubs pad↔trilha, conectividade).

Uso: python _gen_pcb_prodv4.py
"""
from __future__ import annotations

import importlib.util
import sys
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent

# Reutiliza renomeação e build v8 do prodv2
_spec = importlib.util.spec_from_file_location("pcb_p2", OUT / "_gen_pcb_prodv2.py")
_p2 = importlib.util.module_from_spec(_spec)
sys.modules["pcb_p2"] = _p2
_spec.loader.exec_module(_p2)

pads: dict[str, tuple[float, float, float, float]] = {}
traces_b: list[tuple[list[tuple[float, float]], float, str]] = []
traces_f: list[tuple[list[tuple[float, float]], float, str]] = []
traces: list[tuple[list[tuple[float, float]], float, str, str]] = []
jumpers: list[tuple[float, float, float, float, str]] = []
pad_nets: dict[str, str] = {}
W, H = 240.0, 160.0

vias: list[tuple[float, float, str, str]] = []  # x, y, net, uuid placeholder

LAYER_BOTTOM = "B.Cu"
LAYER_TOP = "F.Cu"

VIA_GRID: list[tuple[float, float]] = [
    (x, y)
    for x in range(20, 221, 12)
    for y in range(20, 141, 12)
]

# (camada, x1, y1, x2, y2, net, faixa_y horizontal ou None)
PRIORITY_A: list[tuple[str, float, float, float, float, str, float | None]] = [
    ("F", 40, 14, 176, 128, "IAT", None),
    ("F", 44, 14, 176, 116, "CLT", None),
    ("F", 48, 14, 176, 104, "MAP", None),
    ("F", 52, 14, 184, 92, "TPS", None),
    ("F", 90, 40, 16, 8, "INJ2", 5.0),
    ("B", 108, 40, 20, 8, "INJ3", 15.0),
    ("B", 126, 40, 24, 8, "INJ4", 14.0),
    ("F", 168, 104, 168, 136, "+3V3", None),
    ("F", 100, 130, 100, 148, "+3V3", None),
    ("F", 36, 14, 72, 148, "+3V3", None),
    ("F", 17.27, 112, 32.0, 8, "RL1", 7.0),
    ("F", 31.27, 112, 28.0, 8, "RL2", 6.5),
    ("F", 45.27, 112, 36.0, 8, "RL3", 6.0),
]

PRIORITY_B: list[tuple[str, float, float, float, float, str, float | None]] = [
    ("B", 32, 14, 56, 142, "+5V", 159.0),
    ("B", 116, 90, 116, 142, "+5V", 158.0),
]

SPECIAL_ROUTES: list[tuple[str, str, list[tuple[float, float]]]] = [
    ("F", "+3V3", [(70, 90), (238, 90), (238, 148), (70, 148)]),
    ("F", "+3V3", [(116, 70), (238, 70), (238, 148), (116, 148)]),
    ("F", "+12V_PROT", [(200, 14), (200, 28), (162, 28)]),
    ("B", "+5V", [(164, 50), (164, 157), (150, 157), (150, 142)]),
    ("B", "+5V", [(179.6, 42), (179.6, 156), (150, 156), (150, 142)]),
]

# Redes com rota completa na F.Cu — remove trilhas longas conflitantes da B.Cu (v8)
BCU_PRUNE_NETS = frozenset({"IAT", "CLT", "MAP", "TPS"})

# Redes re-roteadas na prodv3 — remove trilhas parciais do v8/prodv2 antes do roteamento
BCU_STRIP_NETS = frozenset({"INJ2", "INJ3", "INJ4", "CANH", "CANL", "+3V3", "+5V", "IP", "UN", "SWDIO", "SWCLK"})
FCU_STRIP_NETS = frozenset({"INJ2", "INJ4"})

CAN_PATHS: dict[str, list[tuple[float, float]]] = {
    "CANL": [(134, 90), (3.5, 90), (3.5, 153), (44, 153), (44, 8)],
}

# F.Cu + via + B.Cu — roteado por último (evita bloquear INJ/sensores)
CANH_VIA_CANDIDATES: list[
    tuple[list[tuple[float, float]], list[tuple[float, float]], tuple[float, float]]
] = [
    ([(128, 90), (48, 10)], [(48, 10), (40, 8)], (48, 10)),
    ([(128, 90), (50, 10)], [(50, 10), (40, 8)], (50, 10)),
    ([(128, 90), (50, 12)], [(50, 12), (40, 8)], (50, 12)),
    ([(128, 90), (52, 10)], [(52, 10), (40, 8)], (52, 10)),
    ([(128, 90), (128, 10), (48, 10)], [(48, 10), (40, 8)], (48, 10)),
    ([(128, 90), (128, 10), (50, 10)], [(50, 10), (40, 8)], (50, 10)),
]

BCU_BUS_X: dict[str, float] = {
    "GINJ1": 84.0,
    "GINJ3": 88.0,
    "GINJ4": 92.0,
    "GHEAT": 94.0,
    "IP": 190.0,
    "UN": 194.0,
    "QG": 16.5,
    "INJ1": 10.0,
    "+12V_IN": 14.0,
}

# Barramentos B.Cu com mesmo corredor — deslocamento por âncora X/Y
BCU_X_ANCHOR_NETS: dict[float, frozenset[str]] = {
    12.0: frozenset({"INJ1", "+12V_IN"}),
    192.0: frozenset({"IP", "UN"}),
}
BCU_Y_ANCHOR_NETS: dict[float, frozenset[str]] = {
    148.0: frozenset({"QG"}),
}
BCU_Y_OFFSET: dict[str, float] = {"QG": 146.0, "IP": 80.0, "UN": 82.0}

# Pinos fixos (v8 / esquemático prod) — sobrescreve inferência por proximidade
MCU_PAD_NETS: dict[str, str] = {
    "MCU.L1": "+3V3",
    "MCU.L2": "VREF",
    "MCU.L9": "VBAT",
    "MCU.L10": "RPM_OUT",
    "MCU.L11": "CAN_RX",
    "MCU.L12": "CAN_TX",
    "MCU.L13": "GINJ1",
    "MCU.L14": "GINJ2",
    "MCU.L15": "GINJ3",
    "MCU.L16": "GINJ4",
    "MCU.L17": "GHEAT",
    "MCU.L18": "GRL1",
    "MCU.L19": "GRL2",
    "MCU.L20": "GRL3",
    "MCU.R1": "+5V",
    "MCU.R3": "IAT",
    "MCU.R4": "CLT",
    "MCU.R5": "MAP",
    "MCU.R6": "TPS",
    "MCU.R7": "DAC_VM",
    "MCU.R8": "IP",
    "MCU.R10": "UN",
    "MCU.R11": "RI_PULSE",
    "MCU.R14": "SWDIO",
    "MCU.R15": "SWCLK",
}

STATIC_PAD_NETS: dict[str, str] = {
    **MCU_PAD_NETS,
    "R20.B": "GINJ1",
    "R21.B": "GINJ2",
    "R22.B": "GINJ3",
    "R23.B": "GINJ4",
    "R25.B": "GHEAT",
    "R10.A": "GINJ1",
    "R11.A": "GINJ2",
    "R12.A": "GINJ3",
    "R13.A": "GINJ4",
    "R15.A": "GHEAT",
    "R25.A": "GHEAT",
    "R30.A": "GRL1",
    "R31.A": "GRL2",
    "R32.A": "GRL3",
    "R40.A": "IAT",
    "R41.A": "CLT",
    "R42.A": "MAP",
    "R53.A": "TPS",
    "R50.A": "IAT",
    "R51.A": "CLT",
    "R52.A": "MAP",
    "R54.A": "TPS",
    "R60.A": "RPM_IN",
    "R61.A": "RPM_IN",
    "R62.A": "RPM_OUT",
    "R70.A": "IP",
    "R70.B": "IP",
    "R71.A": "UN",
    "R71.B": "RI_PULSE",
    "R74.A": "VBAT",
    "R74.B": "VBAT",
    "R75.A": "VBAT",
    "R75.B": "VBAT",
    "R76.B": "DAC_VM",
    "R77.B": "DAC_VM",
    "R78.A": "UN",
    "U6004.2": "DAC_VM",
    "U6004.3": "VM",
    "U8628.3": "VM",
    "U8628.6": "VM",
    "BUCK.VOUT": "+5V",
    "LDO.IN": "+5V",
    "LDO.OUT": "+3V3",
    "CAN.VCC": "+3V3",
    "CAN.TX": "CAN_TX",
    "CAN.RX": "CAN_RX",
    "CAN.H": "CANH",
    "CAN.L": "CANL",
    "QREV.G": "QG",
    "D10.K": "+12V_PROT",
    "D11.A": "INJ2",
    "D11.K": "+12V_PROT",
    "D12.A": "INJ3",
    "D12.K": "+12V_PROT",
    "D13.A": "INJ4",
    "D13.K": "+12V_PROT",
    "D14.K": "+12V_PROT",
    "D20.K": "+12V_PROT",
    "D21.K": "+12V_PROT",
    "D22.K": "+12V_PROT",
    "C3.A": "+5V",
    "C4.A": "+3V3",
    "C10.A": "IAT",
    "C11.A": "CLT",
    "C12.A": "MAP",
    "C13.A": "TPS",
    "C20.A": "RPM_OUT",
    "C30.A": "IP",
    "C31.A": "UN",
    "C33.A": "VBAT",
    "SWD.1": "+3V3",
    "SWD.2": "SWDIO",
    "SWD.3": "SWCLK",
    "SWD.4": "GND",
}

# Trechos extras para fechar gaps do DRC KiCad (pad↔trilha / F↔B)
V4_CONNECT_ROUTES: list[tuple[str, list[tuple[float, float]], str]] = [
    ("F", [(200, 28), (200, 157), (70, 157)], "+12V_PROT"),
    ("F", [(116, 148), (168, 104)], "+3V3"),
    ("B", [(32, 14), (32, 142), (150, 142)], "+5V"),
    ("F", [(200, 60), (208, 60), (208, 14)], "IP"),
    ("B", [(56, 14), (56, 74), (54, 74)], "RPM_IN"),
    ("F", [(192, 66), (204, 66), (204, 8)], "UN"),
    ("B", [(100, 130), (94, 130)], "VBAT"),
    ("B", [(100, 130), (100, 126)], "VBAT"),
    ("B", [(202, 46.54), (202, 8), (200, 8)], "VM"),
    ("F", [(118.54, 70), (124, 82)], "SWDIO"),
    ("F", [(121.08, 70), (132, 78)], "SWCLK"),
    ("B", [(124, 82), (152, 96.98)], "SWDIO"),
    ("B", [(132, 78), (152, 94.44)], "SWCLK"),
]


def _manhattan_paths(x1: float, y1: float, x2: float, y2: float) -> list[list[tuple[float, float]]]:
    """Candidatos Manhattan + corredores (topo da placa = F.Cu)."""
    paths: list[list[tuple[float, float]]] = []
    seen: set[tuple] = set()

    def add(*pts: tuple[float, float]) -> None:
        clean: list[tuple[float, float]] = [pts[0]]
        for p in pts[1:]:
            if abs(p[0] - clean[-1][0]) > 0.05 or abs(p[1] - clean[-1][1]) > 0.05:
                clean.append(p)
        if len(clean) < 2:
            return
        key = tuple(clean)
        if key not in seen:
            seen.add(key)
            paths.append(clean)

    add((x1, y1), (x2, y1), (x2, y2))
    add((x1, y1), (x1, y2), (x2, y2))
    mids_y = {y1, y2, (y1 + y2) / 2}
    mids_x = {x1, x2, (x1 + x2) / 2}
    for y in list(mids_y) + [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18, 24, 28, 32, 38, 44, 52, 58, 64, 72, 78, 84, 92, 98,
                              106, 112, 118, 124, 132, 138, 145, 152]:
        add((x1, y1), (x1, y), (x2, y), (x2, y2))
    for x in list(mids_x) + [8, 16, 24, 32, 40, 52, 64, 76, 88, 100, 112, 124, 136, 148,
                              160, 172, 184, 196, 208, 220, 228]:
        add((x1, y1), (x, y1), (x, y2), (x2, y2))
    return paths


def _seg_collinear_overlap(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
    d: tuple[float, float],
    eps: float = 0.05,
) -> bool:
    """Trechos colineares na mesma linha com intervalo sobreposto = curto."""
    if abs(a[1] - b[1]) < eps and abs(c[1] - d[1]) < eps and abs(a[1] - c[1]) < eps:
        x1, x2 = sorted([a[0], b[0]])
        x3, x4 = sorted([c[0], d[0]])
        return x2 > x3 + eps and x4 > x1 + eps
    if abs(a[0] - b[0]) < eps and abs(c[0] - d[0]) < eps and abs(a[0] - c[0]) < eps:
        y1, y2 = sorted([a[1], b[1]])
        y3, y4 = sorted([c[1], d[1]])
        return y2 > y3 + eps and y4 > y1 + eps
    return False


def _would_cross(traces_list: list, pts: list[tuple[float, float]], net: str) -> bool:
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]

    def ori(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def near(p, q, eps=0.2):
        return abs(p[0] - q[0]) < eps and abs(p[1] - q[1]) < eps

    def hit(a, b, c, d):
        if near(a, c) or near(a, d) or near(b, c) or near(b, d):
            return False
        return ori(a, b, c) * ori(a, b, d) < -1e-9 and ori(c, d, a) * ori(c, d, b) < -1e-9

    for pts2, _w, n2 in traces_list:
        if n2 == net:
            continue
        for i in range(len(pts2) - 1):
            c, d = pts2[i], pts2[i + 1]
            for a, b in segs:
                if hit(a, b, c, d) or _seg_collinear_overlap(a, b, c, d):
                    return True
    return False


def _count_overlap(traces_list: list) -> int:
    segs = []
    for pts, _w, net in traces_list:
        for i in range(len(pts) - 1):
            segs.append((pts[i], pts[i + 1], net))
    n = 0
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            a, b, n1 = segs[i]
            c, d, n2 = segs[j]
            if n1 == n2:
                continue
            if _seg_collinear_overlap(a, b, c, d):
                n += 1
    return n


def _count_cross(traces_list: list) -> int:
    segs = []
    for pts, _w, net in traces_list:
        for i in range(len(pts) - 1):
            segs.append((pts[i], pts[i + 1], net))
    n = 0

    def ori(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def hit(p1, p2, p3, p4):
        o1, o2 = ori(p1, p2, p3), ori(p1, p2, p4)
        o3, o4 = ori(p3, p4, p1), ori(p3, p4, p2)
        return o1 * o2 < -1e-9 and o3 * o4 < -1e-9

    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            a, b, n1 = segs[i]
            c, d, n2 = segs[j]
            if n1 == n2:
                continue
            if hit(a, b, c, d):
                n += 1
    return n


def _trace_width(net: str) -> float:
    if net in ("+12V_PROT", "+12V_IN", "+12V"):
        return 1.2
    if net in ("+5V", "+3V3"):
        return 1.0
    if net.startswith("INJ") or net.startswith("RL"):
        return 0.95
    return 0.75


def _route_jumper_on_layer(
    traces_list: list,
    x1: float, y1: float, x2: float, y2: float, net: str, lane_hint: float,
) -> bool:
    w = _trace_width(net)
    for path in _manhattan_paths(x1, y1, x2, y2):
        if not _would_cross(traces_list, path, net):
            traces_list.append((path, w, net))
            return True
    for k in range(160):
        ly = lane_hint + k * 0.38
        if ly > H - 6:
            ly = lane_hint - k * 0.38
        for path in (
            [(x1, y1), (x1, ly), (x2, ly), (x2, y2)],
            [(x1, y1), (x2, ly), (x2, y2)],
        ):
            if not _would_cross(traces_list, path, net):
                traces_list.append((path, w, net))
                return True
    for k in range(160):
        lx = (x1 + x2) / 2 + (k - 80) * 0.5
        if lx < 6 or lx > W - 6:
            continue
        for path in (
            [(x1, y1), (lx, y1), (lx, y2), (x2, y2)],
            [(x1, y1), (x1, y2), (lx, y2), (x2, y2)],
        ):
            if not _would_cross(traces_list, path, net):
                traces_list.append((path, w, net))
                return True
    return False


def _route_via_net_hub(traces_list: list, x1: float, y1: float, x2: float, y2: float, net: str) -> bool:
    """Liga dois pontos passando por trilha existente da mesma net."""
    w = _trace_width(net)
    hubs: list[tuple[float, float]] = []
    for pts, _wn, n in traces_list:
        if n == net:
            hubs.extend(pts)
    for H in hubs:
        for path in (
            [(x1, y1), H, (x2, y2)],
            [(x1, y1), (H[0], y1), H, (H[0], y2), (x2, y2)],
            [(x1, y1), (x1, H[1]), H, (x2, H[1]), (x2, y2)],
        ):
            clean: list[tuple[float, float]] = [path[0]]
            for p in path[1:]:
                if abs(p[0] - clean[-1][0]) > 0.05 or abs(p[1] - clean[-1][1]) > 0.05:
                    clean.append(p)
            if len(clean) < 2:
                continue
            ok = True
            for i in range(len(clean) - 1):
                if _would_cross(traces_list, [clean[i], clean[i + 1]], net):
                    ok = False
                    break
            if ok:
                traces_list.append((clean, w, net))
                return True
    return False


def _route_jumper_perimeter(traces_list: list, x1: float, y1: float, x2: float, y2: float, net: str) -> bool:
    """Último recurso: contorno da placa."""
    w = _trace_width(net)
    m = 3.5
    perim_pts = [m, H - m, W - m, m]  # not used directly
    candidates = [
        [(x1, y1), (m, y1), (m, y2), (x2, y2)],
        [(x1, y1), (x2, y1), (x2, m), (m, m), (m, y2), (x2, y2)],
        [(x1, y1), (W - m, y1), (W - m, y2), (x2, y2)],
        [(x1, y1), (x1, H - m), (x2, H - m), (x2, y2)],
        [(x1, y1), (x1, m), (x2, m), (x2, y2)],
    ]
    for path in candidates:
        if not _would_cross(traces_list, path, net):
            traces_list.append((path, w, net))
            return True
    return False


def _route_segment(traces_list: list, ax: float, ay: float, bx: float, by: float, net: str) -> bool:
    w = _trace_width(net)
    for path in ([(ax, ay), (bx, by)], [(ax, ay), (bx, ay), (bx, by)], [(ax, ay), (ax, by), (bx, by)]):
        if not _would_cross(traces_list, path, net):
            traces_list.append((path, w, net))
            return True
    return False


def _route_two_layer_via(x1: float, y1: float, x2: float, y2: float, net: str) -> bool:
    """F.Cu até via, B.Cu da via ao destino (furo THT/via)."""
    for vx, vy in VIA_GRID:
        snap_f, snap_b = len(traces_f), len(traces_b)
        ok_f = _route_segment(traces_f, x1, y1, vx, vy, net)
        ok_b = _route_segment(traces_b, vx, vy, x2, y2, net) if ok_f else False
        if ok_f and ok_b:
            vias.append((vx, vy, net, ""))
            return True
        del traces_f[snap_f:]
        del traces_b[snap_b:]
    # Via dupla — só vizinhos próximos (evita O(n²) grande)
    for i, v1 in enumerate(VIA_GRID):
        for v2 in VIA_GRID[i + 1 : i + 40]:
            s1, s2 = len(traces_f), len(traces_b)
            ok = (
                _route_segment(traces_f, x1, y1, v1[0], v1[1], net)
                and _route_segment(traces_b, v1[0], v1[1], v2[0], v2[1], net)
                and _route_segment(traces_f, v2[0], v2[1], x2, y2, net)
            )
            if ok:
                vias.extend([(v1[0], v1[1], net, ""), (v2[0], v2[1], net, "")])
                return True
            del traces_f[s1:]
            del traces_b[s2:]
    return False


def _route_l_shape(
    traces_list: list,
    x1: float, y1: float, x2: float, y2: float, net: str,
    lane_y: float | None = None,
) -> bool:
    w = _trace_width(net)
    candidates: list[list[tuple[float, float]]] = []
    if lane_y is not None:
        candidates.append([(x1, y1), (x1, lane_y), (x2, lane_y), (x2, y2)])
    candidates.extend([
        [(x1, y1), (x1, y2), (x2, y2)],
        [(x1, y1), (x2, y1), (x2, y2)],
    ])
    for path in candidates:
        if not _would_cross(traces_list, path, net):
            traces_list.append((path, w, net))
            return True
    return False


def _clean_trace_points(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if not pts:
        return []
    clean: list[tuple[float, float]] = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - clean[-1][0]) > 0.05 or abs(p[1] - clean[-1][1]) > 0.05:
            clean.append(p)
    return clean


def _fix_bcu_bus_collisions(traces_list: list) -> list:
    """Separa barramentos B.Cu que compartilhavam o mesmo corredor (x=88, 192…)."""
    shared_x: dict[float, dict[str, float]] = {
        88.0: BCU_BUS_X,
        192.0: {"IAT": 192.0, "CLT": 194.0, "MAP": 196.0, "TPS": 198.0},
        155.0: {"IAT": 155.0, "CLT": 157.0, "MAP": 159.0, "TPS": 161.0},
    }
    out: list[tuple[list[tuple[float, float]], float, str]] = []
    for pts, w, net in traces_list:
        new_pts: list[tuple[float, float]] = []
        for x, y in pts:
            nx, ny = x, y
            for sx, mapping in shared_x.items():
                if net in mapping and abs(x - sx) < 0.15:
                    nx = mapping[net]
                    break
            if net in BCU_BUS_X and abs(x - 88.0) < 0.15:
                nx = BCU_BUS_X[net]
            for ax, nets in BCU_X_ANCHOR_NETS.items():
                if net in nets and abs(x - ax) < 0.15 and net in BCU_BUS_X:
                    nx = BCU_BUS_X[net]
            for ay, nets in BCU_Y_ANCHOR_NETS.items():
                if net in nets and abs(y - ay) < 0.15 and net in BCU_Y_OFFSET:
                    ny = BCU_Y_OFFSET[net]
            if net == "IP" and abs(y - 60.0) < 0.15 and x >= 180.0:
                ny = BCU_Y_OFFSET["IP"]
            if net == "UN" and abs(y - 70.0) < 0.15 and x >= 198.0:
                ny = BCU_Y_OFFSET["UN"]
            if net == "UN" and abs(y - 74.0) < 0.15 and x >= 198.0:
                ny = BCU_Y_OFFSET["UN"]
            if net == "UN" and abs(y - 78.0) < 0.15 and x >= 198.0:
                ny = BCU_Y_OFFSET["UN"]
            if net == "UN" and abs(x - 200.0) < 0.15:
                nx = 206.0
            if net == "IP" and abs(x - 220.0) < 0.15 and y > 10.0:
                nx = 224.0
            new_pts.append((nx, ny))
        cleaned = _clean_trace_points(new_pts)
        if len(cleaned) >= 2:
            out.append((cleaned, w, net))
    return out


def _strip_nets(traces_list: list, nets: frozenset[str]) -> list:
    return [(pts, w, net) for pts, w, net in traces_list if net not in nets]


def _route_forced(
    traces_list: list,
    x1: float, y1: float, x2: float, y2: float, net: str,
    lane_y: float | None,
) -> bool:
    """Rota prioritária — usa faixa_y fixa quando informada."""
    w = _trace_width(net)
    if lane_y is not None:
        path = [(x1, y1), (x1, lane_y), (x2, lane_y), (x2, y2)]
        if not _would_cross(traces_list, path, net):
            traces_list.append((path, w, net))
            return True
        return False
    paths: list[list[tuple[float, float]]] = [
        [(x1, y1), (x1, y2), (x2, y2)],
        [(x1, y1), (x2, y1), (x2, y2)],
    ]
    for path in paths:
        if not _would_cross(traces_list, path, net):
            traces_list.append((path, w, net))
            return True
    return False


def _route_canh() -> bool:
    """CANH por via F↔B após demais rotas (MCU 128,90 → CN1 40,8)."""
    if any(n == "CANH" for _, _, n in traces_f + traces_b):
        return True
    w = _trace_width("CANH")
    for fpath, bpath, via in CANH_VIA_CANDIDATES:
        if not _would_cross(traces_f, fpath, "CANH") and not _would_cross(traces_b, bpath, "CANH"):
            traces_f.append((fpath, w, "CANH"))
            traces_b.append((bpath, w, "CANH"))
            vias.append((via[0], via[1], "CANH", ""))
            return True
    return False


def _route_path(traces_list: list, path: list[tuple[float, float]], net: str) -> bool:
    if len(path) < 2:
        return False
    if not _would_cross(traces_list, path, net):
        traces_list.append((path, _trace_width(net), net))
        return True
    return False


def _prune_bcu_nets(traces_list: list, nets: frozenset[str]) -> list:
    """Remove trilhas B.Cu de redes re-roteadas na F.Cu (evita barramento comum)."""
    return [(pts, w, net) for pts, w, net in traces_list if net not in nets]


def _covered_by_priority(j: tuple[float, float, float, float, str]) -> bool:
    for _layer, x1, y1, x2, y2, net, _lane in PRIORITY_A + PRIORITY_B:
        if _same_jumper(j, x1, y1, x2, y2, net):
            return True
    jx1, jy1, jx2, jy2, jn = j
    if (
        jn == "+3V3"
        and abs(jx2 - 168) < 0.15
        and abs(jy2 - 136) < 0.15
        and jy1 >= 100
    ):
        return True
    if jn == "+3V3" and abs(jx1 - 70) < 0.15 and abs(jy1 - 90) < 0.15:
        return True
    if jn == "+12V_PROT" and abs(jx1 - 200) < 0.2 and abs(jy1 - 14) < 0.2:
        return True
    if jn in ("SWDIO", "SWCLK"):
        return True
    return False


def _same_jumper(
    j: tuple[float, float, float, float, str],
    x1: float, y1: float, x2: float, y2: float, net: str,
) -> bool:
    jx1, jy1, jx2, jy2, jn = j
    return (
        jn == net
        and abs(jx1 - x1) < 0.15
        and abs(jy1 - y1) < 0.15
        and abs(jx2 - x2) < 0.15
        and abs(jy2 - y2) < 0.15
    )


def _route_jumper_any(x1: float, y1: float, x2: float, y2: float, net: str, lane_hint: float) -> str | None:
    """Tenta F.Cu, depois B.Cu, hub e perímetro. Retorna camada usada."""
    if _route_jumper_on_layer(traces_f, x1, y1, x2, y2, net, lane_hint):
        return LAYER_TOP
    if _route_via_net_hub(traces_f, x1, y1, x2, y2, net):
        return LAYER_TOP
    if _route_jumper_perimeter(traces_f, x1, y1, x2, y2, net):
        return LAYER_TOP
    if _route_jumper_on_layer(traces_b, x1, y1, x2, y2, net, 150.0 - lane_hint):
        return LAYER_BOTTOM
    if _route_via_net_hub(traces_b, x1, y1, x2, y2, net):
        return LAYER_BOTTOM
    if _route_jumper_perimeter(traces_b, x1, y1, x2, y2, net):
        return LAYER_BOTTOM
    if _route_two_layer_via(x1, y1, x2, y2, net):
        return "via"
    return None


def build_layout() -> None:
    global pads, traces_b, traces_f, traces, jumpers, pad_nets, W, H, vias

    _p2.build_layout()
    pads = dict(_p2.pads)
    W, H = _p2.W, _p2.H
    traces_b = _strip_nets(
        _prune_bcu_nets(
            _fix_bcu_bus_collisions(
                [([tuple(p) for p in pts], w, net) for pts, w, net in _p2.traces]
            ),
            BCU_PRUNE_NETS,
        ),
        BCU_STRIP_NETS,
    )
    jumpers = list(_p2.jumpers)
    traces_f = _strip_nets([], FCU_STRIP_NETS)
    vias = []

    failed_prio: list[tuple] = []
    for routes in (PRIORITY_A,):
        for layer, x1, y1, x2, y2, net, lane_y in routes:
            tl = traces_f if layer == "F" else traces_b
            if net in CAN_PATHS:
                ok = _route_path(tl, CAN_PATHS[net], net)
            else:
                ok = _route_forced(tl, x1, y1, x2, y2, net, lane_y)
            if not ok:
                failed_prio.append((x1, y1, x2, y2, net))

    for layer, net, path in SPECIAL_ROUTES:
        tl = traces_f if layer == "F" else traces_b
        if not _route_path(tl, path, net):
            failed_prio.append((path[0][0], path[0][1], path[-1][0], path[-1][1], net))

    for layer, x1, y1, x2, y2, net, lane_y in PRIORITY_B:
        tl = traces_f if layer == "F" else traces_b
        if net in CAN_PATHS:
            ok = _route_path(tl, CAN_PATHS[net], net)
        else:
            ok = _route_forced(tl, x1, y1, x2, y2, net, lane_y)
        if not ok:
            failed_prio.append((x1, y1, x2, y2, net))

    if not any(n == "CANL" for _, _, n in traces_f + traces_b):
        if not _route_two_layer_via(134, 90, 44, 8, "CANL"):
            failed_prio.append((134, 90, 44, 8, "CANL"))

    if not any(n == "CANH" for _, _, n in traces_f + traces_b):
        if not _route_canh():
            failed_prio.append((128, 90, 40, 8, "CANH"))

    routed_nets = {n for _, _, n in traces_f + traces_b}
    remaining = [
        j for j in jumpers
        if not _covered_by_priority(j) and j[4] not in routed_nets
    ]

    failed: list[tuple] = list(failed_prio)
    order = sorted(
        remaining,
        key=lambda j: (
            j[4] in ("+12V_PROT", "+12V_IN", "+5V", "+3V3"),
            abs(j[2] - j[0]) + abs(j[3] - j[1]),
        ),
    )
    for idx, (x1, y1, x2, y2, net) in enumerate(order):
        lane = 20.0 + (idx % 50) * 1.25
        if _route_jumper_any(x1, y1, x2, y2, net, lane) is None:
            failed.append((x1, y1, x2, y2, net))

    # Retry final: bordas + barramento potência
    still = []
    seen_retry: set[str] = set()
    for x1, y1, x2, y2, net in failed:
        if net in seen_retry:
            continue
        seen_retry.add(net)
        routed = False
        for edge_x in (4.5, 6.0, 8.0, 232.0, 234.5, 236.0):
            for tl in (traces_f, traces_b):
                path = [(x1, y1), (edge_x, y1), (edge_x, y2), (x2, y2)]
                if not _would_cross(tl, path, net):
                    tl.append((path, _trace_width(net), net))
                    routed = True
                    break
            if routed:
                break
        if not routed and net in ("+3V3", "+5V", "+12V_PROT", "+12V_IN"):
            for ly in (156, 154, 152, 148, 145, 142, 138, 134, 128, 120):
                for tl in (traces_f, traces_b):
                    path = [(x1, y1), (x1, ly), (x2, ly), (x2, y2)]
                    if not _would_cross(tl, path, net):
                        tl.append((path, _trace_width(net), net))
                        routed = True
                        break
                if routed:
                    break
        if not routed and _route_two_layer_via(x1, y1, x2, y2, net):
            routed = True
        if not routed:
            still.append((x1, y1, x2, y2, net))
    failed = still

    if failed:
        raise RuntimeError(
            f"prodv4: {len(failed)} ligações sem rota — "
            + ", ".join(f"{n}" for *_, n in failed[:8])
        )

    cross_b = _count_cross(traces_b)
    cross_f = _count_cross(traces_f)
    overlap_b = _count_overlap(traces_b)
    overlap_f = _count_overlap(traces_f)
    if cross_b or cross_f or overlap_b or overlap_f:
        raise RuntimeError(
            f"prodv4 DRC FAIL: B cross={cross_b} overlap={overlap_b} · "
            f"F cross={cross_f} overlap={overlap_f}"
        )

    traces = [
        *[(pts, w, net, LAYER_BOTTOM) for pts, w, net in traces_b],
        *[(pts, w, net, LAYER_TOP) for pts, w, net in traces_f],
    ]
    jumpers = []  # tudo virou cobre

    _apply_v4_connect_routes()
    _purge_colocated_vias()
    combined = traces_b + traces_f
    pad_nets = _compute_pad_nets_v4(combined)
    _stitch_traces_to_pads(pad_nets)


def _apply_v4_connect_routes() -> None:
    """Fecha gaps reportados pelo DRC KiCad (10 unconnected + SWD)."""
    global vias
    # Remove SWD legado com via compartilhada em (128, 80)
    for tl in (traces_f, traces_b):
        kept: list[tuple[list[tuple[float, float]], float, str]] = []
        for pts, w, net in tl:
            if net in ("SWDIO", "SWCLK") and any(
                abs(x - 128) < 0.15 and abs(y - 80) < 0.15 for x, y in pts
            ):
                continue
            kept.append((pts, w, net))
        tl[:] = kept
    vias = [
        v for v in vias
        if not (v[2] in ("SWDIO", "SWCLK") and abs(v[0] - 128) < 0.15 and abs(v[1] - 80) < 0.15)
    ]

    for layer, path, net in V4_CONNECT_ROUTES:
        tl = traces_f if layer == "F" else traces_b
        if not _would_cross(tl, path, net):
            tl.append((path, _trace_width(net), net))
    for vx, vy, vnet in ((124, 82, "SWDIO"), (132, 78, "SWCLK")):
        if not any(n == vnet for _, _, n in traces_f + traces_b):
            continue
        if not any(abs(v[0] - vx) < 0.1 and abs(v[1] - vy) < 0.1 and v[2] == vnet for v in vias):
            vias.append((vx, vy, vnet, ""))

    # SWCLK: F.Cu até MCU.R15 (evita via compartilhada)
    if "MCU.R15" in pads:
        rx, ry = pads["MCU.R15"][0], pads["MCU.R15"][1]
        if not _route_jumper_on_layer(traces_f, 132, 78, rx, ry, "SWCLK", 94.0):
            _route_jumper_on_layer(traces_f, 121.08, 70, rx, ry, "SWCLK", 94.0)


def _purge_colocated_vias() -> None:
    """Remove vias distintas no mesmo furo (ex.: SWDIO/SWCLK em 128,80)."""
    global vias
    seen: dict[tuple[float, float], tuple[float, float, str, str]] = {}
    cleaned: list[tuple[float, float, str, str]] = []
    for item in vias:
        key = (round(item[0], 2), round(item[1], 2))
        if key in seen:
            continue
        seen[key] = item
        cleaned.append(item)
    vias = cleaned


def _stitch_traces_to_pads(pad_net_map: dict[str, str], max_gap: float = 1.6) -> None:
    """Segmentos curtos pad↔trilha para o KiCad reconhecer conexão elétrica."""
    import math

    for layer_name, traces_list in ((LAYER_BOTTOM, traces_b), (LAYER_TOP, traces_f)):
        stubs: list[tuple[list[tuple[float, float]], float, str]] = []
        for pname, net in pad_net_map.items():
            if not net or pname not in pads:
                continue
            px, py, _od, _dr = pads[pname]
            best: tuple[tuple[float, float], float] | None = None
            best_d = max_gap
            for pts, w, tnet in traces_list:
                if tnet != net:
                    continue
                for ex, ey in (pts[0], pts[-1]):
                    d = math.hypot(px - ex, py - ey)
                    if 0.08 < d < best_d:
                        best_d = d
                        best = ((ex, ey), w)
            if best is None:
                continue
            (ex, ey), w = best
            path = [(ex, ey), (px, py)]
            if not _would_cross(traces_list, path, net):
                stubs.append((path, w, net))
        for path, w, net in stubs:
            traces_list.append((path, w, net))

    global traces
    traces = [
        *[(pts, w, net, LAYER_BOTTOM) for pts, w, net in traces_b],
        *[(pts, w, net, LAYER_TOP) for pts, w, net in traces_f],
    ]


def _compute_pad_nets_v4(all_traces: list) -> dict[str, str]:
    import math

    out: dict[str, str] = dict(STATIC_PAD_NETS)
    priority = {"GND": 0, "+12V_PROT": 1, "+5V": 2, "+3V3": 3}
    for pts, _w, net in all_traces:
        for x, y in pts:
            for pname, (px, py, _od, _dr) in pads.items():
                if math.hypot(px - x, py - y) <= 0.5:
                    if pname in out and out[pname] != net:
                        if priority.get(net, 99) < priority.get(out[pname], 99):
                            out[pname] = net
                    elif pname not in out:
                        out[pname] = net
    for i, net in _p2.CN1_PAD_NETS.items():
        key = f"CN1.{i}"
        if key in pads:
            out[key] = net
    for i, net in _p2.CN2_PAD_NETS.items():
        key = f"CN2.{i}"
        if key in pads and net:
            out[key] = net
    gnd_exact = {
        "BUCK.GND", "LDO.GND", "CAN.GND", "U817.2", "U817.3", "U8628.4", "U6004.4",
        "SWD.4", "MCU.R2", "R1.B", "D2.K", "C1.B", "C2.B", "C3.B", "C4.B",
        "C10.B", "C11.B", "C12.B", "C13.B", "C20.B", "C30.B", "C31.B", "C32.B", "C33.B",
        "R43.B", "U8.GND", "QREV.S",
    }
    for pname in pads:
        if pname in gnd_exact:
            out[pname] = "GND"
        if pname.startswith("QINJ") and pname.endswith(".S"):
            out[pname] = "GND"
        if pname.startswith("QHEAT") and pname.endswith(".S"):
            out[pname] = "GND"
        if pname.startswith("QRL") and pname.endswith(".S"):
            out[pname] = "GND"
        if pname.startswith("C") and pname.endswith(".B") and pname[0] == "C":
            out.setdefault(pname, "GND")
    # Segundo terminal dos divisores / pull para sinal
    for ref, net in (
        ("R40.B", "IAT"), ("R41.B", "CLT"), ("R42.B", "MAP"), ("R53.B", "TPS"),
        ("R50.B", "IAT"), ("R51.B", "CLT"), ("R52.B", "MAP"), ("R54.B", "TPS"),
        ("R10.B", "GINJ1"), ("R11.B", "GINJ2"), ("R12.B", "GINJ3"), ("R13.B", "GINJ4"),
        ("R30.B", "GRL1"), ("R31.B", "GRL2"), ("R32.B", "GRL3"),
        ("R61.B", "RPM_IN"), ("R62.B", "RPM_OUT"),
        ("R76.A", "VM"), ("R77.A", "VM"), ("R78.B", "RI_PULSE"),
    ):
        if ref in pads:
            out[ref] = net
    return out


def _assign_pad_nets(all_traces: list) -> dict[str, str]:
    return _compute_pad_nets_v4(all_traces)


def _render_outputs() -> None:
    from PIL import Image, ImageDraw, ImageFont

    PPM = 9.0
    DPI = int(25.4 * PPM)

    def font(mm):
        try:
            return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", max(7, int(mm * PPM)))
        except OSError:
            return ImageFont.load_default()

    def px(*a):
        return tuple(int(round(v * PPM)) for v in a)

    def Y(y):
        return H - y

    def P(x, y):
        return px(x, Y(y))

    img = Image.new("RGB", px(W, H), (12, 16, 20))
    d = ImageDraw.Draw(img)
    d.rectangle([*px(0.3, 0.3), *px(W - 0.3, H - 0.3)], fill=(16, 72, 44), outline=(210, 220, 210), width=2)

    for pts, w, net, layer in traces:
        col = (255, 200, 80) if layer == LAYER_TOP else (210, 185, 55)
        if net.startswith("+12"):
            col = (230, 80, 80) if layer == LAYER_BOTTOM else (255, 120, 120)
        flat = []
        for x, y in pts:
            flat.extend(P(x, y))
        if len(flat) >= 4:
            d.line(flat, fill=col, width=max(2, int(w * PPM * 0.85)))

    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MH_"):
            continue
        r = od / 2
        fill = (215, 180, 55) if drill > 0 else (190, 110, 230)
        d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], fill=fill, outline=(80, 60, 20))
        if drill > 0:
            rd = drill / 2
            d.ellipse([*P(x - rd, y + rd), *P(x + rd, y - rd)], fill=(12, 16, 20))

    d.text(px(3, 2), "INJET RACING prodv4 · 2L FR4 · F.Cu+ B.Cu · 0 fios", fill=(240, 245, 240), font=font(2.3))
    d.text(
        px(3, 6),
        f"B.Cu={len(traces_b)} F.Cu={len(traces_f)} cruz=0  {W}x{H}mm",
        fill=(140, 255, 160),
        font=font(2.0),
    )
    d.text(px(3, 9), "Laranja claro=F.Cu (topo)  Escuro=B.Cu (baixo)", fill=(180, 180, 180), font=font(1.6))
    img.save(OUT / "ecu-pcb-prodv4-assembly.png", dpi=(DPI, DPI))

    (OUT / "ecu-pcb-prodv4-drc.md").write_text(
        "\n".join([
            "# DRC — INJET RACING ECU prodv4 (2 camadas FR4)",
            "",
            f"- Placa: **{W}×{H} mm**",
            f"- **B.Cu:** {len(traces_b)} trilhas (roteamento principal prodv2)",
            f"- **F.Cu:** {len(traces_f)} trilhas (ex-jumpers prodv2 → cobre topo)",
            "- **Fios/jumpers:** **0**",
            f"- **Vias F↔B:** **{len(vias)}**",
            f"- Cruzamentos B.Cu: **{_count_cross(traces_b)}**",
            f"- Cruzamentos F.Cu: **{_count_cross(traces_f)}**",
            f"- Sobreposição B.Cu: **{_count_overlap(traces_b)}**",
            f"- Sobreposição F.Cu: **{_count_overlap(traces_f)}**",
            "",
            "## Stackup",
            "",
            "| Camada | Função |",
            "|---|---|",
            "| F.Cu | Componentes THT + trilhas de ligação (face componentes) |",
            "| FR4 | Core 1.6 mm |",
            "| B.Cu | Trilhas principais + GND pour |",
            "",
            "## vs prodv3",
            "",
            "| | prodv3 | prodv4 |",
            "|---|---|---|",
            "| Pad nets KiCad | parcial | **completo (MCU+passivos)** |",
            "| Stubs pad↔trilha | não | **sim** |",
            "",
        ]),
        encoding="utf-8",
    )


def main() -> None:
    build_layout()
    _render_outputs()
    print(f"prodv4: B.Cu={len(traces_b)} F.Cu={len(traces_f)} jumpers=0 pads={len(pads)} nets={len(pad_nets)}")
    print(f"  {OUT / 'ecu-pcb-prodv4-assembly.png'}")
    print(f"  {OUT / 'ecu-pcb-prodv4-drc.md'}")


if __name__ == "__main__":
    main()
