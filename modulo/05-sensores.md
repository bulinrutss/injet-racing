# Tópico 5 — Sensores (IAT, MAP, TPS, CLT)

> Projeto INJET RACING — Fase 1 (TBI / monoponto / batch-fire / speed-density)
> Arquivo detalhado do tópico 5 do `dicas.md`.
> Motor de referência: Opala 6 cil ~4400 cc (aspirado). Versão 4 cil compartilha o mesmo hardware.
> ⚡ **Placa/MCU e adaptação 5 V (Arduino) ↔ 3,3 V (STM32): ver `00-hardware.md`.**
> As ligações abaixo assumem **5 V** (Arduino). No STM32 (3,3 V) os divisores/pull-ups mudam — ver `00-hardware.md`.

---

## 0. DECISÕES CONFIRMADAS (peças escolhidas)

| Sensor | Função | Peça escolhida | Tipo elétrico | Montagem |
|---|---|---|---|---|
| **IAT** | Temp. do ar admitido | **Bosch 0280130085** | NTC ~2,5k @ 20 °C, 2 vias | **push-in** (borracha) na parede da TBI, acima da borboleta |
| **MAP** | Pressão do coletor (carga) | **Bosch 0279980411** (VW Gol 1 bar) | analógico 0–5 V, 3 vias | **mangueira** → furo 1/8" NPT na flange, abaixo da borboleta |
| **TPS** | Posição da borboleta | **Gol Mi 96-98** | potenciômetro 3 vias | parafusa **direto** no eixo da TBI (a TBI é feita pra ele) |
| **CLT** | Temp. da água (motor) | **60513205** (GM/Fiat) | NTC ~2,5k @ 20 °C, 2 vias | **roscado** na galeria de água (adaptador se preciso) |

> **Alimentação comum:** todos usam a mesma referência de **+5 V** e **GND** da ECU.
> Manter a **massa dos sensores separada** da massa de potência (bicos/relés) → ligar num único ponto (star ground) na ECU.

---

## 1. Conceito: por que cada sensor

Na estratégia **speed-density**, a massa de ar que entra no motor é estimada por:

```
massa_ar ∝ (MAP × VE(RPM,MAP)) / (R × Temp_ar_absoluta)
```

- **MAP** = quanto de ar (pressão) está entrando → carga do motor.
- **IAT** = densidade do ar (ar frio pesa mais) → corrige a massa.
- **RPM** = rotação (vem do negativo da bobina, tópico 5 do `dicas.md`).
- **VE** = tabela de eficiência volumétrica (o "mapa").
- **TPS** = detecta aceleração (bomba de aceleração eletrônica) e abertura total (WOT / corte de injeção na desaceleração).
- **CLT** = enriquecimento de partida a frio e aquecimento.

---

## 2. Divisor de tensão dos NTC (IAT e CLT)

Os dois NTC (IAT e CLT) são lidos igual: **divisor de tensão** com um resistor de *pull-up* fixo para +5 V.

```
+5V ---[ R_pullup 2,26k ]---+--- ADC (pino do MCU)
                            |
                          [ NTC ]  (IAT ou CLT)
                            |
                           GND
+ capacitor 100 nF do pino ADC p/ GND (filtro anti-ruído)
```

**Tensão lida:**
```
V_adc = 5 × R_ntc / (R_ntc + R_pullup)
ADC   = V_adc / 5 × 1023        (ADC de 10 bits, ref 5 V)
```

**Resistência do NTC a partir do ADC (para converter em temperatura):**
```
R_ntc = R_pullup × ADC / (1023 - ADC)
```

### 2.1 Por que pull-up de 2,26 k
Como o NTC vale ~2,5 k @ 20 °C, um pull-up de **2,26 k** (valor comercial 1% E96, mais fácil de achar que 2,49 k) coloca o ponto de trabalho perto do meio da escala na faixa útil (0–100 °C p/ água, -10–80 °C p/ ar) → **boa resolução**. (2,49 k / 2,5 k / 2,7 k também servem; só recalcular a curva com o valor real usado.)

---

## 3. Curva R×T dos NTC (família Bosch/GM ~2,5k @ 20 °C)

Valores **aproximados** (confirmar medindo — ver seção 3.1). Servem para IAT e CLT (mesma família).

| Temp (°C) | R_ntc (Ω) aprox. | V_adc c/ 2,26k | ADC (0–1023) |
|---|---|---|---|
| -10 | 9 400 | 3,94 V | 806 |
| 0 | 5 900 | 3,52 V | 720 |
| 20 | 2 500 | 2,51 V | 513 |
| 40 | 1 175 | 1,60 V | 328 |
| 60 | 600 | 0,97 V | 199 |
| 80 | 330 | 0,59 V | 120 |
| 100 | 190 | 0,35 V | 72 |

> **Beta aproximado** desta família: **β ≈ 3900 K** (R25 ≈ 2,5 kΩ). Bom para primeira aproximação no firmware.

### 3.1 Como levantar/confirmar a curva real (bancada)
1. Multímetro em resistência nos 2 terminais do sensor.
2. Medir em **3 pontos**: gelo derretendo (**~0 °C**), ambiente (**~25 °C**), água quente com termômetro (**~60–80 °C**).
3. Anotar (T, R). Com 3 pontos já dá pra ajustar Beta ou montar a tabela de interpolação.

---

## 4. MAP — Bosch 0279980411 (1 bar, aspirado)

- **Saída analógica 0–5 V** proporcional à pressão absoluta.
- 3 fios: **+5 V**, **GND**, **Sinal** (→ ADC, com 100 nF p/ GND).
- Faixa típica ~**20 a 105 kPa** (aspirado). Conectar por **mangueira** à tomada de vácuo da flange (abaixo da borboleta).

**Calibração linear (2 pontos):**
```
kPa = a × ADC + b
```
- **Ponto 1:** motor desligado, chave ligada → MAP lê **pressão atmosférica** (~101 kPa ao nível do mar; ~92–95 kPa em altitude).
- **Ponto 2:** valor de vácuo conhecido (bomba de vácuo com manômetro) OU usar o datasheet do sensor.
- Resolver `a` e `b` com os dois pares (ADC, kPa).

> Sem bomba de vácuo, dá pra começar só com o ponto atmosférico + a inclinação típica do sensor (0,04 kPa/mV aprox.) e refinar depois no motor.

---

## 5. TPS — Gol Mi 96-98 (potenciômetro)

- 3 fios: **+5 V**, **GND**, **Sinal** (cursor do potenciômetro → ADC).
- Tensão do sinal sobe conforme abre a borboleta.
- **Não precisa de pull-up** (é potenciômetro, já entrega tensão).

**Calibração (aprendizado min/max):**
```
TPS_% = 100 × (ADC - ADC_fechado) / (ADC_aberto - ADC_fechado)
```
- **ADC_fechado:** borboleta em repouso (marcha lenta).
- **ADC_aberto:** borboleta em WOT (pé no fundo).
- Guardar esses dois valores (rotina de calibração no firmware) e limitar o resultado a 0–100%.

> ⚠️ Ligar o cursor no pino do **meio** do conector nem sempre é regra — identificar qual pino varia com a borboleta (medir com multímetro girando a borboleta). Os outros dois são +5 V e GND.

---

## 6. Resumo de ligação (pinos da ECU)

| Sensor | Pino ECU | Precisa pull-up? | Filtro |
|---|---|---|---|
| IAT (sinal) | ADC (ex.: A0) | **Sim, 2,26k p/ +5V** | 100 nF |
| CLT (sinal) | ADC (ex.: A1) | **Sim, 2,26k p/ +5V** | 100 nF |
| MAP (sinal) | ADC (ex.: A2) | Não | 100 nF |
| TPS (sinal) | ADC (ex.: A3) | Não | 100 nF |
| +5 V | saída regulada 5 V | — | comum aos 4 |
| GND sensores | massa de sinal (star ground) | — | comum aos NTC/MAP/TPS |

---

## 7. Código de leitura (firmware — Arduino/ATmega2560)

Exemplo didático em C. Lê os 4 sensores e converte para unidades físicas.

```cpp
#include <math.h>

// ---- Pinos ----
const uint8_t PIN_IAT = A0;   // NTC ar   (com pull-up 2,26k)
const uint8_t PIN_CLT = A1;   // NTC agua (com pull-up 2,26k)
const uint8_t PIN_MAP = A2;   // MAP analogico 0-5V
const uint8_t PIN_TPS = A3;   // TPS potenciometro

// ---- Constantes de hardware ----
const float VREF      = 5.0f;      // referencia do ADC
const float ADC_MAX   = 1023.0f;   // 10 bits
const float R_PULLUP  = 2260.0f;   // pull-up dos NTC (ohms) — resistor 2K26 1%

// ---- NTC (Beta) : R25 e Beta da familia ~2,5k ----
const float NTC_R25   = 2500.0f;   // ohms @ 25 C
const float NTC_T25_K = 298.15f;   // 25 C em Kelvin
const float NTC_BETA  = 3900.0f;   // K (ajustar apos medir a curva real)

// ---- Calibracao MAP (linear: kPa = a*ADC + b) ----
// Ajustar 'a' e 'b' apos calibrar (ver secao 4).
float MAP_A = 0.10547f;   // exemplo p/ ~20-105 kPa em 0-5V
float MAP_B = 12.0f;

// ---- Calibracao TPS (aprendida) ----
int TPS_ADC_FECHADO = 120;   // atualizar na rotina de calibracao
int TPS_ADC_ABERTO  = 900;   // atualizar na rotina de calibracao

// Le a media de N amostras de um pino (estabiliza o valor)
int lerADC(uint8_t pino, uint8_t n = 8) {
  long soma = 0;
  for (uint8_t i = 0; i < n; i++) soma += analogRead(pino);
  return (int)(soma / n);
}

// Converte ADC de NTC -> temperatura em C (equacao Beta)
float lerNTC_C(uint8_t pino) {
  int adc = lerADC(pino);
  if (adc <= 0)   adc = 1;            // evita divisao por zero
  if (adc >= 1023) adc = 1022;
  float r_ntc = R_PULLUP * (float)adc / (ADC_MAX - (float)adc);
  // 1/T = 1/T25 + (1/Beta)*ln(R/R25)
  float invT = (1.0f / NTC_T25_K) + (1.0f / NTC_BETA) * log(r_ntc / NTC_R25);
  float T_K = 1.0f / invT;
  return T_K - 273.15f;              // Kelvin -> Celsius
}

// Converte ADC do MAP -> kPa (linear)
float lerMAP_kPa(uint8_t pino) {
  int adc = lerADC(pino);
  return MAP_A * (float)adc + MAP_B;
}

// Converte ADC do TPS -> % (0 fechado, 100 WOT)
float lerTPS_pct(uint8_t pino) {
  int adc = lerADC(pino);
  float pct = 100.0f * (float)(adc - TPS_ADC_FECHADO) /
              (float)(TPS_ADC_ABERTO - TPS_ADC_FECHADO);
  if (pct < 0)   pct = 0;
  if (pct > 100) pct = 100;
  return pct;
}

void setup() {
  Serial.begin(115200);
  analogReference(DEFAULT);   // 5 V
}

void loop() {
  float iat = lerNTC_C(PIN_IAT);
  float clt = lerNTC_C(PIN_CLT);
  float map_kpa = lerMAP_kPa(PIN_MAP);
  float tps = lerTPS_pct(PIN_TPS);

  Serial.print("IAT="); Serial.print(iat, 1); Serial.print("C  ");
  Serial.print("CLT="); Serial.print(clt, 1); Serial.print("C  ");
  Serial.print("MAP="); Serial.print(map_kpa, 1); Serial.print("kPa  ");
  Serial.print("TPS="); Serial.print(tps, 1); Serial.println("%");

  delay(200);
}
```

> **Notas:**
> - A conversão por **Beta** é aproximada; para precisão, trocar por **tabela de interpolação** com os pontos medidos na seção 3.1.
> - No STM32 (produto), o ADC é 12 bits (0–4095) e a referência é **3,3 V** → trocar `ADC_MAX = 4095` e `VREF = 3.3`, e adaptar os divisores/pull-ups dos sensores. **Ver `00-hardware.md` (seções 3 e 4)** para o passo a passo e o cuidado de não ligar sinal de 0–5 V direto no STM32.
> - Filtrar leituras com **média móvel** (já feito com `lerADC(n=8)`); pode aumentar `n` se houver ruído.

---

## 8. Onde cada sensor fica (recapitulando a flange 03c)

| Sensor | Local | Observação |
|---|---|---|
| **IAT** | parede da TBI, **acima** da borboleta | ar fresco; **furo liso + borracha** (o Bosch 0280130085 é push-in, NÃO rosca) |
| **MAP** | tomada de vácuo na flange, **abaixo** da borboleta | 1/8" NPT + mangueira até o sensor |
| **TPS** | eixo da borboleta da TBI | parafusa direto (TBI feita pra ele) |
| **CLT** | galeria de água / cabeçote do Opala | roscado; usar adaptador de latão ou inline na mangueira se a rosca não casar |

> ⚠️ **Correção do doc 03c:** lá está escrito "IAT rosqueado". Como o sensor escolhido é **push-in**, o furo do IAT na TBI é **liso com borracha de vedação**, não rosca. Ajustar no desenho final.

---

## 9. Checklist do tópico
- [x] Definir IAT → **Bosch 0280130085**
- [x] Definir MAP → **Bosch 0279980411** (VW 1 bar)
- [x] Definir TPS → **Gol Mi 96-98** (parafusa na TBI)
- [x] Definir CLT → **60513205** (GM/Fiat)
- [ ] Medir curva R×T real do IAT e do CLT (3 pontos) e ajustar Beta/tabela
- [ ] Calibrar MAP (ponto atmosférico + vácuo) → achar `a` e `b`
- [ ] Rotina de calibração do TPS (aprender fechado/WOT)
- [ ] Confirmar rosca do CLT 60513205 x galeria de água do Opala (adaptador?)
- [ ] Identificar pino do cursor do TPS (medir girando a borboleta)
- [ ] Prever conectores/chicote de cada sensor (2 vias NTC, 3 vias MAP/TPS)
- [ ] Sonda lambda wideband: ver **`06-sonda-lambda.md`** (LSU 4.2 + op-amps DIY + malha fechada)
- [ ] Sensor VBat (divisor 100k/10k → PC1): ver **`esquema-eletrico.md`** §3.4 e `firmware/include/pins.h`
