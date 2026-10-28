# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +0.8 -> +3.2e12, B 0.8 -> 10 T uniform-1/B ===
from sharpelab_nb.gates import calc_gate_voltages

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(0.8, 3.2, 71)                    # 1e12 cm^-2; dn = 0.0343e12
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
print(f"fast axis: n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = 0, {len(ns)} pts; "
      f"Vtg [{Vtgs.min():+.4f}, {Vtgs.max():+.4f}], Vbg [{Vbgs.min():+.4f}, {Vbgs.max():+.4f}] V")

# --- slow axis: uniform in 1/B (per-column SdH-FFT fan), Nyquist 1/3 per period of F_L(n_max) = 33.1 T ---
F_L_MAX = 33.085                                  # (h/4e) * 3.2e16
B_LO, B_HI = 0.8, 10.0
d_invB_target = 1.0 / (3 * F_L_MAX)
NB = int(np.ceil((1 / B_LO - 1 / B_HI) / d_invB_target)) + 1
invB = np.linspace(1 / B_LO, 1 / B_HI, NB)
B_vec = np.round(1.0 / invB, 4)                   # ascending 0.8 -> 10 T
assert B_vec.max() <= B_SESSION_CAP
assert (invB[0] - invB[1]) <= 1 / (2 * F_L_MAX), "B-axis under Nyquist floor"
print(f"slow axis: {NB} rows, B {B_vec[0]} -> {B_vec[-1]} T, d(1/B) = {invB[0]-invB[1]:.5f} 1/T "
      f"({1/(3*(invB[0]-invB[1]))/F_L_MAX:.2f}x of 1/3-per-period at F_L={F_L_MAX:.1f} T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0, _tau = T_sample(), magnet.field(), sr1.time_constant()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts with the 0.8 T ramp), "
      f"V_si = {k_si():+.3f} V (0), sr1 tau = {_tau} s / slope {sr1.filter_slope()} dB (fast_delay = 6 tau), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert abs(_tau - 0.3) < 0.05, "tau changed on the front panel — fast_delay=1.8 s keyed to 6*0.3 s"
assert magnet.persistent_switch_on() and magnet.output_enabled()

I_TRIP = 1e-9
# Fixed sensitivity 100 uV = 10 kOhm FS at 10 nA: worst corner is low-n x high-B (n=0.8e12 at 10 T, nu ~ 3.3,
# QH-regime Rxx peaks kOhm-scale; session run-4 lesson: >=10x the 1D max, 576 Ohm @ 10 T run 7 -> >= 5.8 kOhm).
sr1.sensitivity(100e-6)
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS); mid-B SdH amplitudes ~10-100 Ohm = 0.1-1% FS — "
      f"resolution traded for headroom; runs 6/7 (50 uV) stay the amplitude reference")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: n +0.8..+3.2e12 (71) at D = 0 (run-5 cal), "
                  f"B 0.8 -> 10 T uniform-1/B ({NB} rows), slow_delay 1, fast_delay 1.8 (6 tau), sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = 0.00 V/nm, n = +0.80 to +3.20e12 cm^-2 (71 pts), '
              f'B = 0.8 to 10 T uniform-1/B ({NB} rows, d(1/B) = {invB[0]-invB[1]:.5f}); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'inherits run-6 settling (6 tau at tau 0.3 s)')

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=1, fast_delay=1.8)
finally:
    # park gates at 0 V (defined state); field stays where it is deliberately — at 10 T when complete;
    # the next move (LK ladder / hole-side ride-down / firming fan) is decided from this fan's read,
    # never re-traversing.
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    print(f"done: B = {magnet.field():+.3f} T, gates parked at 0 V")
