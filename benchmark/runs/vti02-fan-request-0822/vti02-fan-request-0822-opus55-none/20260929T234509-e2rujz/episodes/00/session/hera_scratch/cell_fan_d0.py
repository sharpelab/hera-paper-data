# === D = 0 Landau fan (`landau-fan`): n fast along the region-A D = 0 line, B slow 0 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (ratio data-calibrated; absolute n-scale = geometry prior, the fan calibrates it) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.linspace(-1.24, 3.24, 150), 4)             # 1e12 cm^-2 (nominal), 0.030 step
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
print(f"fast: n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts); Vtg {Vtg_vec[0]:+.4f} .. {Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f} .. {Vbg_vec[-1]:+.4f} V")

# --- field grid (slow, ascending from where the magnet sits): 0, 0.5; 1-1.5 T at d(1/B) = 0.03; 1.5-4.5 T at d(1/B) = 0.012 (F_Nyq 42 T); 4.5-10 T at 0.25 T
B_vec = np.hstack(([0.0, 0.5], 1 / np.arange(1.0, 1 / 1.5, -0.03), 1 / np.arange(1 / 1.5, 1 / 4.5, -0.012), np.arange(4.5, 10.0001, 0.25)))
B_vec = np.unique(np.round(B_vec, 3)); B_vec = B_vec[np.hstack((np.diff(B_vec) > 0.015, True))]
assert B_vec.min() >= 0 and B_vec.max() <= B_SESSION_CAP
print(f"slow: B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), sr1 tau {sr1.time_constant()} s / {sr1.filter_slope()} dB (0.3/24), "
      f"drive {sr1.amplitude()} V (1.0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24 and abs(sr1.amplitude() - 1.0) < 1e-3
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 1.0, 3.0        # 1 s = 3.3 tau (same as gatemap run 5, the timing calibration); 3 s = 10 tau after flyback
I_TRIP, T_TRIP = 1e-9, 2.5               # A, K
# Fixed sensitivity: 100 uV = 10 kOhm FS at 10 nA (run 5: R <= 3.1 kOhm at 0 T). A rail on the CNP column at the highest B is accepted.
sr1.sensitivity(100e-6)
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS), sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 nominal (150, co-swept Vtg/Vbg on run-5 D=0 line), "
                  f"B 0 -> 10 T {len(B_vec)} rows (1/B-uniform 1-4.5 T, 0.25 T above), sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: fast n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 cm^-2 nominal (150 pts, 0.030), D = 0; (Vtg, Vbg) co-swept '
              f'({Vtg_vec[0]:+.4f},{Vbg_vec[0]:+.4f}) -> ({Vtg_vec[-1]:+.4f},{Vbg_vec[-1]:+.4f}); slow B 0 -> 10 T {len(B_vec)} rows '
              f'(0, 0.5; d(1/B) 0.03 on 1-1.5 T; 0.012 on 1.5-4.5 T; 0.25 T on 4.5-10 T); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; Vsi 0; fast_delay 1 s, slow_delay 3 s')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def guard(station, data):
    i_tg, i_bg, T = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP or T > T_TRIP:
        print(f"GUARD TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A, T={T:.3f} K")
        station.interrupt_requested = True
s.register_run_after(guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # gates parked; the field stays where the fan ends (10 T) — the next step rides it down
    print(f"end: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample {T_sample():.3f} K")
