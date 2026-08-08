# FUT-01 — 3-step / rev-limit por corte de bobina

**Status:** ideia salva · **não** na prodv6 atual  
**Canvas:** `canvases/corte-3step-pcb.canvas.tsx` (Cursor)

## Decisão

- Corta **faísca** (alimentaçãoda bobina), **não** os bicos.
- Cut de combustível sob carga = risco de motor — descartado para limiter/3-step.
- Não é controle de ponto: ignição continua mecânica; ECU só liga/desliga o +12V da bobina por RPM.

## Hardware (delta)

| Ref | Peça | Qtd | Função |
|-----|------|-----|--------|
| Q_ign | 2N7000 ou IRLZ44N | 1 | Driver low-side bobina do relé |
| R_g | 1k (2N7000) / 100Ω (IRLZ) | 1 | Gate série |
| R_pd | 10k | 1 | Gate → GND |
| D_fly | 1N4007 | 1 | Flyback relé |
| RL_IGN | SRD-12V (placa) + relé 20–30A chicote | 1+1 | Abre +12V → bobina (+) |
| CN1 | 1 pino | 1 | Comando / contatos |
| SW_LAUNCH | Switch embreagem/botão | 1 | Limiar baixo (opcional 3-step) |
| R_sw + C | 1k–4k7 + 100nF | 1+1 | Entrada LAUNCH |

**Total típico:** ~6–8 peç. (só limiter) · ~9–13 com launch.

## Ligações (resumo)

| Net | De | Para |
|-----|----|------|
| +12V_IGN | Chave/fusível ignição | RL_IGN COM |
| +12V_COIL | RL_IGN NO | Bobina + (15) |
| COIL− | Bobina − | Módulo/platina (inalterado) |
| GIGN | MCU GPIO | R_g → Q_ign.G |
| — | Q_ign.D | RL_IGN COIL− |
| +12V_PROT | +12V_PROT | RL_IGN COIL+ |

**RPM_IN** (opto no − da bobina) permanece. Validar se cut no +12 afeta contagem; se afetar, hold do último RPM durante o cut.

**Fail-safe:** decidir antes de rotear (rua: preferir faísca ligada se MCU morrer; pista: pode ser cut default).

## Firmware (quando fizer)

- Limiar alto = rev-limit.
- LAUNCH ativo = limiar baixo (3-step).
- Não zerar PWM dos bicos para limiter.

## Fora deste item

- Soft cut INJ / duty 0 nos bicos para 3-step.
- Roda fônica / avanço por mapa → Fase 2 (outro doc).
