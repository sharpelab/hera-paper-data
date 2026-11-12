# === CNP scoping cut: 1D TG sweep at Vbg=0, 100 mV drive (E1 auto) ===
# Purpose: see the CNP cross-section + calibrate sensitivities before pricing
# the first gatemap. Per-point current normalization downstream: Rxx = sr_X /
# (sr0_X / sr0_gain) — the T_SD contact (~109 MOhm) sets the current, not the
# 10 MOhm bias resistor, so nominal I_bias is wrong; sr0 is the truth.

# --- preconditions ---
_B, _T = magnet.field(), T_sample()
print(f"preconditions: B={_B:+.4f} T (~0), T={_T:.3f} K (base), "
      f"Vtg={k_tg.volt():+.4f}, Vbg={k_bg.volt():+.4f} (~0), Vsi={dc205.voltage():+.2f} (-20, ramping to 0)")
assert abs(_B) < 0.02 and _T < 1.5, "B/T precondition failed — stop"
assert abs(k_bg.volt()) < 0.01, "BG not at 0 — stop"

# Si is inert on this device (runs 4-5): park at 0 (from held -20; ~40 s at 0.5 V/s)
dc205.smart_voltage(0.0)

# measurement config for the campaign's contact reality:
sr1.amplitude(0.100)       # 100 mV drive — ohmic-verified to here (discriminator cell)
sr0.sensitivity(0.01)      # 10 mV fs = 10 nA absolute ceiling (100 mV / 10 MOhm) — can never clip
sr0.time_constant(0.1)     # 0.3 -> 0.1 s; dwell 1 s = 10 tau (state0 holds the original)
sr1.sensitivity(0.001)     # Rxx channels: 1 mV fs; near-CNP rows may rail — the
sr2.sensitivity(0.001)     # cnp recipe's railed-row guard handles that; metallic-
sr3.sensitivity(0.001)     # region resolution is what matters for the ridge fit
print("drive 100 mV @ 13.777 Hz; sens sr0=10mV sr1/2/3=1mV; tau sr0=0.1s")

mc = {**meas_config,
      "sample_temperature:": T_sample(),
      "Si (V)": 0.0,
      "comments": ("cnp-and-dline-calibration scoping: 1D TG cut -0.8 -> +0.8 V at "
                   "Vbg=0, Vsi=0, B~0, drive 100 mV / 10 MOhm nominal (T_SD contact "
                   "~109 MOhm dominates; normalize by sr0 current per point). "
                   "Sens: sr0 10 mV, sr1/2/3 1 mV; tau sr0 0.1 s.")}
s = sweep.AsyncStation(mc)
s.add_comment('cnp-and-dline-calibration')
s.add_comment('scoping: 1D TG cut at Vbg=0; CNP visibility + sensitivity calibration')

s.ramp(k_bg.volt, 0)
s.ramp(k_tg.volt, -0.8)
interruptible_sleep(5)

xp = k_tg.volt
s.fp(k_tg.curr).fp(k_bg.curr)
s.fp(T_sample)
s.plot(xp, k_tg.curr)
s.plot(xp, k_bg.curr)
s.plot(xp, T_sample)
for lia in [sr0, sr1, sr2, sr3]:
    s.fp(lia.X).fp(lia.P)
    s.plot(xp, lia.X)
    s.plot(xp, lia.P)

try:
    s.sweep(k_tg.volt, np.linspace(-0.8, 0.8, 321), delay=1)
finally:
    s.ramp(k_tg.volt, 0)
print("cut done; TG parked at 0")
