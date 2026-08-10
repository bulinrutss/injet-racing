# ProdV6 — PCB do zero (checklist)

Placa **240×160 mm**, **F.Cu + B.Cu**, esquemático = prodv5 (congelado).

**Última revisão PCB:** 2026-08-10 · `injet-racing-prodv6.kicad_pcb` · DRC `DRC.rpt` 01:02:55

**Bancada (sem motor):** [`BENCH-CHECKLIST.md`](BENCH-CHECKLIST.md)

## Estado atual (roteamento)

| Item | Status |
|------|--------|
| MOD3–MOD12 rotas | **FEITO** — highlight net + `_check_modN_now.py` |
| CN1 6–16, 20–21 | **FEITO** |
| CN2 λ · CN3 relés | **FEITO** (footprints + rotas NO) |
| DRC elétrico (unconnected) | **16** — falsos positivos PTH / F↔B / R A↔B |
| DRC layout | **6** clearance U5 B.Cu · **1** Edge.Cuts |
| Gerber / silk final | pendente |

### +3V3 (duas regiões no cobre — conferir highlight)

| Região | Alimenta | Tronco |
|--------|----------|--------|
| **MCU** | J2 3V3 · R10/R11 · R22 · C10/C11 · R76 λ | barra y≈105,5 · corredor x=104 |
| **CAN/CN1-7** | U6 VCC · C40/C41 · **CN1 pino 7** | y≈34,5 + B.Cu y=30 |

CN1-7 ↔ U6.VCC: **OK** (mesmo grafo). Bancada: CN1-7 = **3,25–3,40 V** com 12 V (§2 `BENCH-CHECKLIST.md`).

## Regras

- [x] **Revisão de rotas** (conectividade + regras A/B caps) — MOD3–12
- [ ] DRC **0 erros** estritos (aceito: 16 unconnected cosméticos + U5 clearance)
- [ ] Uma net por vez no highlight; sem cruzar sinal x sinal
- [ ] Largura: +12V 1.2 mm · +5V/+3V3 1.0 mm · GND 0.8 mm · sinal 0.5–0.65 mm
- [ ] Clearance 0.3 mm (classe Default)

## Portas I/O entre módulos

Cada módulo tem **contorno sólido** (Dwgs.User) + rótulos curtos nas portas (sem caixas IN/OUT):
- Trilhas alinhadas em x/y fixo · potência preferir B.Cu
- Rótulos: net ou destino (`+12V_BAT`, `->MOD4`, etc.)

## Padrões MOD3 → todos os módulos

Regra Cursor: `.cursor/rules/prodv6-pcb-rebuild.mdc`

- Footprints com contorno real (cápsula / TO-220 / radial) — ver `_patch_fp_shapes.py`
- **Caps / 2 terminais:** trilha só até **pad A**; pad B = GND zone; **nunca** cruzar A e B com cobre
- **Espaçamento:** ≥1 mm entre courtyards; radial grande (C1) ≥6 mm do vizinho vertical

| Módulo | Porta | Net | x/y | Destino |
|--------|-------|-----|-----|---------|
| MOD3 | IN-NW | +12V_BAT | x=16 | CN1 |
| MOD3 | OUT-N | +12V_PROT | x=48, y=118 | MOD4 |
| MOD3 | OUT-E | +12V_PROT | y=148, x≥48 | CN2 / leste |
| MOD4 | IN-S | +12V_PROT | x=48, y=58 | MOD3 |

| MOD4 | OUT-E | +5V | x=78, y=44.5 | MOD5 |
| MOD5 | IN-W | +5V | x=78, y=44.5 → P5V canto | MOD4 |
| MOD5 | OUT-E | +3V3 | cluster (148–150, 88–110.5) | periféricos |

| # | Bloco | Status |
|---|--------|--------|
| 1 | Contorno + furos M3 + **CN1 CN2 CN3** | feito |
| 2 | GND pour F + B (zones) | **FEITO** — tecla **B** no KiCad |
| 3 | +12V_IN / +12V_PROT / proteção QREV | **FEITO** |
| 4 | Módulo MP1584 → **+5V** (C3–C6) | **FEITO** |
| 5 | Black Board JL-32F4XX 2×24 + REF3033 (C10–C12) | **FEITO** — rotas manuais KiCad · `_patch_mod5_close.py` · DRC bloco |
| 6 | Sensores IAT CLT MAP TPS VBAT | **FEITO** — CN1 + cond. → U1 J2 (L12O…L17I) |
| 7 | RPM (PC817) | **FEITO** — CN1-12 → U7 → PE8 |
| 8 | Injetores Q10–Q13 (4×) | **FEITO** — CN1 13–16 → drenos |
| 9 | Relés Q20–Q22 + CN3 | **FEITO** — gate/bobina/flyback · NO → CN3 1–3 |
| 10 | CAN U6 | **FEITO** — U6 ↔ U1 L6 · CANH/L ↔ CN1 20–21 |
| 11 | Lambda U4 U5 CN2 | **FEITO** — VM/IP/UN · U5 IP fechado |
| 12 | Aquecedor Q30 | **FEITO** — GHEAT · CN2 1–2 |
| 13 | DRC final + silk + Gerber | **parcial** — ver § DRC abaixo |

## KiCad — cada sessão

1. Abrir `injet-racing-prodv6.kicad_pro`
2. PCB Editor → rotear só o bloco atual
4. **B** (fill zones) → highlight net → `python _review_routes.py` → DRC → salvar `DRC.rpt`

### PCB ↔ esquemático

- **Salvar no PCB Editor não altera o esquemático.** Trilhas, posição de footprints e vias ficam só no `.kicad_pcb`.
- **Esquemático → PCB:** *Tools → Update PCB from Schematic* (F8).
- **PCB → esquemático (parcial):** *Tools → Update Schematic from PCB* — só campos/refs/footprints escolhidos, **não** leva trilhas nem posições de layout.
- Edições manuais no PCB: **não** rodar o gerador Python sem backup (apaga trilhas/zones preenchidas).

## Regenerar passo 1

```powershell
python "e:\injet racing\kicad\prodv6\_gen_kicad_prodv6.py"
```

(Atenção: regenerar apaga trilhas manuais se ainda não versionou.)

## MOD6 — sensores (sessão 2026-08-07)

**Layout manual** (posições atuais no `.kicad_pcb` — não usar `prodv6_layout.py` POS_SENS):

| Ref | Posição (mm) | Ref | Posição (mm) |
|-----|--------------|-----|--------------|
| R10 | 20.0, 107.5 | R16 | 19.5, 90.0 |
| R11 | 32.0, 105.5 | R17 | 30.0, 85.0 |
| R18 | 20.0, 121.0 | C20 | 30.5, 112.0 |
| R19 | 20.5, 102.5 | C21 | 37.0, 98.0 |
| R12 | 24.5, 96.0 | C22 | 39.0, 92.0 |
| R13 | 30.0, 90.0 | C23 | 24.5, 85.0 |
| R14 | 20.5, 76.5 | C24 | 37.0, 76.0 |
| R15 | 30.5, 68.0 | | |

**Feito (itens 1–10 — CN1 + condicionamento, sem U1)**
- [x] 15 footprints MOD6 colocados
- [x] **+12V_PROT → R14** (divisor VBAT)
- [x] **+3V3 → R10/R11** (pull-ups IAT/CLT)
- [x] **IAT** CN1-8 → R18 → C20
- [x] **CLT** CN1-9 → R19 → C21
- [x] **MAP** CN1-10 → R16 → R12/R13/C22
- [x] **TPS** CN1-11 → R17 → C23
- [x] **CN1-6 +5V** · **CN1-7 +3V3**
- [x] Caps pad B = GND (zone)

Sensores no **J2** (coluna exterior quando possível) — prodv6 2026-08-07:

| Sensor | Pad U1 | MCU | mm @ U1(86,108) |
|--------|--------|-----|-----------------|
| IAT | **L12O** | PC11 | 86, 77.52 |
| CLT | **L16O** | PC9 | 86, 67.36 |
| MAP | **L17O** | PC7 | 86, 64.82 |
| TPS | **L18I** | PC6 | 88.54, 62.28 |
| VBAT | **L17I** | PC8 | 88.54, 64.82 |

- [x] Nets U1 J2 atribuídas · rotas condicionamento → pads (**`_check_mod6_now.py` OK**)
- [x] **CN1-7 +3V3** → tronco CAN (U6/C40) — não usar R10.A como teste de CN1-7
- [x] Firmware `pins.h` PC11/PC9/PC7/PC6/PC8

**DRC cosmético MOD6:** TPS/MAP/CLT/IAT splits F↔B — highlight net OK

**Checagem:** `python _check_mod6_now.py`

## MOD7 — RPM PC817 (DRC 2026-08-07 07:29)

**Posições PCB** (origem footprint @ KiCad):

| Ref | mm (at) | rot | Função |
|-----|---------|-----|--------|
| R20 | 77.5, 31.5 | 90° | série bobina 10k 2W |
| R21 | 77.5, 20 | 0° | série bobina 10k 2W |
| U7 | 89.19, 26.73 | 0° | PC817 |
| D3 | 83.5, 25.5 | 0° | 1N4148 — **A=GND, K=RPM_IN OK** |
| R22 | 104, 26.5 | −90° | pull-up 4k7 |
| C25 | 104, 21 | 180° | filtro 1nF |

**Feito**
- [x] CN1-12 → R20 → R21 → U7 pin1 (bobina)
- [x] D3 anti-paralelo LED
- [x] U7 pin4 → R22/C25 → corredor B.Cu → **R17O** (PE8) @ (136, 64.82)
- [x] Opto isolado (pin1 ⊥ pin4)

**DRC MOD7:** R20/R21 série (unconnected A↔B = normal KiCad) · stub `(150.5,65.5)` pode ficar sem uso ou apagar

**Checagem:** `python _check_mod7_now.py` → MOD7 completo

## MOD8 — injetores IRLZ44N ×4 (DRC 2026-08-07 08:39)

**Esquema:** `modulo/esquema-eletrico.md` §5 · Q10–Q13 + R30–R33 (100R) + R40–R43 (10k) + D10–D13 (1N4007)

**Posições PCB** (origem @ KiCad; R30–33 rot 180° · R40–43 rot −90°):

| Canal | Q @ y=112 | R_gate @ 91 | R_gs @ 100 | D @ 106 | col x |
|-------|-----------|-------------|------------|---------|-------|
| INJ1 | Q10 (163.5) | R30 (166) | R40 (167.5) | D10 (174) | 163–174 |
| INJ2 | Q11 (180.5) | R31 (183) | R41 (184.5) | D11 (191) | 180–191 |
| INJ3 | Q12 (197.5) | R32 (200) | R42 (201.5) | D12 (208) | 197–208 |
| INJ4 | Q13 (214.5) | R33 (217) | R43 (218.5) | D13 (225) | 214–225 |

**Feito**
- [x] U1 GINJ1–4 → R18I/R19I/R20I/R21I (PE9/11/13/15)
- [x] Gate · GND · dreno · flyback K→+12V_PROT
- [x] **CN1 13–16** → drenos INJ1–4

**DRC cosmético:** GINJ R_gate pad A↔B (PTH) — highlight OK

**Checagem:** `python _check_mod8_now.py` → **MOD8 bloco OK**

## MOD9 — relés 2N7000 ×3 + SRD 12V (footprints only)

**Esquema:** `modulo/esquema-eletrico.md` §6 · Q20–Q22 + R50–R52 (1k) + R55–R57 (10k) + D20–D22 (1N4007) + RL1–RL3

**Posições PCB** (`POS_REL` — 3 colunas na zona 118–188 × 118–148):

| Canal | Q @ 128 | R_gate @ 120 | R_pd @ 124 | D @ 126 | RL @ 132 | saída NO |
|-------|---------|--------------|------------|---------|----------|----------|
| RL1 main | Q20 (122) | R50 | R55 | D20 (130) | RL1 (120) | RL_MAIN → **CN3-3** |
| RL2 bomba | Q21 (142) | R51 | R56 | D21 (150) | RL2 (140) | RL_PUMP → **CN3-2** |
| RL3 IAC | Q22 (162) | R52 | R57 | D22 (170) | RL3 (160) | RL_IAC → **CN3-1** |

**Feito**
- [x] 15 peças + rotas gate/bobina/flyback/+12V
- [x] **GRL1–3** → U1 L22I/L23I/L22O (PD10/PD8/PD9)
- [x] **RLx NO** → **CN3** pads 1–3 · pad 4 GND

**CN3** — PCIe-6 @ `(215.74, 121.10)` · `python _check_cn3_now.py`

**Nota:** CN1 pads **17–19 = NC** (relés só por CN3).

**Checagem:** `python _check_mod9_routes.py` · DRC GRL pad A↔B = cosmético

## MOD10 — CAN SN65HVD230 (footprints only)

**Esquema:** `modulo/esquema-eletrico.md` §8 · U6 + C40 (100nF) + C41 (10µF)

**Posições PCB** (`POS_CAN` — zona 118–158 × 18–38):

| Ref | Posição | Função |
|-----|---------|--------|
| U6 | **(134.5, 35)** rot 180° | SN65HVD230 |
| C40 | (128.5, 22) | 100nF decoupling |
| C41 | (134.5, 22) | 10µF bulk |

**Pads U6 (Injet:CAN):** TX→CAN_TX · RX→CAN_RX · VCC→+3V3 · GND · H→CANH · L→CANL

**MCU:** L6O PB8 CAN_RX · L6I PB9 CAN_TX · **CN1** pads **20–21** CANH/CANL

**Feito**
- [x] U6 + C40/C41 · decoupling pad A=+3V3 pad B=GND
- [x] CAN_TX/RX → U1 L6I/L6O (PB9/PB8)
- [x] CANH/CANL → CN1 20–21
- [x] +3V3 tronco y≈34,5 (cluster CAN + CN1-7)

**Checagem:** `python _check_mod10_now.py`

## MOD11 — Lambda MCP6004 + AD8628

**Esquema:** `modulo/esquema-eletrico.md` §7 · `06-sonda-lambda.md`

**Posições PCB** (sync 2026-08-08 — layout manual KiCad):

| Ref | Posição | Função |
|-----|---------|--------|
| U4 | (217.62, 73.69) rot −90° | MCP6004 — ch.A **VM** · ch.B **UN** |
| U5 | (225.3, 41.1) B.Cu | AD8628 malha **Ip** (2−/3+/6out) |
| C32/C33 | (217.7, 87) / (228, 81.5) | decoupling +5V |
| R76/R77 | (222.5, 65.5) / (218.5, 59.5) | bias Vm |
| R70 | (211.5, 36.75) | shunt 61R9 IP↔VM |
| R71/R78 | (215, 51.5) / (202, 68) | R_ESR + série Un/Ri |
| C30/C31 | (228, 51) / (209, 46.5) | filtros Ip / Un |

**MCU:** R13I PA4 VM ✓ · R13O PA5 IP ✓ · R14I PA6 UN ✓ · R5I PC0 RI_PULSE ✓

**Feito**
- [x] 11 peças + rotas internas op-amp/shunt/filtros
- [x] VM + IP + UN → U1 R13I/R13O/R14I

**DRC 2026-08-08 13:31** — bloco λ: ver abaixo (placa global **378** erros, −5 vs 13:06)

**DRC MOD11 (aceito para montagem)**
- [x] U5 pad 2 IP fechado · VM/UN stubs
- [ ] U5 clearance B.Cu 0,12 mm (6 erros) — footprint SMD · não elétrico
- [ ] Courtyard R70/R71/R78/C31 — opcional `_patch_fp_shapes.py`

**Checagem:** `python _check_mod11_now.py` → **OK**

## MOD12 — Aquecedor λ IRLZ44N

**Posições PCB** (sync 2026-08-08):

| Ref | Posição | Função |
|-----|---------|--------|
| R80 | (184, 31) | R_gate 100Ω |
| R81 | (195, 31) | R_gs 10k |
| Q30 | (203.2, 31) | IRLZ44N |
| D30 | (231, 25.5) | flyback |

**Feito**
- [x] 4 peças + nets Q30/R80/R81/D30
- [x] GHEAT → U1 **L21I** ✓ · CN2-1/2 ✓

**Feito**
- [x] GHEAT → U1 L21I · CN2-1/2 · Q30/D30

**DRC cosmético:** GHEAT split B.Cu — highlight OK

**Checagem:** `python _check_mod12_now.py` → **OK**

## DRC — snapshot 2026-08-10

| Tipo | Qtd | Ação |
|------|-----|------|
| Clearance U5 | 6 | Aceitar ou mover AD8628 B.Cu antes Gerber |
| Edge.Cuts | 1 | Fechar contorno placa |
| Unconnected | 16 | Cosmético — GRL/GINJ/TPS/MAP/CLT/IAT/RPM/GHEAT |
| Footprint | 0 | — |

Scripts: `_check_mod6_now.py` … `_check_mod12_now.py` · `_check_cn3_now.py` · `_review_routes.py`

## Pinout (referência)

**CN1** — ATX-24: 1-2 +12V_BAT · 3-5 GND · 6 +5V · 7 +3V3 · 8-11 sensores · 12 RPM_IN · 13-16 INJ · **17-19 NC** · 20-21 CAN · 22-24 aux

**CN2** — λ: 1 +12V_PROT · 2 H- · 3 IP · 4 VM · 5 UN · 6 NC

**CN3** — relés PCIe-6 @ `(215.74, 121.10)`: **1 RL_IAC · 2 RL_PUMP · 3 RL_MAIN** · 4 GND · 5-6 NC

Gravação: **USB/SWD na Black Board STM32** (sem conector na ECU)
