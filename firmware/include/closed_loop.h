#pragma once

void closedLoopInit();
void closedLoopUpdate(float rpm, float mapKpa, float tpsPct, float cltC, float lambda);

float closedLoopGetTrim();     // ±0.15 max
bool  closedLoopIsActive();
