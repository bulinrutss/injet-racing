#include "rpm.h"
#include "pins.h"
#include <Arduino.h>

static volatile uint32_t lastPulseUs = 0;
static volatile uint32_t periodUs = 0;
static float rpmFiltered = 0.0f;

static void IRAM_ATTR onRpmPulse() {
  uint32_t now = micros();
  uint32_t dt = now - lastPulseUs;
  if (dt < 5000) return;  // debounce ~12000 RPM max (6 cil)
  periodUs = dt;
  lastPulseUs = now;
}

void rpmInit() {
  pinMode(PIN_RPM, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_RPM), onRpmPulse, FALLING);
}

void rpmUpdate() {
  if (periodUs == 0) return;
  float pulsesPerRev = (float)ENGINE_CYLINDERS / 2.0f;
  float rpm = 60.0e6f / ((float)periodUs * pulsesPerRev);
  rpmFiltered = rpmFiltered * 0.75f + rpm * 0.25f;
}

float rpmGet() { return rpmFiltered; }

bool rpmHasSignal() {
  return (micros() - lastPulseUs) < 500000;  // pulso nos últimos 500 ms
}
