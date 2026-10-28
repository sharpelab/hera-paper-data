# === Landau fan, electron side (`landau-fan-vti`): D = 0, n = +0.80..+3.25e12 (64), B 0.5 -> 10 T uniform-1/B (193) ===
from sharpelab_nb.gates import calc_gate_voltages

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_N, N_B = 64, 193
ns = np.linspace(3.25, 0.80, N_N)              # 1e12 cm^-2, fast axis high -> low n
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtgs.min() and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert BG_MIN <= Vbgs.min() and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())

B_vec = field_invB(0.5, 10.0, N_B)             # uniform in 1/B, ascending
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() >= 0.5 - 1e-9
d_invB = (1 / 0.5 - 1 / 10.0) / (N_B - 1)
FL_max = cst.h / (4 * cst.e) * ns.max() * 1e16
assert d_invB <= 1 / (3 * FL_max), (d_invB, 1 / (3 * FL_max))   # 1/3-Nyquist on F_L(n_max) = 33.6 T

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: positioning ramp is 0 -> 0.5 T), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(sr1.time_constant() - 0.3) < 1e-9 and int(sr1.filter_slope()) == 24, "dwell floor sized for tau=0.3 s @ 24 dB/oct"

I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange): 50 uV = 5 kOhm FS at 10 nA.
# Worst corner (n=0.8, 10 T) ~ 1.1 kOhm (run 5 R(0.8,0)=147 Ohm x run-6 MR ~7.6x) -> >=3x headroom.
sr1.sensitivity(50e-6)
FAST_DELAY, SLOW_DELAY = 2.1, 2.0              # 7*tau settling floor; slow_delay covers gate flyback
print(f"fan: {N_B} B-rows x {N_N} n-cols = {N_B*N_N} pts; d(1/B) = {d_invB:.5f} /T (alias ceiling {0.5/d_invB:.1f} T); "
      f"n {ns.max():.2f} -> {ns.min():.2f} e12, Vtg [{Vtgs.min():+.4f}, {Vtgs.max():+.4f}], Vbg [{Vbgs.min():+.4f}, {Vbgs.max():+.4f}]; "
      f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron: D = 0 (run-5 cal), n = +0.80..+3.25e12 ({N_N} cols), "
                  f"B 0.5 -> 10 T uniform-1/B ({N_B} rows), sr1 50 uV, fast_delay 2.1 s (7 tau)")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = 0 (run-5 cal): n = +3.25 -> +0.80e12 cm^-2 fast ({N_N} cols, step 0.0389e12), '
              f'B = 0.5 -> 10 T slow, uniform-1/B ({N_B} rows, d(1/B) = {d_invB:.5f} = 1/3-Nyquist on F_L(3.25) = {FL_max:.1f} T); '
              f'sr1 50 uV, fast_delay 2.1 s (7 tau, 24 dB/oct), slow_delay 2 s; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_tg.volt, Vtgs[0]); s.ramp(k_bg.volt, Vbgs[0])
magnet.field(0.5)                              # position; the blocking set call is the settle (~3.7 min from 0)
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)  # park gates; field holds at 10 T — next move decided from the data
print(f"done: B = {magnet.field():+.3f} T, gates parked ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
