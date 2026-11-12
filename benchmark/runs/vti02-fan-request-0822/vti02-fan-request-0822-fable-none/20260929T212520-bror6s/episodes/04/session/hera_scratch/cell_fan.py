# === Landau fan at D = 0 (`landau-fan`): fast (Vtg, Vbg) co-swept, n -1.25 -> +3.24e12 (205); slow B 0.2 -> 10 T (99) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.25, 3.24, 205)            # 1e12 cm^-2, dn ~ 0.022
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
B_vec = np.round(np.arange(0.2, 10.0001, 0.1), 4)  # ascending from parked 0 T
assert B_vec.max() <= B_SESSION_CAP
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts): Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}], "
      f"Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}] V; slow: B {B_vec[0]} -> {B_vec[-1]} T ({len(B_vec)} rows)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0.2), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP, T_TRIP = 1e-9, 1.8
# Fixed sensitivity for the whole fan: 200 uV = 20 kOhm FS at 10 nA (gapped-CNP headroom; run-5 lesson).
sr1.sensitivity(200e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (20 kOhm FS); sr0 sens {sr0.sensitivity()} V; "
      f"tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan D=0: fast co-swept (Vtg,Vbg) n -1.25..+3.24e12 (205 pts), slow B 0.2..10 T (99 rows, 0.1 T), "
                  "sr1 200 uV, fast_delay 1.0; cal run 5")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}); '
              f'fast n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12, 205 pts (Vtg {Vtg_vec.min():+.3f}..{Vtg_vec.max():+.3f}, Vbg {Vbg_vec.min():+.3f}..{Vbg_vec.max():+.3f}); '
              f'slow B 0.2 -> 10.0 T, 0.1 T, ascending; Vsi = 0; T = {_T0:.2f} K')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def fan_guard(station, data):
    i_tg, i_bg, t_s = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP or t_s > T_TRIP:
        print(f"GUARD TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A, T={t_s:.3f} K")
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# end state: B = 10 T, gates at n = +3.24e12 — next step rides the field down (never re-traverse); no park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
