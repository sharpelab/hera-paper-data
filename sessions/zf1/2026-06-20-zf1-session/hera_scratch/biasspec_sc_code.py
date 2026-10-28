import numpy as np
import time

# --- preconditions ---
T = temperature(); B = magnet.field()
print(f"precond: T={T*1e3:.1f} mK ; B={B*1e3:.4f} mT ; k_tg={k_tg.volt():+.3f} k_bg={k_bg.volt():+.3f} ; dc205={dc205_1.volt():+.3f}")
assert T < 0.1, f"T not base {T}"
assert abs(B) < 0.005, f"B not pristine {B}"

# AC lowered to 0.1 nA to probe below a sub-nA Ic (NOT a volt.step change)
sr830_1.amplitude(0.01); meas_config["bias_voltage_1"] = sr830_1.amplitude()
print(f"AC drive {sr830_1.amplitude()*1e3:.0f} mV -> I_ac {meas_config['bias_voltage_1']/meas_config['bias_resistor']*1e9:.3f} nA")

TG_OP, BG_OP = -5.61, 4.17        # SC feature center (n~-0.48, D~-0.67)
k_tg.nplci(1); k_bg.nplci(1)

Vdc = np.linspace(-0.5, 0.5, 101)   # I_dc -5..+5 nA ; volt.step left at default
meas_config["comment"] = (
    f"bias-spectroscopy at SC dip (Vtg={TG_OP}, Vbg={BG_OP}; n~-0.48e12, D~-0.67 V/nm); "
    f"dV/dI=sr2&sr3; I_dc -5..+5 nA; AC 0.1 nA; B~0 nominal"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('bias-spectroscopy')
s.add_comment(f'SC dip @ Vtg={TG_OP} Vbg={BG_OP}; I_dc -5..+5 nA; AC 0.1 nA; dV/dI sr2&sr3; B~0')

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
s.plot(dc205_1.volt, sr830_2.X)   # dV/dI (sr2)
s.plot(dc205_1.volt, sr830_3.X)   # dV/dI (sr3)

try:
    s.sweep(dc205_1.volt, Vdc, delay=1.5)
finally:
    s.ramp(dc205_1.volt, 0)
