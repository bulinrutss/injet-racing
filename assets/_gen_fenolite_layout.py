"""
INJET RACING — layout fenolite THT 200×100 mm
Gera:
  - vista com zonas + trilhas (referência)
  - máscara só cobre (CNC) em SVG + PNG
Escala: 1 unidade = 1 mm
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"e:\injet racing\assets")
OUT.mkdir(parents=True, exist_ok=True)

W, H = 200.0, 100.0  # mm
DPI = 25.4 * 10  # 10 px/mm → 254 DPI  (boa p/ CNC bitmap)
PX_PER_MM = 10.0


def mm(*xy: float) -> tuple[int, ...]:
    return tuple(int(round(v * PX_PER_MM)) for v in xy)


def font(size_mm: float):
    px = max(10, int(size_mm * PX_PER_MM))
    try:
        return ImageFont.truetype("arial.ttf", px)
    except OSError:
        try:
            return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", px)
        except OSError:
            return ImageFont.load_default()


# ---------- geometria dos pads / trilhas (mm) ----------
# anel: (x, y, od_mm, id_mm)  id=furo
# trilha: polyline [(x,y),...] width_mm

pads: list[tuple[float, float, float, float]] = []
traces: list[tuple[list[tuple[float, float]], float]] = []  # (pts, width)
labels: list[tuple[float, float, str, float]] = []  # x,y,text,size
zones: list[tuple[float, float, float, float, str, tuple]] = []  # x,y,w,h,name,color


def add_pad(x, y, od=2.2, drill=1.0):
    pads.append((x, y, od, drill))


def add_dip(x0, y0, n_pins, pitch=2.54, row_gap=7.62, od=1.8, drill=0.9):
    """DIP: pin 1 bottom-left, CCW standard left side down then right up."""
    half = n_pins // 2
    for i in range(half):
        add_pad(x0, y0 + i * pitch, od, drill)
        add_pad(x0 + row_gap, y0 + (half - 1 - i) * pitch, od, drill)


def add_to220(x, y):
    """TO-220 3 pins horizontal, tab toward +Y."""
    for i, dx in enumerate((-2.54, 0, 2.54)):
        add_pad(x + dx, y, 2.4, 1.1)
    return [(x - 2.54, y), (x, y), (x + 2.54, y)]  # G D S-ish


def add_header_row(x0, y0, n, pitch=2.54):
    for i in range(n):
        add_pad(x0 + i * pitch, y0, 1.8, 1.0)


def add_trace(pts, w=1.2):
    traces.append((pts, w))


# --- zonas ---
zones = [
    (4, 58, 48, 38, "POWER\n12V BUCK 3V3", (40, 70, 55)),
    (58, 52, 78, 44, "STM32F407\nBLACK BOARD", (35, 55, 90)),
    (142, 55, 54, 41, "SENSOR\nIAT CLT MAP TPS", (55, 75, 45)),
    (4, 4, 55, 42, "CN1\nAMPSEAL 23", (70, 55, 40)),
    (64, 4, 36, 28, "RPM\nPC817", (80, 60, 50)),
    (104, 4, 36, 28, "CAN\nSN65HVD230", (50, 65, 85)),
    (144, 4, 52, 42, "LAMBDA DIY\nMCP6004 OPA388IDR\nCN2 LSU4.2", (90, 55, 45)),
]

# --- POWER pads ---
# IRF9540
add_to220(18, 88)
labels.append((18, 95, "IRF9540", 2.2))
# bulk cap
add_pad(32, 88, 2.8, 0.9)
add_pad(38, 88, 2.8, 0.9)
labels.append((35, 95, "220u/50V", 2.0))
# buck module 4 pins
for i, (bx, by) in enumerate([(14, 72), (22, 72), (14, 64), (22, 64)]):
    add_pad(bx, by, 2.0, 1.0)
labels.append((18, 78, "BUCK 5V", 2.0))
# AMS1117 module / TO
add_pad(40, 72, 2.0, 1.0)
add_pad(46, 72, 2.0, 1.0)
add_pad(43, 64, 2.0, 1.0)
labels.append((43, 78, "3V3 LDO", 2.0))
# TVS + zener
add_pad(48, 88, 1.8, 0.8)
add_pad(48, 82, 1.8, 0.8)

# --- Injector MOSFETs top ---
inj_x = [62, 78, 94, 110, 126]
inj_names = ["INJ1", "INJ2", "INJ3", "INJ4", "HEAT"]
for x, name in zip(inj_x, inj_names):
    add_to220(x, 90)
    labels.append((x, 97, name, 2.0))

# --- Relay drivers TO-92 ---
for i, x in enumerate([62, 72, 82]):
    add_pad(x - 1.27, 58, 1.6, 0.8)
    add_pad(x, 55, 1.6, 0.8)
    add_pad(x + 1.27, 58, 1.6, 0.8)
    labels.append((x, 62, f"RL{i+1}", 1.8))

# --- STM32 Black Board headers (2×20 verticais, passo 2,54) ---
for i in range(20):
    add_pad(68, 70 - i * 2.54, 1.7, 0.95)  # esquerda
    add_pad(68 + 52.5, 70 - i * 2.54, 1.7, 0.95)  # direita
labels.append((94, 48, "STM32F407", 2.5))
labels.append((94, 44, "BLACK BOARD", 2.0))

# SWD header bottom of MCU area
add_header_row(88, 34, 4, 2.54)
labels.append((93, 30, "SWD", 1.8))

# --- Sensor dividers (4 channels) ---
sx0 = 152
for i, name in enumerate(["IAT", "CLT", "MAP", "TPS"]):
    y = 88 - i * 8
    add_pad(sx0, y, 1.6, 0.8)
    add_pad(sx0 + 8, y, 1.6, 0.8)
    add_pad(sx0 + 16, y, 1.6, 0.8)
    add_pad(sx0 + 24, y, 1.6, 0.8)  # to MCU via
    labels.append((sx0 + 8, y + 3.5, name, 1.8))

# --- AMPSEAL 23 simplified as 2 rows ---
for i in range(12):
    add_pad(10 + i * 3.5, 28, 2.0, 1.0)
for i in range(11):
    add_pad(10 + i * 3.5, 18, 2.0, 1.0)
labels.append((28, 12, "CN1 AMPSEAL 23", 2.2))

# --- PC817 DIP4 ---
add_dip(72, 12, 4, pitch=2.54, row_gap=7.62)
labels.append((76, 24, "PC817", 2.0))
# 10k 2W pads
add_pad(68, 22, 2.2, 0.9)
add_pad(84, 22, 2.2, 0.9)

# --- CAN module 4 pins ---
for x in (110, 118, 126, 134):
    add_pad(x, 16, 2.0, 1.0)
labels.append((122, 24, "CAN MOD", 2.0))

# --- MCP6004 DIP14 ---
add_dip(152, 12, 14, pitch=2.54, row_gap=7.62)
labels.append((156, 34, "MCP6004", 2.0))

# --- OPA388IDR SOIC-DIP adapter 8 pin ---
add_dip(172, 12, 8, pitch=2.54, row_gap=7.62)
labels.append((176, 28, "OPA388IDR", 1.8))

# --- CN2 lambda 6 pin ---
add_header_row(148, 38, 6, 2.54)
labels.append((156, 42, "CN2 LSU4.2", 1.8))

# --- Trilhas principais (barramentos) ---
# GND bus bottom
add_trace([(8, 8), (192, 8)], 2.5)
# GND top
add_trace([(8, 98), (192, 98)], 2.0)
# +12V_PROT from IRF9540 drain area to injectors
add_trace([(18, 88), (18, 92), (62, 92), (126, 92)], 2.5)
# +5V from buck to sensor/lambda
add_trace([(22, 72), (22, 50), (150, 50), (150, 38), (160, 38)], 1.8)
# +3V3 from LDO to MCU left header mid
add_trace([(43, 64), (43, 50), (68, 50)], 1.8)
# MCU to injectors gates (signals)
for i, x in enumerate(inj_x):
    y_mcu = 70 - (2 + i) * 2.54
    add_trace([(68 + 52.5, y_mcu), (x, y_mcu), (x, 90)], 1.0)
# MCU to sensor pads
for i in range(4):
    y = 88 - i * 8
    y_mcu = 70 - (8 + i) * 2.54
    add_trace([(sx0 + 24, y), (68 + 52.5 + 4, y), (68 + 52.5, y_mcu)], 1.0)
# AMPSEAL to power
add_trace([(10, 28), (10, 64), (14, 64)], 2.0)
add_trace([(13.5, 28), (13.5, 50), (18, 50), (18, 72)], 1.5)
# RPM to MCU
add_trace([(72 + 7.62, 12), (72 + 7.62, 34), (88, 34)], 1.0)
# CAN to MCU
add_trace([(110, 16), (110, 40), (68 + 52.5, 40)], 1.0)
# Lambda MCP to CN2
add_trace([(152, 12 + 3 * 2.54), (148, 12 + 3 * 2.54), (148, 38)], 1.0)
add_trace([(152 + 7.62, 12 + 2 * 2.54), (163, 12 + 2 * 2.54), (163, 38)], 1.0)
# Heater MOSFET to CN2 area
add_trace([(126, 90), (140, 90), (140, 42), (148 + 5 * 2.54, 42), (148 + 5 * 2.54, 38)], 2.0)
# Relay driver to AMPSEAL region
for i, x in enumerate([62, 72, 82]):
    add_trace([(x, 55), (x, 40), (20 + i * 3.5, 40), (20 + i * 3.5, 28)], 1.0)

# flyback diodes near injectors (pads only)
for x in inj_x[:4]:
    add_pad(x + 5, 86, 1.8, 0.8)
    add_trace([(x + 2.54, 90), (x + 5, 90), (x + 5, 86)], 1.2)
    add_trace([(x + 5, 86), (x + 5, 92), (x, 92)], 1.2)


def render_reference() -> Image.Image:
    img = Image.new("RGB", mm(W, H), (18, 22, 28))
    d = ImageDraw.Draw(img)
    # board
    d.rectangle([*mm(0, 0), *mm(W, H)], fill=(26, 90, 55), outline=(200, 210, 200), width=3)
    # zones
    for x, y, w, h, name, col in zones:
        d.rectangle([*mm(x, y), *mm(x + w, y + h)], outline=col + (0,), width=2)
        # semi overlay
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rectangle([*mm(x, y), *mm(x + w, y + h)], fill=(*col, 40))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        d = ImageDraw.Draw(img)
        f = font(2.4)
        d.multiline_text(mm(x + 2, y + h - 12), name, fill=(230, 240, 230), font=f, spacing=2)
    # traces
    for pts, w in traces:
        if len(pts) < 2:
            continue
        flat = []
        for p in pts:
            flat.extend(mm(*p))
        d.line(flat, fill=(210, 170, 60), width=max(2, int(w * PX_PER_MM)))
    # pads
    for x, y, od, drill in pads:
        r = od / 2
        d.ellipse([*mm(x - r, y - r), *mm(x + r, y + r)], fill=(200, 160, 50), outline=(120, 90, 20))
        rd = drill / 2
        d.ellipse([*mm(x - rd, y - rd), *mm(x + rd, y + rd)], fill=(18, 22, 28))
    # mounting holes
    for x, y in [(5, 5), (195, 5), (5, 95), (195, 95)]:
        d.ellipse([*mm(x - 1.6, y - 1.6), *mm(x + 1.6, y + 1.6)], outline=(220, 220, 220), width=2)
        d.ellipse([*mm(x - 1.0, y - 1.0), *mm(x + 1.0, y + 1.0)], fill=(18, 22, 28))
    # title
    d.text(mm(6, 48), "INJET RACING ECU  ·  FENOLITE 200×100 mm  ·  THT", fill=(240, 245, 240), font=font(3.0))
    d.text(mm(6, 52), "Referência de zonas + trilhas (proto CNC)", fill=(180, 200, 180), font=font(2.2))
    # dimension arrows
    d.line([*mm(0, -0), *mm(200, 0)], fill=(255, 255, 255), width=1)  # noop safe
    return img


def render_cnc(invert: bool = False) -> Image.Image:
    """Cobre = preto (invert=False) ou branco (invert=True). Fundo oposto."""
    bg = 255 if not invert else 0
    cu = 0 if not invert else 255
    img = Image.new("L", mm(W, H), bg)
    d = ImageDraw.Draw(img)
    # copper pour outline margin optional — skip, isolation mill prefers traces+pads only
    for pts, w in traces:
        if len(pts) < 2:
            continue
        flat = []
        for p in pts:
            flat.extend(mm(*p))
        d.line(flat, fill=cu, width=max(2, int(w * PX_PER_MM)))
    for x, y, od, drill in pads:
        r = od / 2
        d.ellipse([*mm(x - r, y - r), *mm(x + r, y + r)], fill=cu)
        # furo: limpar cobre no centro (isolação do furo)
        rd = max(0.3, drill / 2 - 0.05)
        d.ellipse([*mm(x - rd, y - rd), *mm(x + rd, y + rd)], fill=bg)
    # mounting keepouts (furos)
    for x, y in [(5, 5), (195, 5), (5, 95), (195, 95)]:
        d.ellipse([*mm(x - 1.6, y - 1.6), *mm(x + 1.6, y + 1.6)], fill=bg)
    # borda da placa (contorno) — linha fina de referência no cobre? não: só contorno em outro arquivo
    return img


def write_svg_cnc(path: Path, invert: bool = False):
    """SVG vetorial em mm — melhor p/ CNC do que bitmap."""
    cu = "#000000" if not invert else "#FFFFFF"
    bg = "#FFFFFF" if not invert else "#000000"
    parts = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{bg}"/>',
        f'<!-- INJET RACING fenolite 200x100 mm — só cobre | cobre={"preto" if not invert else "branco"} -->',
        f'<g id="copper" fill="{cu}" stroke="{cu}" stroke-linecap="round" stroke-linejoin="round">',
    ]
    for pts, w in traces:
        if len(pts) < 2:
            continue
        dpath = "M " + " L ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
        parts.append(f'  <path d="{dpath}" fill="none" stroke-width="{w:.3f}"/>')
    for x, y, od, drill in pads:
        r = od / 2
        parts.append(f'  <circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}"/>')
    parts.append("</g>")
    # furos (recortes)
    parts.append(f'<g id="holes" fill="{bg}">')
    for x, y, od, drill in pads:
        rd = drill / 2
        parts.append(f'  <circle cx="{x:.3f}" cy="{y:.3f}" r="{rd:.3f}"/>')
    for x, y in [(5, 5), (195, 5), (5, 95), (195, 95)]:
        parts.append(f'  <circle cx="{x}" cy="{y}" r="1.6"/>')
    parts.append("</g>")
    # contorno placa (guia, não cobre)
    parts.append(
        f'<rect x="0.4" y="0.4" width="{W-0.8}" height="{H-0.8}" fill="none" '
        f'stroke="#888888" stroke-width="0.3" stroke-dasharray="2 1"/>'
    )
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_svg_layout(path: Path):
    parts = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="#1a5a37"/>',
        f'<text x="6" y="50" fill="#e8f0e8" font-size="3.2" font-family="Arial">INJET RACING ECU · FENOLITE 200×100 mm THT</text>',
    ]
    for x, y, w, h, name, col in zones:
        hexcol = "#%02x%02x%02x" % col
        parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{hexcol}" fill-opacity="0.18" '
            f'stroke="{hexcol}" stroke-width="0.4"/>'
        )
        ty = y + h - 3
        for line in name.split("\n"):
            parts.append(
                f'<text x="{x+2}" y="{ty}" fill="#e8f0e8" font-size="2.2" font-family="Arial">{line}</text>'
            )
            ty -= 3
    parts.append('<g stroke="#d2aa3c" stroke-linecap="round" stroke-linejoin="round" fill="none">')
    for pts, w in traces:
        dpath = "M " + " L ".join(f"{a:.3f},{b:.3f}" for a, b in pts)
        parts.append(f'  <path d="{dpath}" stroke-width="{w:.3f}"/>')
    parts.append("</g>")
    parts.append('<g fill="#c8a032" stroke="#785a14" stroke-width="0.15">')
    for x, y, od, drill in pads:
        parts.append(f'  <circle cx="{x:.3f}" cy="{y:.3f}" r="{od/2:.3f}"/>')
    parts.append("</g>")
    parts.append('<g fill="#12161c">')
    for x, y, od, drill in pads:
        parts.append(f'  <circle cx="{x:.3f}" cy="{y:.3f}" r="{drill/2:.3f}"/>')
    parts.append("</g>")
    for x, y, t, sz in labels:
        parts.append(
            f'<text x="{x}" y="{y}" fill="#f0f5f0" font-size="{sz}" text-anchor="middle" font-family="Arial">{t}</text>'
        )
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main():
    # PIL/SVG: Y=0 no topo. Espelhar geometria p/ bater com o render 3D
    # (potência/MOSFETs em cima, CN1/CN2 embaixo).
    global pads, traces, labels, zones

    def fy(y: float) -> float:
        return H - y

    pads = [(x, fy(y), od, dr) for x, y, od, dr in pads]
    traces = [([(x, fy(y)) for x, y in pts], w) for pts, w in traces]
    labels = [(x, fy(y), t, s) for x, y, t, s in labels]
    zones = [(x, fy(y + h), w, h, name, col) for x, y, w, h, name, col in zones]
    ref = render_reference()
    ref_path = OUT / "ecu-fenolite-100x200-layout.png"
    ref.save(ref_path, dpi=(DPI, DPI))

    cnc = render_cnc(invert=False)
    cnc_path = OUT / "ecu-fenolite-100x200-traces-cnc.png"
    cnc.save(cnc_path, dpi=(DPI, DPI))

    cnc_inv = render_cnc(invert=True)
    cnc_inv_path = OUT / "ecu-fenolite-100x200-traces-cnc-invert.png"
    cnc_inv.save(cnc_inv_path, dpi=(DPI, DPI))

    write_svg_cnc(OUT / "ecu-fenolite-100x200-traces-cnc.svg", invert=False)
    write_svg_cnc(OUT / "ecu-fenolite-100x200-traces-cnc-invert.svg", invert=True)
    write_svg_layout(OUT / "ecu-fenolite-100x200-layout.svg")

    print("pads", len(pads), "traces", len(traces))
    print("saved:")
    for p in [
        ref_path,
        cnc_path,
        cnc_inv_path,
        OUT / "ecu-fenolite-100x200-traces-cnc.svg",
        OUT / "ecu-fenolite-100x200-traces-cnc-invert.svg",
        OUT / "ecu-fenolite-100x200-layout.svg",
    ]:
        print(" ", p, p.stat().st_size if p.exists() else "MISSING")


if __name__ == "__main__":
    main()
