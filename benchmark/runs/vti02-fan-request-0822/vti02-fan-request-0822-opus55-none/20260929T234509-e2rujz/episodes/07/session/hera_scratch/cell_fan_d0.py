# === Landau fan at D = 0 (`landau-fan`): B slow 1 -> 10 T x n fast along D = 0, -1.25 .. +3.25e12 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB
# --- session calibration from run 5 (ratio data-calibrated, c_tg = geometry prior; this fan checks the absolute scale) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.25, 3.25 + 1e-9, 0.03), 4)          # 1e12 cm^-2, 151 pts
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_nr, _Dr = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_nr, n_vec, atol=1e-6) and np.allclose(_Dr, 0, atol=1e-6)
# --- field rows: uniform in 1/B 1 -> 4 T (85 rows, d(1/B) = 0.0089 /T), then 0.15 T steps 4.15 -> 10 T (40 rows) ---
B_vec = np.hstack([field_invB(1.0, 4.0, 85), np.round(np.arange(4.15, 10.0001, 0.15), 4)])
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP and len(B_vec) == 125
print(f"fast: n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, D = 0); Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f}, "
      f"Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V | slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T ({len(B_vec)} rows)")
# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_hs, _hv = heater.sample_range(), heater.vaporizer_range()
_amp, _frq, _tau, _s0 = sr1.amplitude(), sr1.frequency(), sr1.time_constant(), sr0.sensitivity()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5) | B = {_B0:+.4f} T (|B|<0.05) | V_si = {k_si():+.3f} V (0) | "
      f"heater ranges {_hs}/{_hv} (0/0) | nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1) | volt.step {k_tg.volt.step}/{k_bg.volt.step} (0.005) | "
      f"PS {magnet.persistent_switch_on()} out {magnet.output_enabled()} | drive {_amp} V @ {_frq:.3f} Hz (1.0 @ 13.777), "
      f"tau {_tau} s (0.3), sr0 sens {_s0} (0.02)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} off base"
assert abs(_B0) < 0.05, f"field not at 0: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert _hs == 0 and _hv == 0, "heaters not off"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert k_tg.volt.step == 0.005 and k_bg.volt.step == 0.005
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(_amp - 1.0) < 1e-3 and abs(_frq - 13.777) < 0.01 and _tau == 0.3 and _s0 == 0.02, "lock-in drive/tau/sr0 not as calibrated"
# --- lock-in: fixed sensitivity for the whole fan (no mid-row autorange). 100 uV = 10 kOhm FS at 10 nA ---
sr1.sensitivity(100e-6)
FAST_DELAY, SLOW_DELAY = 0.6, 3.0
I_TRIP, T_TRIP, B_TOL = 1e-9, 2.0, 0.02
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 x {len(n_vec)} (0.03e12) along D=0 (run-5 cal); "
                  f"B 1->4 T uniform 1/B (85) + 4.15->10 T 0.15 T (40); fast_delay {FAST_DELAY}, slow_delay {SLOW_DELAY}; sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan; fast: n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 cm^-2, {len(n_vec)} pts (co-swept k_tg/k_bg along D = 0); '
              f'slow: B 1.0 -> 4.0 T uniform in 1/B (85 rows) + 4.15 -> 10.0 T at 0.15 T (40 rows); Vsi = 0; '
              f'cal run 5: c_tg {CAL["c_tg"]:.3e} (prior), c_bg {CAL["c_bg"]:.3e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm')
# park gates at the first fan point, then pre-ramp the field 0 -> 1 T (blocks ~7.5 min)
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
s.ramp(magnet.field, B_vec[0])
print(f"at start: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}); sr1 sens {sr1.sensitivity()} V (10 kOhm FS)")
# row layout: [time, B(set), Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', T_sample); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
_guard = {"B": None, "trips": []}
def fan_guard(station, data):
    B_set, T, i_tg, i_bg = float(data[1]), float(data[4]), abs(float(data[5])), abs(float(data[6]))
    msg = None
    if B_set != _guard["B"]:                       # first point of a new row: field read-truth check
        _guard["B"] = B_set
        B_rd = magnet.field()
        if abs(B_rd - B_set) > B_TOL:
            msg = f"FIELD MISMATCH row B_set={B_set:.4f}: readback {B_rd:+.4f} T"
    if i_tg > I_TRIP or i_bg > I_TRIP:
        msg = f"LEAK TRIP at B={B_set:.3f}, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A"
    if T > T_TRIP:
        msg = f"T TRIP at B={B_set:.3f}: T_sample={T:.3f} K > {T_TRIP} K"
    if msg:
        print(msg); _guard["trips"].append(msg); station.interrupt_requested = True
s.register_run_after(fan_guard, ())
s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY, init_delay=True)
# field stays at 10 T (step 5 rides it down); gates stay at the last fan point (n = +3.25e12, D = 0), in-box.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K, trips: {_guard['trips']}")
