# === Landau fan, electron side, D = 0 (`landau-fan-vti`, for `tetralayer-stacking-fs-count` Step 4) ===
# n 2.00 -> 3.25e12 (27 pts, paired TG/BG line) fast  x  B 1.0 -> 10.0 T uniform in 1/B (91 rows) slow; ends at 10 T.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_N, D0 = 2.00, 3.25, 27, 0.0            # 1e12 cm^-2, V/nm
ns = np.linspace(N_LO, N_HI, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs[[0, -1]], Vbgs[[0, -1]])
print(f"n-line: {N_LO:+.2f} -> {N_HI:+.2f}e12, {N_N} pts (dn = {ns[1]-ns[0]:.4f}e12), D = {D0}; "
      f"Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V")

# --- field axis: uniform in 1/B, d(1/B) = 0.0100 1/T (1/3 Nyquist on F_L(3.25e12) = 33.6 T) ---
B_LO, B_HI, N_B = 1.0, 10.0, 91
B_vec = np.round(1.0 / np.linspace(1.0 / B_LO, 1.0 / B_HI, N_B), 4)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"B axis: {N_B} rows {B_vec[0]} -> {B_vec[-1]} T, d(1/B) = {np.mean(-np.diff(1/B_vec)):.4f} 1/T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_tau, _slope, _amp = sr1.time_constant(), sr1.filter_slope(), sr1.amplitude()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"sr1 tau {_tau} s / {_slope} dB (0.3/24), drive {_amp} V (1.0 -> 10 nA), nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert _tau == 0.3 and _slope == 24 and abs(_amp - 1.0) < 1e-3, "lock-in settling/drive differ from the spot checks the fan inherits"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

# --- lock-in: fixed for the whole fan (inherited from runs 6/7). 50 uV = 5 kOhm FS at 10 nA ---
SENS = 50e-6
sr1.sensitivity(SENS)
FAST_DELAY, SLOW_DELAY = 1.8, 3.0      # 6 tau per point; 10 tau after the row-start flyback + field step
I_TRIP = 1e-9
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS), sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti e-side: n {N_LO:+.2f}..{N_HI:+.2f}e12 ({N_N}) at D = {D0} (run-5 cal) fast x "
                  f"B {B_LO}..{B_HI} T uniform 1/B ({N_B}, d(1/B) 0.01) slow; sr1 50 uV; fast 1.8 s, slow 3 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'tetralayer-stacking-fs-count Step 4: D = {D0} V/nm, n = {N_LO:+.2f} to {N_HI:+.2f}e12 cm^-2 ({N_N} pts), '
              f'B = {B_LO} to {B_HI} T uniform in 1/B ({N_B} rows, d(1/B) = 0.0100 1/T); '
              f'cal run 5: c_tg {CAL["c_tg"]:.4e}, c_bg {CAL["c_bg"]:.4e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'inherits runs 6/7: tau 0.3 s / 24 dB, sr1 50 uV, 10 nA')

# --- position: gates to the first n point, then the field to B_LO (blocking ramp = the settle) ---
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
print(f"ramping field {magnet.field():+.3f} -> {B_vec[0]} T (~{abs(B_vec[0]-magnet.field())/0.137:.0f} min)")
magnet.field(B_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_rail = {"n": 0}
def guards(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.4f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[9])) > 0.9 * SENS:
        _rail["n"] += 1
        if _rail["n"] <= 5:
            print(f"RAIL WARN sr1 |X| = {abs(float(data[9])):.3e} V > 0.9 FS at B={float(data[1]):.4f} T, Vtg={float(data[2]):+.4f}")
s.register_run_after(guards, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY, init_delay=True)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field is left where the fan ended (10 T on completion) — the LK ladder rides it down; never re-traverse.
    print(f"end: B = {magnet.field():+.3f} T, gates parked (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
          f"T = {T_sample():.3f} K, rail warnings {_rail['n']}")
