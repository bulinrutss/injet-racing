# INJET RACING

ECU de injeção para TBI (corpo de borboleta), Fase 1. Mede ar por velocidade e pressão (speed-density), calcula o tempo de injeção e aciona até quatro bicos em batch-fire. O cérebro é uma **Black Board STM32F407VET6** encaixada na placa; a fonte de 5 V fica na própria ECU.

A placa em curso é a **prodv6** (240 × 160 mm, duas camadas). O firmware em `firmware/` lê sensores, calcula o pulso e registra na serial. Ainda não dispara os bicos.

## Como funciona

A bateria entra por proteção (fusível, MOSFET contra inversão e TVS) e vira **+12V_PROT**. Esse 12 V alimenta bicos, bobinas de relé e o aquecedor da sonda pelo chicote. Um módulo **MP1584** gera **+5 V** para a Black Board, o MAP e os amplificadores da lambda. O 3,3 V sai do regulador interno da Black Board e é só distribuído na placa (sensores, pull-ups, opto de RPM). Não há um segundo LDO na ECU.

```
+12 V bateria
    │
    ├─ proteção ── +12V_PROT ── bicos (lado +), relés, aquecedor λ
    │
    └─ MP1584 ── +5 V ── Black Board ── +3V3 ── sensores e lógica
```

Cada volta do motor chega pelo **negativo da bobina**, isolado por um opto **PC817**. Com RPM, MAP, temperatura do ar e tensão da bateria, o firmware estima a massa de ar, aplica uma eficiência volumétrica (VE) e soma o tempo morto do bico. A sonda **LSU 4.2** (wideband, frente analógica com MCP6002 e OPA388IDR) devolve lambda; um PI corrige o pulso em até ±15 % com o motor quente e fora de plena carga. Os bicos são low-side: o chicote leva +12 V e a placa fecha o negativo com **IRLZ44N**. Três **2N7000** comandam relés externos (principal, bomba e IAC) pelo conector CN3. O relé em si não é soldado na placa.

Gravação e debug são pela USB da Black Board. Não há conector SWD na ECU.

| Ação | 12 V na ECU | Cabo USB |
|------|-------------|----------|
| Gravar firmware | desligado | normal |
| Monitor serial / tune | ligado | power blocker (só D+, D− e GND) |
| No carro | ligado | desconectado |

Serial de bancada: **115200 baud**.

## Estado agora

| Bloco | Situação |
|-------|----------|
| Proteção de 12 V e buck +5 V (MOD3–4) | roteado na prodv6 |
| Black Board, +3V3 e referência (MOD5) | roteado |
| Sensores IAT, CLT, MAP, TPS, tensão de bateria (MOD6) | roteado até os headers da Black Board |
| RPM pelo negativo da bobina (MOD7) | roteado, CN1-22 → PC817 → PE8 |
| Quatro injetores IRLZ44N (MOD8) | roteado, CN1-13…16 |
| Três drivers de relé + CN3 (MOD9) | roteado; SRD fica no chicote |
| Lambda e aquecedor (MOD11–12) | roteado |
| CAN (MOD10) | desativado nesta revisão |
| DRC, silk e Gerber | em aberto (clearance do OPA388, contorno da placa, unconnected cosmético) |
| Bancada sem motor | roteiro em `kicad/prodv6/BENCH-CHECKLIST.md`, ainda não é validação de rua |
| Firmware | referência de bancada: lê, calcula e loga; o pulso não sai nos MOSFETs |
| prodv7 | cópia da prodv6 com o OPA388 em DIP-8 no lado dos componentes |

O DRC da prodv6 ainda não está zerado. O checklist de layout e os scripts `_check_modN_now.py` estão em `kicad/prodv6/`.

## Placa

Abrir no KiCad 8:

`kicad/prodv6/injet-racing-prodv6.kicad_pro`

Salvar o PCB não mexe no esquemático. Atualizar o PCB a partir do esquemático é o F8. Não rodar o gerador Python por cima do `.kicad_pcb`: ele apaga trilhas e zonas já feitas.

A prodv7 (`kicad/prodv7/`) existe para trocar o OPA388 de SOIC na face de baixo por DIP-8 furado. O desenho de trabalho continua sendo a prodv6 até essa troca fechar.

### Conectores da prodv6

Pinagem que os scripts de checagem conferem na placa roteada. O restante do chicote está em `modulo/esquema-eletrico.md` §9.

**CN1** — header ATX 24 pinos (alimentação, sensores, RPM, bicos):

| Pinos | Função |
|-------|--------|
| 1–2 | +12V_BAT |
| 3 | +5 V (MAP) |
| 4 | +3V3 (TPS e pull-ups) |
| 6 | IAT |
| 7 | CLT |
| 8 | MAP |
| 10 | TPS |
| 11 | +12V_PROT (divisor de bateria) |
| 13–16 | INJ1…INJ4 (low-side) |
| 22 | RPM, negativo da bobina |

**CN2** — PCIe 6 pinos, sonda LSU:

| Pino | Função |
|------|--------|
| 1 | +12V_PROT, aquecedor H+ |
| 2 | H− (dreno do MOSFET) |
| 3 | sem ligação |
| 4 | IP |
| 5 | VM |
| 6 | UN |

**CN3** — PCIe 6 pinos, contato NA dos relés externos:

| Pino | Função |
|------|--------|
| 1 | IAC |
| 2 | bomba |
| 3 | relé principal |
| 4 | GND |

### GPIO da Black Board

Definidos em `firmware/include/pins.h` e no esquemático.

| Sinal | Pino |
|-------|------|
| IAT / CLT / MAP / TPS / VBat | PD0 / PA9 / PC9 / PC8 / PA8 |
| Lambda Vm, Ip, Un, Ri | PA4 / PA5 / PA6 / PE2 |
| Aquecedor | PB0 |
| RPM | PE8 |
| INJ1…4 | PE9, PE11, PE13, PE15 |
| Relé principal / bomba / IAC | PD10 / PD8 / PD9 |

## Firmware

Alvo: STM32F407VET6 pela core STM32duino (placa Generic F407VET6 ou equivalente da Black Board). Os fontes estão em `firmware/src/`; não há `platformio.ini` no repositório.

O `loop` faz isto a cada passagem:

1. Atualiza a wideband (aquecedor pela resistência da célula, corrente de bomba, lambda).
2. Lê MAP, TPS, CLT, IAT e bateria.
3. Atualiza o trim de lambda.
4. A cada 10 ms calcula o tempo de injeção em ms.
5. A cada 100 ms imprime `RPM MAP TPS CLT VBat L PW TRIM`.

O que esse código ainda não faz: agendar o pulso nos quatro MOSFETs (há um TODO no `main.cpp`), tabela VE de verdade (`fuelVeLookup` devolve 0,75 fixo) e protocolo de tune. A interrupção de RPM guarda o período; quem publica o valor filtrado é `rpmUpdate()`, e o `loop` ainda não chama essa função — por isso o campo RPM da serial fica em zero. A bomba é ligada no `setup` e permanece ligada.

Cilindrada, vazão dos bicos e número de cilindros em `fuel.cpp` / `pins.h` são constantes de bancada, não o acerto de um motor específico.

## Mapa do repositório

| Pasta | Conteúdo |
|-------|----------|
| `modulo/` | Esquema elétrico, listas de componentes, sensores, bicos, lambda, pinout e flanges |
| `kicad/prodv6/` | PCB atual, checklist, bancada e scripts de checagem |
| `kicad/prodv7/` | Variante com OPA388 em DIP-8 |
| `kicad/` | Esquemático hierárquico e PCBs anteriores (prod … prodv5) |
| `firmware/` | Firmware de referência da Fase 1 |
| `implementacoes-futuras/` | Ideias fora da Fase 1 (3-step, relé pesado, roda fônica, condicionador VR) |
| `projetos piloto/` | Produtos à parte, hoje o limitador 3-step |
| `assets/` | Renders e estudos de placa de uma camada |

Na raiz também estão o manual e a lista de TBI compatíveis (PDFs).

Itens de `implementacoes-futuras/` e de `projetos piloto/` ficam fora da prodv6 até serem puxados para o escopo.

## Licença

MIT. Copyright (c) 2026 Marcos Gasperin. Ver `LICENSE`.
