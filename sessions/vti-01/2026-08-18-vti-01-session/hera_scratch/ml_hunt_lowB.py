# === ML-pocket hunt: low-B spot check, n = -1.74, D = 0(true), B 2.5 -> 0.5 T ===
# The ABA-vs-ABC residual: ABA predicts a light ML pocket (model F ~ 2.3 T at
# this n, m* ~ 0.01 me — thermal damping negligible at T_e ~ 8 K even sub-tesla).
# Window 0.5-2.5 T holds ~3.8 periods of a 2.4 T tone; dF ~ 0.6 T. Absence here
# is informative (searched, resolvable, not found), unlike runs 8/10.

# --- preconditions ---
_B, _T, _amp = magnet.field(), T_sample(), sr1.amplitude()
print(f"preconditions: B={_B:+.3f} T (expect ~5 hold), T={_T:.3f} K, drive={_amp*1e3:.0f} mV, "
      f"Vsi={dc205.voltage():+.2f}, Vtg={k_tg.volt():+.4f}, Vbg={k_bg.volt():+.4f}")
assert abs(_B - 5.0) < 0.05, f"B={_B:+.3f}, expected 5 T hold — stop"
assert _T < 1.6 and abs(_amp - 0.100) < 0.005, "T/drive precondition failed — stop"

n_t, D_t = -1.74, -0.009   # nominal-D design coordinate of true D=0
Vtg_t, Vbg_t = calc_gate_voltages(n_t, D_t, c_tg_cal, c_bg_cal, n_offset=n_off_e12)
print(f"target: n={n_t}e12 at true D=0 -> Vtg={Vtg_t:+.4f}, Vbg={Vbg_t:+.4f}")
assert abs(Vtg_t) <= 0.8 and abs(Vbg_t) <= 5.0

B_vec = np.linspace(2.5, 0.5, 401)   # dB = 5 mT: Nyquist/3 on branch A (16 T) at B_lo 0.5
mc = {**meas_config,
      "sample_temperature:": T_sample(),
      "Si (V)": 0.0,
      "comments": (f"sdh-spot-check ML hunt: n={n_t}e12, true D=0 "
                   f"(Vtg={Vtg_t:+.4f}, Vbg={Vbg_t:+.4f}), B 2.5->0.5 T dB=5 mT, "
                   f"delay 1 s, drive 100 mV. Target: ABA ML pocket ~2.4 T "
                   f"(3.8 periods in window, dF~0.6 T); extends runs 8/10 record "
                   f"at this density down to 0.5 T.")}
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'ML hunt, low-B: n = {n_t}e12, D = 0 true, B 2.5 -> 0.5 T')

s.ramp(k_tg.volt, Vtg_t)
s.ramp(k_bg.volt, Vbg_t)
s.ramp(magnet.field, 2.5)     # bare blocking ramp 5 -> 2.5 (~18 min)
interruptible_sleep(5)

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
    s.sweep(magnet.field, B_vec, delay=1)
finally:
    print(f"ML hunt done; B at {magnet.field():+.3f} T, gates at n={n_t} — "
          f"LK ladder repositions to its own window next")
