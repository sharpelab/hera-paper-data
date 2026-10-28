# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +2.10 -> +3.22e12, B 0.7 -> 7.5 T ===
# Per-column SdH-FFT fan: B slow (uniform in 1/B), paired (k_tg, k_bg) n-line fast at fixed D = 0.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

N_LO, N_HI, N_N = 2.10, 3.22, 47          # 1e12 cm^-2; n_hi = TG ceiling at D = 0, n_lo = 5-period floor on f1
B_LO, B_MAX, N_B = 0.70, 7.50, 132        # T; uniform in 1/B, d(1/B) = 1/(3 F_L(n_max))
D0 = 0.0                                  # V/nm — the investigation's operating point
FAST_DELAY, SLOW_DELAY = 1.8, 1.0         # 1.8 s = 6 tau at tau = 0.3 s / 24 dB/oct
I_TRIP = 1e-9

ns = np.linspace(N_LO, N_HI, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"],
                                CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
_nD_lo, _nD_hi = (calc_nD(Vtgs[0], Vbgs[0], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]),
                  calc_nD(Vtgs[-1], Vbgs[-1], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]))
print(f"n-line: {N_N} pts, n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = {D0:+.2f} V/nm; "
      f"Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} V (TG headroom {TG_MAX - Vtgs.max():+.4f} V), "
      f"Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V; roundtrip ends {_nD_lo} {_nD_hi}")

# --- field grid: uniform in 1/B (per-column SdH-FFT fan), ascending; magnet starts at 0 T ---
B_vec = np.round(1.0 / np.linspace(1.0 / B_LO, 1.0 / B_MAX, N_B), 4)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
_dinv = abs(np.median(np.diff(1.0 / B_vec)))
_F_L_max = abs(ns[-1]) * 1e16 * cst.h / (4 * cst.e)
print(f"B grid: {len(B_vec)} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T; d(1/B) = {_dinv:.5f} 1/T "
      f"(Nyquist F = {1/(2*_dinv):.1f} T vs F_L(n_max) = {_F_L_max:.1f} T); "
      f"dB {np.diff(B_vec).min()*1e3:.1f} -> {np.diff(B_vec).max()*1e3:.0f} mT; "
      f"1/B span {1/B_LO - 1/B_MAX:.4f} 1/T -> dF = {1/(1/B_LO - 1/B_MAX):.2f} T")
print(f"n-axis: dn = {(ns[1]-ns[0]):.4f}e12 vs LL ray {4*cst.e/cst.h*B_LO/1e16:.4f}e12 at B_lo "
      f"-> {(4*cst.e/cst.h*B_LO/1e16)/(ns[1]-ns[0]):.2f} pts/ray")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05 at entry), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# Sensitivity inherited from the spot checks (runs 6/7): 50 uV = 5 kOhm FS at 10 nA.
# Worst corner is low-n x high-B (run 7 peaked 587 Ohm, run 6 530 Ohm) -> ~8x headroom. Fixed for the whole fan.
sr1.sensitivity(50e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (5 kOhm FS); "
      f"sr0 sens {sr0.sensitivity()} V; tau {sr1.time_constant()} s / {sr1.filter_slope()} dB "
      f"-> fast_delay {FAST_DELAY} s = {FAST_DELAY/sr1.time_constant():.0f} tau")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan electron side: n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 at D = {D0:+.2f} V/nm, "
                  f"B {B_LO} -> {B_MAX} T uniform-1/B {N_B} rows x {N_N} n-pts, "
                  f"fast_delay {FAST_DELAY} s (6 tau), sr1 50 uV; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 ({N_N} pts), '
              f'B = {B_LO} to {B_MAX} T ({N_B} rows, uniform in 1/B, d(1/B) = {_dinv:.5f} 1/T); '
              f'per-column SdH-FFT fan for tetralayer-stacking-fs-count Step 4; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f}; sr1 50 uV, fast_delay {FAST_DELAY} s = 6 tau')

# position: gates onto the n-line start, then the magnet to B_lo (FastBi1K5 set blocks through the ramp)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
magnet.field(B_LO)
_Bstart = magnet.field()
print(f"positioned: B = {_Bstart:+.4f} T (target {B_LO}), (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V")
assert abs(_Bstart - B_LO) < 0.02, f"magnet did not reach B_lo: {_Bstart}"

# row layout: [time, magnet_field(slow), k_tg_volt, k_bg_volt(fast), T_sample,
#              k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', sr1.P); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# no park: ends at B = 7.5 T with the gates on the n-line — the Verify LK mass series
# (temperature-dependence-vti Flavor B) rides the magnet down from here.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
      f"T_sample = {T_sample():.3f} K")
