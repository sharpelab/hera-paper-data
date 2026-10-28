# === Landau fan (`landau-fan-vti`): D = 0 n-line x B, electron side ===
# Step 4 of `investigations/tetralayer-stacking-fs-count.md`. Reads the identity of
# run 6's big tone (29.4 T) by its n-dependence: harmonic-of-7.3 vs ABAB heavy vs
# ABCA singleton vs trilayer BL. Fast axis = paired (Vtg, Vbg) n-line at D = 0.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: 33-pt n-line at D = 0, n = +3.20 -> +1.60e12 (dn = 0.050e12) ---
N_N, D0 = 33, 0.0
ns = np.linspace(3.20, 1.60, N_N)
Ds = D0 * np.ones_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())

# --- slow axis: 91 rows uniform in 1/B, 1.0 -> 10.0 T, d(1/B) = 0.0100 /T ---
B_vec = field_invB(1.0, 10.0, 91)
assert B_vec.max() <= B_SESSION_CAP, B_vec.max()
d_invB = float(abs(np.diff(1.0 / B_vec)[0]))
FAST_DELAY, SLOW_DELAY = 2.1, 1.0      # 7 tau at tau = 0.3 s / 24 dB/oct (rig-card settling floor)
I_TRIP = 1e-9

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: starts at 0), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- sensitivity: fixed for the whole fan, sized on the worst corner (low n x high B) ---
# R(n=1.6, B=0) = 83 Ohm (run 5, D~0); run 6 MR at n=3.2 was x10 to B=10 T; the
# n=1.6/B=10 corner sits at nu ~ 6.6 (QH peak) -> estimate ~2 kOhm, un-measured.
# 100 uV = 10.1 kOhm FS at 10 nA: worst corner ~20 % FS. Saturation is the
# asymmetric failure (`landau-fan` step 1) and a clipped high-B row is unrecoverable.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> {sr1.amplitude()/100e6*1e9:.2f} nA; sr1 sens {sr1.sensitivity()} V "
      f"({sr1.sensitivity()/(sr1.amplitude()/100e6):.0f} Ohm FS); tau {sr1.time_constant()} s, "
      f"slope {sr1.filter_slope()} dB/oct -> fast_delay {FAST_DELAY} s = {FAST_DELAY/sr1.time_constant():.1f} tau")
print(f"n-line: {N_N} pts, n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = {D0:+.2f} V/nm; "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")
print(f"B grid: {len(B_vec)} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {d_invB:.5f} /T "
      f"(Nyquist {1/(2*d_invB):.0f} T; F_L(n_max) = 33.1 T -> 3.0 pts/period)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan: D = {D0} V/nm, n = {ns[-1]:+.2f} to {ns[0]:+.2f}e12 ({N_N} pts), "
                  f"B = {B_vec[0]:.2f} to {B_vec[-1]:.2f} T ({len(B_vec)} rows, uniform 1/B, d(1/B) = {d_invB:.4f}/T), "
                  f"sr1 100 uV, fast_delay {FAST_DELAY} s (7 tau)")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {ns[-1]:+.2f} to {ns[0]:+.2f}e12 ({N_N} pts, dn = {abs(ns[1]-ns[0]):.3f}e12), '
              f'B = {B_vec[0]:.2f} to {B_vec[-1]:.2f} T ({len(B_vec)} rows, uniform in 1/B, d(1/B) = {d_invB:.4f}/T)')
s.add_comment(f'per-column SdH-FFT fan, electron side (run 6 cleaner than run 7); B_lo from the measured onset '
              f'(sdh_onset on run 6 B>=1 T leg: onset_b = 1.00 T, censored); cal run 5: '
              f'ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')

# position the magnet at the fan start before committing the grid (FastBi blocking ramp ~7 min)
magnet.field(float(B_vec[0]))
print(f"positioned: B = {magnet.field():+.4f} T (target {B_vec[0]:.3f})")
assert abs(magnet.field() - B_vec[0]) < 0.02

s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', sr1.P); s.plot('time', sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# field left at 10 T deliberately: the LK mass ladder / firming fan rides it down, never re-traverses.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
