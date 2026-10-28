# === Landau fan (`landau-fan-vti`): B slow 1 -> 10 T uniform-1/B (91) x paired n-line n = 3.2 -> 0.8e12 at D = 0 (61) ===
# Investigation Step 4 (tetralayer-stacking-fs-count): per-column SdH FFT on the
# electron side, the only side of the D = 0 line reaching design density.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_hi, n_lo, N_n = 3.20, 0.80, 61          # 1e12 cm^-2, D = 0 line, electron side
B_LO, B_HI, N_B = 1.00, 10.0, 91          # B_lo = run-6 onset lower bound; B_hi = session cap
FAST_DELAY, SLOW_DELAY = 1.8, 1.0         # 6 tau at tau = 0.3 s / 24 dB (n-axis carries the extracted signal)
I_TRIP = 1e-9

ns = np.linspace(n_hi, n_lo, N_n)
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"],
                                CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
_n_rt, _D_rt = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.max(np.abs(_D_rt)) < 1e-9, "n-line is not at D = 0"
B_vec = field_invB(B_LO, B_HI, N_B)       # uniform in 1/B — per-column SdH-FFT fan
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
print(f"n-line: {N_n} pts {n_hi} -> {n_lo}e12 at D = 0 | V_tg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V "
      f"| V_bg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V | dn = {abs(ns[1]-ns[0]):.4f}e12 "
      f"({0.0967/abs(ns[1]-ns[0]):.2f} pts per ray at B_lo)")
print(f"B axis: {N_B} rows {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {abs(np.median(np.diff(1/B_vec))):.5f} 1/T "
      f"({1/abs(np.median(np.diff(1/B_vec)))/33.09:.2f} samples/period at F_L(n_max) = 33.1 T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05 — fan positions from ~0), "
      f"V_si = {k_si():+.3f} V (0), V_tg = {k_tg.volt():+.4f}, V_bg = {k_bg.volt():+.4f} V (0, 0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, "
      f"output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# Fixed sensitivity for the whole fan (no autorange mid-row): 50 uV = 5 kOhm FS at 10 nA.
# Worst corner (n = 0.8e12, B = 10 T) projects to 600-1350 Ohm = 0.12-0.27 of FS.
sr1.sensitivity(50e-6)
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS), tau {sr1.time_constant()} s, "
      f"slope {sr1.filter_slope()} dB/oct -> fast_delay {FAST_DELAY} s = {FAST_DELAY/sr1.time_constant():.0f} tau; "
      f"sr0 sens {sr0.sensitivity()} V; drive {sr1.amplitude()} V -> 10 nA")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti: B slow {B_LO}->{B_HI} T uniform-1/B ({N_B}); fast paired n-line "
                  f"n {n_hi}->{n_lo}e12 at D = 0 ({N_n}); sr1 50 uV; fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0.00 V/nm, n = {n_hi} to {n_lo}e12 cm^-2 ({N_n} pts, dn {abs(ns[1]-ns[0]):.4f}e12), '
              f'B = {B_LO} to {B_HI} T uniform in 1/B ({N_B} rows, d(1/B) = 0.0100 1/T); '
              f'electron side (sdh-spot-check run 6); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'sr1 50 uV, fast_delay {FAST_DELAY} s (6 tau), slow_delay {SLOW_DELAY} s')

# --- position: magnet.field() blocks through the ramp (FastBi1K5), so this IS the settle ---
print(f"positioning magnet 0 -> {B_LO} T (~{B_LO/0.137:.0f} min, blocking) ...")
magnet.field(B_vec[0])
print(f"  at {magnet.field():+.4f} T")
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

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
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# Field is left at 10 T deliberately: the investigation's next step (LK mass split,
# temperature-dependence-vti Flavor B) rides the magnet down at elevated T. No park here.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
      f"T_sample = {T_sample():.3f} K")
