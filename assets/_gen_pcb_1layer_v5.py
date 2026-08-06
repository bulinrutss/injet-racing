# -*- coding: utf-8 -*-
"""
INJET RACING ECU — 1-layer, mínimo de fios, silk com códigos, mapa de furos.
Placa 220×140 mm (folga para roteamento planar). Sem tarja na imagem.
"""
from __future__ import annotations

from collections import deque
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"e:\injet racing\assets")
DOC = Path(r"e:\injet racing\modulo")
W, H = 220.0, 140.0
PPM = 10.0
DPI = int(25.4 * PPM)
GRID = 0.5
CLR = 1

pads: dict[str, tuple[float, float, float, float]] = {}
silk: list[tuple[float, float, str, float]] = []  # x,y,text,size
boxes: list[tuple] = []
traces: list[tuple] = []
jumpers: list[tuple] = []  # last resort only
bom: list[tuple[str, str, str]] = []  # code, value, desc

gw, gh = int(W / GRID) + 1, int(H / GRID) + 1
occ = [[None] * gw for _ in range(gh)]


def font(mm):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", max(8, int(mm * PPM)))
    except OSError:
        return ImageFont.load_default()


def px(*a):
    return tuple(int(round(v * PPM)) for v in a)


def add_bom(code, value, desc):
    bom.append((code, value, desc))


def pad(n, x, y, od=1.8, drill=0.9):
    pads[n] = (x, y, od, drill)


def label(x, y, t, s=1.8):
    silk.append((x, y, t, s))


def box(x0, y0, x1, y1, t):
    boxes.append((x0, y0, x1, y1, t))


def axial(n1, n2, x1, y1, x2, y2, od=1.6, dr=0.85):
    pad(n1, x1, y1, od, dr)
    pad(n2, x2, y2, od, dr)


def to220(code, x, y):
    pad(f"{code}.G", x - 2.54, y, 2.2, 1.05)
    pad(f"{code}.D", x, y, 2.2, 1.05)
    pad(f"{code}.S", x + 2.54, y, 2.2, 1.05)
    label(x, y + 8, code, 2.0)
    box(x - 5, y - 1, x + 5, y + 11, code)


def to92(code, x, y):
    pad(f"{code}.S", x - 1.27, y, 1.5, 0.8)
    pad(f"{code}.G", x, y + 1.8, 1.5, 0.8)
    pad(f"{code}.D", x + 1.27, y, 1.5, 0.8)
    label(x, y + 5, code, 1.7)


def dip(code, x0, y0, n, pitch=2.54, row=7.62):
    h = n // 2
    for i in range(h):
        pad(f"{code}.{i+1}", x0, y0 + i * pitch, 1.6, 0.85)
        pad(f"{code}.{n-i}", x0 + row, y0 + i * pitch, 1.6, 0.85)
    label(x0 + row / 2, y0 + (h - 1) * pitch + 3, code, 2.0)
    box(x0 - 1, y0 - 1, x0 + row + 1, y0 + (h - 1) * pitch + 1, code)


def soic8(code, x0, y0):
    for i in range(4):
        pad(f"{code}.{i+1}", x0, y0 + i * 1.27, 1.25, 0.0)
        pad(f"{code}.{8-i}", x0 + 5.4, y0 + i * 1.27, 1.25, 0.0)
    label(x0 + 2.7, y0 - 2, code + " SMD", 1.6)
    box(x0 - 1, y0 - 1, x0 + 6.4, y0 + 4.8, code)


def cell(x, y):
    return int(round(x / GRID)), int(round(y / GRID))


def xy(cx, cy):
    return cx * GRID, cy * GRID


def mark(x, y, r, net):
    cr = max(1, int(round(r / GRID)))
    cx, cy = cell(x, y)
    for dy in range(-cr, cr + 1):
        for dx in range(-cr, cr + 1):
            if dx * dx + dy * dy <= cr * cr + 1:
                xx, yy = cx + dx, cy + dy
                if 0 <= xx < gw and 0 <= yy < gh:
                    if occ[yy][xx] in (None, net):
                        occ[yy][xx] = net


def can(cx, cy, net, half):
    for dy in range(-half - CLR, half + CLR + 1):
        for dx in range(-half - CLR, half + CLR + 1):
            xx, yy = cx + dx, cy + dy
            if not (0 <= xx < gw and 0 <= yy < gh):
                return False
            o = occ[yy][xx]
            if o is not None and o != net:
                return False
    return True


def paint(cells, net, half):
    for cx, cy in cells:
        for dy in range(-half, half + 1):
            for dx in range(-half, half + 1):
                xx, yy = cx + dx, cy + dy
                if 0 <= xx < gw and 0 <= yy < gh and occ[yy][xx] in (None, net):
                    occ[yy][xx] = net


def simplify(cells):
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


def astar(a, b, net, w):
    sx, sy = cell(*a)
    gx, gy = cell(*b)
    half = max(0, int(round((w / 2) / GRID)))
    q = deque([(sx, sy)])
    came = {(sx, sy): None}
    while q:
        cx, cy = q.popleft()
        if (cx, cy) == (gx, gy):
            path = []
            cur = (gx, gy)
            while cur:
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
            if (nx, ny) == (gx, gy) or can(nx, ny, net, half):
                came[(nx, ny)] = (cx, cy)
                q.append((nx, ny))
    return None


def route(net, pa, pb, w=0.85):
    if pa not in pads or pb not in pads:
        return False
    ax, ay = pads[pa][0], pads[pa][1]
    bx, by = pads[pb][0], pads[pb][1]
    mark(ax, ay, pads[pa][2] / 2, net)
    mark(bx, by, pads[pb][2] / 2, net)
    path = astar((ax, ay), (bx, by), net, w)
    if path is None:
        jumpers.append((ax, ay, bx, by, net))
        return False
    half = max(0, int(round((w / 2) / GRID)))
    paint(path, net, half)
    traces.append(([xy(*c) for c in simplify(path)], w, net))
    return True


def bus_h(net, y, w, x1=3, x2=W - 3):
    # paint horizontal bus directly
    half = max(0, int(round((w / 2) / GRID)))
    y0 = int(round(y / GRID))
    x0 = int(round(x1 / GRID))
    x1c = int(round(x2 / GRID))
    cells = [(x, y0) for x in range(x0, x1c + 1)]
    paint(cells, net, half)
    traces.append(([(x1, y), (x2, y)], w, net))


def stub(net, p, by, w=1.0):
    if p not in pads:
        return
    x, y = pads[p][0], pads[p][1]
    route(net, p, p)  # noop safeguard
    # route via temporary: mark endpoint on bus
    mark(x, by, w / 2, net)
    path = astar((x, y), (x, by), net, w)
    if path:
        half = max(0, int(round((w / 2) / GRID)))
        paint(path, net, half)
        traces.append(([xy(*c) for c in simplify(path)], w, net))


# ========== PLACE (fluxo L→R, sinais sem cruzar) ==========
# Y: 0 bottom, H top. Layout maior 220x140.

# CN1 ATX-24 bottom-left
ATX = 4.2
for i in range(12):
    pad(f"J1.{i+1}", 8 + i * ATX, 14, 2.2, 1.1)
    pad(f"J1.{i+13}", 8 + i * ATX, 8, 2.2, 1.1)
label(30, 4, "J1 ATX-24", 2.2)
box(5, 5, 60, 18, "J1")
add_bom("J1", "ATX-24 header", "Conector principal chicote")

# CN2 PCIe-6 bottom-right near lambda
for i in range(3):
    pad(f"J2.{i+1}", 185 + i * ATX, 14, 2.2, 1.1)
    pad(f"J2.{i+4}", 185 + i * ATX, 8, 2.2, 1.1)
label(192, 4, "J2 PCIe-6", 2.0)
box(182, 5, 205, 18, "J2")
add_bom("J2", "PCIe-6 header", "Conector lambda LSU 4.2")

# POWER top-left
to220("Q6", 16, 128)
add_bom("Q6", "IRF9540", "MOSFET-P proteção reversa")
axial("C1.A", "C1.B", 28, 130, 36, 130, 2.4, 0.9)
label(32, 134, "C1", 1.6)
add_bom("C1", "220u/50V", "Bulk entrada")
axial("C2.A", "C2.B", 28, 124, 32, 124)
label(30, 120, "C2", 1.5)
add_bom("C2", "100n/100V", "Cerâmico entrada")
axial("D1.A", "D1.K", 40, 130, 40, 124)
label(43, 127, "D1", 1.5)
add_bom("D1", "P6KE33A/SMBJ33A", "TVS load dump")
axial("R1.A", "R1.B", 10, 120, 10, 114)
label(7, 117, "R1", 1.5)
add_bom("R1", "100k", "Gate Q6")
axial("D2.A", "D2.K", 14, 120, 14, 114)
label(17, 117, "D2", 1.5)
add_bom("D2", "Zener 12V", "Proteção gate Q6")
pad("U6.VIN", 48, 130)
pad("U6.GND", 54, 130)
pad("U6.OUT", 48, 122)
label(51, 134, "U6 BUCK", 1.7)
box(46, 120, 56, 134, "U6")
add_bom("U6", "MP1584 módulo", "Buck 5V")
pad("U7.IN", 62, 130)
pad("U7.GND", 68, 130)
pad("U7.OUT", 65, 122)
label(65, 134, "U7 LDO", 1.7)
box(60, 120, 72, 134, "U7")
add_bom("U7", "AMS1117-3.3", "LDO 3V3")
axial("C3.A", "C3.B", 74, 130, 78, 130)
label(76, 134, "C3", 1.5)
add_bom("C3", "10u", "LDO in")
axial("C4.A", "C4.B", 74, 124, 78, 124)
label(76, 120, "C4", 1.5)
add_bom("C4", "10u+100n", "LDO out")
box(6, 110, 80, 136, "POWER")

# Injectors top center
for i, x in enumerate([92, 108, 124, 140]):
    code = f"Q{i+1}"
    to220(code, x, 128)
    add_bom(code, "IRLZ44N", f"Driver bico INJ{i+1}")
    axial(f"R{10+i}.A", f"R{10+i}.B", x - 2.54, 118, x - 2.54, 112)
    label(x - 5, 115, f"R{10+i}", 1.4)
    add_bom(f"R{10+i}", "100R", f"Gate INJ{i+1}")
    axial(f"R{20+i}.A", f"R{20+i}.B", x - 2.54, 110, x, 110)
    label(x + 3, 110, f"R{20+i}", 1.4)
    add_bom(f"R{20+i}", "10k", f"Pull-down INJ{i+1}")
    axial(f"D{10+i}.A", f"D{10+i}.K", x + 5, 128, x + 5, 122)
    label(x + 7, 125, f"D{10+i}", 1.4)
    add_bom(f"D{10+i}", "1N4007", f"Flyback INJ{i+1}")

to220("Q5", 160, 128)
add_bom("Q5", "IRLZ44N", "Aquecedor lambda")
axial("R15.A", "R15.B", 157.46, 118, 157.46, 112)
label(152, 115, "R15", 1.4)
add_bom("R15", "100R", "Gate Q5")
axial("R25.A", "R25.B", 157.46, 110, 160, 110)
label(163, 110, "R25", 1.4)
add_bom("R25", "10k", "Pull-down Q5")
box(86, 108, 172, 136, "DRIVERS")

# Relay drivers left mid
for i, x in enumerate([12, 24, 36]):
    code = f"Q{7+i}"
    to92(code, x, 90)
    add_bom(code, "2N7000", f"Driver relé RL{i+1}")
    axial(f"R{30+i}.A", f"R{30+i}.B", x, 84, x, 78)
    label(x - 4, 81, f"R{30+i}", 1.4)
    add_bom(f"R{30+i}", "1k", f"Gate relé {i+1}")
    axial(f"D{20+i}.A", f"D{20+i}.K", x + 4, 90, x + 4, 84)
    label(x + 6, 87, f"D{20+i}", 1.4)
    add_bom(f"D{20+i}", "1N4007", f"Flyback relé {i+1}")
box(6, 74, 44, 100, "RELAY")

# MCU center — headers
for i in range(20):
    pad(f"U1.L{i+1}", 78, 96 - i * 2.54, 1.55, 0.9)
    pad(f"U1.R{i+1}", 130, 96 - i * 2.54, 1.55, 0.9)
label(104, 50, "U1 STM32F407", 2.2)
box(76, 44, 132, 100, "U1")
add_bom("U1", "STM32F407 Black Board", "MCU")
for i in range(4):
    pad(f"J3.{i+1}", 96 + i * 2.54, 40, 1.7, 0.95)
label(100, 36, "J3 SWD", 1.6)
add_bom("J3", "header 1x4", "SWD debug")

# Sensors right column (acima da lambda) — ordem IAT→CLT→MAP→TPS de cima
sy = [100, 90, 80, 70]
for i, (n, y) in enumerate(zip(["IAT", "CLT", "MAP", "TPS"], sy)):
    if n != "TPS":
        axial(f"R{40+i}.A", f"R{40+i}.B", 150, y, 158, y)
        label(154, y + 3, f"R{40+i}", 1.4)
        add_bom(f"R{40+i}", "2K26" if n != "MAP" else "10k 1%", f"{n} pullup/div")
    if n == "MAP":
        axial("R43.A", "R43.B", 158, y, 158, y - 4)
        label(161, y - 2, "R43", 1.4)
        add_bom("R43", "18k 1%", "MAP divisor GND")
    axial(f"C{10+i}.A", f"C{10+i}.B", 162, y, 162, y - 3.5)
    label(165, y - 1, f"C{10+i}", 1.4)
    add_bom(f"C{10+i}", "100n", f"Filtro {n}")
    axial(f"R{50+i}.A", f"R{50+i}.B", 166, y, 174, y)
    label(170, y + 3, f"R{50+i}", 1.4)
    add_bom(f"R{50+i}", "1k", f"Série ADC {n}")
box(148, 64, 178, 106, "SENS")

# RPM left of MCU bottom
dip("U4", 50, 48, 4)
add_bom("U4", "PC817", "Opto RPM")
axial("R60.A", "R60.B", 40, 54, 48, 54)
label(44, 57, "R60", 1.4)
add_bom("R60", "10k 2W", "RPM série 1")
axial("R61.A", "R61.B", 32, 54, 40, 54)
label(36, 57, "R61", 1.4)
add_bom("R61", "10k 2W", "RPM série 2")
axial("D30.A", "D30.K", 44, 48, 44, 42)
label(47, 45, "D30", 1.4)
add_bom("D30", "1N4148", "Proteção LED opto")
axial("R62.A", "R62.B", 60, 58, 60, 52)
label(63, 55, "R62", 1.4)
add_bom("R62", "4k7", "Pull-up RPM")
axial("C20.A", "C20.B", 64, 52, 64, 46)
label(67, 49, "C20", 1.4)
add_bom("C20", "1nF", "Filtro RPM")
box(30, 40, 70, 64, "RPM")

# CAN
pad("U5.VCC", 96, 58)
pad("U5.GND", 102, 58)
pad("U5.TX", 96, 52)
pad("U5.RX", 102, 52)
pad("U5.H", 108, 58)
pad("U5.L", 114, 58)
label(105, 62, "U5 CAN", 1.7)
box(94, 50, 118, 64, "U5")
add_bom("U5", "SN65HVD230 módulo", "CAN transceiver")

# Lambda bottom-right above J2
dip("U2", 150, 28, 14)
add_bom("U2", "MCP6004 DIP14", "Op-amp quádruplo wideband")
soic8("U3", 175, 30)
add_bom("U3", "AD8628 SOIC", "Chopper Ip (SMD embaixo)")
axial("R70.A", "R70.B", 168, 46, 176, 46)
label(172, 49, "R70", 1.4)
add_bom("R70", "61R9 1%", "Shunt Ip")
axial("R71.A", "R71.B", 168, 52, 176, 52)
label(172, 55, "R71", 1.4)
add_bom("R71", "6k8 1%", "R_ESR LSU 4.2")
axial("C30.A", "C30.B", 180, 46, 180, 40)
label(183, 43, "C30", 1.4)
add_bom("C30", "220n", "Filtro Ip")
axial("C31.A", "C31.B", 184, 52, 184, 46)
label(187, 49, "C31", 1.4)
add_bom("C31", "220n", "Filtro Un")
axial("C32.A", "C32.B", 144, 36, 144, 30)
label(141, 33, "C32", 1.4)
add_bom("C32", "100n+10u", "Decoupling +5V opamps")
axial("R72.A", "R72.B", 158, 38, 166, 38)
label(162, 41, "R72", 1.4)
add_bom("R72", "10k 1%", "Divisor O2")
axial("R73.A", "R73.B", 166, 38, 166, 32)
label(169, 35, "R73", 1.4)
add_bom("R73", "18k 1%", "Divisor O2 GND")
box(142, 24, 198, 58, "LAMBDA")

# Mount holes
for x, y in [(4, 4), (216, 4), (4, 136), (216, 136)]:
    pad(f"MH_{x}_{y}", x, y, 3.6, 3.2)
    mark(x, y, 2.0, "__HOLE__")


def route_all():
    YG, Y12, Y5, Y33 = 2.5, 137.0, 106.0, 102.0
    # buses on edges — leave channel gaps
    bus_h("GND", YG, 2.2, 3, 210)
    bus_h("+12V", Y12, 2.0, 3, 210)
    # +5/+3V3 as shorter horizontal under drivers area only (avoid crossing injectors verticals)
    # Use right-side vertical buses instead
    # paint vertical bus
    half5 = max(0, int(round(0.7 / GRID)))
    x5 = int(round(210 / GRID))
    cells5 = [(x5, y) for y in range(int(20 / GRID), int(130 / GRID))]
    paint(cells5, "+5V", half5)
    traces.append(([(210, 20), (210, 130)], 1.3, "+5V"))
    x33 = int(round(206 / GRID))
    cells33 = [(x33, y) for y in range(int(20 / GRID), int(130 / GRID))]
    paint(cells33, "+3V3", half5)
    traces.append(([(206, 20), (206, 130)], 1.2, "+3V3"))

    # Power locals + stubs via route
    route("QG", "Q6.G", "R1.A", 0.7)
    route("QG", "Q6.G", "D2.A", 0.7)
    route("GND", "R1.B", "D2.K", 0.7)
    route("+12V", "Q6.S", "C1.A", 1.4)
    route("GND", "C1.B", "C2.B", 1.0)
    route("+12V", "C2.A", "D1.A", 1.0)
    route("GND", "D1.K", "C1.B", 1.0)
    route("+12V", "U6.VIN", "Q6.S", 1.3)
    route("GND", "U6.GND", "U7.GND", 1.0)
    route("+5V", "U6.OUT", "U7.IN", 1.1)
    route("+5V", "U7.IN", "C3.A", 0.9)
    route("GND", "C3.B", "C4.B", 0.9)
    route("+3V3", "U7.OUT", "C4.A", 1.0)

    # Connect buses taps
    for p in ["J1.3", "J1.4", "J1.5", "J1.24", "C1.B", "U6.GND", "Q1.S", "Q5.S", "Q7.S",
              "U1.L2", "U1.R2", "J3.4", "U4.3", "U5.GND", "U2.4", "C13.B"]:
        if p not in pads:
            continue
        x, y = pads[p][0], pads[p][1]
        mark(x, YG, 1.0, "GND")
        path = astar((x, y), (x, YG), "GND", 1.0)
        if path:
            paint(path, "GND", 1)
            traces.append(([xy(*c) for c in simplify(path)], 1.0, "GND"))
        else:
            jumpers.append((x, y, x, YG, "GND"))

    for p in ["Q6.S", "U6.VIN", "D10.K", "D11.K", "D12.K", "D13.K", "D20.K", "D21.K", "D22.K", "J2.1"]:
        if p in pads:
            x, y = pads[p][0], pads[p][1]
            mark(x, Y12, 1.0, "+12V")
            path = astar((x, y), (x, Y12), "+12V", 1.2)
            if path:
                paint(path, "+12V", 1)
                traces.append(([xy(*c) for c in simplify(path)], 1.2, "+12V"))

    for p in ["U6.OUT", "J1.6", "U1.R1", "C32.A", "U2.14"]:
        if p in pads:
            route("+5V", p, "U6.OUT", 1.0)

    for p in ["U7.OUT", "J1.7", "U1.L1", "J3.1", "R40.A", "U5.VCC", "R62.A"]:
        if p in pads:
            route("+3V3", p, "U7.OUT", 0.95)

    # Injector local
    for i in range(1, 5):
        route(f"INJ{i}", f"D{9+i}.A", f"Q{i}.D", 1.0)
        route(f"GI{i}", f"R{9+i}.A", f"Q{i}.G", 0.75)
        route(f"GI{i}", f"R{19+i}.A", f"Q{i}.G", 0.7)
        route("GND", f"R{19+i}.B", f"Q{i}.S", 0.8)
        route(f"INJ{i}", f"Q{i}.D", f"J1.{12+i}", 1.2)
        route(f"GI{i}", f"U1.L{12+i}", f"R{9+i}.B", 0.8)

    route("GH", "R15.A", "Q5.G", 0.75)
    route("GH", "R25.A", "Q5.G", 0.7)
    route("GND", "R25.B", "Q5.S", 0.8)
    route("GH", "U1.L20", "R15.B", 0.8)
    route("H-", "Q5.D", "J2.2", 1.5)

    for i, cn in enumerate([18, 17, 19], 1):
        route(f"RL{i}", f"D{19+i}.A", f"Q{6+i}.D", 0.9)
        route(f"GR{i}", f"R{29+i}.A", f"Q{6+i}.G", 0.7)
        route(f"RL{i}", f"Q{6+i}.D", f"J1.{cn}", 1.0)
        route(f"GR{i}", f"U1.L{16+i}", f"R{29+i}.B", 0.75)

    # Sensors
    route("IAT", "J1.8", "R40.B", 0.85)
    route("IAT", "R40.B", "C10.A", 0.7)
    route("IAT", "R40.B", "R50.A", 0.7)
    route("IAT", "R50.B", "U1.L3", 0.85)
    route("CLT", "J1.9", "R41.B", 0.85)
    route("CLT", "R41.B", "C11.A", 0.7)
    route("CLT", "R41.B", "R51.A", 0.7)
    route("CLT", "R51.B", "U1.L4", 0.85)
    route("MAP", "J1.10", "R42.A", 0.85)
    route("MAP", "R42.B", "R43.A", 0.7)
    route("MAP", "R42.B", "C12.A", 0.7)
    route("MAP", "R42.B", "R52.A", 0.7)
    route("MAP", "R52.B", "U1.L5", 0.85)
    route("TPS", "J1.11", "R53.A", 0.85)
    route("TPS", "R53.A", "C13.A", 0.7)
    route("TPS", "R53.B", "U1.L6", 0.85)

    # RPM
    route("RPMi", "J1.12", "R61.A", 0.9)
    route("RPMi", "R61.B", "R60.A", 0.85)
    route("RPMi", "R60.B", "U4.1", 0.8)
    route("GND", "U4.2", "U4.3", 0.75)
    route("RPMi", "D30.A", "U4.1", 0.65)
    route("RPMi", "D30.K", "U4.2", 0.65)
    route("RPMo", "U4.4", "R62.B", 0.75)
    route("RPMo", "U4.4", "C20.A", 0.65)
    route("RPMo", "U4.4", "U1.L10", 0.85)

    # CAN
    route("CANTX", "U1.L12", "U5.TX", 0.75)
    route("CANRX", "U1.L11", "U5.RX", 0.75)
    route("CANH", "U5.H", "J1.20", 0.95)
    route("CANL", "U5.L", "J1.21", 0.95)

    # Lambda
    route("IP", "J2.3", "R70.A", 0.9)
    route("IP", "R70.B", "C30.A", 0.7)
    route("IP", "R70.B", "U1.L8", 0.85)
    route("IP", "U3.6", "R70.A", 0.75)
    route("IP", "U3.2", "R70.A", 0.7)
    route("VM", "U1.R3", "U2.3", 0.75)
    route("VM", "U2.1", "U2.2", 0.65)
    route("VM", "U2.1", "J2.4", 0.85)
    route("VM", "U3.3", "J2.4", 0.7)
    route("UN", "J2.5", "R71.A", 0.85)
    route("UN", "R71.A", "C31.A", 0.7)
    route("UN", "R71.A", "U1.L9", 0.85)
    route("RI", "U1.R8", "R71.B", 0.75)
    route("O2", "U2.7", "R72.A", 0.75)
    route("O2", "R72.B", "R73.A", 0.65)
    route("O2", "R72.B", "U1.L7", 0.85)

    route("+12VIN", "J1.1", "Q6.D", 1.6)
    route("+12VIN", "J1.2", "Q6.D", 1.4)
    route("SWDIO", "J3.2", "U1.R4", 0.7)
    route("SWCLK", "J3.3", "U1.R5", 0.7)


def count_cross():
    S = []
    for pts, w, net in traces:
        for i in range(len(pts) - 1):
            S.append((pts[i], pts[i + 1], net))

    def ori(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def hit(a, b, c, d):
        return ori(a, b, c) * ori(a, b, d) < -1e-9 and ori(c, d, a) * ori(c, d, b) < -1e-9

    n = 0
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            (a, b, n1), (c, d, n2) = S[i], S[j]
            if n1 != n2 and hit(a, b, c, d):
                n += 1
    return n


def draw_base(d, show_traces=True, show_jumpers=True, show_silk=True, show_boxes=True):
    def Y(y):
        return H - y

    def P(x, y):
        return px(x, Y(y))

    d.rectangle([*px(0.3, 0.3), *px(W - 0.3, H - 0.3)], fill=(18, 78, 48), outline=(200, 210, 200), width=2)
    if show_boxes:
        for x0, y0, x1, y1, t in boxes:
            d.rectangle([*P(x0, y1), *P(x1, y0)], outline=(140, 190, 150), width=1)
    if show_traces:
        for pts, w, net in traces:
            flat = []
            for x, y in pts:
                flat.extend(P(x, y))
            if len(flat) >= 4:
                col = {"GND": (40, 40, 40), "+12V": (220, 45, 45), "+12VIN": (180, 30, 30),
                       "+5V": (210, 140, 40), "+3V3": (50, 130, 210)}.get(net, (210, 185, 55))
                d.line(flat, fill=col, width=max(2, int(w * PPM * 0.9)))
    if show_jumpers:
        for x1, y1, x2, y2, net in jumpers:
            d.line([*P(x1, y1), *P(x2, y2)], fill=(255, 255, 255), width=2)
    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MH_"):
            d.ellipse([*P(x - 1.8, y + 1.8), *P(x + 1.8, y - 1.8)], outline=(230, 230, 230), width=2)
            continue
        r = od / 2
        fill = (215, 180, 55) if drill > 0 else (200, 120, 230)
        d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], fill=fill, outline=(90, 70, 20))
        if drill > 0:
            d.ellipse([*P(x - drill / 2, y + drill / 2), *P(x + drill / 2, y - drill / 2)], fill=(12, 16, 20))
    if show_silk:
        for x, y, t, s in silk:
            d.text(P(x, y), t, fill=(245, 250, 245), font=font(s))
    # BOM strip on board edge (right margin text small) — printed on PCB silk area bottom
    bom_y = 22
    d.text(P(8, bom_y), "INJET RACING ECU 1L", fill=(230, 240, 230), font=font(2.4))


def render_assembly():
    img = Image.new("RGB", px(W, H), (14, 18, 22))
    d = ImageDraw.Draw(img)
    draw_base(d, True, True, True, True)
    return img


def render_pads_map():
    """Só furos/pads + códigos — mapa de montagem."""
    img = Image.new("RGB", px(W, H), (245, 245, 240))
    d = ImageDraw.Draw(img)

    def Y(y):
        return H - y

    def P(x, y):
        return px(x, Y(y))

    d.rectangle([*px(0.3, 0.3), *px(W - 0.3, H - 0.3)], outline=(30, 30, 30), width=2)
    for x0, y0, x1, y1, t in boxes:
        d.rectangle([*P(x0, y1), *P(x1, y0)], outline=(160, 160, 160), width=1)
    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MH_"):
            d.ellipse([*P(x - 1.8, y + 1.8), *P(x + 1.8, y - 1.8)], outline=(0, 0, 0), width=2)
            continue
        r = od / 2
        if drill > 0:
            d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], outline=(0, 0, 0), width=2)
            d.ellipse([*P(x - drill / 2, y + drill / 2), *P(x + drill / 2, y - drill / 2)], fill=(255, 255, 255), outline=(0, 0, 0))
        else:
            # SMD pad
            d.rectangle([*P(x - r, y + r * 0.6), *P(x + r, y - r * 0.6)], fill=(80, 80, 80), outline=(0, 0, 0))
    for x, y, t, s in silk:
        d.text(P(x, y), t, fill=(0, 0, 0), font=font(s))
    d.text(P(8, 22), "MAPA DE MONTAGEM — furos THT + pads SMD", fill=(0, 0, 0), font=font(2.4))
    return img


def render_cnc(inv=False):
    bg, cu = (255, 0) if not inv else (0, 255)
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
    # jumpers NOT in CNC
    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MH_"):
            d.ellipse([*P(x - 1.8, y + 1.8), *P(x + 1.8, y - 1.8)], fill=bg)
            continue
        r = od / 2
        d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], fill=cu)
        if drill > 0:
            d.ellipse([*P(x - drill / 2, y + drill / 2), *P(x + drill / 2, y - drill / 2)], fill=bg)
    return img


def write_svg(path, inv=False):
    cu, bg = ("#000", "#FFF") if not inv else ("#FFF", "#000")

    def Y(y):
        return H - y

    L = ['<?xml version="1.0"?>',
         f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{bg}"/>',
         f'<g fill="{cu}" stroke="{cu}" stroke-linecap="round" stroke-linejoin="round">']
    for pts, w, net in traces:
        dd = "M " + " L ".join(f"{x:.3f},{Y(y):.3f}" for x, y in pts)
        L.append(f'<path d="{dd}" fill="none" stroke-width="{w:.3f}"/>')
    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MH_"):
            continue
        L.append(f'<circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{od/2:.3f}"/>')
    L.append("</g>")
    L.append(f'<g fill="{bg}">')
    for name, (x, y, od, drill) in pads.items():
        if drill > 0:
            L.append(f'<circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{drill/2:.3f}"/>')
    for x, y in [(4, 4), (216, 4), (4, 136), (216, 136)]:
        L.append(f'<circle cx="{x}" cy="{Y(y)}" r="1.6"/>')
    L.append("</g></svg>")
    path.write_text("\n".join(L), encoding="utf-8")


def write_bom_md():
    lines = [
        "# BOM com códigos — PCB INJET RACING (1-layer)",
        "",
        f"> Placa **{W:.0f}×{H:.0f} mm**. Códigos iguais ao silk da placa / mapa de furos.",
        "",
        f"- Cruzamentos cobre: ver DRC ao gerar",
        f"- Jumpers (fio topo, último recurso): ver geração",
        "",
        "| Código | Valor / P/N | Função |",
        "|---|---|---|",
    ]
    for code, val, desc in bom:
        lines.append(f"| **{code}** | `{val}` | {desc} |")
    lines += [
        "",
        "## Conectores — pinagem rápida",
        "",
        "### J1 ATX-24",
        "1:+12 IGN · 2:+12 BAT · 3/4:GND_P · 5:GND_S · 6:+5 · 7:+3V3 · 8:IAT · 9:CLT · 10:MAP · 11:TPS · 12:RPM",
        "13–16:INJ1–4 · 17:RL bomba · 18:RL main · 19:RL IAC · 20:CANH · 21:CANL · 22:tacho · 23:start · 24:shield",
        "",
        "### J2 PCIe-6 (lambda)",
        "1:H+ · 2:H− · 3:IP · 4:VM · 5:UN · 6:NC",
        "",
        "### J3 SWD",
        "1:+3V3 · 2:SWDIO · 3:SWCLK · 4:GND",
        "",
    ]
    (DOC / "pcb-bom-codigos.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    print("Routing…")
    route_all()
    cross = count_cross()
    print(f"cross={cross} traces={len(traces)} jumpers={len(jumpers)} bom={len(bom)}")

    render_assembly().save(OUT / "ecu-pcb-1layer-assembly.png", dpi=(DPI, DPI))
    render_pads_map().save(OUT / "ecu-pcb-1layer-pads-map.png", dpi=(DPI, DPI))
    render_cnc(False).save(OUT / "ecu-pcb-1layer-traces-cnc.png", dpi=(DPI, DPI))
    render_cnc(True).save(OUT / "ecu-pcb-1layer-traces-cnc-invert.png", dpi=(DPI, DPI))
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc.svg")
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc-invert.svg", True)
    write_bom_md()
    (OUT / "ecu-pcb-1layer-drc.md").write_text(
        f"# DRC\n\n- Cruzamentos cobre: **{cross}**\n- Trilhas: {len(traces)}\n"
        f"- Jumpers (último recurso): **{len(jumpers)}**\n- Placa: {W}×{H} mm\n\n"
        + ("Sem tarja nas imagens.\n\n## Jumpers\n\n" if jumpers else "Quase/zero jumper.\n")
        + "\n".join(f"- `{n}`" for *_, n in jumpers),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
