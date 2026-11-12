# === Landau fan (`landau-fan-vti`) for `tetralayer-stacking-fs-count` Step 4: electron side, D = 0 ===
# n = +3.20 -> +2.00e12 (31 pts) x B = 0.85 -> 6.0 T uniform in 1/B (136 rows, d(1/B) = 0.0075 1/T); ends at 6 T.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_HI, N_LO, N_N, D0 = 3.20, 2.00, 31, 0.0          # 1e12 cm^-2, V/nm
B_LO, B_HI, N_B = 0.85, 6.0, 136                    # T; uniform in 1/B
FAST_DELAY, SLOW_DELAY = 1.8, 3.0                   # 6 tau fast (tau 0.3 s / 24 dB); flyback settle 10 tau
I_TRIP = 1e-9

ns = np.linspace(N_HI, N_LO, N_N); Ds = D0 * np.ones(N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
B_vec = field_invB(B_LO, B_HI, N_B)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs, Vbgs)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
_nr, _Dr = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast: n {ns[0]:+.3f} -> {ns[-1]:+.3f}e12 ({N_N} pts, step {ns[0]-ns[1]:.4f}); roundtrip max|D| {np.abs(_Dr).max():.1e}; "
      f"Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f}")
print(f"slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows, d(1/B) {abs(np.diff(1/B_vec)).mean():.5f} 1/T, "
      f"dB {B_vec[1]-B_vec[0]:.4f} .. {B_vec[-1]-B_vec[-2]:.3f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _Tv, _B0 = T_sample(), T_vaporizer(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {_Tv:.3f} K (< 1.5, tracking base), heater ranges "
      f"{heater.sample_range()}/{heater.vaporizer_range()} (0/0), B = {_B0:+.4f} T (|B| < 0.05; fan ramps to {B_LO} T), "
      f"V_si = {k_si():+.3f} V (0), PS {magnet.persistent_switch_on()} / output {magnet.output_enabled()} (True/True)")
print(f"precondition drive {sr1.amplitude()} V (1.0 -> 10 nA), sr1 tau {sr1.time_constant()} s / {sr1.filter_slope()} dB (0.3 / 24), "
      f"nplci tg/bg {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and _Tv < 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "a heater is on"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(sr1.amplitude() - 1.0) < 1e-3 and sr1.time_constant() == 0.3 and sr1.filter_slope() == 24, "drive / tau changed — fast_delay is priced on tau = 0.3 s"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

# Fixed sensitivity for the whole fan (inherited from runs 6/7): 50 uV = 5 kOhm FS at 10 nA.
sr1.sensitivity(50e-6)
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS); sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti (tetralayer-stacking-fs-count Step 4): D = 0, n = {N_HI:+.2f} -> {N_LO:+.2f}e12 ({N_N}), "
                  f"B = {B_LO} -> {B_HI} T uniform 1/B ({N_B}), sr1 50 uV, run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {N_LO:+.2f} to {N_HI:+.2f}e12 cm^-2 ({N_N} pts, high->low), B = {B_LO} to {B_HI} T uniform in 1/B '
              f'({N_B} rows, d(1/B) 0.0075); electron side; tetralayer-stacking-fs-count Step 4; cal run 5: ratio '
              f'{CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; Vsi 0; sr1 50 uV')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# field left where the fan ended (6 T on completion) — the LK mass split rides down from there; no re-traverse.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
