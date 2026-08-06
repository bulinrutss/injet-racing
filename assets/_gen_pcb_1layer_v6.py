# -*- coding: utf-8 -*-
"""
INJET RACING ECU — 1-layer CNC, mínimo/zero fio externo.
Estratégia: canais de roteamento + sinais primeiro (curtos) + pour GND.
Sem tarja preta. Silk com códigos. Mapa só de furos/pads.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"e:\injet racing\assets")
DOC = Path(r"e:\injet racing\modulo")
W, H = 240.0, 160.0  # folga extra para planar
PPM = 9.0
DPI = int(25.4 * PPM)
GRID = 1.0  # 1 mm — rápido o bastante p/ autoroute
CLR = 1  # cells of clearance beyond half-width

pads: dict[str, tuple[float, float, float, float]] = {}
silk: list[tuple[float, float, str, float]] = []
boxes: list[tuple] = []
traces: list[tuple] = []
jumpers: list[tuple] = []
bom: list[tuple[str, str, str]] = []
pad_net: dict[str, str] = {}  # pad -> preferred net (for pour check)

gw, gh = int(W / GRID) + 1, int(H / GRID) + 1
occ: list[list[str | None]] = [[None] * gw for _ in range(gh)]


def font(mm):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", max(7, int(mm * PPM)))
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
    label(x, y + 7, code, 2.0)
    box(x - 5, y - 1, x + 5, y + 10, code)


def to92(code, x, y):
    pad(f"{code}.S", x - 1.27, y, 1.5, 0.8)
    pad(f"{code}.G", x, y + 1.8, 1.5, 0.8)
    pad(f"{code}.D", x + 1.27, y, 1.5, 0.8)
    label(x, y + 5, code, 1.6)


def dip(code, x0, y0, n, pitch=2.54, row=7.62):
    h = n // 2
    for i in range(h):
        pad(f"{code}.{i+1}", x0, y0 + i * pitch, 1.6, 0.85)
        pad(f"{code}.{n-i}", x0 + row, y0 + i * pitch, 1.6, 0.85)
    label(x0 + row / 2, y0 + (h - 1) * pitch + 3, code, 1.9)
    box(x0 - 1, y0 - 1, x0 + row + 1, y0 + (h - 1) * pitch + 1, code)


def soic8(code, x0, y0):
    for i in range(4):
        pad(f"{code}.{i+1}", x0, y0 + i * 1.27, 1.2, 0.0)
        pad(f"{code}.{8-i}", x0 + 5.4, y0 + i * 1.27, 1.2, 0.0)
    label(x0 + 2.7, y0 - 2.2, code + " SMD", 1.5)
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
                if 0 <= xx < gw and 0 <= yy < gh and occ[yy][xx] in (None, net):
                    occ[yy][xx] = net


def block_holes():
    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MH_"):
            mark(x, y, 2.2, "__HOLE__")


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


def bfs(a, b, net, w, limit=50000):
    from collections import deque

    sx, sy = cell(*a)
    gx, gy = cell(*b)
    half = max(0, int(round((w / 2) / GRID)))
    q = deque([(sx, sy)])
    came = {(sx, sy): None}
    n = 0
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
        n += 1
        if n > limit:
            return None
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in came or not (0 <= nx < gw and 0 <= ny < gh):
                continue
            if (nx, ny) != (gx, gy) and not can(nx, ny, net, half):
                continue
            came[(nx, ny)] = (cx, cy)
            q.append((nx, ny))
    return None


def route_via_waypoints(net, ax, ay, bx, by, w, waypoints):
    pts = [(ax, ay)] + list(waypoints) + [(bx, by)]
    halves = max(0, int(round((w / 2) / GRID)))
    full = []
    painted = []
    for i in range(len(pts) - 1):
        seg = bfs(pts[i], pts[i + 1], net, w, limit=25000)
        if not seg:
            for xx, yy in painted:
                if occ[yy][xx] == net:
                    occ[yy][xx] = None
            return None
        chunk = seg if i == 0 else seg[1:]
        full.extend(chunk)
        for cx, cy in chunk:
            for dy in range(-halves, halves + 1):
                for dx in range(-halves, halves + 1):
                    xx, yy = cx + dx, cy + dy
                    if 0 <= xx < gw and 0 <= yy < gh and occ[yy][xx] is None:
                        occ[yy][xx] = net
                        painted.append((xx, yy))
                    elif not (0 <= xx < gw and 0 <= yy < gh) or occ[yy][xx] not in (None, net):
                        for px_, py_ in painted:
                            if occ[py_][px_] == net:
                                occ[py_][px_] = None
                        return None
    traces.append(([xy(*c) for c in simplify(full)], w, net))
    return full


def route_pts(net, ax, ay, bx, by, w=0.8, via=None):
    mark(ax, ay, 0.8, net)
    mark(bx, by, 0.8, net)
    path = bfs((ax, ay), (bx, by), net, w)
    if path is None:
        midy = 22.0 if min(ay, by) < 40 else (68.0 if max(ay, by) < 120 else 122.0)
        for wps in (
            [((ax + bx) / 2, ay), ((ax + bx) / 2, by)],
            [(ax, midy), (bx, midy)],
            [(80.0, ay), (80.0, by)],
            [(148.0, ay), (148.0, by)],
        ):
            if route_via_waypoints(net, ax, ay, bx, by, w, wps) is not None:
                return True
        jumpers.append((ax, ay, bx, by, net))
        return False
    half = max(0, int(round((w / 2) / GRID)))
    paint(path, net, half)
    traces.append(([xy(*c) for c in simplify(path)], w, net))
    return True


def route(net, pa, pb, w=0.8):
    if pa not in pads or pb not in pads:
        return False
    pad_net[pa] = net
    pad_net[pb] = net
    ax, ay = pads[pa][0], pads[pa][1]
    bx, by = pads[pb][0], pads[pb][1]
    mark(ax, ay, pads[pa][2] / 2, net)
    mark(bx, by, pads[pb][2] / 2, net)
    return route_pts(net, ax, ay, bx, by, w)


def bus_h(net, y, w, x1=4, x2=None):
    if x2 is None:
        x2 = W - 4
    half = max(0, int(round((w / 2) / GRID)))
    y0 = int(round(y / GRID))
    cells = [(x, y0) for x in range(int(round(x1 / GRID)), int(round(x2 / GRID)) + 1)]
    paint(cells, net, half)
    traces.append(([(x1, y), (x2, y)], w, net))


def bus_v(net, x, w, y1, y2):
    half = max(0, int(round((w / 2) / GRID)))
    x0 = int(round(x / GRID))
    cells = [(x0, y) for y in range(int(round(y1 / GRID)), int(round(y2 / GRID)) + 1)]
    paint(cells, net, half)
    traces.append(([(x, y1), (x, y2)], w, net))


def stub_to_bus(net, p, bus_y=None, bus_x=None, w=1.0):
    if p not in pads:
        return False
    pad_net[p] = net
    x, y = pads[p][0], pads[p][1]
    mark(x, y, pads[p][2] / 2, net)
    half = max(0, int(round((w / 2) / GRID)))
    if bus_y is not None:
        mark(x, bus_y, w / 2, net)
        # trilha vertical direta se livre
        y0, y1 = (y, bus_y) if y < bus_y else (bus_y, y)
        cx = int(round(x / GRID))
        cells = []
        blocked = False
        for yy in range(int(round(y0 / GRID)), int(round(y1 / GRID)) + 1):
            if not can(cx, yy, net, half) and occ[yy][cx] != net:
                blocked = True
                break
            cells.append((cx, yy))
        if not blocked and cells:
            paint(cells, net, half)
            traces.append(([(x, y), (x, bus_y)], w, net))
            return True
        return route_pts(net, x, y, x, bus_y, w)
    if bus_x is not None:
        mark(bus_x, y, w / 2, net)
        return route_pts(net, x, y, bus_x, y, w)
    return False


def flood_gnd():
    """After signal routing, flood free copper as GND pour from bottom bus."""
    # seed from existing GND cells
    seeds = []
    for y in range(gh):
        for x in range(gw):
            if occ[y][x] == "GND":
                seeds.append((x, y))
    from collections import deque
    q = deque(seeds)
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < gw and 0 <= ny < gh and occ[ny][nx] is None:
                occ[ny][nx] = "GND"
                q.append((nx, ny))


def connect_gnd_pads():
    """Ensure every pad assigned GND touches pour; else stub/jumper."""
    for p, net in list(pad_net.items()):
        if net != "GND" or p not in pads:
            continue
        x, y = pads[p][0], pads[p][1]
        cx, cy = cell(x, y)
        # if already on GND, ok
        ok = False
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                xx, yy = cx + dx, cy + dy
                if 0 <= xx < gw and 0 <= yy < gh and occ[yy][xx] == "GND":
                    ok = True
        if ok:
            mark(x, y, pads[p][2] / 2, "GND")
            continue
        # try stub to nearest GND cell (search)
        from collections import deque
        q = deque([(cx, cy)])
        came = {(cx, cy): None}
        found = None
        while q and found is None:
            ux, uy = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = ux + dx, uy + dy
                if (nx, ny) in came or not (0 <= nx < gw and 0 <= ny < gh):
                    continue
                o = occ[ny][nx]
                if o == "GND":
                    came[(nx, ny)] = (ux, uy)
                    found = (nx, ny)
                    break
                if o is None:
                    came[(nx, ny)] = (ux, uy)
                    q.append((nx, ny))
        if found:
            path = []
            cur = found
            while cur:
                path.append(cur)
                cur = came[cur]
            path.reverse()
            paint(path, "GND", 1)
            traces.append(([xy(*c) for c in simplify(path)], 1.0, "GND"))
            mark(x, y, pads[p][2] / 2, "GND")
        else:
            jumpers.append((x, y, x, 3.0, "GND"))


# ========== PLACE — módulos + canais livres ==========
# Canais H: y≈20 (conn), y≈66 (mid), y≈118 (driver bottom)
# Canais V: x≈66, x≈136, x≈200

ATX = 4.0
# J1 bottom-left
for i in range(12):
    pad(f"J1.{i+1}", 10 + i * ATX, 16, 2.2, 1.1)
    pad(f"J1.{i+13}", 10 + i * ATX, 10, 2.2, 1.1)
label(34, 5, "J1 ATX-24", 2.2)
box(7, 7, 62, 20, "J1")
add_bom("J1", "ATX-24 header", "Conector principal chicote")

# J2 bottom-right
for i in range(3):
    pad(f"J2.{i+1}", 200 + i * ATX, 16, 2.2, 1.1)
    pad(f"J2.{i+4}", 200 + i * ATX, 10, 2.2, 1.1)
label(206, 5, "J2 PCIe-6", 2.0)
box(197, 7, 220, 20, "J2")
add_bom("J2", "PCIe-6 header", "Conector lambda LSU 4.2")

# POWER top-left
to220("Q6", 18, 148)
add_bom("Q6", "IRF9540", "MOSFET-P proteção reversa")
axial("C1.A", "C1.B", 30, 150, 38, 150, 2.4, 0.9)
label(34, 154, "C1", 1.5)
add_bom("C1", "220u/50V", "Bulk entrada")
axial("C2.A", "C2.B", 30, 144, 34, 144)
label(32, 140, "C2", 1.4)
add_bom("C2", "100n/100V", "Cerâmico entrada")
axial("D1.A", "D1.K", 42, 150, 42, 144)
label(45, 147, "D1", 1.4)
add_bom("D1", "P6KE33A/SMBJ33A", "TVS load dump")
axial("R1.A", "R1.B", 12, 140, 12, 134)
label(9, 137, "R1", 1.4)
add_bom("R1", "100k", "Gate Q6")
axial("D2.A", "D2.K", 16, 140, 16, 134)
label(19, 137, "D2", 1.4)
add_bom("D2", "Zener 12V", "Proteção gate Q6")
pad("U6.VIN", 52, 150)
pad("U6.GND", 58, 150)
pad("U6.OUT", 52, 142)
label(55, 154, "U6", 1.6)
box(50, 140, 60, 154, "U6")
add_bom("U6", "MP1584 módulo", "Buck 5V")
pad("U7.IN", 66, 150)
pad("U7.GND", 72, 150)
pad("U7.OUT", 69, 142)
label(69, 154, "U7", 1.6)
box(64, 140, 76, 154, "U7")
add_bom("U7", "AMS1117-3.3", "LDO 3V3")
axial("C3.A", "C3.B", 78, 150, 82, 150)
label(80, 154, "C3", 1.4)
add_bom("C3", "10u", "LDO in")
axial("C4.A", "C4.B", 78, 144, 82, 144)
label(80, 140, "C4", 1.4)
add_bom("C4", "10u+100n", "LDO out")
box(8, 130, 86, 156, "POWER")

# Injectors — top, spaced for local verticals only
for i, x in enumerate([100, 118, 136, 154]):
    code = f"Q{i+1}"
    to220(code, x, 148)
    add_bom(code, "IRLZ44N", f"Driver bico INJ{i+1}")
    axial(f"R{10+i}.A", f"R{10+i}.B", x - 2.54, 138, x - 2.54, 132)
    label(x - 5.5, 135, f"R{10+i}", 1.3)
    add_bom(f"R{10+i}", "100R", f"Gate INJ{i+1}")
    axial(f"R{20+i}.A", f"R{20+i}.B", x - 2.54, 130, x, 130)
    label(x + 3, 130, f"R{20+i}", 1.3)
    add_bom(f"R{20+i}", "10k", f"Pull-down INJ{i+1}")
    axial(f"D{10+i}.A", f"D{10+i}.K", x + 5, 148, x + 5, 142)
    label(x + 7, 145, f"D{10+i}", 1.3)
    add_bom(f"D{10+i}", "1N4007", f"Flyback INJ{i+1}")

to220("Q5", 176, 148)
add_bom("Q5", "IRLZ44N", "Aquecedor lambda")
axial("R15.A", "R15.B", 173.46, 138, 173.46, 132)
label(168, 135, "R15", 1.3)
add_bom("R15", "100R", "Gate Q5")
axial("R25.A", "R25.B", 173.46, 130, 176, 130)
label(179, 130, "R25", 1.3)
add_bom("R25", "10k", "Pull-down Q5")
box(94, 126, 188, 156, "DRIVERS")

# Relays left mid — above connector channel
for i, x in enumerate([14, 28, 42]):
    code = f"Q{7+i}"
    to92(code, x, 108)
    add_bom(code, "2N7000", f"Driver relé RL{i+1}")
    axial(f"R{30+i}.A", f"R{30+i}.B", x, 102, x, 96)
    label(x - 4, 99, f"R{30+i}", 1.3)
    add_bom(f"R{30+i}", "1k", f"Gate relé {i+1}")
    axial(f"D{20+i}.A", f"D{20+i}.K", x + 4, 108, x + 4, 102)
    label(x + 6, 105, f"D{20+i}", 1.3)
    add_bom(f"D{20+i}", "1N4007", f"Flyback relé {i+1}")
box(8, 92, 50, 116, "RELAY")

# MCU center — left header for injectors/relays/ADC, right for sensors/lambda/power
for i in range(20):
    pad(f"U1.L{i+1}", 86, 114 - i * 2.54, 1.55, 0.9)
    pad(f"U1.R{i+1}", 138, 114 - i * 2.54, 1.55, 0.9)
label(112, 58, "U1 STM32F407", 2.1)
box(84, 60, 140, 118, "U1")
add_bom("U1", "STM32F407 Black Board", "MCU")
for i in range(4):
    pad(f"J3.{i+1}", 104 + i * 2.54, 54, 1.7, 0.95)
label(108, 50, "J3 SWD", 1.5)
add_bom("J3", "header 1x4", "SWD debug")

# Sensors right of MCU (aligned to U1.R)
sy = [112, 100, 88, 76]
for i, (n, y) in enumerate(zip(["IAT", "CLT", "MAP", "TPS"], sy)):
    if n != "TPS":
        axial(f"R{40+i}.A", f"R{40+i}.B", 156, y, 164, y)
        label(160, y + 2.5, f"R{40+i}", 1.3)
        add_bom(f"R{40+i}", "2K26" if n != "MAP" else "10k 1%", f"{n} pullup/div")
    if n == "MAP":
        axial("R43.A", "R43.B", 164, y, 164, y - 4)
        label(167, y - 2, "R43", 1.3)
        add_bom("R43", "18k 1%", "MAP divisor GND")
    axial(f"C{10+i}.A", f"C{10+i}.B", 168, y, 168, y - 3.5)
    label(171, y - 1, f"C{10+i}", 1.3)
    add_bom(f"C{10+i}", "100n", f"Filtro {n}")
    axial(f"R{50+i}.A", f"R{50+i}.B", 172, y, 180, y)
    label(176, y + 2.5, f"R{50+i}", 1.3)
    add_bom(f"R{50+i}", "1k", f"Série ADC {n}")
box(154, 70, 184, 118, "SENS")

# RPM left of MCU
dip("U4", 56, 70, 4)
add_bom("U4", "PC817", "Opto RPM")
axial("R60.A", "R60.B", 46, 76, 54, 76)
label(50, 79, "R60", 1.3)
add_bom("R60", "10k 2W", "RPM série 1")
axial("R61.A", "R61.B", 38, 76, 46, 76)
label(42, 79, "R61", 1.3)
add_bom("R61", "10k 2W", "RPM série 2")
axial("D30.A", "D30.K", 50, 70, 50, 64)
label(53, 67, "D30", 1.3)
add_bom("D30", "1N4148", "Proteção LED opto")
axial("R62.A", "R62.B", 66, 80, 66, 74)
label(69, 77, "R62", 1.3)
add_bom("R62", "4k7", "Pull-up RPM")
axial("C20.A", "C20.B", 70, 74, 70, 68)
label(73, 71, "C20", 1.3)
add_bom("C20", "1nF", "Filtro RPM")
box(36, 62, 76, 86, "RPM")

# CAN under MCU
pad("U5.VCC", 100, 72)
pad("U5.GND", 106, 72)
pad("U5.TX", 100, 66)
pad("U5.RX", 106, 66)
pad("U5.H", 112, 72)
pad("U5.L", 118, 72)
label(109, 76, "U5 CAN", 1.6)
box(98, 64, 122, 78, "U5")
add_bom("U5", "SN65HVD230 módulo", "CAN transceiver")

# Lambda bottom-right
dip("U2", 160, 36, 14)
add_bom("U2", "MCP6004 DIP14", "Op-amp quádruplo wideband")
soic8("U3", 188, 38)
add_bom("U3", "AD8628 SOIC", "Chopper Ip (SMD embaixo)")
axial("R70.A", "R70.B", 180, 54, 188, 54)
label(184, 57, "R70", 1.3)
add_bom("R70", "61R9 1%", "Shunt Ip")
axial("R71.A", "R71.B", 180, 60, 188, 60)
label(184, 63, "R71", 1.3)
add_bom("R71", "6k8 1%", "R_ESR LSU 4.2")
axial("C30.A", "C30.B", 194, 54, 194, 48)
label(197, 51, "C30", 1.3)
add_bom("C30", "220n", "Filtro Ip")
axial("C31.A", "C31.B", 198, 60, 198, 54)
label(201, 57, "C31", 1.3)
add_bom("C31", "220n", "Filtro Un")
axial("C32.A", "C32.B", 154, 44, 154, 38)
label(151, 41, "C32", 1.3)
add_bom("C32", "100n+10u", "Decoupling +5V opamps")
axial("R72.A", "R72.B", 168, 46, 176, 46)
label(172, 49, "R72", 1.3)
add_bom("R72", "10k 1%", "Divisor O2")
axial("R73.A", "R73.B", 176, 46, 176, 40)
label(179, 43, "R73", 1.3)
add_bom("R73", "18k 1%", "Divisor O2 GND")
box(152, 32, 212, 66, "LAMBDA")

# Silk BOM strip (compact codes on board)
label(8, 24, "BOM: ver modulo/pcb-bom-codigos.md", 1.6)
label(8, 28, "INJET RACING ECU 1L 240x160", 1.8)

for x, y in [(4, 4), (236, 4), (4, 156), (236, 156)]:
    pad(f"MH_{x}_{y}", x, y, 3.6, 3.2)


def route_all():
    block_holes()
    YG, Y12 = 3.0, 157.0

    # Thin edge buses only (não criar floresta de stubs ainda)
    bus_h("GND", YG, 2.0, 6, 230)
    bus_h("+12V", Y12, 1.8, 6, 190)
    # +5V / +3V3 em trilhos H sob drivers (canal), não atravessando MCU
    bus_h("+5V", 124.0, 1.2, 50, 230)
    bus_h("+3V3", 120.0, 1.1, 66, 230)

    jobs = []  # (manhattan, net, a, b, w)

    def add(net, a, b, w=0.75):
        if a not in pads or b not in pads:
            return
        ax, ay = pads[a][0], pads[a][1]
        bx, by = pads[b][0], pads[b][1]
        jobs.append((abs(ax - bx) + abs(ay - by), net, a, b, w))

    # --- Power locals (curtíssimos) ---
    add("QG", "Q6.G", "R1.A", 0.7)
    add("QG", "Q6.G", "D2.A", 0.7)
    add("GND", "R1.B", "D2.K", 0.7)
    add("+12V", "Q6.S", "C1.A", 1.3)
    add("GND", "C1.B", "C2.B", 0.9)
    add("+12V", "C2.A", "D1.A", 0.9)
    add("GND", "D1.K", "C1.B", 0.9)
    add("+12V", "U6.VIN", "Q6.S", 1.2)
    add("GND", "U6.GND", "U7.GND", 0.9)
    add("+5V", "U6.OUT", "U7.IN", 1.0)
    add("+5V", "U7.IN", "C3.A", 0.85)
    add("GND", "C3.B", "C4.B", 0.85)
    add("+3V3", "U7.OUT", "C4.A", 0.95)

    # Injector locals
    for i in range(4):
        add(f"INJ{i+1}", f"D{10+i}.A", f"Q{i+1}.D", 1.0)
        add(f"GI{i+1}", f"R{10+i}.A", f"Q{i+1}.G", 0.7)
        add(f"GI{i+1}", f"R{20+i}.A", f"Q{i+1}.G", 0.65)
        add("GND", f"R{20+i}.B", f"Q{i+1}.S", 0.75)

    add("GH", "R15.A", "Q5.G", 0.7)
    add("GH", "R25.A", "Q5.G", 0.65)
    add("GND", "R25.B", "Q5.S", 0.75)

    for i in range(3):
        add(f"RL{i+1}", f"D{20+i}.A", f"Q{7+i}.D", 0.85)
        add(f"GR{i+1}", f"R{30+i}.A", f"Q{7+i}.G", 0.65)

    # Sensor locals
    for i, n in enumerate(["IAT", "CLT", "MAP", "TPS"]):
        if n != "TPS":
            add(n, f"R{40+i}.B", f"C{10+i}.A", 0.65)
            add(n, f"R{40+i}.B", f"R{50+i}.A", 0.65)
        else:
            add(n, f"R{50+i}.A", f"C{10+i}.A", 0.65)
    add("MAP", "R42.B", "R43.A", 0.65)
    add("O2", "R72.B", "R73.A", 0.6)
    add("IP", "R70.B", "C30.A", 0.65)
    add("UN", "R71.A", "C31.A", 0.65)

    # RPM locals
    add("RPMi", "R61.B", "R60.A", 0.8)
    add("RPMi", "R60.B", "U4.1", 0.75)
    add("GND", "U4.2", "U4.3", 0.7)
    add("RPMi", "D30.A", "U4.1", 0.6)
    add("RPMi", "D30.K", "U4.2", 0.6)
    add("RPMo", "U4.4", "R62.B", 0.7)
    add("RPMo", "U4.4", "C20.A", 0.6)

    # Lambda locals
    add("VM", "U2.1", "U2.2", 0.6)
    add("IP", "U3.6", "R70.A", 0.7)
    add("IP", "U3.2", "R70.A", 0.65)
    add("VM", "U3.3", "J2.4", 0.7)

    # Longer nets — pin map aligned to reduce crossings
    # INJ drains → J1 13-16 (row bottom)
    for i in range(4):
        add(f"INJ{i+1}", f"Q{i+1}.D", f"J1.{13+i}", 1.1)
        add(f"GI{i+1}", f"U1.L{13+i}", f"R{10+i}.B", 0.75)

    add("GH", "U1.L17", "R15.B", 0.75)
    add("H-", "Q5.D", "J2.2", 1.3)

    # Relays → J1 18,17,19
    for i, cn in enumerate([18, 17, 19]):
        add(f"RL{i+1}", f"Q{7+i}.D", f"J1.{cn}", 0.95)
        add(f"GR{i+1}", f"U1.L{18+i}", f"R{30+i}.B", 0.7)

    # Sensors J1 → chain → MCU
    add("IAT", "J1.8", "R40.B", 0.8)
    add("IAT", "R50.B", "U1.R3", 0.8)
    add("CLT", "J1.9", "R41.B", 0.8)
    add("CLT", "R51.B", "U1.R4", 0.8)
    add("MAP", "J1.10", "R42.A", 0.8)
    add("MAP", "R52.B", "U1.R5", 0.8)
    add("TPS", "J1.11", "R53.A", 0.8)
    add("TPS", "R53.B", "U1.R6", 0.8)

    add("RPMi", "J1.12", "R61.A", 0.85)
    add("RPMo", "U4.4", "U1.L10", 0.8)

    add("CANTX", "U1.L12", "U5.TX", 0.7)
    add("CANRX", "U1.L11", "U5.RX", 0.7)
    add("CANH", "U5.H", "J1.20", 0.9)
    add("CANL", "U5.L", "J1.21", 0.9)

    add("IP", "J2.3", "R70.A", 0.85)
    add("IP", "R70.B", "U1.R8", 0.8)
    add("VM", "U1.R9", "U2.3", 0.75)
    add("VM", "U2.1", "J2.4", 0.8)
    add("UN", "J2.5", "R71.A", 0.8)
    add("UN", "R71.A", "U1.R10", 0.8)
    add("RI", "U1.R11", "R71.B", 0.7)
    add("O2", "U2.7", "R72.A", 0.7)
    add("O2", "R72.B", "U1.R7", 0.8)

    add("+12VIN", "J1.1", "Q6.D", 1.5)
    add("+12VIN", "J1.2", "Q6.D", 1.3)
    add("SWDIO", "J3.2", "U1.R14", 0.65)
    add("SWCLK", "J3.3", "U1.R15", 0.65)

    # Power taps to buses (após locais) — stubs curtos
    jobs.sort(key=lambda t: t[0])
    for _, net, a, b, w in jobs:
        route(net, a, b, w)

    # Stubs to power rails (só os necessários)
    for p in ["Q6.S", "U6.VIN", "D10.K", "D11.K", "D12.K", "D13.K", "D20.K", "D21.K", "D22.K", "J2.1"]:
        stub_to_bus("+12V", p, bus_y=Y12, w=1.1)

    for p in ["U6.OUT", "J1.6", "U1.R1", "C32.A", "U2.14", "U5.VCC"]:
        stub_to_bus("+5V", p, bus_y=124.0, w=0.95)

    for p in ["U7.OUT", "J1.7", "U1.L1", "J3.1", "R40.A", "R41.A", "R42.A", "R62.A"]:
        stub_to_bus("+3V3", p, bus_y=120.0, w=0.9)

    # GND pads marked then pour
    for p in ["J1.3", "J1.4", "J1.5", "J1.24", "C1.B", "U6.GND", "Q1.S", "Q2.S", "Q3.S", "Q4.S",
              "Q5.S", "Q7.S", "Q8.S", "Q9.S", "U1.L2", "U1.R2", "J3.4", "U4.3", "U5.GND",
              "U2.4", "C10.B", "C11.B", "C12.B", "C13.B", "C20.B", "C30.B", "C31.B", "C32.B",
              "R43.B", "R73.B", "C4.B"]:
        if p in pads:
            pad_net[p] = "GND"
            mark(pads[p][0], pads[p][1], pads[p][2] / 2, "GND")

    # Seed GND from bus already painted; short stubs for nearby only
    for p in ["J1.3", "J1.4", "J1.5", "J1.24", "C20.B", "C32.B"]:
        stub_to_bus("GND", p, bus_y=YG, w=1.0)

    flood_gnd()
    connect_gnd_pads()


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
                col = {"GND": (35, 35, 35), "+12V": (220, 45, 45), "+12VIN": (180, 30, 30),
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
    d.text(P(8, 30), "MAPA MONTAGEM — furos THT + pads SMD (roxo=U3)", fill=(0, 0, 0), font=font(2.2))
    return img


def render_cnc(inv=False):
    bg, cu = (255, 0) if not inv else (0, 255)
    img = Image.new("L", px(W, H), bg)
    d = ImageDraw.Draw(img)

    def Y(y):
        return H - y

    def P(x, y):
        return px(x, Y(y))

    # Draw pour GND lightly? For CNC isolation we only want copper of nets as lines+pads
    # Pour is conceptual for connectivity — export only explicit traces + pads to avoid solid plate
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
    L.append("</g>")
    L.append(f'<g fill="{bg}">')
    for name, (x, y, od, drill) in pads.items():
        if drill > 0:
            L.append(f'<circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{drill/2:.3f}"/>')
    for x, y in [(4, 4), (236, 4), (4, 156), (236, 156)]:
        L.append(f'<circle cx="{x}" cy="{Y(y)}" r="1.6"/>')
    L.append("</g></svg>")
    path.write_text("\n".join(L), encoding="utf-8")


def write_bom_md(cross, nj):
    lines = [
        "# BOM com códigos — PCB INJET RACING (1-layer)",
        "",
        f"> Placa **{W:.0f}×{H:.0f} mm**. Códigos = silk da placa / mapa de furos.",
        "",
        f"- Cruzamentos cobre: **{cross}**",
        f"- Fios topo (último recurso): **{nj}**",
        "",
        "| Código | Valor / P/N | Função |",
        "|---|---|---|",
    ]
    for code, val, desc in bom:
        lines.append(f"| **{code}** | `{val}` | {desc} |")
    lines += [
        "",
        "## Conectores",
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
        "## Montagem",
        "",
        "- THT pelo lado componentes (topo).",
        "- **U3 AD8628** SMD no lado do cobre.",
        "- Arquivos: `assets/ecu-pcb-1layer-pads-map.png` (só furos) · `ecu-pcb-1layer-assembly.png` (trilhas) · `ecu-pcb-1layer-traces-cnc.svg` (CNC).",
        "",
    ]
    (DOC / "pcb-bom-codigos.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    print("Routing v6…")
    route_all()
    cross = count_cross()
    # unique jumper nets count
    from collections import Counter
    jc = Counter(n for *_, n in jumpers)
    print(f"cross={cross} traces={len(traces)} jumpers={len(jumpers)} unique={dict(jc)} bom={len(bom)}")

    render_assembly().save(OUT / "ecu-pcb-1layer-assembly.png", dpi=(DPI, DPI))
    render_pads_map().save(OUT / "ecu-pcb-1layer-pads-map.png", dpi=(DPI, DPI))
    render_cnc(False).save(OUT / "ecu-pcb-1layer-traces-cnc.png", dpi=(DPI, DPI))
    render_cnc(True).save(OUT / "ecu-pcb-1layer-traces-cnc-invert.png", dpi=(DPI, DPI))
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc.svg")
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc-invert.svg", True)
    write_bom_md(cross, len(jumpers))
    (OUT / "ecu-pcb-1layer-drc.md").write_text(
        f"# DRC\n\n- Cruzamentos cobre: **{cross}**\n- Trilhas: {len(traces)}\n"
        f"- Jumpers: **{len(jumpers)}**\n- Placa: {W}×{H} mm\n\n"
        "## Jumpers restantes\n\n"
        + ("\n".join(f"- `{n}`" for *_, n in jumpers) if jumpers else "Nenhum."),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
