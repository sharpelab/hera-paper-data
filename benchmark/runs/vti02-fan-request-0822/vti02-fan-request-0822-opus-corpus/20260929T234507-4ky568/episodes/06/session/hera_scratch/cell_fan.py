# === Landau fan (`landau-fan-vti`): D = 0, n = +1.60 -> +3.20e12 fast, B 0.7 -> 7.0 T uniform-1/B slow ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_N = 1.60, 3.20, 49                 # 1e12 cm^-2; dn = 0.0333e12 = 2.03 LL rays/period at B_lo
D_FAN = 0.0                                      # V/nm
B_LO, B_HI, N_B = 0.7, 7.0, 172                  # d(1/B) = 0.00752 1/T -> Nyquist 66.5 T, 4.0 pts/period at F_L(n_max)

ns = np.linspace(N_LO, N_HI, N_N)
Ds = np.full_like(ns, D_FAN)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
B_vec = field_invB(B_LO, B_HI, N_B)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
_dinv = np.diff(1.0 / B_vec)
F_L_max = cst.h * (N_HI * 1e16) / (4 * cst.e)    # Luttinger frequency at n_max, Tesla
print(f"fast: n {N_LO:+.2f} -> {N_HI:+.2f}e12 at D = {D_FAN:+.2f} V/nm, {N_N} pts (dn = {ns[1]-ns[0]:.4f}e12); "
      f"Vtg {Vtgs.min():+.4f} -> {Vtgs.max():+.4f}, Vbg {Vbgs.min():+.4f} -> {Vbgs.max():+.4f} V")
print(f"slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows, d(1/B) = {abs(_dinv.mean()):.5f} 1/T "
      f"(dB {B_vec[1]-B_vec[0]:.4f} T at B_lo, {B_vec[-1]-B_vec[-2]:.3f} T at B_hi); "
      f"F_L(n_max) = {F_L_max:.1f} T -> {1/(abs(_dinv.mean())*F_L_max):.2f} pts/period; dF = {1/(1/B_LO-1/B_HI):.2f} T")
print(f"grid: {N_B} x {N_N} = {N_B*N_N} pts")
print(f"roundtrip (n, D) at first/last column: {calc_nD(Vtgs[0], Vbgs[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}, "
      f"{calc_nD(Vtgs[-1], Vbgs[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: magnet parked at 0 by close-out), "
      f"V_si = {k_si():+.3f} V (0), Vtg = {k_tg.volt():+.4f}, Vbg = {k_bg.volt():+.4f} V (0, 0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- fixed sensitivity for the whole fan (no autorange mid-row): 50 uV = 5 kOhm FS at 10 nA.
# Worst corner is low n x high B: R(B=0) = 82.9 Ohm at n = 1.6 (run 5) vs 55.9 at n = 3.2, and run 6's
# MR+SdH maximum was 522 Ohm -> ~1.2-1.5 kOhm expected at (1.6e12, 7 T), ~3.5x under full scale.
sr1.sensitivity(50e-6)
SLOW_DELAY, FAST_DELAY = 3.0, 1.2        # 10 tau (covers the n_max -> n_min flyback) / 4 tau; tau = 0.3 s, 24 dB/oct
I_TRIP, T_TRIP = 1e-9, 2.0
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (5 kOhm FS); sr0 sens {sr0.sensitivity()} V; "
      f"tau {sr1.time_constant()} s, slope {sr1.filter_slope()}; slow_delay {SLOW_DELAY} s, fast_delay {FAST_DELAY} s "
      f"(magnet settle_s {magnet.settle_s} s on top of each row's blocking ramp)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti: D = {D_FAN:+.2f} V/nm, n = {N_LO:+.2f} -> {N_HI:+.2f}e12 ({N_N} cols), "
                  f"B = {B_LO} -> {B_HI} T uniform-1/B ({N_B} rows, d(1/B) = {abs(_dinv.mean()):.5f}), sr1 50 uV, "
                  f"fast_delay {FAST_DELAY} s / slow_delay {SLOW_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D_FAN:+.2f} V/nm, n = {N_LO:+.2f} to {N_HI:+.2f}e12 cm^-2 ({N_N} cols, dn {ns[1]-ns[0]:.4f}e12), '
              f'B = {B_LO} to {B_HI} T uniform-1/B ({N_B} rows, d(1/B) = {abs(_dinv.mean()):.5f} 1/T, '
              f'{1/(abs(_dinv.mean())*F_L_max):.2f} pts/period at F_L(n_max) = {F_L_max:.1f} T, dF = {1/(1/B_LO-1/B_HI):.2f} T); '
              f'sr1 50 uV (5 kOhm FS), I_bias 10 nA; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'tetralayer-stacking-fs-count Step 4, follows spot checks runs 6/7')

# --- position: gates to the first column, magnet to B_lo (FastBi1K5 set blocks through the ramp = the settle) ---
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
magnet.field(B_vec[0])
print(f"positioned: B = {magnet.field():+.4f} T (target {B_vec[0]:.3f}), (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V")

# row layout: [time, magnet_field(slow), k_tg_volt(fast), k_bg_volt(fast), T_sample, k_tg_curr, k_bg_curr,
#              sr0_X, sr0_P, sr1_X, sr1_P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def fan_guard(station, data):
    assert len(data) == 11, f"unexpected column count {len(data)} — leak-guard indices are wrong"
    i_tg, i_bg, t_s = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if t_s > T_TRIP:
        print(f"TEMPERATURE TRIP at B={float(data[1]):+.3f} T: T_sample = {t_s:.3f} K > {T_TRIP} K")
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # park gates; leave the field at B_hi deliberately — the LK mass split rides the magnet back down.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
