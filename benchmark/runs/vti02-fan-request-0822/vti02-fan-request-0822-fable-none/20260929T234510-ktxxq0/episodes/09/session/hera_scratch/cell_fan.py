# === Landau fan at D = 0 (`landau-fan`): n fast -1.25 -> +3.25e12 (181), B slow 1 -> 10 T (121 rows, 75 mT) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.25, 3.25, 181)                    # 1e12 cm^-2, dn = 0.025
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
B_vec = np.round(np.arange(1.0, 10.0001, 0.075), 4)      # ascending, ends at 10 T
assert B_vec.max() <= B_SESSION_CAP
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts); Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, "
      f"Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V | slow: B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan ramps up from 0), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 200 uV = 20 kOhm FS at 10 nA (CNP stripe clips >~21 kOhm at high B
# -- the clip marks the nu=0 gap; SdH features 50-600 Ohm stay >= 0.25 % FS).
sr1.sensitivity(200e-6)
print(f"sr1 sens {sr1.sensitivity()} V (20 kOhm FS), tau {sr1.time_constant()} s; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan: n fast -1.25..+3.25e12 (181, dn 0.025) along D = 0 (run-5 cal), "
                  "B slow 1..10 T (121 rows, 75 mT), sr1 200 uV, fast_delay 1.0")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: n -1.25 -> +3.25e12 cm^-2 fast (181 pts, dn 0.025), B 1 -> 10 T slow (121 rows, 75 mT); '
              f'Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'sr1 200 uV (20 kOhm FS), fast_delay 1.0 s')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
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

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=1.0, fast_delay=1.0)
# ends at 10 T, n = +3.25e12 -- no park: the next step rides the field down (never re-traverse).
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, "
      f"T = {T_sample():.3f} K")
