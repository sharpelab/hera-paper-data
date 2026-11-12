# === Landau fan (`landau-fan`): B slow 1 -> 10 T uniform in 1/B (73 rows) x D = 0 line fast, n = -1.2 .. +3.2e12 (177 pts) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.2, 3.2 + 1e-9, 0.025), 4)            # 1e12 cm^-2, 177 pts; endpoints = runs 6/7 spot points
D_fan = 0.0                                                         # V/nm
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.full_like(n_vec, D_fan), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert len(Vtg_vec) == len(Vbg_vec) == len(n_vec) == 177
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
print(f"fast line D = {D_fan:+.2f} V/nm: n {n_vec[0]:+.3f} .. {n_vec[-1]:+.3f}e12 ({len(n_vec)} pts, step 0.025); "
      f"Vtg {Vtg_vec.min():+.4f} .. {Vtg_vec.max():+.4f} V (lims {TG_MIN}/{TG_MAX}); Vbg {Vbg_vec.min():+.4f} .. {Vbg_vec.max():+.4f} V (lims {BG_MIN}/{BG_MAX})")

# --- field grid: uniform in 1/B, 1 -> 10 T (magnet sits at 0; first slow set ramps 0 -> 1 T). Nyquist F = 0.5/d(1/B) = 40 T > F_L(3.2e12) = 33 T.
B_vec = np.round(field_invB(1.0, 10.0, 73), 4)
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"B grid: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T, d(1/B) = {abs(np.mean(np.diff(1/B_vec))):.4f} /T; first dB {B_vec[1]-B_vec[0]:.4f}, last dB {B_vec[-1]-B_vec[-2]:.3f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left 0 T), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 1.0, 3.0      # fast: as run 5 (same lag as the calibration map); slow: gate flyback settle on top of the driver's 3 s field settle
I_TRIP = 1e-9
# Fixed sensitivity: 100 uV = 10 kOhm FS at 10 nA. 1D peaks (runs 6/7) 530-590 Ohm -> >= 10x headroom; the nu = 0 CNP peak at high B may rail over a narrow n window (accepted).
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V; tau {sr1.time_constant()} s / {sr1.filter_slope()} dB")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan: B slow 1->10 T uniform 1/B ({len(B_vec)} rows); fast (Vtg,Vbg) co-swept along D = {D_fan:+.2f} V/nm, "
                  f"n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 step 0.025 ({len(n_vec)} pts); run-5 cal; Vsi = 0; sr1 100 uV; fast_delay 1 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_fan:+.2f} V/nm line, n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 cm^-2 step 0.025 ({len(n_vec)} pts, fast, Vtg/Vbg co-swept); '
              f'B {B_vec[0]} -> {B_vec[-1]} T uniform in 1/B ({len(B_vec)} rows, slow); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; fast-axis endpoints = run 6 / run 7 spot points')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, magnet.field, sr1.X)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # gates parked; field stays where the sweep left it (10 T if complete) - next step rides it down
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
