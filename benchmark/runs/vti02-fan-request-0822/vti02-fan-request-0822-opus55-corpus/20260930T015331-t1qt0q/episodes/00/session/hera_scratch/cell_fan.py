# === Landau fan, electron side, D = 0 (`landau-fan-vti`): n +1.80 -> +3.25e12 (32 pts) x B 1.0 -> 10 T (155 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_N, D0 = 1.80, 3.25, 32, 0.0          # 1e12 cm^-2, V/nm; dn = 0.0468 <= ray-Nyquist floor 0.048 at B_lo = 1.0 T
ns = np.linspace(N_LO, N_HI, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs), np.asarray(Vbgs)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs, Vbgs)
_n_chk, _D_chk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"n-line: {N_N} pts, n {ns[0]:+.3f} -> {ns[-1]:+.3f}e12 (dn {ns[1]-ns[0]:.4f}), D = {D0}; "
      f"Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f}; roundtrip |D|max {np.max(np.abs(_D_chk)):.1e}")

# --- field grid: uniform 1/B at 0.0099 T^-1 (Nyquist 1/3 on F_L(3.25) = 33.6 T) from 1.0 T up to 1.616 T,
#     then geometric at dB/B = 1.6 % (local F_Nyquist = 31*B) to 10 T. The geometric leg follows the run-6
#     harmonic comb, whose highest frequency grows ~23*B (130 T at 5.6 T). A plain field_invB at 0.0099 would
#     fold 81-130 T onto 20-29 T, right on the tones under test.
B_LO, B_HI, DINV_LO, R_STEP = 1.0, 10.0, 0.0099, 0.016
B_X = R_STEP / DINV_LO
_seg1 = 1.0 / np.arange(1 / B_LO, 1 / B_X, -DINV_LO)
_seg2 = np.geomspace(B_X, B_HI, int(np.ceil(np.log(B_HI / B_X) / np.log(1 + R_STEP))) + 1)
B_vec = np.round(np.concatenate([_seg1, _seg2]), 4)
assert np.all(np.diff(B_vec) > 0) and B_vec.min() >= B_LO - 1e-9 and B_vec.max() <= B_SESSION_CAP
print(f"B grid: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T; max d(1/B) {np.max(-np.diff(1 / B_vec)):.4f} 1/T; "
      f"grid = {len(B_vec)} x {N_N} = {len(B_vec) * N_N} pts")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: rig handed back at 0 T), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert abs(_B0) < 0.05, f"magnet not at 0 T: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "a heater is on"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
_f, _a = sr1.frequency(), sr1.amplitude()
assert abs(_f - 13.777) < 0.01 and abs(_a - 1.0) < 1e-6, (_f, _a)
print(f"drive {_a} V @ {_f} Hz -> I_bias 10 nA; tau sr1 {sr1.time_constant()} s / {sr1.filter_slope()} dB, sr0 {sr0.time_constant()} s")
assert sr1.time_constant() == 0.3 and sr0.time_constant() == 0.3, "tau changed since bring-up: re-price fast_delay"

# --- lock-in: fixed for the whole fan (no autorange). 50 uV = 5 kOhm FS at 10 nA, same as spot checks 6/7.
#     Worst corner n = 1.8 x 10 T: R(n=1.8, 0 T) = 77 Ohm (run 5) x ~20 (2x the run-6 MR peak factor 9.5) ~ 1.5 kOhm -> 30 % FS.
sr1.sensitivity(50e-6)
SENS = sr1.sensitivity()
FAST_DELAY, SLOW_DELAY = 2.1, 3.0     # 7 tau at 0.3 s / 24 dB (residual ~8 %); slow_delay covers flyback settle
I_TRIP = 1e-9
print(f"sr1 sens {SENS} V, sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron D=0: n {N_LO:+.2f}..{N_HI:+.2f}e12 ({N_N}), B {B_LO}..{B_HI} T ({len(B_vec)} rows: "
                  f"1/B-uniform {DINV_LO} to {B_X:.3f} T, then dB/B {R_STEP}), sr1 50 uV, fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = {D0} V/nm, n = {N_LO:+.2f} to {N_HI:+.2f}e12 cm^-2 ({N_N} pts), B = {B_LO} to {B_HI} T '
              f'({len(B_vec)} rows; uniform 1/B at {DINV_LO} 1/T to {B_X:.3f} T, geometric dB/B = {R_STEP} above); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'stacking FS-count fan (tetralayer-stacking-fs-count Step 4), follows spot checks runs 6/7')

# gates to the first n-point, then the first slow set ramps 0 -> 1.0 T (blocking, ~7.5 min) inside the sweep
s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_rail_rows = set()
def fan_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    x = abs(float(data[9]))
    if x > 0.9 * SENS and float(data[1]) not in _rail_rows:          # warn once per row; the agent decides at checkpoints
        _rail_rows.add(float(data[1]))
        print(f"RAIL WARN sr1 |X| = {x:.3e} V ({x / SENS:.2f} FS) at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}")
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# field stays at 10 T (the next step, LK ladder / firming fan, starts there and rides down); gates stay on the D = 0 line.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K; "
      f"rail-warned rows: {len(_rail_rows)}")
