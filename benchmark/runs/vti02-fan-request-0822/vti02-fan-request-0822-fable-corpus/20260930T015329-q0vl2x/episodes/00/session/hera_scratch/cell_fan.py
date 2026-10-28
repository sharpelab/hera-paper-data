# === Landau fan (`landau-fan-vti`): electron side, D = 0, n 3.24 -> 1.00 e12 (fast) x B 0.7 -> 10 T uniform-1/B (slow) ===
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(3.24, 1.00, 101)               # 1e12 cm^-2; dn = 2.24e10
Ds = np.zeros_like(ns)                          # D = 0 (investigation operating point)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
print(f"fast axis: n = {ns[0]:.2f} -> {ns[-1]:.2f} e12 ({len(ns)} pts); "
      f"Vtg [{Vtgs.min():+.4f}, {Vtgs.max():+.4f}], Vbg [{Vbgs.min():+.4f}, {Vbgs.max():+.4f}] V")

# --- slow axis: uniform in 1/B for the per-column FFT ---
B_vec = field_invB(0.7, 10.0, 161)              # d(1/B) = 0.0083 /T
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
print(f"slow axis: B = {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {len(B_vec)} rows, d(1/B) = {(1/B_vec[0]-1/B_vec[-1])/(len(B_vec)-1):.5f} /T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts with the 0.7 T ramp), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- fixed sensitivity for the whole fan (worst corner: n = 1.0e12 x 10 T; run-7 anchor 587 Ohm at |n|=1.2e12, 10 T) ---
sr1.sensitivity(50e-6)                          # 5 kOhm FS at 10 nA
I_TRIP = 1e-9
FAST_DELAY, SLOW_DELAY = 1.8, 1.0               # 6*tau (tau = 0.3 s, 24 dB/oct) — per-column-FFT dwell, base recipe step 7
print(f"drive {sr1.amplitude()} V -> ~10 nA; sr1 sens {sr1.sensitivity()} V (5 kOhm FS), tau {sr1.time_constant()} s, "
      f"slope {sr1.filter_slope()}; sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan electron side: n = +1.00..+3.24e12 (101), D = 0 (run-5 cal), "
                  "B 0.7 -> 10 T uniform-1/B (161), sr1 50 uV, fast_delay 1.8 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = 0.00 V/nm: n = {ns[-1]:.2f} to {ns[0]:.2f} e12 cm^-2 (101 pts, fast, paired n-line); '
              f'B = 0.7 to 10 T uniform-1/B (161 rows, d(1/B) = 0.0083); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'follows spot checks runs 6-7 (tones 7.8 + 28.9 T at n = +3.2e12)')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field stays at 10 T deliberately: the follow-up (LK cuts / ride-down) starts there — never re-traverse.
    print(f"done: B = {magnet.field():+.3f} T, gates parked at 0, T_sample = {T_sample():.3f} K")
