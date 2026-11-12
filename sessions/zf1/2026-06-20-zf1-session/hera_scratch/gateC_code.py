import numpy as np

# --- preconditions: state this cell assumes but does not set ---
T = temperature()
B = magnet.field()
print(f"precond: probe MC T = {T*1e3:.1f} mK (expect base, <100 mK)")
print(f"precond: magnet field = {B*1e3:.4f} mT (expect ~0; magnet untouched this session)")
print(f"precond: gate setpoints  k_tg={k_tg.volt():+.3f} V  k_bg={k_bg.volt():+.3f} V")
assert T < 0.1, f"T not at base: {T} K"
assert abs(B) < 0.005, f"field unexpectedly finite: {B} T"

# pA-floor leakage readback for the gate-current channels (reset to 1 below)
k_tg.nplci(10)
k_bg.nplci(10)

meas_config["comment"] = (
    "Gate C liveness: k_bg -4 -> +4.2 V leg at k_tg=0, B~0; "
    "confirm 4T Rxx (sr3 30-31) live, current channel passes ~1 nA, "
    "no gate leakage, not a grounded-short"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('gate-current-sanity-check')
s.add_comment('liveness leg: k_bg -4.0 -> +4.2 V, k_tg=0, B~0')

s.ramp(k_tg.volt, 0)
s.ramp(k_bg.volt, -4.0)

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for lia in (sr830_1, sr830_2, sr830_3, sr830_4):
    s.fp(lia.X).fp(lia.P)

xp = k_bg.volt
s.plot(xp, k_tg.curr)
s.plot(xp, k_bg.curr)
for lia in (sr830_1, sr830_2, sr830_3, sr830_4):
    s.plot(xp, lia.X)

try:
    s.sweep(k_bg.volt, np.linspace(-4.0, 4.2, 83), delay=1)
finally:
    s.ramp(k_bg.volt, 0)
    k_tg.nplci(1)
    k_bg.nplci(1)
