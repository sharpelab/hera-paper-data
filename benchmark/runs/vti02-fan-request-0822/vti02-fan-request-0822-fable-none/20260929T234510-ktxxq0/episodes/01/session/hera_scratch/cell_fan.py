# === Landau fan (`landau-fan`): n fast along D = 0 [-1.25, +3.25]e12 (91 pts), B slow 1 -> 10 T uniform-1/B (140 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.arange(-1.25, 3.2501, 0.05)              # 1e12 cm^-2, 91 pts along D = 0
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
B_vec = field_invB(1.0, 10.0, 140)                  # uniform in 1/B: d(1/B) = 6.5e-3 -> F_Nyq = 77 T; FFT dF = 1.11 T
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() >= 0.99
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9
print(f"fan: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 x B {B_vec[0]:.2f}..{B_vec[-1]:.2f} T ({len(n_vec)} x {len(B_vec)}); "
      f"Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}], Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}]")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts with the 0->1 T ramp), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

# Fixed sensitivity for the whole fan: 200 uV = 20 kOhm FS at 10 nA. Sized to the unknown CNP
# column at high B (gatemap lesson, run 4: the extreme feature sets R_max, not the 1D peaks);
# branch oscillations at 50-600 Ohm sit at 0.25-3 % FS, fine for the FFT. If the D = 0 CNP
# gap exceeds 20 kOhm at high B that column rails -- accepted and itself a gap read (R >= FS).
sr1.sensitivity(200e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (20 kOhm FS); "
      f"sr0 sens {sr0.sensitivity()} V; tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan: n fast -1.25..+3.25e12 (91, 0.05e12) co-swept (TG,BG) on the run-5 D=0 line; "
                  "B slow 1->10 T uniform-1/B (140); sr1 200 uV; ends 10 T, gates park at 0")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'n fast [-1.25, +3.25]e12 91 pts (0.05e12) along D = 0 (co-swept Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, '
              f'Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f}); B slow 1 -> 10 T uniform-1/B 140 rows (F_Nyq 77 T, dF 1.11 T); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
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
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # gates park at 0; field stays at 10 T for the next step
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
