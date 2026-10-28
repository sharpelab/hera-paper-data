# === Landau fan (`landau-fan-vti`): electron side, D = 0, n-line 3.2 -> 1.0e12 (121 pts) fast, B 0.6 -> 10 T uniform-1/B (160 rows) slow ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_N, N_B = 121, 160
ns = np.linspace(3.2, 1.0, N_N)            # 1e12 cm^-2, descending along the row
Ds = np.zeros(N_N)                         # D = 0 line
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, \
    (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
print(f"n-line: n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = 0; Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, "
      f"Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")

# --- field axis: uniform in 1/B (per-column SdH-FFT fan), 1/3-Nyquist on F_L(3.2e12) = 33.6 T ---
invB = np.linspace(1 / 0.6, 1 / 10.0, N_B)
B_vec = 1.0 / invB                          # 0.6 -> 10 T ascending (magnet sits at 0)
assert B_vec.max() <= B_SESSION_CAP
dinvB = abs(invB[1] - invB[0])
print(f"B: {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows, d(1/B) = {dinvB:.5f} 1/T "
      f"(Nyquist F = {1/(2*dinvB):.1f} T >= 33.6 needed x1.5)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan positions to 0.6 T itself), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- lock-in: inherit run 6 (50 uV = 5 kOhm FS at 10 nA; worst-corner anchor run 7 max 587 Ohm) ---
sr1.sensitivity(50e-6)
FAST_DELAY, SLOW_DELAY = 1.8, 1.0           # 6*tau at tau = 0.3 s / 24 dB (per-column-FFT discipline)
I_TRIP = 1e-9
print(f"drive {sr1.amplitude()} V -> ~10 nA; sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s, "
      f"slope {sr1.filter_slope()} dB/oct; fast_delay {FAST_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12, D = 0 (run-5 cal), "
                  f"B 0.6 -> 10 T uniform-1/B {N_B} rows, {N_N}-pt n-line, sr1 50 uV, fast_delay 1.8 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = 0: n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 cm^-2 ({N_N} pts, paired n-line); '
              f'B = {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T uniform-1/B ({N_B} rows, d(1/B) = {dinvB:.5f}); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'follows spot checks runs 6-7 (tones 7.1/22.2 T, sum 0.885 F_L)')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # end state by design: B = 10 T (LK ladder rides down from here), gates parked at 0
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
          f"T_sample = {T_sample():.3f} K")
