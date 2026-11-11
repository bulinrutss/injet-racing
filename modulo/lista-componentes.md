# Lista de Componentes / BOM — INJET RACING (Fase 1)

> Documento vivo. Consolida **todas as peças e componentes** citados nos arquivos:
> `dicas.md`, `04-bicos-injetores.md`, `05-sensores.md`, `06-sonda-lambda.md`, `00-hardware.md` + decisões de conversa.
> **Legenda de status:** ✅ confirmado · 🟡 opcional/recomendado · ⬜ a definir/medir · ❌ **não comprar** (já vem na Black Board).
> **Coluna "Buscar como":** texto curto para colar em marketplace (Mercado Livre / Shopee / Amazon / AliExpress). Prefira lojas com boa reputação para peças automotivas/eletrônicas.

---

## 0. Configuração confirmada (sua montagem)

| Decisão | O que significa |
|---|---|
| **MCU** | Placa comercial **STM32F407VET6 Black Board** (módulo com headers/USB) — **não** é o chip solto |
| **Fonte** | **Na própria placa ECU:** 12 V bateria → proteção → **buck +5 V** → alimenta MAP, lambda e **entrada 5 V da Black Board** |
| **3,3 V lógica** | Gerado **dentro da Black Board** (LDO dela). **Distribuir +3V3** na fenolite (barra + caps) → TPS, NTC, opto, CAN, **CN1 pino 7** |
| **Buck Fase 1** | **Módulo MP1584** soldado na placa ECU (Opção A §7.2). TPS5430 discreto só se refazer PCB depois |

```
  +12V carro ──► [IRF9540 + TVS + fusível] ──► [Buck MP1584] ──► +5V ──┬── MAP
                                                                        ├── lambda (+5V)
                                                                        └── pin 5V da Black Board
                                                                                    │
                                                                              [LDO interno]
                                                                                    ▼
                                                                                 +3V3 ──► TPS, NTC, PC817...
```

> **Não depende** de USB/fonte de bancada no carro. USB só serve p/ gravar/debug na mesa.

---

## 1. Microcontrolador / placa (ver `00-hardware.md`)

| Item | Especificação | Qtd | Buscar como | Status |
|---|---|---|---|---|
| **Placa STM32F407** | **Black Board** com chip soldado, USB, cristal, headers 2,54 mm | 1 | `STM32F407VET6 Black Board` | ✅ **você já tem** |
| Gravador SWD | ST-Link V2 — só se USB da placa não gravar firmware | 1 | `ST-Link V2 STM32` | 🟡 |
| Pilha CR2032 + suporte | backup RTC (VBAT) | 1 | `pilha CR2032 com suporte PCB` | 🟡 (só se usar RTC) |

> **Não comprar** chip LQFP100 solto — você usa a **placa comercial** encaixada na ECU via headers.

### 1.1 ❌ Não comprar — já vem na Black Board

| Item | Motivo |
|---|---|
| Cristal 8 MHz + caps 22 pF | Clock HSE onboard |
| Caps decoupling VDD do MCU (6× 100 nF, bulk 10 µF) | No módulo |
| NRST 100 nF, BOOT0 pull-down 10 kΩ | No módulo |
| **AMS1117-3.3 na placa ECU** | A Black Board já tem LDO 3,3 V (alimente ela em **+5 V**) |
| Header SWD 4 pinos | 🟡 opcional — placa já expõe SWD ou grava por USB |

---

## 2. Sensores do motor (ver `05-sensores.md`)

| Sensor | Peça | Tipo elétrico | Qtd | Buscar como | Status |
|---|---|---|---|---|---|
| **IAT** (temp. ar) | **Bosch 0280130085** | NTC ~2,5k @ 20 °C, 2 vias, push-in | 1 | `sensor IAT Bosch 0280130085` | ✅ |
| **MAP** (carga) | **Bosch 0279980411** (VW Gol 1 bar) | analógico 0–5 V, 3 vias | 1 | `sensor MAP Gol 0279980411` **ou** `MAP 1 bar VW` | ✅ |
| **TPS** (borboleta) | **Gol Mi 96-98** | potenciômetro 3 vias | 1 | `TPS Gol Mi 1996 1997 1998` | ✅ |
| **CLT** (temp. água) | **60513205** (GM/Fiat) | NTC ~2,5k @ 20 °C, 2 vias | 1 | `sensor temperatura agua 60513205 GM Fiat` | ✅ |
| **O2 / Lambda** | **LSU 4.2 0258007351** (padrão, 5 fios) ou **4.9 0258017025** + op-amps DIY | wideband, M18×1,5 | 1 | ver §5b | ✅ |

**Conectores dos sensores (chicote):**

| Item | Especificação | Qtd | Buscar como |
|---|---|---|---|
| Conector IAT / CLT (2 vias) | JPT ou similar | 2 | `conector chicote sensor temperatura 2 vias VW` |
| Conector MAP (3 vias) | conector Bosch 3 vias | 1 | `conector sensor MAP Gol 3 vias` |
| Conector TPS (3 vias) | conector VW 3 vias | 1 | `conector TPS Gol Mi 3 vias` |

---

## 3. Bicos injetores e combustível (ver `04-bicos-injetores.md`)

| Item | Especificação | Qtd | Buscar como | Status |
|---|---|---|---|---|
| **Bicos injetores** | **Bosch 0280156086** — 28 lb/h (296 cc/min) @ 3 bar, alta impedância **12 Ω** | 4 | `bico injetor Bosch 0280156086` **ou** `bico Bosch 28 lb` | ✅ |
| Chicote / conector dos bicos | EV1 (conector padrão Bosch antigo) | 4 | `conector bico injetor EV1 Bosch` | ✅ |
| Bomba de combustível | Elétrica alta pressão (**Bosch 040/044** externa ou de tanque) | 1 | `bomba combustivel Bosch 044` **ou** `bomba GTI externa` | ⬜ |
| Regulador de pressão | **3 bar, com retorno** | 1 | `regulador pressao combustivel 3 bar com retorno` | ✅ |
| Filtro alta pressão | injeção eletrônica | 1 | `filtro combustivel injecao eletronica` | ⬜ |
| Pré-filtro (tela sucção) | tela da bomba | 1 | `pre filtro tela bomba combustivel` | ⬜ |
| Linhas de combustível | mangueira alta pressão injeção (7,5 mm ida / 6,5 mm retorno) | 2 m | `mangueira combustivel injecao eletronica 7,5mm` | ⬜ |
| O-rings dos bicos | vedação combustível + lado do ar (Viton) | 8 | `o-ring bico injetor Bosch Viton kit` | ⬜ |

---

## 4. Condicionador de sinal de RPM — negativo da bobina (ver `esquema-eletrico.md` §4)

> **Escolher UMA das duas versões abaixo** (não montar as duas). A §4.1 (opto) é a escolha ✅ do projeto pelo isolamento galvânico. A §4.2 fica de referência histórica.

### 4.1 Versão isolada por opto — **ESCOLHIDA** ✅

| Ref | Componente | Valor | Qtd | Buscar como |
|---|---|---|---|---|
| R1, R2 | Resistor **2 W** | **10 kΩ** | 2 | `resistor 10k 2W` |
| R3 | Resistor 1/4 W | **4,7 kΩ** 5% | 1 | `resistor 4k7 1/4W` (usa do kit) |
| D1 | Diodo | **1N4148** | 1 | `diodo 1N4148` |
| U1 | Optoacoplador | **PC817** (ou 4N25) | 1 | `optoacoplador PC817` |
| C1 | Capacitor cerâmico | **1 nF disco 50 V** (código 102) | 1 | `capacitor ceramico 1nF 102 disco 50V` |

### 4.2 Versão alternativa a transistor 🟡 — **NÃO COMPRAR** (referência apenas)

| Ref | Componente | Valor | Qtd | Buscar como |
|---|---|---|---|---|
| R1 | Resistor **1 W** | 33 kΩ | 1 | `resistor 33k 1W` |
| Dz | Diodo zener | 5V6 (1/2 W = 500 mW) | 1 | `diodo zener 5V6 1/2W` |
| R2 | Resistor 1/4 W | 4,7 kΩ | 1 | `resistor 4k7 1/4W` |
| Q1 | Transistor NPN | BC547B | 1 | `transistor BC547B` |
| R3 | Resistor 1/4 W | 1 kΩ | 1 | `resistor 1k 1/4W` |
| C1 | Capacitor cerâmico | 1 nF disco 50 V (código 102) | 1 | `capacitor ceramico 1nF 102 disco 50V` |

---

## 5. Interface dos sensores com o ADC do STM32 (3,3 V)

| Item | Valor | Onde | Qtd | Buscar como | Status |
|---|---|---|---|---|---|
| Resistor pull-up NTC | **2,26 kΩ** 1% (2K26) | IAT e CLT — firmware: `R_PULLUP = 2260.0f` | 2 | `resistor 2K26 1% 1/4W` | ✅ |
| Capacitor de filtro ADC | **100 nF** cerâmico | cada pino analógico (IAT, CLT, MAP, TPS, Ip, Un, VBat) | 7+ | `capacitor ceramico 100nF 104` | ✅ |
| Divisor de tensão (R1) | **10 kΩ** 1% | MAP (5 V → 3,3 V) | 1 | `resistor 10k 1% SMD` | ✅ |
| Divisor de tensão (R2) | **18 kΩ** 1% | MAP (5 V → 3,3 V) | 1 | `resistor 18k 1% SMD` | ✅ |
| Divisor VBat (R1) | **100 kΩ** 1% | +12V → ADC PC1 | 1 | `resistor 100k 1%` | ✅ |
| Divisor VBat (R2) | **10 kΩ** 1% | VBat → GND | 1 | `resistor 10k 1%` | ✅ |
| Diodo de clamp | **BAT54S** (dual schottky) | cada entrada ADC | por pino | `diodo BAT54S SMD SOT-23` | 🟡 |
| Resistor série de proteção | **1 kΩ** | IAT, CLT, MAP, TPS, Ip, Un, VBat (7 entradas ADC) | **7** | `resistor 1k SMD 0805` | ✅ |

> **Kits práticos:** vale mais a pena comprar **kit variado de resistores 1% SMD 0805** e **kit variado de capacitores cerâmicos 0805** do que peças avulsas. Custa ~R$ 50–80 e cobre a placa toda.

---

## 5b. Sonda lambda wideband DIY — LSU **4.2** (padrão) / 4.9 (opcional)

> **Sem CJ125.** STM32 + **MCP6002** + **OPA388IDR**. Ver `06-sonda-lambda.md` e `esquema-eletrico.md` §7.
> **Padrão do projeto:** LSU **4.2** `0258007351` (**5 fios**), conector placa **PCIe 6 pinos**, R_ESR **6,8 kΩ**, Ri≈80 Ω + free-air no FW.

### Lista de compra — circuito comum (serve 4.2 e 4.9)

| Item | Especificação | Qtd | Buscar como | Status |
|---|---|---|---|---|
| **Op-amp dual RRIO** | **MCP6002-I/P** DIP-8 | 1 | `MCP6002 DIP` | ✅ |
| **Op-amp zero-drift** | **OPA388IDR** | 1 | `OPA388IDR` | ✅ |
| **Adaptador SOIC→DIP** | SOIC-8 → DIP-8 | 1 | `adaptador SOIC8 DIP` | ✅ |
| **Referência ADC** | **REF3033** 3,3 V | 1 | `REF3033 3.3V` | ✅ |
| Shunt Ip | **61,9 Ω** 1% | 1 | `resistor 61R9 1%` | ✅ |
| R bias Vm | **10 kΩ** | 2 | `resistor 10k` | ✅ |
| R série OPA388IDR | **1 kΩ** | 1 | `resistor 1k` | ✅ |
| MOSFET aquecedor | **IRLZ44N** | 1 | `MOSFET IRLZ44N` | ✅ |
| D flyback aquecedor | **1N4007** | 1 | `diodo 1N4007` | ✅ |
| R gate aquecedor | **100 Ω** | 1 | (kit) | ✅ |
| R pull-down gate aquecedor | **10 kΩ** | 1 | (kit) | ✅ |
| Caps filtro Ip/Un ADC | **100 nF** | 2 | PA5 + PA6 | (kit) | ✅ |
| Caps filtro Un/Ip (op-amp) | **220 nF** | 2 | C30 + C31 | (kit) | ✅ |
| Caps decoupling +5V op-amp | **100 nF + 10 µF** | 1+1 | C32 | (kit) | ✅ |
| Fusível aquecedor | 3–5 A | 1 | `porta fusivel automotivo 5A` | 🟡 |
| **Bung** | M18×1,5 inox + plug | 1 | `bung sonda lambda M18x1,5 inox` | ✅ |
| Anti-seize | pasta cobre | 1 | `anti seize cobre sonda lambda` | 🟡 |
| Chicote | 0,5 mm² + 1,0 mm² | 1,5 m | `fio automotivo 0,5mm 1mm` | ✅ |

### Sonda + conector + R_ESR

| Opção | Sonda | Conector | R_ESR | Buscar como | Status |
|---|---|---|---|---|---|
| **A — padrão** | LSU **4.2** `0258007351` (5 fios) | **PCIe 6 pinos** (placa) | **6,8 kΩ** 1% | `sonda LSU 4.2 Bosch 0258007351` · `conector PCI-E 6 pinos` · `resistor 6k8 1%` | ✅ |
| **B — opcional** | LSU **4.9** `0258017025` | **PCIe 6 pinos** (placa) | **22 kΩ** 1% | `sonda LSU 4.9 Bosch 0258017025` · `conector PCI-E 6 pinos` · `resistor 22k 1%` | 🟡 |

> Padrão 4.2: firmware **Ri≈80 Ω** + **free-air**. Se 4.9: Ri≈300 Ω, sem free-air.

### Cancelar (não comprar)

| Item | Motivo |
|---|---|
| CJ125 | Substituído por op-amps |
| Passivos exclusivos do circuito CJ125 | Topologia diferente |

## 5c. Sensor VBat — dead-time dos bicos

> Divisor 100k/10k em +12V_PROT → **PC1** ADC. **Passivos já listados em §5** (linhas VBat) — esta seção é referência de ligação.
> Ver `esquema-eletrico.md` §3.4 e `04-bicos-injetores.md` §7.

| Item | Valor | Qtd | Onde na §5 / §13 | Status |
|---|---|---:|---|---|
| R_VBAT_hi | **100 kΩ** 1% | 1 | §5 linha VBat hi | ✅ |
| R_VBAT_lo | **10 kΩ** 1% | 1 | §5 linha VBat lo | ✅ |
| C filtro | **100 nF** | 1 | §5 caps ADC (+ C33 na PCB) | ✅ |
| R série ADC | **1 kΩ** | 1 | §5 proteção ADC (1 de 7) | ✅ |
| BAT54S (opc.) | clamp ADC | 1 | §5 clamp | 🟡 |

---

## 6. Saídas de potência — relés e drivers (3,3 V → 12 V)

| Ref | Item | Especificação | Qtd | Buscar como | Status |
|---|---|---|---|---|---|
| RL1 | Relé principal (ECU auto-hold) | automotivo 12 V, 20–30 A, 5 pinos | 1 | `rele automotivo 30A 12V 5 pinos` | ✅ |
| RL2 | Relé bomba de combustível | automotivo 12 V, 20–30 A | 1 | `rele automotivo 30A 12V 5 pinos` | ✅ |
| RL3 | Relé IAC / auxiliar | automotivo 12 V, 20 A | 1 | `rele automotivo 20A 12V` | 🟡 |
| — | Soquete p/ relé automotivo | 5 vias, com chicote | 3 | `soquete rele automotivo 5 vias com chicote` | ✅ |
| — | Driver dos relés | **2N7000** (THT, PCB) **ou** **AO3400** (SMD) | 3 | `transistor 2N7000` **ou** `MOSFET AO3400 SOT-23` | ✅ |
| — | Resistor de gate | **1 kΩ** | 3 | (usa do kit) | ✅ |
| — | **Diodo flyback bobina do relé** | **1N4007** | 3 | `diodo 1N4007` | ✅ |

### 6.1 Drivers dos bicos injetores (detalhado — ver `esquema-eletrico.md` §5)

| Ref | Item | Especificação | Qtd | Buscar como | Status |
|---|---|---|---|---|---|
| Q_inj1..4 | MOSFET low-side | **IRLZ44N** (TO-220) | 4 | `MOSFET IRLZ44N` | ✅ |
| R_gate | Resistor de gate | **100 Ω** 1/4 W | 4 | (usa do kit) | ✅ |
| R_gs | Pull-down do gate | **10 kΩ** 1/4 W | 4 | (usa do kit) | ✅ |
| D_flyback | Diodo flyback do bico | **1N4007** (cátodo p/ +12V_PROT) | 4 | `diodo 1N4007` | ✅ |
| Dissipador | opcional, se muitos bicos batch-fire | — | 1 | `dissipador TO-220 aluminio` | 🟡 |

---

## 7. Fonte de alimentação da ECU (ver `esquema-eletrico.md` §1)

### 7.1 Proteção de entrada (12 V da bateria)

| Item | Valor/Especificação | Qtd | Buscar como | Status |
|---|---|---|---|---|
| Porta-fusível de entrada | 5–7,5 A blade | 1 | `porta fusivel automotivo com fio` | ✅ |
| Fusível ECU | 5–7,5 A blade | 2 | `fusivel automotivo 5A blade` (comprar reserva) | ✅ |
| **MOSFET-P proteção reversa** | **IRF9540** (TO-220, VDS ≥ 60 V) | 1 | `MOSFET IRF9540 P-channel` | ✅ |
| Resistor gate do MOSFET-P | 47–100 kΩ 1/4 W | 1 | (usa do kit) | ✅ |
| Zener proteção do gate | **12 V** ou **15 V** 400 mW | 1 | `diodo zener 12V 400mW` | ✅ |
| **Diodo TVS load dump** | **SMBJ33A** ou **P6KE33A** (33 V) | 1 | `diodo TVS SMBJ33A automotivo` **ou** `P6KE33A` | ✅ |
| Capacitor bulk entrada | eletrolítico **220 µF / 50 V** low-ESR | 1 | `capacitor eletrolitico 220uF 50V low ESR` | ✅ |
| Capacitor cerâmico entrada | **100 nF / 100 V** | 1 | `capacitor ceramico 100nF 100V` | ✅ |
| Ferrite bead / indutor EMI | 100 Ω @ 100 MHz | 1 | `ferrite bead SMD 0805 100 ohm` | 🟡 |

### 7.2 Regulador 5 V (buck / step-down) — **na placa ECU** ✅

> **Confirmado:** fonte automotiva **própria** (12 V → 5 V). Não usar USB/fonte externa no carro.

**Opção A — módulo pronto (Fase 1 / sua montagem atual)** ✅

| Item | Valor | Qtd | Buscar como | Status |
|---|---|---|---|---|
| Módulo buck ajustável | MP1584 ou LM2596 (Vin até 40 V) | 1 | `mini modulo buck MP1584` | ✅ |
| Ajuste | Multímetro na saída → **5,00 V** antes de ligar MAP/Black Board | — | — | ✅ |

**Opção B — circuito discreto (PCB produto futuro)** 🟡 adiar

| Item | Valor | Qtd | Buscar como | Status |
|---|---|---|---|---|
| CI regulador buck | TPS5430 ou LM2596-ADJ SMD | 1 | `TPS5430 SMD` | 🟡 futuro |
| Indutor, SS34, caps feedback | ver §7.2 antigo | — | — | 🟡 futuro |

### 7.3 Regulador 3,3 V — **❌ não montar na placa ECU**

| Item | Status | Motivo |
|---|---|---|
| AMS1117-3.3 na fenolite | ❌ **não comprar** | Black Board gera +3V3 a partir do +5 V que você manda |
| MIC5219 alternativo | ❌ idem | — |

**Ligação:** buck **+5 V** → pino **5V** da Black Board · **GND** comum · pino **3V3** da Black Board → **barra +3V3_EC** na fenolite (10 µF + 100 nF) → sensores/CAN/opto/CN1.

### 7.4 Fusíveis (chicote)

| Circuito | Fusível | Buscar como |
|---|---|---|
| ECU (VBAT) | 5–7,5 A blade | `fusivel automotivo 5A blade` |
| Bomba | 15–20 A blade | `fusivel automotivo 15A blade` |
| Bicos | 10 A blade | `fusivel automotivo 10A blade` |
| IAC / aux | 10 A blade | `fusivel automotivo 10A blade` |
| Aquecedor lambda | 3–5 A blade | `fusivel automotivo 5A blade` |

---

## 8. Suporte do STM32 — só se usar **chip solto** (❌ não é seu caso)

> **Com Black Board:** pule quase toda esta seção. Mantenha só o que melhora **ADC analógico** na placa periférica.

| Item | Valor/Especificação | Qtd | Status c/ Black Board |
|---|---|---:|---|
| Cap. decoupling VDD MCU | 100 nF × 6 | 6 | ❌ no módulo |
| Cap. bulk MCU | 10 µF | 1 | ❌ no módulo |
| Filtro VDDA ferrite + 1 µF + 10 nF | — | 1+1+1 | ❌ no módulo |
| **Referência ADC (VREF+)** | **REF3033** 3,3 V | 1 | ✅ **comprar** — melhora Ip/Un/lambda (ligar ao VDDA/VREF+ da Black Board se acessível) |
| Cristal HSE 8 MHz + 22 pF ×2 | — | — | ❌ no módulo |
| Cristal LSE 32 kHz + 12 pF ×2 | — | — | 🟡 ❌ salvo RTC |
| NRST 100 nF, BOOT0 10 kΩ | — | — | ❌ no módulo |
| Header SWD | 4 pinos | 1 | 🟡 só se não usar USB |

---

## 8b. CAN — comunicação (painel / telemetria — ver `esquema-eletrico.md` §8)

| Item | Especificação | Qtd | Buscar como | Status |
|---|---|---|---|---|
| **Transceiver CAN** | **SN65HVD230** (3,3 V, SOIC-8) — recomendado | 1 | `SN65HVD230 CAN transceiver SMD` | ✅ |
| Adaptador SOIC→DIP (CAN) | SOIC-8 → DIP-8 | 1 | `adaptador SOIC8 DIP` | 🟡 (protoboard) |
| Transceiver CAN alt. | TJA1050 (5 V, SOIC-8) | 1 | `TJA1050 CAN transceiver` | 🟡 |
| C decoupling | 100 nF + 10 µF | 1+1 | (usa do kit) | ✅ |
| Resistor terminação | **120 Ω** 1/4 W (só nas duas pontas do barramento) | 1 | `resistor 120R 1/4W` | 🟡 |
| TVS proteção CAN | **PESD1CAN** (SOT-23) | 1 | `PESD1CAN TVS CAN` | 🟡 |

---

## 9. Conector, chicote e caixa

| Item | Especificação | Qtd | Buscar como | Status |
|---|---|---|---|---|
| **CN1 — conector principal** | **ATX 24 pinos** (header placa-mãe ↔ fonte) | 1 | `conector ATX 24 pinos placa mae` / `header ATX 24 PCB` | ✅ |
| **CN2 — lambda** | **PCIe 6 pinos** (igual GPU); 5 sinais LSU 4.2 | 1 | `conector PCI-E 6 pinos` / `header PCIe 6 pin PCB` | ✅ |
| Ferramenta crimpagem ATX/PCIe | alicate terminais (se usar fio avulso) | 1 | `alicate crimpagem terminais` | 🟡 |
| Cabo blindado sinal RPM | 2 vias + malha (0,5 mm²) | 1 m | `cabo blindado 2x0,5mm automotivo` | ✅ |
| Fio automotivo 0,5 mm² | várias cores (sensores) | 5 m | `fio automotivo 0,5mm rolo` | ✅ |
| Fio automotivo 1,0 mm² | vermelho/preto (alimentação sensores) | 3 m | `fio automotivo 1mm rolo` | ✅ |
| Fio automotivo 2,5 mm² | vermelho (+12V VBAT) | 2 m | `fio automotivo 2,5mm rolo` | ✅ |
| Fio automotivo 4,0 mm² | vermelho (bomba) | 2 m | `fio automotivo 4mm rolo` | ✅ |
| Espaguete termorretrátil | kit variado | 1 kit | `kit espaguete termoretratil variado` | ✅ |
| Caixa (case) | alumínio 100×70×30 mm | 1 | `caixa aluminio projeto eletronico 100x70` | ✅ |
| Prensa-cabos (glands) | PG7 / PG9 | 2 | `prensa cabo PG7 PG9` | ✅ |
| **Fios jumper PCB 1-layer** | AWG28 ~15 cm cada | **~43** | `fio esmaltado 0.3mm` / `wire wrap` | ✅ (PCB fenolite) |
| Placa fenolite / FR1 | 200×100 ou 240×160 mm, 1 face | 1 | `placa fenolite cobre 200x100` | 🟡 (PCB DIY) |

---

## 10. Ferramentas de bancada (comprar avulso)

| Item | Uso no projeto | Buscar como |
|---|---|---|
| Multímetro | medir NTC, calibrar MAP/TPS, aferir 3,3 V | `multimetro digital com capacimetro` |
| Fonte de bancada 0–30 V | testar ECU sem carro | `fonte laboratorio 30V 5A` |
| Ferro de solda 60 W + estanho | montagem SMD (ponta fina) | `estacao solda 60W ponta fina` |
| Pasta de solda + ar quente | SMD (para o STM32 LQFP e SOICs) | `estacao ar quente + pasta solda SMD` |
| Osciloscópio ≥ 20 MHz | debug de RPM, PWM aquecedor | `osciloscopio 20MHz` (opcional, caro) |
| Kit resistores 1% SMD 0805 | todos os divisores/pull-ups | `kit resistor SMD 0805 1% variado` |
| Kit capacitores cerâmicos 0805 | decoupling geral (100 nF, 10 nF, 22 pF etc.) | `kit capacitor ceramico SMD 0805 variado` |
| Protoboard + jumpers | testes iniciais com STM32 Black Board | `kit protoboard jumpers` |

---

## 11. Pendências de compra / definição

- [x] MCU → **Black Board** (placa comercial, não chip solto)
- [x] Fonte ECU → **buck MP1584 na placa** (12 V → 5 V); **sem** AMS1117 extra
- [ ] Confirmar bomba de combustível (modelo) e filtros
- [x] Sonda lambda → **LSU 4.2 (0258007351, 5 fios)** + op-amps DIY (sem CJ125) — ver `06-sonda-lambda.md` / §5b
- [ ] Kit de resistores 1% SMD 0805 (cobre §5, §5b, §6, §8, §8b)
- [ ] Kit de capacitores cerâmicos SMD 0805 (cobre decoupling geral)
- [ ] Definir relés automotivos + soquetes
- [ ] Escolher CI do buck 5 V: **módulo MP1584 na placa ECU** ✅ (TPS5430 = futuro)
- [x] LDO 3,3 V → **usa o da Black Board** (não comprar AMS1117 p/ fenolite)
- [x] Referência ADC → **REF3033** (recomendado p/ lambda Ip/Un)
- [ ] Cristais: 8 MHz + (opcional) 32,768 kHz — comprar junto com caps de carga
- [ ] Conector **ATX 24** (CN1) + **PCIe 6** (CN2 lambda) + chicote
- [ ] Bung M18×1,5 aço inox + soldagem no coletor de escape (oficina)
- [ ] O-rings dos bicos e assentos na flange

---

## 12. Onde comprar (Brasil — sugestões por categoria)

| Categoria | Onde procurar |
|---|---|
| **Peças de motor / injeção** (bicos, sensores, sonda) | Kaizen Autopeças, Maturo, Casa da Injeção, desmanche VW/GM |
| **Módulo wideband pronto** | ODG, Octtane, FuelTech, RS Performance |
| **Componentes eletrônicos** | Mercado Livre (Baú da Eletrônica, Multcomercial, USINAINFO), AliExpress, Amazon BR, Farnell (BR) |
| **Conectores automotivos AMPSEAL, EV1, JPT** | Chicoteando Brasil, ML "conector automotivo TE Connectivity" |
| **Cristais + caps NP0** | Baú da Eletrônica, Multcomercial (evitar kits genéricos — cristais precisam ser confiáveis) |
| **Bung + solda** | oficina de escape local, ou pedir bung em ML e levar num soldador MIG/TIG |
| **Fio e chicote automotivo** | ML "fio automotivo rolo", auto peças local |

> ⚠️ **Cuidado com falsificações:** LSU 4.2 falsa no ML é comum. Preferir vendedor com nota fiscal Bosch, ou desmanche de Golf 1.8T com procedência.

---

## 13. LISTA TOTAL CONSOLIDADA (compra)

> Soma de **todas as partes** escolhidas no projeto.
> **Não inclui:** §4.2 transistor (RPM). **Padrão O2:** LSU **4.2** `0258007351` (**5 fios**). **🟡** = opcional.
> Colunas: **Valor / P/N** = especificação · **Buscar como** = colar no ML/Shopee · **≈ R$** = preço típico BR sem frete (meio da faixa).
> Totais por seção no título de cada bloco; resumo em **§13.10**.

### 13.1 MCU — **subtotal ≈ R$ 220** (Black Board já comprada)

| # | Componente | Valor / P/N | Buscar como | Qtd | ≈ R$ |
|---|---|---|---|---:|---:|
| 1 | Placa MCU | STM32F407VET6 Black Board | `STM32F407VET6 Black Board` | 1 | ✅ já tem |
| 2 | Gravador | ST-Link V2 | `ST-Link V2` | 1 | 🟡 30 |
| ~~3~~ | ~~Cristal HSE~~ | — | — | — | ❌ na placa |
| ~~4~~ | ~~Cap 22 pF~~ | — | — | — | ❌ na placa |
| 5 | Cristal LSE | 32,768 kHz | `cristal 32.768 kHz` | 1 | 🟡 5 |
| 6 | Cap carga LSE | 12 pF NP0 | `capacitor 12pF NP0` | 2 | 🟡 2 |
| 7 | Pilha + suporte | CR2032 | `pilha CR2032 suporte` | 1 | 🟡 8 |
| ~~8~~ | ~~Header SWD~~ | — | — | — | 🟡 USB basta |

### 13.2 Sensores e sonda — **subtotal ≈ R$ 1.050** (c/ λ 4.2) · **≈ R$ 470** (sem λ)

| # | Componente | Valor / P/N | Buscar como | Qtd | ≈ R$ |
|---|---|---|---|---:|---:|
| 9 | Sensor IAT | Bosch 0280130085 | `sensor IAT Bosch 0280130085` | 1 | 100 |
| 10 | Sensor MAP | Bosch 0279980411 | `sensor MAP 0279980411` | 1 | 200 |
| 11 | Sensor TPS | Gol Mi 96-98 | `TPS Gol Mi 96 98` | 1 | 90 |
| 12 | Sensor CLT | 60513205 | `sensor temperatura agua 60513205` | 1 | 70 |
| 13 ★ | Sonda lambda **4.2** | **0258007351** (5 fios) | `sonda lambda Bosch 0258007351 LSU 4.2` | 1 | **550** |
| 14 | Bung escape | M18×1,5 inox + plug | `bung sonda lambda M18x1.5 inox` | 1 | 50 |
| 15 | Anti-seize cobre | pasta cobre | `anti seize cobre sonda lambda` | 1 | 🟡 25 |

> Alternativa 4.9 (não padrão): `sonda lambda Bosch 0258017025 LSU 4.9` ≈ R$ 550–720.

### 13.3 Combustível / injeção — **subtotal ≈ R$ 1.300** (c/ bomba) · **≈ R$ 550** (só bicos+filtros)

| # | Componente | Valor / P/N | Buscar como | Qtd | ≈ R$ |
|---|---|---|---|---:|---:|
| 16 | Bico injetor | Bosch 0280156086 28 lb/h | `bico injetor Bosch 0280156086` | 4 | 400 |
| 17 | Conector bico EV1 | EV1 Bosch | `conector bico injetor EV1` | 4 | 60 |
| 18 | Bomba combustível | Bosch 040/044 | `bomba combustível Bosch 044` | 1 | ⬜ 550 |
| 19 | Regulador pressão | 3 bar c/ retorno | `regulador pressão combustível 3 bar retorno` | 1 | 200 |
| 20 | Filtro alta pressão | injeção | `filtro combustível alta pressão injeção` | 1 | 40 |
| 21 | Pré-filtro tela | tela sucção | `pré filtro combustível tela` | 1 | 20 |
| 22 | Mangueira injeção | 7,5 / 6,5 mm | `mangueira injeção 7.5mm` | 2 m | 40 |
| 23 | O-ring bico Viton | kit | `o-ring bico injetor Viton` | 8 | 20 |

### 13.4 Semicondutores — **subtotal ≈ R$ 160** (obrig.) · **≈ R$ 190** (c/ 🟡)

| # | Componente | Valor / P/N | Buscar como | Qtd | ≈ R$ |
|---|---|---|---|---:|---:|
| 24 | Op-amp dual RRIO | MCP6002-I/P | `MCP6002 DIP` | 1 | 12 |
| 25 | Op-amp zero-drift | OPA388IDR | `OPA388IDR` | 1 | 35 |
| 26 | Optoacoplador | PC817 | `PC817` | 1 | 2 |
| 27 | Transceiver CAN | SN65HVD230 | `SN65HVD230` | 1 | 18 |
| 28 | ~~LDO 3,3 V~~ AMS1117 | — | — | — | ❌ Black Board |
| 29 | Módulo buck 5 V | MP1584 / LM2596 | `módulo buck MP1584` | 1 | 12 |
| 30–31 | MOSFET-N | IRLZ44N | `IRLZ44N` | 5 | 20 |
| 32 | MOSFET-N relés | 2N7000 / AO3400 | `2N7000` | 3 | 6 |
| 33 | MOSFET-P | IRF9540 | `IRF9540` | 1 | 8 |
| 34 | Diodo sinal | 1N4148 | `1N4148` | 2 | 1 |
| 35 | Diodo flyback | 1N4007 | `1N4007` | **8** | 4 |
| 36 | Zener 12 V | 12 V 0,5 W | `diodo zener 12V 0.5W` | 1 | 1 |
| 37 | TVS | SMBJ33A | `SMBJ33A` | 1 | 5 |
| 38 | Clamp ADC | BAT54S | `BAT54S SOT-23` | 5 | 🟡 10 |
| 39 | TVS CAN | PESD1CAN | `PESD1CAN` | 1 | 🟡 8 |
| 40 | Ref. ADC | REF3033 | `REF3033` | 1 | 15 |
| 41 | Adaptador SOIC8→DIP | OPA388IDR | `adaptador SOIC8 DIP` | 1 | 8 |
| 41b | Adaptador SOIC8→DIP | SN65HVD230 (opc.) | `adaptador SOIC8 DIP` | 1 | 🟡 8 |

**§13.4b** (buck discreto no lugar do #29): `TPS5430` + `indutor 47uH` + `SS34` ≈ +R$ 30.

### 13.5 Resistores — **subtotal ≈ R$ 45**

| # | Componente | Valor / P/N | Buscar como | Qtd | ≈ R$ |
|---|---|---|---|---:|---:|
| 84 | Resistor potência | **10 kΩ 2 W** | `resistor 10k 2W` | 2 | 4 |
| 85 | Resistor 1% MAP div | **10 kΩ** 1% | `resistor 10k 1%` | 1 | 1 |
| 86 | Resistor pull-down gate | **10 kΩ** 1/4 W | `resistor 10k 1/4W` | 6 | 3 |
| 87 | Resistor 1% MAP div | **18 kΩ** 1% | `resistor 18k 1%` | 1 | 1 |
| 88 | Pull-up NTC | **2,26 kΩ (2K26)** 1% | `resistor 2.26k 1%` / `2K26` | 2 | 5 |
| 89 | Pull-up RPM opto | **4,7 kΩ** | `resistor 4.7k` | 1 | 1 |
| 90 | Resistor série ADC | **1 kΩ** | `resistor 1k` | 7 | 3 |
| 91 | Resistor gate INJ/HEAT | **100 Ω** | `resistor 100 ohm` | 5 | 2 |
| 92 | Resistor gate relé | **1 kΩ** | `resistor 1k` | 3 | 1 |
| 93 | Shunt Ip | **61,9 Ω** 1% | `resistor 61.9 ohm 1%` / `61R9` | 1 | 4 |
| 94 ★ | R_ESR (LSU **4.2**) | **6,8 kΩ** 1% | `resistor 6.8k 1%` / `6k8` | 1 | 2 |
| 95 | Gate IRF9540 | 47–100 kΩ | `resistor 47k` / `100k` | 1 | 1 |
| 96 | Terminação CAN | **120 Ω** | `resistor 120 ohm` | 1 | 🟡 1 |
| 97 | Divisor VBat hi | **100 kΩ** 1% | `resistor 100k 1%` | 1 | 2 |
| 98 | Divisor VBat lo | **10 kΩ** 1% | `resistor 10k 1%` | 1 | 1 |
| 99 | R bias Vm | **10 kΩ** | `resistor 10k` | 2 | 2 |
| 100 | R série OPA388IDR | **1 kΩ** | `resistor 1k` | 1 | 1 |
| — | Kit auxiliar | kit 1% 0805/THT | `kit resistor 1% 0805` | 1 | 20 |

> Se usar 4.9: R_ESR = **22 kΩ** (`resistor 22k 1%`) em vez do #50.

### 13.6 Capacitores — **subtotal ≈ R$ 40**

| # | Componente | Valor / P/N | Buscar como | Qtd | ≈ R$ |
|---|---|---|---|---:|---:|
| 101 | Cerâmico filtro ADC | **100 nF** (104) | `capacitor 100nF` | ≈22 | 8 |
| 102 | Cerâmico decoupling | **10 µF** | `capacitor 10uF 16V` | ≈6 | 6 |
| 103 | Cerâmico VDDA | **1 µF** | `capacitor 1uF` | 1 | 1 |
| 104 | Cerâmico VDDA | **10 nF** (103) | `capacitor 10nF` | 1 | 1 |
| 105 | Disco RPM | **1 nF** (102) | `capacitor 1nF disco` | 1 | 2 |
| 106 | Cerâmico filtro λ | **220 nF** (224) | `capacitor 220nF` | 2 | 2 |
| 107 | Eletrolítico bulk 12V | **220 µF / 50 V** | `eletrolítico 220uF 50V` | 1 | 5 |
| 108 | Cerâmico HV entrada | **100 nF / 100 V** | `capacitor 100nF 100V` | 1 | 2 |
| 109 | Filtro VBat ADC | **100 nF** | `capacitor 100nF` | 1 | 1 |
| 110 | NRST / BOOT0 | **100 nF** reset | `capacitor 100nF` | 1 | ❌ na Black Board |
| — | Kit auxiliar | kit 0805 | `kit capacitor cerâmico 0805` | 1 | 20 |

### 13.7 Indutores / ferrite — **subtotal ≈ R$ 5** (🟡)

| # | Componente | Valor / P/N | Buscar como | Qtd | ≈ R$ |
|---|---|---|---|---:|---:|
| 111 | Ferrite bead | 100 Ω @ 100 MHz | `ferrite bead 100 ohm` | 2 | 🟡 5 |

### 13.8 Relés, fusíveis, conectores — **subtotal ≈ R$ 520**

| # | Componente | Valor / P/N | Buscar como | Qtd | ≈ R$ |
|---|---|---|---|---:|---:|
| 62 | Relé 30 A | 12 V 5 pinos | `relé automotivo 30A 5 pinos 12V` | 2 | 40 |
| 63 | Relé 20 A | 12 V | `relé automotivo 20A 12V` | 1 | 🟡 15 |
| 64 | Soquete relé | 5 vias | `soquete relé 5 vias` | 3 | 30 |
| 65 | Fusível ECU | 5 A + porta | `porta fusível lâmina + fusível 5A` | 1+2 | 15 |
| 66 | Fusível bomba | 15–20 A | `fusível 15A lâmina` | 1 | 3 |
| 67 | Fusível bicos | 10 A | `fusível 10A lâmina` | 1 | 3 |
| 68 | Fusível IAC | 10 A | `fusível 10A lâmina` | 1 | 🟡 3 |
| 69 | Fusível aquecedor λ | 5 A + porta | `porta fusível + fusível 5A` | 1 | 12 |
| 70 | Conector IAT/CLT | 2 vias | `conector sensor temperatura 2 vias` | 2 | 20 |
| 71 | Conector MAP | 3 vias | `conector sensor MAP 3 vias` | 1 | 15 |
| 72 | Conector TPS | 3 vias | `conector TPS 3 vias` | 1 | 15 |
| 73 ★ | Conector λ PCIe-6 | header PCIe 6 pinos | `conector PCI-E 6 pinos` | 1 | **15** |
| 74 | Conector CN1 ATX-24 | header ATX 24 pinos | `conector ATX 24 pinos placa mae` | 1 | **25** |
| 75 | Prensa-cabo | PG7 / PG9 | `prensa cabo PG7` | 2 | 15 |
| 76 | Caixa | alumínio ~100×70×30 | `caixa alumínio 100x70x30` | 1 | 50 |
| 77 | Placa fenolite 1L | 240×160 mm | `placa fenolite cobre` | 1 | 🟡 40 |
| 78 | Fios jumper PCB | AWG28 ~15 cm | `fio esmaltado 0.3mm` | ~43 | 15 |

> Alternativa 4.9: conector `1928404687` ≈ R$ 80–150.

### 13.9 Fios e chicote — **subtotal ≈ R$ 100**

| # | Componente | Valor / P/N | Buscar como | Qtd | ≈ R$ |
|---|---|---|---|---:|---:|
| 77 | Cabo blindado | 2×0,5 mm | `cabo blindado 2x0.5mm` | 1 m | 15 |
| 78 | Fio sensores | 0,5 mm² | `fio automotivo 0.5mm` | 5 m | 20 |
| 79 | Fio alimentação | 1,0 mm² | `fio automotivo 1.0mm` | 4,5 m | 20 |
| 80 | Fio VBAT | 2,5 mm² | `fio automotivo 2.5mm` | 2 m | 15 |
| 81 | Fio bomba | 4,0 mm² | `fio automotivo 4.0mm` | 2 m | 20 |
| 82 | Termorretrátil | kit | `espaguete termorretrátil kit` | 1 | 15 |

---

### 13.10 Resumo de custo (padrão = LSU **4.2**)

| Seção | O que é | ≈ R$ | Faixa |
|---|---|---:|---|
| **13.1** | MCU + ST-Link + clock | **260** | 220–350 |
| **13.2** | Sensores + **LSU 4.2** + bung | **1.050** | 900–1.300 |
| **13.3** | Bicos + bomba + regulador + filtros | **1.300** | 800–2.000 |
| **13.4** | ICs, MOSFETs, diodos | **160** | 120–220 |
| **13.5** | Resistores (incl. **6k8** R_ESR) | **45** | 30–70 |
| **13.6** | Capacitores | **40** | 25–60 |
| **13.7** | Ferrite (🟡) | **5** | 0–10 |
| **13.8** | Relés, fusíveis, **ATX-24 + PCIe-6**, caixa | **400** | 300–550 |
| **13.9** | Fios | **100** | 70–150 |
| | | | |
| **TOTAL projeto completo** | c/ λ 4.2 + bomba | **≈ R$ 3.480** | **R$ 2.700 – 4.800** |
| **Sem sonda lambda** | −λ/−bung/−conector/−fusível heater | **≈ R$ 2.750** | |
| **Só eletrônica ECU** | placa + drive + caixa | **≈ R$ 900 – 1.200** | |
| **Já tem bomba/regulador** | − bomba+reg §13.3 | **− R$ 550 – 1.100** | |

> **LSU 4.2** tipicamente **R$ 550–680** (Bosch original). Frete / importação (OPA388IDR) **não** inclusos.

### 13.11 Contagem rápida

| Categoria | Qtd |
|---|---:|
| ICs / módulos | **8** (Black Board + MCP6002 + OPA388IDR + PC817 + SN65 + buck + REF3033 — **sem** AMS1117) |
| MOSFETs | **9** (5× IRLZ44N + 3× 2N7000 + 1× IRF9540) |
| Diodos | **≈18** (8× 1N4007 + 2× 1N4148 + TVS + zener + 🟡 BAT54S×5 + PESD1CAN) |
| Resistores (valores distintos) | **≈17** (+ kit) |
| Caps 100 nF | **≈22** (+ kit) |
| Sensores + sonda | **5** |
| Bicos | **4** |
| Relés | **2–3** |

### 13.12 Checklist de compra (copiar)

```
[ ] Black Board (já tenho) — alimentar com +5V do buck, GND comum, sinais nos headers
[ ] Buck MP1584 na placa ECU (12V → 5V) — NÃO AMS1117 separado
[ ] IAT 0280130085 · MAP 0279980411 · TPS Gol Mi · CLT 60513205
[ ] Sonda LSU 4.2 0258007351 (5 fios) + header PCIe 6 pinos + bung M18
[ ] Resistor R_ESR 6,8 kΩ 1%
[ ] 4× bico 0280156086 + 4× EV1
[ ] MCP6002 + OPA388IDR + adaptador SOIC8-DIP + 61R9 + REF3033
[ ] Divisor VBat 100k + 10k → PC1
[ ] R bias 10k×2 + R série 1k (lambda)
[ ] 8× 1N4007 (4 bicos + aquecedor λ + 3 relés) · 2× 1N4148
[ ] 3× 2N7000 (drivers relé) · 5× IRLZ44N · 1× IRF9540
[ ] PC817 · SN65HVD230 · buck MP1584 · REF3033
[ ] Adaptador SOIC8-DIP (OPA388IDR) · 🟡 2º adaptador (SN65 CAN)
[ ] 2× 10k 2W · 2× 2K26 · 1× 10k 1% · 1× 18k 1% · 100k+10k VBat
[ ] 7× 1k série ADC · 5× 100R gate · 6× 10k pull-down · 3× 1k gate relé
[ ] Kit resistor 1% + kit cap 100nF/10uF
[ ] 1nF disco · 2× 220nF λ · ~~cristal 8MHz~~ (só se chip solto no futuro)
[ ] ~43 fios jumper AWG28 (PCB 1-layer) · 🟡 placa fenolite
[ ] 2× relé 30A + soquetes · fusíveis 5/10/15A + porta λ heater
[ ] Header ATX-24 + PCIe-6 · fios 0.5/1/2.5/4 mm · caixa alumínio
```

---

## 14. Auditoria — circuito × BOM (vistoria)

> Cruzamento `esquema-eletrico.md` + `pcb-bom-codigos.md` (76 itens PCB) × esta lista.
> **Legenda:** ✅ listado · ⚠️ corrigido nesta revisão · 🟡 opcional · ⬜ pendente decisão

| Bloco | Componentes obrigatórios | Onde na lista | Status |
|---|---|---|---|
| **1. Proteção 12 V** | Fusível, IRF9540, R gate 100k, zener 12V, TVS 33V, C 220µF, C 100nF | §7.1 | ✅ |
| **2. Buck 5 V** | MP1584 (módulo) ou TPS5430+indutor+SS34 | §7.2 A ou B | ✅ |
| **3. LDO 3,3 V** | ~~AMS1117~~ — **na Black Board** | §7.3 | ❌ dispensado |
| **4. STM32 suporte** | ~~HSE, decoupling, NRST~~ — **na Black Board**; manter **REF3033** se ligar VREF+ | §8 | ⚠️ parcial |
| **5. REF3033** | REF3033 + breakout SOT-23 | §5b, §8, #40 | ✅ |
| **6. Sensores ADC** | 2×2K26, 1×10k+1×18k MAP, 7×100nF filtro, 7×1k série | §5 | ✅ |
| **7. VBat PC1** | 100k + 10k + 100nF (C33) | §5, §5c, #97–98, #109 | ✅ |
| **8. RPM opto** | PC817, 2×10k 2W, 4k7, 1N4148, 1nF | §4.1 | ✅ |
| **9. Bicos ×4** | 4× IRLZ44N, 4×100R, 4×10k PD, 4×1N4007 | §6.1 | ✅ |
| **10. Aquecedor λ** | 1× IRLZ44N, 100R, 10k PD, **1×1N4007**, fusível 5A | §5b | ⚠️ flyback explícito |
| **11. Relés ×3** | 3× relé + soquete, 3×2N7000, 3×1k gate, 3×1N4007 | §6 | ✅ |
| **12. Lambda op-amp** | MCP6002, OPA388IDR+adaptador, 61R9, 6k8 R_ESR, R76/R77 10k, R78 1k, C30/C31 220n, C32 | §5b | ✅ |
| **13. CAN** | SN65HVD230, 100nF+10µF decoup, 🟡 adapt SOIC, 🟡 120Ω, 🟡 PESD1CAN | §8b | ✅ |
| **14. Conectores** | ATX-24, PCIe-6, chicotes sensores, EV1×4 | §9, §2 | ✅ |
| **15. PCB 1-layer** | Fenolite, **~43 fios jumper AWG28** | §9 #77–78 | ⚠️ adicionado |
| **16. Mecânico λ** | Bung M18, anti-seize, chicote λ | §5b | ✅ |
| **17. Combustível** | 4 bicos, bomba, regulador, filtros, mangueiras | §3 | ⬜ bomba/filtros |

### Itens que NÃO entram na placa (chicote / carro)

| Item | Motivo |
|---|---|
| Sensores IAT/MAP/TPS/CLT | No motor/TBI — só conector + fio |
| Sonda LSU 4.2 | No escape — CN2 + chicote |
| Relés (bobina na placa, contatos no chicote) | Soquete + fiação 12V |
| Bicos injetores | Na TBI — EV1 + fio |

### Duplicatas evitadas

- REF3033: citado em §5b e §8 — **mesmo CI, comprar 1×**
- VBat: §5 e §5c — **mesmos passivos, comprar 1× cada**
- Adaptador SOIC8: 1× obrigatório (OPA388IDR), 2º 🟡 se SN65 também for chip solto

### Equivalências aceitas

| Lista | PCB (`pcb-bom-codigos`) | Nota |
|---|---|---|
| SMBJ33A | P6KE33A (D1) | Mesma função TVS 33 V, encapsulamento diferente |
| 2N7000 relés | Q7–Q9 2N7000 | PCB usa THT 2N7000 |
| Black Board | U1 módulo | Cristal/decoupling já no módulo — §8 parcialmente dispensável |

---
