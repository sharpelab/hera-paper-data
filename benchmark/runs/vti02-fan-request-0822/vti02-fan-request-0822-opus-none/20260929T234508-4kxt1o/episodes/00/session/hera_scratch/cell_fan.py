# === Landau fan (`landau-fan`) at D = 0: B slow 0.25 -> 10 T (125 mT) x (Vtg, Vbg) fast along n = -1.22 .. +3.22e12 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_FAST = 111
n_vec = np.linspace(-1.22, 3.22, N_FAST)                      # 1e12 cm^-2, 0.0404e12 step
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
print(f"fast axis: n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f} e12 ({N_FAST} pts, {1e3*(n_vec[1]-n_vec[0]):.1f}e9 step) at D = 0")
print(f"  Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V ({1e3*(Vtg_vec[1]-Vtg_vec[0]):.2f} mV step, margins "
      f"{1e3*(Vtg_vec[0]-TG_MIN):.0f}/{1e3*(TG_MAX-Vtg_vec[-1]):.0f} mV)")
print(f"  Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V ({1e3*(Vbg_vec[1]-Vbg_vec[0]):.2f} mV step, margins "
      f"{1e3*(Vbg_vec[0]-BG_MIN):.0f}/{1e3*(BG_MAX-Vbg_vec[-1]):.0f} mV)")
print(f"  roundtrip (n, D) at the ends: {calc_nD(Vtg_vec[0], Vbg_vec[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}, "
      f"{calc_nD(Vtg_vec[-1], Vbg_vec[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0.25 T), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- slow axis: B uniform, ascending (the magnet is the blocking axis; one monotonic traverse) ---
B_vec = np.round(np.arange(0.25, 10.0001, 0.125), 4)          # 79 rows
assert B_vec.max() <= B_SESSION_CAP
FAST_DELAY, SLOW_DELAY = 0.8, 2.0
I_TRIP = 1e-9

# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm full scale at 10 nA.
sr1.sensitivity(100e-6)
print(f"B rows: {len(B_vec)} x {B_vec[1]-B_vec[0]:.3f} T, {B_vec[0]} -> {B_vec[-1]} T; "
      f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); tau {sr1.time_constant()} s / {sr1.filter_slope()} dB")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan at D = 0: B slow {B_vec[0]}..{B_vec[-1]} T (125 mT, {len(B_vec)} rows) x "
                  f"(Vtg, Vbg) fast along n = {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({N_FAST} pts), run-5 cal, sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line, n = {n_vec[0]:+.3f}..{n_vec[-1]:+.3f}e12 cm^-2 fast ({N_FAST} pts, {1e3*(n_vec[1]-n_vec[0]):.1f}e9 step; '
              f'Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f}); '
              f'B {B_vec[0]}..{B_vec[-1]} T slow, {B_vec[1]-B_vec[0]:.3f} T, ascending; Vsi = 0; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.4e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout (multimegasweep): [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))    # cols 5, 6 -- multimegasweep has 3 axis columns
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T (left where the fan ended -- the next step rides it down), "
          f"(Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
