# === Landau fan at D = 0 (`landau-fan`): n fast [-1.25, +3.25]e12 (141 pts) x B slow 1 -> 10 T (120 rows, uniform 1/B) ===
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.25, 3.25, 141)          # 1e12 cm^-2 along D = 0; dn = 0.032e12
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
B_vec = field_invB(1.0, 10.0, 120)             # uniform in 1/B: d(1/B) = 0.00756 /T -> F_Nyquist 66 T, dF 1.1 T
assert B_vec.max() <= B_SESSION_CAP
FAST_DELAY, SLOW_DELAY, I_TRIP = 1.0, 3.0, 1e-9

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan opens with the 1 T ramp), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# Fixed sensitivity: 100 uV = 10 kOhm FS at 10 nA (run-4 lesson: size to the worst corner,
# here the high-B CNP stripe; a nu=0 clip in a narrow n-window is accepted and stated in the md).
sr1.sensitivity(100e-6)
print(f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s; sr0 sens {sr0.sensitivity()} V; fast dwell {FAST_DELAY} s")
print(f"n [-1.25, +3.25]e12 -> Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}] V, Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}] V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = "landau-fan D=0: n fast -1.25..+3.25e12 (141), B slow 1..10 T uniform-1/B (120 rows), run-5 cal, sr1 100 uV"
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: n fast [-1.25, +3.25]e12 141 pts (dn 0.032e12); B slow 1 -> 10 T 120 rows uniform in 1/B '
              f'(d(1/B) 0.00756 /T, F_Nyq 66 T); cal run 5: ratio 0.773, n_offset -0.089e12, D_offset -0.013; '
              f'sr1 100 uV (10 kOhm FS), I = 10 nA')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
print(f"done: B = {magnet.field():+.3f} T (held for the next step), gates parked at 0")
