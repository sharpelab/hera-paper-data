# B_c-perp field-killing test at the SC arc minimum (n=-5.02e11, D=-0.673).
# Decisive constellation piece: does a small B_perp destroy the low-Rxx state
# while the normal state stays put? Rxx (4T, AC 0.5nA, DC bias = 0) vs B.
# FIELD DISCIPLINE (brief): ramp to the extreme, settle, sweep TOWARD 0; never
# increase |B| through 0 during a measurement. Two one-sided sweeps (+50->0,
# -50->0) meet at 0 -> reveals the effective-zero (Rxx min) and B_c_perp.
# *** FIRST magnet energising this session -> injects remanence (~10 mT), ends
#     the pristine-field condition. All base-T zero-field work is done. ***
import numpy as np, time

T=temperature(); B=magnet.field()
print(f"T={T*1e3:.1f} mK  B={B*1e3:.3f} mT  ramp_rate={magnet.ramp_rate()} T/s")
assert T<0.08, f"T not base {T*1e3:.1f} mK"

# gate at arc min, AC 0.5 nA, DC bias 0 (measure Rxx, not Ic)
sr830_1.amplitude(0.05)
for sr in (sr830_1,sr830_3): sr.time_constant(0.3)
sr830_1.sensitivity(1e-3); sr830_3.sensitivity(2e-5)

mc=dict(meas_config); mc["bias_voltage_1"]=sr830_1.amplitude()
mc["comment"]="B_c_perp field-kill at SC arc min n=-5.02e11 D=-0.673; Rxx vs B, Idc=0 Iac=0.5nA; one-sided sweeps to 0"
s=sweep.AsyncStation(mc)
s.add_comment('field-sweep-1d')
s.add_comment('B_c_perp field-killing at SC arc min n=-5.02e11 D=-0.673, base T')
s.ramp(dc205_1.volt,0.0)
s.ramp(k_tg.volt,-5.640); s.ramp(k_bg.volt,4.200); time.sleep(5)
s.fp(temperature).fp(fridge_temperature).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr830_1.X).fp(sr830_1.P).fp(sr830_3.X).fp(sr830_3.P)
s.plot(magnet.field, sr830_3.X)     # live Rxx vs B
s.plot('time', temperature)         # watch for ramp heating

# Sweep A: position at +50 mT, settle, sweep down to 0
s.ramp(magnet.field, 0.05); time.sleep(60)
s.sweep(magnet.field, np.linspace(0.05, 0.0, 101), delay=1.0)
# Sweep B: position at -50 mT, settle, sweep up to 0
s.ramp(magnet.field, -0.05); time.sleep(60)
s.sweep(magnet.field, np.linspace(-0.05, 0.0, 101), delay=1.0)

s.ramp(magnet.field, 0.0)           # park at nominal 0 (carries remanence)
