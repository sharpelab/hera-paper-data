# === Landau fan at D = 0 (`landau-fan`): (Vtg, Vbg) co-swept along n, B slow 0.3 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- fast axis: 89 columns along the calibrated D = 0 line, dn = 0.05e12 cm^-2.
#     Edge columns sit exactly on the run-6 (+3.20) and run-7 (-1.20) spot densities.
n_vec = np.round(np.arange(-1.20, 3.2001, 0.05), 4)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
_nr, _Dr = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_Dr).max() < 1e-9, "fast axis is not on D = 0"
print(f"fast: n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f} e12 ({len(n_vec)} cols, dn 0.05); "
      f"Vtg {Vtg_vec.min():+.4f} .. {Vtg_vec.max():+.4f} (margin {Vtg_vec.min()-TG_MIN:+.4f}/{TG_MAX-Vtg_vec.max():+.4f} V), "
      f"Vbg {Vbg_vec.min():+.4f} .. {Vbg_vec.max():+.4f} (margin {Vbg_vec.min()-BG_MIN:+.4f}/{BG_MAX-Vbg_vec.max():+.4f} V)")

# --- slow axis: 6 low-field rows (fan convergence) + 71 rows uniform in 1/B, 1.2 -> 10 T (F_Nyq 47.7 T, dF 1.36 T).
B_vec = np.unique(np.round(np.concatenate([np.array([0.30, 0.45, 0.60, 0.80, 0.95, 1.10]), field_invB(1.2, 10.0, 71)]), 4))
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
assert np.all(np.diff(B_vec) > 0), "B grid must be monotonic ascending (no re-traverse)"
_inv = 1.0 / field_invB(1.2, 10.0, 71)
print(f"slow: {len(B_vec)} rows, B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T; dB {np.diff(B_vec).min()*1e3:.1f}-{np.diff(B_vec).max()*1e3:.0f} mT "
      f"(max row ramp {np.diff(B_vec).max()/0.137:.1f} min); 1/B block d(1/B) = {np.abs(np.diff(_inv)).mean():.5f} "
      f"-> F_Nyq {1/(2*np.abs(np.diff(_inv)).mean()):.1f} T, dF {1/(1/1.2 - 1/10):.2f} T")

FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9

# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm full scale at 10 nA.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V / {sr1.frequency()} Hz -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), "
      f"tau {sr1.time_constant()} s / {sr1.filter_slope()} dB, fast_delay {FAST_DELAY} s = {FAST_DELAY/sr1.time_constant():.1f} tau; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan: D = 0, n fast {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({len(n_vec)} cols, 0.05), "
                  f"B slow {B_vec[0]:.2f}..{B_vec[-1]:.2f} T ({len(B_vec)} rows, 6 low-field + 71 uniform in 1/B), "
                  f"Vsi = 0, sr1 sens 100 uV, fast_delay {FAST_DELAY}")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan, region-A calibration (run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e} F/m2 geometry prior, '
              f'n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.4f} V/nm); '
              f'fast = (k_tg.volt, k_bg.volt) co-swept along D = 0, n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 cm^-2 in 0.05 ({len(n_vec)} cols), '
              f'Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V; '
              f'slow = magnet.field {B_vec[0]:.2f}..{B_vec[-1]:.2f} T, {len(B_vec)} rows (0.30/0.45/0.60/0.80/0.95/1.10 T + 71 uniform in 1/B 1.2-10 T), '
              f'F_Nyq 47.7 T, dF 1.36 T; edge columns match the run-6 (+3.20) / run-7 (-1.20) sdh-spot-check densities')

s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(set), Vtg, Vbg, B(meas), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(magnet.field).fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, magnet.field, sr1.X); s.plot(k_tg.volt, magnet.field, sr0.X)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', sr1.P); s.plot('time', sr0.P)
s.plot('time', magnet.field); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[6])), abs(float(data[7]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates parked at 0; the field is LEFT where the fan ended (step 5 uses it -- a 10 T re-traverse costs 73 min).
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
