# === Landau fan at D = 0 (`landau-fan`): Rxx over (n, B). n fast along the
# === calibrated D = 0 line, B slow and uniform in 1/B, 1.0 -> 10.0 T ascending.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: D = 0 line, n = -1.20 .. +3.20e12 cm^-2 (validator-limited span is -1.27 .. +3.27) ---
n_vec = np.round(np.arange(-1.20, 3.2001, 0.04), 4)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"],
                                      CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.round(Vtg_vec, 5), np.round(Vbg_vec, 5)
_tg_ok = (Vtg_vec >= TG_MIN) & (Vtg_vec <= TG_MAX)
_bg_ok = (Vbg_vec >= BG_MIN) & (Vbg_vec <= BG_MAX)
assert _tg_ok.all() and _bg_ok.all(), (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_D = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])[1]
print(f"fast axis: {len(n_vec)} pts, n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 (dn {n_vec[1]-n_vec[0]:.3f}); "
      f"Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V; "
      f"|D| <= {np.abs(_D).max():.1e} V/nm")

# --- slow axis: uniform in 1/B (SdH is periodic in 1/B -> sdh_fft needs no resample),
#     then bisect any gap wider than 0.4 T so the high-B end is still sampled as a map.
B_vec = np.round(field_invB(1.0, 10.0, 90), 4)
B_vec[0], B_vec[-1] = 1.0, 10.0
_B = list(B_vec)
while True:
    _s = np.array(sorted(_B)); _d = np.diff(_s)
    if _d.max() <= 0.4:
        break
    _i = int(np.argmax(_d)); _B.append(round(float((_s[_i] + _s[_i + 1]) / 2), 4))
B_vec = np.array(sorted(_B))
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP, (B_vec.min(), B_vec.max())
_dinv = np.abs(np.diff(1.0 / B_vec)).max()
print(f"slow axis: {len(B_vec)} rows, B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T; max d(1/B) {_dinv:.5f} 1/T "
      f"(F_Nyquist {1/(2*_dinv):.0f} T); dF resolution {1/(1/B_vec[0] - 1/B_vec[-1]):.2f} T; max dB/row {np.diff(B_vec).max():.3f} T")

# --- dwell: set by the lock-in sweep-RATE ceiling, not by a per-point settle rule.
#     sr1 is tau = 0.3 s at 24 dB/oct (4-pole) -> it averages the fast axis over
#     sigma_n ~ 2*tau*(dn/dt). Washout starts when sigma_n approaches the LL period
#     in n, dn_LL = 4eB/h (smallest at the lowest row). FAST_DELAY below keeps the
#     lowest row (1 T) at >= 80 % amplitude retention, >= 95 % above 2 T.
FAST_DELAY, SLOW_DELAY = 2.30, 3.0
_rate = (n_vec[1] - n_vec[0]) / (FAST_DELAY + 0.02)
_sig = 2 * sr1.time_constant() * _rate
_dnLL = 4 * cst.e * B_vec[0] / cst.h * 1e-16
print(f"dwell: fast_delay {FAST_DELAY} s (tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct); "
      f"dn/dt {_rate:.4f} e12/s -> sigma_n {_sig:.4f}e12 vs dn_LL(1 T) {_dnLL:.4f}e12 "
      f"-> retention {np.exp(-0.5*(2*np.pi*_sig/_dnLL)**2):.2f} at the lowest row")

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: the fan ramps up from 0), "
      f"V_si = {k_si():+.3f} V (0), Vtg = {k_tg.volt():+.4f}, Vbg = {k_bg.volt():+.4f} (0 after handoff), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
# validators still the committed ones (gate B contract)
assert (k_2400_tg.volt.vals._min_value, k_2400_tg.volt.vals._max_value) == (TG_MIN, TG_MAX)
assert (k_2400_bg.volt.vals._min_value, k_2400_bg.volt.vals._max_value) == (BG_MIN, BG_MAX)
assert magnet.field.vals._max_value == B_SESSION_CAP

# --- sensitivity: 100 uV = 10.1 kOhm full scale at 10 nA. Runs 6/7 peaked at 0.59 kOhm
#     off the CNP; the CNP columns at high B are the ones that can clip, and 100 uV is
#     the run-5 proven headroom. Noise is 0.10 % of FS/pt (run 6) = ~10 Ohm, against
#     SdH amplitudes of 100-500 Ohm.
sr1.sensitivity(100e-6)
I_TRIP, TRIP_N = 1e-9, 3          # abort only on 3 consecutive points over trip (flyback transients are single-point)
CLIP = 0.95 * sr1.sensitivity()
_ibias = sr1.amplitude() / meas_config["bias_resistor"]
print(f"drive {sr1.amplitude()} V / {meas_config['bias_resistor']:.0e} Ohm -> I_bias {_ibias*1e9:.2f} nA; "
      f"sr1 sens {sr1.sensitivity()} V -> {sr1.sensitivity()/_ibias:.0f} Ohm full scale; "
      f"leak trip {I_TRIP:.0e} A x{TRIP_N} consecutive")

_eta = len(B_vec) * (len(n_vec) * (FAST_DELAY + 0.02) + 19) + (B_vec[-1] - B_vec[0]) / 0.137 * 60 + len(B_vec) * 3
print(f"predicted wall-clock {_eta/3600:.2f} h (rows {len(B_vec)} x {len(n_vec)} = {len(B_vec)*len(n_vec)} pts)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({len(n_vec)} pts) fast, "
                  f"B {B_vec[0]:.2f}->{B_vec[-1]:.2f} T uniform-1/B ({len(B_vec)} rows) slow, sr1 100 uV, fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: fast (Vtg, Vbg) co-swept along the run-5 D = 0 line, n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2, '
              f'dn {n_vec[1]-n_vec[0]:.3f}e12, {len(n_vec)} pts; slow B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T ascending, '
              f'uniform in 1/B (d(1/B) <= {_dinv:.5f}, F_Nyq {1/(2*_dinv):.0f} T, dF {1/(1/B_vec[0]-1/B_vec[-1]):.2f} T), '
              f'{len(B_vec)} rows, gaps > 0.4 T bisected; fast_delay {FAST_DELAY} s (sr1 tau 0.3 s / 24 dB rate ceiling), '
              f'sr1 100 uV; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')

# park the gates at the first fast point before the field starts moving
s.ramp(k_bg.volt, float(Vbg_vec[0])); s.ramp(k_tg.volt, float(Vtg_vec[0]))
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_state = {"leak": 0, "clip": 0, "warm": 0}

def fan_guard(station, data):
    """Abort on sustained gate leakage; count (do not abort on) sr1 clipping and T excursions."""
    try:
        i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
        if i_tg > I_TRIP or i_bg > I_TRIP:
            _state["leak"] += 1
            if _state["leak"] >= TRIP_N:
                print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
                      f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A ({TRIP_N} consecutive)")
                station.interrupt_requested = True
        else:
            _state["leak"] = 0
        if abs(float(data[9])) >= CLIP:
            _state["clip"] += 1
            if _state["clip"] in (1, 100, 1000, 5000):
                print(f"sr1 near full scale ({_state['clip']} pts) at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}")
        if float(data[4]) > 1.6 or float(data[4]) < 0.9:
            _state["warm"] += 1
            if _state["warm"] in (1, 50, 500):
                print(f"T_sample out of band: {float(data[4]):.3f} K at B={float(data[1]):+.3f} T ({_state['warm']} pts)")
    except Exception as exc:          # a guard bug must never kill a 9 h run
        print(f"fan_guard error (ignored): {exc!r}")

s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY, init_delay=True)

# gates stay on the D = 0 line, field stays at 10 T — the next step (LK mass ladder or a
# second fan) starts from there rather than re-traversing.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
      f"T = {T_sample():.3f} K; clip pts {_state['clip']}, T-excursion pts {_state['warm']}")
