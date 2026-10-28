# === Landau fan at D = 0 (`landau-fan`): (Vtg, Vbg) co-swept along the D=0 line, n -1.25 -> +3.24e12 (129 pts) x B 0 -> 10 T (50 mT, 201 rows) ===
from sharpelab_nb.gates import calc_gate_voltages

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)  # run-5 cnp-and-dline-calibration
n_vec = np.linspace(-1.25, 3.24, 129)          # 1e12 cm^-2, 0.035e12/pt
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
B_vec = np.round(np.arange(0.0, 10.0001, 0.05), 3)   # 201 rows, 50 mT
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
assert B_vec.max() <= B_SESSION_CAP
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 (129 pts): Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f}, "
      f"Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f}; slow: B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.02: fan starts at 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.02 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not at 1"

FAST_DELAY, SLOW_DELAY = 1.0, 3.0   # fast_delay 1.0 s = 3.3 tau, bent knowingly (gatemap run-5 precedent)
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange mid-row): 500 uV = 50 kOhm FS at 10 nA — sized for a gapped CNP at 10 T.
sr1.sensitivity(500e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (50 kOhm FS); sr0 sens {sr0.sensitivity()} V; "
      f"tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = "landau-fan: D=0 line (run-5 cal), n -1.25..+3.24e12 129 pts co-swept, B 0..10 T 50 mT 201 rows, sr1 500 uV"
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line (run-5 cal: ratio 0.773, n_offset -0.089e12, D_offset -0.013 V/nm): n -1.25 -> +3.24e12, 129 pts '
              f'(Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f}); '
              f'B 0 -> 10 T, 50 mT, 201 rows; sr1 500 uV; fast_delay 1.0, slow_delay 3.0; T_sample {_T0:.2f} K')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg(fast bundle), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
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
# field stays at 10 T — the next step rides it down (never re-traverse)
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
