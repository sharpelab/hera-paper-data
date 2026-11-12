# === Landau fan, electron side, D = 0 (`landau-fan-vti`, per `tetralayer-stacking-fs-count` Step 4) ===
# Per-column SdH-FFT fan: B slow, uniform in 1/B, 0.85 -> 6.0 T (123 rows, d(1/B) = 0.00828 -> Nyquist 60 T);
# n fast, paired (Vtg, Vbg) line at D = 0, n = 2.40 -> 3.24e12 (22 pts, 0.04e12). Ends at 6 T, gates parked at 0.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (ratio data-calibrated, scale = geometry prior; same as runs 6/7) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0
ns = np.linspace(2.40, 3.24, 22)                                  # fast axis, 1e12 cm^-2
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs), np.asarray(Vbgs)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs, Vbgs)
_nchk, _Dchk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_nchk, ns) and np.allclose(_Dchk, D0, atol=1e-9)
B_LO, B_HI, N_B = 0.85, 6.0, 123
B_vec = field_invB(B_LO, B_HI, N_B)                                # ascending (magnet sits at ~0 T)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
SLOW_DELAY, FAST_DELAY = 3.0, 1.8                                 # 10 tau after flyback / 6 tau per n-point
I_TRIP = 1e-9
print(f"fan: n {ns[0]:.2f}->{ns[-1]:.2f}e12 ({len(ns)} pts), Vtg {Vtgs[0]:+.4f}->{Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f}->{Vbgs[-1]:+.4f}; "
      f"B {B_vec[0]:.3f}->{B_vec[-1]:.3f} T ({len(B_vec)} rows, d(1/B) {(1/B_LO-1/B_HI)/(N_B-1):.5f})")

# --- preconditions (assumed, not set): print expected vs actual, stop on mismatch ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_amp, _f, _tau, _slope = sr1.amplitude(), sr1.frequency(), sr1.time_constant(), sr1.filter_slope()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5) | B = {_B0:+.4f} T (|B|<0.05) | V_si = {k_si():+.3f} V (0) | "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0) | PS {magnet.persistent_switch_on()} out {magnet.output_enabled()} | "
      f"nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1) | drive {_amp} V @ {_f:.3f} Hz (1.0 @ 13.777) | tau {_tau} s / {_slope} dB (0.3 / 24) | "
      f"sr0 sens {sr0.sensitivity()} V (>= 0.02)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert abs(_B0) < 0.05, f"magnet not near 0 T: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "a heater is on"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert abs(_amp - 1.0) < 1e-6 and abs(_f - 13.777) < 0.01, "drive changed (I_bias assumed 10 nA)"
assert abs(_tau - 0.3) < 1e-9 and _slope == 24, "lock-in tau/slope differ from what the dwell was priced against"
assert sr0.sensitivity() >= 0.02, "sr0 sensitivity would rail the 10 mV drain signal"

# --- station first (a setup error costs nothing: no instrument has moved yet) ---
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron D=0: n {ns[0]:.2f}->{ns[-1]:.2f}e12 x{len(ns)}, B {B_LO}->{B_HI} T x{N_B} uniform 1/B, "
                  f"fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, sr1 50 uV, run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'tetralayer-stacking-fs-count Step 4 fan, electron side: D = {D0} V/nm, n = {ns[0]:.2f} to {ns[-1]:.2f}e12 cm^-2 ({len(ns)} pts, 0.04e12); '
              f'B = {B_LO} to {B_HI} T, {N_B} rows uniform in 1/B (d(1/B) {(1/B_LO-1/B_HI)/(N_B-1):.5f} 1/T, Nyquist 60 T); '
              f'fast_delay {FAST_DELAY} s (6 tau), slow_delay {SLOW_DELAY} s; sr1 50 uV (5 kOhm FS); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; inherits spot check run 6')
# row layout: [time, magnet_field, k_tg_volt, k_bg_volt, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

# Fixed sensitivity for the whole fan (no autorange): 50 uV = 5 kOhm FS at 10 nA. Worst corner n = 2.4 x 6 T:
# R(0) 66 Ohm (run 5) x MR ~10-13 (run 6) ~ 0.7-0.9 kOhm -> >= 5x headroom. sr1 sat at 2 uV after the handoff restore.
sr1.sensitivity(50e-6)
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS) | sr0 sens {sr0.sensitivity()} V | tau {sr1.time_constant()} s")

# --- position: gates to the row start, then the magnet (blocking, ~6 min 0 -> 0.85 T) ---
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
magnet.field(B_vec[0])
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # field stays where the fan ended (6 T unless interrupted) — the next step rides it down; gates park at 0.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
