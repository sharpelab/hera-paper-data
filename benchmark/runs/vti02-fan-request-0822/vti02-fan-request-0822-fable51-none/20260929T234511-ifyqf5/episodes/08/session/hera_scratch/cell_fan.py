# === Landau fan along D = 0 (`landau-fan`): (Vtg, Vbg) co-swept fast along the calibrated D = 0 line, B slow 1 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D_FAN = 0.0                                                   # V/nm
n_req = np.round(np.arange(-1.3, 3.5001, 0.025), 4)           # 1e12 cm^-2, 0.025 steps; clipped to the committed box below
Vt_all, Vb_all = calc_gate_voltages(n_req, np.full_like(n_req, D_FAN), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = sanitize_tg_bg(Vt_all, Vb_all, tg_lims, bg_lims)   # drops the out-of-box ends (monotonic line -> ends only)
n_fast, D_fast = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
assert np.all(np.diff(Vtg_vec) > 0) and np.all(np.diff(Vbg_vec) > 0) and np.abs(D_fast).max() < 1e-6
print(f"fast axis: {len(Vtg_vec)} pts along D = {D_FAN:+.2f} V/nm, n = {n_fast.min():+.3f} .. {n_fast.max():+.3f} e12 (step 0.025); "
      f"Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V")

# --- slow axis: uniform in B, ascending from where the magnet sits (0 T) -> ends at 10 T (next step rides it down)
B_vec = np.round(np.arange(1.0, 10.0001, 0.2), 4)             # 46 rows
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 1 T from 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 1.0, 3.0     # run-5 calibrated: 1.17 s/pt at fast_delay 1 s (tau 0.3 s, 24 dB)
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange mid-row): 200 uV = 20 kOhm full scale at 10 nA.
# Runs 6/7 peaked at ~590 Ohm at 10 T away from the CNP; nu = 0 at 10 T may be insulating -> headroom over the run-5 choice.
sr1.sensitivity(200e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (20 kOhm FS), tau {sr1.time_constant()} s; sr0 sens {sr0.sensitivity()} V; "
      f"B grid {len(B_vec)} rows {B_vec[0]} -> {B_vec[-1]} T (0.2 T); magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = {D_FAN:+.2f} V/nm: fast (Vtg, Vbg) co-swept {len(Vtg_vec)} pts n {n_fast.min():+.3f}..{n_fast.max():+.3f} e12 (run-5 cal), "
                  f"slow B {B_vec[0]} -> {B_vec[-1]} T step 0.2 ({len(B_vec)} rows), sr1 200 uV, Vsi 0, T ~1.2 K")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_FAN:+.2f} V/nm line; fast (Vtg, Vbg) co-swept {len(Vtg_vec)} pts, n = {n_fast.min():+.3f} .. {n_fast.max():+.3f} e12 cm^-2 step 0.025 '
              f'(Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f}, Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V); '
              f'slow B {B_vec[0]} -> {B_vec[-1]} T uniform 0.2 T ({len(B_vec)} rows); fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; sr1 200 uV; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e} (geometry prior), n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # gates parked at 0; field stays where the fan ends (10 T) — never re-traverse
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
