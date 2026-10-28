# === Landau fan (`landau-fan-vti`): electron side, D = 0, n +1.2 -> +3.25e12 x B 0.75 -> 10 T (uniform 1/B) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: paired-(Vtg, Vbg) n-line at D = 0, n descending +3.25 -> +1.2 e12 (81 cols) ---
ns = np.linspace(3.25, 1.2, 81)                 # 1e12 cm^-2; claim window n >= ~2.2 (partner 5-period floor)
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, \
    (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
print(f"n-line: {ns[0]:+.2f} -> {ns[-1]:+.2f} e12 (81 cols), Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, "
      f"Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")

# --- slow axis: uniform in 1/B, 0.75 -> 10 T ascending (magnet sits at 0; fan ends at 10 T for the next step) ---
N_B = 126                                        # d(1/B) = 0.00987 <= 1/(3*F_L(n_max)=33.6 T); Nyq f_max 50.7 T
B_vec = 1.0 / np.linspace(1/0.75, 1/10.0, N_B)
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
I_TRIP = 1e-9

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
_tau = sr1.time_constant()
assert abs(_tau - 0.3) < 0.01, f"sr1 tau changed: {_tau} s (dwell math assumes 0.3 s / 24 dB)"
assert abs(sr1.amplitude() - 1.0) < 0.01, f"drive amplitude {sr1.amplitude()} V != 1.0 (I_bias sizing assumes 10 nA)"

# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA — sized to the global worst corner
# (low n x high B: run 7 analog at |n|=1.2e12 read 576 Ohm at 10 T and rising; QH peaks headroom 17x).
sr1.sensitivity(100e-6)
FAST_DELAY, SLOW_DELAY = 1.8, 1.0                # 6*tau dwell (per-column FFT reads point values); gates retrace inside the field ramp
print(f"B rows: {N_B}, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {_tau} s; "
      f"fast_delay {FAST_DELAY}, slow_delay {SLOW_DELAY}")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan-vti: D = 0 electron fan, n = +1.2..+3.25e12 (81 cols), B 0.75 -> 10 T uniform-1/B "
                  "(126 rows, d(1/B)=0.00987), sr1 100 uV, fast_delay 1.8 s (6 tau); cal run 5; spots runs 6/7")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0.00 V/nm, n = {ns[-1]:+.2f} to {ns[0]:+.2f} e12 cm^-2 (81 cols, fast, descending), '
              f'B = {B_vec[0]:.3f} to {B_vec[-1]:.1f} T (126 rows, uniform 1/B, ascending); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'B_lo bound by spot run 6 (light tone censored at 0.30 T record edge)')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# field stays at 10 T (deliberate — next step decides the descent; never re-traverse).
print(f"done: B = {magnet.field():+.3f} T, gates parked at 0, T_sample = {T_sample():.3f} K")
