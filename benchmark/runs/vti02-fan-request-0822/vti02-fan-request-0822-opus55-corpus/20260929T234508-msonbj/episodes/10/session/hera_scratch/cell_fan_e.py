# === Landau fan, electron side, D = 0 (`landau-fan-vti`; governs: tetralayer-stacking-fs-count Step 4) ===
# fast: paired (Vtg, Vbg) n-line n = 3.25 -> 2.00e12 (30 pts) at D = 0 (run-5 cal)
# slow: magnet.field 0.9 -> 10 T uniform in 1/B (103 rows, d(1/B) = 0.0099 1/T = 1/(3 F_L(n_max)))
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB
# --- session calibration from run 5 (cnp-and-dline-calibration; same constants as spot checks runs 6-7) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_HI, N_LO, N_N = 3.25, 2.00, 30                 # 1e12 cm^-2; dn = 0.043 = ray spacing 4eB/h at B_lo / 2
B_LO, B_HI, N_B = 0.90, 10.0, 103                # B_lo = sdh_onset of run 6 (0.91 T); B_hi = session cap
FAST_DELAY, SLOW_DELAY = 2.1, 3.0                # 7 tau at tau = 0.3 s / 24 dB (settling floor); flyback settle
SENS = 50e-6                                     # sr1: 5 kOhm FS at 10 nA (spot checks peaked at 12 % FS)
I_TRIP, T_TRIP = 1e-9, 2.0                       # A, K — auto-abort thresholds (E1: no eyes on the live plot)
ns = np.linspace(N_HI, N_LO, N_N); Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, \
    (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
_rt = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_rt[0], ns, atol=1e-6) and np.allclose(_rt[1], 0, atol=1e-6)
B_vec = field_invB(B_LO, B_HI, N_B)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"fast: n {ns[0]:+.3f} -> {ns[-1]:+.3f}e12, {N_N} pts (dn {ns[0]-ns[1]:.4f}); Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, "
      f"Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V")
print(f"slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows uniform-1/B (d(1/B) {1/B_vec[0]-1/B_vec[1]:.5f}); "
      f"dB {B_vec[1]-B_vec[0]:.4f} T at B_lo, {B_vec[-1]-B_vec[-2]:.3f} T at B_hi")

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_tau, _slope, _amp, _f = sr1.time_constant(), sr1.filter_slope(), sr1.amplitude(), sr1.frequency()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {T_vaporizer():.3f} K, B = {_B0:+.4f} T (|B| < 0.05, handoff left 0 T), "
      f"V_si = {k_si():+.3f} V (0), heaters {heater.sample_range()}/{heater.vaporizer_range()} (0/0), "
      f"PS {magnet.persistent_switch_on()} output {magnet.output_enabled()}, nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"sr1 tau {_tau} s slope {_slope} dB (0.3 / 24), drive {_amp} V @ {_f} Hz (1.0 / 13.777)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} off base"
assert abs(_B0) < 0.05, f"magnet not at ~0 T: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "a heater is on"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert abs(_tau - 0.3) < 1e-9 and _slope == 24, "lock-in tau/slope changed: FAST_DELAY is derived from 0.3 s / 24 dB"
assert abs(_amp - 1.0) < 1e-6 and abs(_f - 13.777) < 0.01, "drive changed (I_bias = 10 nA assumed)"

# --- fixed sensitivity for the whole fan (no autorange mid-fan) ---
sr1.sensitivity(SENS)
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS), sr0 sens {sr0.sensitivity()} V")
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan electron side D = 0 (run-5 cal): n {N_HI:+.2f} -> {N_LO:+.2f}e12 ({N_N}), "
                  f"B {B_LO} -> {B_HI} T uniform-1/B ({N_B}), fast_delay {FAST_DELAY} s, sr1 50 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'tetralayer-stacking-fs-count Step 4 fan: D = 0 V/nm, n = {N_HI:+.2f} to {N_LO:+.2f}e12 cm^-2 ({N_N} pts), '
              f'B = {B_LO} to {B_HI} T uniform-1/B ({N_B} rows); B_lo = sdh_onset run 6 (0.91 T); '
              f'cal run 5: c_tg {CAL["c_tg"]:.4e}, c_bg {CAL["c_bg"]:.4e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'fast_delay {FAST_DELAY} s (7 tau), slow_delay {SLOW_DELAY} s, sr1 50 uV, 10 nA')

# --- positioning: magnet 0 -> B_lo (blocking, ~7 min), then gates to the first n-point ---
print(f"positioning magnet {magnet.field():+.4f} -> {B_vec[0]:.3f} T (blocking)")
magnet.field(B_vec[0])
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, magnet_field, k_tg.volt, k_bg.volt, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_clip = {"n": 0}
def fan_guard(station, data, writer):
    """E1 auto-guards, looked up by column name: gate leakage / temperature excursion -> interrupt; sr1 clip -> log."""
    c = writer.metadata["columns"]; v = dict(zip(c, data))
    i_tg, i_bg = abs(float(v["k_2400_tg_curr"])), abs(float(v["k_2400_bg_curr"]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(v['magnet_field']):.3f} T, Vtg={float(v['k_2400_tg_volt']):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if float(v["T_sample"]) > T_TRIP:
        print(f"T TRIP at B={float(v['magnet_field']):.3f} T: T_sample = {float(v['T_sample']):.3f} K > {T_TRIP} K")
        station.interrupt_requested = True
    if abs(float(v["sr1_X"])) >= 0.95 * SENS:
        _clip["n"] += 1
        if _clip["n"] <= 5 or _clip["n"] % 50 == 0:
            print(f"CLIP #{_clip['n']} sr1_X = {float(v['sr1_X']):.3e} V at B={float(v['magnet_field']):.3f} T, Vtg={float(v['k_2400_tg_volt']):+.4f}")
s.register_run_after(fan_guard, ())
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # park gates; the field stays where the fan ended (10 T) for the next step to ride down — never re-traverse
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
          f"T_sample = {T_sample():.3f} K, sr1 clips = {_clip['n']}")
