# === Landau fan, electron side, D = 0 (`landau-fan-vti`): n +1.60 -> +3.25e12 (38) fast x B 1.0 -> 7.5 T uniform-1/B (89 rows) slow ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_N, D0 = 1.60, 3.25, 38, 0.0          # 1e12 cm^-2, V/nm
ns = np.linspace(N_LO, N_HI, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.max(), Vbgs.max())
_n_chk, _D_chk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"n-line: {N_N} pts, n {ns[0]:+.3f} -> {ns[-1]:+.3f}e12 (dn {ns[1]-ns[0]:.4f}e12), D = {D0:+.2f} V/nm (roundtrip max|D| {np.max(np.abs(_D_chk)):.1e}); "
      f"Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V")

# --- field axis: uniform in 1/B (per-column SdH-FFT fan), dinvB = 1/(3 F_L(n_hi)) ---
B_LO, B_HI, N_B = 1.0, 7.5, 89
B_vec = 1.0 / np.linspace(1.0 / B_LO, 1.0 / B_HI, N_B)          # ascending 1.0 -> 7.5 T
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"B axis: {N_B} rows {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) {(1/B_LO-1/B_HI)/(N_B-1):.5f} 1/T (Nyquist F {0.5*(N_B-1)/(1/B_LO-1/B_HI):.1f} T; F_L(n_hi) = 33.6 T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _Tv, _B0 = T_sample(), T_vaporizer(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {_Tv:.3f} K, B = {_B0:+.4f} T (|B|<0.05: handoff left 0 T), V_si = {k_si():+.3f} V (0), "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci tg/bg {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "heaters not off"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

# --- lock-in: fixed for the whole fan. 50 uV = 5 kOhm FS at 10 nA (inherited from runs 6-7); tau 0.1 s x 24 dB, dwell 1.0 s = 10 tau ---
sr1.sensitivity(50e-6)
sr0.time_constant(0.1); sr1.time_constant(0.1)
FAST_DELAY, SLOW_DELAY = 1.0, 2.0
print(f"drive {sr1.amplitude()} V; sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; "
      f"sr0 sens {sr0.sensitivity()} V, tau {sr0.time_constant()} s / {sr0.filter_slope()} dB; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")
assert sr1.filter_slope() == 24 and sr0.filter_slope() == 24
I_TRIP, T_TRIP = 1e-9, 2.0

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron D=0: n {N_LO:+.2f}..{N_HI:+.2f}e12 ({N_N}) fast, B {B_LO}->{B_HI} T uniform-1/B ({N_B}) slow, "
                  f"sr1 50 uV, tau 0.1 s, fast_delay 1.0 s; cal run 5")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {N_LO} to {N_HI} (1e12 cm^-2, {N_N} pts), B = {B_LO} to {B_HI} T uniform in 1/B ({N_B} rows, '
              f'd(1/B) = 1/(3 F_L(n_hi))); tetralayer-stacking-fs-count Step 4; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; spot checks runs 6-7')

# --- position: field first (blocking ramp 0 -> 1.0 T, ~7.5 min), then gates to the row start ---
magnet.field(B_vec[0])
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V")

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_rail = {"n": 0}
def fan_guard(station, data):
    T, i_tg, i_bg, x1 = float(data[4]), abs(float(data[5])), abs(float(data[6])), abs(float(data[9]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if T > T_TRIP:
        print(f"T TRIP at B={float(data[1]):.3f} T: T_sample = {T:.3f} K > {T_TRIP} K")
        station.interrupt_requested = True
    if x1 > 0.9 * 50e-6 and _rail["n"] < 5:
        _rail["n"] += 1
        print(f"RAIL WARN at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}: |sr1.X| = {x1:.3e} V (>0.9 FS)")
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field stays where the fan ended (7.5 T on completion) -- the next step decides; never re-traverse blind.
    print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
