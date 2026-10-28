# === Landau fan (`landau-fan-vti`), electron side, D = 0: n +3.2 -> +1.2e12 (43 pts) x B 1.0 -> 10 T uniform-1/B (91 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_HI, N_LO, N_N = 3.2, 1.2, 43            # 1e12 cm^-2; dn = 0.0476 <= ray-Nyquist/2 at B_lo (0.0967e12/T x 1.0 T / 2)
B_LO, B_HI, N_B = 1.0, 10.0, 91           # d(1/B) = 0.0100 <= 1/(3 F_L(3.2e12) = 3 x 33.1 T)
FAST_DELAY, SLOW_DELAY = 3.0, 3.0         # 10 tau at tau 0.3 s / 24 dB (= spot-check settling); slow: post-flyback settle
I_TRIP, T_TRIP = 1e-9, 2.5                # A (gate leak), K (fridge-event guard, 3 consecutive pts)

ns = np.linspace(N_HI, N_LO, N_N); Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs[[0, -1]], Vbgs[[0, -1]])
B_vec = field_invB(B_LO, B_HI, N_B)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
print(f"fast: n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({N_N} pts, dn {abs(ns[1]-ns[0]):.4f}); Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V; "
      f"D roundtrip max |D| = {np.abs(calc_nD(Vtgs, Vbgs, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])[1]).max():.1e}")
print(f"slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T ({N_B} rows, d(1/B) {1/B_vec[0]-1/B_vec[1]:.4f} 1/T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _Tv, _B0 = T_sample(), T_vaporizer(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {_Tv:.3f} K (<2), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and _Tv < 2.0 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
_amp, _frq, _tau, _slope = sr1.amplitude(), sr1.frequency(), sr1.time_constant(), sr1.filter_slope()
print(f"precondition drive {_amp} V @ {_frq} Hz (1.0 V, 13.777 Hz -> 10 nA); sr1 tau {_tau} s / {_slope} dB (0.3 / 24: dwell {FAST_DELAY} s = {FAST_DELAY/_tau:.0f} tau); "
      f"sr0 sens {sr0.sensitivity()} V, tau {sr0.time_constant()} s")
assert abs(_amp - 1.0) < 1e-3 and abs(_frq - 13.777) < 0.01 and abs(_tau - 0.3) < 1e-6 and _slope == 24

# Fixed sensitivity for the whole fan (no autorange): 50 uV = 5 kOhm FS at 10 nA — the spot-check scale; worst corner
# R(n=1.2, 10 T) ~ 105 Ohm x ~10 MR ~ 1 kOhm (0.2 FS), 2x QH-peak margin still < 0.5 FS. (state0 restore left it at 2 uV.)
sr1.sensitivity(50e-6)
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti (tetralayer-stacking-fs-count Step 4): electron side D = 0, n {N_HI:+.2f} -> {N_LO:+.2f}e12 ({N_N}), "
                  f"B {B_LO} -> {B_HI} T uniform-1/B ({N_B}), fast_delay {FAST_DELAY} s, sr1 50 uV, run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0 V/nm, n = {N_HI:+.2f} to {N_LO:+.2f}e12 cm^-2 ({N_N} pts, dn {abs(ns[1]-ns[0]):.4f}), B = {B_LO} to {B_HI} T uniform-1/B '
              f'({N_B} rows, d(1/B) 0.0100); fast_delay {FAST_DELAY} s (10 tau), slow_delay {SLOW_DELAY} s; sr1 50 uV; '
              f'cal run 5: c_tg {CAL["c_tg"]:.3e}, c_bg {CAL["c_bg"]:.3e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'investigation tetralayer-stacking-fs-count Step 4 (per-column FFT, F(n) vs F_L)')

# --- position: field first (gates parked at 0; blocking ~7 min), then gates to the first n point ---
magnet.field(B_vec[0])
print(f"positioned: B = {magnet.field():+.4f} T")
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, magnet_field, k_tg_volt, k_bg_volt, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_hot = [0]
def guards(station, data):
    i_tg, i_bg, T = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    _hot[0] = _hot[0] + 1 if T > T_TRIP else 0
    if _hot[0] >= 3:
        print(f"T TRIP at B={float(data[1]):.3f} T: T_sample {T:.3f} K > {T_TRIP} K for 3 pts")
        station.interrupt_requested = True
s.register_run_after(guards, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field is NOT parked: it ends at 10 T for the next step (LK / firming fan ride it down — never re-traverse).
    print(f"done: B = {magnet.field():+.4f} T, gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample {T_sample():.3f} K")
