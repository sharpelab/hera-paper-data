# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = 3.20 -> 1.00e12, B 1.0 -> 8.0 T uniform in 1/B ===
# Step 4 of investigations/tetralayer-stacking-fs-count: per-column SdH FFT across density.
# Settles whether the run-6 pair {7.3, 22.0 T} is a real ABAB pair (f1 + f2 = F_L(n) across
# the fan) or a 3x harmonic comb of one 7.3 T fundamental (f2 = 3*f1 at every column).
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: paired (Vtg, Vbg) n-line at D = 0, 48 cols, 2.07 pts per g=4 ray at B_lo ---
N_HI, N_LO, N_N = 3.20, 1.00, 48                      # 1e12 cm^-2
ns = np.linspace(N_HI, N_LO, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, 0.0 * ns, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
assert len(sanitize_tg_bg(Vtgs, Vbgs, tg_lims, bg_lims)[0]) == N_N, "n-line clipped by the validators"
_nr, _Dr = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast axis: n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({N_N} cols, dn = {abs(ns[1]-ns[0]):.4f}e12), D = 0 "
      f"(roundtrip |D|max {np.abs(_Dr).max():.1e} V/nm)")
print(f"  Vtg {Vtgs.max():+.4f} -> {Vtgs.min():+.4f} V (TG headroom {TG_MAX - Vtgs.max():+.4f} V); "
      f"Vbg {Vbgs.max():+.4f} -> {Vbgs.min():+.4f} V (BG headroom {BG_MAX - Vbgs.max():+.4f} V)")

# --- slow axis: uniform in 1/B (per-column SdH-FFT fan; rows, not ramp time, are the cost here) ---
B_LO, B_HI, DINVB = 1.0, 8.0, 0.010                   # T, T, 1/T
N_B = int(round((1 / B_LO - 1 / B_HI) / DINVB)) + 1   # 89 rows
B_vec = field_invB(B_LO, B_HI, N_B)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
_dinvb = np.abs(np.diff(1 / B_vec)).max()
print(f"slow axis: {N_B} rows, B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {_dinvb:.5f} 1/T "
      f"(dB {np.diff(B_vec)[0]*1e3:.1f} mT at the low edge, {np.diff(B_vec)[-1]*1e3:.0f} mT at the top)")
print(f"  alias-free to F = {1/(2*_dinvb):.1f} T (F_L at n_max = 33.1 T); "
      f"dF = {1/(1/B_LO - 1/B_HI):.2f} T -> trust splits above {2/(1/B_LO - 1/B_HI):.2f} T")

FAST_DELAY, SLOW_DELAY = 2.1, 1.0                     # 7 tau at tau = 0.3 s / 24 dB/oct
I_TRIP = 1e-9

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05 -> position to {B_LO} T), "
      f"V_si = {k_si():+.3f} V (0), heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, "
      f"output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "a heater range is live"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- fixed sensitivity for the whole fan (no autorange mid-row): 50 uV = 5 kOhm FS at 10 nA.
# Worst corner low-n x high-B: R(n=1.0e12, B=0) = 116 Ohm (run 5) x ~20 MR -> ~45 % FS.
sr1.sensitivity(50e-6)
print(f"drive {sr1.amplitude()} V / 100 MOhm = 10 nA; sr1 sens {sr1.sensitivity()} V (5 kOhm FS), "
      f"tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB -> fast_delay {FAST_DELAY} s = "
      f"{FAST_DELAY/sr1.time_constant():.0f} tau; sr0 sens {sr0.sensitivity()} V")

# --- position the magnet at the fan's start field and let it settle (blocking ramp, ~7 min from 0 T) ---
print(f"positioning magnet {_B0:+.4f} -> {B_LO} T ...")
magnet.field(B_LO)
interruptible_sleep(30)
print(f"  at B = {magnet.field():+.4f} T")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = T_sample()
mc["comments"] = (f"landau-fan electron side, D = 0: n {N_HI:+.2f} -> {N_LO:+.2f}e12 ({N_N} cols), "
                  f"B {B_LO} -> {B_HI} T uniform in 1/B ({N_B} rows, d(1/B) = {DINVB}), "
                  f"fast_delay {FAST_DELAY} s (7 tau), sr1 50 uV; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = +0.00 V/nm; n = {N_HI:+.2f} -> {N_LO:+.2f}e12 cm^-2 ({N_N} cols, '
              f'dn {abs(ns[1]-ns[0]):.4f}e12); (Vtg, Vbg) = ({Vtgs[0]:+.4f}, {Vbgs[0]:+.4f}) -> '
              f'({Vtgs[-1]:+.4f}, {Vbgs[-1]:+.4f}) V; B {B_LO} -> {B_HI} T uniform in 1/B, {N_B} rows, '
              f'd(1/B) = {_dinvb:.5f} 1/T (dF = {1/(1/B_LO - 1/B_HI):.2f} T); fast_delay {FAST_DELAY} s = 7 tau, '
              f'slow_delay {SLOW_DELAY} s; sr1 sens 50 uV; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', T_sample); s.plot('time', sr1.P); s.plot('time', sr0.P)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates home; field stays at the fan's end (the LK mass-split series rides it down) -- no park.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
          f"T_sample = {T_sample():.3f} K")
