# === Landau fan, electron side, D = 0 (`landau-fan-vti`): n = +0.8 -> +3.2e12 (61 cols) x B 1.0 -> 10 T uniform-1/B (151 rows) ===
# Investigation Step 4 (tetralayer-stacking-fs-count): per-column SdH FFT -> F(n) vs the Luttinger line, harmonic
# screen by n-dependence, ABAB-pair / ABCA-singleton / breakdown-sum discrimination. Design from spot checks 6 (e) / 7 (h).
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0                                             # V/nm, the operating point
n_lo, n_hi, N_n = 0.8, 3.2, 61                       # 1e12 cm^-2; dn = 0.04e12 -> 2.4 pts per LL ray at B_lo = 1.0 T (>= 2 floor), 3.4 at 1.4 T
ns = np.linspace(n_lo, n_hi, N_n); Ds = D0 * np.ones(N_n)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
print(f"fast axis: n = {n_lo:+.2f} -> {n_hi:+.2f}e12 at D = {D0:+.2f} V/nm, {N_n} pts; Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V "
      f"(limits TG [{TG_MIN},{TG_MAX}], BG [{BG_MIN},{BG_MAX}]); roundtrip end = {calc_nD(Vtgs[-1], Vbgs[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- slow axis: uniform in 1/B (per-column SdH-FFT fan). d(1/B) = 0.006 /T -> f_s = 167 T, alias-free to 83 T = 2.5 x F_L(3.2e12) = 33.1 T.
B_lo, B_hi, N_B = 1.0, 10.0, 151
B_vec = field_invB(B_lo, B_hi, N_B)                  # ascending: the magnet sits at 0 T, positions to 1.0 T, ends at 10 T
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
d_invB = np.abs(np.diff(1 / B_vec)); print(f"slow axis: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows, d(1/B) = {d_invB.mean():.4f} +/- {d_invB.std():.1e} /T; dB {np.diff(B_vec).min()*1e3:.1f} mT (low B) .. {np.diff(B_vec).max()*1e3:.0f} mT (high B)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: handoff left it at 0), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, T_vaporizer = {T_vaporizer():.3f} K")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- lock-in: fixed for the whole fan. Worst corner is low n x high B: CNP anchor 240 Ohm (run 5, D = 0) x low-n MR factor
# ~10-20 (runs 6/7) ~ 2.5-5 kOhm -> 100 uV = 10 kOhm FS at 10 nA (2x headroom; run 6 at 50 uV peaked at 0.11 FS, n = 3.2).
FAST_DELAY, SLOW_DELAY = 1.8, 3.0                    # 6 tau at tau = 0.3 s / 24 dB (per-column-FFT fan); 10 tau after each row's gate flyback
I_TRIP = 1e-9
sr1.sensitivity(100e-6)
assert abs(sr1.time_constant() - 0.3) < 1e-6, sr1.time_constant()
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V; "
      f"drive {sr1.amplitude()} V @ {sr1.frequency()} Hz; magnet settle_s {magnet.settle_s} s; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side D = {D0:+.2f} V/nm (run-5 cal): n = {n_lo:+.2f} -> {n_hi:+.2f}e12 ({N_n} pts, paired Vtg/Vbg line), "
                  f"B {B_lo} -> {B_hi} T uniform-1/B ({N_B} rows, d(1/B) 0.006), fast_delay {FAST_DELAY}, slow_delay {SLOW_DELAY}, sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {n_lo:+.2f} to {n_hi:+.2f}e12 cm^-2 ({N_n} pts, electron side), B = {B_lo} to {B_hi} T uniform-1/B ({N_B} rows); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; design from spot checks 6/7')

# position: gates to the first fast point, then the magnet to B_lo (blocking ramp, ~7 min from 0 T)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
print(f"positioning magnet 0 -> {B_lo} T (blocking) ...", flush=True)
magnet.field(B_lo)
print(f"at B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}); T_sample = {T_sample():.3f} K", flush=True)
interruptible_sleep(5)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY, init_delay=True)
# field ends at 10 T (deliberate: the next step rides it down); gates parked at 0 so the device idles at the CNP-side of nothing in particular.
k_tg.volt(0.0); k_bg.volt(0.0)
print(f"done: B = {magnet.field():+.3f} T (left at B_hi), gates parked (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}); T_sample = {T_sample():.3f} K")
