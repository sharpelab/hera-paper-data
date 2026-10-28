# === Landau fan at D = 0 (`landau-fan`): B slow 1.5 -> 10 T (0.1 T, 86 rows); (Vtg, Vbg) co-swept along the calibrated D = 0 line, n = -1.25 .. +3.25e12 (129 pts) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.25, 3.25, 129)                       # 1e12 cm^-2; step 0.0352e12 (TG ~10 mV)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.round(np.asarray(Vtg_vec, float), 5), np.round(np.asarray(Vbg_vec, float), 5)
assert TG_MIN <= Vtg_vec.min() and Vtg_vec.max() <= TG_MAX and BG_MIN <= Vbg_vec.min() and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(np.asarray(_Dchk)).max() < 1e-3, "D = 0 line round-trip"
B_vec = np.round(np.arange(1.5, 10.0001, 0.1), 3)
assert B_vec.max() <= B_SESSION_CAP and len(B_vec) == 86
print(f"fast: {len(n_vec)} pts along D = 0, n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 (step {n_vec[1]-n_vec[0]:.4f}); "
      f"Vtg {Vtg_vec[0]:+.4f} .. {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} .. {Vbg_vec[-1]:+.4f} V")
print(f"slow: {len(B_vec)} rows, B {B_vec[0]} -> {B_vec[-1]} T, step 0.1 T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: handoff left the magnet at 0), V_si = {k_si():+.3f} V (0), "
      f"gates now (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

I_TRIP = 1e-9
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
# Fixed sensitivity 200 uV = 20 kOhm FS at 10 nA: runs 6/7 maxima <= 590 Ohm at |n| >= 1.2e12. The nu = 0 column at high B may
# exceed 20 kOhm and soft-clip (reads as ">= 20 kOhm: insulating" - informative); metallic minima keep ~0.75 Ohm resolution.
sr1.sensitivity(200e-6)
print(f"sr1 sens {sr1.sensitivity()} V (FS {sr1.sensitivity()/10e-9:.0f} Ohm at 10 nA), tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB; "
      f"fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: B slow {B_vec[0]} -> {B_vec[-1]} T (0.1 T, {len(B_vec)} rows); (Vtg, Vbg) co-swept along D = 0, "
                  f"n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, run-5 cal); sr1 200 uV; fast_delay {FAST_DELAY}, slow_delay {SLOW_DELAY}")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: B slow {B_vec[0]} -> {B_vec[-1]} T step 0.1 ({len(B_vec)} rows); fast (k_tg.volt, k_bg.volt) co-swept along D = 0: '
              f'n = {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 cm^-2 ({len(n_vec)} pts); Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f} V; '
              f'cal run 5: c_tg {CAL["c_tg"]:.3e} F/m2, ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; sr1 200 uV')
# gates to the first fast point before the 1.5 T lead-in ramp (each later row flies back to it)
s.ramp(k_bg.volt, float(Vbg_vec[0])); s.ramp(k_tg.volt, float(Vtg_vec[0]))
interruptible_sleep(5)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, k_tg.curr); s.plot(k_tg.volt, k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# ends at 10 T with the gates at the last fast point (n = +3.25e12) - no park; the next step rides the magnet down.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
