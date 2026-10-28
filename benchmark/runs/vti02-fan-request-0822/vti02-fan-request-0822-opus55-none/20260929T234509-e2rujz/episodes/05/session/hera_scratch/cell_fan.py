# === D = 0 Landau fan (`landau-fan`), plan step 4: n fast along the calibrated D = 0 line, B slow 1 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (ratio data-calibrated; absolute scale = geometry prior, ~11 % high per runs 6/7) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.25, 3.24, 150)                       # 1e12 cm^-2 (cal units), 0.030 step
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.round(Vtg_vec, 5), np.round(Vbg_vec, 5)
assert (Vtg_vec.min() >= TG_MIN) and (Vtg_vec.max() <= TG_MAX) and (Vbg_vec.min() >= BG_MIN) and (Vbg_vec.max() <= BG_MAX), \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_n_rt, _D_rt = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast: n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, dn {n_vec[1]-n_vec[0]:.4f}); "
      f"Vtg {Vtg_vec[0]:+.4f} .. {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} .. {Vbg_vec[-1]:+.4f} V; roundtrip max|D| {np.abs(_D_rt).max():.1e} V/nm")

# --- slow: uniform in 1/B (d(1/B) = 0.0101 /T, Nyquist ~50 T) 1.0 -> 3.1 T, then uniform 0.1 T 3.2 -> 10 T ---
B_vec = np.round(np.hstack((field_invB(1.0, 3.1, 68), np.arange(3.2, 10.0001, 0.1))), 4)
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
print(f"slow: B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows (68 uniform-1/B to 3.1 T, then 0.1 T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05, handoff left 0 T), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0

# --- lock-ins: state0 restore left sr1 at 2 uV; fixed 100 uV = 10 kOhm FS at 10 nA for the whole fan (no mid-row autorange) ---
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V @ {sr1.frequency()} Hz -> {sr1.amplitude()/100e6*1e9:.1f} nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); "
      f"sr0 sens {sr0.sensitivity()} V; tau {sr1.time_constant()} s / {sr1.filter_slope()} dB")
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP, T_TRIP = 1e-9, 3.0
tripped = []

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: n fast {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 (150, run-5 cal) co-swept (Vtg, Vbg); "
                  f"B slow 1->10 T (68 uniform-1/B to 3.1 T + 0.1 T to 10 T, 137 rows); Vsi 0; sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 cm^-2, 150 pts, fast = co-swept (k_tg.volt, k_bg.volt) along D = 0; '
              f'B 1 -> 10 T, 137 rows (uniform 1/B 1-3.1 T, 0.1 T 3.2-10 T); cal run 5: c_tg {CAL["c_tg"]:.3e}, c_bg {CAL["c_bg"]:.3e}, '
              f'n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm (density scale uncalibrated, ~11 % high per runs 6/7); '
              f'Vsi 0; sr1 100 uV fixed; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; tau 0.3 s / 24 dB')

# gates to the fan start at B = 0, then the field to the first row
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
print(f"gates at fan start: Vtg {k_tg.volt():+.4f}, Vbg {k_bg.volt():+.4f}; ramping field {magnet.field():+.3f} -> {B_vec[0]} T (~7.5 min, blocking)")
magnet.field(float(B_vec[0]))
print(f"field at {magnet.field():+.4f} T")

# row layout: [time, magnet_field(slow), k_tg.volt, k_bg.volt (fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot(k_tg.volt, k_tg.curr); s.plot(k_tg.volt, k_bg.curr); s.plot('time', T_sample)
_F0 = 4   # first followed column

def guard(station, data):
    T, i_tg, i_bg = float(data[_F0]), abs(float(data[_F0 + 1])), abs(float(data[_F0 + 2]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        tripped.append(("leak", float(data[1]), float(data[2]), float(data[3]))); station.interrupt_requested = True
    elif T > T_TRIP:
        print(f"T TRIP at B={float(data[1]):+.3f} T: T_sample = {T:.3f} K > {T_TRIP} K")
        tripped.append(("T", float(data[1]), T)); station.interrupt_requested = True
s.register_run_after(guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    if any(t[0] == "leak" for t in tripped):
        print("leak trip -> parking gates at 0 (field held where it is)")
        s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end state: B = {magnet.field():+.4f} T, Vtg = {k_tg.volt():+.4f}, Vbg = {k_bg.volt():+.4f}, T = {T_sample():.3f} K; trips: {tripped}")
# Normal completion: field stays at 10 T and gates at the fan's e-side end — plan step 5 rides the field down from here.
