# === Step 4: Landau fan (`landau-fan-vti`) — D = 0 electron side, per-column SdH FFT ===
# n-line +2.00 -> +3.20e12 cm^-2 (44 cols) x B 0.60 -> 10.0 T uniform in 1/B (157 rows).
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior)
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_N = 2.00, 3.20, 44          # 1e12 cm^-2, ascending; last column = the run-6 spot
B_LO, B_MAX, N_B = 0.60, 10.0, 157
D0 = 0.0                                   # V/nm
FAST_DELAY, SLOW_DELAY = 1.8, 3.0          # 6 tau at tau = 0.3 s; slow_delay covers the gate flyback
I_TRIP, SENS = 1e-9, 100e-6                # gate-leakage trip; sr1 full scale (10 kOhm at 10 nA)

# --- fast axis: paired (Vtg, Vbg) n-line at fixed D = 0
ns = np.linspace(N_LO, N_HI, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns),
                                CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
_nrt, _Drt = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_Drt).max() < 1e-9, "fast axis is not a constant-D line"

# --- slow axis: uniform in 1/B (per-column SdH-FFT fan), both endpoints > 0, ascending
B_vec = field_invB(B_LO, B_MAX, N_B)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
_span = 1.0 / B_LO - 1.0 / B_MAX
_dinvB = _span / (N_B - 1)
_dn_ray = 4 * (cst.e / cst.h) * B_LO * 1e-16     # LL ray spacing at B_lo, 1e12 cm^-2
_dn = (N_HI - N_LO) / (N_N - 1)
print(f"grid: {N_B} B rows x {N_N} n cols = {N_B * N_N} pts")
print(f"  B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {_dinvB:.5f} 1/T -> F_Nyq = {1 / (2 * _dinvB):.1f} T "
      f"(needs > 2*f_heavy = 44.5 T); delta_F = {1 / _span:.3f} T")
print(f"  n {ns[0]:+.3f} -> {ns[-1]:+.3f}e12, dn = {_dn:.4f}e12 = {_dn_ray / _dn:.2f} pts/LL-ray at B_lo (floor 2)")
print(f"  Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} V (limits {TG_MIN:+.2f}/{TG_MAX:+.2f}); "
      f"Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V (limits {BG_MIN:+.2f}/{BG_MAX:+.2f})")
assert 1 / (2 * _dinvB) > 44.5 and _dn_ray / _dn >= 2.0, "grid Nyquist check failed"

# --- preconditions (assumed, not set)
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.02 at entry), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
print(f"  sr1 tau = {_tau} s at {_slope} dB/oct -> fast_delay {FAST_DELAY} s = {FAST_DELAY / _tau:.1f} tau; "
      f"volt.step tg/bg = {k_2400_tg.volt.step}/{k_2400_bg.volt.step} V (operator-owned, read only)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.02 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert _tau == 0.3 and _slope == 24, f"lock-in settling changed: tau={_tau}, slope={_slope}"

# --- fixed sensitivity for the whole fan (no autorange mid-row). Worst corner is low n x high B.
sr1.sensitivity(SENS)
_Ifs = sr1.amplitude() / 100e6
print(f"drive {sr1.amplitude()} V -> I_bias {_Ifs * 1e9:.2f} nA; sr1 sens {sr1.sensitivity()} V "
      f"= {SENS / _Ifs / 1e3:.1f} kOhm full scale; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti: D = {D0:+.2f} V/nm, n = {N_LO:+.2f} to {N_HI:+.2f}e12 ({N_N} cols), "
                  f"B = {B_LO} to {B_MAX} T uniform in 1/B ({N_B} rows, d(1/B) = {_dinvB:.5f}), "
                  f"sr1 sens {SENS * 1e6:.0f} uV, fast_delay {FAST_DELAY} s (6 tau), slow_delay {SLOW_DELAY} s; "
                  f"electron side per run 6/7 spot checks; cal run 5")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {N_LO:+.2f} to {N_HI:+.2f}e12 cm^-2 ({N_N} cols, dn = {_dn:.4f}e12), '
              f'B = {B_LO} to {B_MAX} T ascending, uniform in 1/B ({N_B} rows, d(1/B) = {_dinvB:.5f} 1/T, '
              f'F_Nyq = {1 / (2 * _dinvB):.1f} T, delta_F = {1 / _span:.3f} T); Vsi = 0; sr1 {SENS * 1e6:.0f} uV; '
              f'cal run 5: ratio {CAL["c_bg"] / CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f}; step-4 fan of tetralayer-stacking-fs-count, electron side')

# --- position: gates to the first n column, then the magnet to B_lo (blocking set == the settle)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
magnet.field(B_LO)
print(f"positioned: B = {magnet.field():+.4f} T (target {B_LO}), (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', T_sample); s.plot('time', sr1.P); s.plot('time', sr0.P)

_trip = dict(clip=0, warm=0)

def fan_guard(station, data):
    """Per-point guards: gate leakage, lock-in clipping, fridge excursion."""
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    # clipping is unrecoverable in the FFT (flat-topped columns) -> abort rather than bank it
    if abs(float(data[9])) > 0.95 * SENS:
        _trip["clip"] += 1
        if _trip["clip"] == 1 or _trip["clip"] % 5 == 0:
            print(f"CLIP WARN #{_trip['clip']} at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
                  f"sr1_X={float(data[9]):.3e} V vs FS {SENS:.0e}")
        if _trip["clip"] >= 10:
            print("CLIP TRIP: 10 consecutive points >95% full scale — sensitivity under-ranged the worst corner")
            station.interrupt_requested = True
    else:
        _trip["clip"] = 0
    _T = float(data[4])
    if _T > 1.8:
        _trip["warm"] += 1
        if _trip["warm"] >= 20:
            print(f"TEMP TRIP: 20 consecutive points with T_sample = {_T:.3f} K > 1.8 K")
            station.interrupt_requested = True
    else:
        _trip["warm"] = 0

s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)

# Gates stay at the n_max column (the run-6 spot density) and the field at 10 T: the endpoint
# for the follow-on (LK mass split) is decided after the fan is read, not blind. No park here.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
      f"T_sample = {T_sample():.3f} K")
