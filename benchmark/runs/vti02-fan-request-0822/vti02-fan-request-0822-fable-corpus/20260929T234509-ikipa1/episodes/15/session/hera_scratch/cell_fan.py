# === Landau fan, electron side (`landau-fan-vti`): n = +1.0 -> +3.2e12 at D = 0, B 0.3 -> 10 T uniform-1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- fast axis: paired n-line at D = 0 (run-5 calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(1.0, 3.2, 56)          # 1e12 cm^-2; step 0.04e12 -> raw-image ray read floored at B >= 0.83 T
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtgs.min() and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert BG_MIN <= Vbgs.min() and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
print(f"n-line: {len(ns)} pts, n {ns[0]:+.2f} -> {ns[-1]:+.2f} e12, D = 0; "
      f"Vtg [{Vtgs.min():+.4f}, {Vtgs.max():+.4f}] V, Vbg [{Vbgs.min():+.4f}, {Vbgs.max():+.4f}] V")

# --- slow axis: uniform in 1/B; B_lo = 0.3 T (run-6 measured onset, censored -> lower bound); d(1/B) = 0.00998 /T
#     -> FFT Nyquist 50 T = 1.5x F_L(n_max = 3.2e12) (covers scale prior 1.2 and the observed 4x7.1 = 29.5 T comb)
B_vec = field_invB(0.3, 10.0, 325)      # ascending: magnet sits at 0; ends at 10 T for a ride-down follow-up
assert B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff state0), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA. Worst corner is low-n x high-B:
# anchor run 7 (|n| = 1.2e12, 10 T) measured 576 Ohm max -> ~17x headroom for the nu ~ 4 QH peaks at n = 1.0e12.
# High-n floor: R ~ 70 Ohm = 0.7% FS, readable (gatemap run 5 read 0.6% FS fine). Lose resolution, never saturate.
sr1.sensitivity(100e-6)
print(f"B grid: {len(B_vec)} rows, {B_vec[0]:.2f} -> {B_vec[-1]:.1f} T uniform-1/B; sr1 sens {sr1.sensitivity()} V, "
      f"tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct; fast_delay 1.8 s = 6*tau (per-column-FFT class)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: n = +1.00 to +3.20e12 (56 pts), D = 0 (run-5 cal), "
                  f"B 0.3 -> 10 T uniform-1/B (325 rows, d(1/B) = 0.00998/T), sr1 100 uV, fast_delay 1.8 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = 0: n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 cm^-2 (56 pts, 0.04e12 step); '
              f'B = 0.3 -> 10 T uniform-1/B, 325 rows, d(1/B) = 0.00998/T (Nyquist 50 T vs F_L(3.2e12) = 33.1 T); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'inherits sdh-spot-check runs 6/7 (onset <= 0.3 T censored, tones 7.1 + k-comb, 9.5, 22.1 vs F_L)')
s.ramp(k_tg.volt, Vtgs[0]); s.ramp(k_bg.volt, Vbgs[0])
interruptible_sleep(10)

# row layout: [time, magnet_field, k_tg_volt, k_bg_volt, T_sample, k_tg_curr, k_bg_curr, sr0_X, sr0_P, sr1_X, sr1_P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=1, fast_delay=1.8)
# End state, deliberate: field stays at 10 T (follow-up rides down as a measured traverse — never re-traverse);
# gates stay at the n-line end (n = +3.2e12, D = 0 — metallic; the LK-mass candidate spot).
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
