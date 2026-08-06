#include "wideband.h"
#include "pins.h"
#include <Arduino.h>
#include <math.h>

static WidebandState wb = {};
static float ipOffset_mA = 0.0f;
static float unOffset_V = 0.0f;
static uint32_t warmupStartMs = 0;

// Tabela Ip → λ (LSU 4.x, simplificada — expandir conforme mck1117/wideband)
struct IpLambda { float ip_mA; float lambda; };
static const IpLambda IP_LAMBDA[] = {
  {-2.0f, 0.650f}, {-1.5f, 0.700f}, {-1.0f, 0.800f}, {-0.5f, 0.900f},
  { 0.0f, 1.000f}, { 0.5f, 1.050f}, { 1.0f, 1.100f}, { 1.5f, 1.300f},
  { 2.0f, 1.500f}, { 2.5f, 2.000f},
};
static const int N_IP_LAMBDA = sizeof(IP_LAMBDA) / sizeof(IpLambda);

static float adcToVolts(int raw) {
  return (float)raw * ADC_VREF_V / ADC_MAX_COUNTS;
}

static float readAdcAvg(uint8_t pin, uint8_t n = 16) {
  long sum = 0;
  for (uint8_t i = 0; i < n; i++) sum += analogRead(pin);
  return (float)(sum / n);
}

static float ipVoltsTo_mA(float vShunt) {
  return (vShunt / WB_SHUNT_OHMS) * 1000.0f;
}

static float interpolateLambda(float ip_mA) {
  if (ip_mA <= IP_LAMBDA[0].ip_mA) return IP_LAMBDA[0].lambda;
  if (ip_mA >= IP_LAMBDA[N_IP_LAMBDA - 1].ip_mA) return IP_LAMBDA[N_IP_LAMBDA - 1].lambda;
  for (int i = 1; i < N_IP_LAMBDA; i++) {
    if (ip_mA < IP_LAMBDA[i].ip_mA) {
      float t = (ip_mA - IP_LAMBDA[i - 1].ip_mA) /
                (IP_LAMBDA[i].ip_mA - IP_LAMBDA[i - 1].ip_mA);
      return IP_LAMBDA[i - 1].lambda + t * (IP_LAMBDA[i].lambda - IP_LAMBDA[i - 1].lambda);
    }
  }
  return 1.0f;
}

// PID aquecedor — alvo Ri ~80 Ω (LSU 4.2)
static float riIntegral = 0.0f;
static const float HEATER_KP = 0.8f;
static const float HEATER_KI = 0.05f;
static const float HEATER_DT = 0.01f;

static void updateHeaterPid() {
  float err = WB_RI_TARGET_OH - wb.ri_ohms;
  riIntegral += err * HEATER_KI * HEATER_DT;
  if (riIntegral > 1.0f) riIntegral = 1.0f;
  if (riIntegral < 0.0f) riIntegral = 0.0f;
  float out = HEATER_KP * err + riIntegral;
  if (out < 0.0f) out = 0.0f;
  if (out > 1.0f) out = 1.0f;
  wb.heaterDuty = out;
  analogWrite(PIN_HEATER, (int)(out * 255.0f));
  wb.heaterStable = fabsf(wb.ri_ohms - WB_RI_TARGET_OH) < 15.0f;
}

// Malha Un → Ip (simplificada — referência mck1117/wideband)
static void updatePumpCurrent() {
  float err = WB_UN_TARGET_V - wb.un_V;
  static float ipCmd_mA = 0.0f;
  ipCmd_mA += err * 0.5f;  // ganho proporcional simples
  if (ipCmd_mA < -5.0f) ipCmd_mA = -5.0f;
  if (ipCmd_mA > 5.0f) ipCmd_mA = 5.0f;
  // DAC Vm ajusta terra virtual; valor base ~2,5 V
  float vm = 2.5f + err * 0.1f;
  if (vm < 1.0f) vm = 1.0f;
  if (vm > 3.0f) vm = 3.0f;
  analogWrite(PIN_DAC_VM, (int)(vm / ADC_VREF_V * 255.0f));
}

static void measureRi() {
  // Pulso curto via R_ESR — leitura simplificada
  pinMode(PIN_RI_PULSE, OUTPUT);
  digitalWrite(PIN_RI_PULSE, HIGH);
  delayMicroseconds(100);
  float v = adcToVolts((int)readAdcAvg(PIN_ADC_UN, 4));
  digitalWrite(PIN_RI_PULSE, LOW);
  if (v > 0.01f) {
    wb.ri_ohms = WB_R_ESR_OHMS * (ADC_VREF_V / v - 1.0f);
  }
}

void widebandInit() {
  pinMode(PIN_HEATER, OUTPUT);
  pinMode(PIN_RI_PULSE, OUTPUT);
  pinMode(PIN_DAC_VM, OUTPUT);
  analogWrite(PIN_HEATER, 0);
  warmupStartMs = millis();
  wb.ready = false;
}

void widebandUpdate() {
  wb.un_V = adcToVolts((int)readAdcAvg(PIN_ADC_UN)) - unOffset_V;
  float ipV = adcToVolts((int)readAdcAvg(PIN_ADC_IP));
  wb.ip_mA = ipVoltsTo_mA(ipV) - ipOffset_mA;

  measureRi();
  updateHeaterPid();
  updatePumpCurrent();

  wb.lambda = interpolateLambda(wb.ip_mA);
  wb.afr = wb.lambda * STOICH_AFR;

  uint32_t elapsed = (millis() - warmupStartMs) / 1000;
  wb.ready = wb.heaterStable && elapsed > 30;
}

float widebandGetLambda() { return wb.lambda; }
float widebandGetAfr() { return wb.afr; }
bool widebandIsReady() { return wb.ready; }

void widebandCalibrateFreeAir() {
  // LSU 4.2: sonda fora do escape, aquecida, ar limpo
  delay(5000);
  float ipSum = 0, unSum = 0;
  const int n = 32;
  for (int i = 0; i < n; i++) {
    ipSum += adcToVolts((int)readAdcAvg(PIN_ADC_IP));
    unSum += adcToVolts((int)readAdcAvg(PIN_ADC_UN));
    delay(50);
  }
  ipOffset_mA = ipVoltsTo_mA(ipSum / n);
  unOffset_V = unSum / n - WB_UN_TARGET_V;
}
