# === Landau fan #1 (`landau-fan`): D = 0 line, n = -1.25 .. +3.25e12 fast (151 pts), B 1.0 -> 10 T slow (76 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_line = np.linspace(-1.25, 3.25, 151)          # 1e12 cm^-2, 0.03e12 step, hole -> electron
D_line = 0.0                                    # V/nm
Vtg_line, Vbg_line = calc_gate_voltages(n_line, np.full_like(n_line, D_line), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_line.min() >= TG_MIN and Vtg_line.max() <= TG_MAX, (Vtg_line.min(), Vtg_line.max())
assert Vbg_line.min() >= BG_MIN and Vbg_line.max() <= BG_MAX, (Vbg_line.min(), Vbg_line.max())
print(f"fast line: n {n_line[0]:+.2f} -> {n_line[-1]:+.2f}e12 ({len(n_line)} pts, {n_line[1]-n_line[0]:.3f}e12), D = {D_line:+.2f} V/nm; "
      f"Vtg {Vtg_line.min():+.4f}..{Vtg_line.max():+.4f} V, Vbg {Vbg_line.min():+.4f}..{Vbg_line.max():+.4f} V (limits TG [{TG_MIN},{TG_MAX}], BG [{BG_MIN},{BG_MAX}])")

# --- field grid: uniform in B (LL lines straight in (n, B)); coarse below 4 T, fine above where nu is assigned
B_vec = np.round(np.concatenate((np.arange(1.0, 3.8001, 0.2), np.arange(4.0, 10.0001, 0.1))), 3)
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"slow B: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T (0.2 T to 3.8, 0.1 T from 4.0); {len(B_vec)*len(n_line)} pts")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left 0 T), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 200 uV = 20 kOhm FS at 10 nA. Run 6/7 maxima <= 590 Ohm at 10 T away from the CNP;
# only the nu = 0 region at high B can exceed 20 kOhm (a rail there is not diagnostic). Quantization ~0.3 Ohm.
sr1.sensitivity(200e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (20 kOhm FS); sr0 sens {sr0.sensitivity()} V; tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = {D_line:+.2f} V/nm (run-5 cal): fast (Vtg,Vbg) along n = {n_line[0]:+.2f}..{n_line[-1]:+.2f}e12 ({len(n_line)} pts), "
                  f"slow B {B_vec[0]}..{B_vec[-1]} T ({len(B_vec)} rows: 0.2 T to 3.8, 0.1 T from 4.0), sr1 200 uV, fast_delay 1 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_line:+.2f} V/nm; fast n = {n_line[0]:+.2f} -> {n_line[-1]:+.2f}e12 cm^-2 ({len(n_line)} pts, {n_line[1]-n_line[0]:.3f}e12) as co-swept (Vtg, Vbg); '
              f'slow B = {B_vec[0]} -> {B_vec[-1]} T ({len(B_vec)} rows); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e} (prior), '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; Vsi = 0; T_sample {_T0:.3f} K')
s.ramp(k_bg.volt, Vbg_line[0]); s.ramp(k_tg.volt, Vtg_line[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_line, Vbg_line],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates parked at 0; field stays where the fan ends (10 T) — fan #2 rides it down, never re-traverse.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
