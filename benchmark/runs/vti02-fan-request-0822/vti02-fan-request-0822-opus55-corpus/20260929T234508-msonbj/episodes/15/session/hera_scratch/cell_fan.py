# === Landau fan, electron side, D = 0 (`landau-fan-vti`, per `tetralayer-stacking-fs-count` Step 4) ===
# Slow: magnet.field uniform in 1/B, 1.0 -> 10.0 T, 121 rows (d(1/B) = 0.0075 T^-1 = 1/(4.03 F_L(3.2e12))).
# Fast: paired (Vtg, Vbg) n-line at D = 0 (run-5 region-A calibration), n = +3.2 -> +1.6e12, 35 pts (dn = 0.047e12).
# Ends at B = 10 T (left there on purpose: the LK down-leg starts where the fan ends); gates parked at 0.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_HI, N_LO, N_N, D0 = 3.2, 1.6, 35, 0.0
ns = np.linspace(N_HI, N_LO, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs, Vbgs)
_n_rt, _D_rt = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_n_rt, ns, atol=1e-6) and np.allclose(_D_rt, 0, atol=1e-6)
print(f"n-line: {ns[0]:+.3f} -> {ns[-1]:+.3f}e12 ({N_N} pts, dn = {abs(ns[1]-ns[0]):.4f}e12), D = 0; "
      f"Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V")

B_LO, B_HI, N_B = 1.0, 10.0, 121
B_vec = field_invB(B_LO, B_HI, N_B)
assert B_vec[0] == B_LO and abs(B_vec[-1] - B_HI) < 1e-9 and np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP
_dinv = abs(np.diff(1 / B_vec)).max(); _FL = 10.345 * N_HI
print(f"B grid: {N_B} rows {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {_dinv:.5f} T^-1 "
      f"(Nyquist {1/(2*_dinv):.1f} T vs F_L(n_hi) = {_FL:.1f} T -> {1/(_dinv*_FL):.2f} pts/period)")

FAST_DELAY, SLOW_DELAY = 2.4, 3.0   # 8 tau at tau = 0.3 s / 24 dB (residual step ~4 %); slow_delay 10 tau after flyback + field step
I_TRIP, T_TRIP, SENS = 1e-9, 1.6, 50e-6

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_tau, _slope, _amp, _f = sr1.time_constant(), sr1.filter_slope(), sr1.amplitude(), sr1.frequency()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5) | B = {_B0:+.4f} T (|B| < 0.05) | V_si = {k_si():+.3f} V (0) | "
      f"PS heater {magnet.persistent_switch_on()} / output {magnet.output_enabled()} (True/True) | "
      f"nplci tg/bg {k_tg.nplci()}/{k_bg.nplci()} (1/1) | sr1 tau {_tau} s slope {_slope} dB (0.3/24) | "
      f"drive {_amp} V @ {_f:.3f} Hz (1.0 V / 13.777) | heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert abs(_B0) < 0.05, f"magnet not at ~0 T: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert _tau == 0.3 and _slope == 24, "lock-in settling differs from the spot checks' - dwell was priced on tau = 0.3 s / 24 dB"
assert abs(_amp - 1.0) < 1e-6 and abs(_f - 13.777) < 0.01, "drive differs from I_bias = 10 nA @ 13.777 Hz"
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0

# Fixed sensitivity for the whole fan (no autorange): 50 uV = 5 kOhm FS at 10 nA, same as spot checks runs 6/7.
sr1.sensitivity(SENS)
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS), sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti (tetralayer-stacking-fs-count Step 4): electron side, D = 0 (run-5 cal), "
                  f"n = {N_HI:+.2f} -> {N_LO:+.2f}e12 x {N_N}, B = {B_LO} -> {B_HI} T uniform-1/B x {N_B}, "
                  f"fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, sr1 50 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'tetralayer-stacking-fs-count Step 4 fan: D = {D0} V/nm, n = {N_HI} to {N_LO} (1e12 cm^-2, {N_N} pts), '
              f'B = {B_LO} to {B_HI} T uniform in 1/B ({N_B} rows, d(1/B) = {_dinv:.4f}); cal run 5: ratio '
              f'{CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'fast_delay {FAST_DELAY} s (8 tau), sr1 50 uV; inherits spot checks runs 6/7')

# --- position: gates to the first fan point, then the field to B_lo (blocking ramp, ~7.5 min from 0 T) ---
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
print(f"ramping field {magnet.field():+.4f} -> {B_vec[0]:.3f} T (blocking, ~{abs(B_vec[0]-magnet.field())/0.137:.1f} min)")
magnet.field(B_vec[0])
print(f"at B = {magnet.field():+.4f} T")
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_rails = []
def fan_guard(station, data):
    i_tg, i_bg, T, x1 = abs(float(data[5])), abs(float(data[6])), float(data[4]), float(data[9])
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if T > T_TRIP:
        print(f"T TRIP at B={float(data[1]):.3f} T: T_sample = {T:.3f} K > {T_TRIP} K")
        station.interrupt_requested = True
    if abs(x1) > 0.95 * SENS:
        _rails.append((float(data[1]), float(data[2]), x1))
        if len(_rails) > 20:
            print(f"RAIL TRIP: {len(_rails)} points with |sr1.X| > 95 % FS, last at B={float(data[1]):.3f} T Vtg={float(data[2]):+.4f}")
            station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.4f} T (left at the fan's top), (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
          f"T_sample = {T_sample():.3f} K, rail points = {len(_rails)}")
