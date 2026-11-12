# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +2.0..+3.2e12, B 0.7 -> 10 T ===
# Slow axis = magnet.field, uniform in 1/B (per-column SdH-FFT fan).
# Fast axis = paired (k_tg, k_bg) n-line at fixed D = 0.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: n-line at D = 0. N_n = 37 is the LL-ray Nyquist floor at B_lo
#     (ray spacing dn = 4(e/h)B_lo = 0.0677e12 -> grid dn <= 0.0339e12; used 0.0333e12).
n_lo, n_hi, N_n = 2.0, 3.2, 37                 # 1e12 cm^-2
D0 = 0.0                                        # V/nm
ns = np.linspace(n_lo, n_hi, N_n)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns),
                                CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
_dn = ns[1] - ns[0]
print(f"n-line: {N_n} pts, n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 (dn {_dn:.4f}e12), D = {D0:+.2f} V/nm")
print(f"   Vtg {Vtgs.min():+.4f} .. {Vtgs.max():+.4f} V (limit {TG_MIN}..{TG_MAX}, headroom {TG_MAX-Vtgs.max():+.4f})")
print(f"   Vbg {Vbgs.min():+.4f} .. {Vbgs.max():+.4f} V (limit {BG_MIN}..{BG_MAX})")

# --- slow axis: uniform in 1/B. d(1/B) = 7.464e-3 -> f_Nyq = 67.0 T = 2.03 F_L(n_max = 3.2e12).
B_LO, B_HI, N_B = 0.7, 10.0, 179
B_vec = field_invB(B_LO, B_HI, N_B)
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP
_dinv = float(np.median(-np.diff(1.0 / B_vec)))
_FL = cst.h / (4 * cst.e) * n_hi * 1e16
print(f"B grid: {N_B} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T; d(1/B) = {_dinv:.6f} 1/T "
      f"-> f_Nyq {1/(2*_dinv):.1f} T = {1/(2*_dinv)/_FL:.2f} F_L(n_max={n_hi}e12, F_L={_FL:.2f} T)")
print(f"   row dB: min {np.min(np.diff(B_vec))*1e3:.1f} mT, max {np.max(np.diff(B_vec)):.3f} T; "
      f"dF = {1/(1/B_LO - 1/B_HI):.2f} T")

FAST_DELAY, SLOW_DELAY = 1.8, 3.0   # 6 tau (per-column SdH-FFT fan) / 10 tau over the row-start flyback
I_TRIP = 1e-9

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: starts from the handoff 0 T), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# Fixed sensitivity for the whole fan (no autorange mid-row), inherited from the spot checks:
# 50 uV = 5 kOhm FS at 10 nA. Worst corner n_min x B_max ~ 1 kOhm = 20 % FS.
sr1.sensitivity(50e-6)
print(f"sr1 sens {sr1.sensitivity()} V ({sr1.sensitivity()/10e-9:.0f} Ohm FS at 10 nA), "
      f"tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct -> fast_delay {FAST_DELAY} s "
      f"= {FAST_DELAY/sr1.time_constant():.0f} tau; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan electron side: D = {D0:+.2f} V/nm, n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 cm^-2 "
                  f"({N_n} pts), B = {B_vec[0]:.3f} to {B_vec[-1]:.3f} T ({N_B} rows, uniform 1/B, "
                  f"d(1/B) = {_dinv:.6f}), sr1 50 uV, fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('landau-fan')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 cm^-2 ({N_n} pts, dn {_dn:.4f}e12), '
              f'B = {B_vec[0]:.3f} to {B_vec[-1]:.3f} T ({N_B} rows, uniform in 1/B, d(1/B) = {_dinv:.6f} 1/T, '
              f'f_Nyq {1/(2*_dinv):.1f} T = 2.03 F_L, dF {1/(1/B_LO - 1/B_HI):.2f} T); '
              f'Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f}; Vsi = 0; '
              f'sr1 sens 50 uV, tau 0.3 s/24 dB, fast_delay {FAST_DELAY} s (6 tau), slow_delay {SLOW_DELAY} s; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f}; per-column SdH-FFT fan for tetralayer-stacking-fs-count Step 4')

# Position: gates to the row start, then the magnet to B_lo (blocking, ~5 min from 0 T).
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
magnet.field(B_vec[0])
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', T_sample); s.plot('time', sr1.P)

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
# Field deliberately left at 10 T: the LK mass split (Verify) rides it back down.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
      f"T_sample = {T_sample():.3f} K")
