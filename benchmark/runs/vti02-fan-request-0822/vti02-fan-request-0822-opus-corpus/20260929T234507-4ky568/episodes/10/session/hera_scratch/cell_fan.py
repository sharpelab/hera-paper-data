# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = 1.0 -> 3.2e12, B 0.8 -> 10 T ===
# Slow axis magnet.field (uniform in 1/B), fast axis the paired (Vtg, Vbg) n-line at D = 0.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_N = 1.0, 3.2, 60          # 1e12 cm^-2, electron side
B_LO, B_HI, N_B = 0.8, 10.0, 154        # T
D0 = 0.0                                # V/nm

ns = np.linspace(N_LO, N_HI, N_N)
Ds = np.full_like(ns, D0)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
B_vec = field_invB(B_LO, B_HI, N_B)     # uniform in 1/B, ascending

# --- design asserts: validators + Nyquist, both axes (landau-fan step 1) ---
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP, (B_vec.min(), B_vec.max())
_FL_max = cst.h / (4 * cst.e) * N_HI * 1e16                 # Luttinger freq at n_max, T
_dinvB = np.abs(np.diff(1 / B_vec)).max()
_dn_ray = 4 * (cst.e / cst.h) * B_LO / 1e16                 # LL ray spacing at B_lo, 1e12 cm^-2
_pts_per_ray = _dn_ray / (ns[1] - ns[0])
_span = 1 / B_LO - 1 / B_HI
assert 1 / (2 * _dinvB) >= 2.0 * _FL_max, "B sampling below the 2*F_L harmonic-alias floor"
assert _pts_per_ray >= 2.0, f"n-axis below ray-Nyquist: {_pts_per_ray:.2f} pts/ray"
print(f"F_L(n_max) = {_FL_max:.2f} T; d(1/B) = {_dinvB:.5f} 1/T -> Nyquist {1/(2*_dinvB):.1f} T "
      f"= {1/(2*_dinvB)/_FL_max:.2f} F_L; 1/B record {_span:.3f} 1/T -> dF = {1/_span:.2f} T")
print(f"n-line: {N_N} pts, step {(ns[1]-ns[0]):.4f}e12 -> {_pts_per_ray:.2f} pts/ray at {B_LO} T; "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")
print(f"roundtrip (n, D) at the ends: {calc_nD(Vtgs[0], Vbgs[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])} "
      f"{calc_nD(Vtgs[-1], Vbgs[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")
print(f"B rows: {N_B}, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, dB {np.diff(B_vec).min()*1e3:.1f} mT (low) "
      f"-> {np.diff(B_vec).max():.3f} T (top); grid {N_B * N_N} pts")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05, cell positions to "
      f"{B_LO} T), V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
assert _tau == 0.3 and _slope == 24, f"sr1 settling changed: tau {_tau}, slope {_slope} (dwell is 6 tau)"

FAST_DELAY, SLOW_DELAY = 1.8, 1.0       # 6 tau; slow_delay on top of the blocking field set
I_TRIP = 1e-9

# Fixed sensitivity for the whole fan (worst corner = low n x high B): 100 uV = 10 kOhm FS at 10 nA.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {_tau} s / {_slope} dB; "
      f"sr0 sens {sr0.sensitivity()} V; dwell {FAST_DELAY} s = {FAST_DELAY/_tau:.0f} tau")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan electron side: D = {D0} V/nm, n = {N_LO} -> {N_HI}e12 cm^-2 ({N_N} pts), "
                  f"B = {B_LO} -> {B_HI} T uniform-1/B ({N_B} rows), sr1 100 uV, dwell {FAST_DELAY} s; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {N_LO} to {N_HI}e12 cm^-2 ({N_N}-pt paired n-line), B = {B_LO} to {B_HI} T '
              f'({N_B} rows uniform in 1/B, d(1/B) = {_dinvB:.5f} 1/T = Nyquist at {1/(2*_dinvB):.0f} T); '
              f'sr1 sens 100 uV (10 kOhm FS), dwell {FAST_DELAY} s = 6 tau (tau 0.3 s, 24 dB/oct); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'step 4 of tetralayer-stacking-fs-count, electron side per spot checks runs 6/7')

# position the magnet and park the n-line at its start (blocking ramp ~6 min from 0 T)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
magnet.field(B_LO)
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field deliberately left at the fan's end point (10 T) for the LK ladder to ride down.
    print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
          f"T_sample = {T_sample():.3f} K")
