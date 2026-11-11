# Tópico 3D — Corpo Completo TBI (2 peças, estilo Inject Solution)

> Projeto INJET RACING — Fase 1 (TBI / monoponto)
> **Direção mecânica vigente:** substituir flange + TBI comprada por um **corpo integrado** em alumínio,
> no conceito da [Inject Solution](https://injectsolution.com.br/) — tira o carburador, encaixa a TBI
> direto no coletor, com bicos, borboleta, sensores e combustível no mesmo conjunto.
> Evolução dos tópicos `03-flange.md`, `03c-flange-55mm-tbi.md` (mantidos como histórico/alternativa).
> 🖼️ **3D 4 ângulos (v6):** `../assets/corpo-completo-tbi-3d-v6.png`

---

## 1. Referência comercial — o que copiar (e o que não)

A Inject Solution vende TBIs **corpo único em alumínio** que substituem o carburador:

| Produto | O que traz integrado |
|---|---|
| [TBI 42 mm](https://injectsolution.com.br/produto/tbi-42mm-1-bico-40-lbs/) | Corpo AL, 1–2 bicos, TPS, IAT, conexão combustível, base p/ coletor |
| [Kit TBI 60 mm](https://injectsolution.com.br/produto/kit-tbi-60mm-modulo-injepro-t3000-chicote-personalizado/) | Corpo AL, 4 bicos, TPS, flautas interligadas, suporte cabo/filtro |
| [Quadrijet](https://injectsolution.com.br/produto/quadrijet-injectsolution/) | Corpo AL, 4 bicos 80 lb/h, TPS, **atuador de lenta**, flautas AL (~26×27×16 cm) |

**Ideia central:** uma peça (ou conjunto) que o cliente **parafusa no coletor** e já tem admissão +
injeção + sensores — sem adaptador + TBI separados.

**O que o INJET RACING faz diferente (proposital):**
- ECU **própria** (não InjePro/T3000).
- Bicos **Bosch 0280156086 (28 lb/h)** — ver `04-bicos-injetores.md`.
- Coletor de referência: **Brosol 3E** no Opala 6 cil ~4400 cc (Galaxie).
- Borboleta alvo: **~55 mm** (melhor casamento que 60 mm neste motor).
- Fase 1: ignição **mecânica** → sem atuador de lenta eletrônico no v1 (opcional v2).
- **2 peças usinadas** (base + corpo) → facilita CNC, vedação e manutenção.

---

## 2. Conceito — corpo completo em 2 partes

```
                    AR (filtro / corneta)
                           |
                    +------+------+
                    |  CORPO (1)  |  <- borboleta, TPS, IAT, entrada ar
                    |  ~55 mm TB  |
                    +------+------+
                    | 4 bicos     |  spray abaixo da borboleta
                    +------+------+
                    |  BASE (2)   |  <- parafusos coletor, MAP, galeria comb.
                    +------+------+
                           |
                      COLETOR 3E
```

### Peça 1 — BASE (inferior)
Fixa no coletor. Concentra tudo que é “motor-side”:

- Face inferior: furação **3E** (medir no coletor real) + opcional **DFV 446 (46×93)**.
- Boca para o plenum: **oval ~70×45 mm** (2 bocas 3E 30/34 mm).
- **4 alojamentos de bico** (Bosch EV6), spray convergindo para a garganta.
- **Galeria de combustível** interna *ou* assentos para **flautas externas** (v1 recomenda flautas — mais fácil de usinar e vedar).
- Porta **MAP** 1/8" NPT — comunicação com plenum **abaixo** da borboleta.
- Parafusos do coletor em **furo rebaixado (Allen)** → cabeça abaixo da face de junção.
- Face superior: plana, junta, **4× M6** recebendo o corpo.

### Peça 2 — CORPO (superior)
“TBI” propriamente dita — usinada, não comprada:

- **Entrada de ar** (corneta/filtro) no topo.
- **Furo da borboleta Ø55 mm** (eixo horizontal, TPS na lateral).
- Geometria interna: **difusor/venturi** suave (transição ar → plenum oval).
- **IAT** (Bosch 0280130085): boss na parede da entrada, **acima** da borboleta, ar fresco.
- **TPS** (Gol Mi): flange padrão no eixo da borboleta.
- Fixação na base: **4× M6** passantes ou prisioneiros; esconde parafusos do coletor.
- Saída inferior: flange plano + junta O-ring ou papel contra a base.

> **Por que 2 peças:** usina cada metade em setups simples (3 eixos); furos de bico e MAP ficam
> na base; borboleta e IAT ficam no corpo; desmonta corpo → acessa coletor e bicos.

---

## 3. Cotas preliminares (v6 — a confirmar no coletor)

| Cota | Valor | Obs |
|---|---|---|
| Envelope externo (L × W) | **~130 × 100 mm** | Referência Quadrijet IS ~26×27 cm; nosso alvo mais compacto |
| Altura BASE | **~35 mm** | Bicos + galeria + MAP |
| Altura CORPO | **~55–65 mm** | Entrada ar + eixo borboleta + difusor |
| Altura total | **~90–100 mm** | ⚠️ Conferir **capô** do Galaxie |
| Borboleta | **Ø55 mm** | Pistão ~Ø55–58 mm conforme cálculo VE |
| Plenum (saída p/ coletor) | **~70 × 45 mm oval** | Abertura 3E |
| Bicos | **4×** inclinados **~25–30°** p/ baixo/centro | Ver geometria 3E em `03c-flange-55mm-tbi.md` |
| Bico C/C (mesmo lado) | **~45 mm** | Herdado v3 |
| Flautas | **2 externas** (tarugo Ø~16–20) | Entrada 1/8" NPT cada |
| MAP | **1/8" NPT** lateral na base | Abaixo do plano da borboleta |
| IAT | push-in **0280130085** | Parede da entrada de ar |
| TPS | Gol Mi 96–98 | Eixo borboleta |
| Parafusos coletor | **M8** rebaixados | Quantidade/padrão = medir no 3E |
| Parafusos BASE↔CORPO | **4× M6** | Retângulo ~80×70 mm (herdar TBI 55 mm) |
| Material | **6061-T6** | Usinabilidade + vedação + custo |

---

## 4. Componentes usinados vs comprados

| Item | Origem | Obs |
|---|---|---|
| Base + corpo AL | **Usinar (CNC)** | Coração do projeto |
| Disco borboleta + eixo | **Comprar kit** ou **sucata TBI** Bosch/VW | Usinar só furo e assentos no corpo |
| Rolamentos eixos TB | Kit TBI / sucata | Não reinventar |
| Mola retorno borboleta | Kit / sucata | |
| TPS | Gol Mi (comprado) | |
| IAT | Bosch 0280130085 | |
| MAP | Bosch 0279980411 (mangueira da base) | |
| 4× bicos | Bosch 0280156086 | |
| O-rings bico (Viton) | 8× (2 por bico) | |
| Flautas | **Tornear** tarugo AL | Ou usinar bloco reto na CNC |
| Parafusos, bujões NPT | Comercial | |
| Juntas | Fenolite (base↔coletor) + papel/O-ring (base↔corpo) | |

---

## 5. Fluxo de ar e combustível

### Ar
```
Filtro → corneta → entrada CORPO → borboleta Ø55 → difusor → junta → plenum oval BASE → coletor
                                              ↑
                                            IAT (ar fresco)
```

### Combustível (flautas externas — v1)
```
Bomba 3 bar → regulador c/ retorno → ENTRADA flauta L
                                        |    |
                                       B1   B2  (lado esquerdo)
                                        |    |
                              [plenum oval na BASE]
                                        |    |
                                       B3   B4  (lado direito)
                                        |    |
                              RETORNO flauta R → regulador → tanque
```

> Flautas **externas** como na Inject Solution (Quadrijet) e no design v3 — evita furo passante
> longitudinal com vedação crítica na base.

### Vácuo MAP
Furo da base até câmara **abaixo da borboleta** (mesmo volume que o coletor enxerga).

---

## 6. Geometria dos bicos (3E)

O 3E tem abertura **alongada (~70×40 mm)**, menor que o Ø55 da borboleta.

- Bicos **inclinados ~30°** para baixo e para dentro → spray cai na garganta, não na “prateleira”.
- Cálculo: centro do bico ~30 mm do eixo, queda ~20 mm → `atan(20/30) ≈ 34°` → alvo **30°**.
- Com CNC **4/5 eixos**, furos inclinados saem limpos; em **3 eixos**, usar indexador ou desenho
  **horizontal (90°)** da v3 (trade-off de atomização aceitável em batch/TBI).

---

## 7. Fabricação CNC — roteiro sugerido

### BASE
1. Bloco bruto ~135×105×40 mm 6061-T6.
2. Facear superior e inferior.
3. Mandrilamento/ fresagem da **boca oval** inferior (plenum).
4. Bolsas dos **4 bicos** (rebaixo duplo o-ring).
5. Furos **inclinados ou laterais** dos bicos.
6. Furação/roscas **coletor** (3E + rebaixo Allen).
7. Boss **MAP** 1/8" NPT.
8. Furos **M6** topo + face de junção retificada.

### CORPO
1. Bloco bruto ~135×105×70 mm.
2. Facear base e topo.
3. **Vazamento interno:** fresa ball-end ou lápides — difusor Ø55 → transição oval.
4. Furo **borboleta Ø55** + assentos de eixo (fresado após montar eixo de referência).
5. Boss **IAT** na parede da entrada.
6. Flange **TPS**.
7. Furos fixação M6 na base.

### Pós-usinagem
- Rebarbar, jatear leve, **anodizar** (opcional, como Quadrijet Black).
- Montar borboleta, TPS, bicos, flautas.
- Teste estanqueidade: ar comprimido na galeria + MAP.

### Mock-up antes do alumínio
1. Imprimir **3D PLA/PETG** (encaixe capô, altura, cabo acelerador).
2. Validar no coletor → usinar 6061.

---

## 8. Máquina necessária — comparativo

| Peça / operação | Router 6040 hobby | Fresadora BR (ex. Carissimi FRC6) |
|---|---|---|
| Base plana, oval, furos | ⚠️ Lento, possível | ✅ |
| Bolsas o-ring bico | ⚠️ Marginal | ✅ |
| Furos bico 30° / lateral | ⚠️ 4º eixo frágil | ✅ 5 eixos |
| Difusor interno corpo | ❌ Muito limitado | ✅ Com ball-end |
| Flautas redondas | ❌ Precisa **torno** | ❌ Precisa **torno** |
| Repetibilidade produção | ❌ | ✅ |

**Veredicto:** corpo completo **não é projeto de router 6040** — o **difusor interno**, bolsas de
o-ring e furos angulados pedem fresadora com rigidez (Carissimi ~R$ 130k faz sentido **só se for
oficina/produção**; para 1–3 protótipos, **terceirizar CNC** ou começar com **flautas + base**
e corpo simplificado).

**Caminho econômico de protótipo:**
- Corpo com difusor **simples** (furo cônico reto, sem venturi otimizado) na CNC terceirizada.
- Flautas no torno.
- Borboleta/eixo de sucata TBI 55 mm Bosch/VW.

---

## 9. BOM mecânica (corpo completo)

| Item | Qtd | Obs |
|---|---|---|
| Bloco AL 6061 base (~135×105×40) | 1 | |
| Bloco AL 6061 corpo (~135×105×70) | 1 | |
| Tarugo AL flautas | 2 | Torno |
| Bicos Bosch 0280156086 | 4 | |
| O-rings Viton bico | 8 | |
| TPS Gol Mi | 1 | |
| IAT 0280130085 | 1 | |
| Kit eixo + disco borboleta Ø55 | 1 | Sucata ou aftermarket |
| Parafusos M8 Allen coletor | jogo | Rebaixados |
| Parafusos M6 base↔corpo | 4 | |
| Conexões 1/8" NPT combustível | 2–3 | Entrada + retorno |
| Junta fenolite base↔coletor | 1 | Isolamento térmico |
| Junta base↔corpo | 1 | Papel AL ou O-ring |
| Grampos/retentor bicos | 1 jogo | |

---

## 10. Fases de desenvolvimento

| Fase | Entrega |
|---|---|
| **A — CAD** | STEP base + corpo, cotado, compatível 3E medido |
| **B — Mock-up 3D** | Encaixe capô + coletor |
| **C — Protótipo AL** | Usinagem CNC (terceirizada ou própria) |
| **D — Bancada** | Estanqueidade + ECU + motor parado |
| **E — Carro** | Mapa VE + aceleração + capô fechado |
| **F — v2 (opcional)** | Atuador lenta, galeria interna, DFV duplo, anodização |

---

## 11. Relação com designs anteriores

| Arquivo | Papel agora |
|---|---|
| `03-flange.md` v3 | Referência de bicos laterais + 2 peças — **base herdada** |
| `03c-flange-55mm-tbi.md` | Referência 3E + ângulo 30° + TBI 55 mm — **geometria bico** |
| `03b-flange-torno.md` | Fallback sem CNC (só base + TBI comprada) |
| **`03d-corpo-completo-tbi.md`** | **Direção vigente** — corpo integrado estilo Inject Solution |

---

## 12. Checklist

- [x] Definir direção → **corpo completo 2 peças**, estilo Inject Solution
- [x] Borboleta alvo → **Ø55 mm**
- [x] Bicos → **4× 0280156086**, batch abaixo da borboleta
- [x] Combustível v1 → **flautas externas**
- [ ] **Medir furação 3E** no coletor do Galaxie
- [ ] Confirmar **altura total × capô**
- [ ] Escolher fonte **eixo/discos borboleta** (sucata TBI 55 mm?)
- [ ] Modelar **CAD** (base + corpo) → STEP para cotação CNC
- [ ] Mock-up 3D → validar encaixe
- [ ] Definir CNC **própria vs terceirizada**
- [ ] Teste estanqueidade galeria + MAP
- [ ] Integrar TPS/IAT/MAP no firmware ECU
