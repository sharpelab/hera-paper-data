# === Landau fan, electron side (`landau-fan-vti`): D = 0 n-line n = +1.0 -> +3.2e12 (45 pts, fast) x B 0.7 -> 10 T uniform-1/B (121 rows, slow) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_lo, n_hi, N_n, D0 = 1.0, 3.2, 45, 0.0                  # 1e12 cm^-2 (step 0.05), V/nm
ns = np.linspace(n_lo, n_hi, N_n); Ds = np.full(N_n, D0)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
_n_chk, _D_chk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_n_chk, ns, atol=1e-6) and np.abs(_D_chk).max() < 1e-6
print(f"n-line: {N_n} pts n = {n_lo:+.2f} .. {n_hi:+.2f}e12 at D = {D0:+.2f} V/nm; Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")

# --- field grid: uniform in 1/B, ascending from 0.7 T (magnet sits at 0), ending at 10 T (the next step rides it down) ---
B_lo, B_hi, N_B = 0.7, 10.0, 121
B_vec = np.asarray(field_invB(B_lo, B_hi, N_B), float)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
d_inv = (1 / B_lo - 1 / B_hi) / (N_B - 1)
print(f"B grid: {N_B} rows {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {d_inv:.5f}/T (Nyquist F = {1/(2*d_inv):.0f} T vs F_L(3.2e12) = 33 T); "
      f"steps {np.diff(B_vec)[0]*1e3:.1f} mT at the bottom, {np.diff(B_vec)[-1]:.2f} T at the top")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan ramps up from 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 2.0, 1.0     # fast: ~6.7 tau at tau = 0.3 s / 24 dB (the n-axis carries the per-column read); slow: rides the driver's 3 s field settle
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA — sized for the low-n x high-B corner (QH peaks near nu = 4-8 at n ~ 1e12),
# not the 10-50 Ohm high-n low-B floor (0.3 Ohm LSB there; the spot check's 5 kOhm FS would soft-clip a 5 kOhm peak).
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron: D = {D0:+.2f} V/nm, n = {n_lo:+.2f} .. {n_hi:+.2f}e12 ({N_n} pts) fast, "
                  f"B {B_lo} -> {B_hi} T uniform-1/B ({N_B} rows) slow; run-5 cal; sr1 100 uV; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {n_lo:+.2f} to {n_hi:+.2f}e12 cm^-2 ({N_n} pts, paired (Vtg, Vbg) line, fast), '
              f'B = {B_lo} to {B_hi} T uniform in 1/B ({N_B} rows, d(1/B) = {d_inv:.5f}/T, slow); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'electron side chosen from spot check run 6 (7.1 T tone + 14/22/29.5 T components)')
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
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)     # gates parked; the field is left where the fan ended (10 T) — the next step rides it down
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
