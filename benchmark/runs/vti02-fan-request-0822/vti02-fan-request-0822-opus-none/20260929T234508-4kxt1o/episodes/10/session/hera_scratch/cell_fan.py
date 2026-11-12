# === Landau fan (`landau-fan`): D = 0 line n = -1.20 .. +3.20e12 (fast) x B = 0 -> 10 T (slow) ===
# Plan step 4. Fast axis co-sweeps (Vtg, Vbg) along D = 0 so every fast point is a pure
# density move; slow axis is the blocking magnet. Ends at 10 T, gates at n = +3.20e12.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_FAST, D_FAN = 119, 0.0
n_vec = np.linspace(-1.20, 3.20, N_FAST)                      # 1e12 cm^-2; endpoints = the run 6 / run 7 spot densities
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.full_like(n_vec, D_FAN),
                                      CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
B_vec = np.round(np.arange(0.0, 10.0001, 0.125), 4)           # 81 rows, uniform in B
FAST_DELAY, SLOW_DELAY = 1.5, 2.0
I_TRIP = 1e-9

# --- SAFETIES still fencing? (software only: vals.validate touches no hardware) ---
def _fence(param, lo, hi, name):
    param.vals.validate(lo); param.vals.validate(hi)
    for bad in (lo - 1e-3, hi + 1e-3):
        try:
            param.vals.validate(bad)
        except Exception:
            continue
        raise AssertionError(f"SAFETIES: {name} validator does not reject {bad}")
_fence(k_2400_tg.volt, TG_MIN, TG_MAX, "k_tg.volt")
_fence(k_2400_bg.volt, BG_MIN, BG_MAX, "k_bg.volt")
_fence(dc205.smart_voltage, SI_MIN, SI_MAX, "k_si")
_fence(magnet.field, -B_SESSION_CAP, B_SESSION_CAP, "magnet.field")
print(f"SAFETIES re-checked: tg [{TG_MIN}, {TG_MAX}], bg [{BG_MIN}, {BG_MAX}], si [{SI_MIN}, {SI_MAX}], |B| <= {B_SESSION_CAP} T")

# --- the swept vectors live inside those fences, with margin ---
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() >= 0.0
_D_rt = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])[1]
assert np.abs(_D_rt).max() < 1e-9, "fast axis is not on the D = 0 line"
print(f"fast: n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 ({N_FAST} pts, dn {n_vec[1]-n_vec[0]:.4f}e12) at D = {D_FAN:+.2f} V/nm")
print(f"      Vtg {Vtg_vec.min():+.4f} .. {Vtg_vec.max():+.4f} V (margin {1e3*(Vtg_vec.min()-TG_MIN):.0f} / {1e3*(TG_MAX-Vtg_vec.max()):.0f} mV), "
      f"Vbg {Vbg_vec.min():+.4f} .. {Vbg_vec.max():+.4f} V (margin {1e3*(Vbg_vec.min()-BG_MIN):.0f} / {1e3*(BG_MAX-Vbg_vec.max()):.0f} mV)")
print(f"slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {len(B_vec)} rows, dB {B_vec[1]-B_vec[0]:.3f} T")

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: fan starts at 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm full scale at 10 nA.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V / {sr1.frequency()} Hz -> {sr1.amplitude()/100e6*1e9:.2f} nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), "
      f"tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct -> fast_delay {FAST_DELAY} s = {FAST_DELAY/sr1.time_constant():.1f} tau; sr0 sens {sr0.sensitivity()} V")
_pred = len(B_vec) * (N_FAST * (FAST_DELAY + 0.15) + (B_vec[1] - B_vec[0]) / 0.137 * 60 + 3 + SLOW_DELAY + 3.5)
print(f"predicted wall-clock {_pred/3600:.2f} h (+8% -> {_pred*1.08/3600:.2f} h)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan: D = 0 line, n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({N_FAST} pts) fast, "
                  f"B 0 -> 10 T ({len(B_vec)} rows, 125 mT) slow, sr1 100 uV, fast_delay {FAST_DELAY} s; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_FAN:+.2f} V/nm; fast (Vtg, Vbg) co-swept along D = 0: n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 cm^-2, {N_FAST} pts '
              f'(dn {n_vec[1]-n_vec[0]:.4f}e12), Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f}; '
              f'slow B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T uniform {B_vec[1]-B_vec[0]:.3f} T, {len(B_vec)} rows; T ~ {_T0:.2f} K; Vsi = 0; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e} F/m2 (geometry prior), n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.4f}; '
              f'fan endpoints = the run 6 / run 7 spot densities')

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
# (followed + plotted before anything moves, so a bad plot spec fails with the rig untouched)
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

_t0 = time.time()
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # No park: the field stays at 10 T and the gates at the last fast point (n = +3.20e12) —
    # plan step 5a starts there and rides the magnet down. Never re-traverse.
    _el = time.time() - _t0
    print(f"elapsed {_el/3600:.2f} h (predicted {_pred/3600:.2f} h, {100*(_el/_pred-1):+.0f}%); "
          f"B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
