# === Landau fan, electron side, D = 0 (`landau-fan-vti`): n_cal +1.50 -> +3.20e12 (35) x B 1.0 -> 6.0 T uniform-1/B (85) ===
# Per-column SdH-FFT fan for tetralayer-stacking-fs-count Step 4. Grid inherits the run-6 spot check
# (Delta(1/B) = 0.0099 = 1/(3 F_L,cal) at n_hi; sr1 50 uV; tau 0.3 s / 24 dB). Magnet ascends from where it sits.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration (run 5; ratio data-calibrated, scale geometry prior; runs 6 QH minima say n_true ~ 0.906 n_cal) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0
ns = np.round(np.arange(1.50, 3.2001, 0.05), 4)            # 35 pts, dn = 0.05e12 (>= 2 per LL ray period at 1 T)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs, Vbgs)
B_LO, B_HI, N_B = 1.0, 6.0, 85
B_vec = field_invB(B_LO, B_HI, N_B)                         # ascending, uniform in 1/B
assert B_vec.min() > 0 and np.abs(B_vec).max() <= B_SESSION_CAP
FAST_DELAY, SLOW_DELAY = 2.4, 3.0                           # 8 tau at 24 dB/oct (floor 7-10 tau); 10 tau after flyback
SENS = 50e-6                                                 # 5 kOhm FS at 10 nA — inherited from runs 6/7
I_TRIP, RAIL_FRAC, RAIL_MAX, T_MAX = 1e-9, 0.95, 10, 2.0
print(f"n_cal {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({len(ns)}), D = {D0}; Vtg {Vtgs[0]:+.4f}->{Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f}->{Vbgs[-1]:+.4f} V; "
      f"roundtrip end n,D = {calc_nD(Vtgs[-1], Vbgs[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")
print(f"B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {len(B_vec)} rows, d(1/B) = {abs(np.diff(1/B_vec)).mean():.5f} 1/T, dB {np.diff(B_vec)[0]*1e3:.0f} -> {np.diff(B_vec)[-1]*1e3:.0f} mT")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _Tv, _B0 = T_sample(), T_vaporizer(), magnet.field()
_tau, _slope, _amp = sr1.time_constant(), sr1.filter_slope(), sr1.amplitude()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {_Tv:.3f} K, B = {_B0:+.4f} T (|B| < 0.05; ramps to {B_LO} T), "
      f"V_si = {k_si():+.3f} V (0), heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), "
      f"PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"sr1 tau {_tau} s / {_slope} dB (0.3 / 24), drive {_amp} V (1.0 -> 10 nA), sr0 sens {sr0.sensitivity()} V")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} off base"
assert abs(_B0) < 0.05, f"magnet not at ~0 T: {_B0}"
assert abs(k_si()) < 0.01 and heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert _tau == 0.3 and _slope == 24, "lock-in settling changed — FAST_DELAY priced on tau 0.3 s / 24 dB"
assert abs(_amp - 1.0) < 1e-6, "drive amplitude changed — sensitivity sized on 10 nA"

sr1.sensitivity(SENS)
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron D=0: n_cal {ns[0]:+.2f}->{ns[-1]:+.2f}e12 (35), B {B_LO}->{B_HI} T uniform-1/B (85), "
                  f"fast_delay {FAST_DELAY} s, sr1 50 uV; cal run 5; stacking FS-count Step 4")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 cm^-2 (cal run 5: ratio 0.773, n_offset -0.089, D_offset -0.013; '
              f'QH scale n_true/n_cal ~ 0.906 from run 6), B = {B_LO} to {B_HI} T uniform in 1/B, {N_B} rows x {len(ns)} pts, '
              f'fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, sr1 50 uV, tau 0.3 s/24 dB; investigation tetralayer-stacking-fs-count Step 4')

# --- position: gates to the first column, magnet 0 -> B_LO (blocking ramp ~7 min) ---
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
magnet.field(B_LO)
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")

# row layout: [time, magnet_field, k_tg_volt, k_bg_volt, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_rails = []
def fan_guard(station, data):
    i_tg, i_bg, T, x1 = abs(float(data[5])), abs(float(data[6])), float(data[4]), abs(float(data[9]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f}, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if T > T_MAX:
        print(f"T TRIP: T_sample = {T:.3f} K > {T_MAX} K at B={float(data[1]):.3f}")
        station.interrupt_requested = True
    if x1 >= RAIL_FRAC * SENS:
        _rails.append((float(data[1]), float(data[2]), x1))
        print(f"RAIL sr1 |X| = {x1*1e6:.1f} uV at B={float(data[1]):.3f}, Vtg={float(data[2]):+.4f} ({len(_rails)}/{RAIL_MAX})")
        if len(_rails) >= RAIL_MAX:
            station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# field deliberately left at the fan's top (6 T): the LK-mass series (Verify) rides down from here; close-out owns 0 T.
print(f"done: B = {magnet.field():+.4f} T (left for the LK ride-down), gates parked ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), rails {len(_rails)}")
