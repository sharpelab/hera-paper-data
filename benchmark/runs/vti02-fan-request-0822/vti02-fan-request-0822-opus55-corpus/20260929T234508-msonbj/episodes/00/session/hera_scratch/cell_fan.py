# === Landau fan (`landau-fan-vti`, for `tetralayer-stacking-fs-count` Step 4): electron side, D = 0 ===
# fast: paired (Vtg, Vbg) n-line n = +1.50 -> +3.24e12 at D = 0 (37 pts); slow: magnet.field 1.0 -> 8.0 T uniform in 1/B (89 rows)
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_N = 1.50, 3.24, 37          # 1e12 cm^-2; dn = 0.0483 <= half the ray spacing 4eB/h = 0.0967 at B_lo
B_LO, B_HI, N_B = 1.0, 8.0, 89            # T; d(1/B) = 0.00994 1/T = 1/(3.0 F_L(3.24) = 33.5 T)
D0 = 0.0
ns = np.linspace(N_LO, N_HI, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
B_vec = field_invB(B_LO, B_HI, N_B)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
_n_chk, _D_chk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"n-line: {ns[0]:+.3f} -> {ns[-1]:+.3f}e12 ({N_N} pts, dn {ns[1]-ns[0]:.4f}); Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, "
      f"Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V; roundtrip max|D| {np.abs(_D_chk).max():.1e}")
print(f"B: {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows, d(1/B) {1/B_vec[0]-1/B_vec[1]:.5f} 1/T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _Tv, _B0 = T_sample(), T_vaporizer(), magnet.field()
_hs, _hv = heater.sample_range(), heater.vaporizer_range()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {_Tv:.3f} K (<1.5), heater ranges {_hs}/{_hv} (0/0), "
      f"B = {_B0:+.4f} T (|B|<0.05, handoff left 0 T), V_si = {k_si():+.3f} V (0), drive {sr1.amplitude()} V (1.0 -> 10 nA), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS {magnet.persistent_switch_on()} / output {magnet.output_enabled()}, "
      f"sr1 tau {sr1.time_constant()} s / {sr1.filter_slope()} dB (0.3 / 24)")
assert 1.0 <= _T0 <= 1.5 and _Tv < 1.5 and _hs == 0 and _hv == 0, "not at base / heater on"
assert abs(_B0) < 0.05 and abs(k_si()) < 0.01 and abs(sr1.amplitude() - 1.0) < 1e-3
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24, "tau/slope changed - dwell sizing assumes 0.3 s / 24 dB"

# --- lock-in: fixed sensitivity for the whole fan (the handoff restored sr1 to 2 uV - set it explicitly) ---
SENS = 50e-6          # 5 kOhm FS at 10 nA - run 6/7's setting; worst corner (n=1.5, B=8 T) sized below
sr1.sensitivity(SENS)
FAST_DELAY, SLOW_DELAY = 1.8, 3.0         # 6 tau at tau = 0.3 s / 24 dB; slow_delay covers the 0.5 V flyback
I_TRIP, T_TRIP = 1e-9, 2.0
print(f"sr1 sens {sr1.sensitivity()} V ({sr1.sensitivity()/10e-9:.0f} Ohm FS), sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti: D = {D0} V/nm, n = {N_LO} to {N_HI}e12 ({N_N}), B = {B_LO} to {B_HI} T uniform 1/B ({N_B}), "
                  f"run-5 cal, sr1 50 uV, fast_delay {FAST_DELAY} s; tetralayer-stacking-fs-count step 4 (electron side)")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {N_LO} to {N_HI}e12 cm^-2 ({N_N} pts, paired Vtg/Vbg), B = {B_LO} to {B_HI} T field_invB ({N_B} rows, d(1/B) = 0.00994); '
              f'per-column SdH-FFT fan for tetralayer-stacking-fs-count step 4; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}; sr1 50 uV, tau 0.3 s / 24 dB, fast_delay 1.8 s')

# --- position: gates to the row start, field to B_lo (blocking ramp, ~7.5 min from 0 T) ---
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
magnet.field(B_vec[0])
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_rail = {"n": 0}
def fan_guard(station, data):
    i_tg, i_bg, T = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if T > T_TRIP:
        print(f"T TRIP: T_sample = {T:.3f} K > {T_TRIP} K at B={float(data[1]):.3f} T")
        station.interrupt_requested = True
    if abs(float(data[9])) > 0.95 * SENS:
        _rail["n"] += 1
        if _rail["n"] in (1, 10, 100):
            print(f"RAIL #{_rail['n']}: |sr1.X| = {abs(float(data[9])):.3e} V at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}")
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates park at 0; the field is deliberately LEFT at its last row (8 T at completion): the LK/field-sweep follow-ups ride it down
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.4f} T (left), gates parked ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}); rail count {_rail['n']}")
