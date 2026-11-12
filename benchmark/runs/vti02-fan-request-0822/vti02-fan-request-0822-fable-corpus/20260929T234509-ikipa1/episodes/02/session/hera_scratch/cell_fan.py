# === Landau fan (`landau-fan-vti`): electron side, D = 0, n +3.2 -> +1.2e12 (141) x B 10 -> 0.3 T uniform-1/B (269) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_N, N_B = 141, 269
ns = np.linspace(3.2, 1.2, N_N)                 # 1e12 cm^-2, high->low n each row
Ds = np.zeros(N_N)                              # V/nm
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
print(f"n-line: {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = 0; Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, "
      f"Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V; roundtrip n,D[0] = {calc_nD(Vtgs[0], Vbgs[0], *CAL.values())}")

# --- slow axis: uniform in 1/B, descending 10 -> 0.3 T; D(1/B) = 0.0121 T^-1 (Nyquist 41.3 T) ---
invB = np.linspace(1.0 / 10.0, 1.0 / 0.3, N_B)
B_vec = np.round(1.0 / invB, 4)                 # 10 -> 0.3 T
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() >= 0.29
print(f"B: {B_vec[0]} -> {B_vec[-1]} T, {N_B} rows uniform-1/B, D(1/B) = {invB[1]-invB[0]:.5f} T^-1")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: pre-ramp starts at 0), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"

# --- lock-in: fixed for the whole fan (inherited from runs 6/7; worst corner 587 Ohm = 12% FS, run 7) ---
sr1.sensitivity(50e-6)
print(f"drive {sr1.amplitude()} V -> ~10 nA; sr1 sens {sr1.sensitivity()} V (5 kOhm FS); "
      f"sr0 sens {sr0.sensitivity()} V; tau {sr1.time_constant()} s")

FAST_DELAY, SLOW_DELAY = 1.2, 1.0               # 4*tau; retrace lag static per column, < dF after bg removal
I_TRIP = 1e-9

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan electron side: n +3.2 -> +1.2e12 (141 pts) at D = 0 (run-5 cal), "
                  "B 10 -> 0.3 T uniform-1/B (269 rows, D(1/B)=0.0121), sr1 50 uV, fast_delay 1.2 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('electron side: n = +3.2 -> +1.2e12 cm^-2 (141 pts), D = 0.00 V/nm; B 10 -> 0.3 T uniform-1/B, '
              '269 rows D(1/B) = 0.0121 T^-1; cal run 5: ratio 0.773, n_offset -0.089e12, D_offset -0.013; '
              'inherits sdh-spot-check runs 6/7 (onset <= 0.3 T censored, Nyq 41.3 T vs content <= 32.4 T)')

# gates to the first point, then the bare positioning ramp 0 -> 10 T (blocking, ~73 min)
s.ramp(k_tg.volt, Vtgs[0]); s.ramp(k_bg.volt, Vbgs[0])
interruptible_sleep(10)
print("pre-ramp 0 -> 10 T (blocking, ~73 min)...")
magnet.field(float(B_vec[0]))
print(f"at B = {magnet.field():+.4f} T; starting fan")

# row layout: [time, B(slow), Vtg, Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot(k_bg.volt, k_bg.curr)
s.plot('time', T_sample)

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
    print(f"fan done/stopped: B = {magnet.field():+.4f} T (left there deliberately), gates parked at 0")
