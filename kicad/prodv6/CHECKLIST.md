# ProdV6 — PCB do zero (checklist)

Placa **240×160 mm**, **F.Cu + B.Cu**, esquemático = prodv5 (congelado).

## Regras

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

| # | Bloco | Status |
|---|--------|--------|
| 1 | Contorno + furos M3 + **CN1 CN2** | feito |
| 2 | GND pour F + B (zones) | **FEITO** — tecla **B** no KiCad |
| 3 | +12V_IN / +12V_PROT / proteção QREV | **FEITO** — tecla **B** → DRC |
| 4 | Buck MP1584 → **+5V** (C3–C6) | **FEITO** — +3V3 na Black Board |
| 5 | U1 JL-32F4XX (socket) + SWD | pendente |
| 6 | Sensores IAT CLT MAP TPS VBAT | pendente |
| 7 | RPM (PC817) | pendente |
| 8 | Injetores Q10–Q13 (4×) | pendente |
| 9 | Relés Q20–Q22 | pendente |
| 10 | CAN U6 | pendente |
| 11 | Lambda U4 U5 CN2 | pendente |
| 12 | Aquecedor Q30 | pendente |
| 13 | DRC final + silk + 3D | pendente |

## KiCad — cada sessão

1. Abrir `injet-racing-prodv6.kicad_pro`
2. PCB Editor → rotear só o bloco atual
3. **Inspect → Design Rules Checker** → salvar `DRC.rpt`
4. Enviar DRC antes de avançar

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

## Pinout (referência)

**CN1** — ATX-24: 1-2 +12V_IN · 3-5 GND · 6 +5V · 7 +3V3 · 8-11 sensores · 12 RPM_IN · 13-16 INJ · 17-19 relés · 20-21 CAN · 22-24 aux

**CN2** — λ: 1 +12V_PROT · 2 H- · 3 IP · 4 VM · 5 UN · 6 NC

Gravação: **USB/SWD na Black Board STM32** (sem conector na ECU)
