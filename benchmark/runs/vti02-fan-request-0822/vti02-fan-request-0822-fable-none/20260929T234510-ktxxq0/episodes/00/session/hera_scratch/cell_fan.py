# === Landau fan (`landau-fan`): n fast along D = 0, B slow 0.5 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.2, 3.2, 111)             # 1e12 cm^-2, delta-n = 0.04e12, D = 0
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
print(f"fast axis: n = {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts) along D = 0 -> "
      f"Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}] V, Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}] V")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan ascends from 0), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"

# --- slow axis: B ascending, two segments (LL features crowd as B^2/F at low B) ---
B_vec = np.unique(np.round(np.hstack((np.arange(0.5, 3.0, 0.025), np.arange(3.0, 10.0001, 0.05))), 4))
assert B_vec.max() <= B_SESSION_CAP
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9
# Fixed sensitivity: 100 uV = 10 kOhm FS at 10 nA (run-5 gatemap choice; CNP column may
# soft-clip at high B if a field-induced gap opens there — accepted, flagged by hera-watch).
sr1.sensitivity(100e-6)
print(f"B: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T (25 mT to 3 T, 50 mT above); "
      f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s; fast/slow delay {FAST_DELAY}/{SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan: n fast {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({len(n_vec)} pts) along D = 0 "
                  f"(run-5 cal), B slow 0.5->3 T 25 mT + 3->10 T 50 mT ({len(B_vec)} rows), Vsi = 0, sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'n fast [-1.2, +3.2]e12 111 pts (0.04e12) along D = 0; B slow 0.5 -> 3 T 25 mT + 3 -> 10 T 50 mT '
              f'({len(B_vec)} rows, ascending from park at 0); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; follows runs 6/7 spot checks')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f} V: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec],
                     [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# field stays at 10 T (never re-traverse; next leg rides it down)
print(f"done: B = {magnet.field():+.3f} T, gates at 0, T = {T_sample():.3f} K")
