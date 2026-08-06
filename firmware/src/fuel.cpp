#include "fuel.h"
#include "sensors.h"
#include "closed_loop.h"
#include "pins.h"
#include <Arduino.h>
#include <math.h>

// Placeholder VE — substituir por tabela 2D calibrada
static const float DISPLACEMENT_CC = 4400.0f;
static const float INJ_FLOW_G_MIN = 213.0f * 4.0f;  // 4 bicos 0280156086
static const float VE_DEFAULT = 0.75f;

float fuelVeLookup(float rpm, float mapKpa) {
  (void)rpm;
  (void)mapKpa;
  return VE_DEFAULT;
}

float fuelCalcPulseWidthMs(float rpm, float mapKpa, float iatC, float vbat) {
  if (rpm < 100.0f) return 0.0f;

  float ve = fuelVeLookup(rpm, mapKpa);
  float iatK = iatC + 273.15f;
  if (iatK < 200.0f) iatK = 298.0f;

  // Speed-density simplificado
  float airMass = (mapKpa * DISPLACEMENT_CC) / (iatK * 120.0f);  // escala empírica
  float fuelMass = airMass * ve / STOICH_AFR;
  float pulseMs = (fuelMass / INJ_FLOW_G_MIN) * 60000.0f / rpm;

  pulseMs *= (1.0f + closedLoopGetTrim());
  pulseMs += injectorDeadTimeMs(vbat);
  if (pulseMs < 0.0f) pulseMs = 0.0f;
  return pulseMs;
}
