# === Step-1 reconnaissance: 3-row gatemap (TG slow {-3,0,+3}, BG fast) ===
# De-risks the full survey: CNP magnitude (-> map sensitivity), CNP-vs-TG slope
# (cap-ratio preview), per-point timing (-> map pricing), leakage/clipping check.
# Still pre-field (magnet pristine), per Step 1.

# --- precondition reads (state this cell assumes but does not set) ---
_T = temperature(); _B = magnet.field()
print(f"probe MC T = {_T*1e3:.1f} mK   (expect base)")
print(f"magnet B   = {_B*1e3:+.3f} mT  (expect ~0 — still pristine)")
print(f"k_tg.volt  = {k_tg.volt():+.4f} V   k_bg.volt = {k_bg.volt():+.4f} V")
assert _T < 0.060, f"T={_T*1e3:.1f} mK not at base"
assert abs(_B) < 0.005, f"|B|={_B*1e3:.2f} mT not ~0 (magnet should be pristine)"

# AC drive -> 1 nA; refresh meas_config so THIS run's metadata is correct.
sr830_1.amplitude(0.1)
meas_config["bias_voltage_1"] = sr830_1.amplitude()
meas_config["lockin_freq_1"]  = sr830_1.frequency()
meas_config["comment"] = "recon 3-row gatemap: TG{-3,0,+3}, BG -4..+4.2, 1nA, B=0"

# Print live lock-in settings (snapshot didn't capture them), then set voltage
# channels GENEROUS so the CNP peak can't clip during reconnaissance.
for lia in (sr830_1, sr830_2, sr830_3):
    print(f"{lia.name}: tc={lia.time_constant()} s  sens={lia.sensitivity()} V")
sr830_2.sensitivity(0.5)
sr830_3.sensitivity(0.5)
print("set sr830_2/3 sensitivity -> 0.5 V (recon, no-clip)")

s = sweep.AsyncStation(meas_config)
s.add_comment('gatemap')
s.add_comment('branch: Step-1 reconnaissance (3-row, de-risk full survey)')
s.add_comment('TG slow {-3,0,+3} V; BG fast -4 -> +4.2 V (83); B=0')

s.ramp(k_tg.volt, -3.0)
s.ramp(k_bg.volt, -4.0)

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for lia in (sr830_1, sr830_2, sr830_3):
    s.fp(lia.X).fp(lia.P)

s.plot(k_bg.volt, sr830_3.X)   # 4T Rxx (30-31)
s.plot(k_bg.volt, sr830_2.X)   # 2T (5-4)
s.plot('time', k_tg.curr)      # live leakage
s.plot('time', k_bg.curr)

try:
    s.megasweep(k_tg.volt, np.array([-3.0, 0.0, 3.0]),
                k_bg.volt, np.linspace(-4.0, 4.2, 83),
                slow_delay=2, fast_delay=0.5)
finally:
    s.ramp(k_bg.volt, 0.0)
    s.ramp(k_tg.volt, 0.0)
