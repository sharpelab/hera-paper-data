# === Si contact-doping survey: k_si 0 -> +20 V (operator-allowlisted 2026-08-19) ===
# Goal: recover the contacts (R_SD ~ 109 MOhm at Vsi=0). Graphite BG screens the
# channel, so Si gates the contact/lead regions only (device card). Watch drain
# current (sr0) come alive; endpoint HELD at +20 V until the operating point is
# picked from the data (no blind re-traverse of the SiO2).

# --- preconditions ---
_B, _T = magnet.field(), T_sample()
_vtg, _vbg, _vsi = k_tg.volt(), k_bg.volt(), dc205.voltage()
print(f"preconditions: B={_B:+.4f} T (~0), T={_T:.3f} K (base), "
      f"Vtg={_vtg:+.4f}, Vbg={_vbg:+.4f}, Vsi={_vsi:+.4f} (all ~0)")
assert abs(_B) < 0.02 and _T < 1.5, "B/T precondition failed — stop"
assert abs(_vtg) < 0.01 and abs(_vbg) < 0.01 and abs(_vsi) < 0.01, "gates not at 0 — stop"

mc = {**meas_config,
      "sample_temperature:": T_sample(),
      "Si (V)": dc205.voltage(),
      "comments": ("silicon-backgate-survey, 1D contact-doping flavor: k_si 0 -> +20 V "
                   "@ 0.5 V/s, TG=BG=0, B~0, drive 10 mV / 10 MOhm ~ 1 nA. Si gates "
                   "contacts only (graphite BG screens channel). Operator allowlisted "
                   "Si to card limits 2026-08-19.")}
s = sweep.AsyncStation(mc)
s.add_comment('silicon-backgate-survey')
s.add_comment('flavor: 1D k_si contact-doping; V_si 0 -> +20 V, TG=BG=0')

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
    s.sweep(dc205.smart_voltage, np.linspace(0, 20, 101), delay=1)
finally:
    print(f"V_si held at {dc205.voltage():+.2f} V — operating point decided from the data")
