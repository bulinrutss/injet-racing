#pragma once

void rpmInit();
void rpmUpdate();              // chamar na interrupção ou poll

float rpmGet();
bool  rpmHasSignal();
