# INJET 3 Step — projeto piloto (detalhado)

**Status:** ideia / piloto · **fora** da prodv6 Fase 1  
**Referência:** ODG 3 Step GIII / G3 Rev8 (manual RV2 07/2020)  
**Relacionado:** `implementacoes-futuras/FUT-01-3step-corte-bobina.md`

---

## 1. Objetivo do produto

Limitador de giros tipo **3-step** para pista:

- **Burn-out** — botão curto → limiar baixo de RPM  
- **Pre-stage** — botão segurado → limiar médio  
- **Corte final** — automático por RPM alto  
- **Shift light** — 4 LEDs progressivos + saída externa  

**Decisão fixa:** corta **faísca** (alimentação da bobina), **não** combustível nos bicos. Cut de INJ sob carga = risco de motor.

Não é controle de ponto: ignição continua mecânica/ECU original; o aparelho só **liga/desliga +12 V** da bobina por RPM.

---

## 2. Tecnologia ODG (igual — o que replicar)

### 2.1 Núcleo (sempre igual)

| Bloco | Função |
|-------|--------|
| **Entrada RPM** | Fio **VERDE** — pulso Hall / negativo da bobina / saída condicionada |
| **Corte** | Relé interno **COM/NC**, até **10 A** — interrompe **+12 V** da bobina |
| **MCU** | Conta pulsos → compara 3 limiares programáveis |
| **UI** | Display 2 dígitos, botão SET + botão corte, 4 LEDs shift, dimmer opcional |
| **Config** | Nº de cilindros, limiares ×100 RPM, shift % (−10/−7/−3%) |

### 2.2 Ligação elétrica (padrão manual ODG)

**Chicote 10 vias (aparelho):**

| Cabo | Função |
|------|--------|
| Vermelho | +12 V pós-chave (≥ 11,5 V) |
| Preto | GND bateria |
| Branco | Dimmer (farol meia) |
| Verde | RPM in (Hall / − bobina / condensador) |
| Roxo / Verde-Branco | Pickup magnético (alternativa) |
| Amarelo | Shift light externo (−, máx. 1,6 A) |
| Rosa | Auxiliar (ponte AUX↔SL+ em alguns esquemas) |

**Chicote 2 vias (corte potência):**

| Terminal | Cabo | Ligação |
|----------|------|---------|
| COM | Vermelho/Preto | +12 V **antes** do corte (chave/fusível) |
| NC | Preto/Amarelo | +12 V **para bobina** (+) |

Regra do manual: **só** PRETO/AMARELO no **+ da bobina**; fios que estavam no + vão para VERMELHO/PRETO.

### 2.3 Firmware (comportamento)

- **Burn-out:** botão solto rápido → LED ON → limita no RPM programado → botão de novo desliga  
- **Pre-stage:** botão pressionado → LED ON → limita no RPM programado → soltar botão desliga  
- **Corte final:** sempre ativo no limiar alto  
- **Shift:** LED1 −10%, LED2 −7%, LED3 −3%, LED4 + saída amarela no valor programado  
- **Não** zerar PWM dos bicos para limiter  

**Fail-safe (decidir antes de rotear):** relé energizado = faísca ON (NC) vs relé OFF = faísca ON — depende se preferir fail com ou sem faísca se MCU morrer.

---

## 3. Três modos de instalação (aplicação)

### Modo A — Clássico (1 bobina + distribuidor)

- **Adaptador:** nenhum  
- **RPM:** VERDE no **− da bobina**  
- **Corte:** COM/NC no **+ da bobina**  
- **Alvo INJET:** Opala, AP, motores com platina/módulo externo + 1 bobina  

### Modo B — Centelha perdida 4 cil. (2 bobinas / bobina dupla, sem módulo na bobina)

- **Adaptador:** **chicote DI 2 canais** (incluso no kit ODG; replicar no nosso chicote)  
- **RPM:** adaptador junta pulso das 2 vias → VERDE  
- **Corte:** PRETO/AMARELO no **+ comum** das bobinas  
- Ex.: GM Vectra 2010, VW Gol 2011  

### Modo C — Multi-bobina / COP (3–6 bobinas ou módulo integrado na bobina)

- **Adaptador RPM:** **Condensador de Sinais** ODG (DI-RPM ou TR-RPM, 6 canais) — **vendido à parte**  
- **Função do condensador:** **só leitura RPM** — até 6 entradas → 1 saída pro VERDE (≤ 100 mA)  
- **Corte:** mesmo relé COM/NC no **+12 V de ignição/bobinas** (alimentação), não no trigger da ECU  

| Tipo bobina | Condensador |
|-------------|-------------|
| Sem módulo de potência integrado (Omega, Marea…) | **DI-RPM** (0970001) |
| Com módulo integrado (Gol 1.0T, Civic 2010…) | **TR-RPM** (0970000) |

**Atalho:** VERDE na **saída RPM da ECU** (quando existir) — sem condensador.  
**Aviso ODG:** ligação DI/TR errada **pode danificar bobina**.  
**ECU sensível:** Uno 2010, Celta 2011 — cut no + pode acender MIL ou falhar; validar por modelo.

---

## 4. Hardware proposto (piloto standalone)

Produto **caixa separada** (não delta na prodv6 atual), estilo painel ODG.

### 4.1 BOM principal (1 unidade)

| Ref | Peça | Qtd | Função |
|-----|------|-----|--------|
| U1 | STM32F103C8T6 (Blue Pill) ou similar | 1 | MCU, timers, GPIO |
| DISP | Display 7 seg. 0,56" **2 dígitos** CC | 1 | RPM / programação |
| LED1–4 | LED 5 mm | 4 | Shift progressivo |
| SW1 | Botão tátil SET | 1 | Programação |
| SW2 | Botão corte (externo ou na caixa) | 1 | Burn / Pre |
| Q_ign | 2N7000 ou IRLZ44N | 1 | Driver low-side bobina do relé |
| R_g | 1k (2N7000) / 100Ω (IRLZ) | 1 | Gate série |
| R_pd | 10k | 1 | Gate → GND |
| D_fly | 1N4007 | 1 | Flyback relé |
| RL_IGN | SRD-12V (placa) + relé **20–30 A** chicote | 1+1 | COM/NC corta +12 V bobina |
| U_rpm | PC817 + R 10k×2 + D 1N4148 + C 1nF | 1 | Entrada RPM (modo A) |
| U_drv | ULN2003 ou CI driver LED/display | 1 | Multiplex display / shift out |
| REG | 7805 ou AMS1117-5.0 | 1 | Alimentação 5 V |
| — | Passivos, conectores, fusível | — | Decoupling, headers |

**Opcional launch (se unificar com 3-step na ECU futura):** SW embreagem + R 1k–4k7 + C 100nF.

### 4.2 PCB

- **Material:** FR4 **dupla face cobreada** 10×15 cm (CNC isolamento)  
- **Tamanho útil do circuito:** ~7×10 cm (caixa painel compacta)  
- **Relé potência:** contatos no **chicote** (30 A), driver + SRD na placa  

### 4.3 Case

- Impressão 3D PLA/PETG  
- Janela display, furos botão/LED, passa-fio chicote  
- Fixação painel (porcas M3 ou clip)  

### 4.4 Chicote

- **Principal 10 vias** + **potência 2 vias** (COM/NC) — espelhar ODG  
- Fio automotivo, terminais, tubo corrugado  
- Modo B: ramificação **DI 2 canais** no chicote  
- Modo C: conector para **condensador DI/TR** (ou produto ODG avulso ~R$ 105)  

---

## 5. Comparação mercado

| Item | ODG 3 Step G3 Rev8 | Piloto INJET (meta) |
|------|-------------------|---------------------|
| Preço loja | ~R$ 595–613 | DIY ~R$ 110–200 completo |
| Corte | Relé 10 A +12 bobina | Igual (relé COM/NC) |
| RPM clássico | VERDE − bobina | Igual (opto PC817) |
| RPM COP | Condensador DI/TR | Mesmo adaptador ou saída ECU |
| Condensador | ~R$ 105 à parte | Comprar ODG ou desenvolver Fase 2 |

---

## 6. Escopo Fase piloto vs INJET ECU

| | Piloto caixa INJET 3 Step | Integração futura ECU |
|--|---------------------------|------------------------|
| Produto | Standalone painel | Delta FUT-01 na prodv6 |
| MCU | Blue Pill dedicado | STM32F407 já na placa |
| Display/botões | Na caixa 3-step | Display externo ou serial |
| Cut bobina | Relé dedicado 10–30 A | +1 canal relé (FUT-01) |
| RPM | Entrada própria ou condensador | PE8 / R17O já existe |

---

## 7. Riscos e validação

1. **RPM durante cut:** se cortar +12 V sumir pulso no −, usar hold do último RPM ou edge só com faísca.  
2. **COP / ECU moderna:** sem condensador ou saída ECU → contagem errada.  
3. **Cabos de vela resistivos** e distribuidor OK — manual ODG exige (ruído EMI).  
4. **Homologação / rua:** produto de pista; fail-safe e chicote críticos.  

---

## 8. Próximos passos (quando puxar o piloto)

1. Esquemático KiCad (MCU + display + relé + RPM)  
2. Layout 7×10 cm + case 3D  
3. Firmware: contagem RPM, 3 limiares, shift, programação SET  
4. Protoboard Modo A (Opala/AP) → depois Modo B se necessário  
5. Chicote com terminologia ODG (cores/nomes)  

---

## 9. Referências

- Manual ODG 3 Step GIII RV2: `https://odginstruments1.websiteseguro.com/pdf/man_3STEP_GIII.pdf`  
- Condensador DI/TR 6ch: `https://www.odginstruments.com.br/acessorios/condensador-de-sinais-ditr-6-canais`  
- FUT-01 repo: `implementacoes-futuras/FUT-01-3step-corte-bobina.md`  
- Canvas planilha BOM: `canvases/corte-3step-pcb.canvas.tsx` (Cursor)
