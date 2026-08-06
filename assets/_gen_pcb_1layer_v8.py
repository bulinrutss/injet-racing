# -*- coding: utf-8 -*-
"""
INJET RACING ECU — 1-layer fenolite CNC.
- Trilhas manuais Manhattan (sinais + potência)
- GND = pour (cobre restante) — não precisa fio
- Sem tarja · silk com códigos · mapa só furos
- Meta: 0 cruzamento cobre, 0 fio externo
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
traces: list[tuple] = []
jumpers: list[tuple] = []
bom: list[tuple[str, str, str]] = []


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
        pad(f"{code}.{i + 1}", x0, y0 + i * pitch, 1.55, 0.85)
        pad(f"{code}.{n - i}", x0 + row, y0 + i * pitch, 1.55, 0.85)
    label(x0 + row / 2, y0 + (h - 1) * pitch + 2.8, code, 1.8)


def soic8(code, x0, y0):
    for i in range(4):
        pad(f"{code}.{i + 1}", x0, y0 + i * 1.27, 1.15, 0.0)
        pad(f"{code}.{8 - i}", x0 + 5.4, y0 + i * 1.27, 1.15, 0.0)
    label(x0 + 2.7, y0 - 2, code + " SMD", 1.4)


def pxy(n):
    return pads[n][0], pads[n][1]


def man(*pts):
    """Expand any diagonal into Manhattan via horizontal-then-vertical."""
    out = [pts[0]]
    for i in range(1, len(pts)):
        x0, y0 = out[-1]
        x1, y1 = pts[i]
        if abs(x0 - x1) > 0.05 and abs(y0 - y1) > 0.05:
            out.append((x1, y0))
        out.append((x1, y1))
    return out


def would_cross(pts, net):
    """True se a polilinha cruza alguma trilha de outra net."""
    segs = []
    for i in range(len(pts) - 1):
        segs.append((pts[i], pts[i + 1]))

    def ori(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def near(p, q, eps=0.2):
        return abs(p[0] - q[0]) < eps and abs(p[1] - q[1]) < eps

    def hit(a, b, c, d):
        if near(a, c) or near(a, d) or near(b, c) or near(b, d):
            return False
        return ori(a, b, c) * ori(a, b, d) < -1e-9 and ori(c, d, a) * ori(c, d, b) < -1e-9

    for pts2, w2, net2 in traces:
        if net2 == net:
            continue
        for i in range(len(pts2) - 1):
            c, d = pts2[i], pts2[i + 1]
            for a, b in segs:
                if hit(a, b, c, d):
                    return True
    return False


def tr(net, w, *pts):
    path = man(*pts)
    if would_cross(path, net):
        jumpers.append((path[0][0], path[0][1], path[-1][0], path[-1][1], net))
        return False
    traces.append((path, w, net))
    return True


def trp(net, w, pa, pb, *mids):
    ax, ay = pxy(pa)
    bx, by = pxy(pb)
    tr(net, w, (ax, ay), *mids, (bx, by))


# ===================== PLACE =====================
ATX = 4.0
for i in range(12):
    pad(f"J1.{i + 1}", 12 + i * ATX, 14, 2.15, 1.1)
    pad(f"J1.{i + 13}", 12 + i * ATX, 8, 2.15, 1.1)
label(36, 3.5, "J1 ATX-24", 2.1)
box(9, 5, 64, 18, "J1")
add_bom("J1", "ATX-24 header", "Conector principal chicote")

for i in range(3):
    pad(f"J2.{i + 1}", 200 + i * ATX, 14, 2.15, 1.1)
    pad(f"J2.{i + 4}", 200 + i * ATX, 8, 2.15, 1.1)
label(206, 3.5, "J2 PCIe-6", 1.9)
box(197, 5, 220, 18, "J2")
add_bom("J2", "PCIe-6 header", "Lambda LSU 4.2")

# Drivers above mid — columns clear of connector fanout
inj_x = [72, 90, 108, 126]
for i, x in enumerate(inj_x):
    to220(f"Q{i + 1}", x, 40)
    add_bom(f"Q{i + 1}", "IRLZ44N", f"Driver INJ{i + 1}")
    axial(f"R{10 + i}.A", f"R{10 + i}.B", x - 2.54, 52, x - 2.54, 60)
    label(x - 6, 56, f"R{10 + i}", 1.3)
    add_bom(f"R{10 + i}", "100R", f"Gate INJ{i + 1}")
    axial(f"R{20 + i}.A", f"R{20 + i}.B", x - 2.54, 62, x + 2.54, 62)
    label(x + 5, 62, f"R{20 + i}", 1.3)
    add_bom(f"R{20 + i}", "10k", f"PD INJ{i + 1}")
    # diodo à ESQUERDA — coletor +12V não cruza descida do drain (direita)
    axial(f"D{10 + i}.A", f"D{10 + i}.K", x - 5.2, 40, x - 5.2, 32)
    label(x - 8, 36, f"D{10 + i}", 1.3)
    add_bom(f"D{10 + i}", "1N4007", f"Flyback INJ{i + 1}")

to220("Q5", 152, 40)
add_bom("Q5", "IRLZ44N", "Aquecedor lambda")
axial("R15.A", "R15.B", 149.46, 52, 149.46, 60)
label(144, 56, "R15", 1.3)
add_bom("R15", "100R", "Gate Q5")
axial("R25.A", "R25.B", 149.46, 62, 154.54, 62)
label(157, 62, "R25", 1.3)
add_bom("R25", "10k", "PD Q5")
axial("D14.A", "D14.K", 146.8, 40, 146.8, 32)
label(142, 36, "D14", 1.3)
add_bom("D14", "1N4007", "Flyback Q5")
box(64, 28, 162, 68, "DRIVERS")

# Power top-left
to220("Q6", 22, 148)
add_bom("Q6", "IRF9540", "Proteção reversa")
axial("C1.A", "C1.B", 34, 150, 44, 150, 2.3, 0.9)
label(39, 154, "C1", 1.4)
add_bom("C1", "220u/50V", "Bulk")
axial("C2.A", "C2.B", 34, 144, 38, 144)
label(36, 140, "C2", 1.3)
add_bom("C2", "100n/100V", "Entrada")
axial("D1.A", "D1.K", 48, 150, 48, 144)
label(51, 147, "D1", 1.3)
add_bom("D1", "P6KE33A", "TVS")
axial("R1.A", "R1.B", 14, 140, 14, 134)
label(11, 137, "R1", 1.3)
add_bom("R1", "100k", "Gate Q6")
axial("D2.A", "D2.K", 18, 140, 18, 134)
label(21, 137, "D2", 1.3)
add_bom("D2", "Zener 12V", "Gate Q6")
pad("U6.VIN", 58, 150)
pad("U6.GND", 64, 150)
pad("U6.OUT", 58, 142)
label(61, 154, "U6", 1.5)
add_bom("U6", "MP1584", "Buck 5V")
pad("U7.IN", 72, 150)
pad("U7.GND", 78, 150)
pad("U7.OUT", 75, 142)
label(75, 154, "U7", 1.5)
add_bom("U7", "AMS1117-3.3", "LDO 3V3")
axial("C3.A", "C3.B", 84, 150, 88, 150)
label(86, 154, "C3", 1.3)
add_bom("C3", "10u", "LDO in")
axial("C4.A", "C4.B", 84, 144, 88, 144)
label(86, 140, "C4", 1.3)
add_bom("C4", "10u+100n", "LDO out")
box(8, 130, 92, 156, "POWER")

# Relays left
for i, x in enumerate([16, 30, 44]):
    to92(f"Q{7 + i}", x, 112)
    add_bom(f"Q{7 + i}", "2N7000", f"Relé RL{i + 1}")
    axial(f"R{30 + i}.A", f"R{30 + i}.B", x, 104, x, 96)
    label(x - 4, 100, f"R{30 + i}", 1.25)
    add_bom(f"R{30 + i}", "1k", f"Gate RL{i + 1}")
    axial(f"D{20 + i}.A", f"D{20 + i}.K", x + 4, 112, x + 4, 104)
    label(x + 6, 108, f"D{20 + i}", 1.25)
    add_bom(f"D{20 + i}", "1N4007", f"Flyback RL{i + 1}")
box(8, 92, 52, 120, "RELAY")

# MCU
for i in range(20):
    pad(f"U1.L{i + 1}", 100, 130 - i * 2.54, 1.5, 0.9)
    pad(f"U1.R{i + 1}", 152, 130 - i * 2.54, 1.5, 0.9)
label(126, 74, "U1 STM32F407", 2.0)
box(98, 76, 154, 134, "U1")
add_bom("U1", "STM32F407 Black Board", "MCU")
for i in range(4):
    pad(f"J3.{i + 1}", 116 + i * 2.54, 70, 1.65, 0.95)
label(120, 66, "J3 SWD", 1.4)
add_bom("J3", "1x4 SWD", "Debug")

# Sensors
sy = [128, 116, 104, 92]
for i, (n, y) in enumerate(zip(["IAT", "CLT", "MAP", "TPS"], sy)):
    if n != "TPS":
        axial(f"R{40 + i}.A", f"R{40 + i}.B", 168, y, 176, y)
        label(172, y + 2.4, f"R{40 + i}", 1.25)
        add_bom(f"R{40 + i}", "2K26" if n != "MAP" else "10k 1%", n)
    if n == "MAP":
        axial("R43.A", "R43.B", 176, y, 176, y - 4)
        label(179, y - 2, "R43", 1.25)
        add_bom("R43", "18k 1%", "MAP div")
    axial(f"C{10 + i}.A", f"C{10 + i}.B", 180, y, 180, y - 3.5)
    label(183, y - 1, f"C{10 + i}", 1.25)
    add_bom(f"C{10 + i}", "100n", f"Filtro {n}")
    axial(f"R{50 + i}.A", f"R{50 + i}.B", 184, y, 192, y)
    label(188, y + 2.4, f"R{50 + i}", 1.25)
    add_bom(f"R{50 + i}", "1k", f"Série {n}")
box(166, 86, 196, 134, "SENS")

# RPM
dip("U4", 60, 80, 4)
add_bom("U4", "PC817", "Opto RPM")
axial("R60.A", "R60.B", 50, 86, 58, 86)
label(54, 89, "R60", 1.25)
add_bom("R60", "10k 2W", "RPM s1")
axial("R61.A", "R61.B", 42, 86, 50, 86)
label(46, 89, "R61", 1.25)
add_bom("R61", "10k 2W", "RPM s2")
axial("D30.A", "D30.K", 54, 80, 54, 74)
label(57, 77, "D30", 1.25)
add_bom("D30", "1N4148", "Opto prot")
axial("R62.A", "R62.B", 70, 90, 70, 84)
label(73, 87, "R62", 1.25)
add_bom("R62", "4k7", "Pull-up RPM")
axial("C20.A", "C20.B", 74, 84, 74, 78)
label(77, 81, "C20", 1.25)
add_bom("C20", "1nF", "Filtro RPM")
box(40, 72, 80, 96, "RPM")

# CAN
pad("U5.VCC", 116, 90)
pad("U5.GND", 122, 90)
pad("U5.TX", 116, 84)
pad("U5.RX", 122, 84)
pad("U5.H", 128, 90)
pad("U5.L", 134, 90)
label(124, 94, "U5 CAN", 1.5)
box(114, 82, 138, 96, "U5")
add_bom("U5", "SN65HVD230", "CAN")

# Lambda
dip("U2", 172, 42, 14)
add_bom("U2", "MCP6004", "Opamp WB")
soic8("U3", 202, 44)
add_bom("U3", "AD8628 SOIC", "Chopper Ip SMD")
axial("R70.A", "R70.B", 192, 60, 200, 60)
label(196, 63, "R70", 1.25)
add_bom("R70", "61R9 1%", "Shunt Ip")
axial("R71.A", "R71.B", 192, 66, 200, 66)
label(196, 69, "R71", 1.25)
add_bom("R71", "6k8 1%", "R_ESR")
axial("C30.A", "C30.B", 206, 60, 206, 54)
label(209, 57, "C30", 1.25)
add_bom("C30", "220n", "Filtro Ip")
axial("C31.A", "C31.B", 210, 66, 210, 60)
label(213, 63, "C31", 1.25)
add_bom("C31", "220n", "Filtro Un")
axial("C32.A", "C32.B", 164, 50, 164, 44)
label(161, 47, "C32", 1.25)
add_bom("C32", "100n+10u", "Decoupling")
axial("R76.A", "R76.B", 168, 52, 172, 52)
label(170, 55, "R76", 1.25)
add_bom("R76", "10k", "Bias Vm")
axial("R77.A", "R77.B", 168, 48, 172, 48)
label(170, 51, "R77", 1.25)
add_bom("R77", "10k", "Bias Vm")
axial("R78.A", "R78.B", 204, 52, 204, 48)
label(207, 50, "R78", 1.25)
add_bom("R78", "1k", "Serie AD8628")
box(162, 38, 220, 72, "LAMBDA")

# VBat sense + REF3033
axial("R74.A", "R74.B", 94, 130, 100, 130)
label(97, 133, "R74", 1.25)
add_bom("R74", "100k 1%", "VBat hi")
axial("R75.A", "R75.B", 100, 130, 100, 126)
label(103, 128, "R75", 1.25)
add_bom("R75", "10k 1%", "VBat lo")
axial("C33.A", "C33.B", 104, 130, 104, 126)
label(107, 128, "C33", 1.25)
add_bom("C33", "100n", "Filtro VBat")
pad("U8.OUT", 88, 142)
pad("U8.GND", 88, 138)
label(88, 146, "U8 REF", 1.4)
add_bom("U8", "REF3033", "Ref ADC 3V3")
box(84, 134, 108, 148, "VREF")

# Silk BOM strip on board
label(8, 22, "INJET RACING ECU 1L", 2.0)
label(8, 26, "GND=POUR  CNC=traces  BOM=pcb-bom-codigos.md", 1.35)
codes = " ".join(c for c, _, _ in bom)
# wrap codes onto silk
x, y, line = 8.0, 154.0, ""
for c in codes.split():
    t = (line + " " + c).strip()
    if len(t) > 48:
        label(x, y, line, 1.2)
        y -= 3.0
        line = c
    else:
        line = t
if line:
    label(x, y, line, 1.2)

for x, y in [(4, 4), (236, 4), (4, 156), (236, 156)]:
    pad(f"MH_{x}_{y}", x, y, 3.5, 3.2)


def route_all():
    """Sinais primeiro (canais), potência depois. GND=pour. tr() recusa cruzamento."""
    # === LOCAIS POWER (curtos) ===
    trp("QG", 0.7, "Q6.G", "R1.A")
    trp("QG", 0.7, "Q6.G", "D2.A")
    trp("+12V", 1.2, "Q6.S", "C1.A")
    trp("+12V", 0.9, "C2.A", "D1.A")
    trp("+12V", 1.1, "U6.VIN", "Q6.S")
    trp("+5V", 1.0, "U6.OUT", "U7.IN")
    trp("+5V", 0.85, "U7.IN", "C3.A")
    trp("+3V3", 0.9, "U7.OUT", "C4.A")

    # === INJECTORS ===
    for i in range(4):
        trp(f"INJ{i+1}", 1.0, f"D{10+i}.A", f"Q{i+1}.D")
        trp(f"GI{i+1}", 0.7, f"R{10+i}.A", f"Q{i+1}.G")
        trp(f"GI{i+1}", 0.65, f"R{20+i}.A", f"Q{i+1}.G")
        lane = 17.0 + i * 1.0
        xa, ya = pxy(f"Q{i+1}.D")
        xb, yb = pxy(f"J1.{13+i}")
        tr(f"INJ{i+1}", 1.05, (xa, ya), (xa + 3.2, ya), (xa + 3.2, lane), (xb, lane), (xb, yb))
        gl = 72.0 + i * 1.0
        ra, ry = pxy(f"R{10+i}.B")
        mx, my = pxy(f"U1.L{13+i}")
        tr(f"GI{i+1}", 0.75, (mx, my), (88, my), (88, gl), (ra, gl), (ra, ry))

    trp("GH", 0.7, "R15.A", "Q5.G")
    trp("GH", 0.65, "R25.A", "Q5.G")
    xa, ya = pxy("Q5.D")
    xb, yb = pxy("J2.2")
    tr("H-", 1.2, (xa, ya), (xa + 3.2, ya), (xa + 3.2, 22), (xb, 22), (xb, yb))
    trp("H-", 0.9, "D14.A", "Q5.D")
    ra, ry = pxy("R15.B")
    mx, my = pxy("U1.L17")
    tr("GH", 0.75, (mx, my), (88, my), (88, 76), (ra, 76), (ra, ry))

    for i, cn in enumerate([18, 17, 19]):
        trp(f"RL{i+1}", 0.85, f"D{20+i}.A", f"Q{7+i}.D")
        trp(f"GR{i+1}", 0.65, f"R{30+i}.A", f"Q{7+i}.G")
        xa, ya = pxy(f"Q{7+i}.D")
        xb, yb = pxy(f"J1.{cn}")
        lane = 24.0 + i * 0.9
        tr(f"RL{i+1}", 0.95, (xa, ya), (xa, lane), (xb, lane), (xb, yb))
        ra, ry = pxy(f"R{30+i}.B")
        mx, my = pxy(f"U1.L{18+i}")
        tr(f"GR{i+1}", 0.7, (mx, my), (86, my), (86, ry), (ra, ry))

    for i, (n, jp, mcu) in enumerate([
        ("IAT", 8, "U1.R3"), ("CLT", 9, "U1.R4"), ("MAP", 10, "U1.R5"), ("TPS", 11, "U1.R6")
    ]):
        jx, jy = pxy(f"J1.{jp}")
        fan = 5.2 + i * 0.45
        if n != "TPS":
            rx, ry = pxy(f"R{40+i}.B")
            tr(n, 0.8, (jx, jy), (jx, fan), (186, fan), (186, ry), (rx, ry))
            trp(n, 0.65, f"R{40+i}.B", f"C{10+i}.A")
            trp(n, 0.65, f"R{40+i}.B", f"R{50+i}.A")
        else:
            rx, ry = pxy("R53.A")
            tr(n, 0.8, (jx, jy), (jx, fan), (186, fan), (186, ry), (rx, ry))
            trp(n, 0.65, "R53.A", "C13.A")
        if n == "MAP":
            trp("MAP", 0.65, "R42.B", "R43.A")
        rx, ry = pxy(f"R{50+i}.B")
        mx, my = pxy(mcu)
        tr(n, 0.8, (rx, ry), (rx, 134), (155, 134), (155, my), (mx, my))

    jx, jy = pxy("J1.12")
    rx, ry = pxy("R61.A")
    tr("RPMi", 0.85, (jx, jy), (jx, 23.5), (42, 23.5), (rx, ry))
    trp("RPMi", 0.8, "R61.B", "R60.A")
    trp("RPMi", 0.75, "R60.B", "U4.1")
    trp("RPMi", 0.6, "D30.A", "U4.1")
    trp("RPMi", 0.6, "D30.K", "U4.2")
    trp("RPMo", 0.7, "U4.4", "R62.B")
    trp("RPMo", 0.6, "U4.4", "C20.A")
    trp("RPMo", 0.8, "U4.4", "U1.L10", (92, pxy("U4.4")[1]))

    trp("CANTX", 0.7, "U1.L12", "U5.TX")
    trp("CANRX", 0.7, "U1.L11", "U5.RX")
    xa, ya = pxy("U5.H")
    xb, yb = pxy("J1.20")
    tr("CANH", 0.9, (xa, ya), (140, ya), (140, 27), (xb, 27), (xb, yb))
    xa, ya = pxy("U5.L")
    xb, yb = pxy("J1.21")
    tr("CANL", 0.9, (xa, ya), (142, ya), (142, 28.2), (xb, 28.2), (xb, yb))

    tr("IP", 0.85, pxy("J2.3"), (pxy("J2.3")[0], 1.8), (220, 1.8), (220, 60), pxy("R70.A"))
    trp("IP", 0.65, "R70.B", "C30.A")
    trp("IP", 0.7, "U3.6", "R70.A")
    trp("IP", 0.65, "U3.2", "R70.A")
    trp("IP", 0.8, "R70.B", "U1.R8", (220, pxy("R70.B")[1]), (220, pxy("U1.R8")[1]))
    trp("DAC_VM", 0.75, "U1.R7", "U2.2")
    trp("DAC_VM", 0.65, "U2.1", "U2.2")
    trp("DAC_VM", 0.6, "R76.B", "U2.2")
    tr("VM", 0.8, pxy("U2.1"), (pxy("U2.1")[0], 2.2), (pxy("J2.4")[0], 2.2), pxy("J2.4"))
    tr("VM", 0.7, pxy("U3.3"), (pxy("U3.3")[0], 1.5), (pxy("J2.4")[0], 1.5), pxy("J2.4"))
    tr("UN", 0.8, pxy("J2.5"), (pxy("J2.5")[0], 1.2), (230, 1.2), (230, 70), (200, 70), (200, 66), pxy("R71.A"))
    trp("UN", 0.65, "R71.A", "C31.A")
    trp("UN", 0.65, "R78.A", "R71.A")
    trp("UN", 0.8, "R71.A", "U1.R10", (230, pxy("R71.A")[1]), (230, pxy("U1.R10")[1]))
    trp("RI", 0.7, "U1.R11", "R71.B", (234, pxy("U1.R11")[1]), (234, pxy("R71.B")[1]))

    # VBat sense: +12V_PROT -> R74 -> R75 -> PC1 (U1.L9)
    trp("VBAT_ADC", 0.7, "R74.A", "Q6.S")
    trp("VBAT_ADC", 0.65, "R74.B", "R75.A")
    trp("VBAT_ADC", 0.65, "R74.B", "C33.A")
    trp("VBAT_ADC", 0.8, "R75.B", "U1.L9", (108, pxy("R75.B")[1]), (108, pxy("U1.L9")[1]))

    # REF3033 -> VDDA / VREF (U1.L2)
    trp("VREF", 0.65, "U8.OUT", "U1.L2")
    trp("VREF", 0.6, "U8.GND", "U7.GND")

    trp("SWDIO", 0.65, "J3.2", "U1.R14")
    trp("SWCLK", 0.65, "J3.3", "U1.R15")

    # === POTÊNCIA por último (borda/topo) — o que cruzar vira jumper curto ===
    tr("+12V", 1.8, (70, 157), (200, 157))
    tr("+12V", 1.2, (66, 32), (148, 32))
    tr("+12V", 1.3, (148, 32), (148, 28), (162, 28), (162, 132), (70, 132), (70, 157))
    for p in ["D10.K", "D11.K", "D12.K", "D13.K", "D14.K"]:
        x, y = pxy(p)
        tr("+12V", 0.95, (x, y), (x, 32))
    tr("+5V", 1.2, (56, 142), (150, 142))
    tr("+3V3", 1.1, (72, 148), (120, 148))
    tr("+3V3", 1.0, (120, 148), (120, 155), (190, 155), (190, 136))
    tr("+3V3", 1.0, (168, 136), (195, 136))
    for p in ["D20.K", "D21.K", "D22.K"]:
        x, y = pxy(p)
        tr("+12V", 1.0, (x, y), (x, 125), (70, 125), (70, 157))
    x, y = pxy("Q6.S")
    tr("+12V", 1.1, (x, y), (x, 157), (70, 157))
    x, y = pxy("J2.1")
    tr("+12V", 1.1, (x, y), (x, 25), (162, 25), (162, 28))
    for p in ["U5.VCC", "U1.R1", "U6.OUT"]:
        x, y = pxy(p)
        tr("+5V", 0.9, (x, y), (x, 142))
    for p in ["C32.A", "U2.14"]:
        x, y = pxy(p)
        tr("+5V", 0.9, (x, y), (170, y), (170, 142), (150, 142))
    x, y = pxy("J1.6")
    tr("+5V", 0.95, (x, y), (4, y), (4, 142), (56, 142))
    for p in ["R40.A", "R41.A", "R42.A"]:
        x, y = pxy(p)
        tr("+3V3", 0.85, (x, y), (x, 136))
    for p in ["R62.A", "J3.1", "U1.L1", "U7.OUT"]:
        x, y = pxy(p)
        tr("+3V3", 0.85, (x, y), (x, 148))
    x, y = pxy("J1.7")
    tr("+3V3", 0.85, (x, y), (4, y), (4, 148), (72, 148))
    trp("+12VIN", 1.5, "J1.1", "Q6.D", (pxy("J1.1")[0], 7.0), (4, 7.0), (4, pxy("Q6.D")[1]))
    trp("+12VIN", 1.3, "J1.2", "Q6.D", (pxy("J1.2")[0], 7.5), (5.2, 7.5), (5.2, pxy("Q6.D")[1]))


def count_cross():
    S = []
    for pts, w, net in traces:
        for i in range(len(pts) - 1):
            S.append((pts[i], pts[i + 1], net, w))

    def ori(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def near(p, q, eps=0.15):
        return abs(p[0] - q[0]) < eps and abs(p[1] - q[1]) < eps

    def hit(a, b, c, d):
        # ignora se compartilham extremo (T-junction / continuação)
        if near(a, c) or near(a, d) or near(b, c) or near(b, d):
            return False
        o1, o2 = ori(a, b, c), ori(a, b, d)
        o3, o4 = ori(c, d, a), ori(c, d, b)
        return o1 * o2 < -1e-9 and o3 * o4 < -1e-9

    n = 0
    pairs = []
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            (a, b, n1, _), (c, d, n2, _) = S[i], S[j]
            if n1 == n2:
                continue
            if hit(a, b, c, d):
                n += 1
                pairs.append((n1, n2))
    return n, pairs


def draw_base(d, show_traces=True, show_jumpers=True, show_silk=True, show_boxes=True, pour_hint=False):
    def Y(y):
        return H - y

    def P(x, y):
        return px(x, Y(y))

    # fundo = pour GND
    d.rectangle([*px(0.3, 0.3), *px(W - 0.3, H - 0.3)], fill=(22, 70, 42), outline=(200, 210, 200), width=2)
    if pour_hint:
        d.text(P(100, 8), "GND POUR", fill=(40, 100, 60), font=font(3))
    if show_boxes:
        for x0, y0, x1, y1, t in boxes:
            d.rectangle([*P(x0, y1), *P(x1, y0)], outline=(140, 190, 150), width=1)
    if show_traces:
        for pts, w, net in traces:
            flat = []
            for x, y in pts:
                flat.extend(P(x, y))
            if len(flat) >= 4:
                col = {"+12V": (220, 45, 45), "+12VIN": (180, 30, 30),
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
    draw_base(ImageDraw.Draw(img), True, True, True, True, True)
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
    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MH_"):
            d.ellipse([*P(x - 1.8, y + 1.8), *P(x + 1.8, y - 1.8)], outline=(0, 0, 0), width=2)
            continue
        r = od / 2
        if drill > 0:
            d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], outline=(0, 0, 0), width=2)
            d.ellipse([*P(x - drill / 2, y + drill / 2), *P(x + drill / 2, y - drill / 2)],
                      fill=(255, 255, 255), outline=(0, 0, 0))
        else:
            d.rectangle([*P(x - r, y + r * 0.55), *P(x + r, y - r * 0.55)], fill=(70, 70, 70), outline=(0, 0, 0))
    for x, y, t, s in silk:
        d.text(P(x, y), t, fill=(0, 0, 0), font=font(s))
    d.text(P(8, 30), "MAPA MONTAGEM — furos THT + pads SMD (U3)", fill=(0, 0, 0), font=font(2.1))
    return img


def render_cnc(inv=False):
    """CNC: cobre = trilhas + pads. Fundo = isolado (ou invertido).
    Na fresagem real: deixar pour GND e isolar só ao redor das trilhas/sinal."""
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
        L.append(f'<circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{od / 2:.3f}"/>')
    L.append(f'</g><g fill="{bg}">')
    for name, (x, y, od, drill) in pads.items():
        if drill > 0:
            L.append(f'<circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{drill / 2:.3f}"/>')
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
        f"- Cruzamentos cobre (sinais/potência): **{cross}**",
        f"- Fios topo: **{nj}**",
        "- **GND = pour** (cobre de fundo). Pads GND soldam no pour; CNC isola só trilhas de sinal/potência.",
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
        "**Pinagem MCU:** PA4=DAC Vm · PA5=Ip · PA6=Un · PC1=VBat",
        "",
        "### J2 PCIe-6",
        "1:H+ · 2:H− · 3:IP · 4:VM · 5:UN · 6:NC",
        "",
        "### J3 SWD",
        "1:+3V3 · 2:SWDIO · 3:SWCLK · 4:GND",
        "",
        "## Arquivos",
        "",
        "| Arquivo | Uso |",
        "|---|---|",
        "| `assets/ecu-pcb-1layer-pads-map.png` | Montagem: só furos THT + pads SMD + códigos |",
        "| `assets/ecu-pcb-1layer-assembly.png` | Visão com trilhas (sem tarja) |",
        "| `assets/ecu-pcb-1layer-traces-cnc.svg` | Máscara CNC |",
        "",
    ]
    (DOC / "pcb-bom-codigos.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    print("Routing v8 (GND pour + manual)…")
    route_all()
    cross, pairs = count_cross()
    print(f"cross={cross} traces={len(traces)} jumpers={len(jumpers)} bom={len(bom)}")
    if pairs:
        from collections import Counter
        print("top crossings:", Counter(pairs).most_common(12))

    render_assembly().save(OUT / "ecu-pcb-1layer-assembly.png", dpi=(DPI, DPI))
    render_pads_map().save(OUT / "ecu-pcb-1layer-pads-map.png", dpi=(DPI, DPI))
    render_cnc(False).save(OUT / "ecu-pcb-1layer-traces-cnc.png", dpi=(DPI, DPI))
    render_cnc(True).save(OUT / "ecu-pcb-1layer-traces-cnc-invert.png", dpi=(DPI, DPI))
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc.svg")
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc-invert.svg", True)
    write_bom(cross, len(jumpers))
    extra = ""
    if pairs:
        from collections import Counter
        extra = "\n## Cruzamentos\n\n" + "\n".join(f"- `{a}` × `{b}`" for (a, b), _ in Counter(pairs).most_common(30))
    (OUT / "ecu-pcb-1layer-drc.md").write_text(
        f"# DRC\n\n- Cruzamentos cobre: **{cross}**\n- Trilhas CNC: {len(traces)}\n"
        f"- Fios topo (AWG28 pad–pad): **{len(jumpers)}**\n- Placa: {W}×{H} mm\n"
        f"- GND: **pour** (sem fio de terra)\n\nSem tarja nas imagens.\n\n"
        + ("## Fios topo\n\n" + "\n".join(f"- `{n}`" for *_, n in jumpers) if jumpers else "Zero fios topo.\n"),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
