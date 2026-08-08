#pragma once

// INJET RACING — pinagem fixada STM32F407 Fase 1
// Ver esquema-eletrico.md §3.5 e ecu-pcb-1layer-netlist.md

// --- Sensores ADC (J2 esquerda — L16O/L17O/L12O/L17I/L18I) ---
#define PIN_IAT   PC9   // L16O ADC1_IN9
#define PIN_CLT   PC7   // L17O ADC1_IN7
#define PIN_MAP   PC11  // L12O ADC1_IN11
#define PIN_TPS   PC8   // L17I ADC1_IN8
#define PIN_VBAT  PC6   // L18I ADC1_IN6

// --- Lambda wideband DIY ---
#define PIN_DAC_VM    PA4   // DAC1 — terra virtual Vm (~2,5 V)
#define PIN_ADC_IP    PA5   // corrente bomba (shunt 61,9 Ω)
#define PIN_ADC_UN    PA6   // célula Nernst
#define PIN_HEATER    PD12  // PWM aquecedor MOSFET
#define PIN_RI_PULSE  PC0   // pulso Ri (mede resistência Nernst)

// --- RPM ---
#define PIN_RPM   PE8       // R17O — EXTI falling edge (opto PC817)

// --- CAN ---
#define PIN_CAN_RX  PB8
#define PIN_CAN_TX  PB9

// --- Injetores (batch-fire) ---
#define PIN_INJ1  PE9
#define PIN_INJ2  PE11
#define PIN_INJ3  PE13
#define PIN_INJ4  PE15

// --- Relés ---
#define PIN_RL_MAIN  PD8
#define PIN_RL_PUMP  PD9
#define PIN_RL_IAC   PD10

// --- ADC ---
#define ADC_VREF_V       3.3f
#define ADC_MAX_COUNTS   4095.0f

// Divisor VBat 100k / 10k
#define VBAT_R_HI_OHMS   100000.0f
#define VBAT_R_LO_OHMS   10000.0f
#define VBAT_DIV_RATIO   ((VBAT_R_HI_OHMS + VBAT_R_LO_OHMS) / VBAT_R_LO_OHMS)

// Lambda LSU 4.2 (padrão)
#define WB_SHUNT_OHMS    61.9f
#define WB_RI_TARGET_OH  80.0f      // Ω @ ~780 °C
#define WB_UN_TARGET_V   0.450f
#define WB_R_ESR_OHMS    6800.0f   // 6k8 para LSU 4.2

// Motor
#define ENGINE_CYLINDERS 6          // 4 ou 6 — configurável
#define RPM_MIN_VALID    200.0f     // abaixo = falha/parado — não atualiza filtro
#define RPM_MAX_VALID    7000.0f    // acima = ringing/lixo — não atualiza filtro
// Debounce ISR (µs): deve ser < período em RPM_MAX_VALID.
// 6 cil @ 7000 → período ≈ 2857 µs; 2500 deixa margem e ainda corta ringing.
// No carro: ↑ se contar pulso duplo; ↓ se RPM alto “travar” cedo.
#define RPM_DEBOUNCE_US  2500u
#define STOICH_AFR       14.7f
