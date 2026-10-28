# === Landau fan (`landau-fan-vti`), D = 0, electron side: n 3.20 -> 1.20e12 x B 0.8 -> 10 T ===
# Step 4 of investigations/tetralayer-stacking-fs-count. Per-column SdH FFT in 1/B:
# ABAB pair (partner fraction curving 0.09 -> 0.22) vs ABCA singleton vs harmonic comb.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (read, cell positions it), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()
# fast_delay below is 6*tau — assert the tau it is derived from (front-panel owned, not set by the kit)
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24, (sr1.time_constant(), sr1.filter_slope())

# --- fast axis: paired (k_tg, k_bg) n-line at D = 0, descending so column 0 == run 6's spot ---
N_N = 53                                   # n-axis Nyquist floor: 2.0 pts per LL ray at B_lo = 0.8 T
ns = np.linspace(3.20, 1.20, N_N)          # 1e12 cm^-2, dn = 0.0385e12
Ds = np.zeros(N_N)                         # D = 0 (the operating point: finite D gaps ABCA / hybridizes ABAB)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, **CAL)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
_n0, _D0 = calc_nD(Vtgs[0], Vbgs[0], **CAL)
print(f"n-line: {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({N_N} pts, dn = {ns[0]-ns[1]:.4f}e12) at D = 0; "
      f"Vtg {Vtgs.max():+.4f}..{Vtgs.min():+.4f}, Vbg {Vbgs.max():+.4f}..{Vbgs.min():+.4f}; "
      f"col0 roundtrip n,D = ({_n0:+.3f}e12, {_D0:+.4f}) [= run 6 spot]")

# --- slow axis: field, uniform in 1/B (per-column SdH-FFT fan) ---
N_B = 114
B_vec = field_invB(0.8, 10.0, N_B)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
_dinv = 1 / B_vec[0] - 1 / B_vec[1]
_span = 1 / B_vec[0] - 1 / B_vec[-1]
print(f"B rows: {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows uniform in 1/B; "
      f"d(1/B) = {_dinv:.5f} /T -> Nyquist ceiling {1/(2*_dinv):.1f} T (fastest expected tone F_L = 33.1 T); "
      f"1/B span {_span:.4f} /T -> dF = {1/_span:.3f} T; dB {B_vec[1]-B_vec[0]:.4f} -> {B_vec[-1]-B_vec[-2]:.4f} T")

FAST_DELAY, SLOW_DELAY = 1.8, 1.0          # 1.8 s = 6*tau (per-column SdH-FFT dwell)
I_TRIP = 1e-9

# Fixed sensitivity for the whole fan, inherited from the spot checks (runs 6/7):
# 50 uV = 5 kOhm FS at 10 nA. Worst corner (n_min x B_max) anchored at 576 Ohm (run 7, |n|=1.2e12, 10 T) = 12% FS.
sr1.sensitivity(50e-6)
print(f"drive {sr1.amplitude()} V / 100 MOhm -> 10 nA; sr1 sens {sr1.sensitivity()} V (5 kOhm FS), "
      f"tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct; fast_delay {FAST_DELAY} s = {FAST_DELAY/sr1.time_constant():.0f}tau")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti D=0 electron: n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({N_N} pts), "
                  f"B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T ({N_B} rows, uniform 1/B), sr1 50 uV, "
                  f"fast_delay {FAST_DELAY} s; run-5 cal; stacking call Step 4")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0 V/nm, n = {ns[-1]:+.2f} to {ns[0]:+.2f}e12 cm^-2 ({N_N} pts, dn {ns[0]-ns[1]:.4f}e12, fast axis descending), '
              f'B = {B_vec[0]:.3f} to {B_vec[-1]:.3f} T ({N_B} rows, uniform in 1/B, d(1/B) {_dinv:.5f} /T, dF {1/_span:.3f} T); '
              f'Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f}; Vsi = 0; '
              f'sr1 sens 50 uV (5 kOhm FS), tau 0.3 s / 24 dB/oct, fast_delay {FAST_DELAY} s = 6tau, slow_delay {SLOW_DELAY} s; '
              f'cal run 5: c_tg {CAL["c_tg"]:.4e}, c_bg {CAL["c_bg"]:.4e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.4f}; '
              f'col 0 == run 6 spot-check gate point (uniform-1/B vs run 6 uniform-B = grid-change reproduction)')

# position: gates first, then the magnet (FastBi1K5 set blocks until reached -- the set IS the settle)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
print(f"gates positioned: Vtg = {k_tg.volt():+.4f}, Vbg = {k_bg.volt():+.4f}; ramping magnet to {B_vec[0]:.3f} T (~6 min from 0 T)")
s.ramp(magnet.field, B_vec[0])
print(f"magnet positioned: B = {magnet.field():+.4f} T")

# row layout: [time, B(slow), Vtg(fast0), Vbg(fast1), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
I_TG, I_BG = 5, 6
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
# every fp'd channel gets a live plot
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[I_TG])), abs(float(data[I_BG]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates park at 0; field is LEFT at the fan's end deliberately (LK mass series rides it down)
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.4f} T (left here on purpose), Vtg = {k_tg.volt():+.4f}, Vbg = {k_bg.volt():+.4f}")
