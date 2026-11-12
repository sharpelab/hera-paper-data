# === Fan step B — Landau fan, electron side, D = 0 (`landau-fan-vti`): n 3.2 -> 1.6e12 (35 pts) x B 1.0 -> 10.0 T uniform in 1/B (102 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run 5 (cnp-and-dline-calibration)
# --- slow axis: shared 1/B lattice with step A, k = 101..0 -> B 1.0 -> 10.0 T ascending (starts where step A left the magnet, ends at 10 T)
DINVB = 0.9 / 101
B_vec = 1.0 / (0.1 + np.arange(101, -1, -1) * DINVB)
assert len(B_vec) == 102 and abs(B_vec[0] - 1.0) < 1e-9 and abs(B_vec[-1] - 10.0) < 1e-9 and np.all(np.diff(B_vec) > 0)
assert np.abs(B_vec).max() <= B_SESSION_CAP
# --- fast axis: paired (Vtg, Vbg) n-line at D = 0; dn = 0.0471e12 <= 0.048e12 = half the LL period (4e/h)*B at B_lo = 1 T
ns = np.linspace(3.2, 1.6, 35); Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
_vt, _vb = sanitize_tg_bg(Vtgs, Vbgs, tg_lims, bg_lims)
assert len(_vt) == len(ns), "n-line leaves the validator box"
n_chk, D_chk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(n_chk, ns, atol=1e-6) and np.allclose(D_chk, 0, atol=1e-6)
print(f"n-line: {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({len(ns)} pts, dn {ns[0]-ns[1]:.4f}), D = 0: Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V")
print(f"B: {B_vec[0]:.4f} -> {B_vec[-1]:.4f} T, {len(B_vec)} rows uniform in 1/B (DINVB {DINVB:.6f} 1/T, Nyquist {1/(2*DINVB):.1f} T)")
# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0, _Vsi = T_sample(), magnet.field(), k_si()
_hs, _hv = heater.sample_range(), heater.vaporizer_range()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (step A left ~0.991 T; accept 0.25-1.05), V_si = {_Vsi:+.3f} V (0), "
      f"heater ranges {_hs}/{_hv} (0/0), PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and 0.25 <= _B0 <= 1.05 and abs(_Vsi) < 0.01 and _hs == 0 and _hv == 0
assert magnet.persistent_switch_on() and magnet.output_enabled() and k_tg.nplci() == 1 and k_bg.nplci() == 1
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24 and sr0.time_constant() == 0.3 and abs(sr1.amplitude() - 1.0) < 1e-6
# Fixed sensitivity for the whole fan (no autorange): 100 uV = 10 kOhm FS at 10 nA. Worst corner n = 1.6e12 x 10 T:
# R0(1.6) = 84 Ohm (run 5) x low-n MR/QH factor ~15-25 -> ~1.3-2.1 kOhm = 13-21 % FS (run 6: 522 Ohm at 3.2e12, 10 T).
sr1.sensitivity(100e-6)
FAST_DELAY, SLOW_DELAY = 1.8, 3.0      # 6 tau at 0.3 s / 24 dB (per-column SdH fan); 10 tau after each row's flyback
I_TRIP, T_TRIP = 1e-9, 1.7
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS), sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, magnet settle_s {magnet.settle_s} s")
mc = dict(meas_config); mc["Si (V)"] = _Vsi; mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side D = 0 (run-5 cal): n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({len(ns)} pts) x B 1.0 -> 10.0 T uniform 1/B "
                  f"({len(B_vec)} rows, DINVB 0.9/101), fast_delay {FAST_DELAY}, sr1 100 uV; stacking FS count (tetralayer-stacking-fs-count step 4)")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0 V/nm, n = {ns[-1]:+.2f} to {ns[0]:+.2f}e12 cm^-2 ({len(ns)} pts, fast, high->low), B = 1.0 to 10.0 T ({len(B_vec)} rows uniform in 1/B, '
              f'DINVB = {DINVB:.6f} 1/T, shared lattice with step A); cal run 5: c_tg 2.796e-3, c_bg 2.161e-3 F/m2, n_offset -0.089e12, D_offset -0.013; '
              f'per-column SdH FFT fan for investigations/tetralayer-stacking-fs-count')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(5)
# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', T_sample); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
def guard(station, data):
    T, i_tg, i_bg = float(data[4]), abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.4f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if T > T_TRIP:
        print(f"T TRIP at B={float(data[1]):+.4f} T: T_sample = {T:.3f} K > {T_TRIP} K"); station.interrupt_requested = True
s.register_run_after(guard, ())
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field is left where the fan ended (10 T on completion): the next step (LK mass split / firming) rides it down — never re-traverse.
    print(f"end: B = {magnet.field():+.4f} T, gates parked ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T = {T_sample():.3f} K")
