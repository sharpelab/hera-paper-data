# === Landau fan, electron side (`landau-fan-vti`): D = 0, n +3.2 -> +0.4 e12 (81 cols) x B 1.2 -> 10 T uniform-1/B (74 rows) ===
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(3.2, 0.4, 81)               # 1e12 cm^-2, fast axis: high n first (low-R end at row start)
D0 = 0.0                                        # V/nm
Vtgs, Vbgs = calc_gate_voltages(n_vec, np.full_like(n_vec, D0), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, \
    (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
print(f"fast axis: n = {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 at D = {D0} (dn = {abs(n_vec[1]-n_vec[0]):.3f}e12); "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")

# --- slow axis: uniform in 1/B (per-column SdH-FFT fan), ascending from where the magnet sits (0 T -> 1.2 T position) ---
B_vec = field_invB(1.2, 10.0, 74)               # d(1/B) = 0.0100 /T <= 1/(3*F_L(3.2e12) = 33.1 T); Nyquist 49.8 T
assert B_vec.max() <= B_SESSION_CAP
print(f"slow axis: {len(B_vec)} rows, {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T uniform 1/B; "
      f"d(1/B) = {abs(1/B_vec[0] - 1/B_vec[1]):.4f} /T; dF = {1/(1/B_vec[0] - 1/B_vec[-1]):.2f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0, _tau = T_sample(), magnet.field(), sr1.time_constant()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan positions to 1.2 T itself), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"tau = {_tau} s / slope {sr1.filter_slope()} dB, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert _tau == 0.3 and k_tg.nplci() == 1 and k_bg.nplci() == 1

FAST_DELAY, SLOW_DELAY = 1.8, 1.0               # 6*tau on the fast axis (per-column-FFT fan, base recipe step 7)
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA. Worst corner is low-n x high-B:
# R(n=0.4e12, 10 T) <~ 330 Ohm (CNP D~0 anchor, runs 0-3/5) x ~8 (near-CNP MR, run 7 showed 4x) ~ 2.6 kOhm = 26% FS.
sr1.sensitivity(100e-6)
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V; drive {sr1.amplitude()} V -> 10 nA")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = {D0} V/nm, n = +3.2 -> +0.4 e12 (81 cols, run-5 cal), "
                  f"B = 1.2 -> 10 T uniform 1/B (74 rows), sr1 100 uV, fast_delay 1.8 s (6 tau), slow_delay 1 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = +3.2 to +0.4 e12 cm^-2 (81 pts), B = 1.2 to 10 T uniform 1/B (74 rows); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'per-column SdH-FFT fan after spot checks runs 6-7 (pair 7.11/22.08 T + sum tone, scale 0.88)')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, magnet_field, k_tg_volt, k_bg_volt, T_sample, k_tg_curr, k_bg_curr, sr0_X, sr0_P, sr1_X, sr1_P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# field ends at 10 T deliberately — the next step (LK ladder or firming cuts) rides it down; never re-traverse.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V")
