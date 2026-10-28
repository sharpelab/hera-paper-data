# Ramp Si +50 -> 0 V. Aaron's procedure: 5 mV step + 0.05 s pacing.
# k_2410.volt.step is CONSENT-GATED — do NOT change it; assert it's fine.
import numpy as np, time
assert k_2410.volt.step <= 0.005 + 1e-9, f"k_2410.volt.step={k_2410.volt.step} coarse (consent-gated) — ABORT, not changing"
k_2410.volt.inter_delay = 0.05   # pacing (inter_delay is not consent-gated)
print("Si start:", k_2410.volt(), "V ; step", k_2410.volt.step, "inter_delay", k_2410.volt.inter_delay)
for v in [40.0, 30.0, 20.0, 10.0, 0.0]:
    k_2410.volt(v)
    time.sleep(1.0); s=[k_2410.curr() for _ in range(5)]; il=float(np.median(s))
    print(f"Si {v:4.0f} V  I_leak(med) {il:.2e} A")
    assert abs(il) < 2e-8, f"Si leak {il:.2e} at {v} V — ABORT"
print("Si at:", k_2410.volt(), "V")
