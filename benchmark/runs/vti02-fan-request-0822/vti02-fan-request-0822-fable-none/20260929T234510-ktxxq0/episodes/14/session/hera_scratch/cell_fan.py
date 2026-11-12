# === Landau fan at D = 0 (`landau-fan`): B slow 0.5 -> 10 T uniform-1/B (220 rows), n fast -1.26 -> +3.24e12 (91 pts) ===
from sharpelab_nb.gates import calc_gate_voltages

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.26, 3.24, 91)                     # 1e12 cm^-2, dn = 0.05
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
print(f"fast axis: n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 at D = 0 -> Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}], "
      f"Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}] V")

# --- field rows: uniform in 1/B, ascending 0.5 -> 10 T (magnet sits at 0; low-B rows first, cheap ramps) ---
B_vec = np.round(1.0 / np.linspace(1 / 0.5, 1 / 10.0, 220), 4)
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"slow axis: {len(B_vec)} rows, B {B_vec[0]} -> {B_vec[-1]} T uniform-1/B; "
      f"FFT dF = {1/(1/B_vec[0]-1/B_vec[-1]):.2f} T, Nyquist {len(B_vec)/(2*(1/B_vec[0]-1/B_vec[-1])):.0f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.02), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.02 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"

# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA (run-5 lesson: size to the map's
# worst corner). Known trade: the nu = 0 CNP column can exceed 10 kOhm at high B and clip — accepted,
# gap positions survive clipping and the SdH columns need the dynamic range.
sr1.sensitivity(100e-6)
I_TRIP = 1e-9
print(f"drive {sr1.amplitude()} V -> ~10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); tau {sr1.time_constant()} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan: D = 0 (run-5 cal), n -1.26..+3.24e12 fast (91 pts), B 0.5 -> 10 T uniform-1/B slow (220 rows), "
                  "sr1 100 uV, fast_delay 1.0, slow_delay 3.0")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 fast 91 pts (dn 0.05); B {B_vec[0]}..{B_vec[-1]} T slow '
              f'220 rows uniform-1/B ascending; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f}; sr1 100 uV; stacking-call dataset (plan step 4)')
s.ramp(k_tg.volt, Vtg_vec[0]); s.ramp(k_bg.volt, Vbg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg (fast bundle), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=3.0, fast_delay=1.0)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T (left at high field), gates parked at 0: "
          f"(Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V")
