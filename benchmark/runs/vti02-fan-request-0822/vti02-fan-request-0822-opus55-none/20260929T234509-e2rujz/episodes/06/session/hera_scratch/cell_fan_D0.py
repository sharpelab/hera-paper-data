# === Landau fan at D = 0 (`landau-fan`): B slow 1 -> 9 T (uniform-1/B 1-4 T, 0.2 T 4-9 T) x n fast -1.25 .. +3.25e12 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.25, 3.25 + 1e-9, 0.025), 4)          # 1e12 cm^-2, 181 pts, 0.025e12 step
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.round(Vtg_vec, 5), np.round(Vbg_vec, 5)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_n_chk, _D_chk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast: {len(n_vec)} pts, n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f}e12 at D = 0 (max|D| roundtrip {np.abs(_D_chk).max():.1e}); "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V")

# --- field grid: uniform in 1/B from 1 to 4 T (dInvB = 0.0119 1/T: >= 2.5 samples/period up to F = 34 T, the n = 3.25 Luttinger
#     frequency), then uniform 0.2 T from 4.2 to 9 T (QH picture). Ascending: the magnet sits at 0 T.
B_vec = np.unique(np.round(np.hstack((1.0 / np.linspace(1.0 / 1.0, 1.0 / 4.0, 64), np.arange(4.2, 9.0001, 0.2))), 4))
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"slow: {len(B_vec)} rows, B {B_vec[0]} -> {B_vec[-1]} T (first steps {np.diff(B_vec)[:2]}, step at 4 T {np.diff(B_vec)[62]:.3f} T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_tau, _amp, _f = sr1.time_constant(), sr1.amplitude(), sr1.frequency()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"Vtg/Vbg = {k_tg.volt():+.3f}/{k_bg.volt():+.3f} V, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS {magnet.persistent_switch_on()} output {magnet.output_enabled()}, sr1 tau {_tau} s / {sr1.filter_slope()} dB, drive {_amp} V @ {_f} Hz")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} off base"
assert abs(_B0) < 0.05, f"field not at 0: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert _tau == 0.3 and abs(_amp - 1.0) < 1e-6 and abs(_f - 13.777) < 0.01, "lock-in state differs from the priced one (tau 0.3 s, 1 V, 13.777 Hz)"

# Fixed sensitivity, no mid-row autorange: 100 uV = 10 kOhm FS at 10 nA. Runs 6/7 peaked at 590 Ohm (10 T) off the CNP; the CNP
# column at high B (nu = 0) may rail above 10 kOhm -- accepted, flagged in the read.
sr1.sensitivity(100e-6)
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP, T_TRIP = 1e-9, 3.0
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: n -1.25..+3.25e12 (181, 0.025e12) fast (Vtg, Vbg co-swept, run-5 cal), "
                  f"B 1 -> 9 T slow ({len(B_vec)} rows: uniform-1/B 1-4 T, 0.2 T 4-9 T), Vsi 0, sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg prior 9.5 nm, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm); '
              f'fast n -1.25 -> +3.25e12, 181 pts (0.025e12), Vtg {Vtg_vec[0]:+.4f}->{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}->{Vbg_vec[-1]:+.4f}; '
              f'slow B 1 -> 9 T, {len(B_vec)} rows (64 uniform-1/B 1-4 T + 0.2 T 4.2-9 T); Vsi 0; fast_delay 1 s; ends at 9 T, gates parked 0')

# row layout: [time, magnet_field, k_tg_volt, k_bg_volt, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def guard(station, data):
    i_tg, i_bg, T = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP or T > T_TRIP:
        print(f"GUARD TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A, T={T:.3f} K")
        station.interrupt_requested = True
s.register_run_after(guard, ())

s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
s.ramp(magnet.field, B_vec[0])            # 0 -> 1 T, blocks ~7.5 min
print(f"at row start: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
interruptible_sleep(10)
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY, init_delay=True)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # field holds where it is (9 T on completion) -- step 5 starts there
    print(f"end: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
