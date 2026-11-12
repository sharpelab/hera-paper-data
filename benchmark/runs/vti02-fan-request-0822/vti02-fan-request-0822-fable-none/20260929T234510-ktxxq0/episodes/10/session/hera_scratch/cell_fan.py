# === Landau fan along D = 0 (`landau-fan`): n -1.24 -> +3.24e12 fast (113 pts), B 0.5 -> 8 T slow (190 rows, uniform 1/B) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.24, 3.2401, 0.04), 3)          # 1e12 cm^-2, D = 0
Vtgs, Vbgs = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtgs.min() and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert BG_MIN <= Vbgs.min() and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
B_rows = np.round(field_invB(0.5, 8.0, 190), 5)              # ascending, uniform in 1/B
assert B_rows.max() <= B_SESSION_CAP
F_nyq = len(B_rows) / (2 * (1 / B_rows[0] - 1 / B_rows[-1]))
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, dn 0.04); Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V")
print(f"slow: B {B_rows[0]:.3f} -> {B_rows[-1]:.3f} T, {len(B_rows)} rows uniform 1/B, F_Nyq = {F_nyq:.1f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left 0), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

I_TRIP, T_TRIP = 1e-9, 2.0
# 200 uV = 20 kOhm FS at 10 nA: the field-gapped CNP column sets R_max (run-4 rail lesson), not the 0 T peaks.
sr1.sensitivity(200e-6)
print(f"sr1 sens {sr1.sensitivity()} V ({sr1.sensitivity() / 10e-9 / 1e3:.0f} kOhm FS), tau {sr1.time_constant()} s; fast_delay 1.0 s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = f"landau-fan D=0: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 (113 pts), B 0.5-8 T 190 rows uniform 1/B, sr1 200 uV, run-5 cal"
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}): '
              f'fast n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2, {len(n_vec)} pts (Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f}); '
              f'slow B {B_rows[0]:.3f} -> {B_rows[-1]:.3f} T, {len(B_rows)} rows uniform 1/B (F_Nyq {F_nyq:.0f} T); fast_delay 1 s, slow_delay 0')

# park gates at the first fast point before the first field row
s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def fan_guard(station, data):
    i_tg, i_bg, t_s = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if t_s > T_TRIP:
        print(f"T TRIP at B={float(data[1]):+.3f} T: T_sample={t_s:.3f} K")
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_rows], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=0, fast_delay=1.0)
# ends at 8 T with the gates at the electron end (n = +3.24e12) - next step starts from there; no park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
