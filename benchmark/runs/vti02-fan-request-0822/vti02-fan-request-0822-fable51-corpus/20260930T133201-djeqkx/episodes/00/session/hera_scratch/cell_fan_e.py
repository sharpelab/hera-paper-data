# === Landau fan, electron side (`landau-fan-vti`): D = 0, n = +3.2 -> +0.5e12 (fast, paired TG/BG), B 1 -> 10 T uniform in 1/B (slow) ===
# Step 4 of investigations/tetralayer-stacking-fs-count: per-column SdH-FFT fan on the cleaner (electron) side.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0
ns = np.linspace(3.2, 0.5, 55)                      # 1e12 cm^-2, dn = 0.05: >= 2 pts per ray period at B >= 1.03 T, 2.9 at 1.5 T
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
print(f"fast axis: {len(ns)} pts, n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = {D0:+.2f} V/nm; Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V; "
      f"roundtrip n,D at column 0 = {calc_nD(Vtgs[0], Vbgs[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- slow axis: uniform in 1/B, 1 -> 10 T. d(1/B) = 0.006 /T (F_s = 167 T): Nyquist x2.5 on F_L(3.2e12) = 33.1 T, and the run-6
#     harmonic content at ~60 / ~90 T folds to 60 / 77 T -- outside the <= 45 T read band (d(1/B) = 0.010 would fold 2*F_L onto F_L).
B_vec = field_invB(1.0, 10.0, 151)
assert B_vec[0] < B_vec[-1] and B_vec.max() <= B_SESSION_CAP
_dinv = np.abs(np.diff(1 / B_vec))
print(f"slow axis: {len(B_vec)} rows, B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {_dinv.mean():.4f} /T (F_s = {1/_dinv.mean():.0f} T); dB = {B_vec[1]-B_vec[0]:.4f} T at 1 T, {B_vec[-1]-B_vec[-2]:.3f} T at 10 T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: magnet parked at 0 after the handoff), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1 -- fast axis would run 5x slow"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 1.2, 2.0    # 4 tau at tau = 0.3 s / 24 dB (lag is uniform per column -> harmless to the per-column FFT)
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA. Worst corner is low n x high B (n = 0.5, 10 T: nu ~ 2);
# spot checks maxed at 530 / 587 Ohm at 10 T (n = +3.2 / -1.2). Sized for headroom, not precision (n = 3.2 at 2 T is ~20 Ohm = 0.2 % FS).
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = {D0:+.2f} V/nm, n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({len(ns)} pts, run-5 cal), "
                  f"B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T uniform 1/B ({len(B_vec)} rows), fast_delay {FAST_DELAY}, sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 cm^-2 ({len(ns)} pts, dn 0.05), B = {B_vec[0]:.2f} to {B_vec[-1]:.2f} T uniform 1/B '
              f'({len(B_vec)} rows, d(1/B) {_dinv.mean():.4f}); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'follows sdh-spot-check runs 6 (e, +3.2e12) and 7 (h, -1.2e12)')

# position: gates to the first column, magnet to B_lo (blocking ramp ~7 min from 0 -- the set call is the settle)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
magnet.field(B_vec[0])
interruptible_sleep(10)
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates home; field stays at 10 T -- the next move (hole-side fan or LK ladder) rides it down, never re-traverses
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T (left at the fan top), (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
