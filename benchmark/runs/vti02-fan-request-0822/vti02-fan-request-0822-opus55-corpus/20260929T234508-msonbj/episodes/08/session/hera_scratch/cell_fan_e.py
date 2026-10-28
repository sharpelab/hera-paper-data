# === Landau fan (`landau-fan-vti`), electron side, D = 0: n 3.2 -> 1.5e12 (39 pts) x B 1.0 -> 8.0 T uniform in 1/B (117 rows) ===
# Per-column SdH-FFT fan for the stacking call (investigations/tetralayer-stacking-fs-count Step 4).
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (same as spot checks runs 6/7)
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_hi, n_lo, N_n, D0 = 3.2, 1.5, 39, 0.0
ns = np.linspace(n_hi, n_lo, N_n); Ds = D0 * np.ones(N_n)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, **CAL)
_vt, _vb = sanitize_tg_bg(Vtgs, Vbgs, tg_lims, bg_lims)
assert len(_vt) == N_n, "n-line leaves the validator box"
print(f"n-line: {n_hi:+.2f} -> {n_lo:+.2f}e12 ({N_n} pts, dn {abs(ns[1]-ns[0]):.4f}e12), D = {D0}; "
      f"Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V")

# --- field axis: uniform in 1/B, ascending from where the magnet sits (0 T)
B_lo, B_hi, N_B = 1.0, 8.0, 117
B_vec = field_invB(B_lo, B_hi, N_B)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
print(f"B axis: {N_B} rows {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {(1/B_lo-1/B_hi)/(N_B-1):.5f} 1/T (F_Nyq {0.5*(N_B-1)/(1/B_lo-1/B_hi):.1f} T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"sr1 tau {_tau} s / {_slope} dB (0.3 / 24 — dwell priced on it), drive {sr1.amplitude()} V @ {sr1.frequency()} Hz (1.0 V, 13.777)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} off base"
assert abs(_B0) < 0.05, f"magnet not at 0 T: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert _tau == 0.3 and _slope == 24, "lock-in tau/slope differ from the priced 0.3 s / 24 dB — re-price before running"
assert abs(sr1.amplitude() - 1.0) < 1e-6 and abs(sr1.frequency() - 13.777) < 0.01

# --- lock-in: fixed sensitivity for the whole fan (inherited from runs 6/7): 50 uV = 5 kOhm FS at 10 nA
SENS = 50e-6
sr1.sensitivity(SENS)
FAST_DELAY, SLOW_DELAY = 2.1, 3.0      # 7 tau (24 dB/oct settling floor); slow = 10 tau after the flyback
I_TRIP, T_TRIP, CLIP = 1e-9, 2.5, 0.9 * SENS
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS), sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = {D0} V/nm, n = {n_hi:+.2f} -> {n_lo:+.2f}e12 ({N_n}), "
                  f"B = {B_lo} -> {B_hi} T uniform 1/B ({N_B}), sr1 50 uV, fast_delay {FAST_DELAY}, run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {n_lo} to {n_hi} (1e12 cm^-2, {N_n} pts, fast n_hi->n_lo), B = {B_lo} to {B_hi} T '
              f'uniform in 1/B ({N_B} rows, F_Nyq {0.5*(N_B-1)/(1/B_lo-1/B_hi):.0f} T); per-column SdH FFT for tetralayer-stacking-fs-count Step 4; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}; inherits runs 6/7')

# --- position: gates to the first n-line point, then the magnet to B_lo (blocking ramp ~6 min from 0 T)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
magnet.field(B_vec[0])
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}); T = {T_sample():.3f} K")
interruptible_sleep(10)

# row layout: [time, magnet_field, k_tg_volt, k_bg_volt, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_clips = []
def fan_guard(station, data):
    i_tg, i_bg, T, x1 = abs(float(data[5])), abs(float(data[6])), float(data[4]), abs(float(data[9]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if T > T_TRIP:
        print(f"T TRIP: T_sample = {T:.3f} K > {T_TRIP} K at B = {float(data[1]):.3f} T")
        station.interrupt_requested = True
    if x1 > CLIP:
        _clips.append((float(data[1]), float(data[2]), x1))
        if len(_clips) <= 5 or len(_clips) % 50 == 0:
            print(f"CLIP WARN #{len(_clips)}: |sr1.X| = {x1*1e6:.1f} uV > 90% FS at B = {float(data[1]):.3f} T, Vtg = {float(data[2]):+.4f}")
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field endpoint: stays at 8 T (the next step — LK mass / follow-up — rides it down; never re-traverse)
    print(f"end: B = {magnet.field():+.4f} T, gates parked ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}); clip warnings: {len(_clips)}; T = {T_sample():.3f} K")
