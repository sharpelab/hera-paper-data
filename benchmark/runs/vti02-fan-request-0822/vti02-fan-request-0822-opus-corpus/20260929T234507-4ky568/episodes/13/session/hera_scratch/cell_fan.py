# === Step 4: Landau fan at D = 0, electron side (`landau-fan-vti`) ===
# n = +3.20 -> +1.50e12 cm^-2 (50 columns) x B = 0.8 -> 10 T uniform in 1/B (117 rows).
# Per-column SdH FFT read: ABAB pair partitioning F_L vs ABCA singleton at F_L.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import luttinger_frequency

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: paired (Vtg, Vbg) n-line at D = 0, high n -> low n so the gates
#     sit at the LOW-|V| end during each (blocking, up to 7 min) field ramp ---
N_HI, N_LO, N_N, D0 = 3.20, 1.50, 50, 0.0          # 1e12 cm^-2, V/nm
ns = np.linspace(N_HI, N_LO, N_N)
Ds = D0 * np.ones(N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, **CAL)
assert TG_MIN <= Vtgs.min() and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert BG_MIN <= Vbgs.min() and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
_vt, _vb = sanitize_tg_bg(Vtgs, Vbgs, tg_lims, bg_lims)
assert len(_vt) == N_N, f"n-line clipped by the operating limits: {len(_vt)}/{N_N}"
print(f"fast axis: n {N_HI:+.2f} -> {N_LO:+.2f}e12 at D = {D0:+.2f} V/nm, {N_N} cols, dn = {abs(ns[1]-ns[0]):.4f}e12; "
      f"Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} ({1e3*(TG_MAX-Vtgs.max()):.0f} mV under TG_MAX), Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f}")
print(f"  roundtrip (n, D): {calc_nD(Vtgs[0], Vbgs[0], **CAL)} ... {calc_nD(Vtgs[-1], Vbgs[-1], **CAL)}")

# --- slow axis: uniform in 1/B (per-column SdH FFT), ascending from where the magnet sits ---
B_LO, B_HI, N_B = 0.8, 10.0, 117
B_vec = np.round(field_invB(B_LO, B_HI, N_B), 4)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP, (B_vec.min(), B_vec.max())
_d = np.abs(np.diff(1.0 / B_vec))
FL_max = float(luttinger_frequency(N_HI * 1e16))                       # F_L at n_max, Tesla
assert _d.max() <= 1.0 / (3 * FL_max), f"1/B grid coarser than the 1/3 target: {_d.max():.5f} > {1/(3*FL_max):.5f}"
_span = 1.0 / B_vec[0] - 1.0 / B_vec[-1]
# n-axis ray Nyquist at the lowest field (finest LL ray spacing), g = 4:
_dn_ray = 4 * (cst.e / cst.h) * B_vec[0] / 1e16                        # 1e12 cm^-2
print(f"slow axis: {N_B} rows, B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T uniform-1/B; "
      f"d(1/B) {_d.min():.5f}-{_d.max():.5f} 1/T (Nyquist {1/(2*_d.max()):.1f} T vs F_L(n_max) {FL_max:.1f} T)")
print(f"  1/B span {_span:.4f} 1/T -> dF = {1/_span:.2f} T (2dF = {2/_span:.2f} T; B-window-split halves dF = {2/_span:.2f} T)")
print(f"  ray Nyquist at B_lo: dn_ray = {_dn_ray:.4f}e12 -> {_dn_ray/abs(ns[1]-ns[0]):.1f} pts/ray (floor 2)")
print(f"  dB row spacing {np.diff(B_vec).min()*1e3:.1f} mT (at {B_vec[0]:.2f} T) -> {np.diff(B_vec).max()*1e3:.0f} mT (at {B_vec[-1]:.2f} T); "
      f"traverse {(B_vec[-1]-B_vec[0])/0.137:.0f} min bare")

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.1: ramping up from ~0), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.1 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not at 1"
# SAFETIES still committed on this kernel (gate B is a per-measurement-cell gate):
print(f"  validators: k_tg {k_2400_tg.volt.vals}, k_bg {k_2400_bg.volt.vals}, magnet {magnet.field.vals}")
assert repr(k_2400_tg.volt.vals) == repr(validators.Numbers(TG_MIN, TG_MAX)), "TG validator not the committed fence"
assert repr(k_2400_bg.volt.vals) == repr(validators.Numbers(BG_MIN, BG_MAX)), "BG validator not the committed fence"
assert repr(magnet.field.vals) == repr(validators.Numbers(-B_SESSION_CAP, B_SESSION_CAP)), "field cap not the committed fence"

# --- lock-in: one fixed sensitivity for the whole fan (no autorange mid-row).
#     50 uV = 5 kOhm full scale at 10 nA; worst corner (n_min x B_max) ~0.9-1.2 kOhm = ~20 % FS.
sr1.sensitivity(50e-6)
print(f"drive {sr1.amplitude()} V / {meas_config['bias_resistor']:.0e} Ohm; sr1 sens {sr1.sensitivity()} V (5 kOhm FS), "
      f"tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct -> fast_delay 1.8 s = 6 tau; sr0 sens {sr0.sensitivity()} V")

FAST_DELAY, SLOW_DELAY = 1.8, 2.0
print(f"est. wall-clock: traverse {(B_vec[-1]-B_vec[0])/0.137:.0f} min + grid {N_B*N_N*(FAST_DELAY+0.12)/60:.0f} min "
      f"+ row overhead {N_B*6/60:.0f} min ~ {((B_vec[-1]-B_vec[0])/0.137 + N_B*N_N*(FAST_DELAY+0.12)/60 + N_B*6/60)/60:.2f} h")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti: D = {D0:+.2f} V/nm, n = {N_HI:+.2f} -> {N_LO:+.2f}e12 ({N_N} cols), "
                  f"B = {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T uniform-1/B ({N_B} rows), sr1 50 uV, "
                  f"fast_delay {FAST_DELAY} s / slow_delay {SLOW_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = {D0:+.2f} V/nm; n = {N_HI:+.2f} to {N_LO:+.2f}e12 cm^-2, {N_N} cols, dn = {abs(ns[1]-ns[0]):.4f}e12; '
              f'B = {B_vec[0]:.2f} to {B_vec[-1]:.2f} T uniform in 1/B, {N_B} rows, d(1/B) = {_d.mean():.5f} 1/T '
              f'(Nyquist {1/(2*_d.max()):.1f} T vs F_L(n_max) {FL_max:.1f} T); dF = {1/_span:.2f} T; '
              f'Vtg {Vtgs[0]:+.4f} to {Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f} to {Vbgs[-1]:+.4f}; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.add_comment('step 4 of investigations/tetralayer-stacking-fs-count; onset + tones + settling inherited from sdh-spot-check run 6 '
              '(onset_b 0.30 T censored, fundamental 7.1 T); top column n = +3.20e12 reproduces run 6 on a changed grid (uniform-1/B vs uniform-B)')

# --- position: gates to the fast-axis start, then the magnet (blocking ~6 min from 0 T) ---
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
s.ramp(magnet.field, B_vec[0])
interruptible_sleep(10)
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")

# row layout: [time, B, Vtg, Vbg, T_sample, I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, magnet.field, sr1.X)      # the fan itself (Rxx)
s.plot(k_tg.volt, magnet.field, sr0.X)      # drain current over the same plane
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)   # live leakage, both gates
s.plot('time', T_sample)                    # base-T hold across a 4.5 h run
s.plot('time', sr1.P); s.plot('time', sr0.P)

# --- guards: 3 consecutive violations to trip, so the row-start gate flyback
#     transient (session note, runs 4/5: +-110 pA single-point excursions) cannot false-fire ---
I_TRIP, T_TRIP_LO, T_TRIP_HI, N_STRIKE = 1e-9, 1.0, 1.6, 3
_strikes = {"leak": 0, "temp": 0}

def fan_guard(station, data):
    t_s = float(data[4]); i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    _strikes["leak"] = _strikes["leak"] + 1 if (i_tg > I_TRIP or i_bg > I_TRIP) else 0
    _strikes["temp"] = _strikes["temp"] + 1 if not (T_TRIP_LO <= t_s <= T_TRIP_HI) else 0
    if _strikes["leak"] >= N_STRIKE:
        print(f"LEAK TRIP at B = {float(data[1]):+.3f} T, Vtg = {float(data[2]):+.4f} V: "
              f"|I_tg| = {i_tg:.3e}, |I_bg| = {i_bg:.3e} A ({N_STRIKE} consecutive)")
        station.interrupt_requested = True
    if _strikes["temp"] >= N_STRIKE:
        print(f"TEMP TRIP at B = {float(data[1]):+.3f} T: T_sample = {t_s:.3f} K outside "
              f"[{T_TRIP_LO}, {T_TRIP_HI}] K ({N_STRIKE} consecutive)")
        station.interrupt_requested = True

s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)

# Ends at 10 T with the gates at n = +1.50e12 — the LK mass series rides the magnet down. No park here.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
