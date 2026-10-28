import numpy as np
import time

# --- preconditions: state this cell assumes but does not set ---
T = temperature()
B = magnet.field()
print(f"precond: probe MC T = {T*1e3:.1f} mK (expect base, <100 mK)")
print(f"precond: magnet field = {B*1e3:.4f} mT (PRISTINE — magnet must be untouched, |B|<5 mT)")
print(f"precond: gate setpoints  k_tg={k_tg.volt():+.3f} V  k_bg={k_bg.volt():+.3f} V")
assert T < 0.1, f"T not at base: {T} K"
assert abs(B) < 0.005, f"field not pristine: {B} T — Step-1 map must precede energising the magnet"

# --- drive at the validated 0.5 nA (idempotent re-assert) ---
sr830_1.amplitude(0.05)
meas_config["bias_voltage_1"] = sr830_1.amplitude()
Ibias = meas_config["bias_voltage_1"] / meas_config["bias_resistor"]
print(f"drive: sr830_1.amplitude = {sr830_1.amplitude()*1e3:.0f} mV -> I_bias = {Ibias*1e9:.3f} nA")
assert abs(sr830_1.amplitude() - 0.05) < 1e-4, "drive not at validated 0.5 nA"

# standard readback (not pA-floor) on gate-current channels
k_tg.nplci(1)
k_bg.nplci(1)

# --- map box: full validators, ~0.13 V grid ---
bg_slow = np.linspace(-4.0, 4.2, 61)   # slow axis (0.137 V)
tg_fast = np.linspace(-7.0, 6.0, 101)  # fast axis (0.13 V) — both TG extremes swept every row

meas_config["comment"] = (
    "Step-1 pristine-field gatemap (candidate ID): BG slow [-4,4.2] x TG fast [-7,6], "
    "B~0 (pristine, magnet untouched), drive 0.5 nA, 61x101"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('gatemap')
s.add_comment('zf1 Step-1 candidate-ID map; BG slow [-4,4.2] (61), TG fast [-7,6] (101); B~0 pristine; 0.5 nA')

# ramp to start corner and settle (recipe step 3)
s.ramp(k_bg.volt, bg_slow[0])
s.ramp(k_tg.volt, tg_fast[0])
time.sleep(10)

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for lia in (sr830_1, sr830_2, sr830_3, sr830_4):
    s.fp(lia.X).fp(lia.P)

# live leakage + fast-axis feature monitors
s.plot(k_bg.volt, k_bg.curr)
s.plot('time', k_tg.curr)
s.plot(k_tg.volt, sr830_3.X)   # 4T Rxx along the fast axis
s.plot(k_tg.volt, sr830_2.X)   # 2T along the fast axis

try:
    s.megasweep(k_bg.volt, bg_slow, k_tg.volt, tg_fast, slow_delay=3, fast_delay=1)
finally:
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
