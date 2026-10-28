# === Si contact-doping survey, hole side: k_si +20 -> -20 V ===
# Electron side (run 4) flat: drain pinned ~88 pA to +20 V. sr0 phase ~172 deg
# (resistive through the inverting Ithaco) => real R_SD ~ 109 MOhm, not pickup.
# Sweep down through 0 to -20 V; overlap 0..+20 doubles as a hysteresis check.

# --- preconditions ---
_B, _T = magnet.field(), T_sample()
_vtg, _vbg, _vsi = k_tg.volt(), k_bg.volt(), dc205.voltage()
print(f"preconditions: B={_B:+.4f} T (~0), T={_T:.3f} K (base), "
      f"Vtg={_vtg:+.4f}, Vbg={_vbg:+.4f} (~0), Vsi={_vsi:+.2f} (expect +20)")
assert abs(_B) < 0.02 and _T < 1.5, "B/T precondition failed — stop"
assert abs(_vtg) < 0.01 and abs(_vbg) < 0.01, "TG/BG not at 0 — stop"
assert abs(_vsi - 20.0) < 0.1, f"Vsi={_vsi:+.2f}, expected +20 (held from run 4) — stop"

mc = {**meas_config,
      "sample_temperature:": T_sample(),
      "Si (V)": dc205.voltage(),
      "comments": ("silicon-backgate-survey, 1D contact-doping flavor, hole side: "
                   "k_si +20 -> -20 V @ 0.5 V/s, TG=BG=0, B~0, drive 10 mV / 10 MOhm. "
                   "Run 4 (0->+20) flat; downsweep overlap is the hysteresis check.")}
s = sweep.AsyncStation(mc)
s.add_comment('silicon-backgate-survey')
s.add_comment('flavor: 1D k_si contact-doping; V_si +20 -> -20 V, TG=BG=0')

s.ramp(k_tg.volt, 0)
s.ramp(k_bg.volt, 0)

xp = dc205.smart_voltage
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
    s.sweep(dc205.smart_voltage, np.linspace(20, -20, 201), delay=1)
finally:
    print(f"V_si held at {dc205.voltage():+.2f} V — operating point decided from the data")
