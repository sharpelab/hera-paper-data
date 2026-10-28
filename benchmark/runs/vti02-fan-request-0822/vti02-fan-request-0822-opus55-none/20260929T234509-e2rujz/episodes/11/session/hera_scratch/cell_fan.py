# === D = 0 Landau fan (`landau-fan`): n fast along the D = 0 line [-1.2, +3.2]e12 (101 pts) x B slow 0.5 -> 10 T (121 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = 9.5 nm prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D_FAN = 0.0                                              # V/nm
n_vec = np.round(np.linspace(-1.2, 3.2, 101), 4)         # 1e12 cm^-2, 0.044e12 step; endpoints = runs 7 / 6 spot densities
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.full_like(n_vec, D_FAN), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_nchk, n_vec, atol=1e-6) and np.allclose(_Dchk, D_FAN, atol=1e-6)
print(f"fast line D = {D_FAN}: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts); "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V")
# --- field grid: 1/B-uniform where SdH needs it, uniform-B at high field (never re-traverse: 0 -> 10 T, ends at 10 T) ---
B_lo_seg = 1 / np.arange(2.0, 1.0 - 1e-9, -0.05)         # 0.5 -> 1 T, d(1/B) = 0.05  (light tone F ~ 7 T: 3+ pts/period)
B_mid_seg = 1 / np.arange(1.0, 0.2 - 1e-9, -0.01)        # 1 -> 5 T,  d(1/B) = 0.01  (Nyquist 50 T > F_L(3.2e12) = 33 T)
B_hi_seg = np.arange(5.25, 10.0 + 1e-9, 0.25)            # 5.25 -> 10 T, 0.25 T     (QH regime, fan lines resolved along n)
B_vec = np.unique(np.round(np.hstack((B_lo_seg, B_mid_seg, B_hi_seg)), 4))
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"B grid: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T ascending; dB {np.diff(B_vec).min()*1e3:.0f}-{np.diff(B_vec).max()*1e3:.0f} mT")
# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {T_vaporizer():.3f} K, B = {_B0:+.4f} T (|B|<0.05: handoff left 0 T), "
      f"V_si = {k_si():+.3f} V (0), heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"tau {sr1.time_constant()} s / {sr1.filter_slope()} dB (0.3/24)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} off base"
assert abs(_B0) < 0.05, f"magnet not at 0: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "heaters not off"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24, "lock-in tau/slope differ from the run-5 dwell calibration"
FAST_DELAY, SLOW_DELAY = 1.0, 3.0        # same dwell as run 5 (tau 0.3 s / 24 dB); slow_delay settles the lock-in after flyback
I_TRIP, T_TRIP = 1e-9, 2.0               # A, K — auto-abort (no operator eyes in E1)
# Fixed sensitivity for the whole fan: 500 uV = 50 kOhm FS at 10 nA. Runs 6/7 peaked 0.59 kOhm at 10 T, but the D = 0
# line crosses the CNP, where a high-B nu = 0 state can go insulating; size >= 10x the 1D peaks (session RECIPE FIX).
sr1.sensitivity(500e-6)
print(f"drive {sr1.amplitude()} V -> {sr1.amplitude()/100e6*1e9:.1f} nA; sr1 sens {sr1.sensitivity()} V; sr0 sens {sr0.sensitivity()} V; "
      f"magnet settle_s {magnet.settle_s} s")
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({len(n_vec)}) fast co-swept (Vtg, Vbg); "
                  f"B 0.5 -> 10 T ({len(B_vec)} rows; 1/B-uniform 0.5-5 T, 0.25 T above); sr1 500 uV; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_FAN:+.2f} V/nm line; n fast {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2, {len(n_vec)} pts (co-swept Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, '
              f'Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f} V); B slow 0.5 -> 10 T ascending, {len(B_vec)} rows (d(1/B) 0.05 to 1 T, 0.01 to 5 T, 0.25 T steps above); '
              f'Vsi 0; T base; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; sr1 500 uV; '
              f'cal run 5: c_tg {CAL["c_tg"]:.3e}, c_bg {CAL["c_bg"]:.3e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)
# row layout: [time, magnet_field(slow), Vtg, Vbg (fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)
def guard(station, data):
    i_tg, i_bg, T = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP or T > T_TRIP:
        print(f"GUARD TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A, T={T:.3f} K")
        station.interrupt_requested = True
s.register_run_after(guard, ())
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates to 0 at their driver pacing; the field stays where the fan left it (10 T on completion) — step 5 rides it down.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T = {T_sample():.3f} K")
