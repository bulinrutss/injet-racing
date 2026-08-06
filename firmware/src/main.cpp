/*
 * INJET RACING — Fase 1 firmware (referência / bancada)
 * STM32F407 Black Board · speed-density · batch-fire · wideband DIY
 *
 * Serial 115200: log RPM, MAP, lambda, pulse width, VBat
 */
#include <Arduino.h>
#include "pins.h"
#include "wideband.h"
#include "sensors.h"
#include "fuel.h"
#include "rpm.h"
#include "closed_loop.h"

static uint32_t lastLogMs = 0;
static uint32_t lastFuelMs = 0;
static float lastPulseMs = 0.0f;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);

  pinMode(PIN_INJ1, OUTPUT);
  pinMode(PIN_INJ2, OUTPUT);
  pinMode(PIN_INJ3, OUTPUT);
  pinMode(PIN_INJ4, OUTPUT);
  pinMode(PIN_RL_PUMP, OUTPUT);

  rpmInit();
  widebandInit();
  closedLoopInit();

  digitalWrite(PIN_RL_PUMP, HIGH);  // bomba on (substituir por lógica relé)
}

void loop() {
  widebandUpdate();

  float rpm = rpmGet();
  float mapKpa = sensorsReadMapKpa();
  float tps = sensorsReadTpsPct();
  float clt = sensorsReadCltC();
  float iat = sensorsReadIatC();
  float vbat = sensorsReadVbat();
  float lambda = widebandGetLambda();

  closedLoopUpdate(rpm, mapKpa, tps, clt, lambda);

  uint32_t now = millis();
  if (now - lastFuelMs >= 10) {
    lastFuelMs = now;
    lastPulseMs = fuelCalcPulseWidthMs(rpm, mapKpa, iat, vbat);
    // TODO: agendar injeção batch-fire por timer (1–2× por volta)
  }

  if (now - lastLogMs >= 100) {
    lastLogMs = now;
    Serial.print("RPM:");
    Serial.print(rpm, 0);
    Serial.print(" MAP:");
    Serial.print(mapKpa, 1);
    Serial.print(" TPS:");
    Serial.print(tps, 0);
    Serial.print(" CLT:");
    Serial.print(clt, 0);
    Serial.print(" VBat:");
    Serial.print(vbat, 1);
    Serial.print(" L:");
    Serial.print(lambda, 3);
    Serial.print(" PW:");
    Serial.print(lastPulseMs, 2);
    Serial.print(" TRIM:");
    Serial.println(closedLoopGetTrim(), 3);
  }
}
