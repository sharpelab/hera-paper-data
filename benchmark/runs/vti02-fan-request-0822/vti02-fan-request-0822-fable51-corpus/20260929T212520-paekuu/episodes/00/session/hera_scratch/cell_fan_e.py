# === Landau fan (`landau-fan-vti`), investigation Step 4: electron side, D = 0, n = 1.2 -> 3.2e12 (fast, 76 pts) x B 0.6 -> 10 T (slow, 143 rows uniform in 1/B, 3 segments) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0                                                  # V/nm — the investigation's operating point
ns = np.linspace(1.2, 3.2, 76)                            # 1e12 cm^-2, ascending within each row (dn = 0.0267)
Vtgs, Vbgs = calc_gate_voltages(ns, np.full_like(ns, D0), **CAL)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
_nr, _Dr = calc_nD(Vtgs, Vbgs, **CAL); assert np.allclose(_nr, ns) and np.allclose(_Dr, D0)
print(f"fast axis: n {ns[0]:.2f} -> {ns[-1]:.2f}e12 ({len(ns)} pts, dn {ns[1]-ns[0]:.4f}e12) at D = {D0}: "
      f"Vtg {Vtgs[0]:+.4f} .. {Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f} .. {Vbgs[-1]:+.4f} V (inside validators)")

# --- slow axis: uniform in 1/B per segment (per-column SdH FFT). Nyquist per segment from the run-6 tone/onset set:
FL_MAX = 33.1   # T = F_L(n = 3.2e12), the fastest fundamental
segs = [(0.6, 1.0, 1 / (3 * 16.0)),    # below the 22 T tone's onset (1.2-1.4 T): light tone 7.3 T + its 2x -> Nyquist 24 T
        (1.0, 3.5, 1 / (3 * FL_MAX)),  # F_L at 1/3 -> Nyquist 50 T (22, 29, 44 T content)
        (3.5, 10.0, 0.005)]            # QH-like harmonics of the 29.4 T tone (58.6 T from ~3.7 T, 88 T from ~5.3 T) -> Nyquist 100 T
B_parts = [field_invB(a, b, int(np.ceil((1 / a - 1 / b) / d)) + 1) for a, b, d in segs]
B_vec = np.unique(np.round(np.hstack(B_parts), 5))        # ascending: starts near where the magnet sits (0 T), ends at 10 T
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"slow axis: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T; dB {np.diff(B_vec)[0]*1e3:.1f} mT (first) .. {np.diff(B_vec)[-1]*1e3:.0f} mT (last); "
      f"segments (B_lo, B_hi, rows) = {[(a, b, len(p)) for (a, b, _), p in zip(segs, B_parts)]}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: the fan ramps to 0.6 T itself), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"

FAST_DELAY, SLOW_DELAY = 1.0, 3.0      # fast: n-axis is not the FFT axis (lag = a <2-column n-smear); slow: 10 tau after the row flyback
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA. Worst corner (n = 1.2, 10 T): R(B = 0) ~ 100 Ohm (run 5)
# x MR 6-10x (runs 6/7 incl. the Hall admixture on B_1-B_2) ~ 1 kOhm -> >= 5x headroom. sr0 stays at 20 mV (10 nA = 50 % FS).
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s / {sr1.filter_slope()} dB/oct; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = {D0} V/nm, n = {ns[0]:.2f} -> {ns[-1]:.2f}e12 ({len(ns)} pts) fast; "
                  f"B {B_vec[0]} -> {B_vec[-1]} T ({len(B_vec)} rows, uniform 1/B in 3 segments) slow; run-5 cal; sr1 100 uV; "
                  f"fast_delay {FAST_DELAY}, slow_delay {SLOW_DELAY}")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {ns[0]:.2f} to {ns[-1]:.2f}e12 cm^-2 ({len(ns)} pts, electron side), B = {B_vec[0]} to {B_vec[-1]} T '
              f'({len(B_vec)} rows, uniform 1/B: 0.6-1.0 T d(1/B) = 1/48, 1.0-3.5 T 1/99.3, 3.5-10 T 1/200); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'sr1 100 uV, tau 0.3 s / 24 dB; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; onset/tones from run 6')
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
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # park gates; the field stays where the fan ended (10 T) — the next step decides the endpoint
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
