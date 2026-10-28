# Re-energize Si to +50 V: coarse step (GPIB-safe) + settle + median read.
# The -64 nA earlier was SiO2 gate charging current (coarse-step dV/dt), not
# leakage; settle before reading and reject spikes with a median.
import numpy as np, time
k_2410.visa_handle.timeout = 10000
k_2410.volt.step = 1.0; k_2410.volt.inter_delay = 0.05
print("range:", k_2410.rangev(), "V ; start Si:", k_2410.volt(), "V")
for v in range(5, 51, 5):
    k_2410.volt(float(v))
    time.sleep(1.0)                       # let SiO2 charging current decay
    s = [k_2410.curr() for _ in range(5)]
    il = float(np.median(s))
    print(f"Si {v:3d} V  I_leak(med) = {il:.2e} A  [{min(s):.1e}..{max(s):.1e}]")
    assert abs(il) < 2e-8, f"Si settled leak {il:.2e} at {v} V — ABORT"  # 20 nA > ~2 nA noise
time.sleep(2.0)
print("Si energized:", k_2410.volt(), "V ; leak(med)", float(np.median([k_2410.curr() for _ in range(5)])), "A")
