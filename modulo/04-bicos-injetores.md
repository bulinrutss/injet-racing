# Tópico 4 — Bicos Injetores (Dimensionamento e Construção)

> Projeto INJET RACING — Fase 1 (TBI / monoponto / batch-fire)
> Arquivo detalhado do tópico 4 do `dicas.md`.
> Aplicações: motor 6 cil ~4400 cc (Galaxie/Opala) e versão 4 cil.

---

## 0. DECISÕES CONFIRMADAS (protótipo 6 cil)

| Item | Decisão |
|---|---|
| Potência-alvo (6 cil 4400 cc) | **130–150 cv** (config atual: Opala 6cc com pistões do 4cc) |
| Nº de bicos | **4** (na flange, batch-fire) |
| Bico escolhido | **Bosch 0280156086 (WLF Automotive) — 28 lb/h (≈ 296 cc/min / 213 g/min N-Heptano) @ 3 bar** (x4) ✅ vazão confirmada (ficha fabricante) |
| Aplicação | GM Astra/Vectra/Zafira/S10/Blazer (2.0/2.2/2.4) — conector EV6/USCAR |
| Impedância | **Alta = 12 Ω** ✅ confirmado na ficha → driver MOSFET simples |
| Pressão de linha | **3 bar** com regulador com retorno |
| Duty no pico | ~73% @130 cv / ~84% @150 cv (ver 4.2) |

> Peça avaliada e **descartada** para este motor: injetor LS **80 lb/h (850 cc/min)** — ver seção 12
> (muito superdimensionado para 130–150 cv).

---

## 1. Conceito e função

Os bicos injetores são as **válvulas eletromagnéticas** que a ECU abre por um tempo controlado
(em milissegundos) para pulverizar combustível. Na Fase 1 (monoponto), os bicos ficam **na flange**,
borrifando **abaixo da borboleta** da TBI, para o plenum comum do coletor.

- **Modo batch-fire:** todos os bicos abrem juntos, 1 ou 2 vezes por ciclo do motor.
- O que a ECU calcula = **tempo de abertura** (pulso), com base em: massa de ar (MAP+IAT+RPM),
  tabela VE, correções (partida, aquecimento, aceleração) e **dead-time** (ver seção 7).

---

## 2. Grandezas e unidades

| Grandeza | Unidade | Observação |
|---|---|---|
| Vazão do bico | **lb/h** ou **cc/min** | 1 lb/h ≈ **10,5 cc/min** (gasolina) |
| Pressão de linha | **bar** ou psi | Vazão varia com **√(pressão)** |
| Impedância | **Ω** | Alta (12–16 Ω) x Baixa (2–3 Ω) |
| Dead-time / latência | **ms** | Tempo morto de abertura (depende da tensão) |
| Duty cycle | **%** | % do tempo que o bico fica aberto (máx útil ~80–85%) |

---

## 3. Fórmula de dimensionamento (vazão)

### 3.1 Vazão TOTAL necessária
```
Vazao_total (lb/h) = Potencia_alvo (cv) × BSFC / Duty_max
```
- **BSFC** (consumo específico) gasolina aspirado ≈ **0,50 lb/cv·h** (faixa 0,45–0,55).
- **Duty_max** de projeto = **0,80** (nunca projetar para 100%).

### 3.2 Vazão POR BICO
```
Vazao_por_bico = Vazao_total / numero_de_bicos
```

### 3.3 Correção por pressão (se mudar de 3 bar)
```
Vazao_nova = Vazao_catalogo × raiz( Pressao_nova / Pressao_catalogo )
```
Ex.: bico de 30 lb/h @ 3 bar → a 4 bar = 30 × √(4/3) ≈ **34,6 lb/h**.

---

## 4. Exemplo aplicado — motor 6 cil 4400 cc

Cenário-alvo: **200 cv** (meta conservadora para o 4400 cc com TBI 60 mm).

```
Vazao_total = 200 × 0,50 / 0,80 = 125 lb/h
Com 4 bicos: 125 / 4 = 31,25 lb/h por bico  ->  ~336 cc/min por bico
```

**Escolha:** 4 bicos de **~32 lb/h (≈ 340 cc/min) @ 3 bar**, alta impedância.

Margem: se um dia buscar ~230 cv, os mesmos bicos vão a ~92% duty — apertado. Se quiser folga,
usar **4 × 36 lb/h (≈ 380 cc/min)**.

### 4.1 Tabela rápida (4 bicos, BSFC 0,5, duty 0,8)
| Potência-alvo | Vazão total | Por bico (x4) |
|---|---|---|
| 150 cv | 94 lb/h | ~24 lb/h (≈ 250 cc/min) |
| 180 cv | 113 lb/h | ~28 lb/h (≈ 300 cc/min) |
| 200 cv | 125 lb/h | ~32 lb/h (≈ 340 cc/min) |
| 230 cv | 144 lb/h | ~36 lb/h (≈ 380 cc/min) |

### 4.2 CASO REAL do protótipo — 130 a 150 cv com 4× Bosch 0280156086 (28 lb/h) ✅

Com os **bicos Bosch 0280156086 de 28 lb/h (≈ 296 cc/min)**, capacidade total = 4 × 28 = **112 lb/h**.

| Cenário | Vazão total necessária | **Duty máx. no pico** | Situação |
|---|---|---|---|
| 130 cv | 81 lb/h | **~73%** | ótimo |
| 140 cv | 88 lb/h | **~78%** | ótimo (no limite ideal) |
| 150 cv | 94 lb/h | **~84%** | aceitável (levemente acima de 80%) |

**Conclusão:** 4× 28 lb/h atende bem 130–150 cv. Casa perfeito até ~140 cv (≤80% duty); a 150 cv fica
em ~84% (aceitável para pico momentâneo em rua). Se buscar 150 cv com folga, subir p/ ~30–32 lb/h.
Na lenta o pulso fica saudável (boa resolução). É a escolha do projeto.

---

## 5. Versão 4 cilindros

Mesma fórmula, potência menor e possibilidade de **2 ou 4 bicos**.

Exemplo **130 cv**:
```
Vazao_total = 130 × 0,50 / 0,80 = 81 lb/h
Com 2 bicos: ~40 lb/h cada (≈ 425 cc/min)
Com 4 bicos: ~20 lb/h cada (≈ 210 cc/min)  <- melhor atomização
```

| Potência-alvo (4 cil) | Vazão total | 2 bicos | 4 bicos |
|---|---|---|---|
| 110 cv | 69 lb/h | ~35 lb/h | ~17 lb/h |
| 130 cv | 81 lb/h | ~40 lb/h | ~20 lb/h |
| 160 cv | 100 lb/h | ~50 lb/h | ~25 lb/h |

**Recomendação:** manter **4 bicos** também no 4 cil se quiser padronizar a flange e o chicote
(mesma placa/driver), variando só a vazão do bico.

---

## 6. Impedância: alta x baixa (DECISÃO)

| Tipo | Resistência | Driver | Uso no projeto |
|---|---|---|---|
| **Alta impedância** | 12–16 Ω | MOSFET simples (satura) | ✅ **ESCOLHIDO** |
| Baixa impedância | 2–3 Ω | Peak & Hold (controle de corrente) | ❌ evitar (complexo) |

**Decisão:** usar **bicos de alta impedância** → driver low-side com 1 MOSFET por canal, sem
circuito de peak&hold. Simplifica hardware e firmware (ver tópico 7 no `dicas.md`).

Corrente por bico (alta-Z, 0280156086 = **12 Ω** confirmado): I = 12 V / 12 Ω = **1,0 A** → tranquilo para um IRLZ44N.

---

## 7. Dead-time (tempo morto / latência)

O bico demora um tempinho para **abrir** de fato após receber tensão. Esse atraso:
- **Aumenta** quando a tensão da bateria **cai** (partida, por ex.).
- Deve ser **somado** ao tempo calculado de injeção, senão a mistura fica pobre em baixa tensão.

Tabela típica (bico alta-Z ~ referência, ajustar ao real):
| Tensão da bateria | Dead-time aprox. |
|---|---|
| 8,0 V | ~2,0 ms |
| 11,0 V | ~1,3 ms |
| 13,8 V | ~1,0 ms |
| 15,0 V | ~0,9 ms |

No firmware: `tempo_final = tempo_calculado + dead_time(Vbat)` — usar a leitura de VBat sense.

---

## 8. Montagem na flange (mecânica)

- **Quantidade:** 4 bicos (2 de cada lado), apontando ~30° da vertical, convergindo ao centro,
  **abaixo da borboleta**.
- **Vedação:** o-ring no lado do combustível (assento na galeria) e o-ring no lado do ar.
- **Galeria (rail):** furo passante na flange alimentando os 4 bicos; entrada 1/8" NPT ou banjo;
  saída para o regulador com retorno.
- **Térmica:** isolar a flange do coletor (fenolite) para reduzir *heat soak* e vaporização
  (vapor lock) no bico.
- Ver desenho completo na seção 3 do `dicas.md`.

---

## 9. Pressão de combustível

- **Linha regulada a 3 bar** com regulador **com retorno** (referência de vácuo opcional).
- Manter pressão estável = vazão previsível (a fórmula da seção 3.3 depende disso).
- Manômetro na linha para conferência/ajuste.

---

## 10. Seleção de peça (DEFINIDO)

**Escolhido:** 4× **Bosch 0280156086** (WLF Automotive), alta impedância **12 Ω**, **28 lb/h (≈ 296 cc/min) @ 3 bar** —
casa com a potência-alvo (130–150 cv) usando ~73–84% de duty no pico. **Ficha completa na seção 10.1.**

- **Impedância confirmada na ficha = 12 Ω (alta-Z → driver simples).** Conferir também com multímetro na peça física.
- Confirmar **vazão real** em bancada antes de fechar o mapa.
- Conector padrão EV6/USCAR (típico deste Bosch) — prever o chicote/conector certo.

> ⚠️ Validar a vazão medida em bancada antes de fechar o mapa base (VE table).
> ⚠️ Peça alternativa avaliada (LS 850 cc) descartada — ver seção 12.

---

## 10.1 Ficha técnica do bico escolhido (CONFIRMADA — fabricante) ✅

**Peça:** Bosch **0280156086** — comercializada pela **WLF Automotive**.

| Parâmetro | Valor | Fonte / observação |
|---|---|---|
| Código | **0280156086** (Bosch 0 280 156 086) | ficha fabricante |
| Marca (fornecedor) | **WLF Automotive** | peça a ser usada no projeto |
| Tipo | Injeção **gasolina** (Petrol) | ficha Bosch |
| **Resistência (impedância)** | **12 Ω → ALTA-Z** ✅ | driver MOSFET simples (sem peak&hold) |
| **Vazão estática @ 3 bar** | **213 g/min** (fluido de teste N-Heptano) | ficha Bosch |
| Vazão convertida | **≈ 28,2 lb/h** (213 × 60 ÷ 453,6) | → gasolina **≈ 296 cc/min** (28 × 10,5) |
| Pressão de referência | **3 bar (43,5 psi)** | casa com a linha do projeto |
| Conector | **EV6 / USCAR** | típico deste Bosch — prever chicote |
| Nº OEM GM | 93 298 396 / 93 392 558 | referência cruzada |

### Compatibilidade (aplicações informadas)
| Veículo | Motor | Anos |
|---|---|---|
| Chevrolet **Astra** | 2.0 | 2005 a 2012 |
| Chevrolet **Vectra** | 2.0 / 2.2 / 2.4 | 2005 a 2011 |
| Chevrolet **Zafira** | 2.0 | 2005 a 2012 |
| Chevrolet **S10** | 2.0 / 2.4 | 2005 a 2011 |
| Chevrolet **Blazer** | 2.0 | 2005 a 2011 |

**O que isso confirma para o projeto:**
- **Impedância ALTA (12 Ω) validada na ficha** → mantém a decisão da seção 6 (driver low-side, 1 MOSFET/canal).
  Corrente por bico: I = 12 V / 12 Ω = **1,0 A** → tranquilo p/ IRLZ44N.
- **Vazão de 28 lb/h (≈ 296 cc/min) confirmada** → atende os 130–150 cv com ~73–84% de duty (seção 4.2).
- Ainda **medir em bancada** a vazão real (tolerância de peça) e **levantar o dead-time × tensão** — a ficha
  do fabricante não traz tempos de abertura/fechamento.

> Nota de conversão: a ficha dá **213 g/min de N-Heptano** (fluido padrão de ensaio Bosch). Isso equivale a
> **≈ 28,2 lb/h** em massa; a vazão volumétrica em gasolina a 3 bar fica em **≈ 296 cc/min** (regra 1 lb/h ≈ 10,5 cc/min).

---

## 11. Checklist do tópico
- [x] Definir potência-alvo real (6 cil) → **130–150 cv**
- [ ] Definir potência-alvo real (4 cil) → a definir
- [x] Fechar vazão do bico → **4× Bosch 0280156086 (28 lb/h) @ 3 bar**
- [x] Confirmar impedância alta no 0280156086 → **12 Ω (alta-Z), confirmado na ficha** (conferir na peça física com multímetro)
- [ ] Medir vazão real em bancada (cc/min @ 3 bar)
- [ ] Levantar curva de dead-time x tensão do bico escolhido
- [ ] Validar o-rings e vedação na flange

---

## 12. Análise da peça avaliada — Injetor LS 80 lb/h (850 cc/min) ❌ para este motor

**Dados informados:** 4 pinos, alta impedância (12 Ω), **80 lb/h (850 cc/min) @ 43,5 PSI (3 bar)**,
1,0 A, abertura 1,14 ms / fechamento 0,85 ms, aplicação GM LS (LS3/LS7/LQ9/LSX).

**Pontos bons:** alta impedância (driver simples ✅), resposta rápida, pressão compatível.

**Por que NÃO usar aqui:** é dimensionado para motores LS de alta potência (350–500+ cv com **8**
bicos). Com **4** desses num motor de 130–150 cv:

| Métrica | 4× 80 lb/h (LS) | 4× 30 lb/h (verde) |
|---|---|---|
| Capacidade total | 320 lb/h (~512 cv) | 120 lb/h (~192 cv) |
| Duty no pico (150 cv) | **~29%** (baixíssimo) | ~78% (ideal) |
| Duty na lenta | **~1–3%** (região não-linear) | saudável |
| Calibração de lenta/carga leve | **difícil, instável** | boa resolução |

**Veredito:** superdimensionado → perde resolução em baixa carga, lenta ruim. **Guardar o LS 850 cc
só se o projeto virar turbo / >300 cv no futuro.** Para o protótipo atual, usar **4× 30 lb/h**.
