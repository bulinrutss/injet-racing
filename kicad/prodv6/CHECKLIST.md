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

Sensores no **J2** (coluna exterior quando possível) — prodv6 2026-08-11:

| Sensor | Pad U1 | MCU | mm @ U1(60.46,107.94) |
|--------|--------|-----|------------------------|
| IAT | **L12O** | PD0 | 60.46, 77.46 |
| CLT | **L16O** | PA9 | 60.46, 67.30 |
| MAP | **L17O** | PC9 | 60.46, 64.76 |
| TPS | **L18I** | PC8 | 63.00, 62.22 |
| VBAT | **L17I** | PA8 | 63.00, 64.76 |

- [x] Nets U1 J2 atribuídas · rotas condicionamento → pads (**`_check_mod6_now.py` OK**)
- [x] **CN1-4 +3V3** pull-ups R10/R11 · **CN1-3 +5V** MAP
- [x] Firmware `pins.h` PD0/PA9/PC9/PC8/PA8

**DRC cosmético MOD6:** TPS/MAP/CLT/IAT splits F↔B — highlight net OK

**Checagem:** `python _check_mod6_now.py`

## MOD7 — RPM PC817 (prodv6 2026-08-11)

**Posições PCB:**

| Ref | mm (at) | rot | Função |
|-----|---------|-----|--------|
| R20 | 93.5, 21.5 | 180° | série bobina 10k |
| R21 | 80.5, 21.5 | 180° | série bobina 10k |
| U7 | 67.19, 26.73 | 0° | PC817 |
| D3 | 67.14, 21.5 | −90° | 1N4148 — **A=GND, K=RPM_IN** |
| R22 | 81.65, 26.69 | −90° | pull-up 4k7 |
| C25 | 88, 32 | −90° | filtro 1nF |

**Feito**
- [x] CN1-22 → R20 → R21 → U7 pin1 (LED bobina)
- [x] D3 anti-paralelo LED (A=GND · K=RPM_IN)
- [x] U7 pin4 → R22/C25 → **R17O** @ (110.46, 64.76)
- [x] Opto isolado (pin1 ⊥ pin4)

**Checagem:** `python _check_mod7_now.py` → **MOD7 completo**

## MOD8 — injetores IRLZ44N ×4 (prodv6 2026-08-11)

**Esquema:** `modulo/esquema-eletrico.md` §5 · Q10–Q13 + R30–R33 (100R) + R40–R43 (10k) + D10–D13 (1N4007)

**Posições PCB:**

| Canal | Q | R_gate | R_gs | D |
|-------|---|--------|------|---|
| INJ1 | Q10 (174.04, 8) | R30 (142.70, 41.80) | R40 (174.5, 15) | D10 (162.5, 14) |
| INJ2 | Q11 (153.80, 11.02) | R31 (144.61, 31.39) | R41 (154, 18.5) | D11 (142.5, 17) |
| INJ3 | Q12 (132.80, 14.52) | R32 (125.5, 44) | R42 (133, 22) | D12 (120, 20.5) |
| INJ4 | Q13 (111.80, 17.52) | R33 (112, 44) | R43 (112, 24.5) | D13 (100, 23.5) |

**Feito**
- [x] **R18I–R21I** → R30–R33 (GINJ1–4)
- [x] Gate · GND · dreno · flyback K→+12V_PROT
- [x] **CN1 13–16** → drenos INJ1–4

**Checagem:** `python _check_mod8_now.py` → **MOD8 completo**

## MOD9 — relés driver 2N7000 ×3 (relé SRD **externo**)

**Esquema:** §6 · Q20–Q22 + R50–R52 + R55–R57 + D20–D22 · **RL1–3 @ y≈227 NÃO montar** · **CN3 @ y≈236** chicote cargas

| Canal | Pad U1 | Driver | Net bobina | CN3 NO |
|-------|--------|--------|------------|--------|
| RL1 main | **L22I** | Q20 | RL1 | pad **3** RL_MAIN |
| RL2 bomba | **L23I** | Q21 | RL2 | pad **2** RL_PUMP |
| RL3 IAC | **L22O** | Q22 | RL3 | pad **1** RL_IAC |

Bobina externa: **+12V_PROT** + net **RLx** no **Q.D** · flyback **D.K→+12V_PROT**

**Feito**
- [x] RL1/RL2/RL3 driver + U1 + CN3 nets OK

**Checagem:** `python _check_mod9_now.py` → **completo**

**Checagem:** `python _check_mod9_now.py`

## MOD10 — CAN SN65HVD230 — **DESATIVADO** (2026-08-11)

U6/C40/C41 fora do build atual · sem checagem.

## MOD11 — Lambda MCP6004 + AD8628 (prodv6 2026-08-11)

| Ref | @ PCB | Função |
|-----|-------|--------|
| U4 | (174.62, 63) | MCP6004 — ch.A VM · ch.B UN |
| U5 | (159.8, 88) B.Cu | AD8628 Ip |
| CN2 | (171, 45.5) | PCIe-6 sonda |

**U1:** **R13I** VM · **R13O** IP (+ **R12O** trilha) · **R14I** UN · **R5I** RI_PULSE

**CN2 real:** 1=+12V_PROT · 2=H− · **3=NC** · **4=IP** · **5=VM** · **6=UN**

**Feito**
- [x] VM/IP/UN → U1 + CN2-4/5/6
- [x] R5I → R71 RI_PULSE
- [x] R70 shunt IP-VM · R78↔R71 RI_PULSE

**Checagem:** `python _check_mod11_now.py` → **completo**

## MOD12 — aquecedor λ IRLZ44N (prodv6 2026-08-11) — FEITO

| Ref | @ | Função |
|-----|---|--------|
| R80 | (121.1, 67.3) | gate série GHEAT |
| R81 | (132.4, 67.1) | pull-down 10k |
| Q30 | (140.2, 67.0) | IRLZ44N |
| D30 | (182.5, 47.5) | flyback 1N4007 |

**U1 R16I** GHEAT · **CN2** 1=+12V_PROT · 2=H−

**Checagem:** `python _check_mod12_now.py` → **completo**

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
