# Cell 1 — ramp Si 0 -> +50 V (Aaron's procedure: 5 mV step CONSENT-GATED + 0.05 pacing)
import numpy as np, time
assert k_2410.volt.step <= 0.005+1e-9, f"k_2410.volt.step coarse (consent-gated): {k_2410.volt.step}"
k_2410.volt.inter_delay = 0.05
print("Si start", k_2410.volt(), "V; step", k_2410.volt.step)
for v in range(5,51,5):
    k_2410.volt(float(v)); time.sleep(1.0)
    il=float(np.median([k_2410.curr() for _ in range(5)]))
    print(f"Si {v:3d} V  leak(med) {il:.2e} A"); assert abs(il)<2e-8, f"Si leak {il:.2e} at {v} V"
print("Si energized:", k_2410.volt(), "V")
