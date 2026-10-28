# === Descent ML spot check, tau = 300 ms: n = -1.74, D = 0(true), B 5 -> 0.5 T ===
# The campaign's sharpest ML-band record: dF = 1/(1/0.5 - 1/5) = 0.56 T,
# x1.7 SNR over run 11, 4 mT uniform-B. Rides the magnet home from the fan.
# Then B parks at 0 (operator: "use the way down ... or simply cooldown").

# --- preconditions ---
_B, _T = magnet.field(), T_sample()
print(f"preconditions: B={_B:+.3f} T (expect ~5, fan end), T={_T:.3f} K, "
      f"drive={sr1.amplitude()*1e3:.0f} mV, taus={[l.time_constant() for l in (sr0,sr1,sr2,sr3)]}")
assert abs(_B - 5.0) < 0.05, f"B={_B:+.3f}, expected 5 T — stop"
assert _T < 1.5, "not at base — stop"
assert abs(sr1.amplitude() - 0.100) < 0.005 and abs(sr1.time_constant() - 0.3) < 0.01

n_t = -1.74
Vtg_t, Vbg_t = calc_gate_voltages(n_t, -0.009, c_tg_cal, c_bg_cal, n_offset=n_off_e12)
k_tg.volt(Vtg_t); k_bg.volt(Vbg_t)   # fan's line end is n=-1.74 — re-assert
print(f"point: n={n_t}e12 true D=0 -> Vtg={Vtg_t:+.4f}, Vbg={Vbg_t:+.4f}")

B_vec = np.linspace(5.0, 0.5, 1126)   # dB = 4 mT descending
mc = {**meas_config,
      "sample_temperature:": T_sample(),
      "Si (V)": 0.0,
      "comments": (f"sdh-spot-check ML descent, tau=300ms: n={n_t}e12 true D=0 "
                   f"(Vtg={Vtg_t:+.4f}, Vbg={Vbg_t:+.4f}), B 5.0->0.5 T uniform-B "
                   f"dB=4 mT (1126 pts), dwell 2.5 s = 8.3 tau, drive 100 mV, "
                   f"sens sr1/sr3 200uV sr2 50uV. dF=0.56 T; definitive ML-band "
                   f"record; pairs with runs 8/11/19.")}
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'ML descent tau=300ms: n = {n_t}e12, D = 0 true, B 5.0 -> 0.5 T @ 4 mT')

xp = magnet.field
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
    s.sweep(magnet.field, B_vec, delay=2.5)
finally:
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
magnet.field(0.0)
print(f"descent done; gates parked, B ramped to {magnet.field():+.3f} T (cooldown endpoint)")
