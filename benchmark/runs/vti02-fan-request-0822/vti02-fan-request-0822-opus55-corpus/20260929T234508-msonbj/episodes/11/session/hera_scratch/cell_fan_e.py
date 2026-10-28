# === Landau fan, electron side, D = 0 (`landau-fan-vti`, for tetralayer-stacking-fs-count Step 4) ===
# n 1.4 -> 3.2e12 (61 pts, fast, paired Vtg/Vbg), B 0.8 -> 5.0 T uniform in 1/B (106 rows, slow, ascending)
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_N, D0 = 1.4, 3.2, 61, 0.0          # 1e12 cm^-2, V/nm
B_LO, B_HI, N_B = 0.8, 5.0, 106                    # T; d(1/B) = 0.0100 1/T = 1/(3 F_L(3.2e12))
ns = np.linspace(N_LO, N_HI, N_N); Ds = D0 * np.ones(N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs, Vbgs)
B_vec = field_invB(B_LO, B_HI, N_B)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
dinv = 1 / B_vec[0] - 1 / B_vec[1]
print(f"fast: n {ns[0]:+.2f}..{ns[-1]:+.2f}e12 ({N_N} pts, dn {ns[1]-ns[0]:.3f}e12), D = {D0}; Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f} V")
print(f"slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows uniform 1/B, d(1/B) = {dinv:.5f} 1/T (Nyquist {1/(2*dinv):.1f} T; F_L(3.2e12) = 33.1 T)")
# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {T_vaporizer():.3f} K, B = {_B0:+.4f} T (|B|<0.05: fan pre-positions 0 -> {B_LO} T), "
      f"V_si = {k_si():+.3f} V (0), heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "a heater is on — fan assumes base T"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
_amp, _frq, _tau, _slope = sr1.amplitude(), sr1.frequency(), sr1.time_constant(), sr1.filter_slope()
print(f"lock-in: drive {_amp} V @ {_frq} Hz (1.0 V / 13.777 Hz -> 10 nA), sr1 tau {_tau} s / {_slope} dB (0.3 s / 24 dB, operator-set — read only), sr0 tau {sr0.time_constant()} s")
assert abs(_amp - 1.0) < 1e-3 and abs(_frq - 13.777) < 1e-3 and _tau == 0.3 and _slope == 24
# Fixed sensitivity for the whole fan (inherited from runs 6/7): 50 uV = 5 kOhm FS at 10 nA.
# Worst corner n = 1.4e12 x 5 T: R(0 T) = 90 Ohm (run 5) x QH-regime MR (runs 6/7: <= 4-6x) ~ 0.5 kOhm -> ~10 % FS.
sr1.sensitivity(50e-6)
SENS = sr1.sensitivity()
print(f"sr1 sens {SENS} V (5 kOhm FS), sr0 sens {sr0.sensitivity()} V")
FAST_DELAY, SLOW_DELAY = 2.1, 2.0     # 7 tau at 24 dB (settle floor); slow_delay after each field step (driver adds 3 s settle)
I_TRIP, T_TRIP = 1e-9, 1.8
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron D=0: n {N_LO}..{N_HI}e12 ({N_N}), B {B_LO}->{B_HI} T uniform-1/B ({N_B}), "
                  f"sr1 50 uV, fast_delay {FAST_DELAY} s; cal run 5; for tetralayer-stacking-fs-count Step 4")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {N_LO} to {N_HI}e12 cm^-2 ({N_N} pts, paired Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f} / Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f}), '
              f'B = {B_LO} to {B_HI} T uniform in 1/B ({N_B} rows, d(1/B) {dinv:.4f}); per-column SdH-FFT fan, electron side; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'investigation tetralayer-stacking-fs-count Step 4; inputs sdh-spot-check runs 6/7')
# --- position: gates to the first n point, field 0 -> B_LO (blocking, ~6 min) ---
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
magnet.field(B_vec[0])
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)
_rail = {"n": 0}
def fan_guard(station, data):
    i_tg, i_bg, T = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if T > T_TRIP:
        print(f"T TRIP at B={float(data[1]):.3f} T: T_sample = {T:.3f} K > {T_TRIP} K")
        station.interrupt_requested = True
    if abs(float(data[9])) > 0.95 * SENS:
        _rail["n"] += 1
        if _rail["n"] <= 5 or _rail["n"] % 50 == 0:
            print(f"RAIL sr1 at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}: |X|={abs(float(data[9])):.3e} V (count {_rail['n']})")
s.register_run_after(fan_guard, ())
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# field stays at 5 T deliberately: the next step (LK mass split / hole-side read) rides it down.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), rail count {_rail['n']}")
