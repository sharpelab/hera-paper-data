# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +3.2 -> +1.6e12, B 0.65 -> 10 T ===
# Step 4 of investigations/tetralayer-stacking-fs-count: per-column SdH FFT vs F_L(n).
# Design numbers (hera_scratch/fan_design.py, from run 5 cal + run 6 onset/FFT + the model F(n) table):
#   B axis  uniform in 1/B, Delta(1/B) = 1/(4 F_L(n_max)) = 0.00756 1/T  -> 191 rows, f_Nyq 66 T
#   n axis  53 columns, dn = 0.0308e12 -> 2.04 pts per LL ray at B_lo (ray-Nyquist floor)
#   record  1/B span 1.4385 1/T -> dF = 0.70 T; partner periods at the n = 2.0 claim floor: 5.1
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)  # run-5 calibration
N_HI, N_LO, N_N = 3.2, 1.6, 53          # 1e12 cm^-2, electron side of the D = 0 line
B_LO, B_HI, N_B = 0.65, 10.0, 191       # T
D_FAN = 0.0                             # V/nm
DWELL = 2.1                             # s = 7 tau at tau = 0.3 s / 24 dB-oct (settling floor)

# --- fast axis: paired (V_tg, V_bg) n-line at D = 0, descending (row starts at high n) ---
ns = np.linspace(N_HI, N_LO, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, np.full_like(ns, D_FAN), CAL["c_tg"], CAL["c_bg"],
                                CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
# --- slow axis: uniform in 1/B (per-column SdH-FFT fan), ascending from the onset floor ---
B_vec = np.round(1.0 / np.linspace(1.0 / B_LO, 1.0 / B_HI, N_B), 4)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
I_TRIP = 1e-9

# --- preconditions (assumed, not set): thermometry live, base T, magnet at 0, Si at 0, PS/output ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: magnet parked at 0), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24, (sr1.time_constant(), sr1.filter_slope())
sr1.sensitivity(50e-6)   # 5 kOhm FS at 10 nA; worst corner (n = 1.6e12, 10 T) ~ 1.0-1.3 kOhm -> ~4x headroom
print(f"fan grid: {N_B} B rows x {N_N} n columns = {N_B*N_N} pts; B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T "
      f"(dB {np.abs(np.diff(B_vec)).min()*1e3:.1f}-{np.abs(np.diff(B_vec)).max()*1e3:.0f} mT); "
      f"n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = {D_FAN:+.2f} V/nm; "
      f"V_tg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f}, V_bg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f}; "
      f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s / {sr1.filter_slope()} dB, dwell {DWELL} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan electron side: n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = {D_FAN:+.2f} V/nm "
                  f"(run-5 cal), B {B_vec[0]} -> {B_vec[-1]} T uniform in 1/B, {N_B} x {N_N}, "
                  f"dwell {DWELL} s, sr1 50 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D_FAN:+.2f} V/nm, n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 ({N_N} cols, dn {abs(ns[1]-ns[0]):.4f}e12), '
              f'B = {B_vec[0]} to {B_vec[-1]} T ({N_B} rows, uniform in 1/B, d(1/B) = {1/B_vec[0]-1/B_vec[1]:.5f} 1/T), '
              f'dwell {DWELL} s = 7 tau (tau 0.3 s / 24 dB), sr1 sens 50 uV')
s.add_comment(f'FS-count investigation step 4 (per-column SdH FFT vs F_L); cal run 5: c_tg {CAL["c_tg"]:.4e}, '
              f'c_bg {CAL["c_bg"]:.4e}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'grid from run 6 onset (<= 0.30 T, censored) + model F(n): partner 3.55 T at the n = 2.0 claim floor')

# --- position: gates to the fan's start density first, then the magnet to B_lo (blocking ramp ~5 min) ---
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
s.ramp(magnet.field, B_vec[0])
interruptible_sleep(5)
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")

# row layout: [time, magnet_field, k_tg_volt, k_bg_volt, T_sample, k_tg_curr, k_bg_curr, sr0_X, sr0_P, sr1_X, sr1_P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, magnet.field, sr1.X)                  # the fan map, live
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)      # per-row Rxx trace + current channel
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)    # leakage, both gates
s.plot('time', T_sample)                                # fridge over an 8 h run
s.plot('time', sr1.P); s.plot('time', sr0.P)            # phase drift on both lock-ins

I_TG_COL, I_BG_COL = 5, 6   # indices into the row layout above
_seen = []
def leak_guard(station, data):
    if not _seen:
        _seen.append(1)
        print(f"first row: B={float(data[1]):+.4f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}, "
              f"T={float(data[4]):.3f} K, I_tg={float(data[5]):.2e}, I_bg={float(data[6]):.2e}, "
              f"sr1_X={float(data[9]):.3e} V, ncols={len(data)}")
        assert len(data) == 11, f"row layout changed ({len(data)} cols) — leak-guard indices invalid"
    i_tg, i_bg = abs(float(data[I_TG_COL])), abs(float(data[I_BG_COL]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=1.0, fast_delay=DWELL)
# ends at B = 10 T with the gates at the fan's low-n end — the LK mass ladder (Verify) rides the magnet down.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
      f"T_sample = {T_sample():.3f} K")
