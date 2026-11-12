import numpy as np

# --- preconditions: state this cell assumes but does not set ---
T = temperature()
B = magnet.field()
print(f"precond: probe MC T = {T*1e3:.1f} mK (expect base, <100 mK)")
print(f"precond: magnet field = {B*1e3:.4f} mT (expect ~0; magnet untouched)")
print(f"precond: gate setpoints  k_tg={k_tg.volt():+.3f} V  k_bg={k_bg.volt():+.3f} V")
assert T < 0.1, f"T not at base: {T} K"
assert abs(B) < 0.005, f"field unexpectedly finite: {B} T"

# --- drive bump: 40 pA -> 0.5 nA for low-Rxx SNR (card nominal 1 nA; 0.5 nA = SC-friendly) ---
sr830_1.amplitude(0.05)
meas_config["bias_voltage_1"] = sr830_1.amplitude()
print(f"AC drive: sr830_1.amplitude = {sr830_1.amplitude()*1e3:.0f} mV -> "
      f"I_bias = {meas_config['bias_voltage_1']/meas_config['bias_resistor']*1e9:.3f} nA")

# pA-floor leakage readback on gate-current channels (reset to 1 below)
k_tg.nplci(10)
k_bg.nplci(10)

meas_config["comment"] = (
    "TG leakage/SNR leg: k_tg 0 -> -7 V at k_bg=0, B~0, drive 0.5 nA; "
    "confirm -7 V TG validator safe this cooldown + validate low-Rxx SNR floor"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('gate-current-sanity-check')
s.add_comment('TG leg: k_tg 0 -> -7.0 V, k_bg=0, B~0, drive 0.5 nA')

s.ramp(k_bg.volt, 0)
s.ramp(k_tg.volt, 0)

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for lia in (sr830_1, sr830_2, sr830_3, sr830_4):
    s.fp(lia.X).fp(lia.P)

xp = k_tg.volt
s.plot(xp, k_tg.curr)
s.plot(xp, k_bg.curr)
for lia in (sr830_1, sr830_2, sr830_3, sr830_4):
    s.plot(xp, lia.X)

try:
    s.sweep(k_tg.volt, np.linspace(0, -7.0, 71), delay=1)
finally:
    s.ramp(k_tg.volt, 0)
    k_tg.nplci(1)
    k_bg.nplci(1)
