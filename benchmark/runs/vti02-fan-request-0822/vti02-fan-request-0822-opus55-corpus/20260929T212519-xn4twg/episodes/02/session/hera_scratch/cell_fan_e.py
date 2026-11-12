# === Landau fan, electron side, D = 0 (`landau-fan-vti` / tetralayer-stacking-fs-count Step 4) ===
# Slow: magnet.field uniform in 1/B, 1.0 -> 10.0 T, 103 rows (d(1/B) = 0.00882 T^-1).  Fast: paired (Vtg, Vbg) n-line at D = 0,
# n = +3.22 -> +1.80e12, 31 pts (dn = 0.047e12).  Fixed sr1 50 uV (5 kOhm FS), tau 0.3 s / 24 dB, fast_delay 2.1 s (7 tau).
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
# --- session calibration, run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_HI, N_LO, N_N, D0 = 3.22, 1.80, 31, 0.0
B_LO, B_HI, N_B = 1.0, 10.0, 103
ns = np.linspace(N_HI, N_LO, N_N); Ds = D0 * np.ones(N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.round(Vtgs, 5), np.round(Vbgs, 5)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
B_vec = field_invB(B_LO, B_HI, N_B)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
nr, Dr = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast: n {ns[0]:+.3f} -> {ns[-1]:+.3f}e12 ({N_N} pts, dn {ns[0]-ns[1]:.4f}); Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f}; "
      f"roundtrip max|D| {np.abs(Dr).max():.1e}")
print(f"slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows uniform 1/B, d(1/B) = {1/B_vec[0]-1/B_vec[1]:.5f} T^-1 "
      f"(Nyquist {1/(2*(1/B_vec[0]-1/B_vec[1])):.1f} T)")
# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _Tv, _B0 = T_sample(), T_vaporizer(), magnet.field()
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {_Tv:.3f} K, B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"sr1 tau {_tau} s slope {_slope} dB (0.3/24: dwell priced on it), nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} off base"
assert abs(_B0) < 0.05, f"magnet not at 0: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "a heater is on"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert _tau == 0.3 and _slope == 24, f"lock-in settling changed: tau {_tau}, slope {_slope}"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
# --- fixed acquisition (inherited from spot checks runs 6/7): sr1 50 uV = 5 kOhm FS at 10 nA; sr0 20 mV ---
sr1.sensitivity(50e-6); sr0.sensitivity(20e-3)
FAST_DELAY, SLOW_DELAY = 2.1, 3.0          # 7 tau at 24 dB/oct per point; 10 tau after each flyback (+ the driver's 3 s field settle)
I_TRIP = 1e-9
print(f"drive {sr1.amplitude()} V -> {sr1.amplitude()/100e6*1e9:.1f} nA; sr1 sens {sr1.sensitivity()} V; sr0 sens {sr0.sensitivity()} V; settle_s {magnet.settle_s} s")
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron D=0: n {N_HI:+.2f} -> {N_LO:+.2f}e12 ({N_N}), B {B_LO} -> {B_HI} T uniform 1/B ({N_B} rows), "
                  f"sr1 50 uV, fast_delay {FAST_DELAY} s, cal run 5")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {N_LO} to {N_HI} e12 cm^-2 ({N_N} pts), B = {B_LO} to {B_HI} T uniform in 1/B ({N_B} rows, d(1/B) {1/B_vec[0]-1/B_vec[1]:.5f}); '
              f'tetralayer-stacking-fs-count Step 4 (electron side); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.4f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f}; sr1 50 uV, tau 0.3 s/24 dB, fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s')
# --- position: gates to the first fan point, magnet 0 -> 1.0 T (blocking, ~7.5 min) ---
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
magnet.field(B_vec[0])
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)
_rail = {"n": 0}
def leak_and_rail_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[9])) > 0.95 * 50e-6:
        _rail["n"] += 1
        if _rail["n"] in (1, 10, 100):
            print(f"sr1 near rail (#{_rail['n']}) at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}: X={float(data[9]):.3e} V")
s.register_run_after(leak_and_rail_guard, ())
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.4f} T (held: next step rides it down), gates parked ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
          f"T_sample = {T_sample():.3f} K, sr1 near-rail points = {_rail['n']}")
