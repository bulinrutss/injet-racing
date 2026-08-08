# ProdV6 — PCB do zero (checklist)

Placa **240×160 mm**, **F.Cu + B.Cu**, esquemático = prodv5 (congelado).

## Regras

- [ ] **Revisão de rotas** (conectividade + regras A/B caps) antes do DRC
- [ ] DRC **0 erros** no bloco antes do próximo
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
| 1 | Contorno + furos M3 + **CN1 CN2** | feito |
| 2 | GND pour F + B (zones) | **FEITO** — tecla **B** no KiCad |
| 3 | +12V_IN / +12V_PROT / proteção QREV | **FEITO** |
| 4 | Módulo MP1584 → **+5V** (C3–C6) | **FEITO** |
| 5 | Black Board JL-32F4XX 2×24 + REF3033 (C10–C12) | **FEITO** — rotas manuais KiCad · `_patch_mod5_close.py` · DRC bloco |
| 6 | Sensores IAT CLT MAP TPS VBAT | **cond. OK** · nets U1 J2 OK · **rotas → L* pendente** |
| 7 | RPM (PC817) | **FEITO** — bobina+opto+D3 · coletor → **R17O** PE8 |
| 8 | Injetores Q10–Q13 (4×) | **bloco OK** · CN1 13–16 pendente |
| 9 | Relés Q20–Q22 | pendente |
| 10 | CAN U6 | pendente |
| 11 | Lambda U4 U5 CN2 | pendente |
| 12 | Aquecedor Q30 | pendente |
| 13 | DRC final + silk + 3D | pendente |

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

**Pendente (STM J2 esquerda + limpeza DRC)**

Sensores no **J2** (coluna exterior quando possível) — prodv6 2026-08-07:

| Sensor | Pad U1 | MCU | mm @ U1(86,108) |
|--------|--------|-----|-----------------|
| IAT | **L16O** | PC9 | 86, 67.36 |
| CLT | **L17O** | PC7 | 86, 64.82 |
| MAP | **L12O** | PC11 | 86, 77.52 |
| TPS | **L17I** | PC8 | 88.54, 64.82 |
| VBAT | **L18I** | PC6 | 88.54, 62.28 |

- [x] Nets U1 J2 atribuídas (L12O MAP · L16O IAT · L17O CLT · L17I TPS · L18I VBAT)
- [ ] Rotear condicionamento → pads acima (DRC ainda reporta 5 ilhas sensor)
- [x] Firmware `pins.h` PC9/PC7/PC11/PC8/PC6
- [x] Apagar **stub MAP** órfão @ (138.54, 78) B.Cu (shorting DRC)
- [ ] Apagar **vias +3V3 inválidas** @ (73.5, 105.5)

**Checagem:** `python _check_mod6_now.py` (conectividade real) · `_review_routes.py` usa coords do gerador (ignorar MOD6).

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

**Feito (bloco MOD8 — sem CN1 bicos)**
- [x] U1 GINJ1–4 → R18I/R19I/R20I/**R21I** (PE9/11/13/15)
- [x] Gate R_gate → Q.G + R_gs → GND (zone)
- [x] Dreno Q.D + D_fly A · D.K → +12V_PROT
- [x] Troncos INJx no dreno (stub leste; **CN1 não ligado**)

**Pendente / DRC esperado**
- [ ] **CN1 pads 13–16** → tronco INJ (usuário deixou pra depois)
- [ ] Stubs **GINJ** DRC: curto **R_gate pad A** ↔ trilha (ex. 160,91 ↔ R30 @ 166,91) — conferir cobre nos 4 R30–R33
- [ ] Via **+12V_PROT** @ (231.5, 96) dangling — ligar barra flyback leste
- [ ] Apagar trilhas INJ **dangling** norte (233.5,122 etc.) se forem sobra de teste

**Checagem:** `python _check_mod8_now.py` → bloco OK · CN1 = pendente

## MOD9 — relés 2N7000 ×3 + SRD 12V (footprints only)

**Esquema:** `modulo/esquema-eletrico.md` §6 · Q20–Q22 + R50–R52 (1k) + R55–R57 (10k) + D20–D22 (1N4007) + RL1–RL3

**Posições PCB** (`POS_REL` — 3 colunas na zona 118–188 × 118–148):

| Canal | Q @ 128 | R_gate @ 120 | R_pd @ 124 | D @ 126 | RL @ 132 | saída NO |
|-------|---------|--------------|------------|---------|----------|----------|
| RL1 main | Q20 (122) | R50 | R55 | D20 (130) | RL1 (120) | RL_MAIN → CN1-18 |
| RL2 bomba | Q21 (142) | R51 | R56 | D21 (150) | RL2 (140) | RL_PUMP → CN1-17 |
| RL3 IAC | Q22 (162) | R52 | R57 | D22 (170) | RL3 (160) | RL_IAC → CN1-19 |

**Feito**
- [x] 15 footprints
- [x] Contorno MOD9 + portas `->U1` · `CN1 17-19` · `+12V_PROT`
- [x] Nets nos pads: GRL* gate · RL* bobina · RL_MAIN/RL_PUMP/RL_IAC contatos
- [x] **Rotas internas 3 canais** (gate + bobina + flyback + GND + +12V + stub NO) — DRC 2026-08-08

**Pendente**
- [ ] **GRL1–3** → U1 L23I/L22O/L22I (pads U1 ainda RL1–3)
- [ ] **RL_MAIN/RL_PUMP/RL_IAC** → CN1 pads 17–19

**Checagem:** `python _check_mod9_routes.py` (interno) · U1/CN1 = depois

## MOD10 — CAN SN65HVD230 (footprints only)

**Esquema:** `modulo/esquema-eletrico.md` §8 · U6 + C40 (100nF) + C41 (10µF)

**Posições PCB** (`POS_CAN` — zona 118–158 × 18–38):

| Ref | Posição | Função |
|-----|---------|--------|
| U6 | (126, 20) | SN65HVD230 — TX/RX/VCC/GND/H/L |
| C40 | (120, 26) | 100nF decoupling |
| C41 | (120, 18) | 10µF bulk |

**Pads U6 (Injet:CAN):** TX→CAN_TX · RX→CAN_RX · VCC→+3V3 · GND · H→CANH · L→CANL

**MCU:** L6O PB8 CAN_RX · L6I PB9 CAN_TX · **CN1** pads **20–21** CANH/CANL

**Feito**
- [x] 3 footprints (sem trilhas)
- [x] Contorno MOD10 + portas `->U1` · `CN1 20-21` · `+3V3`

**Pendente**
- [ ] CAN_TX/RX → U1 L6I/L6O
- [ ] +3V3 tronco + caps só pad A · GND zone pad B
- [ ] CANH/CANL → CN1 pads 20–21

**Checagem:** `python _check_mod10_now.py` → footprints OK

## MOD11 — Lambda MCP6004 + AD8628 (footprints only)

**Esquema:** `modulo/esquema-eletrico.md` §7 · U4 + U5 + R70–R78 + C30–C33 · **U8 REF3033 no MOD5** · **CN2 já no PCB**

**Posições PCB** (`POS_LAMBDA` — zona 158–218 × 24–78):

| Ref | Posição | Função |
|-----|---------|--------|
| U4 | (183.19, 45.88) | MCP6004 DIP-14 |
| U5 | (200.50, 47.00) | AD8628 SOIC-8 **B.Cu** |
| C32/C33 | (180.12, 38.62) / (164.50, 41.00) | decoupling +5V |
| R76/R77 | (171.12, 59.50) / (171.50, 68.50) | bias Vm |
| R70/R71 | (192.50, 67.00) / (192.50, 73.00) | shunt Ip · R_ESR 6k8 |
| R78 | (204.50, 53.00) | série AD8628 |
| C30/C31 | (206.50, 59.00) / (210.50, 65.00) | filtros Ip / Un |

**MCU:** R13I PA4 VM · R13O PA5 IP · R14I PA6 UN · **CN2** pads 1–5 (+12V_PROT · H− · IP · VM · UN)

**Feito**
- [x] 11 footprints (sem trilhas)
- [x] Contorno MOD11 + portas `->U1` · `CN2` · `+5V`

**Pendente**
- [ ] VM/IP/UN → U1 R13I/R13O/R14I
- [ ] IP/VM/UN → CN2 pads 3–5 · +12V_PROT pad 1
- [ ] +5V tronco + C32/C33 só pad A · GND zone pad B
- [ ] Malha op-amp (pads U4/U5 sem net)

**Checagem:** `python _check_mod11_now.py` → footprints OK

## MOD12 — Aquecedor λ IRLZ44N (footprints only)

**Esquema:** `modulo/esquema-eletrico.md` §7 · Q30 + R80 (100Ω) + R81 (10k) + D30 flyback

**Posições PCB** (`POS_HEAT` — faixa norte MOD11, 162–212 × 24–38):

| Ref | Posição | Função |
|-----|---------|--------|
| R80 | (174, 30) | R_gate 100Ω |
| Q30 | (188, 30) | IRLZ44N — G→GHEAT · D→H− · S→GND |
| R81 | (188, 24) | R_gs 10k pull-down |
| D30 | (198, 28) | flyback 1N4007 A=H− K=+12V_PROT |

**MCU:** L21I PD12 **GHEAT** · **CN2** 1=+12V_PROT · 2=H−

**Feito**
- [x] 4 footprints (sem trilhas)
- [x] Contorno MOD12 + portas `->U1` · `CN2 1-2` · `+12V_PROT`

**Pendente**
- [ ] GHEAT → U1 L21I (pad U1 pode estar net H− — renomear ao rotear)
- [ ] H− → CN2 pad 2 · +12V_PROT → CN2 pad 1

**Checagem:** `python _check_mod12_now.py`

## Pinout (referência)

**CN1** — ATX-24: 1-2 +12V_IN · 3-5 GND · 6 +5V · 7 +3V3 · 8-11 sensores · 12 RPM_IN · 13-16 INJ · 17-19 relés · 20-21 CAN · 22-24 aux

**CN2** — λ: 1 +12V_PROT · 2 H- · 3 IP · 4 VM · 5 UN · 6 NC

Gravação: **USB/SWD na Black Board STM32** (sem conector na ECU)
