# === Landau fan at D = 0 (`landau-fan`), plan step 4: B slow 1 -> 10 T (91 rows, uniform in 1/B) x n fast -1.20 -> +3.20e12 (89 pts, D = 0 co-swept) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, abs. scale = 9.5 nm prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.linspace(-1.20, 3.20, 89), 4)                      # 1e12 cm^-2, 0.05 step
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_n_chk, _D_chk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_n_chk, n_vec, atol=1e-6) and np.abs(_D_chk).max() < 1e-6
B_vec = np.round(field_invB(1.0, 10.0, 91), 5)                         # uniform in 1/B: d(1/B) = 0.01 T^-1 -> F_nyq 50 T, dF 1.1 T
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts) | Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V, "
      f"Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V (limits TG [{TG_MIN},{TG_MAX}] BG [{BG_MIN},{BG_MAX}])")
print(f"slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {len(B_vec)} rows uniform in 1/B (dB {B_vec[1]-B_vec[0]:.4f} T at 1 T, {B_vec[-1]-B_vec[-2]:.3f} T at 10 T)")

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _Tv, _B0 = T_sample(), T_vaporizer(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {_Tv:.3f} K (< 2), B = {_B0:+.4f} T (|B| < 0.05), V_si = {k_si():+.3f} V (0), "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
print(f"precondition drive {sr1.amplitude()} V @ {sr1.frequency()} Hz (1.0 V -> 10 nA), sr1 tau {sr1.time_constant()} s / {sr1.filter_slope()} dB (0.3 / 24)")
assert 1.0 <= _T0 <= 1.5 and _Tv < 2.0 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert abs(sr1.amplitude() - 1.0) < 1e-3 and sr1.time_constant() == 0.3 and sr1.filter_slope() == 24

FAST_DELAY, SLOW_DELAY = 1.0, 3.0   # 1 s = 3.3 tau (uniform ~1-step lag in n, same direction every row); 3 s after flyback = 10 tau
I_TRIP, T_TRIP = 1e-9, 3.0
# Fixed sensitivity (no mid-row autorange): 50 uV = 5 kOhm FS at 10 nA — the setting that resolved SdH in runs 6/7
# (max 530-590 Ohm at 10 T, 11-12 % FS). A rail at the CNP / nu = 0 columns at high B is accepted (not FFT evidence).
sr1.sensitivity(50e-6)
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS), sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: B slow 1 -> 10 T (91 rows, uniform 1/B) x n fast -1.20 -> +3.20e12 (89 pts, D = 0, run-5 cal), "
                  f"sr1 50 uV, fast_delay 1 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 V/nm; n fast {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2 (89 pts, 0.05 step; Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, '
              f'Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f}); B slow 1.0 -> 10.0 T, 91 rows uniform in 1/B (d(1/B) = 0.01); '
              f'cal run 5: c_tg {CAL["c_tg"]:.3e}, c_bg {CAL["c_bg"]:.3e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}; Vsi 0; T base')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, magnet_field, Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample); s.plot('time', magnet.field)

def fan_guard(station, data):
    i_tg, i_bg, T = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if T > T_TRIP:
        print(f"T TRIP at B={float(data[1]):.3f} T: T_sample = {T:.3f} K > {T_TRIP} K")
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # gates parked at 0; field stays where the fan left it (10 T on completion)
    print(f"end: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample {T_sample():.3f} K")
