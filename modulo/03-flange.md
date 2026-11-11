# Tópico 3 — Flange Adaptadora (Coletor ↔ TBI + Porta-injetores)

> Projeto INJET RACING — Fase 1 (TBI / monoponto)
> Arquivo detalhado do tópico 3 do `dicas.md`.
> 🖼️ Imagens:
> - **[v3 ATUAL] Cotado:** `../assets/flange-tbi-cotas-v3.png`
> - **[v3 ATUAL] 3D 4 ângulos:** `../assets/flange-tbi-3d-v3.png`
> - **[v3 ATUAL] Explodida:** `../assets/flange-tbi-explodida-v3.png`
> - [v2] Cotado/3D/Explodida: `../assets/flange-tbi-*-v2.png`
> - [v1] Conceito/Cotado/3D: `../assets/flange-tbi-projeto.png`, `-cotas.png`, `-3d-4angulos.png`

---

## DESIGN v3 (ATUAL) — Bicos LATERAIS horizontais (fácil de usinar)

> Versão **vigente**. Evolução da v2. Histórico (v2 = bicos a 30°; v1 = galeria interna) preservado abaixo/nos assets.

**Mudança principal (v2 → v3):**
- **Bicos montados na LATERAL, na HORIZONTAL (90°)**, entrando por **furos retos** nas paredes
  laterais da base, com as pontas cuspindo para o centro do furo. **Não precisa de máquina para
  ângulo de 30°** → dá para furar com **furadeira de bancada ou torno**. Muito mais fácil no protótipo.

**Estrutura (mantida da v2):**
- **Sem duto de combustível interno** → **2 flautas externas** (uma por lado), cada uma alimenta
  **2 bicos**. Fácil de tornear e de dar manutenção.
- **Corpo em 2 peças:**
  - **BASE (baixo):** fixa no coletor (furação dupla 3E + DFV 446), aloja os 4 bicos laterais e o **MAP**.
    Os **parafusos do coletor ficam aqui**.
  - **PARTE DE CIMA (TBI):** segura a borboleta 60 mm; parafusa na base com **parafusos próprios**,
    **escondendo os parafusos do coletor** por baixo. Desmonta a parte de cima e acessa o coletor.
- **Sensores:**
  - **TPS** → eixo da borboleta (lateral da TBI).
  - **MAP** → porta de vácuo na **base**, abaixo da borboleta (1/8" NPT).
  - **IAT** → entrada de ar (topo da TBI), ar fresco.

**Cotas v3 (referência do desenho):**
| Cota | Valor |
|---|---|
| Base (L × W × E) | 120 × 80 × 30 mm |
| Boca central | Ø60 mm |
| Altura da parte de cima (TBI) | ~52 mm |
| Altura total do conjunto | ~99 mm (conferir capô!) |
| Bicos | 4 × **horizontais (90°)**, 2 por lado, 45 mm entre si |
| Furo do bico | reto, radial ao furo central (broca) |
| Flautas | 2 externas, 1/8" NPT de entrada cada |
| Parafusos TBI | 4 × M6 (separados) |
| Parafusos coletor | 4 × M8 (escondidos) |
| MAP | 1/8" NPT (abaixo da borboleta) |

**Fabricação (bem simples):**
- **BASE:** bloco fresado; boca central (furo/mandril); **4 furos retos horizontais** nas laterais
  para os bicos (com rebaixo de o-ring); furos do coletor (2 padrões) e roscas do MAP.
- **FLAUTAS:** 2 tarugos redondos torneados, 2 cavidades de o-ring cada + entrada roscada.
- **PARTE DE CIMA:** anel/flange que recebe a TBI 60 mm e parafusa na base.

**Trade-off honesto do spray horizontal:**
- O jato entra **cruzando** o fluxo de ar (em vez de já apontando para baixo). Para **batch/TBI**
  isso é aceitável — o ar arrasta o combustível para o plenum. Se quiser otimizar no futuro, dá para
  inclinar os furos alguns graus para baixo; mas para o protótipo, **horizontal resolve e é fácil**.

---

## FABRICAÇÃO (DEFINIDO: CNC em alumínio)

### Material
- **6061-T6** — melhor custo-benefício: ótima usinabilidade, boa resistência, anticorrosivo, aceita
  rosca/solda, barato. (7075 = mais forte, caro, desnecessário; fundição = usar **A356**.)

### O que o CNC faz (tudo)
- Faceamento das 2 faces (planas p/ vedação), mandrilamento da **boca Ø60**, bolsas, **furos/roscas**
  (MAP 1/8" NPT, TBI M6, coletor M8), **alojamentos dos bicos com canaleta de o-ring**, chanfros.
- **Flautas:** torneadas (tarugo redondo + cavidades de o-ring + rosca de entrada).

### Furos laterais / angulados
| Recurso | 3 eixos | 4/5 eixos |
|---|---|---|
| Furos verticais, boca, faces, roscas | ✅ | ✅ |
| Furos **laterais (horizontais)** | ✅ com re-fixação / 4º eixo | ✅ fácil |
| Furos **a 30° (angulados)** | ✅ com dispositivo angular / indexação | ✅ trivial |

> Em shop com **4/5 eixos**, dá para voltar aos **bicos a 30°** (melhor atomização) com pouco custo
> extra, pois já se usina pela lateral. Em **3 eixos**, o **horizontal** economiza setups.

### Custo médio (estimativa — confirmar em cotação)
| Cenário | Estimativa |
|---|---|
| Shop BR — protótipo unitário (conjunto completo) | **R$ 1.100 – 3.200** |
| Só a base (unitária) | R$ 600 – 1.800 |
| 2 flautas (torno) | R$ 200 – 600 |
| Parte de cima (adaptador TBI) | R$ 300 – 800 |
| Online (JLCCNC/PCBWay) | ~US$ 100 – 300 + frete/impostos (BR ~60%+) |
| Em série (lote) | cai muito por peça |

- **Encarece:** nº de setups (lateral/angulado), tolerâncias de o-ring, acabamento fino, peça única.
- **Barateia:** enviar **STEP + desenho cotado**, 6061-T6, cotar em 2–3 lugares, ou fundir A356 em lote.

### Impressão 3D (uso recomendado)
- **Mock-up de encaixe:** ✅ ótimo em PLA/PETG — validar caimento, folga do capô, posição de
  bicos/flautas/sensores e furação **antes de usinar**. Não roda o motor.
- **Peça funcional impressa:** ⚠️ só com material de alta temperatura + resistente a combustível
  (PA-CF, PC, PPS/PEEK), **selar porosidade** (vácuo do MAP!) e usar **insertos/luvas metálicas** nos
  furos de parafuso e de bico. Flautas sempre metálicas. Não indicado para venda.
- **Fluxo ideal:** imprimir mock-up → validar → **usinar final em 6061-T6** (ou fundir A356).

#### Custo de impressão 3D (estimativa)
> Base para o cálculo: base **120×80×30 mm** + parte de cima ~52 mm + flautas.
> Volume bruto ~360 cm³ → plástico real (paredes + ~40% infill) ~160–200 cm³ →
> **massa ~200–300 g** (já com suporte/brim/perda). Densidade PA-CF ~1,15 g/cm³.

**Se tiver a impressora (só o filamento):**
| Filamento | Preço/kg (BR) | Custo da peça (~250 g) |
|---|---|---|
| PA-CF / PA6-CF (nylon + carbono) | R$ 250–450 | **R$ 65–115** |
| PETG-CF (mais barato, mais fraco) | R$ 150–250 | R$ 40–65 |
| PLA-CF (só estético/mock-up) | R$ 120–200 | R$ 30–50 |

**Se mandar imprimir em serviço 3D (BR), em PA-CF:** **~R$ 400 – 1.000**
(cobram grama + tempo de máquina + secagem; peça chunky puxa pro meio/alto da faixa).

**Cuidados do PA-CF na função de flange (não resolve sozinho):**
- **Temperatura:** aguenta mais que PLA/PETG, mas o *heat soak* do coletor + gasolina/etanol
  é agressivo. Ideal mesmo seria PPS-CF/PEEK (custo dispara: R$ 2.000+/kg).
- **Porosidade:** precisa **selar** (o MAP puxa vácuo — não pode vazar).
- **Furos de parafuso e alojamento de bico:** usar **insertos/luvas metálicas**.
- **Flautas:** sempre metálicas.

> **Resumo:** PLA/PETG (~R$ 30–65) para **mock-up de encaixe**; PA-CF (~R$ 65–115 filamento
> próprio, ou R$ 400–1.000 em serviço) como **protótipo de bancada** robusto. Para rodar de
> verdade, ainda compensa **usinar em 6061-T6** (R$ 1.100–3.200, ver seção de custo do CNC).

---

## 0. Função da peça
> ⬇️ As seções 0 a 12 abaixo são o **histórico da v1** (galeria interna). O design vigente é o
> **v2** descrito no topo. Mantidas para referência (não excluir).

A flange é a peça-chave da conversão. Ela faz 4 papéis ao mesmo tempo:
1. **Adapta** a base do carburador (coletor) ao corpo de borboleta (TBI 60 mm).
2. **Segura os 4 bicos injetores**, borrifando abaixo da borboleta.
3. **Aloja a galeria (rail) de combustível** que alimenta os bicos.
4. **Fornece a tomada de vácuo do MAP** (abaixo da borboleta).

Funciona como um espaçador espesso usinado, entre o coletor e a TBI.

---

## 1. Compatibilidade dupla (DEFINIDO)

A face **inferior** recebe **os dois padrões de furação** → serve em dois tipos de coletor
(flange "universal", boa para comercializar):

| Carburador/base | Furação | Medida |
|---|---|---|
| **Brosol/Solex 2E–3E** | **3 furos** (triangular) | medir no coletor (sai sem furação de fábrica) |
| **Weber DFV/DGV 446** | **4 furos** (retangular) | **46 × 93 mm** (padrão DGV) |

- Os dois padrões ocupam posições diferentes → cabem **na mesma placa** sem conflito.
- A **boca central** é feita como **oval/rasgo** grande, liberando as bocas dos dois carburadores
  e a saída da TBI (~60 mm).

---

## 2. Dimensões de referência

| Cota | Descrição | Valor |
|---|---|---|
| L | Comprimento | **120 mm** (referência de mercado das bases 2E/3E) |
| W | Largura | **75 mm** |
| E | Espessura total | **25–30 mm** (para caber bico + galeria; base comum é 20 mm) |
| Ø2 | Boca da TBI | **~60 mm** (confirmar na TBI Bosch) |
| DFV | Furação Weber DFV/DGV 446 | **46 × 93 mm** (4 furos) |
| 3E | Furação Brosol 2E/3E | `medir` (3 furos) |
| C | Furação da TBI (topo) | `medir` no corpo Bosch 60 mm |
| H | Altura livre até o capô | `medir` (risco de interferência!) |

> ⚠️ **Altura:** a flange (25–30 mm) + a TBI somam altura. Conferir folga do **capô** antes de usinar.

### 2.1 Cotas PROPOSTAS (do desenho cotado — referência, confirmar no coletor)
| Cota | Valor proposto |
|---|---|
| Comprimento (L) | **120 mm** |
| Largura (W) | **75 mm** |
| Espessura (E) | **28 mm** |
| Boca central | **Ø60 mm** (centralizada) |
| Distância entre bicos do mesmo lado (C/C) | **45 mm** |
| Recuo do bico até a borda | **12 mm** |
| Ângulo dos bicos | **30°** |
| Furos da TBI (topo) | **4× Ø8** em retângulo **70 × 50 mm** |
| Padrão Weber DFV 446 (base) | **46 × 93 mm** (4× Ø8) |
| Padrão Brosol 3E (base) | **~66 × 60 mm** triangular (3 furos) — confirmar |
| Galeria de combustível | **Ø8 mm** passante longitudinal |
| Tomada MAP / entrada combustível | rosca **1/8" NPT** |

> Estes valores são a **proposta de partida** mostrada no desenho cotado. As cotas dos furos do 3E
> e da TBI devem ser **confirmadas com medição** antes de usinar.

---

## 3. Vistas (resumo — ver imagem no topo)

### 3.1 Face superior (TOPO — lado da TBI)
```
        +------------------------------------------------------+
        |  o (furo TBI)                          (furo TBI) o   |
        |        __________________________________           |
        |  B1   /                                  \    B3     |
        |  -->>|          BOCA OVAL CENTRAL          |<<--     |
        |  B2   \__________________________________/    B4     |
        |   [MAP] furo de vacuo (abaixo da borboleta)          |
        |  o (furo TBI)                          (furo TBI) o   |
        +------------------------------------------------------+
   B1..B4 = 4 bicos (2 por lado) apontando p/ o centro
   [MAP]  = tomada de vacuo (1/8 NPT)
```

### 3.2 Face inferior (dois padrões)
```
   3 furos (Brosol 3E, triangular)   +   4 furos (Weber DFV 446, 46x93)
   sobrepostos na mesma placa, sem conflito de posicao
```

### 3.3 Corte lateral (ângulo dos bicos + galeria)
```
        TBI (borboleta) -> ar entra por cima
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        \  bico 30 deg          bico 30 deg  /     FACE SUPERIOR
   [GAL]==*========= centro =========*======[GAL]  GAL = galeria interna
          spray \                 / spray
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        COLETOR (base 3E/DFV) -> plenum         FACE INFERIOR
```

---

## 4. Bicos na flange (mecânica)

- **Quantidade:** 4 (2 de cada lado longo).
- **Ângulo:** ~**30°** da vertical, spray convergindo ao centro da boca, **abaixo da borboleta**.
- **Alojamento do bico:** rebaixo usinado com **2 assentos de o-ring**:
  - o-ring **inferior** (lado do ar/coletor);
  - o-ring **superior** (lado da galeria de combustível).
- **Bico usado:** Bosch **0280156086** (28 lb/h). Conferir o **diâmetro do corpo e o-rings** para
  usinar os alojamentos na medida certa (padrão EV6/USCAR).
- **Fixação dos bicos:** grampo/retentor (clip) ou tampa aparafusada prendendo o topo dos bicos
  contra o assento.

---

## 5. Galeria de combustível (rail interno)

Duas construções possíveis:

**A) Galeria usinada interna (mais elegante):**
- Furo passante longitudinal atravessando a flange, cruzando os 4 alojamentos de bico.
- Tampar as **2 pontas** com bujões roscados; usar 1 ponta como **entrada** (1/8" NPT ou banjo).
- Prever **saída** para o regulador de pressão (retorno).

**B) Trilho (rail) externo aparafusado (mais fácil de fabricar):**
- Barra de alumínio por cima com furos alinhados aos bicos; bicos atravessam a flange.
- Vedação por o-ring em cada bico; entrada/saída nas pontas do trilho.

```
ENTRADA -> [==== galeria ==== ] -> SAIDA (p/ regulador -> retorno)
              |    |    |    |
             B1   B2   B3   B4
```

- **Pressão:** 3 bar, regulador **com retorno**.
- Material da galeria/vedação compatível com gasolina/etanol (Viton nos o-rings).

---

## 6. Tomada de vácuo do MAP

- Furo roscado **1/8" NPT** na lateral, comunicando com a região **abaixo da borboleta** (plenum).
- Mangueira curta e rígida até o sensor MAP (ou MAP direto na flange).
- Evitar pegar vácuo "ported" (acima da borboleta) — o MAP precisa do vácuo do coletor.

---

## 7. IAT (onde NÃO colocar)

- A **IAT (temp. do ar)** vai na **entrada de ar da TBI** (ar fresco), **não** na flange
  (a flange esquenta pelo coletor e falsearia a leitura).

---

## 8. Material, usinagem e térmica

- **Material:** alumínio **6061-T6** (bom p/ usinar) ou 7075.
- **Fabricação:** CNC (preferível para os 2 padrões de furos + galeria) ou fresa + furadeira de bancada.
- **Isolamento térmico:** junta de **fenolite/fibra** entre a flange e o coletor → reduz *heat soak*
  e o risco de **vapor lock** nos bicos.
- **Acabamento:** faces planas e retificadas para boa vedação; quebrar arestas.

---

## 9. Vedação

| Interface | Vedação |
|---|---|
| Flange ↔ TBI (topo) | junta apropriada + faces planas |
| Flange ↔ coletor (base) | junta + fenolite (isolante térmico) |
| Bico ↔ alojamento | o-rings Viton (ar e combustível) |
| Galeria (pontas) | bujões roscados com vedação |
| MAP / entrada comb. | roscas NPT com veda-rosca compatível com combustível |

---

## 10. Roteiro de fabricação (sugerido)

1. Cortar o bloco de alumínio no bruto (~125 × 80 × 32 mm) e faceamento nas 2 faces.
2. Usinar a **boca central oval** (passagem de ar).
3. Furar/rosquear os **4 furos da TBI** (topo) conforme a Bosch 60 mm.
4. Furar os **dois padrões** na base: 3 furos (3E) + 4 furos (46×93 DFV).
5. Usinar os **4 alojamentos de bico** (ângulo ~30°, com rebaixos de o-ring).
6. Furar a **galeria** longitudinal cruzando os bicos; roscar pontas (bujões/entrada/saída).
7. Furar/rosquear a **tomada do MAP** (1/8 NPT) abaixo da borboleta.
8. Rebarbar, limpar cavacos, testar vedação (ar comprimido / estanqueidade da galeria).

---

## 11. BOM da flange

| Item | Qtd | Obs |
|---|---|---|
| Bloco alumínio 6061 (~125×80×32 mm) | 1 | matéria-prima |
| O-rings Viton p/ bico | 8 | 2 por bico |
| Bujões roscados (pontas da galeria) | 2 | 1/8" NPT |
| Conexão de entrada de combustível | 1 | 1/8" NPT ou banjo |
| Conexão/adaptador de saída p/ regulador | 1 | conforme regulador |
| Junta fenolite (base) + juntas | 2+ | isolamento térmico |
| Grampos/retentor dos bicos ou tampa | 1 jogo | fixação dos bicos |
| Parafusos/prisioneiros TBI e base | jogo | conforme furação |

---

## 12. Checklist do tópico
- [x] Definir compatibilidade → **3E (3 furos) + DFV 446 (46×93, 4 furos)**
- [x] Dimensão base de referência → **120 × 75 × ~25–30 mm**
- [x] Padrão DFV 446 → **46 × 93 mm**
- [ ] Medir furação do **3E** no coletor real
- [ ] Medir furação da **TBI Bosch 60 mm** (topo)
- [ ] Confirmar **altura livre do capô** (flange + TBI)
- [ ] Medir corpo/o-rings do bico **0280156086** p/ usinar alojamentos
- [ ] Escolher construção da galeria (interna A x trilho externo B)
- [ ] Fechar **desenho CAD** de fabricação
