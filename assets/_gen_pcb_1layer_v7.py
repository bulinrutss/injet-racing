# -*- coding: utf-8 -*-
"""
INJET RACING ECU — 1-layer, fios externos mínimos.
Layout por colunas + trilhas manuais Manhattan (sem autoroute cego).
Sem tarja. Silk com códigos. Mapa de furos/pads.
Placa 240×160 mm.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"e:\injet racing\assets")
DOC = Path(r"e:\injet racing\modulo")
W, H = 240.0, 160.0
PPM = 9.0
DPI = int(25.4 * PPM)

pads: dict[str, tuple[float, float, float, float]] = {}
silk: list[tuple[float, float, str, float]] = []
boxes: list[tuple] = []
traces: list[tuple] = []  # (pts, w, net)
jumpers: list[tuple] = []
bom: list[tuple[str, str, str]] = []
# occupancy as set of (ix,iy,net) on 0.5mm for DRC of manual routes
GRID = 0.5
gw, gh = int(W / GRID) + 1, int(H / GRID) + 1
occ = [[None] * gw for _ in range(gh)]


def font(mm):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", max(7, int(mm * PPM)))
    except OSError:
        return ImageFont.load_default()


def px(*a):
    return tuple(int(round(v * PPM)) for v in a)


def add_bom(c, v, d):
    bom.append((c, v, d))


def pad(n, x, y, od=1.8, drill=0.9):
    pads[n] = (x, y, od, drill)


def label(x, y, t, s=1.7):
    silk.append((x, y, t, s))


def box(a, b, c, d, t):
    boxes.append((a, b, c, d, t))


def axial(a, b, x1, y1, x2, y2, od=1.55, dr=0.85):
    pad(a, x1, y1, od, dr)
    pad(b, x2, y2, od, dr)


def to220(code, x, y):
    pad(f"{code}.G", x - 2.54, y, 2.15, 1.05)
    pad(f"{code}.D", x, y, 2.15, 1.05)
    pad(f"{code}.S", x + 2.54, y, 2.15, 1.05)
    label(x - 1, y + 6.5, code, 1.9)


def to92(code, x, y):
    pad(f"{code}.S", x - 1.27, y, 1.45, 0.8)
    pad(f"{code}.G", x, y + 1.8, 1.45, 0.8)
    pad(f"{code}.D", x + 1.27, y, 1.45, 0.8)
    label(x, y + 5, code, 1.5)


def dip(code, x0, y0, n, pitch=2.54, row=7.62):
    h = n // 2
    for i in range(h):
        pad(f"{code}.{i+1}", x0, y0 + i * pitch, 1.55, 0.85)
        pad(f"{code}.{n-i}", x0 + row, y0 + i * pitch, 1.55, 0.85)
    label(x0 + row / 2, y0 + (h - 1) * pitch + 2.8, code, 1.8)


def soic8(code, x0, y0):
    for i in range(4):
        pad(f"{code}.{i+1}", x0, y0 + i * 1.27, 1.15, 0.0)
        pad(f"{code}.{8-i}", x0 + 5.4, y0 + i * 1.27, 1.15, 0.0)
    label(x0 + 2.7, y0 - 2, code + " SMD", 1.4)


def cell(x, y):
    return int(round(x / GRID)), int(round(y / GRID))


def paint_seg(x1, y1, x2, y2, net, w):
    """Paint axis-aligned segment into occ; return False if short."""
    half = max(1, int(round((w / 2) / GRID)))
    clr = 1
    steps = max(1, int(round(max(abs(x2 - x1), abs(y2 - y1)) / GRID)))
    for i in range(steps + 1):
        t = i / steps
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        cx, cy = cell(x, y)
        for dy in range(-half - clr, half + clr + 1):
            for dx in range(-half - clr, half + clr + 1):
                xx, yy = cx + dx, cy + dy
                if not (0 <= xx < gw and 0 <= yy < gh):
                    return False
                o = occ[yy][xx]
                if o is not None and o != net:
                    return False
        for dy in range(-half, half + 1):
            for dx in range(-half, half + 1):
                xx, yy = cx + dx, cy + dy
                if 0 <= xx < gw and 0 <= yy < gh and occ[yy][xx] in (None, net):
                    occ[yy][xx] = net
    return True


def wire(net, pts, w=0.8):
    """pts: list of (x,y) Manhattan corners. Fail → jumper endpoints."""
    if len(pts) < 2:
        return False
    # expand pad marks
    for x, y in (pts[0], pts[-1]):
        cx, cy = cell(x, y)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                xx, yy = cx + dx, cy + dy
                if 0 <= xx < gw and 0 <= yy < gh and occ[yy][xx] in (None, net):
                    occ[yy][xx] = net
    ok = True
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        if abs(a[0] - b[0]) > 0.01 and abs(a[1] - b[1]) > 0.01:
            # force manhattan via corner
            mid = (b[0], a[1])
            if not paint_seg(a[0], a[1], mid[0], mid[1], net, w):
                ok = False
                break
            if not paint_seg(mid[0], mid[1], b[0], b[1], net, w):
                ok = False
                break
        else:
            if not paint_seg(a[0], a[1], b[0], b[1], net, w):
                ok = False
                break
    if not ok:
        jumpers.append((pts[0][0], pts[0][1], pts[-1][0], pts[-1][1], net))
        return False
    traces.append((pts, w, net))
    return True


def wp(pa, pb, *mids, w=0.8, net="SIG"):
    if pa not in pads or pb not in pads:
        return False
    ax, ay = pads[pa][0], pads[pa][1]
    bx, by = pads[pb][0], pads[pb][1]
    pts = [(ax, ay)] + list(mids) + [(bx, by)]
    return wire(net, pts, w)


def pxy(name):
    return pads[name][0], pads[name][1]


# ========== PLACE — colunas alinhadas J1 ↔ drivers ↔ MCU ==========
# J1 pins spaced 4 mm; INJ columns under FETs near bottom

ATX = 4.0
for i in range(12):
    pad(f"J1.{i+1}", 12 + i * ATX, 14, 2.15, 1.1)
    pad(f"J1.{i+13}", 12 + i * ATX, 8, 2.15, 1.1)
label(36, 3.5, "J1 ATX-24", 2.1)
box(9, 5, 64, 18, "J1")
add_bom("J1", "ATX-24 header", "Conector principal chicote")

for i in range(3):
    pad(f"J2.{i+1}", 200 + i * ATX, 14, 2.15, 1.1)
    pad(f"J2.{i+4}", 200 + i * ATX, 8, 2.15, 1.1)
label(206, 3.5, "J2 PCIe-6", 1.9)
box(197, 5, 220, 18, "J2")
add_bom("J2", "PCIe-6 header", "Lambda LSU 4.2")

# Drivers JUST ABOVE connector — same X as J1.13..16 and heater near J2
# J1.13 at x=12+0*4=12? Wait J1.13 is i=0 of second row: 12+0*ATX=12 — WRONG
# J1.1 at 12, J1.13 at 12 (same column). J1.14 at 16, ... J1.16 at 24
# Actually: for i in 0..11: J1.i+1 and J1.i+13 at same x = 12+i*4
# So J1.13 at x=12, J1.14 at 16, J1.15 at 20, J1.16 at 24 — too left packed with power pins
# Better remap: put injectors on pins that are physically mid — keep electrical map, place FETs at x of those pads

inj_x = [pads[f"J1.{13+i}"][0] for i in range(4)]  # 12,16,20,24 — cramped
# Spread FETs to the RIGHT of connector body but route H to pin columns via channel y=28
inj_x = [70, 86, 102, 118]
heat_x = 190

for i, x in enumerate(inj_x):
    code = f"Q{i+1}"
    to220(code, x, 36)
    add_bom(code, "IRLZ44N", f"Driver INJ{i+1}")
    axial(f"R{10+i}.A", f"R{10+i}.B", x - 2.54, 48, x - 2.54, 56)
    label(x - 6, 52, f"R{10+i}", 1.3)
    add_bom(f"R{10+i}", "100R", f"Gate INJ{i+1}")
    axial(f"R{20+i}.A", f"R{20+i}.B", x - 2.54, 58, x + 2.54, 58)
    label(x + 5, 58, f"R{20+i}", 1.3)
    add_bom(f"R{20+i}", "10k", f"PD INJ{i+1}")
    axial(f"D{10+i}.A", f"D{10+i}.K", x + 5, 36, x + 5, 28)
    label(x + 7, 32, f"D{10+i}", 1.3)
    add_bom(f"D{10+i}", "1N4007", f"Flyback INJ{i+1}")

to220("Q5", heat_x, 36)
add_bom("Q5", "IRLZ44N", "Aquecedor lambda")
axial("R15.A", "R15.B", heat_x - 2.54, 48, heat_x - 2.54, 56)
label(heat_x - 7, 52, "R15", 1.3)
add_bom("R15", "100R", "Gate Q5")
axial("R25.A", "R25.B", heat_x - 2.54, 58, heat_x + 2.54, 58)
label(heat_x + 5, 58, "R25", 1.3)
add_bom("R25", "10k", "PD Q5")
box(62, 24, 200, 64, "DRIVERS")

# POWER top-left
to220("Q6", 20, 148)
add_bom("Q6", "IRF9540", "Proteção reversa")
axial("C1.A", "C1.B", 32, 150, 42, 150, 2.3, 0.9)
label(37, 154, "C1", 1.4)
add_bom("C1", "220u/50V", "Bulk")
axial("C2.A", "C2.B", 32, 144, 36, 144)
label(34, 140, "C2", 1.3)
add_bom("C2", "100n/100V", "Entrada")
axial("D1.A", "D1.K", 46, 150, 46, 144)
label(49, 147, "D1", 1.3)
add_bom("D1", "P6KE33A", "TVS")
axial("R1.A", "R1.B", 14, 140, 14, 134)
label(11, 137, "R1", 1.3)
add_bom("R1", "100k", "Gate Q6")
axial("D2.A", "D2.K", 18, 140, 18, 134)
label(21, 137, "D2", 1.3)
add_bom("D2", "Zener 12V", "Gate Q6")
pad("U6.VIN", 56, 150)
pad("U6.GND", 62, 150)
pad("U6.OUT", 56, 142)
label(59, 154, "U6", 1.5)
add_bom("U6", "MP1584", "Buck 5V")
pad("U7.IN", 70, 150)
pad("U7.GND", 76, 150)
pad("U7.OUT", 73, 142)
label(73, 154, "U7", 1.5)
add_bom("U7", "AMS1117-3.3", "LDO 3V3")
axial("C3.A", "C3.B", 82, 150, 86, 150)
label(84, 154, "C3", 1.3)
add_bom("C3", "10u", "LDO in")
axial("C4.A", "C4.B", 82, 144, 86, 144)
label(84, 140, "C4", 1.3)
add_bom("C4", "10u+100n", "LDO out")
box(8, 130, 90, 156, "POWER")

# Relays left mid — between power and drivers channel
for i, x in enumerate([16, 30, 44]):
    to92(f"Q{7+i}", x, 110)
    add_bom(f"Q{7+i}", "2N7000", f"Relé RL{i+1}")
    axial(f"R{30+i}.A", f"R{30+i}.B", x, 102, x, 94)
    label(x - 4, 98, f"R{30+i}", 1.25)
    add_bom(f"R{30+i}", "1k", f"Gate RL{i+1}")
    axial(f"D{20+i}.A", f"D{20+i}.K", x + 4, 110, x + 4, 102)
    label(x + 6, 106, f"D{20+i}", 1.25)
    add_bom(f"D{20+i}", "1N4007", f"Flyback RL{i+1}")
box(8, 90, 52, 118, "RELAY")

# MCU center — L pins face relays/inj gates, R face sensors/lambda
for i in range(20):
    pad(f"U1.L{i+1}", 96, 128 - i * 2.54, 1.5, 0.9)
    pad(f"U1.R{i+1}", 148, 128 - i * 2.54, 1.5, 0.9)
label(122, 72, "U1 STM32F407", 2.0)
box(94, 74, 150, 132, "U1")
add_bom("U1", "STM32F407 Black Board", "MCU")
for i in range(4):
    pad(f"J3.{i+1}", 112 + i * 2.54, 68, 1.65, 0.95)
label(116, 64, "J3 SWD", 1.4)
add_bom("J3", "1x4 SWD", "Debug")

# Sensors right of MCU — stacked matching ADC order
sy = [126, 114, 102, 90]
for i, (n, y) in enumerate(zip(["IAT", "CLT", "MAP", "TPS"], sy)):
    if n != "TPS":
        axial(f"R{40+i}.A", f"R{40+i}.B", 164, y, 172, y)
        label(168, y + 2.4, f"R{40+i}", 1.25)
        add_bom(f"R{40+i}", "2K26" if n != "MAP" else "10k 1%", f"{n}")
    if n == "MAP":
        axial("R43.A", "R43.B", 172, y, 172, y - 4)
        label(175, y - 2, "R43", 1.25)
        add_bom("R43", "18k 1%", "MAP div")
    axial(f"C{10+i}.A", f"C{10+i}.B", 176, y, 176, y - 3.5)
    label(179, y - 1, f"C{10+i}", 1.25)
    add_bom(f"C{10+i}", "100n", f"Filtro {n}")
    axial(f"R{50+i}.A", f"R{50+i}.B", 180, y, 188, y)
    label(184, y + 2.4, f"R{50+i}", 1.25)
    add_bom(f"R{50+i}", "1k", f"Série {n}")
box(162, 84, 192, 132, "SENS")

# RPM left of MCU bottom
dip("U4", 58, 78, 4)
add_bom("U4", "PC817", "Opto RPM")
axial("R60.A", "R60.B", 48, 84, 56, 84)
label(52, 87, "R60", 1.25)
add_bom("R60", "10k 2W", "RPM s1")
axial("R61.A", "R61.B", 40, 84, 48, 84)
label(44, 87, "R61", 1.25)
add_bom("R61", "10k 2W", "RPM s2")
axial("D30.A", "D30.K", 52, 78, 52, 72)
label(55, 75, "D30", 1.25)
add_bom("D30", "1N4148", "Opto prot")
axial("R62.A", "R62.B", 68, 88, 68, 82)
label(71, 85, "R62", 1.25)
add_bom("R62", "4k7", "Pull-up RPM")
axial("C20.A", "C20.B", 72, 82, 72, 76)
label(75, 79, "C20", 1.25)
add_bom("C20", "1nF", "Filtro RPM")
box(38, 70, 78, 94, "RPM")

# CAN under MCU
pad("U5.VCC", 112, 88)
pad("U5.GND", 118, 88)
pad("U5.TX", 112, 82)
pad("U5.RX", 118, 82)
pad("U5.H", 124, 88)
pad("U5.L", 130, 88)
label(120, 92, "U5 CAN", 1.5)
box(110, 80, 134, 94, "U5")
add_bom("U5", "SN65HVD230", "CAN")

# Lambda bottom-right above J2
dip("U2", 168, 40, 14)
add_bom("U2", "MCP6004", "Opamp WB")
soic8("U3", 198, 42)
add_bom("U3", "AD8628 SOIC", "Chopper Ip SMD")
axial("R70.A", "R70.B", 188, 58, 196, 58)
label(192, 61, "R70", 1.25)
add_bom("R70", "61R9 1%", "Shunt Ip")
axial("R71.A", "R71.B", 188, 64, 196, 64)
label(192, 67, "R71", 1.25)
add_bom("R71", "6k8 1%", "R_ESR")
axial("C30.A", "C30.B", 202, 58, 202, 52)
label(205, 55, "C30", 1.25)
add_bom("C30", "220n", "Filtro Ip")
axial("C31.A", "C31.B", 206, 64, 206, 58)
label(209, 61, "C31", 1.25)
add_bom("C31", "220n", "Filtro Un")
axial("C32.A", "C32.B", 160, 48, 160, 42)
label(157, 45, "C32", 1.25)
add_bom("C32", "100n+10u", "Decoupling")
axial("R72.A", "R72.B", 176, 50, 184, 50)
label(180, 53, "R72", 1.25)
add_bom("R72", "10k 1%", "Div O2")
axial("R73.A", "R73.B", 184, 50, 184, 44)
label(187, 47, "R73", 1.25)
add_bom("R73", "18k 1%", "Div O2 GND")
box(158, 36, 218, 70, "LAMBDA")

label(8, 22, "INJET RACING ECU 1L 240x160", 1.8)
label(8, 26, "Codigos silk = BOM modulo/pcb-bom-codigos.md", 1.4)

for x, y in [(4, 4), (236, 4), (4, 156), (236, 156)]:
    pad(f"MH_{x}_{y}", x, y, 3.5, 3.2)
    cx, cy = cell(x, y)
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            xx, yy = cx + dx, cy + dy
            if 0 <= xx < gw and 0 <= yy < gh:
                occ[yy][xx] = "__HOLE__"


def route_all():
    # ---- POWER rails (edges + mid channels) ----
    wire("GND", [(6, 3), (230, 3)], 2.0)
    wire("+12V", [(6, 157), (200, 157)], 1.8)
    wire("+5V", [(54, 136), (230, 136)], 1.2)
    wire("+3V3", [(70, 132), (230, 132)], 1.1)

    # Power module locals
    wp("Q6.G", "R1.A", net="QG", w=0.7)
    wp("Q6.G", "D2.A", net="QG", w=0.7)
    wp("R1.B", "D2.K", net="GND", w=0.7)
    wp("Q6.S", "C1.A", net="+12V", w=1.2)
    wp("C1.B", "C2.B", net="GND", w=0.9)
    wp("C2.A", "D1.A", net="+12V", w=0.9)
    wp("D1.K", "C1.B", net="GND", w=0.9)
    wp("U6.VIN", "Q6.S", net="+12V", w=1.1)
    wp("U6.GND", "U7.GND", net="GND", w=0.85)
    wp("U6.OUT", "U7.IN", net="+5V", w=1.0)
    wp("U7.IN", "C3.A", net="+5V", w=0.85)
    wp("C3.B", "C4.B", net="GND", w=0.85)
    wp("U7.OUT", "C4.A", net="+3V3", w=0.9)

    # Stubs power to rails
    for p in ["Q6.S", "U6.VIN"]:
        x, y = pxy(p)
        wire("+12V", [(x, y), (x, 157)], 1.2)
    for p in ["D10.K", "D11.K", "D12.K", "D13.K"]:
        x, y = pxy(p)
        wire("+12V", [(x, y), (x, 24), (6, 24), (6, 157)], 1.0)  # via left channel
    for p in ["D20.K", "D21.K", "D22.K"]:
        x, y = pxy(p)
        wire("+12V", [(x, y), (x, 120), (6, 120), (6, 157)], 1.0)
    x, y = pxy("J2.1")
    wire("+12V", [(x, y), (x, 24), (200, 24), (200, 157)], 1.1)

    for p in ["U6.OUT", "C32.A", "U2.14"]:
        x, y = pxy(p)
        wire("+5V", [(x, y), (x, 136)], 0.95)
    x, y = pxy("J1.6")
    wire("+5V", [(x, y), (x, 20), (230, 20), (230, 136)], 0.95)
    x, y = pxy("U1.R1")
    wire("+5V", [(x, y), (230, y), (230, 136)], 0.9)
    x, y = pxy("U5.VCC")
    wire("+5V", [(x, y), (x, 136)], 0.85)

    for p in ["U7.OUT", "R40.A", "R41.A", "R42.A", "R62.A", "J3.1", "U1.L1"]:
        x, y = pxy(p)
        wire("+3V3", [(x, y), (x, 132)], 0.85)
    x, y = pxy("J1.7")
    wire("+3V3", [(x, y), (x, 20), (226, 20), (226, 132)], 0.85)

    # GND: só rail + ligações locais já feitas; stubs longos no fim (após sinais)
    for p in ["J1.3", "J1.4", "J1.5", "J1.24"]:
        x, y = pxy(p)
        wire("GND", [(x, y), (x, 3)], 1.0)

    # ---- Injector locals + to J1 (canal y=22) ----
    for i in range(4):
        wp(f"D{10+i}.A", f"Q{i+1}.D", net=f"INJ{i+1}", w=1.0)
        wp(f"R{10+i}.A", f"Q{i+1}.G", net=f"GI{i+1}", w=0.7)
        wp(f"R{20+i}.A", f"Q{i+1}.G", net=f"GI{i+1}", w=0.65)
        wp(f"R{20+i}.B", f"Q{i+1}.S", net="GND", w=0.7)
        # drain → connector pin via bottom channel, lane per injector
        lane = 18 + i * 1.5
        xa, ya = pxy(f"Q{i+1}.D")
        xb, yb = pxy(f"J1.{13+i}")
        wire(f"INJ{i+1}", [(xa, ya), (xa, lane), (xb, lane), (xb, yb)], 1.05)
        # gate from MCU L13..L16 via channel y=66, ordered lanes
        glane = 66 + i * 1.2
        ra, ry = pxy(f"R{10+i}.B")
        mx, my = pxy(f"U1.L{13+i}")
        wire(f"GI{i+1}", [(mx, my), (80, my), (80, glane), (ra, glane), (ra, ry)], 0.75)

    wp("R15.A", "Q5.G", net="GH", w=0.7)
    wp("R25.A", "Q5.G", net="GH", w=0.65)
    wp("R25.B", "Q5.S", net="GND", w=0.7)
    xa, ya = pxy("Q5.D")
    xb, yb = pxy("J2.2")
    wire("H-", [(xa, ya), (xa, 22), (xb, 22), (xb, yb)], 1.2)
    ra, ry = pxy("R15.B")
    mx, my = pxy("U1.L17")
    wire("GH", [(mx, my), (80, my), (80, 70), (ra, 70), (ra, ry)], 0.75)

    # Relays
    for i, cn in enumerate([18, 17, 19]):
        wp(f"D{20+i}.A", f"Q{7+i}.D", net=f"RL{i+1}", w=0.85)
        wp(f"R{30+i}.A", f"Q{7+i}.G", net=f"GR{i+1}", w=0.65)
        xa, ya = pxy(f"Q{7+i}.D")
        xb, yb = pxy(f"J1.{cn}")
        lane = 26 + i
        wire(f"RL{i+1}", [(xa, ya), (xa, lane), (xb, lane), (xb, yb)], 0.95)
        ra, ry = pxy(f"R{30+i}.B")
        mx, my = pxy(f"U1.L{18+i}")
        wire(f"GR{i+1}", [(mx, my), (84, my), (84, ry), (ra, ry)], 0.7)

    # Sensors: J1 → Rxx → MCU R3..R6 via right channel x=194
    for i, (n, jpin, mcu) in enumerate([
        ("IAT", 8, "U1.R3"), ("CLT", 9, "U1.R4"), ("MAP", 10, "U1.R5"), ("TPS", 11, "U1.R6")
    ]):
        if n != "TPS":
            wp(f"J1.{jpin}", f"R{40+i}.B", (pads[f"J1.{jpin}"][0], 20), (194, 20), (194, pads[f"R{40+i}.B"][1]), net=n, w=0.8)
            wp(f"R{40+i}.B", f"C{10+i}.A", net=n, w=0.65)
            wp(f"R{40+i}.B", f"R{50+i}.A", net=n, w=0.65)
        else:
            wp("J1.11", "R53.A", (pads["J1.11"][0], 20), (194, 20), (194, pads["R53.A"][1]), net=n, w=0.8)
            wp("R53.A", "C13.A", net=n, w=0.65)
        if n == "MAP":
            wp("R42.B", "R43.A", net="MAP", w=0.65)
        wp(f"R{50+i}.B", mcu, net=n, w=0.8)

    # RPM
    wp("J1.12", "R61.A", (pads["J1.12"][0], 20), (40, 20), net="RPMi", w=0.85)
    wp("R61.B", "R60.A", net="RPMi", w=0.8)
    wp("R60.B", "U4.1", net="RPMi", w=0.75)
    wp("U4.2", "U4.3", net="GND", w=0.7)
    wp("D30.A", "U4.1", net="RPMi", w=0.6)
    wp("D30.K", "U4.2", net="RPMi", w=0.6)
    wp("U4.4", "R62.B", net="RPMo", w=0.7)
    wp("U4.4", "C20.A", net="RPMo", w=0.6)
    wp("U4.4", "U1.L10", (90, pads["U4.4"][1]), net="RPMo", w=0.8)

    # CAN — short under MCU
    wp("U1.L12", "U5.TX", net="CANTX", w=0.7)
    wp("U1.L11", "U5.RX", net="CANRX", w=0.7)
    xa, ya = pxy("U5.H")
    xb, yb = pxy("J1.20")
    wire("CANH", [(xa, ya), (xa, 28), (xb, 28), (xb, yb)], 0.9)
    xa, ya = pxy("U5.L")
    xb, yb = pxy("J1.21")
    wire("CANL", [(xa, ya), (xa, 30), (xb, 30), (xb, yb)], 0.9)

    # Lambda
    wp("J2.3", "R70.A", (pads["J2.3"][0], 20), (188, 20), net="IP", w=0.85)
    wp("R70.B", "C30.A", net="IP", w=0.65)
    wp("U3.6", "R70.A", net="IP", w=0.7)
    wp("U3.2", "R70.A", net="IP", w=0.65)
    wp("R70.B", "U1.R8", (200, pads["R70.B"][1]), (200, pads["U1.R8"][1]), net="IP", w=0.8)
    wp("U1.R9", "U2.3", net="VM", w=0.75)
    wp("U2.1", "U2.2", net="VM", w=0.6)
    wp("U2.1", "J2.4", (pads["U2.1"][0], 20), (pads["J2.4"][0], 20), net="VM", w=0.8)
    wp("U3.3", "J2.4", (pads["U3.3"][0], 20), (pads["J2.4"][0], 20), net="VM", w=0.7)
    wp("J2.5", "R71.A", (pads["J2.5"][0], 18), (188, 18), net="UN", w=0.8)
    wp("R71.A", "C31.A", net="UN", w=0.65)
    wp("R71.A", "U1.R10", (204, pads["R71.A"][1]), (204, pads["U1.R10"][1]), net="UN", w=0.8)
    wp("U1.R11", "R71.B", (210, pads["U1.R11"][1]), (210, pads["R71.B"][1]), net="RI", w=0.7)
    wp("U2.7", "R72.A", net="O2", w=0.7)
    wp("R72.B", "R73.A", net="O2", w=0.6)
    wp("R72.B", "U1.R7", (156, pads["R72.B"][1]), (156, pads["U1.R7"][1]), net="O2", w=0.8)

    # Battery in + SWD
    xa, ya = pxy("J1.1")
    xb, yb = pxy("Q6.D")
    wire("+12VIN", [(xa, ya), (xa, 20), (8, 20), (8, yb), (xb, yb)], 1.5)
    xa, ya = pxy("J1.2")
    wire("+12VIN", [(xa, ya), (xa, 21), (9, 21), (9, yb), (xb, yb)], 1.3)
    wp("J3.2", "U1.R14", net="SWDIO", w=0.65)
    wp("J3.3", "U1.R15", net="SWCLK", w=0.65)

    # GND restante: trilho horizontal mid + stubs curtos (não atravessar a placa inteira)
    wire("GND", [(6, 64), (230, 64)], 1.3)
    wire("GND", [(6, 100), (90, 100)], 1.2)
    for p, by in [
        ("Q1.S", 64), ("Q2.S", 64), ("Q3.S", 64), ("Q4.S", 64), ("Q5.S", 64),
        ("Q7.S", 100), ("Q8.S", 100), ("Q9.S", 100),
        ("C20.B", 64), ("U4.3", 64), ("U5.GND", 64), ("J3.4", 64),
        ("U1.L2", 64), ("U1.R2", 64), ("U2.4", 64), ("C32.B", 64),
        ("C10.B", 64), ("C11.B", 64), ("C12.B", 64), ("C13.B", 64),
        ("C30.B", 64), ("C31.B", 64), ("R43.B", 64), ("R73.B", 64),
    ]:
        if p not in pads:
            continue
        x, y = pxy(p)
        wire("GND", [(x, y), (x, by)], 0.9)
    # power GND → canal esquerdo → bus inferior
    for p in ["C1.B", "U6.GND", "C4.B"]:
        x, y = pxy(p)
        wire("GND", [(x, y), (6, y), (6, 3)], 1.0)


def count_cross():
    S = []
    for pts, w, net in traces:
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            if abs(a[0] - b[0]) > 0.01 and abs(a[1] - b[1]) > 0.01:
                mid = (b[0], a[1])
                S.append((a, mid, net))
                S.append((mid, b, net))
            else:
                S.append((a, b, net))

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
                col = {"GND": (35, 35, 35), "+12V": (220, 45, 45), "+12VIN": (180, 30, 30),
                       "+5V": (210, 140, 40), "+3V3": (50, 130, 210)}.get(net, (210, 185, 55))
                d.line(flat, fill=col, width=max(2, int(w * PPM * 0.85)))
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


def render_assembly():
    img = Image.new("RGB", px(W, H), (14, 18, 22))
    draw_base(ImageDraw.Draw(img), True, True, True, True)
    return img


def render_pads_map():
    img = Image.new("RGB", px(W, H), (248, 248, 242))
    d = ImageDraw.Draw(img)

    def Y(y):
        return H - y

    def P(x, y):
        return px(x, Y(y))

    d.rectangle([*px(0.3, 0.3), *px(W - 0.3, H - 0.3)], outline=(20, 20, 20), width=2)
    for x0, y0, x1, y1, t in boxes:
        d.rectangle([*P(x0, y1), *P(x1, y0)], outline=(150, 150, 150), width=1)
    # compact BOM printed on map
    by = 150
    d.text(P(8, by), "CODIGOS:", fill=(0, 0, 0), font=font(1.8))
    codes = [c for c, _, _ in bom]
    line, x = "", 8
    yy = 146
    for c in codes:
        trial = (line + " " + c).strip()
        if len(trial) > 55:
            d.text(P(x, yy), line, fill=(0, 0, 0), font=font(1.35))
            yy -= 3.2
            line = c
        else:
            line = trial
    if line:
        d.text(P(x, yy), line, fill=(0, 0, 0), font=font(1.35))
    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MH_"):
            d.ellipse([*P(x - 1.8, y + 1.8), *P(x + 1.8, y - 1.8)], outline=(0, 0, 0), width=2)
            continue
        r = od / 2
        if drill > 0:
            d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], outline=(0, 0, 0), width=2)
            d.ellipse([*P(x - drill / 2, y + drill / 2), *P(x + drill / 2, y - drill / 2)], fill=(255, 255, 255), outline=(0, 0, 0))
        else:
            d.rectangle([*P(x - r, y + r * 0.55), *P(x + r, y - r * 0.55)], fill=(70, 70, 70), outline=(0, 0, 0))
    for x, y, t, s in silk:
        d.text(P(x, y), t, fill=(0, 0, 0), font=font(s))
    d.text(P(8, 30), "MAPA MONTAGEM — furos THT + pads SMD (U3)", fill=(0, 0, 0), font=font(2.1))
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
    L.append("</g><g fill=\"" + bg + "\">")
    for name, (x, y, od, drill) in pads.items():
        if drill > 0:
            L.append(f'<circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{drill/2:.3f}"/>')
    for x, y in [(4, 4), (236, 4), (4, 156), (236, 156)]:
        L.append(f'<circle cx="{x}" cy="{Y(y)}" r="1.6"/>')
    L.append("</g></svg>")
    path.write_text("\n".join(L), encoding="utf-8")


def write_bom(cross, nj):
    lines = [
        "# BOM com códigos — PCB INJET RACING (1-layer)",
        "",
        f"> Placa **{W:.0f}×{H:.0f} mm**. Códigos = silk / mapa de furos.",
        "",
        f"- Cruzamentos cobre: **{cross}**",
        f"- Fios topo (último recurso): **{nj}**",
        "",
        "| Código | Valor / P/N | Função |",
        "|---|---|---|",
    ]
    for c, v, d in bom:
        lines.append(f"| **{c}** | `{v}` | {d} |")
    lines += [
        "",
        "## Conectores",
        "",
        "### J1 ATX-24",
        "1:+12 IGN · 2:+12 BAT · 3/4:GND_P · 5:GND_S · 6:+5 · 7:+3V3 · 8:IAT · 9:CLT · 10:MAP · 11:TPS · 12:RPM",
        "13–16:INJ1–4 · 17:RL bomba · 18:RL main · 19:RL IAC · 20:CANH · 21:CANL · 22:tacho · 23:start · 24:shield",
        "",
        "### J2 PCIe-6",
        "1:H+ · 2:H− · 3:IP · 4:VM · 5:UN · 6:NC",
        "",
        "### J3 SWD",
        "1:+3V3 · 2:SWDIO · 3:SWCLK · 4:GND",
        "",
        "## Arquivos",
        "",
        "- `assets/ecu-pcb-1layer-pads-map.png` — só furos/pads + códigos (montagem)",
        "- `assets/ecu-pcb-1layer-assembly.png` — visão com trilhas (sem tarja)",
        "- `assets/ecu-pcb-1layer-traces-cnc.svg` — máscara CNC",
        "",
    ]
    (DOC / "pcb-bom-codigos.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    print("Routing v7 manual…")
    route_all()
    cross = count_cross()
    print(f"cross={cross} traces={len(traces)} jumpers={len(jumpers)} bom={len(bom)}")
    if jumpers:
        from collections import Counter
        print("jumper nets:", dict(Counter(n for *_, n in jumpers)))

    render_assembly().save(OUT / "ecu-pcb-1layer-assembly.png", dpi=(DPI, DPI))
    render_pads_map().save(OUT / "ecu-pcb-1layer-pads-map.png", dpi=(DPI, DPI))
    render_cnc(False).save(OUT / "ecu-pcb-1layer-traces-cnc.png", dpi=(DPI, DPI))
    render_cnc(True).save(OUT / "ecu-pcb-1layer-traces-cnc-invert.png", dpi=(DPI, DPI))
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc.svg")
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc-invert.svg", True)
    write_bom(cross, len(jumpers))
    (OUT / "ecu-pcb-1layer-drc.md").write_text(
        f"# DRC\n\n- Cruzamentos cobre: **{cross}**\n- Trilhas: {len(traces)}\n"
        f"- Jumpers: **{len(jumpers)}**\n- Placa: {W}×{H} mm\n\nSem tarja nas imagens.\n\n"
        + ("## Jumpers\n\n" + "\n".join(f"- `{n}`" for *_, n in jumpers) if jumpers else "Zero jumpers."),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
