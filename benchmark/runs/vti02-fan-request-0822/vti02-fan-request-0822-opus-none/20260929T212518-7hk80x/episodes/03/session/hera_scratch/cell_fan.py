# === Landau fan (`landau-fan`): B slow 1.0 -> 10.0 T x (Vtg, Vbg) co-swept along D = 0, n = -1.20 -> +3.20e12 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: the D = 0 line, uniform in n. Endpoints are exactly the run 6 / run 7 spot densities. ---
NFAST = 141
n_vec = np.linspace(-1.20, 3.20, NFAST)                       # 1e12 cm^-2, dn = 3.14e10
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, **CAL)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
_n_rt, _D_rt = calc_nD(Vtg_vec, Vbg_vec, **CAL)
assert np.max(np.abs(_D_rt)) < 1e-9, "fast axis is not on D = 0"
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 in {NFAST} pts (dn {np.diff(n_vec)[0]*1e12:.2e} cm^-2), D = 0; "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} (margin {Vtg_vec.min()-TG_MIN:+.3f}/{TG_MAX-Vtg_vec.max():+.3f} V), "
      f"Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} (margin {Vbg_vec.min()-BG_MIN:+.3f}/{BG_MAX-Vbg_vec.max():+.3f} V); "
      f"step {np.diff(Vtg_vec)[0]*1e3:.1f} mV tg / {np.diff(Vbg_vec)[0]*1e3:.1f} mV bg")

# --- slow axis: field, ascending from where the magnet sits (0 T). Uniform in B: this is a fan-line map,
#     not a 1/B spectroscopy run (runs 6, 7 already hold the fine-1/B spectra at the two endpoint densities).
B_vec = np.round(np.arange(1.0, 10.0001, 0.1), 4)             # 91 rows
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0

# --- preconditions (assumed by this cell, not set by it) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.1: handoff left the magnet at 0), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.1 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"

FAST_DELAY, SLOW_DELAY = 0.7, 3.0
I_TRIP = 1e-9
# Sensitivity sized to the worst-case R on the map (the nu = 0 CNP column at 10 T), not to the SdH amplitude:
# lock-in noise here is input-referred ~20 nV and flat across 20 -> 100 uV (measured, runs 4 vs 5), so range costs
# nothing in noise. 500 uV = 50 kOhm FS at 10 nA = 200x the B = 0, D = 0 CNP resistance (240 Ohm, run 5).
sr1.sensitivity(500e-6)
print(f"drive {sr1.amplitude()} V / {meas_config['bias_resistor']:.0e} Ohm -> {sr1.amplitude()/meas_config['bias_resistor']*1e9:.1f} nA; "
      f"sr1 sens {sr1.sensitivity()} V (50 kOhm FS), tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct; "
      f"sr0 sens {sr0.sensitivity()} V")
print(f"grid: {len(B_vec)} rows x {NFAST} pts = {len(B_vec)*NFAST} points; "
      f"B {B_vec[0]} -> {B_vec[-1]} T step {np.diff(B_vec)[0]:.2f} T (ramp {np.diff(B_vec)[0]/0.137*60:.0f} s/row, settle_s {magnet.settle_s} s)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan: B slow 1.0 -> 10.0 T (0.1 T, 91 rows) x (Vtg, Vbg) co-swept on D = 0, "
                  "n -1.20 -> +3.20e12 (141 pts), run-5 cal, Vsi = 0, sr1 500 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line, n = {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2 in {NFAST} pts '
              f'(Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f}); '
              f'B slow {B_vec[0]} -> {B_vec[-1]} T, {np.diff(B_vec)[0]:.2f} T, {len(B_vec)} rows; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.4e} F/m2 (9.5 nm prior), '
              f'n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; '
              f'endpoints = the run 6 (+3.2e12) and run 7 (-1.2e12) sdh-spot-check densities')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, magnet.field, sr1.X)      # the live fan map
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

# Leakage trip + per-row field read-truth. magnet.field() blocks through the ramp, so the setpoint column is the
# reached field; this re-reads the measured field once per row (rig-card read-truth rule) and warns on any mismatch.
_row = {"B": None}
def row_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    b_set = float(data[1])
    if _row["B"] != b_set:
        _row["B"] = b_set
        try:
            b_meas = magnet.field()
            if abs(b_meas - b_set) > 5e-3:
                print(f"FIELD MISMATCH row B_set={b_set:+.3f} T, measured {b_meas:+.4f} T (d={b_meas-b_set:+.4f})")
        except Exception as exc:                      # a transient TCP hiccup must not kill a 4 h fan
            print(f"field read-truth check failed at B_set={b_set:+.3f} T: {exc!r}")
s.register_run_after(row_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# field is left at 10 T (or wherever an interrupt left it) — the close-out cell brings it down.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
