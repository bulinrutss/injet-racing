# -*- coding: utf-8 -*-
"""
INJET RACING ECU — 1-LAYER SEM CURTO (método fenolite)

COBRE (CNC):
  - Faixa GND embaixo, +12V em cima
  - Faixas +5V/+3V3 verticais na direita
  - Ligações LOCAIS curtas dentro de cada módulo

FIO TOPO (branco na assembly — NÃO vai na CNC):
  - Tudo entre módulos / conector / MCU / taps nos barramentos

Assim o cobre NÃO se cruza → zero curto.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"e:\injet racing\assets")
W, H = 200.0, 100.0
PPM = 12.0
DPI = int(25.4 * PPM)

pads, outlines, traces, wires, segs = {}, [], [], [], []
YGND, Y12, X5, X33 = 3.0, 97.0, 193.0, 189.0


def font(mm):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", max(9, int(mm * PPM)))
    except OSError:
        return ImageFont.load_default()


def px(*a):
    return tuple(int(round(v * PPM)) for v in a)


def pad(n, x, y, od=1.9, drill=0.95):
    pads[n] = (x, y, od, drill)


def axial(a, b, x1, y1, x2, y2, od=1.7, dr=0.85):
    pad(a, x1, y1, od, dr)
    pad(b, x2, y2, od, dr)


def to220(p, x, y):
    pad(f"{p}.G", x - 2.54, y, 2.3, 1.1)
    pad(f"{p}.D", x, y, 2.3, 1.1)
    pad(f"{p}.S", x + 2.54, y, 2.3, 1.1)
    outlines.append((x - 5, y - 1, x + 5, y + 10, p, "top"))


def to92(p, x, y):
    pad(f"{p}.S", x - 1.27, y, 1.6, 0.8)
    pad(f"{p}.G", x, y + 1.8, 1.6, 0.8)
    pad(f"{p}.D", x + 1.27, y, 1.6, 0.8)
    outlines.append((x - 3, y - 1, x + 3, y + 5, p, "top"))


def dip(p, x0, y0, n, pitch=2.54, row=7.62):
    h = n // 2
    for i in range(h):
        pad(f"{p}.{i+1}", x0, y0 + i * pitch, 1.7, 0.85)
        pad(f"{p}.{n-i}", x0 + row, y0 + i * pitch, 1.7, 0.85)
    outlines.append((x0 - 1, y0 - 1, x0 + row + 1, y0 + (h - 1) * pitch + 1, p, "top"))


def soic8(p, x0, y0):
    for i in range(4):
        pad(f"{p}.{i+1}", x0, y0 + i * 1.27, 1.3, 0.0)
        pad(f"{p}.{8-i}", x0 + 5.4, y0 + i * 1.27, 1.3, 0.0)
    outlines.append((x0 - 1, y0 - 1, x0 + 6.4, y0 + 4.8, p + " SMD↓", "bot"))


def overlap(a1, a2, b1, b2, g):
    return not (max(a1, a2) + g < min(b1, b2) or max(b1, b2) + g < min(a1, a2))


def conflict(x1, y1, x2, y2, net, w):
    g = w / 2 + 0.5
    h = abs(y1 - y2) < 0.05
    for ox1, oy1, ox2, oy2, on in segs:
        if on == net:
            continue
        oh = abs(oy1 - oy2) < 0.05
        if h and oh and abs(y1 - oy1) < g and overlap(x1, x2, ox1, ox2, g):
            return True
        if (not h) and (not oh) and abs(x1 - ox1) < g and overlap(y1, y2, oy1, oy2, g):
            return True
        if h and not oh:
            if min(x1, x2) - g <= ox1 <= max(x1, x2) + g and min(oy1, oy2) - g <= y1 <= max(oy1, oy2) + g:
                return True
        if (not h) and oh:
            if min(y1, y2) - g <= oy1 <= max(y1, y2) + g and min(ox1, ox2) - g <= x1 <= max(ox1, ox2) + g:
                return True
    return False


def copper(pts, net, w):
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        if abs(a[0] - b[0]) < 0.01 and abs(a[1] - b[1]) < 0.01:
            continue
        if conflict(a[0], a[1], b[0], b[1], net, w):
            return False
    for i in range(len(pts) - 1):
        segs.append((pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], net))
    traces.append((pts, w, net))
    return True


def local(net, a, b, w=0.85):
    if a not in pads or b not in pads:
        return False
    ax, ay = pads[a][0], pads[a][1]
    bx, by = pads[b][0], pads[b][1]
    if abs(ax - bx) + abs(ay - by) > 16:
        wire(net, a, b)
        return False
    for pts in ([(ax, ay), (bx, ay), (bx, by)], [(ax, ay), (ax, by), (bx, by)]):
        if copper(pts, net, w):
            return True
    wire(net, a, b)
    return False


def wire(net, a, b):
    if a in pads and b in pads:
        ax, ay = pads[a][0], pads[a][1]
        bx, by = pads[b][0], pads[b][1]
        wires.append((ax, ay, bx, by, net))


def tap(net, p, x_or_y, axis="y"):
    """Fio curto do pad até o barramento (solda no cobre do bus)."""
    if p not in pads:
        return
    x, y = pads[p][0], pads[p][1]
    if axis == "y":
        wires.append((x, y, x, x_or_y, net + "→BUS"))
    else:
        wires.append((x, y, x_or_y, y, net + "→BUS"))


# ========== PLACE ==========
ATX = 4.2
for i in range(12):
    pad(f"CN1.{i+1}", 6 + i * ATX, 11, 2.2, 1.1)
    pad(f"CN1.{i+13}", 6 + i * ATX, 6, 2.2, 1.1)
outlines.append((3, 3.5, 58, 14, "CN1 ATX-24", "top"))
for i in range(3):
    pad(f"CN2.{i+1}", 168 + i * ATX, 11, 2.2, 1.1)
    pad(f"CN2.{i+4}", 168 + i * ATX, 6, 2.2, 1.1)
outlines.append((165, 3.5, 185, 14, "CN2 PCIe-6", "top"))

to220("QREV", 14, 90)
axial("CBULK.A", "CBULK.K", 26, 92, 34, 92, 2.4, 0.9)
axial("CIN.A", "CIN.K", 26, 86, 30, 86)
axial("TVS.A", "TVS.K", 38, 92, 38, 86)
axial("RG.A", "RG.B", 8, 84, 8, 78)
axial("DZ.A", "DZ.K", 12, 84, 12, 78)
pad("BUCK.VIN", 46, 92)
pad("BUCK.GND", 52, 92)
pad("BUCK.OUT", 46, 84)
pad("LDO.IN", 58, 92)
pad("LDO.GND", 64, 92)
pad("LDO.OUT", 61, 84)
axial("C5.A", "C5.B", 68, 92, 72, 92)
axial("C33.A", "C33.B", 68, 86, 72, 86)
outlines.append((5, 76, 74, 96, "POWER", "top"))

for i, x in enumerate([84, 98, 112, 126]):
    to220(f"Q{i+1}", x, 90)
    axial(f"Rg{i+1}.A", f"Rg{i+1}.B", x - 2.54, 82, x - 2.54, 76)
    axial(f"Rgs{i+1}.A", f"Rgs{i+1}.B", x - 2.54, 74, x, 74)
    axial(f"Df{i+1}.A", f"Df{i+1}.K", x + 5, 90, x + 5, 84)
to220("QH", 146, 90)
axial("Rgh.A", "Rgh.B", 143.46, 82, 143.46, 76)
axial("Rgsh.A", "Rgsh.B", 143.46, 74, 148, 74)
outlines.append((78, 72, 158, 96, "INJ+HEAT", "top"))

for i, x in enumerate([10, 20, 30]):
    to92(f"QR{i+1}", x, 58)
    axial(f"Rr{i+1}.A", f"Rr{i+1}.B", x, 52, x, 46)
    axial(f"Dr{i+1}.A", f"Dr{i+1}.K", x + 4, 58, x + 4, 52)
outlines.append((5, 44, 38, 66, "RELAY", "top"))

for i in range(20):
    pad(f"ML{i+1}", 70, 66 - i * 2.54, 1.6, 0.9)
    pad(f"MR{i+1}", 122, 66 - i * 2.54, 1.6, 0.9)
outlines.append((68, 14, 124, 68, "STM32F407", "top"))
for i in range(4):
    pad(f"SWD.{i+1}", 88 + i * 2.54, 18, 1.7, 0.95)

for n, y in [("IAT", 64), ("CLT", 56), ("MAP", 48), ("TPS", 40)]:
    if n != "TPS":
        axial(f"R{n}.A", f"R{n}.B", 138, y, 146, y)
    if n == "MAP":
        axial("Rm2.A", "Rm2.B", 146, y, 146, y - 4)
    axial(f"C{n}.A", f"C{n}.B", 150, y, 150, y - 3.5)
    axial(f"S{n}.A", f"S{n}.B", 154, y, 162, y)
outlines.append((136, 34, 166, 68, "SENS", "top"))

dip("U817", 44, 26, 4)
axial("Rra.A", "Rra.B", 34, 30, 42, 30)
axial("Rrb.A", "Rrb.B", 26, 30, 34, 30)
axial("Drpm.A", "Drpm.K", 38, 26, 38, 21)
axial("Rrp.A", "Rrp.B", 54, 34, 54, 28)
axial("Cr.A", "Cr.B", 58, 28, 58, 23)
outlines.append((24, 18, 62, 38, "RPM", "top"))

for i, nm in enumerate(["CV", "CG", "CT", "CR", "CH", "CL"]):
    pad(f"CAN.{nm}", 88 + (i % 3) * 6, 34 - (i // 3) * 6, 1.8, 1.0)
outlines.append((86, 26, 108, 38, "CAN", "top"))

dip("U6", 128, 16, 14)
soic8("U8", 152, 18)
axial("Rsh.A", "Rsh.B", 148, 32, 156, 32)
axial("Res.A", "Res.B", 148, 38, 156, 38)
axial("Cip.A", "Cip.B", 160, 32, 160, 27)
axial("Cun.A", "Cun.B", 164, 38, 164, 33)
axial("C5a.A", "C5a.B", 124, 24, 124, 19)
axial("Ro1.A", "Ro1.B", 136, 24, 144, 24)
axial("Ro2.A", "Ro2.B", 144, 24, 144, 19)
outlines.append((122, 12, 170, 42, "LAMBDA", "top"))


def route():
    # Barramentos cobre (não se cruzam: H nas bordas + V na direita)
    copper([(4, YGND), (186, YGND)], "GND", 2.5)
    copper([(4, Y12), (186, Y12)], "+12VP", 2.2)
    copper([(X5, 16), (X5, 92)], "+5V", 1.4)
    copper([(X33, 16), (X33, 92)], "+3V3", 1.3)

    # POWER local
    local("QG", "QREV.G", "RG.A")
    local("QG", "QREV.G", "DZ.A")
    local("GND", "RG.B", "DZ.K")
    local("+12VP", "QREV.S", "CBULK.A")
    local("GND", "CBULK.K", "CIN.K")
    local("+12VP", "CIN.A", "TVS.A")
    local("GND", "TVS.K", "CBULK.K")
    local("+12VP", "BUCK.VIN", "QREV.S")
    local("GND", "BUCK.GND", "LDO.GND")
    local("+5V", "BUCK.OUT", "LDO.IN")
    local("+5V", "LDO.IN", "C5.A")
    local("GND", "C5.B", "C33.B")
    local("+3V3", "LDO.OUT", "C33.A")

    for i in range(1, 5):
        local(f"INJ{i}", f"Df{i}.A", f"Q{i}.D")
        local(f"GI{i}", f"Rg{i}.A", f"Q{i}.G")
        local(f"GI{i}", f"Rgs{i}.A", f"Q{i}.G")
        local("GND", f"Rgs{i}.B", f"Q{i}.S")
        if i > 1:
            local("GND", f"Q{i}.S", f"Q{i-1}.S")
            local("+12VP", f"Df{i}.K", f"Df{i-1}.K")
        else:
            local("+12VP", "Df1.K", "QREV.S")
            local("GND", "Q1.S", "BUCK.GND")

    local("GH", "Rgh.A", "QH.G")
    local("GH", "Rgsh.A", "QH.G")
    local("GND", "Rgsh.B", "QH.S")
    local("GND", "QH.S", "Q4.S")
    local("+12VP", "Df4.K", "Df3.K")

    for i in range(1, 4):
        local(f"RL{i}", f"Dr{i}.A", f"QR{i}.D")
        local(f"GR{i}", f"Rr{i}.A", f"QR{i}.G")
        local("GND", f"QR{i}.S", "BUCK.GND")
        local("+12VP", f"Dr{i}.K", "QREV.S")

    for n in ("IAT", "CLT"):
        local(n, f"R{n}.B", f"C{n}.A")
        local(n, f"R{n}.B", f"S{n}.A")
        local("GND", f"C{n}.B", "C33.B")
    local("MAP", "RMAP.B", "Rm2.A")
    local("MAP", "RMAP.B", "CMAP.A")
    local("MAP", "RMAP.B", "SMAP.A")
    local("GND", "Rm2.B", "CMAP.B")
    local("TPS", "STPS.A", "CTPS.A")
    local("GND", "CTPS.B", "CMAP.B")
    local("+3V3", "RIAT.A", "RCLT.A")

    local("RPMi", "Rrb.B", "Rra.A")
    local("RPMi", "Rra.B", "U817.1")
    local("GND", "U817.2", "U817.3")
    local("RPMi", "Drpm.A", "U817.1")
    local("RPMi", "Drpm.K", "U817.2")
    local("RPMo", "U817.4", "Rrp.B")
    local("RPMo", "U817.4", "Cr.A")
    local("GND", "Cr.B", "U817.3")
    local("+3V3", "Rrp.A", "RIAT.A")
    local("GND", "CAN.CG", "Cr.B")
    local("+3V3", "CAN.CV", "Rrp.A")

    local("+5V", "U6.14", "C5a.A")
    local("GND", "U6.4", "C5a.B")
    local("+5V", "U8.8", "U6.14")
    local("GND", "U8.4", "U6.4")
    local("IP", "Rsh.A", "Cip.A")
    local("IP", "U8.6", "Rsh.A")
    local("IP", "U8.2", "Rsh.A")
    local("UN", "Res.A", "Cun.A")
    local("VM", "U6.1", "U6.2")
    local("O2", "U6.7", "Ro1.A")
    local("O2", "Ro1.B", "Ro2.A")
    local("GND", "Ro2.B", "U6.4")
    local("GND", "Cip.B", "Cun.B")

    # Taps barramento = fio topo
    for n in ["CN1.3", "CN1.4", "CN1.5", "CN1.24", "CBULK.K", "BUCK.GND", "Q1.S", "QH.S",
              "QR1.S", "ML2", "MR2", "SWD.4", "U817.3", "CAN.CG", "U6.4", "CTPS.B"]:
        tap("GND", n, YGND, "y")
    for n in ["QREV.S", "BUCK.VIN", "Df1.K", "Df2.K", "Df3.K", "Df4.K", "Dr1.K", "Dr2.K", "Dr3.K", "CN2.1"]:
        tap("+12VP", n, Y12, "y")
    for n in ["BUCK.OUT", "CN1.6", "MR1", "C5a.A", "U6.14"]:
        tap("+5V", n, X5, "x")
    for n in ["LDO.OUT", "CN1.7", "ML1", "SWD.1", "RIAT.A", "CAN.CV"]:
        tap("+3V3", n, X33, "x")

    # Interligação módulos = fio topo
    wire("+12VIN", "CN1.1", "QREV.D")
    wire("+12VIN", "CN1.2", "QREV.D")
    for i, cn in enumerate([13, 14, 15, 16], 1):
        wire(f"INJ{i}", f"Q{i}.D", f"CN1.{cn}")
        wire(f"GI{i}", f"ML{12+i}", f"Rg{i}.B")
    wire("GH", "ML20", "Rgh.B")
    wire("H-", "QH.D", "CN2.2")
    for i, cn in {1: 18, 2: 17, 3: 19}.items():
        wire(f"RL{i}", f"QR{i}.D", f"CN1.{cn}")
        wire(f"GR{i}", f"ML{16+i}", f"Rr{i}.B")
    wire("IAT", "CN1.8", "RIAT.B")
    wire("IAT", "SIAT.B", "ML3")
    wire("CLT", "CN1.9", "RCLT.B")
    wire("CLT", "SCLT.B", "ML4")
    wire("MAP", "CN1.10", "RMAP.A")
    wire("MAP", "SMAP.B", "ML5")
    wire("TPS", "CN1.11", "STPS.A")
    wire("TPS", "STPS.B", "ML6")
    wire("RPMi", "CN1.12", "Rrb.A")
    wire("RPMo", "U817.4", "ML10")
    wire("CANTX", "ML12", "CAN.CT")
    wire("CANRX", "ML11", "CAN.CR")
    wire("CANH", "CAN.CH", "CN1.20")
    wire("CANL", "CAN.CL", "CN1.21")
    wire("IP", "CN2.3", "Rsh.A")
    wire("IP", "Rsh.B", "ML8")
    wire("VM", "MR3", "U6.3")
    wire("VM", "U6.1", "CN2.4")
    wire("VM", "U8.3", "CN2.4")
    wire("UN", "CN2.5", "Res.A")
    wire("UN", "Res.A", "ML9")
    wire("RI", "MR8", "Res.B")
    wire("O2", "Ro1.B", "ML7")
    wire("SWDIO", "SWD.2", "MR4")
    wire("SWCLK", "SWD.3", "MR5")


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


def render():
    img = Image.new("RGB", px(W, H), (12, 16, 20))
    d = ImageDraw.Draw(img)

    def Y(y):
        return H - y

    def P(x, y):
        return px(x, Y(y))

    d.rectangle([*px(0.4, 0.4), *px(W - 0.4, H - 0.4)], fill=(16, 72, 44), outline=(210, 220, 210), width=2)
    for x0, y0, x1, y1, lab, side in outlines:
        col = (255, 170, 60) if side == "bot" else (150, 205, 160)
        d.rectangle([*P(x0, y1), *P(x1, y0)], outline=col, width=2)
        d.text(P(x0 + 0.3, y1 - 0.2), lab, fill=col, font=font(1.7))

    for pts, w, net in traces:
        flat = []
        for x, y in pts:
            flat.extend(P(x, y))
        if len(flat) >= 4:
            color = {"GND": (45, 45, 45), "+12VP": (230, 40, 40), "+5V": (220, 140, 40), "+3V3": (50, 130, 220)}.get(net, (220, 190, 60))
            d.line(flat, fill=color, width=max(2, int(w * PPM)))

    for x1, y1, x2, y2, net in wires:
        d.line([*P(x1, y1), *P(x2, y2)], fill=(255, 255, 255), width=2)

    for name, (x, y, od, drill) in pads.items():
        r = od / 2
        fill = (215, 180, 55) if drill > 0 else (190, 110, 230)
        d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], fill=fill, outline=(80, 60, 20))
        if drill > 0:
            d.ellipse([*P(x - drill / 2, y + drill / 2), *P(x + drill / 2, y - drill / 2)], fill=(12, 16, 20))

    for x, y in [(4, 4), (196, 4), (4, 96), (196, 96)]:
        d.ellipse([*P(x - 1.6, y + 1.6), *P(x + 1.6, y - 1.6)], outline=(240, 240, 240), width=2)

    cross = count_cross()
    d.rectangle([*px(1, 1), *px(199, 12)], fill=(8, 10, 14))
    d.text(px(3, 2), "1-LAYER CORRETO: cobre sem curto | branco = fio TOPO (nao e cobre)", fill=(240, 245, 240), font=font(2.2))
    d.text(px(3, 6), f"Cruzamentos COBRE={cross}  Trilhas CNC={len(traces)}  Fios para soldar={len(wires)}",
           fill=(140, 255, 160) if cross == 0 else (255, 80, 80), font=font(2.0))
    d.text(px(3, 9), "CNC = so arquivo traces. Monte os fios brancos pad a pad (AWG28).", fill=(180, 180, 180), font=font(1.6))
    return img, cross


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
        r = od / 2
        d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], fill=cu)
        if drill > 0:
            d.ellipse([*P(x - drill / 2, y + drill / 2), *P(x + drill / 2, y - drill / 2)], fill=bg)
    for x, y in [(4, 4), (196, 4), (4, 96), (196, 96)]:
        d.ellipse([*P(x - 1.6, y + 1.6), *P(x + 1.6, y - 1.6)], fill=bg)
    return img


def write_svg(path, inv=False):
    cu, bg = ("#000", "#FFF") if not inv else ("#FFF", "#000")

    def Y(y):
        return H - y

    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{bg}"/>',
         '<!-- COPPER ONLY — top wires NOT included -->',
         f'<g fill="{cu}" stroke="{cu}" stroke-linecap="round" stroke-linejoin="round">']
    for pts, w, net in traces:
        dd = "M " + " L ".join(f"{x:.3f},{Y(y):.3f}" for x, y in pts)
        L.append(f'<path d="{dd}" fill="none" stroke-width="{w:.3f}" data-net="{net}"/>')
    for name, (x, y, od, drill) in pads.items():
        L.append(f'<circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{od/2:.3f}"/>')
    L.append("</g>")
    L.append(f'<g fill="{bg}">')
    for name, (x, y, od, drill) in pads.items():
        if drill > 0:
            L.append(f'<circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{drill/2:.3f}"/>')
    for x, y in [(4, 4), (196, 4), (4, 96), (196, 96)]:
        L.append(f'<circle cx="{x}" cy="{Y(y)}" r="1.6"/>')
    L.append("</g></svg>")
    path.write_text("\n".join(L), encoding="utf-8")


def main():
    route()
    img, cross = render()
    img.save(OUT / "ecu-pcb-1layer-assembly.png", dpi=(DPI, DPI))
    render_cnc(False).save(OUT / "ecu-pcb-1layer-traces-cnc.png", dpi=(DPI, DPI))
    render_cnc(True).save(OUT / "ecu-pcb-1layer-traces-cnc-invert.png", dpi=(DPI, DPI))
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc.svg")
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc-invert.svg", True)
    (OUT / "ecu-pcb-1layer-drc.md").write_text(
        f"# DRC 1-layer\n\n- Cruzamentos cobre: **{cross}** {'OK' if cross == 0 else 'ERRO'}\n"
        f"- Trilhas CNC: {len(traces)}\n- Fios TOPO: {len(wires)}\n\n"
        "## Por que tem fio branco?\n\n"
        "Em **1 layer** nao da para passar sinal por cima de outro sinal no cobre sem curto.\n"
        "Padrao fenolite DIY: cobre = power/GND + ligacoes locais; **fio fino no topo** entre modulos.\n\n"
        "## Fios para soldar\n\n" + "\n".join(f"- `{n}`" for *_, n in wires),
        encoding="utf-8",
    )
    print(f"cross={cross} copper={len(traces)} wires={len(wires)}")


if __name__ == "__main__":
    main()
