# === Landau fan at D = 0 (`landau-fan`): B slow 1.0 -> 10 T x n fast -1.25 -> +3.25e12, co-swept (Vtg, Vbg) along the calibrated D = 0 line ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run-5 cnp-and-dline-calibration (ana)
# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: parked at 0 after the handoff), V_si = {k_si():+.3f} V (0), "
      f"V_tg = {k_tg.volt():+.3f}, V_bg = {k_bg.volt():+.3f} V (0, 0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "a heater range is on"
# --- fast axis: n along the calibrated D = 0 line, inside the validators on both ends (TG-limited window is -1.28 .. +3.26e12)
N_FAST = 141
n_vec = np.linspace(-1.25, 3.25, N_FAST)                       # 1e12 cm^-2, dn = 0.032e12
Vtgs, Vbgs = calc_gate_voltages(n_vec, np.zeros(N_FAST), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
_nchk, _Dchk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_nchk, n_vec) and np.abs(_Dchk).max() < 1e-6, "D = 0 line round-trip failed"
# --- slow axis: uniform-B rows ascending from the parked magnet: 50 mT to 3 T (onset / light-tone region), 100 mT above
B_vec = np.unique(np.round(np.hstack((np.arange(1.0, 3.0, 0.05), np.arange(3.0, 10.0001, 0.1))), 4))
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9
sr1.sensitivity(100e-6)   # 10 kOhm FS at 10 nA: headroom for the D = 0 CNP ridge at high B; runs 6/7 peaked at 590 Ohm (<= 6 % FS)
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 ({N_FAST} pts, dn {n_vec[1]-n_vec[0]:.4f}e12), Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V")
print(f"slow: B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows ({np.sum(B_vec < 3.0)} at 50 mT, {np.sum(B_vec >= 3.0)} at 100 mT); "
      f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB; drive {sr1.amplitude()} V -> 10 nA; sr0 sens {sr0.sensitivity()} V")
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: B slow {B_vec[0]} -> {B_vec[-1]} T ({len(B_vec)} rows), n fast {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 ({N_FAST}) "
                  f"co-swept Vtg/Vbg on the run-5 D = 0 line, fast_delay {FAST_DELAY} s, sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e} F/m2, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm); '
              f'slow B {B_vec[0]} -> {B_vec[-1]} T, 0.05 T to 3 T then 0.1 T ({len(B_vec)} rows); '
              f'fast n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 ({N_FAST} pts, dn {n_vec[1]-n_vec[0]:.4f}e12) = (Vtg, Vbg) ({Vtgs[0]:+.4f}, {Vbgs[0]:+.4f}) -> ({Vtgs[-1]:+.4f}, {Vbgs[-1]:+.4f}); '
              f'fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; Vsi = 0; sr1 100 uV (10 kOhm FS); T_sample {_T0:.3f} K at start')
# gates to the first fast point before the field moves, so the first row starts settled
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(5)
# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B = {float(data[1]):+.3f} T, Vtg = {float(data[2]):+.3f}, Vbg = {float(data[3]):+.3f}: |I_tg| = {i_tg:.3e}, |I_bg| = {i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates back to 0 (cheap); the field stays where the sweep left it (10 T if complete) — the next step rides it down, never re-traverses
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
