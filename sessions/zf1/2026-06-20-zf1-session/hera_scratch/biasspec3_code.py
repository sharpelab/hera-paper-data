import numpy as np
import time

# --- preconditions ---
T = temperature(); B = magnet.field()
print(f"precond: T={T*1e3:.1f} mK ; B={B*1e3:.4f} mT ; k_tg={k_tg.volt():+.3f} k_bg={k_bg.volt():+.3f} V ; dc205={dc205_1.volt():+.3f} V")
assert T < 0.1, f"T not at base: {T} K"
assert abs(B) < 0.005, f"field not pristine: {B} T"

# AC excitation lowered to 0.25 nA to catch a fragile sub-0.5 nA Ic (NOT a volt.step change)
sr830_1.amplitude(0.025); meas_config["bias_voltage_1"] = sr830_1.amplitude()
print(f"AC drive {sr830_1.amplitude()*1e3:.0f} mV -> I_ac {meas_config['bias_voltage_1']/meas_config['bias_resistor']*1e9:.3f} nA")
assert abs(sr830_1.amplitude()-0.025) < 1e-4

# operating point = lowest-Rxx point on the sr2 4T map (best-conducting metal)
TG_OP, BG_OP = -6.48, -3.73
k_tg.nplci(1); k_bg.nplci(1)

# DC bias: V_dc/1e8 = I_dc ; -0.5..+0.5 V -> -5..+5 nA. volt.step left at default (hard ban).
Vdc = np.linspace(-0.5, 0.5, 101)

meas_config["comment"] = (
    f"bias-spectroscopy point check at sr2 Rxx-min (Vtg={TG_OP}, Vbg={BG_OP}; n~-8e12, D~-0.12 V/nm); "
    f"dV/dI=sr2(4T)/I_ac; I_dc -5..+5 nA via dc205_1/100MOhm; AC 0.25 nA; B~0"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('bias-spectroscopy')
s.add_comment(f'point check @ Vtg={TG_OP} Vbg={BG_OP}; I_dc -5..+5 nA; AC 0.25 nA; dV/dI=sr2; B~0')

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

s.plot(dc205_1.volt, sr830_2.X)   # dV/dI (4T = sr2) vs DC bias
s.plot(dc205_1.volt, sr830_1.X)   # AC current monitor

try:
    s.sweep(dc205_1.volt, Vdc, delay=1.5)
finally:
    s.ramp(dc205_1.volt, 0)
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
