# === Landau fan (`landau-fan-vti`): electron side, D = 0; n +3.2 -> +0.8e12 (76 pts fast) x B 1 -> 10 T uniform-1/B (109 rows slow) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0
ns = np.linspace(3.2, 0.8, 76)            # 1e12 cm^-2, high -> low; dn = 3.2e10 (3.0 samples/ray at 1 T)
Ds = D0 * np.ones(len(ns))
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, \
    (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
print(f"n-line: {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = {D0:+.2f}; Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, "
      f"Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V; roundtrip end = {calc_nD(Vtgs[-1], Vbgs[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- slow field axis: uniform in 1/B, 1.0 -> 10 T, d(1/B) = 1/120 (Nyquist F = 60 T; spot-check run 6 design) ---
B_vec = 1.0 / np.linspace(1.0, 0.1, 109)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() >= 1.0
print(f"B rows: {len(B_vec)}, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {(1/B_vec[0]-1/B_vec[-1])/(len(B_vec)-1):.6f} /T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff state, fan ramps to 1 T), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

# --- acquisition inherited from spot-check run 6: sens 50 uV (5 kOhm FS at 10 nA), drive 1 V, tau 0.3 s ---
sr1.sensitivity(50e-6)
FAST_DELAY, SLOW_DELAY = 1.8, 1.0         # 6*tau per-column-SdH settling; slow_delay per base step 7
I_TRIP = 1e-9
print(f"drive {sr1.amplitude()} V (expect 1.0); sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s; "
      f"fast_delay {FAST_DELAY} s = 6 tau")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron D = 0: n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 (76 pts), "
                  f"B 1 -> 10 T uniform-1/B (109 rows, d(1/B)=1/120), sr1 50 uV, fast_delay 1.8 s (6 tau); run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = {D0:+.2f} V/nm: n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 cm^-2 (76 pts, paired n-line), '
              f'B = {B_vec[0]:.2f} to {B_vec[-1]:.2f} T uniform-1/B (109 rows); sens 50 uV, fast_delay 1.8 s = 6 tau; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# field stays at 10 T deliberately — next step (LK mass split / ride-down) starts there; never re-traverse.
print(f"done: B = {magnet.field():+.3f} T, gates parked (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
