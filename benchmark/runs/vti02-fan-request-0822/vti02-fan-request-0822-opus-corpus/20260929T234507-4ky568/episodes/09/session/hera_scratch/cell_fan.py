# === Landau fan (`landau-fan-vti`): electron side, D = 0, n 2.10 -> 3.20e12, B 0.7 -> 10 T, 133 x 45 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_n = 2.10, 3.20, 45        # 1e12 cm^-2, along D = 0
B_LO, B_HI, N_B = 0.70, 10.0, 133       # T, uniform in 1/B (per-column SdH-FFT fan)
FAST_DELAY, SLOW_DELAY = 1.8, 2.0       # 6 tau at tau = 0.3 s / 24 dB; slow on top of the blocking field set
I_TRIP = 1e-9

# --- grid + design checks (both-axis Nyquist, validators) ---
ns = np.linspace(N_LO, N_HI, N_n)
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX
B_vec = np.round(field_invB(B_LO, B_HI, N_B), 4)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
_d = np.abs(np.diff(1.0 / B_vec))
_FL = N_HI * 1e16 * cst.h / (4 * cst.e)                       # Luttinger freq at n_max, T
_nyq = 1.0 / (2 * _d.max())
_ray = 4 * (cst.e / cst.h) * B_LO / 1e16 / (ns[1] - ns[0])    # LL-ray spacing at B_lo / dn
print(f"B grid: {N_B} rows {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T uniform-1/B, d(1/B) = {_d.mean():.5f} 1/T "
      f"(dB {np.diff(B_vec).min()*1e3:.1f} mT at B_lo .. {np.diff(B_vec).max()*1e3:.0f} mT at B_hi); "
      f"Nyquist ceiling {_nyq:.1f} T = {_nyq/_FL:.2f} x F_L(n_max) = {_FL:.2f} T")
print(f"n grid: {N_n} cols {ns[0]:.2f} -> {ns[-1]:.2f}e12 at D = 0, dn = {ns[1]-ns[0]:.4f}e12 -> {_ray:.2f} pts/LL-ray "
      f"at B_lo (floor 2); Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f} V; "
      f"dF = {1/(1/B_LO - 1/B_HI):.2f} T")
assert _nyq > 1.2 * _FL, "B-axis Nyquist floor violated"
assert _ray >= 2.0, "n-axis ray Nyquist floor violated"
_n_rt, _D_rt = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_D_rt).max() < 1e-9 and abs(_n_rt.max() - N_HI) < 1e-6

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (expect ~0, close-out parked it), "
      f"V_si = {k_si():+.3f} V (0), (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V (0, 0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), sr1 tau = {sr1.time_constant()} s / "
      f"{sr1.filter_slope()} dB, PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(k_si()) < 0.01
assert abs(_B0) < 0.05, "magnet is not parked near 0 — re-read state before positioning"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not at 1"
assert abs(sr1.time_constant() - 0.3) < 1e-9 and sr1.filter_slope() == 24, "dwell was priced at 6 tau for 0.3 s / 24 dB"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# Fixed sensitivity for the whole fan, inherited from the spot checks: 50 uV = 5.05 kOhm FS at ~9.9 nA.
# Worst corner (n = 2.10e12, 10 T) extrapolates to <~900 Ohm ~ 18 % FS; headroom over precision (run-4 lesson).
sr1.sensitivity(50e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (5 kOhm FS); sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side, D = 0: n {N_LO}..{N_HI}e12 ({N_n} cols), "
                  f"B {B_LO}..{B_HI} T uniform-1/B ({N_B} rows), sr1 50 uV, fast_delay {FAST_DELAY} s (6 tau)")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = +0.00 V/nm; n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 cm^-2, {N_n} cols (dn {ns[1]-ns[0]:.4f}e12); '
              f'B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows uniform-1/B (d(1/B) {_d.mean():.5f}, Nyquist {_nyq:.0f} T); '
              f'(Vtg, Vbg) {Vtgs[0]:+.4f},{Vbgs[0]:+.4f} -> {Vtgs[-1]:+.4f},{Vbgs[-1]:+.4f}; sr1 50 uV, '
              f'fast_delay {FAST_DELAY} s = 6 tau (tau 0.3 s / 24 dB), slow_delay {SLOW_DELAY} s; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'FS-count step 4, follows spot checks runs 6/7')

# row layout: [time, B (slow), Vtg, Vbg (fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', sr1.P); s.plot('time', sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

LEAK = {"tripped": False}

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        LEAK["tripped"] = True
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

# --- position: gates onto the n-line start, then the magnet to B_lo (blocking ramp, ~5 min from 0 T) ---
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
magnet.field(B_vec[0])
print(f"positioned: B = {magnet.field():+.4f} T (target {B_vec[0]:.4f}), "
      f"(Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V; starting fan")

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    if LEAK["tripped"]:
        s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
        print("gates parked at 0 after leak trip")
    # field is left where the fan ended (10 T on completion) — the LK ladder rides it down; no re-traverse.
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, "
          f"T_sample = {T_sample():.3f} K")
