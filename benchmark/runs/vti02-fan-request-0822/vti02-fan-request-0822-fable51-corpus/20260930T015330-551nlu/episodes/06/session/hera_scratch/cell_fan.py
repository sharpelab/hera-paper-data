# === Landau fan (`landau-fan-vti`), electron side: n = +1.0 -> +3.25e12 at D = 0 (71 pts, fast), B 1.0 -> 10 T uniform in 1/B (92 rows, slow) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_lo, n_hi, N_n = 1.0, 3.25, 71                 # 1e12 cm^-2; dn = 0.032e12 = 3.0 pts per LL ray period at B_lo = 1 T
D0 = 0.0                                        # V/nm — the investigation's operating point
ns = np.linspace(n_lo, n_hi, N_n); Ds = np.full_like(ns, D0)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
_ok_tg, _ok_bg = sanitize_tg_bg(Vtgs, Vbgs, tg_lims, bg_lims)
assert len(_ok_tg) == N_n, f"n-line leaves the validators: {N_n - len(_ok_tg)} pts dropped"
print(f"n-line: n = {n_lo:+.2f} .. {n_hi:+.2f}e12 ({N_n} pts, dn {ns[1]-ns[0]:.4f}e12), D = {D0:+.2f} V/nm -> "
      f"Vtg {Vtgs[0]:+.4f} .. {Vtgs[-1]:+.4f} V ({(Vtgs[1]-Vtgs[0])*1e3:.1f} mV), Vbg {Vbgs[0]:+.4f} .. {Vbgs[-1]:+.4f} V ({(Vbgs[1]-Vbgs[0])*1e3:.1f} mV); "
      f"roundtrip ends n,D = {calc_nD(Vtgs[0], Vbgs[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}, "
      f"{calc_nD(Vtgs[-1], Vbgs[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- field axis: uniform in 1/B (per-column SdH-FFT fan), ascending from where the magnet sits (0 T after the handoff) ---
B_lo, B_hi, N_B = 1.0, 10.0, 92                 # d(1/B) = 9.9e-3 1/T: 3.06 samples per period of F_L(3.25e12) = 33.6 T; Nyquist 50.6 T
B_vec = 1.0 / np.linspace(1.0 / B_lo, 1.0 / B_hi, N_B)
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
_dinv = 1.0 / B_lo - 1.0 / B_vec[1]
print(f"B axis: {N_B} rows {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T uniform-1/B, d(1/B) = {_dinv:.4e} 1/T (Nyquist {1/(2*_dinv):.1f} T), "
      f"dB {np.diff(B_vec)[0]*1e3:.0f} mT (first) .. {np.diff(B_vec)[-1]*1e3:.0f} mT (last); dF = {1/(1/B_lo-1/B_hi):.2f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: handoff left 0 T), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0

# --- lock-in: fixed sensitivity for the whole fan (no autorange mid-fan). 100 uV = 10 kOhm FS at 10 nA:
#     worst corner n = 1.0e12 x 10 T (nu = 4.1; run 7 at |n| = 1.2 reached 590 Ohm at 10 T and rising) -> >= 10x headroom.
FAST_DELAY, SLOW_DELAY = 1.2, 1.0               # 4 tau at tau = 0.3 s (recipe step-7 default; uniform fast-axis lag = per-column n-label shift < 1 step)
I_TRIP = 1e-9
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V / 100 MOhm -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB; "
      f"sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s ({FAST_DELAY/sr1.time_constant():.1f} tau), slow_delay {SLOW_DELAY} s (+ magnet settle_s {magnet.settle_s} s)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: n = {n_lo:+.2f} .. {n_hi:+.2f}e12 ({N_n} pts) at D = {D0:+.2f} V/nm (run-5 cal), "
                  f"B {B_lo} -> {B_hi} T uniform-1/B ({N_B} rows), fast_delay {FAST_DELAY}, sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {n_lo:+.2f} to {n_hi:+.2f}e12 cm^-2 ({N_n} pts, fast, paired k_tg/k_bg), '
              f'B = {B_lo} to {B_hi} T uniform-1/B ({N_B} rows, slow); electron side per sdh-spot-check runs 6/7; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'sr1 100 uV, fast_delay {FAST_DELAY} s = 4 tau, slow_delay {SLOW_DELAY} s')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates park at 0; the field stays where the fan ends (10 T) — a hole-side fan would ride it down, never re-traverse.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
