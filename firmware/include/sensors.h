#pragma once

float sensorsReadVbat();       // volts bateria
float sensorsReadMapKpa();     // kPa absoluto (calibrar 2 pontos)
float sensorsReadTpsPct();     // 0–100 %
float sensorsReadIatC();       // °C
float sensorsReadCltC();       // °C

float injectorDeadTimeMs(float vbat);
