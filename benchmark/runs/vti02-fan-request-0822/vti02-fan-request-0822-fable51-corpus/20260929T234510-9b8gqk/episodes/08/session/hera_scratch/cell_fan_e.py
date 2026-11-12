# === Landau fan, electron side, D = 0 (`landau-fan-vti`): n = +1.2 -> +3.2e12 (51 pts, fast paired n-line) x B 0.4 -> 10 T (241 rows, uniform-1/B in two legs, slow) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = 9.5 nm geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_lo, n_hi, N_n = 1.2, 3.2, 51        # 1e12 cm^-2; dn = 0.04e12 = 2.4 pts per 4-fold LL ray at 1 T (ray-pattern read floors at B >= 1 T)
D0 = 0.0                              # V/nm — the investigation's operating point
ns = np.linspace(n_lo, n_hi, N_n); Ds = np.full(N_n, D0)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
n_chk, D_chk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"n-line: n = {n_lo:+.2f} -> {n_hi:+.2f}e12 ({N_n} pts, dn = {ns[1]-ns[0]:.3f}e12) at D = {D0:+.2f} V/nm; "
      f"Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V; "
      f"roundtrip n [{np.min(n_chk):+.3f}, {np.max(n_chk):+.3f}], max|D| {np.max(np.abs(D_chk)):.4f}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: fan starts from 0 -> 0.4 T), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"sr1 tau {sr1.time_constant()} s / slope {sr1.filter_slope()} dB (0.3 / 24 -> dwell 1.2 s = 4 tau)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24, "sr1 tau/slope changed — dwell sized for 0.3 s / 24 dB"

# --- slow axis: uniform in 1/B, two legs (both from the run-6 spot check).
#     Low leg 0.4 -> 1.0 T, d(1/B) = 0.025 (Nyquist 20 T: the light tone and its 2x only — the heavy tone is below its ~1.8 T onset here).
#     Main leg 1.0 -> 10 T, d(1/B) = 0.005 (Nyquist 100 T: heavy tone ~30 T; its 2x/3x/4x/5x harmonics at 59/88/120/150 T fold to
#     59/88/80/50 T — none into the 0-45 T claim band. At d(1/B) = 0.0083 the 3x would fold onto F_L = 33 T; checked on run 6 resampled.)
B_low = field_invB(0.4, 1.0, 61)[:-1]
B_main = field_invB(1.0, 10.0, 181)
B_vec = np.round(np.hstack((B_low, B_main)), 5)
assert np.all(np.diff(B_vec) > 0) and B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
FAST_DELAY, SLOW_DELAY = 1.2, 3.0     # 4 tau at tau = 0.3 s; B is the slow axis, so each row settles through the blocking ramp + 3 s driver settle + SLOW_DELAY
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 50 uV = 5 kOhm FS at 10 nA. Worst corner is low-n x 10 T: run 7 (n = -1.2e12, closer to the CNP
# than any fan column) peaked at 587 Ohm = 0.12 FS at 10 T; run 6 (n = +3.2e12) resolved SdH at 0.2-1 % FS from 1 T. 8x headroom, same setting as both spot checks.
sr1.sensitivity(50e-6)
print(f"B grid: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T (legs: {len(B_low)} rows @ d(1/B) = 0.025, {len(B_main)} rows @ 0.005); "
      f"sr1 sens {sr1.sensitivity()} V, sr0 sens {sr0.sensitivity()} V, drive {sr1.amplitude()} V @ {sr1.frequency()} Hz")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side, D = 0: n {n_lo:+.2f} -> {n_hi:+.2f}e12 ({N_n} pts) fast paired (Vtg, Vbg); "
                  f"B {B_vec[0]} -> {B_vec[-1]} T slow, {len(B_vec)} rows uniform-1/B (0.4-1 T d(1/B) 0.025; 1-10 T d(1/B) 0.005); "
                  f"run-5 cal; sr1 50 uV; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {n_lo:+.2f} to {n_hi:+.2f}e12 cm^-2 ({N_n} pts, electron side), '
              f'B = {B_vec[0]} to {B_vec[-1]} T ({len(B_vec)} rows, uniform-1/B: 0.4-1 T d(1/B) = 0.025, 1-10 T d(1/B) = 0.005); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e} F/m2, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'inherits sdh-spot-check run 6 (light 7.3 T tone alive at 1 T, heavy 29.4 T tone onset ~1.8 T; sum tone ~37 T)')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B (slow), Vtg, Vbg (fast pair), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B = {float(data[1]):+.3f} T, Vtg = {float(data[2]):+.4f} V: |I_tg| = {i_tg:.3e}, |I_bg| = {i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # park gates; the field stays where the fan ended (10 T) — the next step decides the ride-down
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
