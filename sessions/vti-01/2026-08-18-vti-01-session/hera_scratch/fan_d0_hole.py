# === Landau fan, hole side, D = 0 (E1 auto, landau-fan-vti) ===
# Per-column SdH-FFT fan. Design in the proposal markdown; floored per the recipe.

# D_offset commit (run 7 locator: symmetric R_CNP minimum, both channels)
D_OFF = -0.009   # V/nm, nominal-D coordinate of true D=0; design lines at D_nom = D_OFF
cal = GateCalibration(c_tg_cal, c_bg_cal, n_offset=-5.934e14, D_offset=+0.009e9)  # SI update

# --- preconditions ---
_B, _T, _amp = magnet.field(), T_sample(), sr1.amplitude()
print(f"preconditions: B={_B:+.3f} T (expect 0.8 hold), T={_T:.3f} K, drive={_amp*1e3:.0f} mV, "
      f"Vsi={dc205.voltage():+.2f}, sens sr1={sr1.sensitivity()}, sr3={sr3.sensitivity()}")
assert abs(_B - 0.8) < 0.05, f"B={_B:+.3f}, expected 0.8 T hold — stop"
assert _T < 1.6 and abs(_amp - 0.100) < 0.005, "T/drive precondition failed — stop"
try:
    _ami = qcodes.Instrument.find_instrument("ami_he")
    print(f"He level: {_ami.He_level():.2f} in")
except Exception as e:
    print(f"He read unavailable: {e!r}")

# fast axis: n-line at true D=0 (design at nominal D = D_OFF)
ns = np.linspace(-0.70, -1.84, 58)                      # 1e12 cm^-2, 0.02 steps
Vtgs, Vbgs = calc_gate_voltages(ns, D_OFF * np.ones_like(ns),
                                c_tg_cal, c_bg_cal, n_offset=n_off_e12)
Vtgs, Vbgs = np.asarray(Vtgs), np.asarray(Vbgs)
assert np.all(np.abs(Vtgs) <= 0.8) and np.all(np.abs(Vbgs) <= 5.0), "n-line exits validators"
print(f"n-line: {ns[0]} .. {ns[-1]} e12 ({len(ns)} pts), Vtg {Vtgs[0]:+.3f}..{Vtgs[-1]:+.3f}, "
      f"Vbg {Vbgs[0]:+.3f}..{Vbgs[-1]:+.3f}")

# slow axis: uniform in 1/B, 1.6 -> 5.0 T, d(1/B) = 0.006 /T (Nyquist x2.8 on 3f_b ~ 53 T)
B_vec = field_invB(1.6, 5.0, 71)
print(f"B rows: {len(B_vec)}, steps {np.diff(B_vec).min()*1e3:.1f}..{np.diff(B_vec).max()*1e3:.1f} mT")

mc = {**meas_config,
      "sample_temperature:": T_sample(),
      "Si (V)": 0.0,
      "comments": ("landau-fan-vti: hole side D=0 (D_offset +0.009 V/nm, run-7 locator), "
                   "n -0.70..-1.84e12 (58 pts) fast paired-gate line x B 1.6->5.0 T "
                   "uniform-1/B (71 rows, d(1/B)=0.006/T), fast_delay 1 s (spot-check "
                   "settling parity), drive 100 mV, sens sr1/sr3 200uV sr2 50uV; "
                   "Rxx normalize by sr0 per point. Reads: per-column FFT vs F_L(n), "
                   "partition sum, tone n-dependence. Pairs with runs 8-9.")}
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0 (true; D_offset +0.009), n = -0.70 to -1.84e12, B = 1.6 to 5.0 T uniform-1/B')

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

# position gates at the line start, field at B_lo (blocking ramp is the settle)
s.ramp(k_tg.volt, Vtgs[0])
s.ramp(k_bg.volt, Vbgs[0])
s.ramp(magnet.field, 1.6)
interruptible_sleep(5)

try:
    s.multimegasweep([magnet.field], [B_vec],
                     [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=1, fast_delay=1)
finally:
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
print(f"fan done; gates parked, B at {magnet.field():+.3f} T (5.0 hold — LK ladder or "
      f"follow-up decided from the per-column read)")
