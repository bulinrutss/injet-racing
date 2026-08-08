#include "rpm.h"
#include "pins.h"
#include <Arduino.h>

static volatile uint32_t lastPulseUs = 0;
static volatile uint32_t periodUs = 0;
static float rpmFiltered = 0.0f;

static void IRAM_ATTR onRpmPulse() {
  uint32_t now = micros();
  uint32_t dt = now - lastPulseUs;
  if (dt < RPM_DEBOUNCE_US) return;
  periodUs = dt;
  lastPulseUs = now;
}

void rpmInit() {
  pinMode(PIN_RPM, INPUT);  // pull-up externo R22 4k7 no coletor do PC817
  attachInterrupt(digitalPinToInterrupt(PIN_RPM), onRpmPulse, FALLING);
}

void rpmUpdate() {
  // Snapshot atômico: ISR pode escrever periodUs a qualquer momento
  noInterrupts();
  uint32_t period = periodUs;
  interrupts();

  if (period == 0) return;
  float pulsesPerRev = (float)ENGINE_CYLINDERS / 2.0f;
  float rpm = 60.0e6f / ((float)period * pulsesPerRev);
  if (rpm < RPM_MIN_VALID || rpm > RPM_MAX_VALID) return;
  rpmFiltered = rpmFiltered * 0.75f + rpm * 0.25f;
}

float rpmGet() { return rpmFiltered; }

bool rpmHasSignal() {
  return (micros() - lastPulseUs) < 500000;  // pulso nos últimos 500 ms
}
