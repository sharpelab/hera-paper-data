# === Landau fan, electron side, D = 0 (`landau-fan-vti`): n +1.0 -> +3.24e12 (61 pts) x B 1.2 -> 10 T uniform-1/B (100 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB
import scipy.constants as _cst

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts by ramping to 1.2 T), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert abs(_B0) < 0.05, f"magnet not at zero: {_B0} T"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- fast axis: D = 0 n-line (region-A calibration) ---
n_lo, n_hi, N_n = 1.0, 3.24, 61                    # 1e12 cm^-2
ns = np.linspace(n_lo, n_hi, N_n); D0 = 0.0
Vtgs, Vbgs = calc_gate_voltages(ns, np.full_like(ns, D0), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
_nchk, _Dchk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert abs(_nchk - ns).max() < 1e-6 and abs(_Dchk).max() < 1e-9

# --- slow axis: uniform in 1/B, Delta(1/B) = 1/(4 F_L(n_hi)) -> F_L and its 2nd harmonic unaliased in every column ---
B_lo, B_hi = 1.2, 10.0
F_L_max = _cst.h / (4 * _cst.e) * n_hi * 1e16     # T
N_B = int(np.ceil((1 / B_lo - 1 / B_hi) * 4 * F_L_max)) + 1
B_vec = field_invB(B_lo, B_hi, N_B)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
_dinv = abs(np.diff(1 / B_vec)).mean()
_ray = 4 * _cst.e / _cst.h * B_lo * 1e-16          # nu = 4 ray spacing at B_lo, 1e12 cm^-2
print(f"fan: n {n_lo} -> {n_hi} e12 ({N_n} pts, dn {ns[1]-ns[0]:.4f}), Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f} V; "
      f"B {B_lo} -> {B_hi} T, {N_B} rows uniform-1/B, Delta(1/B) = {_dinv:.5f} 1/T (F_L(n_hi) = {F_L_max:.1f} T, Nyquist {0.5/_dinv:.1f} T); "
      f"n-axis {_ray/(ns[1]-ns[0]):.1f} pts per nu=4 ray at B_lo")

FAST_DELAY, SLOW_DELAY = 1.8, 1.0                  # 6 tau at tau = 0.3 s / 24 dB (per-column-FFT floor); field set blocks + 3 s driver settle
I_TRIP = 1e-9
SR1_SENS = 100e-6                                   # 10 kOhm FS at 10 nA — worst corner n = 1.0 x 10 T (~1-3 kOhm expected)
sr1.sensitivity(SR1_SENS)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V; "
      f"est. {N_B * (N_n * (FAST_DELAY + 0.17) + 5) / 60 + 73:.0f} min")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron D = 0: n {n_lo} -> {n_hi} e12 ({N_n} pts) fast (Vtg, Vbg paired), B {B_lo} -> {B_hi} T slow, {N_B} rows uniform-1/B; "
                  f"fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, sr1 {SR1_SENS*1e6:.0f} uV; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {n_lo} to {n_hi} e12 ({N_n} pts), B = {B_lo} to {B_hi} T ({N_B} rows, uniform 1/B, Delta(1/B) = 1/(4 F_L(n_hi))); '
              f'electron side; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'fast_delay {FAST_DELAY} s (6 tau), sr1 sens {SR1_SENS*1e6:.0f} uV')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, k_tg.curr, k_bg.curr, T_sample, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(k_tg.curr).fp(k_bg.curr).fp(T_sample)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

_rail = {"n": 0}
def fan_guard(station, data):
    i_tg, i_bg = abs(float(data[4])), abs(float(data[5]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[9])) > 0.9 * SR1_SENS and _rail["n"] < 5:
        _rail["n"] += 1
        print(f"RAIL WARNING sr1 X = {float(data[9])*1e6:.1f} uV (>0.9 FS) at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V")
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# field is left at the fan's end (10 T) deliberately: the next step (LK mass split at n = +3.2) rides it down.
print(f"done: B = {magnet.field():+.3f} T (left here), gates parked (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), rail warnings {_rail['n']}")
