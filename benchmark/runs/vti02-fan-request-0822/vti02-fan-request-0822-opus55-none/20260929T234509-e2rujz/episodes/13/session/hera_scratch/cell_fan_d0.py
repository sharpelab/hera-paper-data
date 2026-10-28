# === Landau fan at D = 0 (`landau-fan`) — plan Step 4 ===
# slow: magnet.field ascending 0.6 -> 9 T (1/B-uniform 0.6-3 T, d(1/B) = 0.0125 /T; then 0.1 T steps 3.1-9 T)
# fast: co-swept (Vtg, Vbg) along the region-A D = 0 line, n = -1.20 ... +3.25e12, 91 pts (dn = 0.05e12), hole -> electron
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration (run 5, cnp-and-dline-calibration; ratio data-calibrated, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.20, 3.25, 91)                                   # 1e12 cm^-2
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_n_chk, _D_chk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_n_chk, n_vec) and np.abs(_D_chk).max() < 1e-9

B_A = field_invB(0.6, 3.0, 108)                                        # 1/B-uniform, d(1/B) = 0.0125 /T (Nyquist 40 T)
B_B = np.round(np.arange(3.1, 9.0 + 1e-9, 0.1), 4)                     # 0.1 T steps
B_vec = np.hstack((B_A, B_B))
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
print(f"fast: {len(n_vec)} pts n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 (dn {n_vec[1]-n_vec[0]:.3f}); "
      f"Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f} V")
print(f"slow: {len(B_vec)} rows, B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T ({len(B_A)} 1/B-uniform to 3 T, {len(B_B)} at 0.1 T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0.6 T ascending), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert abs(_B0) < 0.05, f"magnet not near 0: {_B0} T"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert float(heater.sample_range()) == 0 and float(heater.vaporizer_range()) == 0, "heaters not off"
print(f"drive {sr1.amplitude()} V @ {sr1.frequency()} Hz -> I_bias ~ {sr1.amplitude()/100e6*1e9:.1f} nA; "
      f"tau sr1 {sr1.time_constant()} s / {sr1.filter_slope()} dB, sr0 {sr0.time_constant()} s")
assert abs(sr1.amplitude() - 1.0) < 1e-3, "drive amplitude changed"

FAST_DELAY, SLOW_DELAY = 1.0, 3.0      # 1.0 s ~ 3.3 tau (uniform lag ~1 step, hole->electron); 3 s = 10 tau after the row flyback
I_TRIP = 1e-9
# Fixed sensitivity, no mid-row autorange: 100 uV = 10 kOhm FS at 10 nA (run-5 map max 3.1 kOhm; SdH/QH maxima <= 600 Ohm in runs 6-7).
sr1.sensitivity(100e-6)
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V; magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan D=0: B 0.6->9 T (1/B-uniform 0.6-3 T d=0.0125, 0.1 T 3.1-9 T, 168 rows) x "
                  "n -1.20..+3.25e12 on D=0 (91 pts, run-5 cal), Vsi 0, sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: slow magnet.field 0.6 -> 9.0 T ascending, {len(B_vec)} rows (1/B-uniform 0.6-3 T d(1/B)=0.0125/T, then 0.1 T); '
              f'fast co-swept (Vtg, Vbg) on D = 0, n = {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12, {len(n_vec)} pts; '
              f'cal run 5: c_tg {CAL["c_tg"]:.4g}, c_bg {CAL["c_bg"]:.4g}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, sr1 100 uV')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(set), Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, magnet.field(read), sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr).fp(magnet.field)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample); s.plot('time', magnet.field)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# field stays at 9 T (plan Step 5 works there — no re-traverse); gates stay at the last fan point.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
