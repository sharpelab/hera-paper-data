# === Landau fan (`landau-fan`), D = 0: B slow 1 -> 10 T uniform in 1/B x n fast -1.25 .. +3.25e12 ===
# Plan step 4. Slow axis = magnet.field (the expensive, blocking axis: traversed once,
# monotonically up). Fast axis = (V_tg, V_bg) co-swept along the run-5-calibrated D = 0 line.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: the D = 0 line, hole edge -> electron edge (85 pts, 53.6e9 cm^-2 step) ---
N_FAST = 85
n_vec = np.linspace(-1.25, 3.25, N_FAST)              # 1e12 cm^-2; TG limit binds at -1.27 / +3.27
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, **CAL)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
_nrt, _Drt = calc_nD(Vtg_vec, Vbg_vec, **CAL)
assert np.allclose(_nrt, n_vec) and np.allclose(_Drt, 0.0, atol=1e-12)
print(f"fast: n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f} e12 cm^-2 at D = 0, {N_FAST} pts ({n_vec[1]-n_vec[0]:.4f}e12 step); "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V ({np.ptp(Vtg_vec):.3f} V span, {abs(Vtg_vec[1]-Vtg_vec[0])*1e3:.1f} mV step), "
      f"Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V ({np.ptp(Vbg_vec):.3f} V span)")

# --- slow axis: uniform in 1/B (SdH is periodic in 1/B -> sdh_fft needs no resample) ---
N_B, B_LO, B_HI = 130, 1.0, 10.0
B_vec = field_invB(B_LO, B_HI, N_B)                   # ascending; magnet sits at 0 T
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
_dinv = abs(np.diff(1/B_vec)).max()
print(f"slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows uniform in 1/B; d(1/B) = {_dinv:.5f} 1/T "
      f"-> F_Nyquist = {1/(2*_dinv):.1f} T; dF_resolution = {1/(1/B_vec.min()-1/B_vec.max()):.2f} T; "
      f"dB {abs(np.diff(B_vec)).min():.4f} .. {abs(np.diff(B_vec)).max():.3f} T")

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: pre-ramp goes to {B_LO} T), "
      f"V_si = {k_si():+.3f} V (0), Vtg = {k_tg.volt():+.4f} V, Vbg = {k_bg.volt():+.4f} V, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, "
      f"output {magnet.output_enabled()}, settle_s {magnet.settle_s} s")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- sensitivity: one fixed setting for the whole fan (no autorange mid-row).
# 200 uV = 20 kOhm full scale at 10 nA -> 38x run 6's maximum (530 Ohm) and 60x run 7's,
# per the run-4 lesson (size for the map's largest feature, not the 1D peak). The one place
# that may still clip is the CNP itself at high B (the nu = 0 state, |n| < ~0.1e12, ~3 columns);
# a clip there is a reportable bound on the nu = 0 gap, not a loss of the fan.
sr1.sensitivity(200e-6)
FAST_DELAY, SLOW_DELAY = 1.0, 3.0    # SLOW_DELAY = 10 tau, covering the row-start gate flyback
I_TRIP = 1e-9
print(f"drive {sr1.amplitude()} V / {meas_config['bias_resistor']:.0e} Ohm -> {sr1.amplitude()/meas_config['bias_resistor']*1e9:.2f} nA; "
      f"sr1 sens {sr1.sensitivity()} V ({sr1.sensitivity()/(sr1.amplitude()/meas_config['bias_resistor']):.0f} Ohm FS), "
      f"tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan at D = 0: B slow {B_LO}->{B_HI} T, {N_B} rows uniform in 1/B; "
                  f"(Vtg,Vbg) co-swept fast along D = 0, n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12, {N_FAST} pts; "
                  f"Vsi = 0, sr1 200 uV, fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: slow magnet.field {B_LO} -> {B_HI} T, {N_B} rows uniform in 1/B '
              f'(F_Nyq {1/(2*_dinv):.1f} T, dF {1/(1/B_vec.min()-1/B_vec.max()):.2f} T); '
              f'fast (k_tg.volt, k_bg.volt) co-swept on the D = 0 line, n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2, '
              f'{N_FAST} pts ({n_vec[1]-n_vec[0]:.4f}e12 step); Vsi = 0; T_sample {_T0:.3f} K; '
              f'cal run 5: c_tg {CAL["c_tg"]:.4e}, c_bg {CAL["c_bg"]:.4e} F/m^2 (geometry prior scale), '
              f'ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.4f} V/nm')

# park the gates at the fast-axis start, then pre-ramp the field (blocking, ~7.3 min)
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)
s.ramp(magnet.field, B_vec[0])
print(f"pre-ramp done: B = {magnet.field():+.4f} T (target {B_vec[0]:.3f})")
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
I_TG, I_BG = 5, 6
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[I_TG])), abs(float(data[I_BG]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates parked at 0 V; field left at 10 T on purpose — the conditional follow-ups
    # (plan steps 5/6) ride it back down rather than re-traversing (66 min each way).
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
          f"T_sample = {T_sample():.3f} K")
