# Tópico 6 — Sonda lambda banda larga DIY (LSU 4.2 / 4.9)

> Projeto INJET RACING — Fase 1 (TBI / speed-density / malha fechada opcional)
> Wideband **montado na ECU**: STM32 + op-amps (sem CJ125).
> Esquemático: `esquema-eletrico.md` §7 · BOM: `lista-componentes.md` §5b · Firmware: `firmware/`

---

## 0. DECISÃO CONFIRMADA

| Item | Peça escolhida | Observação |
|---|---|---|
| **Sonda (padrão)** | **Bosch LSU 4.2** — P/N **0258007351** | wideband; M18×1,5; **5 fios** |
| **Sonda (opcional)** | **Bosch LSU 4.9** — P/N **0258017025** | mesma PCB; muda R_ESR + FW + conector |
| **Controlador** | **DIY:** STM32 + **MCP6002** + **OPA388IDR** | PID aquecedor + malha Ip (topologia rusEFI / `mck1117/wideband`) |
| **Conector 4.2** | **PCIe 6 pinos** (placa) + chicote sonda | housing sonda **1J0973733** |
| **Conector 4.9** | **1928404687** | só se usar 4.9 |

> **Por que sem CJ125?** Chip raro/caro. Topologia open-source (rusEFI / `mck1117/wideband`) usa op-amps comuns + MCU.

### Códigos

| Sonda | P/N | Conector sonda | Conector placa |
|---|---|---|---|
| LSU 4.2 (padrão) | **0258007351**, 0258007057 | 1J0973733 | **PCIe 6 pinos** |
| LSU 4.9 (opcional) | **0258017025** | 1928404687 | PCIe 6 pinos ou 1928404687 |

---

## 0.1 O que muda para usar LSU 4.9 (opcional)

| Item | 4.2 (padrão) | 4.9 (opcional) |
|---|---|---|
| Comprar sonda | 0258007351 | 0258017025 |
| Conector CN2 placa | PCIe 6 pinos | PCIe 6 pinos |
| Resistor R_ESR | **6,8 kΩ** | **22 kΩ** |
| Ri alvo (aquecedor) | ~**80 Ω** | ~**300 Ω** |
| Calibração FW | **free-air** obrigatório | Rcal interno (sem free-air) |
| MCP6002 / OPA388IDR / shunt / MOSFET | iguais | iguais |

---

## 0.2 Pinagem STM32 — lambda (fixada)

| Pino STM32 | Função | Direção |
|---|---|---|
| **PA4** | **DAC1_OUT → Vm** (terra virtual ~2,5 V) | saída analógica |
| **PA5** | **ADC1_IN5 → Ip** (queda no shunt 61,9 Ω) | entrada ADC |
| **PA6** | **ADC1_IN6 → Un** (célula Nernst) | entrada ADC |
| **PD12** | PWM aquecedor (MOSFET H−) | saída PWM |
| **GPIO** (ex. PC0) | Pulso Ri (mede resistência Nernst via R_ESR) | saída digital |

> **λ não tem pino ADC dedicado** — é calculado no firmware a partir de Ip (e Un). PA4 é **somente DAC**, não divisor 0–5 V.

---

## 1. Conceito: o que mede e para que serve

A sonda **banda larga** mede a relação ar/combustível (**λ** ou **AFR**) de forma contínua:

```
AFR_gasolina ≈ 14,7 × λ
```

| λ | AFR (gasolina) | Situação |
|---|---|---|
| 0,85 | ~12,5 | rico (WOT, segurança) |
| 1,00 | 14,7 | estequiométrico |
| 1,05 | ~15,4 | lean (marcha lenta econômica) |

Na estratégia **speed-density**, a injeção base vem do mapa **VE(MAP, RPM)**. A lambda entra como **correção fina** (malha fechada):

```
massa_combustível_final = massa_combustível_VE × (1 + trim_o2)
```

---

## 2. Arquitetura na ECU (op-amps + STM32)

```
                    ┌──────────────── ECU ────────────────────────┐
                    │                                             │
  LSU 4.2 ──CN2──►  │  MCP6002 + OPA388IDR                           │
  (5 fios)          │    ├─ DAC PA4 → Vm (terra virtual)          │
                    │    ├─ ADC PA5 ← Ip (shunt 61,9 Ω)           │
                    │    ├─ ADC PA6 ← Un (Nernst)                 │
                    │    └─ PWM PD12 → aquecedor (IRLZ44N)        │
                    │                                             │
                    │  STM32 FW: PID Ri + malha Ip + Ip→λ         │
                    │            → trim combustível               │
                    └─────────────────────────────────────────────┘
```

| Bloco | Onde fica | Função |
|---|---|---|
| **LSU 4.2** | escape (pré-cat ou coletor) | sensor eletroquímico |
| **MCP6002** | placa ECU | buffer Vm, filtros Un |
| **OPA388IDR** | placa ECU (SMD) | amplificador corrente de bomba (Ip) |
| **MOSFET aquecedor** | placa ECU | mantém sonda ~780 °C (Ri alvo) |
| **STM32** | firmware | PID, ADC, DAC, λ → malha fechada |

Implementação de referência: [mck1117/wideband](https://github.com/mck1117/wideband) (MIT) · Código do projeto: `firmware/src/wideband.*`

---

## 3. Hardware — pinagem CN2 (LSU 4.2)

Conector placa: **PCIe 6 pinos**. Housing da sonda: **1J0973733** (JPT).
Cabo **grosso** no aquecedor (≥ 1,0 mm², até ~2 A).

**Pinagem sinais (LSU 4.2) — pelas cores de fio:**

| Cor do fio (típica) | Sinal | Ligação na ECU |
|---|---|---|
| Vermelho / Branco | **IP** (pump+) | shunt 61,9 Ω + OPA388IDR |
| Amarelo / Preto | **VM** (pump−) | DAC PA4 → buffer MCP6002 |
| Amarelo (2×) | **H+** / **H−** | H+ → +12 V; H− → dreno MOSFET PWM |
| Cinza / Azul | **UN** (Nernst) | ADC PA6 + pulso Ri via R_ESR 6,8 kΩ |
| — | **Rcal** | interno ao conector da sonda (sem fio) |

### 3.1 Passivos do circuito op-amp

| Ref | Valor | Função |
|---|---|---|
| **U2** MCP6002 | dual DIP-8 | buffer Vm, filtros |
| **U3** OPA388IDR | zero-drift | malha corrente Ip |
| **R70** | 61,9 Ω 1% | shunt Ip |
| **R71** | 6,8 kΩ 1% (4.2) / 22 kΩ (4.9) | R_ESR pulso Ri |
| **R76, R77** | 10 kΩ | bias buffer Vm |
| **R78** | 1 kΩ | proteção entrada OPA388IDR |
| **C30** | 220 nF | filtro Ip |
| **C31** | 220 nF | filtro Un |
| **C32** | 100 nF + 10 µF | decoupling +5 V op-amps |
| **REF3033** | 3,3 V | referência ADC (recomendado p/ Ip/Un) |

> Pinagem **MCP6002 DIP-8:** 1–3 = VM (buffer) · 4 = GND · 5–7 = UN (buffer) · 8 = +5 V.

> Ver diagrama completo em `esquema-eletrico.md` §7.

---

## 4. Firmware — wideband (op-amp + ADC)

### 4.1 Constantes e pinos

Ver `firmware/include/pins.h` e `firmware/src/wideband.cpp`.

```cpp
// Pinos fixados (STM32F407)
#define PIN_DAC_VM    PA4   // DAC1 — terra virtual
#define PIN_ADC_IP    PA5   // corrente de bomba (shunt)
#define PIN_ADC_UN    PA6   // célula Nernst
#define PIN_HEATER    PD12  // PWM aquecedor

const float SHUNT_OHMS   = 61.9f;
const float RI_TARGET    = 80.0f;    // Ω — LSU 4.2 @ ~780 °C
const float UN_TARGET_V  = 0.450f;   // V — referência Nernst
const float STOICH       = 14.7f;
```

### 4.2 Malhas de controle

| Malha | Entrada | Saída | Alvo |
|---|---|---|---|
| **Aquecedor** | Ri (pulso via R_ESR) | PWM PD12 | ~80 Ω (4.2) @ ~780 °C |
| **Corrente bomba** | Un ≈ 450 mV | DAC → Ip via OPA388IDR | Un estabilizado → Ip ∝ λ |
| **Leitura λ** | Ip (ADC PA5) | tabela Ip→λ | malha fechada combustível |

### 4.3 Conversão Ip → λ

Tabela não-linear (inspirada em `mck1117/wideband` / datasheet Bosch LSU 4.x):

```cpp
struct PontoLambda { float ip_mA; float lambda; };

const PontoLambda TABELA_IP_LAMBDA[] = {
  {-2.0f, 0.650f},
  {-1.0f, 0.750f},
  { 0.0f, 1.000f},
  { 1.0f, 1.100f},
  { 2.0f, 1.430f},
  // ... pontos intermediários no firmware
};
```

### 4.4 Calibração (LSU 4.2 — free-air)

1. Sonda **fora do escape**, ar ambiente limpo.
2. Aquecedor ativo até Ri estabilizar (~80 Ω).
3. Rodar rotina `widebandCalibrateFreeAir()` — grava offset Ip/Un na flash.
4. Validar no motor com wideband de referência (opcional).

### 4.5 Sonda pronta

```cpp
bool widebandIsReady() {
  return heaterStable && riNearTarget() && warmupSeconds > 30;
}
```

---

## 5. Firmware — malha fechada (controle de combustível)

### 5.1 Estratégia

```
pulse_width_final = pulse_width_VE × (1 + trim_o2)
```

`trim_o2` limitado a **±15%** — ver `firmware/src/closed_loop.cpp`.

### 5.2 Quando a malha fecha e quando não

| Condição | Malha fechada? | Motivo |
|---|---|---|
| Motor frio (CLT < 60 °C) | Não | mapa CLT já enriquece |
| Sonda aquecendo | Não | leitura inválida |
| Marcha lenta / cruzeiro | **Sim** | afinar VE, economia |
| WOT / TPS > 80% | Não | mapa VE manda |
| Aceleração (TPS subindo) | Não | bomba de aceleração |
| Desaceleração (corte) | Não | injeção zerada |

### 5.3 Uso na Fase 1 (afinar VE)

1. Rodar fixo em RPM/MAP conhecidos.
2. Logar `MAP, RPM, λ, pulse_width` (serial ou CAN).
3. Se λ > alvo → aumentar VE; se λ < alvo → diminuir.
4. Com VE ~90% certo, ligar malha fechada.

---

## 6. Instalação mecânica

| Item | Especificação |
|---|---|
| Rosca | **M18 × 1,5** (solda em bung ou flange com rosca) |
| Posição | coletor de escape, **15–30 cm** após junção dos cilindros |
| Orientação | cabeça inclinada 10–90° **acima** da horizontal |
| Material | **aço inox** no bung |
| Combustível | **sem chumbo, sem 2T no óleo** |

> Motor Opala 6 cil aspirado: um ponto no coletor central (pós-junção) serve para todos os cilindros em batch-fire.

### 6.1 O que é o bung

**Bung** = bucha rosqueada de aço inox soldada no cano de escape.

> Buscar como: **"bung sonda lambda M18x1,5 inox"** — R$ 15–40 no ML.

### 6.2 Onde furar/soldar (Opala 6 cil)

- **Depois** da última junção dos cilindros.
- **Antes** do catalisador.
- Cabeça inclinada **para cima** (evita condensado na cerâmica).

### 6.3 Passo a passo

1. Escolher ponto no coletor (regras acima).
2. Furar ~19–20 mm (escape frio).
3. Soldar bung (MIG/TIG).
4. Anti-seize de cobre na rosca; torque **40–60 N·m**.

### 6.4 Cuidados críticos

| ⚠️ Nunca | ✅ Sempre |
|---|---|
| Soldar com combustível na linha | Escape frio |
| Sonda apontando p/ baixo | Inclinada p/ cima |
| Depois do catalisador | Antes do cat |
| Torque > 60 N·m | 40–60 N·m com anti-seize |

---

## 7. Checklist

- [x] Definir sonda → **Bosch LSU 4.2 (0258007351)**
- [x] Controlador onboard → **MCP6002 + OPA388IDR** (sem CJ125)
- [x] Pinagem fixada → **PA4=DAC Vm, PA5=Ip, PA6=Un, PD12=heater**
- [ ] Implementar PID aquecedor + leitura Ri (`firmware/src/wideband.cpp`)
- [ ] Implementar malha Ip + tabela Ip→λ
- [ ] Calibração free-air (LSU 4.2)
- [ ] Tabela lambda alvo (RPM × carga)
- [ ] Testar malha fechada em bancada (motor aquecido, lenta)
- [ ] Bung M18×1,5 no coletor / flange escape
- [ ] Chicote CN2 dedicado (fios aquecedor ≥ 1,0 mm²)

---

## 8. Referências cruzadas

| Arquivo | Conteúdo |
|---|---|
| `esquema-eletrico.md` §3.4, §7 | VBat sense + bloco op-amp + CN2 |
| `lista-componentes.md` §5b | BOM wideband DIY |
| `firmware/` | Código wideband + malha fechada |
| `05-sensores.md` | IAT, MAP, TPS, CLT, VBat |
| `dicas.md` §6 | resumo sensores |
