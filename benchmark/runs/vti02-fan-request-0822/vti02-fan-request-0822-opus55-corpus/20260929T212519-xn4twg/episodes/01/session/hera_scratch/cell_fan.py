# === Landau fan (`landau-fan-vti`) for the stacking call: electron side, D = 0 (region-A cal, run 5) ===
# Slow: magnet.field 0.8 -> 5.0 T, 78 rows UNIFORM IN 1/B (d(1/B) = 0.01364 1/T; Nyquist 36.7 T vs F_L(3.25e12) = 33.6 T at scale 1).
# Fast: paired (Vtg, Vbg) n-line at D = 0, n = +3.25 -> +2.00e12 nominal, 36 pts (dn = 0.0357e12; 2.2 pts per LL period at B_lo).
# Dwell 1.8 s = 6 tau (tau 0.3 s / 24 dB), per-column SdH FFT fan. sr1 fixed at 20 uV = 2 kOhm FS.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration (run 5, cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_HI, N_LO, N_N, D0 = 3.25, 2.00, 36, 0.0          # 1e12 cm^-2, V/nm
B_LO, B_HI, N_B = 0.8, 5.0, 78                     # T
ns = np.linspace(N_HI, N_LO, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
B_vec = 1.0 / np.linspace(1.0 / B_LO, 1.0 / B_HI, N_B)          # uniform in 1/B, ascending in B
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP
_nr, _Dr = calc_nD(Vtgs[[0, -1]], Vbgs[[0, -1]], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast n-line: n {ns[0]:+.3f} -> {ns[-1]:+.3f}e12 ({N_N} pts), D = {D0}; Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} V, "
      f"Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V; roundtrip n {_nr}, D {_Dr}")
print(f"slow B: {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows, d(1/B) = {1/B_vec[0]-1/B_vec[1]:.5f} 1/T, "
      f"dB {(B_vec[1]-B_vec[0])*1e3:.1f} mT (first) .. {(B_vec[-1]-B_vec[-2])*1e3:.0f} mT (last)")

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _Tv, _B0 = T_sample(), T_vaporizer(), magnet.field()
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vaporizer = {_Tv:.3f} K, heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), "
      f"B = {_B0:+.4f} T (read; cell ramps it to {B_LO} T), V_si = {k_si():+.3f} V (0), PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1), sr1 tau {_tau} s / {_slope} dB (0.3 / 24), drive {sr1.amplitude()} V @ {sr1.frequency():.3f} Hz")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "heaters not off"
assert abs(_B0) <= B_LO + 0.05, f"magnet at {_B0} T — expected at/below the fan start (never re-traverse)"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert _tau == 0.3 and _slope == 24, "lock-in tau/slope changed from the priced 0.3 s / 24 dB"
assert abs(sr1.amplitude() - 1.0) < 1e-6 and abs(sr1.frequency() - 13.777) < 0.01, "drive changed from 1 V / 13.777 Hz"

FAST_DELAY, SLOW_DELAY = 1.8, 3.0          # 6 tau per point; slow_delay covers the row flyback (+ magnet 3 s settle)
I_TRIP = 1e-9                              # A, either gate -> interrupt
SENS = 20e-6                               # 2 kOhm FS at 10 nA: R0(n=2.0, D=0) = 73 Ohm (run 5), run-6 max to 5 T ~130 Ohm
sr1.sensitivity(SENS)
print(f"sr1 sens {sr1.sensitivity()} V ({sr1.sensitivity()/1e-8:.0f} Ohm FS at 10 nA); sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti: electron side, D = 0 (run-5 cal), n {N_HI:+.2f} -> {N_LO:+.2f}e12 x {N_N}, "
                  f"B {B_LO} -> {B_HI} T x {N_B} uniform 1/B, fast_delay {FAST_DELAY} s, sr1 20 uV; stacking FS-count fan")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {N_LO:+.2f} to {N_HI:+.2f}e12 cm^-2 (nominal, run-5 cal: ratio 0.773, c_tg 2.796e-3 prior, '
              f'n_offset -0.089, D_offset -0.013), B = {B_LO} to {B_HI} T, {N_B} rows uniform in 1/B, {N_N} n-pts; '
              f'investigation tetralayer-stacking-fs-count Step 4; per-column SdH FFT; sr1 20 uV, tau 0.3 s/24 dB, fast_delay 1.8 s')

# --- position: gates to the fan start, then the magnet to B_LO (blocking ramp ~6 min from 0 T) ---
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
magnet.field(B_vec[0])
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")

# row layout: [time, B, Vtg, Vbg, T_sample, I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', 'T_sample')

_rail = []
def fan_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[9])) > 0.9 * SENS:
        _rail.append((float(data[1]), float(data[2])))
        if len(_rail) <= 5:
            print(f"RAIL WARN sr1 |X| = {abs(float(data[9]))*1e6:.2f} uV > 90% FS at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}")
    if float(data[4]) > 1.6:
        print(f"T WARN T_sample = {float(data[4]):.3f} K at B={float(data[1]):.3f} T")
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)     # gates parked; field HELD where the fan ended (next step decides)
print(f"done: B = {magnet.field():+.3f} T (held), gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}); rail points {len(_rail)}")
