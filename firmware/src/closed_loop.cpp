#include "closed_loop.h"
#include "wideband.h"
#include <Arduino.h>
#include <math.h>

static float trim = 0.0f;
static float trimIntegral = 0.0f;
static bool active = false;

static const float TRIM_MIN = -0.15f;
static const float TRIM_MAX =  0.15f;
static const float KP = 0.5f;
static const float KI = 0.02f;
static const float DT = 0.02f;

void closedLoopInit() {
  trim = 0.0f;
  trimIntegral = 0.0f;
}

static float lambdaTarget(float rpm, float mapKpa, float tpsPct) {
  if (tpsPct > 85.0f || mapKpa > 85.0f) return 0.90f;
  if (rpm < 900.0f) return 1.00f;
  return 1.00f;
}

void closedLoopUpdate(float rpm, float mapKpa, float tpsPct, float cltC, float lambda) {
  active = false;
  if (!widebandIsReady()) return;
  if (cltC < 60.0f) return;
  if (tpsPct > 80.0f) return;
  if (rpm < 400.0f) return;

  float target = lambdaTarget(rpm, mapKpa, tpsPct);
  float err = target - lambda;

  trimIntegral += err * KI * DT;
  if (trimIntegral > TRIM_MAX) trimIntegral = TRIM_MAX;
  if (trimIntegral < TRIM_MIN) trimIntegral = TRIM_MIN;

  trim = KP * err + trimIntegral;
  if (trim > TRIM_MAX) trim = TRIM_MAX;
  if (trim < TRIM_MIN) trim = TRIM_MIN;
  active = true;
}

float closedLoopGetTrim() { return trim; }
bool closedLoopIsActive() { return active; }
