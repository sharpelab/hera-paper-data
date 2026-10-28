# === Landau fan at D = 0 (`landau-fan`): B slow 1 -> 10 T uniform in 1/B (81 rows) x n fast -1.25 -> +3.25e12 along D = 0 (121 pts) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (ratio data-calibrated; absolute scale = 9.5 nm prior, to be re-fixed from this fan's nu-slopes) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.unique(np.round(np.hstack([np.arange(-1.25, -0.75, 0.05),      # hole side, 50e9 step
                                      np.arange(-0.75, 0.7501, 0.025),    # near CNP, 25e9 step
                                      np.arange(0.80, 3.2501, 0.05)]), 4))  # electron side, 50e9 step
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert len(n_vec) == 121
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_nchk, n_vec) and np.abs(_Dchk).max() < 1e-9
B_vec = np.round(field_invB(1.0, 10.0, 81), 5)          # ascending, uniform in 1/B: d(1/B) = 0.01125 /T
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"fast: n {n_vec[0]:+.3f} .. {n_vec[-1]:+.3f}e12 ({len(n_vec)} pts); Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f}, "
      f"Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V; slow: B {B_vec[0]} -> {B_vec[-1]} T ({len(B_vec)} rows, 1/B-uniform)")

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {T_vaporizer():.3f} K, B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"PS {magnet.persistent_switch_on()} / output {magnet.output_enabled()} (True/True), nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0)")
print(f"precondition lock-ins: drive {sr1.amplitude()} V @ {sr1.frequency()} Hz (1.0 @ 13.777), sr1 tau {sr1.time_constant()} s / {sr1.filter_slope()} dB (0.3/24), "
      f"sr0 sens {sr0.sensitivity()} V (0.02), sr0 tau {sr0.time_constant()} s")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert abs(_B0) < 0.05, f"magnet not at ~0: {_B0} T"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "a heater range is on"
assert abs(sr1.amplitude() - 1.0) < 1e-3 and abs(sr1.frequency() - 13.777) < 0.01, "drive changed"
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24 and sr0.time_constant() == 0.3, "tau/slope not what the delays are priced on"
assert sr0.sensitivity() == 0.02, "sr0 sensitivity not 20 mV"

# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm FS at 10 nA (state0 left sr1 at 2 uV).
sr1.sensitivity(100e-6)
FAST_DELAY, SLOW_DELAY = 1.0, 5.0      # 3.3 tau per point (as run 5); 5 s after each field step + gate flyback
I_TRIP, T_TRIP = 1e-9, 2.5             # A on either gate; K on the sample mount
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS); fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan D=0: B 1->10 T 81 rows uniform in 1/B; n -1.25..+3.25e12 along D=0 (121 pts, 25e9 step |n|<=0.75, 50e9 beyond), "
                  "run-5 cal (ratio 0.773, c_tg prior 9.5 nm, n_off -0.089e12, D_off -0.013); sr1 100 uV; fast_delay 1 s, tau 0.3 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('D = 0 fan; slow magnet.field 1.0 -> 10.0 T, 81 rows uniform in 1/B (d(1/B) 0.01125); fast (Vtg, Vbg) co-swept along D = 0, '
              'n -1.25 .. +3.25e12 cm^-2 (121 pts; 25e9 step for |n| <= 0.75, 50e9 beyond); Vsi = 0; T base; '
              'cal run 5: ratio 0.773, c_tg 2.796e-3 F/m2 (prior), n_offset -0.0894e12, D_offset -0.013 V/nm; n labels in run-5 cal units')

# row layout: [time, B_set, Vtg, Vbg, T_sample, B_meas, I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(magnet.field).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample); s.plot('time', magnet.field)
IDX_T, IDX_ITG, IDX_IBG = 4, 6, 7

def guard(station, data):
    i_tg, i_bg, t = abs(float(data[IDX_ITG])), abs(float(data[IDX_IBG])), float(data[IDX_T])
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if t > T_TRIP:
        print(f"T TRIP at B={float(data[1]):.3f} T: T_sample = {t:.3f} K > {T_TRIP} K")
        station.interrupt_requested = True
s.register_run_after(guard, ())

s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # gates parked at 0; field stays where the fan ended (10 T on completion)
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
