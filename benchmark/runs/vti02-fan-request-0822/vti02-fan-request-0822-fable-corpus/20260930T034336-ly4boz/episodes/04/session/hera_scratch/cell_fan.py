# === Landau fan, electron side (`landau-fan-vti`): D = 0, n = +1.5 -> +3.2e12, B 0.3 -> 6 T uniform-1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_hi, n_lo, N_n = 3.2, 1.5, 101                 # 1e12 cm^-2; e-side, D = 0
ns = np.linspace(n_hi, n_lo, N_n)
VV = np.array([calc_gate_voltages(n, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]) for n in ns])
Vtgs, Vbgs = VV[:, 0], VV[:, 1]
assert TG_MIN <= Vtgs.min() and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert BG_MIN <= Vbgs.min() and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
print(f"fast axis: n = {n_hi:+.2f} -> {n_lo:+.2f}e12 ({N_n} cols), Vtg [{Vtgs.min():+.4f}, {Vtgs.max():+.4f}], "
      f"Vbg [{Vbgs.min():+.4f}, {Vbgs.max():+.4f}]; roundtrip n,D @hi = {calc_nD(Vtgs[0], Vbgs[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- slow axis: uniform in 1/B, 0.3 -> 6.0 T ascending; d(1/B) = 1/(3*F_L(3.2e12)) = 0.01005 /T ---
B_lo, B_hi, N_B = 0.3, 6.0, 316
B_vec = np.round(1.0 / np.linspace(1.0 / B_lo, 1.0 / B_hi, N_B), 4)
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP
d_invB = (1 / B_lo - 1 / B_hi) / (N_B - 1)
print(f"slow axis: B {B_vec[0]} -> {B_vec[-1]} T, {N_B} rows uniform-1/B, d(1/B) = {d_invB:.5f} /T "
      f"(Nyquist limit {1/(2*d_invB):.1f} T; F_L(n_max) = 33.1 T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0.3), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 50 uV = 5 kOhm FS at 10 nA (worst corner n_min x 6 T <= ~600 Ohm = 12% FS, runs 6/7 anchor).
sr1.sensitivity(50e-6)
print(f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct; "
      f"fast_delay 1.8 s = 6 tau; drive {sr1.amplitude()} V -> 10 nA")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = 0, n = {n_hi:+.2f} -> {n_lo:+.2f}e12 ({N_n} cols), "
                  f"B {B_lo} -> {B_hi} T uniform-1/B {N_B} rows, sr1 50 uV, fast_delay 1.8 s (run-5 cal)")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = +0.00 V/nm: n = {n_hi:+.2f} -> {n_lo:+.2f}e12 cm^-2 ({N_n} cols, paired n-line); '
              f'B {B_lo} -> {B_hi} T uniform-1/B ({N_B} rows, d(1/B) = {d_invB:.5f} /T, Nyquist 1/3 on F_L(n_max) = 33.1 T); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'from spot checks 6 (e-side, onset censored <= 0.3 T) and 7 (h-side)')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=1, fast_delay=1.8)

# park gates; field stays at 6.0 T deliberately (LK mass split window 2.8-6 T follows the fan read)
s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
print(f"done: B = {magnet.field():+.3f} T (left at 6 T for the LK ladder), gates parked "
      f"({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
