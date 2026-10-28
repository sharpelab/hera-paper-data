# === Landau fan, electron side (`landau-fan-vti`): D = 0, n = +1.0 -> +3.2e12 fast (81 pts), B 0.8 -> 10 T slow, uniform 1/B (145 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0
n_vec = np.linspace(1.0, 3.2, 81)      # 1e12 cm^-2, dn = 0.0275; ray Nyquist at B_lo = 0.8 T: dn_ray = 4eB/h = 0.077e12 -> 2.8 pts/period
Vtgs, Vbgs = calc_gate_voltages(n_vec, D0 * np.ones_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
print(f"n-line: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts) at D = {D0}: Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V; "
      f"roundtrip top (n, D) = {calc_nD(Vtgs[-1], Vbgs[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- field axis: uniform in 1/B, ascending from where the magnet sits (0 T -> B_lo is a bare ramp).
#     B_lo = 0.8 T: run-6 sdh_onset (electron, full record) 0.88 T, run-7 (hole) 0.71 T.
#     d(1/B) = 0.008 /T -> Nyquist 62.5 T: covers run 6's 58.7 T harmonic so it cannot alias onto F_L (F_L(3.2) = 33.1 T needs <= 0.0151; /3 = 0.0101).
B_LO, B_HI, DINVB = 0.8, 10.0, 0.008
N_B = int(round((1 / B_LO - 1 / B_HI) / DINVB)) + 1
B_vec = field_invB(B_LO, B_HI, N_B)
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
FAST_DELAY, SLOW_DELAY = 1.5, 1.0      # 5 tau at tau = 0.3 s / 24 dB (priced in the markdown); slow_delay sits on top of the blocking ramp + 3 s driver settle
I_TRIP = 1e-9
t_pt = FAST_DELAY + 0.12               # run 5: 1.10 s/pt at fast_delay 1.0 with this fp set at nplc 1, + the 2nd gate write
est_h = (N_B * len(n_vec) * t_pt + N_B * 6.0 + B_HI / 0.137 * 60) / 3600
print(f"B grid: {N_B} rows {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {DINVB} /T (dB {np.diff(B_vec)[0]*1e3:.1f} mT at B_lo, {np.diff(B_vec)[-1]*1e3:.0f} mT at the top); "
      f"{N_B * len(n_vec)} pts; estimate {est_h:.1f} h (+5-10 % realistic)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (<= {B_LO}: the fan ascends from where the magnet sits), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and -0.05 < _B0 <= B_LO and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA. Worst corner is n = 1.0 x 10 T (nu ~ 4, QH regime):
# R(B = 0, n = 1) ~ 120 Ohm (run 5) x QH-regime MR; runs 6/7 peaked at 530/590 Ohm at 10 T. Headroom over precision — a railed column is unrecoverable.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct; sr0 sens {sr0.sensitivity()} V")
assert abs(sr1.time_constant() - 0.3) < 1e-6, "tau changed since the spot checks — re-price fast_delay before running"

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = {D0} V/nm, n = {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts) fast; "
                  f"B {B_LO} -> {B_HI} T uniform 1/B ({N_B} rows, d(1/B) {DINVB} /T); fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; sr1 100 uV; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {n_vec[0]:+.2f} to {n_vec[-1]:+.2f}e12 cm^-2 (electron side, {len(n_vec)} pts), B = {B_LO} to {B_HI} T uniform-1/B ({N_B} rows); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; inherits sdh-spot-check runs 6/7 (onset 0.88/0.71 T)')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B (slow), Vtg, Vbg (fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[-6])), abs(float(data[-5]))     # k_tg.curr, k_bg.curr — fp order: T, I_tg, I_bg, sr0 X/P, sr1 X/P
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)     # gates parked at 0; the field stays where the fan ended (10 T) — the next step rides it down
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
