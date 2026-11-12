# === Landau fan at D = 0 (`landau-fan`), plan step 4: n fast (co-swept Vtg/Vbg on the region-A D = 0 line), B slow 1.25 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; same as runs 6/7) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.linspace(-1.25, 3.25, 151), 4)          # 1e12 cm^-2, dn = 0.03
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.round(Vtg_vec, 5), np.round(Vbg_vec, 5)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast: {len(n_vec)} pts, n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 (roundtrip max|dn| {np.abs(_nchk-n_vec).max():.1e}, max|D| {np.abs(_Dchk).max():.1e}); "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V")

# --- field grid: uniform in 1/B (0.007 T^-1) 1.25 -> 5 T, then 0.2 T steps 5 -> 10 T ---
_invB = np.arange(1 / 1.25, 1 / 5.0 - 1e-9, -0.007)
B_vec = np.unique(np.round(np.hstack((1 / _invB[1 / _invB < 5.0 - 1e-6], np.arange(5.0, 10.0001, 0.2))), 4))
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"slow: {len(B_vec)} rows, B {B_vec[0]} -> {B_vec[-1]} T (max step {np.diff(B_vec).max():.3f} T, max d(1/B) {np.abs(np.diff(1/B_vec)).max():.4f} T^-1)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"drive {sr1.amplitude()} V @ {sr1.frequency():.3f} Hz (1.0 V, 13.777), sr0 sens {sr0.sensitivity()} V (0.02), tau {sr1.time_constant()} s / {sr1.filter_slope()} dB")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(sr1.amplitude() - 1.0) < 1e-6 and abs(sr1.frequency() - 13.777) < 0.01 and abs(sr0.sensitivity() - 0.02) < 1e-9

FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP, T_TRIP = 1e-9, 3.0
# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA (runs 6/7 peaked at 590 Ohm; high-B CNP columns may rail - accepted).
sr1.sensitivity(100e-6)
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, co-swept Vtg/Vbg, run-5 cal), "
                  f"B {B_vec[0]}..{B_vec[-1]} T ({len(B_vec)} rows, 1/B-uniform 0.007 to 5 T, 0.2 T above), sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 (region-A line); fast n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2, dn 0.03, {len(n_vec)} pts, co-swept (Vtg, Vbg) '
              f'{Vtg_vec[0]:+.4f}/{Vbg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f}/{Vbg_vec[-1]:+.4f} V; slow B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows, '
              f'uniform 1/B (0.007 T^-1) to 5 T then 0.2 T; fast_delay {FAST_DELAY}, slow_delay {SLOW_DELAY}; Vsi 0; '
              f'cal run 5: c_tg {CAL["c_tg"]:.4e}, c_bg {CAL["c_bg"]:.4e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
print(f"ramping field {magnet.field():+.4f} -> {B_vec[0]} T (~{abs(B_vec[0]-magnet.field())/0.137:.0f} min, blocking)")
s.ramp(magnet.field, B_vec[0])
interruptible_sleep(5)
print(f"at start: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")

# row layout: [time, magnet_field(set), k_2400_tg_volt, k_2400_bg_volt, T_sample, tg.curr, bg.curr, sr0.X, sr0.P, sr1.X, sr1.P, magnet_field(read)]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P).fp(magnet.field)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample); s.plot('time', magnet.field)

def guard(station, data):
    T, i_tg, i_bg = float(data[4]), abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if T > T_TRIP:
        print(f"T TRIP at B={float(data[1]):.3f} T: T_sample = {T:.3f} K > {T_TRIP} K")
        station.interrupt_requested = True
s.register_run_after(guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY, init_delay=True)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field stays where it ended (10 T on completion) - step 5 rides it down; never re-traverse.
    print(f"end: B = {magnet.field():+.4f} T (field left in place), (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
