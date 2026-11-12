import numpy as np
import time

# --- preconditions ---
T = temperature(); B = magnet.field()
print(f"precond: T={T*1e3:.1f} mK ; B={B*1e3:.4f} mT ; k_tg={k_tg.volt():+.3f} k_bg={k_bg.volt():+.3f} V ; dc205={dc205_1.volt():+.3f} V")
assert T < 0.1, f"T not at base: {T} K"
assert abs(B) < 0.005, f"field not pristine: {B} T"
sr830_1.amplitude(0.05); meas_config["bias_voltage_1"] = sr830_1.amplitude()
assert abs(sr830_1.amplitude()-0.05) < 1e-4, "AC drive not 0.5 nA"

# operating point = global Rxx minimum from the Step-1 map
TG_OP, BG_OP = 0.02, 2.70
k_tg.nplci(1); k_bg.nplci(1)

# DC bias axis: V_dc/1e8 = I_dc ; -1..+1 V -> -10..+10 nA
# NOTE: volt.step left at its setup default (0.005 V) — hard ban on changing it.
Vdc = np.linspace(-1.0, 1.0, 101)
Rbias = meas_config["bias_resistor"]

meas_config["comment"] = (
    f"bias-spectroscopy point check at Step-1 Rxx-min (Vtg={TG_OP}, Vbg={BG_OP}; n~+2.2e12, D~-0.2 V/nm); "
    f"dV/dI=sr3(4T)/I_ac; I_dc -10..+10 nA via dc205_1/100MOhm; AC 0.5 nA; B~0"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('bias-spectroscopy')
s.add_comment(f'point check @ Vtg={TG_OP} Vbg={BG_OP}; I_dc -10..+10 nA; AC 0.5 nA; B~0')

# move to operating point, zero DC bias, settle
s.ramp(k_bg.volt, BG_OP)
s.ramp(k_tg.volt, TG_OP)
s.ramp(dc205_1.volt, Vdc[0])
time.sleep(10)

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
s.fp(dc205_1.volt)
for lia in (sr830_1, sr830_2, sr830_3):
    s.fp(lia.X).fp(lia.P)

s.plot(dc205_1.volt, sr830_3.X)   # dV/dI (4T) vs DC bias
s.plot(dc205_1.volt, sr830_1.X)   # AC current monitor

try:
    s.sweep(dc205_1.volt, Vdc, delay=1.5)
finally:
    s.ramp(dc205_1.volt, 0)        # device-card rule: dc205 -> 0 before ending
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
