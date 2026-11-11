# Projeto INJET RACING — Injeção Programável para Carros Antigos Carburados

> Documento vivo do projeto. Este `dicas.md` é o **ÍNDICE GERAL**.
> Cada tópico numerado ganha seu próprio arquivo detalhado (`NN-nome-do-topico.md`)
> com toda a construção daquele assunto.
> Última atualização: Fase 1 — hardware/MCU por fase definido (Uno → Mega → STM32F407) + adaptação 5 V↔3,3 V.

### Arquivos de tópico (detalhados)
| Tópico | Arquivo | Status |
|---|---|---|
| 0. Hardware (MCU por fase + adaptação 5 V↔3,3 V) | `00-hardware.md` | ✅ criado |
| 3. Flange adaptadora (CNC) | `03-flange.md` | ✅ criado |
| 3B. Flange alternativa (torno + furadeira) | `03b-flange-torno.md` | ✅ criado |
| 3C. Flange simples chapa quadrada — TBI 55 mm | `03c-flange-55mm-tbi.md` | ✅ criado |
| 3D. Corpo completo TBI 2 peças (Inject Solution) | `03d-corpo-completo-tbi.md` | ✅ criado (ATUAL) |
| 4. Bicos injetores — dimensionamento | `04-bicos-injetores.md` | ✅ criado |
| 5. Sensores (IAT, MAP, TPS, CLT) | `05-sensores.md` | ✅ criado (ATUAL) |
| — Lista de componentes / BOM geral | `lista-componentes.md` | ✅ criado |
| — Esquema elétrico + conectores + render da PCB | `esquema-eletrico.md` | ✅ criado |
| — Firmware Fase 1 (wideband + speed-density) | `../firmware/` | ✅ esboço |
| (demais tópicos) | a criar conforme avançarmos | ⬜ |

---

## 1. Objetivo do projeto

Criar uma **injeção eletrônica programável** (ECU própria, sem Speeduino) para carros antigos
originalmente carburados, o mais **simples, didático e comercializável** possível.

- **Tipo:** Monoponto (TBI) — *batch-fire* / *speed-density*
- **Aplicações:** motores **4 e 6 cilindros** (configurável por software)
- **Estratégia:** começar pela **Fase 1 (só combustível)**, mantendo a ignição original

### Carro de referência (protótipo)
- Ford Galaxie LTD 1976
- Motor Opala 6 cil ("gaxeta") com pistões do 4 cil → ~**4400 cc**
- Câmbio 4 marchas do Opala 6 cil
- Coletor com base para carburador **Brosol 3E**
- TBI escolhida: **55 mm** (a da foto, furação 80 × 70 mm) — melhor casada que a de 60 mm p/ este motor

---

## 2. Escopo da FASE 1 (foco atual)

| Item | Definição |
|---|---|
| Injeção | 2 a 4 bicos na flange, *batch* (todos juntos), spray abaixo da borboleta |
| Mistura | Speed-Density (MAP + IAT + RPM + tabela VE) |
| Sinal de RPM | **Negativo da bobina** (mais simples) **ou** Hall no distribuidor |
| Ignição | **Distribuidor ORIGINAL 100% mecânico** (avanço mecânico + vácuo) — NÃO mexer nesta fase |
| Roda fônica | **Não usar agora** — só na Fase 2 (controle de ponto) |
| Bomba | Elétrica de alta pressão + regulador com retorno + corte de segurança por RPM |

---

## 3. CORPO MECÂNICO — TBI integrada (direção vigente)

> 📄 Detalhado em **`03d-corpo-completo-tbi.md`**.
> **DESIGN VIGENTE = corpo completo em 2 peças** (estilo [Inject Solution](https://injectsolution.com.br/)):
> tira o carburador 3E e parafusa **BASE + CORPO** usinados — borboleta Ø55, 4 bicos, TPS, IAT, MAP,
> flautas externas. Sem TBI comprada separada.
> Histórico flange/adaptador: `03-flange.md` (v3), `03c-flange-55mm-tbi.md`, `03b-flange-torno.md`.

O conjunto substitui **carburador + flange**. A **BASE** fixa no coletor (bicos + MAP + combustível);
o **CORPO** traz entrada de ar, borboleta e sensores. Funciona como TBI plug-and-play própria.

**COMPATIBILIDADE DUPLA (definido):** a face inferior terá **os dois padrões de furação** para servir
em dois tipos de coletor/carburador — vira uma flange "universal" (bom para comercializar):
- **Brosol/Solex 2E–3E:** fixação de **3 furos** (padrão triangular).
- **Weber DFV/DGV 446:** fixação de **4 furos**, retangular **46 mm × 93 mm** (padrão DGV).

Como os dois padrões ocupam posições diferentes, dá para furar **ambos na mesma flange** sem conflito.
A boca central é feita como **rasgo/oval** grande o suficiente para liberar as bocas dos dois carburadores
e a saída da TBI 60 mm.

**Dimensão base de referência (mercado, bases adaptadoras 2E/3E):**
- Comprimento **120 mm** × Largura **75 mm** × Altura **20 mm** (usaremos **~25–30 mm** de espessura
  para acomodar bicos + galeria).

> IMPORTANTE: as cotas com `?` ainda devem ser **conferidas no coletor real** e na base da TBI.
> O padrão do 3E (3 furos) sai de fábrica **sem furação** justamente porque varia — medir no seu coletor.

### 3.1 Cotas (pesquisadas + a confirmar)

| Cota | Descrição | Valor |
|---|---|---|
| L | Comprimento da flange | **120 mm** (referência de mercado) |
| W | Largura da flange | **75 mm** (referência de mercado) |
| E | Espessura total da flange | **25–30 mm** (p/ bicos + galeria) |
| DFV | Furação Weber DFV/DGV 446 (4 furos) | **46 × 93 mm** (retangular) |
| 3E | Furação Brosol 2E/3E (3 furos) | `medir` (sem padrão fixo) |
| Ø1 | Diâmetro das bocas do 3E (primária/secundária) | `medir` |
| Ø2 | Diâmetro interno da saída da TBI | `~60 mm` |
| C | Furos de fixação da TBI (padrão Bosch) | `medir` |
| H | Altura livre até o capô (interferência) | `medir` |

### 3.2 Vista superior (TOPO) — onde entram bicos, MAP e furos

```
                    FACE SUPERIOR (lado da TBI)
        <---------------------- largura ---------------------->
        +------------------------------------------------------+
        |  o (furo TBI)                          (furo TBI) o   |
        |                                                      |
        |        __________________________________           |
        |       /                                  \           |
        |      |        BOCA / VENTURI central      |          |
        |  B1  |    (passagem de ar da TBI p/       |   B3     |
        |  -->>|         o coletor)                 |<<--       |
        |      |                                    |          |
        |  B2  |                                    |   B4     |
        |  -->>|                                    |<<--      |
        |       \__________________________________/           |
        |                                                      |
        |   [MAP] furo de vacuo (abaixo da borboleta)          |
        |  o (furo TBI)                          (furo TBI) o   |
        +------------------------------------------------------+

   B1..B4 = 4 bicos injetores, 2 de cada lado, apontando p/ o centro/baixo
   [MAP]  = tomada de vacuo p/ sensor MAP (rosca 1/8 NPT)
   o      = furos de fixacao (alinhar com TBI em cima e 3E embaixo)
```

### 3.3 Vista em corte (LATERAL) — ângulo dos bicos e galeria

```
            TBI (borboleta)  ==>  ar entra por cima
        ============  borboleta  ============
        |                                    |   FACE SUPERIOR
   ~~~~~|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|~~~~~
        |   \  bico              bico  /      |
        |    \  30 grados      30 grados /    |   <-- bicos inclinados
   [GAL]|=====*======= centro ========*=====|[GAL]  GAL = galeria de combustivel
        |      spray  \         /  spray      |         (furo passante nas laterais)
        |              \       /              |
        |               v     v              |   E = espessura (20-30 mm)
   ~~~~~|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|~~~~~
        |         COLETOR (base 3E) -> plenum |   FACE INFERIOR
        ============  para os cilindros  ======

   - Bicos a ~30 graus da vertical, spray convergindo p/ o centro do venturi
   - Bicos posicionados ABAIXO da borboleta da TBI
   - Galeria de combustivel [GAL] cruza a flange e alimenta os 4 bicos
```

### 3.4 Galeria de combustível

```
        ENTRADA de combustivel (rosca 1/8 NPT ou banjo)
                     |
                     v
   [ >> galeria usinada dentro da flange (furo passante tampado nas pontas) >> ]
        |        |        |        |
        v        v        v        v
       B1       B2       B3       B4     (assentos dos bicos com o-ring)
                     |
                     v
        SAIDA -> regulador de pressao -> retorno ao tanque
```

- **Furo passante** longitudinal usinado na flange = a galeria (rail interno).
- Tampar as **duas pontas** (bujões) e usar uma como **entrada** e prever **saída p/ regulador**.
- Cada bico assenta em um **rebaixo com o-ring** (vedação de combustível) e outro o-ring no bico
  do lado do ar.
- Alternativa mais simples de fabricar: **trilho (rail) externo** de alumínio aparafusado por cima,
  com os bicos atravessando a flange.

### 3.5 Materiais e fabricação
- **Material:** alumínio (6061/7075) — usinado em CNC (preferível) ou fresado.
- **Isolamento térmico:** junta de fenolite/fibra entre flange e coletor (reduz *heat soak* nos bicos).
- **Vedação:** juntas nas duas faces (TBI e 3E) + o-rings nos bicos.
- **Roscas:** MAP e entrada de combustível em 1/8" NPT (comum e fácil de achar conexões).

### 3.6 Posição dos sensores (resumo)
| Sensor | Onde | Observação |
|---|---|---|
| MAP | **na flange**, furo abaixo da borboleta | Tomada de vácuo do plenum |
| IAT | **na entrada de ar da TBI** (ar fresco) | **Bosch 0280130085** (encaixe push-in c/ borracha). NÃO na flange (evita ar quente) |
| TPS | **no eixo da borboleta da TBI** | — |
| CLT | **na água / cabeçote** | — |
| RPM | negativo da bobina OU Hall no distribuidor | Ver seção 5 |

---

## 4. Bicos injetores — dimensionamento
> 📄 Detalhado em **`04-bicos-injetores.md`** (fórmulas, exemplos, seleção, dead-time).

**DEFINIDO (protótipo 6 cil):**
- Potência-alvo: **130–150 cv**.
- **4× Bosch 0280156086 — 28 lb/h (296 cc/min / 213 g/min) @ 3 bar** ✅ vazão confirmada, alta impedância → driver MOSFET.
- No pico usa ~73% (130 cv) a ~84% (150 cv) de duty. Pressão de linha **3 bar** com regulador com retorno.
- ❌ Injetor LS 80 lb/h (850 cc/min) avaliado e **descartado** (superdimensionado p/ este motor).

---

## 5. Sinal de RPM e IGNIÇÃO (Fase 1)

**DECISÃO DO PROJETO:** o sinal de RPM será obtido do **NEGATIVO DA BOBINA** (sinal de tacômetro).
Sem sensor novo, sem roda fônica. A **ignição continua original** (distribuidor mecânico + vácuo +
bobina) — a ECU controla SÓ combustível nesta fase.

### 5.1 Por que o negativo da bobina
- Já existe no carro (terminal negativo / "-" da bobina, mesmo ponto do tacômetro).
- A cada faísca gera 1 pulso → dá RPM direto.
- Nº de faíscas por volta do virabrequim (4 tempos): **cilindros ÷ 2**
  - 6 cil = **3 pulsos/volta**; 4 cil = **2 pulsos/volta**.
- Fórmula do firmware: `RPM = (pulsos_por_segundo × 60) ÷ (nº_cil ÷ 2)`

### 5.2 O problema do sinal (por que precisa condicionar)
No negativo da bobina, quando a faísca dispara, o *flyback* do primário gera picos de
**+200 a +400 V** com "campainha" (ringing). Ligar isso direto no Arduino **queima**. O condicionador
precisa: (a) **limitar a tensão**, (b) **filtrar o ringing**, (c) **entregar 1 pulso limpo de 5 V**.

### 5.3 Circuito RECOMENDADO — isolado por optoacoplador (para produto)
Isolação galvânica = protege o MCU e reduz ruído. **Esta é a versão para comercializar.**

```
 COIL(-) o---[R1 10k 2W]---[R2 10k 2W]---+----------(A) LED >|--- (K) ---o GND
   (tacô)                                |            optoacoplador
                                    [D1 1N4148]        PC817 / 4N25
                                    (catodo p/ cima,     |  |
                                     protege LED do      |  | (fototransistor)
                                     reverso)            |  |
                                                    +5V --[R3 4k7]--+--> SINAL_RPM (p/ MCU)
                                                                    |
                                                              (C) coletor
                                                              (E) emissor --o GND
                                                                    |
                                                                  [C1 1nF] --o GND  (filtro)
```

- **R1+R2 em série (20k total, 2 W):** dois resistores dividem a **tensão** do pico (cada um segura
  metade) e limitam a corrente no LED: ~300 V ÷ 20k ≈ 15 mA (dentro do LED do opto).
- **D1 (1N4148):** protege o LED do opto contra tensão reversa/ringing negativo.
- **Opto PC817 (ou 4N25):** saída em **coletor aberto**, pull-up R3 4k7 p/ 5 V.
- **Saída invertida:** em repouso = 5 V; a cada faísca = pulso p/ 0 V. Tratar no firmware como
  **borda de descida** (falling edge) na interrupção.
- **C1 1nF:** filtra o ringing (junto com pull-up forma RC ~5 µs).

### 5.4 Circuito ALTERNATIVO — transistor (didático, sem isolação)
Mais barato, bom para bancada/protótipo:

```
 COIL(-) o---[R1 33k 1W]---+---[D_zener 5V6]---o GND     (clampa o pico)
                           |
                           +---[R2 4k7]--- base Q1 (BC547 NPN)
                           |
                         [C1 1nF]
                           |
                          GND
   Q1: emissor -> GND ; coletor -> [R3 1k] -> +5V ; SINAL_RPM sai do coletor (invertido)
```

- **R1 33k 1W** limita corrente; **zener 5V6** clampa o node em ~5,6 V.
- **Q1 BC547** quadra o sinal; saída no coletor (invertida, borda de descida).

### 5.5 BOM do condicionador (versão isolada)
| Ref | Componente | Valor |
|---|---|---|
| R1, R2 | Resistor 2 W | 10 kΩ (x2) |
| R3 | Resistor 1/4 W | 4,7 kΩ |
| D1 | Diodo | 1N4148 |
| U1 | Optoacoplador | PC817 (ou 4N25) |
| C1 | Capacitor cerâmico | 1 nF |

### 5.6 Notas de firmware (leitura de RPM)
- Entrada em **pino de interrupção**, disparo na **borda de descida**.
- **Debounce por tempo:** ignorar pulsos com intervalo menor que o coerente com o RPM máximo
  (ex.: > limite de rev) → evita contar ringing como pulso duplo.
- Medir **período entre pulsos** (mais preciso que contar em janela) e converter com a fórmula 5.1.
- Filtro de média móvel de 2–4 amostras para estabilizar o valor exibido.

### Quando fazer ignição eletrônica (FASE 2 — futuro)
- Só quando a ECU for controlar o **ponto** (avanço por mapa / faísca perdida).
- Aí exige **roda fônica 36-1 no virabrequim** (precisão que o distribuidor não dá) e
  **travar o avanço** do distribuidor.

---

## 6. Sensores mínimos (Fase 1)
| Sensor | Função | Peça sugerida |
|---|---|---|
| MAP | carga do motor | **Bosch 0279980411** (VW, 1 bar aspirado, c/ bico de mangueira) ✅ ESCOLHIDO |
| CLT | temp. motor (partida a frio) | **60513205** (GM/Fiat Astra/Celta/Corsa/Marea/Tipo/Uno) — NTC 2 vias ~2,5k @ 20 °C ✅ ESCOLHIDO |
| IAT | temp. ar admitido | **Bosch 0280130085** (NTC ar, ~2,5k @ 20 °C) ✅ ESCOLHIDO |
| TPS | posição borboleta (aceleração) | **Gol Mi 96-98** (pot. rotativo 3 fios) — a TBI já é feita pra ele, parafusa direto ✅ ESCOLHIDO |
| RPM | rotação | negativo da bobina / Hall distribuidor |
| O2 (opc.) | malha fechada | **LSU 4.2 DIY (op-amps MCP6002+OPA388IDR)** — ver `06-sonda-lambda.md` ✅ · 4.9 opcional |
| VBat | dead-time bicos | divisor 100k/10k → **PC1** ADC (ver `esquema-eletrico.md` §3.4) |

---

## 7. Eletrônica da ECU (hardware) — resumo
> 📄 Escolha da placa/MCU por fase e adaptação 5 V↔3,3 V detalhadas em **`00-hardware.md`**.
> Consolidar esquemático depois.

- **MCU:** ATmega2560 (protótipo) ou **STM32F407VET6** (produto — ver `00-hardware.md`)
- **Fonte:** proteção reversa (MOSFET P) + TVS *load dump* + buck 5 V
- **Condicionamento:** MAX9926 (se VR) / pull-ups NTC 2,26k (2K26 1%) / filtros RC
- **Drivers de bico:** MOSFET low-side (IRLZ44N) + clamp de flyback
- **Saídas de relé:** principal (auto-hold) + bomba (corte por RPM) + IAC (opc.)
- **Conector:** AMPSEAL 23 vias + fios blindados no sinal de RPM
- **Case:** alumínio, instalar no habitáculo

### Relés
| Relé | Função | Corrente |
|---|---|---|
| RL1 | Principal (ECU) | 20–30 A |
| RL2 | Bomba combustível | 30–40 A |
| RL3 | IAC/aux (opc.) | 20 A |

### Fusíveis
| Circuito | Fusível |
|---|---|
| ECU | 5–7,5 A |
| Bomba | 15–20 A |
| Bicos | 10 A |
| IAC/aux | 10 A |

---

## 8. Sistema de combustível
- Bomba elétrica de alta pressão (externa Bosch 040/044 ou de tanque)
- Filtro de alta pressão + pré-filtro (tela) na sucção
- Regulador de pressão **com retorno** (3 bar)
- Linhas de ida e retorno (mangueira p/ injeção)
- **Segurança:** *prime* 2–3 s ao ligar; corta bomba se não houver RPM

---

## 9. Diferenças 4 cil x 6 cil
| Parâmetro | 4 cil | 6 cil (Galaxie/Opala) |
|---|---|---|
| Nº de bicos | 2–4 | 4 |
| Tamanho TBI | 46–52 mm | 60 mm |
| Palhetas Hall (se usar) | 4 | 6 |
| Config firmware | "4 cyl" | "6 cyl" |

---

## 10. Pendências / próximos passos
- [ ] Medir furação do 3E no coletor real (SEM padrão — obrigatório medir)
- [x] Fechar nº de bicos (4) e vazão → **4× 30 lb/h (bico verde)** p/ 130–150 cv
- [x] Definir RPM → **negativo da bobina**
- [x] Detalhar circuito condicionador do negativo da bobina (valores finais) → seção 5
- [ ] Definir potência-alvo da versão 4 cil
- [ ] Esquemático completo da ECU (KiCad) + BOM com códigos
- [ ] Firmware Fase 1 (leitura sensores + speed-density + batch + serial) → ver **`firmware/`**
- [ ] Mapa base VE inicial (4400 cc 6 cil e versão 4 cil)
- [ ] Desenho da flange em CAD (a partir das cotas medidas)
