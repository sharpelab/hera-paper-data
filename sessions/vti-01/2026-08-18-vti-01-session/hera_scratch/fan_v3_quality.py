# === Quality Landau fan (operator-requested): tau = 300 ms, D = 0 hole side ===
# Goals: firm the ABA call (ML band now per-column resolvable, dF ~ 1.1 T) and a
# publication-clean (n, B) fan. B extends below branch A's onset deliberately —
# the light ML band (~2-2.4 T, m* ~ 0.01 me) lives at low B.

# --- preconditions ---
_B, _T = magnet.field(), T_sample()
print(f"preconditions: B={_B:+.4f} T (~0, close-out endpoint), T={_T:.3f} K (base), "
      f"Vtg={k_tg.volt():+.4f}, Vbg={k_bg.volt():+.4f}, Vsi={dc205.voltage():+.2f}")
assert abs(_B) < 0.02 and _T < 1.5, "B/T precondition failed — stop"
assert abs(k_bg.volt()) < 0.01 and abs(dc205.voltage()) < 0.05, "gates not parked — stop"
try:
    _ami = qcodes.Instrument.find_instrument("ami_he")
    print(f"He level: {_ami.He_level():.2f} in")
except Exception as e:
    print(f"He read unavailable: {e!r}")

# --- campaign config (state0 was restored at close-out; re-establish + tau bump) ---
sr1.amplitude(0.100)                       # 100 mV drive (ohmic-verified; contact-limited ~1 nA)
sr0.sensitivity(0.01)
sr1.sensitivity(200e-6); sr3.sensitivity(200e-6); sr2.sensitivity(50e-6)
for _l in (sr0, sr1, sr2, sr3):
    _l.time_constant(0.3)                  # operator-requested tau = 300 ms
print(f"config: drive {sr1.amplitude()*1e3:.0f} mV @ {sr1.frequency():.3f} Hz; "
      f"taus {[l.time_constant() for l in (sr0, sr1, sr2, sr3)]}; "
      f"sens sr0 {sr0.sensitivity()}, sr1/3 200 uV, sr2 50 uV; dwell 2.5 s = 8.3 tau")

# fast axis: same D=0 n-line as run 10 (comparability)
ns = np.linspace(-0.70, -1.74, 53)
Vtgs, Vbgs = calc_gate_voltages(ns, -0.009 * np.ones_like(ns),
                                c_tg_cal, c_bg_cal, n_offset=n_off_e12)
Vtgs, Vbgs = np.asarray(Vtgs), np.asarray(Vbgs)
assert np.all(np.abs(Vtgs) <= 0.8) and np.all(np.abs(Vbgs) <= 5.0), "n-line exits validators"

# slow axis: uniform-1/B, 0.9 -> 5.0 T, d(1/B) = 0.007 /T (131 rows)
B_vec = field_invB(0.9, 5.0, 131)
print(f"B rows: {len(B_vec)}, steps {np.diff(B_vec).min()*1e3:.1f}..{np.diff(B_vec).max()*1e3:.1f} mT; "
      f"n-line {ns[0]}..{ns[-1]} e12 ({len(ns)} pts)")

mc = {**meas_config,
      "sample_temperature:": T_sample(),
      "Si (V)": 0.0,
      "comments": ("landau-fan-vti QUALITY (operator-requested, tau=300ms): hole side "
                   "D=0 true (D_offset +0.009), n -0.70..-1.74e12 (53 pts) x B 0.9->5.0 T "
                   "uniform-1/B (131 rows, d(1/B)=0.007/T), fast_delay 2.5 s (8.3 tau), "
                   "drive 100 mV, sens sr1/sr3 200uV sr2 50uV, all taus 0.3 s. "
                   "B_lo below branch-A onset deliberately: ML band target. "
                   "Firms runs 10/12-18 ABA call; artifact-grade map.")}
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('quality fan tau=300ms: D = 0 true, n = -0.70 to -1.74e12, B = 0.9 to 5.0 T uniform-1/B')

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

s.ramp(k_tg.volt, Vtgs[0])
s.ramp(k_bg.volt, Vbgs[0])
s.ramp(magnet.field, 0.9)
interruptible_sleep(10)

try:
    s.multimegasweep([magnet.field], [B_vec],
                     [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=1, fast_delay=2.5)
finally:
    pass  # gates stay on the line; the descent spot check follows at n = -1.74
print(f"quality fan done; B at {magnet.field():+.2f} T — descent ML spot check next")
