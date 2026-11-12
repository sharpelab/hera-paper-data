# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +1.50 -> +3.25e12, B 1.0 -> 10.0 T uniform in 1/B ===
# Step 4 of investigations/tetralayer-stacking-fs-count: per-column SdH FFT vs F_L across density.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0                                          # V/nm
ns = np.linspace(1.50, 3.25, 45)                  # 1e12 cm^-2, fast axis (45 cols, dn = 0.0398e12)
Ds = D0 * np.ones_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
print(f"n-line: {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = {D0:+.2f} V/nm, {len(ns)} cols (dn = {ns[1]-ns[0]:.4f}e12); "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V (limit {TG_MAX}), Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")
print(f"  endpoint roundtrip n,D: {calc_nD(Vtgs[0], Vbgs[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}, "
      f"{calc_nD(Vtgs[-1], Vbgs[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- slow axis: uniform in 1/B (per-column SdH-FFT fan), ascending so the fan ends at 10 T for the LK ladder ---
B_LO, B_HI, N_B = 1.0, 10.0, 145
B_vec = field_invB(B_LO, B_HI, N_B)
assert np.abs(B_vec).max() <= B_SESSION_CAP
_dinv = abs(np.diff(1.0 / B_vec)[0])
print(f"B grid: {len(B_vec)} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T uniform in 1/B; "
      f"d(1/B) = {_dinv:.5f} 1/T -> Nyquist F = {1/(2*_dinv):.0f} T; dB {np.diff(B_vec).min()*1e3:.1f}-{np.diff(B_vec).max()*1e3:.0f} mT; "
      f"dF = {1/(1/B_vec[0] - 1/B_vec[-1]):.2f} T; ray dn at B_lo = {4*cst.e/cst.h*B_LO/1e16:.4f}e12 "
      f"({(4*cst.e/cst.h*B_LO/1e16)/(ns[1]-ns[0]):.2f} pts/ray)")

# --- preconditions (assumed, not set; B and the gates are set by this cell) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 1.05, this cell positions to {B_LO} T), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 1.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()
# settling budget inherited from the run 6/7 spot checks - read tau/slope, never assume
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24, (sr1.time_constant(), sr1.filter_slope())

FAST_DELAY, SLOW_DELAY = 1.8, 2.0     # 6 tau at 24 dB/oct (per-column SdH-FFT fan); slow axis is the blocking magnet
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (worst corner = low n x high B ~ 1.1 kOhm): 50 uV = 5 kOhm FS at 10 nA.
sr1.sensitivity(50e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (5 kOhm FS), tau {sr1.time_constant()} s / "
      f"{sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s = {FAST_DELAY/sr1.time_constant():.0f} tau")

# --- position the magnet at the fan start (FastBi1K5 set blocks through the ramp; the set IS the settle) ---
print(f"positioning magnet {_B0:+.4f} -> {B_LO} T ...", flush=True)
magnet.field(B_LO)
print(f"  at B = {magnet.field():+.4f} T", flush=True)

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = T_sample()
mc["comments"] = (f"landau-fan electron side, D = 0: n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({len(ns)} cols), "
                  f"B {B_LO} -> {B_HI} T uniform-1/B ({N_B} rows, d(1/B) = {_dinv:.5f}), sr1 50 uV, fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = {D0:+.2f} V/nm; n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 cm^-2, {len(ns)} cols (dn {ns[1]-ns[0]:.4f}e12); '
              f'B = {B_LO} to {B_HI} T, {N_B} rows uniform in 1/B (d(1/B) = {_dinv:.5f} 1/T, Nyquist {1/(2*_dinv):.0f} T, dF = {1/(1/B_vec[0]-1/B_vec[-1]):.2f} T); '
              f'sr1 50 uV, tau 0.3 s / 24 dB, fast_delay {FAST_DELAY} s; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg (fast pair), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', sr1.P); s.plot('time', sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    # negative indices off the 7-long fp tail, so the front matter (1 slow + 2 fast) can't shift them
    i_tg, i_bg = abs(float(data[-6])), abs(float(data[-5]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # park the gates; leave the field at 10 T deliberately - the LK mass ladder rides it down (never re-traverse)
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
