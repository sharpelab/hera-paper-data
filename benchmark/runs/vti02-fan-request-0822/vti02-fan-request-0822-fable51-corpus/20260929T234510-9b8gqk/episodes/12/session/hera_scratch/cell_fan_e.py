# === Landau fan, electron side at D = 0 (`landau-fan-vti`): n = +1.0 -> +3.2e12 (51 cols), B 0.3 -> 8 T (160 rows, uniform 1/B piecewise) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0
ns = np.linspace(3.2, 1.0, 51)                  # 1e12 cm^-2, fast axis, high -> low n (dn = 0.044)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs), np.asarray(Vbgs)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
assert len(Vtgs) == len(Vbgs) == len(ns)
print(f"fast axis: n = {ns[0]:+.2f} -> {ns[-1]:+.2f} e12 ({len(ns)} pts, dn = {abs(ns[1]-ns[0]):.3f}), D = {D0:+.2f} V/nm; "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V; "
      f"roundtrip top/bottom n,D = {calc_nD(Vtgs[0], Vbgs[0], **CAL)}, {calc_nD(Vtgs[-1], Vbgs[-1], **CAL)}")

# --- slow axis: uniform in 1/B, piecewise (run-6 evidence: only the 7.1 T tone + its 14 T harmonic below 1.2 T; F_L-scale tones onset >= 1.36 T) ---
F_L_TOP = cst.h / (4 * cst.e) * ns.max() * 1e16          # Luttinger frequency at the top density, T
d_low, d_dense = 0.025, 1.0 / (2.5 * F_L_TOP)            # T^-1: 20 T Nyquist below 1.2 T; 1.25x Nyquist on F_L above
B_a = field_invB(0.3, 1.2, int(np.ceil((1 / 0.3 - 1 / 1.2) / d_low)) + 1)
B_b = field_invB(1.2, 8.0, int(np.ceil((1 / 1.2 - 1 / 8.0) / d_dense)) + 1)
B_vec = np.unique(np.round(np.hstack((B_a, B_b)), 4))    # ascending, 0.3 -> 8.0 T
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"slow axis: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T ({len(B_a)} rows to 1.2 T at d(1/B) = {d_low}, "
      f"{len(B_b)} rows 1.2 -> 8 T at d(1/B) = {d_dense:.4f}; F_L(top) = {F_L_TOP:.1f} T); max dB {np.diff(B_vec).max():.3f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan positions to 0.3 T), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"

FAST_DELAY, SLOW_DELAY = 1.2, 1.0    # 4 tau at tau = 0.3 s / 24 dB; slow_delay on top of the driver's 3 s field settle
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange): 100 uV = 10 kOhm FS at 10 nA — worst corner n = 1.0 x high B (~1.2 kOhm expected).
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB; "
      f"sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan electron D = 0: n = {ns[0]:+.2f} -> {ns[-1]:+.2f} e12 ({len(ns)} cols), B {B_vec[0]} -> {B_vec[-1]} T "
                  f"({len(B_vec)} rows, uniform 1/B piecewise), run-5 cal, sr1 100 uV, fast_delay {FAST_DELAY}")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {ns[-1]:+.2f} to {ns[0]:+.2f} e12 cm^-2 ({len(ns)} pts, fast high->low), '
              f'B = {B_vec[0]} to {B_vec[-1]} T ({len(B_vec)} rows: {len(B_a)} uniform-1/B to 1.2 T d(1/B)={d_low}, {len(B_b)} uniform-1/B to 8 T d(1/B)={d_dense:.4f}); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'sr1 100 uV, tau {sr1.time_constant()} s, fast_delay {FAST_DELAY}, slow_delay {SLOW_DELAY}; follows sdh-spot-check runs 6/7')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg (fast pair), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # park gates; field stays where the fan ended (8 T) for the next segment
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
