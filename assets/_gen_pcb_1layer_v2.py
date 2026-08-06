# -*- coding: utf-8 -*-
"""
INJET RACING ECU — PCB 1-LAYER SEM CRUZAMENTOS
Fenolite 200×100 mm | cobre 1 face | THT topo | AD8628 SMD no cobre

Roteador em grade (A*) com clearance. Se não houver caminho livre,
insere JUMPER (2 pads) — fio no lado dos componentes (não é cobre).
"""
from __future__ import annotations

from collections import deque
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"e:\injet racing\assets")
W, H = 200.0, 100.0
PPM = 12.0
DPI = int(25.4 * PPM)
GRID = 0.5  # mm por célula
CLR = 1  # células de folga entre nets diferentes (0.5 mm → 0.5mm clearance mínimo; CLR=2 → 1mm)

pads: dict[str, tuple[float, float, float, float]] = {}
outlines: list[tuple[float, float, float, float, str, str]] = []
traces: list[tuple[list[tuple[float, float]], float, str]] = []
jumpers: list[tuple[str, str, str]] = []  # (padA, padB, net) — fio no TOPO
route_fails: list[str] = []


def font(mm):
    px = max(9, int(mm * PPM))
    try:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", px)
    except OSError:
        return ImageFont.load_default()


def px(*xy):
    return tuple(int(round(v * PPM)) for v in xy)


def pad(name, x, y, od=1.9, drill=0.95):
    pads[name] = (x, y, od, drill)


def axial(a, b, x1, y1, x2, y2, od=1.7, drill=0.85):
    pad(a, x1, y1, od, drill)
    pad(b, x2, y2, od, drill)


def to220(prefix, x, y):
    pad(f"{prefix}.G", x - 2.54, y, 2.3, 1.1)
    pad(f"{prefix}.D", x, y, 2.3, 1.1)
    pad(f"{prefix}.S", x + 2.54, y, 2.3, 1.1)
    outlines.append((x - 5, y - 1.5, x + 5, y + 11, prefix, "top"))


def to92(prefix, x, y):
    pad(f"{prefix}.S", x - 1.27, y, 1.6, 0.8)
    pad(f"{prefix}.G", x, y + 1.8, 1.6, 0.8)
    pad(f"{prefix}.D", x + 1.27, y, 1.6, 0.8)
    outlines.append((x - 3, y - 1, x + 3, y + 5, prefix, "top"))


def dip(prefix, x0, y0, n, pitch=2.54, row=7.62):
    half = n // 2
    for i in range(half):
        pad(f"{prefix}.{i+1}", x0, y0 + i * pitch, 1.7, 0.85)
        pad(f"{prefix}.{n - i}", x0 + row, y0 + i * pitch, 1.7, 0.85)
    outlines.append((x0 - 1.2, y0 - 1.2, x0 + row + 1.2, y0 + (half - 1) * pitch + 1.2, prefix, "top"))


def soic8(prefix, x0, y0, pitch=1.27, row=5.4):
    for i in range(4):
        pad(f"{prefix}.{i+1}", x0, y0 + i * pitch, 1.35, 0.0)
        pad(f"{prefix}.{8 - i}", x0 + row, y0 + i * pitch, 1.35, 0.0)
    outlines.append((x0 - 1, y0 - 1, x0 + row + 1, y0 + 3 * pitch + 1, prefix + " SMD↓", "bot"))


def header(prefix, x0, y0, n, pitch=2.54):
    for i in range(n):
        pad(f"{prefix}.{i+1}", x0 + i * pitch, y0, 1.8, 1.0)


# ===================== GRADE / A* =====================
gw = int(W / GRID) + 1
gh = int(H / GRID) + 1
# occ[y][x] = net name or None. Same net OK.
occ: list[list[str | None]] = [[None] * gw for _ in range(gh)]


def xy_to_cell(x, y):
    return int(round(x / GRID)), int(round(y / GRID))


def cell_to_xy(cx, cy):
    return cx * GRID, cy * GRID


def mark_disk(x, y, r_mm, net):
    cr = max(1, int(round(r_mm / GRID)))
    cx, cy = xy_to_cell(x, y)
    for dy in range(-cr, cr + 1):
        for dx in range(-cr, cr + 1):
            if dx * dx + dy * dy <= cr * cr + 1:
                xx, yy = cx + dx, cy + dy
                if 0 <= xx < gw and 0 <= yy < gh:
                    if occ[yy][xx] is None or occ[yy][xx] == net:
                        occ[yy][xx] = net


def mark_pad(name, net):
    x, y, od, _ = pads[name]
    mark_disk(x, y, od / 2 + 0.15, net)


def can_enter(cx, cy, net, half_w_cells):
    for dy in range(-half_w_cells - CLR, half_w_cells + CLR + 1):
        for dx in range(-half_w_cells - CLR, half_w_cells + CLR + 1):
            xx, yy = cx + dx, cy + dy
            if not (0 <= xx < gw and 0 <= yy < gh):
                return False
            o = occ[yy][xx]
            if o is not None and o != net:
                # dentro do half_w+clearance estrito
                if abs(dx) <= half_w_cells + CLR and abs(dy) <= half_w_cells + CLR:
                    return False
    return True


def paint_path(cells, net, half_w_cells):
    for cx, cy in cells:
        for dy in range(-half_w_cells, half_w_cells + 1):
            for dx in range(-half_w_cells, half_w_cells + 1):
                xx, yy = cx + dx, cy + dy
                if 0 <= xx < gw and 0 <= yy < gh:
                    if occ[yy][xx] is None or occ[yy][xx] == net:
                        occ[yy][xx] = net


def astar(start, goal, net, width_mm):
    sx, sy = xy_to_cell(*start)
    gx, gy = xy_to_cell(*goal)
    half = max(0, int(round((width_mm / 2) / GRID)))
    if not (0 <= sx < gw and 0 <= sy < gh and 0 <= gx < gw and 0 <= gy < gh):
        return None
    # allow start/goal even if occupied by same net
    q = deque([(sx, sy)])
    came = {(sx, sy): None}
    while q:
        cx, cy = q.popleft()
        if (cx, cy) == (gx, gy):
            # reconstruct
            path = []
            cur = (gx, gy)
            while cur is not None:
                path.append(cur)
                cur = came[cur]
            path.reverse()
            return path
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in came:
                continue
            if not (0 <= nx < gw and 0 <= ny < gh):
                continue
            # goal always enterable if same net pads
            if (nx, ny) == (gx, gy) or can_enter(nx, ny, net, half):
                came[(nx, ny)] = (cx, cy)
                q.append((nx, ny))
    return None


def simplify(cells):
    """Remove colineares."""
    if len(cells) <= 2:
        return cells
    out = [cells[0]]
    for i in range(1, len(cells) - 1):
        x0, y0 = out[-1]
        x1, y1 = cells[i]
        x2, y2 = cells[i + 1]
        if (x1 - x0) * (y2 - y1) == (y1 - y0) * (x2 - x1) and (x1 - x0) * (x2 - x1) >= 0 and (y1 - y0) * (y2 - y1) >= 0:
            continue
        out.append(cells[i])
    out.append(cells[-1])
    return out


def route(net, a, b, w=0.9):
    """Liga pad a → pad b sem cruzar outras nets. Se falhar, jumper."""
    if a not in pads or b not in pads:
        route_fails.append(f"missing {a}->{b}")
        return False
    ax, ay = pads[a][0], pads[a][1]
    bx, by = pads[b][0], pads[b][1]
    mark_pad(a, net)
    mark_pad(b, net)
    path = astar((ax, ay), (bx, by), net, w)
    if path is None:
        # jumper: dois pads próximos ao destino, fio no topo
        jn = len(jumpers) + 1
        jx, jy = bx - 3.0, by + 3.0
        # achar célula livre perto de b
        for r in range(2, 20):
            found = False
            for ang in range(0, 360, 30):
                import math
                jx = bx + r * 0.7 * math.cos(ang * 3.1415 / 180)
                jy = by + r * 0.7 * math.sin(ang * 3.1415 / 180)
                if 3 < jx < W - 3 and 3 < jy < H - 3:
                    cx, cy = xy_to_cell(jx, jy)
                    if can_enter(cx, cy, net, 1):
                        found = True
                        break
            if found:
                break
        ja, jb = f"JMP{jn}.A", f"JMP{jn}.B"
        pad(ja, jx, jy, 1.8, 0.9)
        pad(jb, jx + 2.54, jy, 1.8, 0.9)
        jumpers.append((ja, jb, net))
        mark_pad(ja, net)
        mark_pad(jb, net)
        # route a → ja on copper; jb → b on copper; ja-jb = WIRE TOP
        p1 = astar((ax, ay), (jx, jy), net, w)
        p2 = astar((jx + 2.54, jy), (bx, by), net, w)
        if p1 is None or p2 is None:
            route_fails.append(f"{net}: {a}->{b} FAIL+jumper")
            return False
        half = max(0, int(round((w / 2) / GRID)))
        paint_path(p1, net, half)
        paint_path(p2, net, half)
        pts1 = [cell_to_xy(*c) for c in simplify(p1)]
        pts2 = [cell_to_xy(*c) for c in simplify(p2)]
        traces.append((pts1, w, net))
        traces.append((pts2, w, net))
        return True
    half = max(0, int(round((w / 2) / GRID)))
    paint_path(path, net, half)
    pts = [cell_to_xy(*c) for c in simplify(path)]
    traces.append((pts, w, net))
    return True


def route_many(net, hub, others, w=0.9):
    for o in others:
        route(net, hub, o, w)


# ===================== COLOCAÇÃO (facilita 1-layer) =====================
# Barramentos nas bordas; sinais sobem/descem em colunas sem cruzar.

CN1_MAP = {
    1: "+12V_IGN", 2: "+12V_BAT", 3: "GND_P", 4: "GND_P", 5: "GND_S",
    6: "+5V", 7: "+3V3", 8: "IAT", 9: "CLT", 10: "MAP", 11: "TPS", 12: "RPM",
    13: "INJ1", 14: "INJ2", 15: "INJ3", 16: "INJ4",
    17: "RL2", 18: "RL1", 19: "RL3", 20: "CANH", 21: "CANL",
    22: "TACHO", 23: "START", 24: "SHIELD",
}

ATX_P = 4.20
# CN1 bottom-left
for i in range(12):
    pad(f"CN1.{i+1}", 8 + i * ATX_P, 14, 2.3, 1.15)
    pad(f"CN1.{i+13}", 8 + i * ATX_P, 8, 2.3, 1.15)
outlines.append((5, 5, 8 + 11 * ATX_P + 3, 18, "CN1 ATX-24", "top"))

# CN2 bottom-right PCIe-6
for i in range(3):
    pad(f"CN2.{i+1}", 175 + i * ATX_P, 14, 2.3, 1.15)
    pad(f"CN2.{i+4}", 175 + i * ATX_P, 8, 2.3, 1.15)
outlines.append((172, 5, 175 + 2 * ATX_P + 3, 18, "CN2 PCIe-6", "top"))

# POWER top-left
to220("QREV", 16, 88)
axial("CBULK.A", "CBULK.K", 28, 90, 36, 90, 2.5, 0.9)
axial("CIN.A", "CIN.K", 28, 84, 32, 84)
axial("TVS.A", "TVS.K", 40, 90, 40, 84)
axial("RG.A", "RG.B", 10, 82, 10, 76)
axial("DZ.A", "DZ.K", 14, 82, 14, 76)
pad("BUCK.VIN", 48, 90, 2.0, 1.0)
pad("BUCK.GND", 54, 90, 2.0, 1.0)
pad("BUCK.VOUT", 48, 82, 2.0, 1.0)
pad("BUCK.FB", 54, 82, 2.0, 1.0)
outlines.append((46, 79, 56, 93, "BUCK5V", "top"))
pad("LDO.IN", 60, 90, 2.0, 1.0)
pad("LDO.GND", 66, 90, 2.0, 1.0)
pad("LDO.OUT", 63, 82, 2.0, 1.0)
axial("C5IN.A", "C5IN.B", 70, 90, 74, 90)
axial("C33.A", "C33.B", 70, 84, 74, 84)
axial("C33n.A", "C33n.B", 70, 78, 74, 78)
outlines.append((58, 76, 76, 93, "LDO3V3", "top"))

# Injectors top center → right
for i, x in enumerate([86, 100, 114, 128]):
    to220(f"QINJ{i+1}", x, 88)
    axial(f"RG{i+1}.A", f"RG{i+1}.B", x - 2.54, 80, x - 2.54, 74)
    axial(f"RGS{i+1}.A", f"RGS{i+1}.B", x - 2.54, 72, x + 0.5, 72)
    axial(f"DF{i+1}.A", f"DF{i+1}.K", x + 5.2, 88, x + 5.2, 82)

to220("QHEAT", 148, 88)
axial("RGH.A", "RGH.B", 145.46, 80, 145.46, 74)
axial("RGSH.A", "RGSH.B", 145.46, 72, 149, 72)

# Relay drivers left mid
for i, x in enumerate([12, 22, 32]):
    to92(f"QRL{i+1}", x, 56)
    axial(f"RRL{i+1}.A", f"RRL{i+1}.B", x, 50, x, 44)
    axial(f"DRL{i+1}.A", f"DRL{i+1}.K", x + 4, 56, x + 4, 50)

# MCU center — headers
mcu_lx, mcu_rx, mcu_yt = 72.0, 124.0, 64.0
for i in range(20):
    pad(f"MCU.L{i+1}", mcu_lx, mcu_yt - i * 2.54, 1.65, 0.95)
    pad(f"MCU.R{i+1}", mcu_rx, mcu_yt - i * 2.54, 1.65, 0.95)
outlines.append((mcu_lx - 2, mcu_yt - 19 * 2.54 - 2, mcu_rx + 2, mcu_yt + 2, "STM32F407", "top"))
header("SWD", 90, 28, 4)
outlines.append((88, 25, 102, 32, "SWD", "top"))

# Sensors right column (stacked vertically — fácil de rotear sem cruzar)
# ordem de cima p/ baixo: IAT CLT MAP TPS
sy = [62, 54, 46, 38]
names = ["IAT", "CLT", "MAP", "TPS"]
for i, (y, n) in enumerate(zip(sy, names)):
    if n in ("IAT", "CLT"):
        axial(f"R{n}.A", f"R{n}.B", 150, y, 158, y)  # 2K26
        axial(f"C{n}.A", f"C{n}.B", 162, y, 162, y - 4)
        axial(f"S{n}.A", f"S{n}.B", 166, y, 174, y)  # 1k
    elif n == "MAP":
        axial("RMAP1.A", "RMAP1.B", 150, y, 158, y)  # 10k
        axial("RMAP2.A", "RMAP2.B", 158, y, 158, y - 4)  # 18k
        axial("CMAP.A", "CMAP.B", 162, y, 162, y - 4)
        axial("SMAP.A", "SMAP.B", 166, y, 174, y)
    else:
        axial("CTPS.A", "CTPS.B", 162, y, 162, y - 4)
        axial("STPS.A", "STPS.B", 166, y, 174, y)
outlines.append((148, 32, 178, 66, "SENSORS", "top"))

# RPM left of MCU bottom
dip("U817", 48, 30, 4)
axial("RR1.A", "RR1.B", 38, 34, 46, 34)
axial("RR2.A", "RR2.B", 30, 34, 38, 34)
axial("DR.A", "DR.K", 42, 30, 42, 24)
axial("RR3.A", "RR3.B", 58, 38, 58, 32)
axial("CR.A", "CR.B", 62, 32, 62, 26)
outlines.append((28, 22, 66, 42, "RPM", "top"))

# CAN below MCU right
pad("CAN.VCC", 90, 40, 1.9, 1.0)
pad("CAN.GND", 96, 40, 1.9, 1.0)
pad("CAN.TX", 90, 34, 1.9, 1.0)
pad("CAN.RX", 96, 34, 1.9, 1.0)
pad("CAN.H", 102, 40, 1.9, 1.0)
pad("CAN.L", 108, 40, 1.9, 1.0)
outlines.append((88, 31, 112, 44, "CAN", "top"))

# Lambda bottom-right above CN2
dip("U6004", 140, 20, 14)
soic8("U8628", 162, 22)
axial("RSH.A", "RSH.B", 158, 36, 166, 36)
axial("RESR.A", "RESR.B", 158, 42, 166, 42)
axial("CIP.A", "CIP.B", 170, 36, 170, 30)
axial("CUN.A", "CUN.B", 174, 42, 174, 36)
axial("C5A.A", "C5A.B", 134, 28, 134, 22)
axial("RO1.A", "RO1.B", 148, 28, 156, 28)
axial("RO2.A", "RO2.B", 156, 28, 156, 22)
axial("CO2.A", "CO2.B", 160, 28, 160, 22)
outlines.append((132, 16, 178, 48, "LAMBDA", "top"))

# Bloquear área fora da placa (já limitado) + furos montagem
for x, y in [(4, 4), (196, 4), (4, 96), (196, 96)]:
    pad(f"MTG_{x}_{y}", x, y, 3.5, 3.2)
    mark_pad(f"MTG_{x}_{y}", "__HOLE__")


# ===================== ROTEAMENTO ORDENADO =====================
def run_routes():
    # 1) GND — hub no CN1.3, espalha
    gnd_hub = "CN1.3"
    mark_pad(gnd_hub, "GND")
    route("GND", gnd_hub, "CN1.4", 2.2)
    route("GND", gnd_hub, "CN1.5", 1.6)
    route("GND", gnd_hub, "CN1.24", 1.2)
    gnds = [
        "CBULK.K", "CIN.K", "TVS.K", "DZ.K", "RG.B",
        "BUCK.GND", "LDO.GND", "C5IN.B", "C33.B", "C33n.B",
        "QINJ1.S", "QINJ2.S", "QINJ3.S", "QINJ4.S", "QHEAT.S",
        "RGS1.B", "RGS2.B", "RGS3.B", "RGS4.B", "RGSH.B",
        "QRL1.S", "QRL2.S", "QRL3.S",
        "MCU.L2", "MCU.R2", "SWD.4",
        "CIAT.B", "CCLT.B", "CMAP.B", "CTPS.B", "RMAP2.B", "CO2.B", "RO2.B",
        "U817.3", "CR.B", "CAN.GND",
        "C5A.B", "CIP.B", "CUN.B", "U6004.4", "U8628.4",
    ]
    for g in gnds:
        route("GND", gnd_hub, g, 1.1)

    # 2) +12V_IN → QREV.D
    route("+12VIN", "CN1.1", "QREV.D", 2.0)
    route("+12VIN", "CN1.2", "QREV.D", 2.0)

    # gate QREV
    route("QG", "QREV.G", "RG.A", 0.7)
    route("QG", "QREV.G", "DZ.A", 0.7)

    # 3) +12V_PROT from QREV.S
    route("+12VP", "QREV.S", "CBULK.A", 2.0)
    route("+12VP", "QREV.S", "CIN.A", 1.0)
    route("+12VP", "QREV.S", "TVS.A", 1.0)
    route("+12VP", "QREV.S", "BUCK.VIN", 1.6)
    for i in range(1, 5):
        route("+12VP", "QREV.S", f"DF{i}.K", 1.2)
        route(f"INJ{i}", f"DF{i}.A", f"QINJ{i}.D", 1.1)
    for i in range(1, 4):
        route("+12VP", "QREV.S", f"DRL{i}.K", 1.0)
        route(f"RL{i}", f"DRL{i}.A", f"QRL{i}.D", 1.0)
    route("+12VP", "QREV.S", "CN2.1", 1.8)  # H+

    # 4) +5V
    route("+5V", "BUCK.VOUT", "LDO.IN", 1.4)
    route("+5V", "BUCK.VOUT", "C5IN.A", 1.0)
    route("+5V", "BUCK.VOUT", "CN1.6", 1.2)
    route("+5V", "BUCK.VOUT", "MCU.R1", 1.1)
    route("+5V", "BUCK.VOUT", "C5A.A", 1.0)
    route("+5V", "BUCK.VOUT", "U6004.14", 1.0)
    route("+5V", "BUCK.VOUT", "U8628.8", 0.8)

    # 5) +3V3
    route("+3V3", "LDO.OUT", "C33.A", 1.0)
    route("+3V3", "LDO.OUT", "C33n.A", 0.8)
    route("+3V3", "LDO.OUT", "MCU.L1", 1.2)
    route("+3V3", "LDO.OUT", "SWD.1", 0.9)
    route("+3V3", "LDO.OUT", "CN1.7", 1.1)
    route("+3V3", "LDO.OUT", "RIAT.A", 0.9)
    route("+3V3", "LDO.OUT", "RCLT.A", 0.9)
    route("+3V3", "LDO.OUT", "RR3.A", 0.9)
    route("+3V3", "LDO.OUT", "CAN.VCC", 1.0)

    # 6) Injector outs CN1 + gates
    for i, cn in enumerate([13, 14, 15, 16], 1):
        route(f"INJ{i}", f"QINJ{i}.D", f"CN1.{cn}", 1.4)
        route(f"GI{i}", f"MCU.L{12+i}", f"RG{i}.B", 0.8)
        route(f"GI{i}", f"RG{i}.A", f"QINJ{i}.G", 0.8)
        route(f"GI{i}", f"RGS{i}.A", f"QINJ{i}.G", 0.7)

    route("GH", "MCU.L20", "RGH.B", 0.8)
    route("GH", "RGH.A", "QHEAT.G", 0.8)
    route("GH", "RGSH.A", "QHEAT.G", 0.7)
    route("H-", "QHEAT.D", "CN2.2", 1.8)

    # Relays
    rl_cn = {1: 18, 2: 17, 3: 19}
    for i in range(1, 4):
        route(f"RL{i}", f"QRL{i}.D", f"CN1.{rl_cn[i]}", 1.1)
        route(f"GR{i}", f"MCU.L{16+i}", f"RRL{i}.B", 0.75)
        route(f"GR{i}", f"RRL{i}.A", f"QRL{i}.G", 0.75)

    # Sensors
    route("IAT", "CN1.8", "RIAT.B", 0.85)
    route("IAT", "RIAT.B", "CIAT.A", 0.7)
    route("IAT", "RIAT.B", "SIAT.A", 0.7)
    route("IAT", "SIAT.B", "MCU.L3", 0.85)

    route("CLT", "CN1.9", "RCLT.B", 0.85)
    route("CLT", "RCLT.B", "CCLT.A", 0.7)
    route("CLT", "RCLT.B", "SCLT.A", 0.7)
    route("CLT", "SCLT.B", "MCU.L4", 0.85)

    route("MAP", "CN1.10", "RMAP1.A", 0.85)
    route("MAP", "RMAP1.B", "RMAP2.A", 0.7)
    route("MAP", "RMAP1.B", "CMAP.A", 0.7)
    route("MAP", "RMAP1.B", "SMAP.A", 0.7)
    route("MAP", "SMAP.B", "MCU.L5", 0.85)

    route("TPS", "CN1.11", "STPS.A", 0.85)
    route("TPS", "STPS.A", "CTPS.A", 0.7)
    route("TPS", "STPS.B", "MCU.L6", 0.85)

    # RPM
    route("RPMi", "CN1.12", "RR2.A", 0.9)
    route("RPMi", "RR2.B", "RR1.A", 0.9)
    route("RPMi", "RR1.B", "U817.1", 0.8)
    route("GND", "U817.2", "CN1.3", 0.8)  # LED K → GND
    route("RPMi", "DR.A", "U817.1", 0.65)
    route("RPMi", "DR.K", "U817.2", 0.65)
    route("RPMo", "U817.4", "RR3.B", 0.75)
    route("RPMo", "U817.4", "CR.A", 0.65)
    route("RPMo", "U817.4", "MCU.L10", 0.85)

    # CAN
    route("CANTX", "MCU.L12", "CAN.TX", 0.75)
    route("CANRX", "MCU.L11", "CAN.RX", 0.75)
    route("CANH", "CAN.H", "CN1.20", 0.95)
    route("CANL", "CAN.L", "CN1.21", 0.95)

    # Lambda
    route("IP", "CN2.3", "RSH.A", 0.95)
    route("IP", "RSH.B", "CIP.A", 0.7)
    route("IP", "RSH.B", "MCU.L8", 0.85)
    route("IP", "U8628.6", "RSH.A", 0.75)
    route("IP", "U8628.2", "RSH.A", 0.7)

    route("VM", "MCU.R3", "U6004.3", 0.75)
    route("VM", "U6004.1", "U6004.2", 0.65)
    route("VM", "U6004.1", "CN2.4", 0.85)
    route("VM", "U8628.3", "CN2.4", 0.7)

    route("UN", "CN2.5", "RESR.A", 0.9)
    route("UN", "RESR.A", "CUN.A", 0.7)
    route("UN", "RESR.A", "MCU.L9", 0.85)
    route("RI", "MCU.R8", "RESR.B", 0.75)

    route("O2", "U6004.7", "RO1.A", 0.75)
    route("O2", "RO1.B", "RO2.A", 0.65)
    route("O2", "RO1.B", "CO2.A", 0.65)
    route("O2", "RO1.B", "MCU.L7", 0.85)

    # SWD
    route("SWDIO", "SWD.2", "MCU.R4", 0.7)
    route("SWCLK", "SWD.3", "MCU.R5", 0.7)


# ===================== VALIDAÇÃO CRUZAMENTOS =====================
def count_copper_crossings():
    """Segmentos de nets diferentes que se cruzam geometricamente."""
    segs = []
    for pts, w, net in traces:
        for i in range(len(pts) - 1):
            segs.append((pts[i], pts[i + 1], net, w))

    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def on_seg(a, b, c, eps=0.05):
        return (min(a[0], b[0]) - eps <= c[0] <= max(a[0], b[0]) + eps and
                min(a[1], b[1]) - eps <= c[1] <= max(a[1], b[1]) + eps)

    def intersects(p1, p2, p3, p4):
        o1, o2 = orient(p1, p2, p3), orient(p1, p2, p4)
        o3, o4 = orient(p3, p4, p1), orient(p3, p4, p2)
        if o1 * o2 < 0 and o3 * o4 < 0:
            return True
        return False

    n = 0
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            (a, b, n1, _), (c, d, n2, _) = segs[i], segs[j]
            if n1 == n2:
                continue
            if intersects(a, b, c, d):
                # ignora se só tocam na ponta (pad comum)
                n += 1
    return n


# ===================== RENDER =====================
NET_COL = {
    "GND": (70, 70, 70), "+12VIN": (160, 30, 30), "+12VP": (220, 40, 40),
    "+5V": (210, 130, 40), "+3V3": (40, 110, 200),
}


def ncol(net):
    if net in NET_COL:
        return NET_COL[net]
    if net.startswith(("INJ", "H-", "RL", "+12")):
        return (200, 90, 40)
    if net.startswith(("G", "CANT", "CANR", "SWD", "RI", "RPM")):
        return (90, 180, 90)
    if net in ("IAT", "CLT", "MAP", "TPS", "O2", "IP", "UN", "VM", "CANH", "CANL"):
        return (60, 200, 200)
    return (220, 190, 70)


def render_assembly():
    img = Image.new("RGB", px(W, H), (14, 18, 22))
    d = ImageDraw.Draw(img)

    def Y(y):
        return H - y

    def P(x, y):
        return px(x, Y(y))

    d.rectangle([*px(0.5, 0.5), *px(W - 0.5, H - 0.5)], fill=(18, 78, 48), outline=(200, 210, 200), width=2)

    for x0, y0, x1, y1, lab, side in outlines:
        col = (255, 170, 70) if side == "bot" else (150, 210, 160)
        d.rectangle([*P(x0, y1), *P(x1, y0)], outline=col, width=2)
        d.text(P(x0 + 0.5, y1 - 0.5), lab, fill=col, font=font(1.9))

    for pts, w, net in traces:
        flat = []
        for x, y in pts:
            flat.extend(P(x, y))
        if len(flat) >= 4:
            d.line(flat, fill=ncol(net), width=max(2, int(w * PPM)))

    # jumpers = fio TOPO (branco tracejado)
    for ja, jb, net in jumpers:
        ax, ay = pads[ja][0], pads[ja][1]
        bx, by = pads[jb][0], pads[jb][1]
        d.line([*P(ax, ay), *P(bx, by)], fill=(255, 255, 255), width=3)
        d.text(P((ax + bx) / 2, (ay + by) / 2 + 2), f"JMP {net}", fill=(255, 255, 255), font=font(1.6))

    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MTG_"):
            continue
        r = od / 2
        fill = (210, 175, 55) if drill > 0 else (190, 110, 230)
        d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], fill=fill, outline=(90, 70, 20))
        if drill > 0:
            rd = drill / 2
            d.ellipse([*P(x - rd, y + rd), *P(x + rd, y - rd)], fill=(14, 18, 22))

    for x, y in [(4, 4), (196, 4), (4, 96), (196, 96)]:
        d.ellipse([*P(x - 1.7, y + 1.7), *P(x + 1.7, y - 1.7)], outline=(230, 230, 230), width=2)

    cross = count_copper_crossings()
    d.rectangle([*px(1, 1), *px(199, 12)], fill=(8, 12, 16))
    d.text(px(3, 2), "INJET RACING · PCB 1-LAYER 200×100 · SEM CRUZAMENTO DE COBRE", fill=(240, 245, 240), font=font(2.4))
    d.text(
        px(3, 6),
        f"Trilhas={len(traces)}  Jumpers fio TOPO={len(jumpers)}  Cruzamentos cobre={cross}  Falhas={len(route_fails)}",
        fill=(180, 220, 180) if cross == 0 else (255, 120, 120),
        font=font(2.0),
    )
    d.text(px(3, 9), "Branco tracejado = JUMPER (fio no lado dos componentes, NÃO é cobre)", fill=(200, 200, 200), font=font(1.7))
    return img, cross


def render_cnc(invert=False):
    bg, cu = (255, 0) if not invert else (0, 255)
    img = Image.new("L", px(W, H), bg)
    d = ImageDraw.Draw(img)

    def Y(y):
        return H - y

    def P(x, y):
        return px(x, Y(y))

    for pts, w, net in traces:
        flat = []
        for x, y in pts:
            flat.extend(P(x, y))
        if len(flat) >= 4:
            d.line(flat, fill=cu, width=max(2, int(w * PPM)))
    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MTG_"):
            d.ellipse([*P(x - 1.7, y + 1.7), *P(x + 1.7, y - 1.7)], fill=bg)
            continue
        r = od / 2
        d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], fill=cu)
        if drill > 0:
            rd = max(0.25, drill / 2 - 0.05)
            d.ellipse([*P(x - rd, y + rd), *P(x + rd, y - rd)], fill=bg)
    return img


def write_svg(path, invert=False):
    cu = "#000" if not invert else "#FFF"
    bg = "#FFF" if not invert else "#000"

    def Y(y):
        return H - y

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{bg}"/>',
        '<!-- 1-layer DRC: copper paths must not cross different nets; jumpers are NOT in this file -->',
        f'<g id="copper" fill="{cu}" stroke="{cu}" stroke-linecap="round" stroke-linejoin="round">',
    ]
    for pts, w, net in traces:
        dpath = "M " + " L ".join(f"{x:.3f},{Y(y):.3f}" for x, y in pts)
        lines.append(f'  <path d="{dpath}" fill="none" stroke-width="{w:.3f}" data-net="{net}"/>')
    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MTG_"):
            continue
        lines.append(f'  <circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{od/2:.3f}" data-pad="{name}"/>')
    lines.append("</g>")
    lines.append(f'<g id="holes" fill="{bg}">')
    for name, (x, y, od, drill) in pads.items():
        if drill > 0 and not name.startswith("MTG_"):
            lines.append(f'  <circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{drill/2:.3f}"/>')
    for x, y in [(4, 4), (196, 4), (4, 96), (196, 96)]:
        lines.append(f'  <circle cx="{x}" cy="{Y(y)}" r="1.7"/>')
    lines.append("</g>")
    # jumpers as dashed (documentação — não fresar como cobre)
    lines.append('<g id="jumpers-TOP-WIRE" fill="none" stroke="#888" stroke-width="0.4" stroke-dasharray="1 0.6">')
    for ja, jb, net in jumpers:
        ax, ay = pads[ja][0], pads[ja][1]
        bx, by = pads[jb][0], pads[jb][1]
        lines.append(f'  <line x1="{ax:.3f}" y1="{Y(ay):.3f}" x2="{bx:.3f}" y2="{Y(by):.3f}" data-net="{net}"/>')
    lines.append("</g>")
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path, cross):
    lines = [
        "# PCB 1-layer — relatório DRC",
        "",
        f"- Cruzamentos de cobre (nets diferentes): **{cross}**",
        f"- Jumpers (fio no TOPO): **{len(jumpers)}**",
        f"- Falhas de rota: **{len(route_fails)}**",
        f"- Trilhas: **{len(traces)}**",
        f"- Pads: **{len(pads)}**",
        "",
        "## Jumpers (soldar fio fino no lado dos componentes)",
        "",
    ]
    if not jumpers:
        lines.append("_Nenhum jumper necessário — 100% cobre 1-layer._")
    else:
        lines.append("| # | Pad A | Pad B | Net |")
        lines.append("|---:|---|---|---|")
        for i, (a, b, n) in enumerate(jumpers, 1):
            lines.append(f"| {i} | `{a}` | `{b}` | `{n}` |")
    if route_fails:
        lines += ["", "## Falhas", ""] + [f"- {f}" for f in route_fails]
    lines += [
        "",
        "## Regra 1-layer",
        "",
        "No cobre **não pode** haver trilha de um net atravessando outro.",
        "Quando o A* não acha caminho, o gerador cria um **jumper** (2 pads + fio no topo).",
        "O arquivo CNC (`*-traces-cnc.*`) contém **só cobre** — jumpers aparecem tracejados só no SVG de documentação.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    print("Routing…")
    run_routes()
    img, cross = render_assembly()
    img.save(OUT / "ecu-pcb-1layer-assembly.png", dpi=(DPI, DPI))
    render_cnc(False).save(OUT / "ecu-pcb-1layer-traces-cnc.png", dpi=(DPI, DPI))
    render_cnc(True).save(OUT / "ecu-pcb-1layer-traces-cnc-invert.png", dpi=(DPI, DPI))
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc.svg", False)
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc-invert.svg", True)
    write_report(OUT / "ecu-pcb-1layer-drc.md", cross)
    print(f"crossings={cross} jumpers={len(jumpers)} fails={len(route_fails)} traces={len(traces)}")
    if route_fails:
        print("FAILS:", route_fails[:20])


if __name__ == "__main__":
    main()
