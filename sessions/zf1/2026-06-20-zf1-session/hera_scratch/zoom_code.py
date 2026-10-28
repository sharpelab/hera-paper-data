import numpy as np
import time

# --- preconditions ---
T = temperature(); B = magnet.field()
print(f"precond: T={T*1e3:.1f} mK ; B={B*1e3:.4f} mT (nominal zero; ~2 mT trapped at sample) ; "
      f"k_tg={k_tg.volt():+.3f} k_bg={k_bg.volt():+.3f} V")
assert T < 0.1, f"T not at base: {T} K"
assert abs(B) < 0.005, f"field unexpectedly finite: {B} T"
sr830_1.amplitude(0.05); meas_config["bias_voltage_1"] = sr830_1.amplitude()
assert abs(sr830_1.amplitude()-0.05) < 1e-4, "drive not 0.5 nA"

k_tg.nplci(1); k_bg.nplci(1)

# zoom box: V_bg>0 / V_tg<0 quadrant, 0.07 V grid
bg_slow = np.linspace(0.0, 4.2, 61)    # slow (0.07 V)
tg_fast = np.linspace(-7.0, 0.0, 101)  # fast (0.07 V)

meas_config["comment"] = (
    "SC re-investigation zoom: V_bg>0/V_tg<0 quadrant (large -D), BG slow [0,4.2] x TG fast [-7,0], "
    "0.07 V grid, Rxx=sr2(4T), 0.5 nA, B~0 (nominal; ~2 mT trapped)"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('gatemap')
s.add_comment('SC zoom V_bg>0/V_tg<0; BG slow [0,4.2] (61), TG fast [-7,0] (101); 0.07 V; Rxx=sr2; B~0 nominal')

s.ramp(k_bg.volt, bg_slow[0])
s.ramp(k_tg.volt, tg_fast[0])
time.sleep(10)

# trimmed reads: sr1 (current) + sr2 (4T Rxx) + gates + T
s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for lia in (sr830_1, sr830_2):
    s.fp(lia.X).fp(lia.P)

s.plot(k_bg.volt, k_bg.curr)
s.plot('time', k_tg.curr)
s.plot(k_tg.volt, sr830_2.X)   # 4T Rxx along the fast axis

try:
    s.megasweep(k_bg.volt, bg_slow, k_tg.volt, tg_fast, slow_delay=3, fast_delay=1)
finally:
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
