# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +1.6 -> +3.2e12, B 1.0 -> 10.0 T uniform in 1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_N = 1.6, 3.2, 41          # 1e12 cm^-2, along the D = 0 line, electron side
B_LO, B_HI, N_B = 1.0, 10.0, 145        # uniform in 1/B: d(1/B) = 1/160 /T -> f_Nyq = 80 T
FAST_DELAY, SLOW_DELAY = 1.8, 3.0       # 6 tau on the n-axis; 10 tau after each flyback
I_TRIP = 1e-9

# --- fast axis: paired (k_tg, k_bg) n-line at D = 0 ---
ns = np.linspace(N_LO, N_HI, N_N)
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
_n0, _D0 = calc_nD(Vtgs[0], Vbgs[0], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
_n1, _D1 = calc_nD(Vtgs[-1], Vbgs[-1], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"n-line: {N_N} pts, n = {N_LO:+.2f} -> {N_HI:+.2f}e12 at D = 0 "
      f"(dn = {(N_HI - N_LO) / (N_N - 1):.4f}e12 = 2.4 pts per LL ray spacing at B_lo)")
print(f"  V_tg {Vtgs.min():+.4f} -> {Vtgs.max():+.4f} V (TG limit {TG_MAX:+.2f}, margin {TG_MAX - Vtgs.max():+.4f} V); "
      f"step {np.diff(Vtgs)[0] * 1e3:.2f} mV")
print(f"  V_bg {Vbgs.min():+.4f} -> {Vbgs.max():+.4f} V (BG limit {BG_MAX:+.2f}, margin {BG_MAX - Vbgs.max():+.4f} V); "
      f"step {np.diff(Vbgs)[0] * 1e3:.2f} mV")
print(f"  roundtrip (n, D) at the ends: ({_n0:+.3f}, {_D0:+.4f}) / ({_n1:+.3f}, {_D1:+.4f})")

# --- slow axis: uniform in 1/B (per-column SdH-FFT fan; landau-fan step 4). Clip, never round:
#     rounding coarsens the worst d(1/B) and drags f_Nyq below 80 T.
B_vec = np.minimum(field_invB(B_LO, B_HI, N_B), B_SESSION_CAP)
_d_inv = np.abs(np.diff(1.0 / B_vec))
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP, (B_vec.min(), B_vec.max())
assert len(np.unique(B_vec)) == N_B
print(f"B grid: {N_B} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, dB {np.diff(B_vec).min() * 1e3:.1f} mT (low end) "
      f"-> {np.diff(B_vec).max() * 1e3:.0f} mT (high end)")
print(f"  d(1/B) = {_d_inv.max():.6f} /T -> f_Nyq = {1 / (2 * _d_inv.max()):.1f} T; "
      f"1/B span {1 / B_LO - 1 / B_HI:.3f} /T -> Rayleigh dF = {1 / (1 / B_LO - 1 / B_HI):.2f} T")
print(f"  rows per LL period: {(1 / (cst.h * N_HI * 1e16 / (4 * cst.e))) / _d_inv.max():.1f} at n_max, "
      f"{(1 / (cst.h * N_LO * 1e16 / (4 * cst.e))) / _d_inv.max():.1f} at n_min  (floor 2, prefer 3)")

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (expect ~0, must be <= B_lo), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(k_si()) < 0.01
assert _B0 <= B_LO + 0.05, f"magnet is above the fan start field ({_B0:+.4f} T) — re-plan, do not re-traverse"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()
print(f"  validators still in force: field {magnet.field.vals}, k_tg.volt {k_tg.volt.vals}, k_bg.volt {k_bg.volt.vals}")
assert magnet.field.vals.max_value == B_SESSION_CAP, magnet.field.vals
assert (k_tg.volt.vals.min_value, k_tg.volt.vals.max_value) == (TG_MIN, TG_MAX), k_tg.volt.vals
assert (k_bg.volt.vals.min_value, k_bg.volt.vals.max_value) == (BG_MIN, BG_MAX), k_bg.volt.vals

# --- lock-in: one fixed sensitivity for the whole fan (no autorange streaks; landau-fan step 3).
#     Worst corner is low n x high B: R(B=0, n=1.6e12) = 84 Ohm (run 5) x MR ~10-12 (run 6: 530/52
#     at n=3.2) + SdH maxima ~ 1.5 kOhm = 30 % of full scale. Headroom, not precision.
sr1.sensitivity(50e-6)
print(f"drive {sr1.amplitude()} V / {meas_config['bias_resistor']:.0e} Ohm -> ~10 nA; "
      f"sr1 sens {sr1.sensitivity()} V = {sr1.sensitivity() / 1e-8:.0f} Ohm FS; sr0 sens {sr0.sensitivity()} V; "
      f"tau {sr1.time_constant()} s at {sr1.filter_slope()} dB/oct -> fast_delay {FAST_DELAY} s = "
      f"{FAST_DELAY / sr1.time_constant():.1f} tau")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = 0, n = {N_LO:+.2f} -> {N_HI:+.2f}e12 ({N_N} pts), "
                  f"B {B_LO} -> {B_HI} T uniform in 1/B ({N_B} rows, d(1/B) = 1/160 /T, f_Nyq 80 T), "
                  f"fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, sr1 50 uV; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = 0: n = {N_LO:+.2f} to {N_HI:+.2f}e12 cm^-2 ({N_N} pts, paired TG/BG n-line), '
              f'B = {B_LO} to {B_HI} T ({N_B} rows, uniform in 1/B, d(1/B) = 1/160 /T -> f_Nyq 80 T); '
              f'Vsi = 0; sr1 50 uV; fast_delay {FAST_DELAY} s (6 tau), slow_delay {SLOW_DELAY} s')
s.add_comment(f'design inputs: run 6 sdh-spot-check (n = +3.2e12) tones 7.3 / 22.3 / 29.4 T, '
              f'Dingle onsets 1.0 (censored) / 1.40 / 1.76 T -> B_lo = 1.0 T; F_L(3.2e12) = 33.1 T; '
              f'cal run 5: ratio {CAL["c_bg"] / CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f}')

# --- position: gates to the first column, then the magnet to the fan start ---
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
print(f"gates at column 0: (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V; "
      f"ramping magnet {_B0:+.3f} -> {B_LO} T (~{(B_LO - _B0) / 0.137:.1f} min, blocking)")
s.ramp(magnet.field, B_LO)
print(f"magnet at {magnet.field():+.4f} T; starting fan "
      f"({N_B} rows x {N_N} pts = {N_B * N_N} points)")

# row layout: [time, magnet_field, k_tg.volt, k_bg.volt, T_sample, k_tg.curr, k_bg.curr,
#              sr0.X, sr0.P, sr1.X, sr1.P]   (multimegasweep: time + slow + fast + fp order)
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', sr1.P); s.plot('time', sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', T_sample)


def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True


def rail_guard(station, data):
    # a railed column is unrecoverable for the FFT (flat-topped -> harmonics); kill early.
    if abs(float(data[9])) >= 0.95 * sr1.sensitivity():
        print(f"RAIL TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"sr1_X={float(data[9]):.3e} V >= 0.95 x {sr1.sensitivity()} V FS")
        station.interrupt_requested = True


s.register_run_after(leak_guard, ())
s.register_run_after(rail_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # park the gates; leave the field at 10 T deliberately - the LK mass ladder
    # (temperature-dependence-vti Flavor B) rides it back down, never re-traversing.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, "
          f"T_sample = {T_sample():.3f} K")
