# === Landau fan (`landau-fan-vti`): D = 0 electron side, n = +0.80 -> +3.20e12, B 1.2 -> 10 T uniform in 1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0
N_N, N_B = 65, 93
ns = np.linspace(0.80, 3.20, N_N)                    # 1e12 cm^-2, fast axis, ascending
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns),
                                CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())

# slow axis: uniform in 1/B (per-column SdH-FFT fan), ascending in B -- starts where the magnet sits.
B_vec = 1.0 / np.linspace(1.0 / 1.2, 1.0 / 10.0, N_B)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
_dinv = np.abs(np.diff(1.0 / B_vec))
_span = 1.0 / B_vec[0] - 1.0 / B_vec[-1]
_FL_max = ns.max() * 1e16 * 6.62607015e-34 / (4 * 1.602176634e-19)
assert _dinv.max() <= 1.0 / (3 * _FL_max), "B grid fails the preferred 1/3 Nyquist bound on F_L"
_dn = ns[1] - ns[0]
_ray = 4 * 1.602176634e-19 / 6.62607015e-34 * B_vec[0] / 1e16      # LL ray spacing, 1e12 cm^-2, at B_lo
assert _ray / _dn >= 2.0, "n grid fails ray-Nyquist at B_lo"
print(f"fast: n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = {D0:+.2f} V/nm, {N_N} pts, dn = {_dn:.4f}e12; "
      f"Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V")
print(f"      ray spacing at B_lo = {_ray:.4f}e12 -> {_ray/_dn:.2f} pts/ray (floor 2, prefer 3)")
print(f"slow: B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T, {N_B} rows, d(1/B) = {_dinv.max():.5f} "
      f"-> Nyquist {0.5/_dinv.max():.1f} T (F_L(n_max) = {_FL_max:.1f} T); 1/B span {_span:.4f} -> dF = {1/_span:.2f} T")
print(f"      roundtrip n,D at the ends: {calc_nD(Vtgs[0], Vbgs[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}, "
      f"{calc_nD(Vtgs[-1], Vbgs[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, "
      f"output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 1.2, 3.0          # 4 tau on the fast axis; 3 s after the gate flyback
I_TRIP, T_WARN = 1e-9, 1.6

# Fixed sensitivity for the whole fan (worst corner n_min x B_max): 100 uV = 10 kOhm FS at 10 nA.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); "
      f"tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan: D = 0, n = +0.80 to +3.20e12 ({N_N} pts) fast, B = 1.2 to 10 T uniform in 1/B "
                  f"({N_B} rows, d(1/B) = {_dinv.max():.5f}), Vsi = 0, sr1 sens 100 uV, fast_delay {FAST_DELAY}")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 cm^-2 ({N_N} pts), '
              f'B = {B_vec[0]:.2f} to {B_vec[-1]:.2f} T ({N_B} rows, uniform in 1/B, d(1/B) = {_dinv.max():.5f}, '
              f'Nyquist {0.5/_dinv.max():.1f} T, dF = {1/_span:.2f} T); electron side per sdh-spot-check runs 6/7; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')

# position: gates first (seconds), then the magnet (blocking ramp, ~9 min from 0 T)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
s.ramp(magnet.field, B_vec[0])
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_warned = {"T": False}
def fan_guard(station, data):
    i_tg, i_bg, t_s = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if t_s > T_WARN and not _warned["T"]:
        print(f"T WARNING at B={float(data[1]):+.3f} T: T_sample = {t_s:.3f} K > {T_WARN} K (recorded, not aborting)")
        _warned["T"] = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field stays at 10 T on purpose: the LK mass split rides it down rather than re-traversing.
    print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
          f"T_sample = {T_sample():.3f} K")
