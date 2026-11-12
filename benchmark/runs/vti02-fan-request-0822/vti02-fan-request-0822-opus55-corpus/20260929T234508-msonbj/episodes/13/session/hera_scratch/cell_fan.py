# === Landau fan, electron side, D = 0 (`landau-fan-vti`): n +2.00 -> +3.24e12 (32 cols) x B 1.0 -> 10 T uniform-1/B (108 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (same as spot checks runs 6/7 — the fan is read against the same n axis) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0
ns = np.round(np.arange(2.0, 3.2401, 0.04), 3)                     # 32 columns, 0.04e12 step; n = 3.20 on-grid (run 6 column)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs), np.asarray(Vbgs)
_vt, _vb = sanitize_tg_bg(Vtgs, Vbgs, tg_lims, bg_lims)
assert len(_vt) == len(ns), f"n-line leaves the validator box: {len(ns) - len(_vt)} points out"
print(f"n-line: {len(ns)} pts, n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = {D0}; Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V")

# --- field axis: uniform in 1/B, two segments (see markdown): 1.0 -> 3.5 T at d(1/B) = 0.0094, 3.5 -> 10 T at 0.0060 ---
_invB = lambda a, b, n: 1.0 / np.linspace(1.0 / a, 1.0 / b, n)     # uniform in 1/B (same as hera.analysis.field_invB)
B_vec = np.hstack((_invB(1.0, 3.5, 77), _invB(3.5, 10.0, 32)[1:]))
assert np.all(np.diff(B_vec) > 0) and B_vec[0] > 0 and B_vec.max() <= B_SESSION_CAP
print(f"B axis: {len(B_vec)} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T; d(1/B) = {abs(np.diff(1/B_vec[:77])).mean():.5f} / {abs(np.diff(1/B_vec[76:])).mean():.5f} 1/T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {T_vaporizer():.3f} K, B = {_B0:+.4f} T (|B|<0.02), V_si = {k_si():+.3f} V (0), "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.02 and abs(k_si()) < 0.01
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
# dwell is derived from tau/slope — assert them, don't assume
print(f"lock-in: drive {sr1.amplitude()} V @ {sr1.frequency()} Hz; sr1 tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; sr0 tau {sr0.time_constant()} s")
assert abs(sr1.amplitude() - 1.0) < 1e-3 and abs(sr1.frequency() - 13.777) < 0.01
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24 and sr0.time_constant() == 0.3

SENS = 50e-6                     # 5 kOhm FS at 10 nA — inherited from spot checks runs 6/7
FAST_DELAY, SLOW_DELAY = 1.8, 3.0   # 6 tau on the n-axis (per-column FFT); 10 tau after flyback (+3 s magnet settle)
I_TRIP = 1e-9
sr1.sensitivity(SENS)
print(f"sr1 sens {sr1.sensitivity()} V ({SENS / 10e-9:.0f} Ohm FS); sr0 sens {sr0.sensitivity()} V; fast/slow delay {FAST_DELAY}/{SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan electron side D = 0: n {ns[0]:+.2f}..{ns[-1]:+.2f}e12 ({len(ns)}), B {B_vec[0]:.1f}->{B_vec[-1]:.1f} T uniform-1/B "
                  f"({len(B_vec)} rows, 2 segs split at 3.5 T), sr1 50 uV, fast 1.8 s / slow 3 s; cal run 5")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 cm^-2 ({len(ns)} pts, 0.04 step), B = {B_vec[0]:.2f} to {B_vec[-1]:.2f} T uniform-1/B '
              f'({len(B_vec)} rows: 1.0-3.5 T d(1/B)=0.0094, 3.5-10 T d(1/B)=0.0060); per-column SdH FFT for tetralayer-stacking-fs-count Step 4; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; sr1 50 uV, tau 0.3 s/24 dB')
s.add_comment('tetralayer-stacking-fs-count')

# position: gates to the first column, magnet 0 -> 1.0 T (blocking, ~7.5 min)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
print(f"positioning magnet {magnet.field():+.3f} -> {B_vec[0]:.3f} T (blocking ~{abs(B_vec[0] - magnet.field()) / 0.137:.1f} min)")
magnet.field(B_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_g = {"first": True, "rail": 0}
def fan_guard(station, data):
    if _g["first"]:   # verify the row layout the guard indexes into, once
        _g["first"] = False
        ok = abs(float(data[2]) - Vtgs[0]) < 3e-3 and abs(float(data[3]) - Vbgs[0]) < 3e-3 and abs(float(data[1]) - B_vec[0]) < 0.02
        print(f"guard layout check: B {float(data[1]):+.4f}, Vtg {float(data[2]):+.4f}, Vbg {float(data[3]):+.4f} -> {'OK' if ok else 'MISMATCH'}")
        if not ok:
            station.interrupt_requested = True; return
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[9])) > 0.95 * SENS:
        _g["rail"] += 1
        if _g["rail"] >= 3:
            print(f"RAIL TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}: sr1.X={float(data[9]):.3e} V vs FS {SENS:.0e}")
            station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # park gates; the field stays where the fan ended (10 T planned) — the LK/temperature step rides it down
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
