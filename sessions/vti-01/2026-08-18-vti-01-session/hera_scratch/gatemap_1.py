# === First 0 T gatemap: TG fast (±0.8 V, 10 mV) × BG slow (±2.5 V, 0.1 V) ===
# Feeds cnp-and-dline-calibration (CNP-line fit -> c_bg/c_tg) and the
# investigation's step 1 (D=0 line, clean regions, contact-arm check).

# --- preconditions ---
_B, _T = magnet.field(), T_sample()
_amp = sr1.amplitude()
print(f"preconditions: B={_B:+.4f} T (~0), T={_T:.3f} K (base), "
      f"Vtg={k_tg.volt():+.4f}, Vbg={k_bg.volt():+.4f}, Vsi={dc205.voltage():+.2f} (all ~0), "
      f"drive={_amp*1e3:.0f} mV (expect 100)")
assert abs(_B) < 0.02 and _T < 1.5, "B/T precondition failed — stop"
assert abs(dc205.voltage()) < 0.05, "Si not at 0 — stop"
assert abs(_amp - 0.100) < 0.005, "drive not 100 mV — stop"

mc = {**meas_config,
      "sample_temperature:": T_sample(),
      "Si (V)": 0.0,
      "comments": ("gatemap: V_tg -0.8..+0.8 (161 pts, fast) x V_bg -2.5..+2.5 "
                   "(51 rows, slow), Vsi=0, B~0, T=1.18 K, drive 100 mV / 10 MOhm "
                   "nominal (T_SD contact ~109 MOhm dominates: I ~ 1 nA, normalize "
                   "Rxx by sr0 current per point). Sens sr0 10 mV, sr1/2/3 1 mV; "
                   "tau 0.1 s; TG leak (~0.5 nA at endpoints) operator-accepted.")}
s = sweep.AsyncStation(mc)
s.add_comment('gatemap')
s.add_comment('first map, Vsi = 0V; feeds cnp-and-dline-calibration')

s.ramp(k_bg.volt, -2.5)
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
    s.megasweep(k_bg.volt, np.linspace(-2.5, 2.5, 51),
                k_tg.volt, np.linspace(-0.8, 0.8, 161),
                slow_delay=3, fast_delay=1)
finally:
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
print("gatemap done; gates parked at 0")
