# === Landau fan at D = 0 (`landau-fan`): B slow 0.2 -> 10 T (84 rows) x n fast -1.25 -> +3.25e12 (181 pts) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0.2), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, sr1 tau {sr1.time_constant()} s")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- fast axis: D = 0 line, n -1.25 -> +3.25 e12 cm^-2, 181 pts (dn = 0.025e12) ---
n_vec = np.linspace(-1.25, 3.25, 181)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
_n_rt, _D_rt = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.max(np.abs(_D_rt)) < 1e-3 and np.max(np.abs(_n_rt - n_vec)) < 1e-6
print(f"fast line: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 ({len(n_vec)} pts); "
      f"Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}], Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}] V")

# --- slow axis: 0.2 -> 0.95 T at 75 mT (apex), then 1 -> 10 T uniform in 1/B (F_Nyq = 40 T) ---
B_tail = np.round(np.arange(0.2, 0.951, 0.075), 4)
B_main = np.round(1.0 / np.linspace(1.0, 0.1, 73), 4)
B_vec = np.unique(np.hstack((B_tail, B_main)))
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"slow axis: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T ({len(B_tail)} apex + {len(B_main)} uniform-1/B)")

FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9
# Fixed sensitivity: 100 uV = 10 kOhm full scale at 10 nA (run-4 lesson; near-CNP high-B rows may clip - accepted).
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan D=0: n -1.25..+3.25e12 (181 pts co-swept TG/BG, run-5 cal), "
                  "B 0.2..10 T (84 rows: 75 mT apex + uniform-1/B d(1/B)=0.0125), sr1 100 uV, fast_delay 1 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: B slow 0.2 -> 10 T, 84 rows (0.2-0.95 T at 75 mT + 1-10 T uniform 1/B, F_Nyq 40 T); '
              f'n fast {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 cm^-2, 181 pts along D = 0; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    print(f"end state: B = {magnet.field():+.3f} T (stays), gates parked at 0, "
          f"(I_tg, I_bg) = ({k_tg.curr():+.3e}, {k_bg.curr():+.3e}) A")
