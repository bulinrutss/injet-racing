#include "sensors.h"
#include "pins.h"
#include <Arduino.h>
#include <math.h>

static const float NTC_BETA = 3950.0f;
static const float NTC_R25 = 2500.0f;
static const float NTC_PULLUP = 2260.0f;

static float ntcAdcToC(int raw) {
  float v = (float)raw * ADC_VREF_V / ADC_MAX_COUNTS;
  if (v <= 0.01f || v >= ADC_VREF_V - 0.01f) return -40.0f;
  float r = NTC_PULLUP * v / (ADC_VREF_V - v);
  float invT = (1.0f / 298.15f) + (1.0f / NTC_BETA) * logf(r / NTC_R25);
  return (1.0f / invT) - 273.15f;
}

static float readAdcAvg(uint8_t pin, uint8_t n = 16) {
  long sum = 0;
  for (uint8_t i = 0; i < n; i++) sum += analogRead(pin);
  return (float)(sum / n);
}

float sensorsReadVbat() {
  float v = (float)readAdcAvg(PIN_VBAT) * ADC_VREF_V / ADC_MAX_COUNTS;
  return v * VBAT_DIV_RATIO;
}

float sensorsReadMapKpa() {
  float v = (float)readAdcAvg(PIN_MAP) * ADC_VREF_V / ADC_MAX_COUNTS;
  v *= (10000.0f + 18000.0f) / 18000.0f;  // reconstrói 0–5 V
  return v * 20.0f;  // ~0–100 kPa linear (calibrar 2 pontos no carro)
}

float sensorsReadTpsPct() {
  float v = (float)readAdcAvg(PIN_TPS) * ADC_VREF_V / ADC_MAX_COUNTS;
  return (v / ADC_VREF_V) * 100.0f;
}

float sensorsReadIatC() { return ntcAdcToC((int)readAdcAvg(PIN_IAT)); }
float sensorsReadCltC() { return ntcAdcToC((int)readAdcAvg(PIN_CLT)); }

float injectorDeadTimeMs(float vbat) {
  // Tabela 04-bicos-injetores.md — interpolar
  if (vbat <= 8.0f) return 2.0f;
  if (vbat <= 11.0f) return 1.3f + (11.0f - vbat) * (2.0f - 1.3f) / 3.0f;
  if (vbat <= 13.8f) return 1.0f + (13.8f - vbat) * (1.3f - 1.0f) / 2.8f;
  if (vbat <= 15.0f) return 0.9f + (15.0f - vbat) * (1.0f - 0.9f) / 1.2f;
  return 0.9f;
}
