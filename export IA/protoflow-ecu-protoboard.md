# PROTOFLOW — ECU INJET RACING (layout protoboard)

> **Instrução para a IA Protoflow:** este arquivo é o brief completo para **gerar o desenho de montagem em protoboard (breadboard)**.
> Use apenas componentes **through-hole / módulos DIP / TO-220**. Ignore SMD quando houver alternativa THT.
> Produza: (1) mapa de zonas na protoboard, (2) lista de jumpers fio-a-fio, (3) rails de alimentação, (4) avisos de corrente/ruído.

---

## 0. Objetivo do projeto (1 parágrafo)

**INJET RACING Fase 1** — ECU de injeção eletrônica speed-density / batch-fire baseada em **STM32F407VET6 Black Board** (módulo pronto 3,3 V). Lê sensores (IAT, CLT, MAP, TPS), RPM pelo negativo/trigger da bobina (opto PC817), aciona **4 bicos** e **3 relés** via MOSFET low-side, condiciona **sonda lambda LSU 4.2** com op-amps (MCP6004 + AD8628), comunica por **CAN** (SN65HVD230). Alimentação: +12 V bateria → proteção → buck **+5 V** → LDO **+3,3 V**.

**Escopo desta protoboard:** eletrônica da ECU (não inclui bomba, flange, bung, mangueiras). Relés automotivos ficam **fora** da proto (só drivers na placa).

---

## 1. Regras de layout (obrigatórias para Protoflow)

1. **Protoboard sugerida:** 830 pontos ou maior (preferível 2× breadboard 830 juntas, ou protoboard 700+ furos perfurada com trilhas).
2. **Rails:** `+12V_PROT`, `+5V`, `+3V3`, `GND_S` (sinal), `GND_P` (potência). Unir `GND_S` e `GND_P` em **1 único ponto** (star ground) perto da entrada de alimentação.
3. **Zonas físicas (da esquerda → direita):**
   - **Z1 POWER** (fusível, IRF9540, TVS, bulk, buck 5 V, LDO 3V3)
   - **Z2 MCU** (STM32 Black Board + SWD)
   - **Z3 SENSORS** (pull-ups IAT/CLT, divisores MAP/O2, filtros 100 nF)
   - **Z4 RPM** (2×10k 2W + PC817 + 4k7 + 1nF) — **longe** dos MOSFET de potência
   - **Z5 CAN** (SN65HVD230)
   - **Z6 LAMBDA** (MCP6004 DIP + AD8628 + shunt 61R9 + R_ESR 6k8)
   - **Z7 INJ** (4× IRLZ44N + gates + flybacks) — **borda**, dissipação
   - **Z8 HEAT + RELAY** (1× IRLZ44N aquecedor + 3× 2N7000/AO3400 drivers)
4. **Corrente alta** (INJ drain, HEAT drain, +12V_PROT): fios **≥ 0,5–1,0 mm²** / jumpers grossos; NÃO usar trilhas finas da breadboard para drains dos bicos.
5. **AD8628** é SMD: usar **adaptador SOP-8 → DIP** se montar em protoboard.
6. **SN65HVD230** é SOIC-8: usar **adaptador SOIC→DIP** ou módulo CAN pronto 3,3 V.
7. Nunca ligar sinal 0–5 V direto no STM32 sem divisor (MAP/O2).
8. Flyback **1N4007** obrigatório em cada carga indutiva (bico / relé / aquecedor).

---

## 2. Resumo de pinout MCU (STM32F407 Black Board)

| Função | Pino STM32 | Direção | Notas |
|---|---|---|---|
| IAT | **PC9** (L16O) | ADC in | pull-up 2K26 → NTC → GND |
| CLT | **PC7** (L17O) | ADC in | pull-up 2K26 → NTC → GND |
| MAP | **PC11** (L12O) | ADC in | divisor 10k/18k do sinal 0–5 V |
| TPS | **PC8** (L17I) | ADC in | cursor do pote (pote alimentado em +3V3) |
| **PA4** | **DAC1 Vm** | out | terra virtual ~2,5 V (lambda) — **não usar como ADC** |
| Ip (lambda) | **PA5** | ADC in | queda no shunt 61R9 |
| Un (Nernst) | **PA6** | ADC in | célula Nernst |
| VBat | **PC6** (L18I) | ADC in | divisor 100k/10k de +12V (dead-time bicos) |
| RPM | **PE8** (R17O) | GPIO EXTI | falling edge (saída opto) |
| CAN1_RX | **PB8** | in | ← SN65HVD230 RXD |
| CAN1_TX | **PB9** | out | → SN65HVD230 TXD |
| INJ1 | **PE9** | out | → gate Q1 via 100 Ω |
| INJ2 | **PE11** | out | → gate Q2 via 100 Ω |
| INJ3 | **PE13** | out | → gate Q3 via 100 Ω |
| INJ4 | **PE15** (R21I) | out | → gate Q4 via 100 Ω |
| RL1 main | **PD8** | out | → gate Q7 via 1 kΩ |
| RL2 bomba | **PD9** | out | → gate Q8 via 1 kΩ |
| RL3 IAC | **PD10** | out | → gate Q9 via 1 kΩ |
| Heater PWM | **PD12** | out | → gate Q5 via 100 Ω |
| SWDIO / SWCLK | PA13 / PA14 | debug | header SWD |

> **Pinagem fixada (prodv6):** sensores J2 esq. PC9/7/11/8/6 · PA4 = DAC Vm · PA5 = Ip · PA6 = Un · λ no firmware a partir de Ip.

---

## 3. BOM protoboard (só eletrônica — THT / módulo)

### 3.1 Módulos / ICs

| Ref | Componente | Encaps. | Qtd | Função |
|---|---|---|---:|---|
| U1 | STM32F407VET6 **Black Board** | módulo headers | 1 | MCU |
| U2 | MCP6004 | **DIP-14** | 1 | op-amps wideband |
| U3 | AD8628 + adaptador SOIC→DIP | SOP-8→DIP | 1 | chopper Ip |
| U8 | REF3033 + breakout SOT-23 | SOT-23 | 1 | referência ADC 3,3 V |
| U4 | PC817 | DIP-4 | 1 | opto RPM |
| U5 | SN65HVD230 + adaptador **ou** módulo CAN 3V3 | SOIC→DIP | 1 | CAN |
| U6 | Módulo buck MP1584 / LM2596 | módulo | 1 | +12→+5 V (ajustar 5,00 V) |
| U7 | AMS1117-3.3 | SOT-223 em breakout **ou** módulo 3V3 | 1 | +5→+3V3 |

### 3.2 MOSFETs / diodos

| Ref | Componente | Encaps. | Qtd | Função |
|---|---|---|---:|---|
| Q1–Q4 | IRLZ44N | TO-220 | 4 | drivers INJ1–4 |
| Q5 | IRLZ44N | TO-220 | 1 | aquecedor lambda |
| Q6 | IRF9540 | TO-220 | 1 | proteção polaridade (P-CH) |
| Q7–Q9 | 2N7000 (THT) **ou** 2N7002 em adaptador | TO-92 | 3 | drivers relé |
| D10–D14, D20–D22 | 1N4007 | DO-41 | 8 | flyback INJ×4 + HEAT + RL×3 |
| D30 | 1N4148 | DO-35 | 1 | protege LED do PC817 |
| D1 | TVS P6KE33A / SMBJ33A | axial/SMB | 1 | load dump |
| D2 | Zener 12 V 0,5 W | DO-35 | 1 | gate Q6 |

### 3.3 Resistores

| Ref | Valor | Potência | Qtd | Função |
|---|---|---|---:|---|
| R60, R61 | 10 kΩ | **2 W** | 2 | série RPM (coil− → opto) |
| R62 | 4,7 kΩ | 1/4 W | 1 | pull-up coletor PC817 |
| R40, R41 | 2,26 kΩ (2K26) **1%** | 1/4 W | 2 | pull-up IAT / CLT |
| R42 | 10 kΩ **1%** | 1/4 W | 1 | divisor MAP (cima) |
| R43 | 18 kΩ **1%** | 1/4 W | 1 | divisor MAP (baixo) |
| R74 | 100 kΩ **1%** | 1/4 W | 1 | divisor VBat (cima) |
| R75 | 10 kΩ **1%** | 1/4 W | 1 | divisor VBat (baixo) |
| R76, R77 | 10 kΩ | 1/4 W | 2 | bias buffer Vm |
| R78 | 1 kΩ | 1/4 W | 1 | série AD8628 |
| R50–R53 | 1 kΩ | 1/4 W | 4 | série proteção ADC |
| R10–R13, R15 | 100 Ω | 1/4 W | 5 | gate INJ + HEAT |
| R20–R23, R25 | 10 kΩ | 1/4 W | 5 | pull-down gate MOSFET N |
| R30–R32 | 1 kΩ | 1/4 W | 3 | gate drivers relé |
| R1 | 100 kΩ | 1/4 W | 1 | gate IRF9540 |
| R70 | 61,9 Ω **1%** | 1/4 W | 1 | shunt Ip |
| R71 | 6,8 kΩ **1%** | 1/4 W | 1 | R_ESR (LSU 4.2) |
| R_term | 120 Ω | 1/4 W | 1 | terminação CAN (só se ponta do bus) |

### 3.4 Capacitores

| Ref | Valor | Qtd | Função |
|---|---|---:|---|
| C1 | 220 µF / 50 V eletrolítico | 1 | bulk +12 |
| C2 | 100 nF / 100 V | 1 | entrada |
| C3 | 10 µF | 1 | LDO in |
| C4 | 10 µF + 100 nF | 1+1 | LDO out |
| C10–C13 | 100 nF | 4 | filtro IAT CLT MAP TPS |
| C20 | 1 nF (102) | 1 | filtro RPM |
| C30, C31 | 220 nF | 2 | filtro Ip / Un |
| C32 | 100 nF + 10 µF | 2 | decoupling op-amps / CAN |
| — | 100 nF | ~6 | decoupling geral perto U1 rails |

### 3.5 Conectores / headers na proto

| Ref | Tipo | Função |
|---|---|---|
| J1 | bornes / header 24 vias (ATX-24 se couber) | chicote motor |
| J2 | header 6 vias (PCIe-6 ou bornes) | lambda LSU 4.2 |
| J3 | header 1×4 | SWD |
| F1 | porta-fusível 5 A | entrada ECU |
| F2 | porta-fusível 5 A | aquecedor λ |

---

## 4. Esquemas elétricos (nets) — copiar para Protoflow

### 4.1 POWER

```
BAT+12 ── F1(5A) ──┬── Source(Q6 IRF9540) 
                   │         Drain(Q6) = +12V_PROT
                   │         Gate(Q6) ── R1(100k) ── GND
                   │                   └── D2(zener12) cátodo no Gate, ânodo GND
                   │
                   ├── D1(TVS 33V) cátodo +12V_PROT, ânodo GND
                   ├── C1(220u/50V) + C2(100n) entre +12V_PROT e GND
                   │
                   ├── U6 buck VIN=+12V_PROT → VOUT=+5V (ajustar 5.00V)
                   │         caps in/out do módulo
                   │
                   └── U7 AMS1117 IN=+5V → OUT=+3V3
                             C3=10u IN, C4=10u+100n OUT → GND

U1 Black Board: pin +3V3 ← +3V3 ; pin GND ← GND_S
```

### 4.2 Sensores → ADC

```
IAT:
  +3V3 ── R40(2K26) ──●── R50(1k) ── PC9 (L16O)
                      │
                     J1.8 (IAT sensor)
                      │
                     GND
                      + C10(100n) PC9→GND

CLT: idem R41, C11, R51, PA1, J1.9

MAP:
  J1.10 (MAP 0-5V) ── R42(10k) ──●── R52(1k) ── PA2
                                 │
                               R43(18k)
                                 │
                                GND
                                 + C12(100n) PA2→GND
  MAP VCC ← +5V (J1.6) ; MAP GND ← GND_S (J1.5)

TPS:
  +3V3 → J1.7 → term.A pote
  GND  → term.B
  cursor J1.11 ── R53(1k) ── PC8 (L17I) + C13(100n)→GND
```

### 4.3 RPM (opto)

```
J1.12 RPM (coil− / trigger bobina) ── R60(10k 2W) ── R61(10k 2W) ──●── ânodo LED PC817(U4)
                                                                   │
                                                              D30 1N4148 (cátodo→ânodo LED, ânodo→cátodo LED = anti-paralelo)
                                                                   │
                                                            cátodo LED PC817 ── GND

PC817 coletor ──●── R62(4k7) ── +3V3
                │
                └── PE8 (R17O)  + C20(1nF)→GND
PC817 emissor ── GND

Firmware: EXTI falling edge em PE8 (R17O)
```

### 4.4 Drivers injetores (×4 iguais)

```
Para n=1..4:
  PE[n] ── R_gate(100) ── Gate(Qn IRLZ44N)
  Gate ── R_pd(10k) ── GND
  Source(Qn) ── GND_P
  Drain(Qn) ──●── J1.(12+n)  = INJn  (low-side do bico)
              │
              └── ânodo D_fly(1N4007) ; cátodo ── +12V_PROT

Bico no veículo: +12V_PROT ── bico(+) ; bico(−) ── INJn
```

### 4.5 Drivers relé (×3)

```
PD8 ── R30(1k) ── Gate Q7(2N7000) ; Source→GND_P ; Drain→ bobina RL1(−)
+12V_PROT ── bobina RL1(+) ; D20 flyback cátodo +12, ânodo Drain
PD9 → Q8 → RL2 bomba (idem)
PD10 → Q9 → RL3 IAC (idem)
Contatos dos relés NÃO entram na proto — só comando da bobina.
```

### 4.6 CAN

```
+3V3 ── U5 VCC ; GND ── U5 GND ; 100n+10u em VCC
PB9 (TX) ── U5 TXD
PB8 (RX) ── U5 RXD
U5 CANH ── J1.20
U5 CANL ── J1.21
(opcional) 120Ω entre CANH–CANL se esta ECU for ponta do barramento
```

### 4.7 Lambda DIY (LSU 4.2) — bloco simplificado

```
J2.1 H+  ← +12V_PROT via F2(5A)
J2.2 H−  ← Drain Q5(IRLZ44N)
         Gate Q5 ← PD12 via R15(100) ; R25(10k) Gate→GND ; Source→GND_P
         D14 flyback H− → +12V_PROT

J2.3 IP ──●── R70(61R9) ── J2.4 VM
           │
           └── medida → (via U3 AD8628) → PA5  + C30(220n)

J2.4 VM ← buffer MCP6004 a partir de DAC (~2,5 V)

J2.5 UN ── R71(6k8) ── (pulso Ri / filtro) → PA6  + C31(220n)

J2.6 NC

U2 MCP6004: VDD=+5V ; VSS=GND ; decoupling C32
U3 AD8628: +5V / GND ; adaptador DIP
```

> Detalhe fino dos pinos do MCP6004 (Vm buffer, filtros): seguir `modulo/06-sonda-lambda.md`. Na proto, agrupar U2+U3+R70+R71 juntos e fios curtos.

---

## 5. Conectores externos (pinagem exata)

### J1 — ATX-24 (chicote motor)

| Pino | Net | Pino | Net |
|---:|---|---:|---|
| 1 | +12V_IGN | 13 | INJ1 |
| 2 | +12V_BAT | 14 | INJ2 |
| 3 | GND_P | 15 | INJ3 |
| 4 | GND_P | 16 | INJ4 |
| 5 | GND_S | 17 | RL2 bomba (comando) |
| 6 | +5V | 18 | RL1 main (comando) |
| 7 | +3V3 | 19 | RL3 IAC (comando) |
| 8 | IAT | 20 | CANH |
| 9 | CLT | 21 | CANL |
| 10 | MAP | 22 | TACHO (opc) |
| 11 | TPS | 23 | START (opc) |
| 12 | RPM | 24 | SHIELD |

### J2 — PCIe-6 (lambda)

| Pino | Net |
|---:|---|
| 1 | H+ |
| 2 | H− |
| 3 | IP |
| 4 | VM |
| 5 | UN |
| 6 | NC |

### J3 — SWD

| Pino | Net |
|---:|---|
| 1 | +3V3 |
| 2 | SWDIO |
| 3 | SWCLK |
| 4 | GND |

---

## 6. Netlist condensada (para gerador de jumpers)

```
NET +12V_BAT: J1.2, F1.in
NET +12V_IGN: J1.1 (pode amarrar em +12V_BAT na proto de teste)
NET +12V_PROT: F1.out/Q6.D, C1+, D1.K, U6.VIN, D10..D14.K, D20..D22.K, F2.in, bobinas_rele+
NET +5V: U6.VOUT, U7.IN, J1.6, U2.VDD, U3.V+
NET +3V3: U7.OUT, U1.3V3, J1.7, R40, R41, R62, U5.VCC, J3.1, TPS_A
NET GND_P: Q1..Q5.S, Q7..Q9.S, C1-, D1.A, J1.3, J1.4
NET GND_S: U1.GND, sensores_GND, opto_GND, ADC_caps, J1.5, J3.4  [ligar GND_P↔GND_S em 1 ponto]
NET IAT: J1.8, R40.mid, R50 → PC9
NET CLT: J1.9, R41.mid, R51 → PA1
NET MAP: J1.10, R42 → div → R52 → PA2
NET TPS: J1.11, R53 → PC8
NET RPM_IN: J1.12 → R60 → R61 → U4.A
NET RPM_MCU: U4.C → PE8 (R17O)
NET INJ1..4: Drain Q1..Q4 → J1.13..16
NET RL1..3: Drain Q7..Q9 → J1.18,17,19
NET CANH/L: U5 → J1.20/21
NET H+: F2.out → J2.1
NET H-: Q5.D → J2.2
NET IP/VM/UN: J2.3/4/5 ↔ circuito U2/U3/R70/R71
```

---

## 7. O que a Protoflow deve entregar

1. **Vista top** da protoboard com zonas Z1–Z8 rotuladas.
2. **Tabela de jumpers:** `de | para | cor sugerida | comprimento relativo`.
3. **Lista de furos** ocupados por cada componente (ref → linhas/colunas da breadboard).
4. **Checklist de power-up:**
   - [ ] polaridade +12
   - [ ] medir +5 V e +3V3 antes de encaixar U1
   - [ ] gates MOSFET em 0 V no reset (pull-downs)
   - [ ] opto: LED não recebe +12 sem R60+R61
   - [ ] nenhum sinal >3,3 V em pinos ADC do STM32

---

## 8. Fora da protoboard (não desenhar na breadboard)

- 4× bico Bosch 0280156086, bomba, regulador 3 bar, filtros
- Sensores IAT/MAP/TPS/CLT (só conectores/bornes na proto)
- Sonda LSU 4.2 0258007351 + bung
- Relés 30 A (só bobina comandada pelos drains Q7–Q9)
- Caixa, chicote longo, CNC/PCB final

---

## 9. Referências do repositório (contexto)

| Arquivo | Conteúdo |
|---|---|
| `modulo/esquema-eletrico.md` | esquemas por bloco |
| `modulo/lista-componentes.md` | BOM completo + preços |
| `modulo/pcb-bom-codigos.md` | códigos silk PCB |
| `assets/ecu-pcb-1layer-netlist.md` | netlist PCB 1-layer |
| `modulo/06-sonda-lambda.md` | detalhe LSU 4.2 |

---

**Fim do brief Protoflow.** Priorize clareza de jumpers e separação potência/sinal. Não invente componentes fora desta lista.
)
