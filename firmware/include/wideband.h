#pragma once

struct WidebandState {
  float lambda;
  float afr;
  float ip_mA;
  float un_V;
  float ri_ohms;
  float heaterDuty;
  bool  ready;
  bool  heaterStable;
};

void widebandInit();
void widebandUpdate();          // chamar a cada ~10 ms

float widebandGetLambda();
float widebandGetAfr();
bool  widebandIsReady();

void widebandCalibrateFreeAir(); // LSU 4.2 — sonda no ar, aquecida
