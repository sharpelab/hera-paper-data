# === Landau fan (`landau-fan-vti`, Step 4 of tetralayer-stacking-fs-count): D = 0, n +3.2 -> +2.0e12 (25 pts) x B 0.70 -> 10.0 T (92 rows, uniform-1/B, 2 segments) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration, run 5 (cnp-and-dline-calibration: ratio data-calibrated, c_tg = geometry prior, D_offset from R_CNP(D) symmetry)
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_HI, N_LO, N_N, D0 = 3.2, 2.0, 25, 0.0                      # 1e12 cm^-2, V/nm; dn = 0.050
ns = np.linspace(N_HI, N_LO, N_N)
Vtgs, Vbgs = (np.asarray(v, float) for v in calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]))
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs, Vbgs)
_n_rt, _D_rt = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_n_rt, ns, atol=1e-6) and np.allclose(_D_rt, D0, atol=1e-6)
print(f"fast: n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({N_N} pts), D = {D0}; Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V")

# --- slow: uniform in 1/B, ascending. 0.70-1.25 T at d(1/B) = 0.030 (only the ~7.5 T light tone is alive there: 3.9 pts/period incl. region B x1.13);
#     1.25-10 T at d(1/B) = 0.010 (3.0 pts/period at F_L(3.2) = 33 T; 2.7 at region B's F_L). Magnet sits at 0 T -> starts low, ends at 10 T.
_inv = np.hstack((np.linspace(1 / 0.70, 1 / 1.25, 22)[:-1], np.linspace(1 / 1.25, 1 / 10.0, 71)))
B_vec = np.minimum(np.round(1 / _inv, 4), B_SESSION_CAP)
assert len(B_vec) == 92 and np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
print(f"slow: B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows (21 coarse + 71 fine); largest step {np.diff(B_vec).max():.3f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _Tv0, _B0 = T_sample(), T_vaporizer(), magnet.field()
_sr_rng, _vap_rng = heater.sample_range(), heater.vaporizer_range()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {_Tv0:.3f} K (<1.6), heater ranges {_sr_rng}/{_vap_rng} (0/0), "
      f"B = {_B0:+.4f} T (<= {B_vec[0]} T: ascending from where it sits), V_si = {k_si():+.3f} V (0), "
      f"PS {magnet.persistent_switch_on()} / output {magnet.output_enabled()}, nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
print(f"precondition drive sr1 {sr1.amplitude()} V @ {sr1.frequency()} Hz (1.0 V, 13.777 -> 10 nA), tau {sr1.time_constant()} s / {sr1.filter_slope()} dB (0.3 / 24: dwell basis), "
      f"sr0 sens {sr0.sensitivity()} V (0.02)")
assert 1.0 <= _T0 <= 1.5 and _Tv0 < 1.6 and _sr_rng == 0 and _vap_rng == 0
assert -0.05 < _B0 <= B_vec[0] + 0.02
assert abs(k_si()) < 0.01 and magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert abs(sr1.amplitude() - 1.0) < 1e-3 and abs(sr1.frequency() - 13.777) < 0.01
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24 and sr0.sensitivity() == 0.02

# --- acquisition settings inherited from the spot checks (runs 6/7) ---
SENS = 50e-6                                   # 5 kOhm FS at 10 nA; run 6 peak 530 Ohm, worst corner (n 2.0, 10 T) est. <= 1.5 kOhm
sr1.sensitivity(SENS)                          # (state0 replay at handoff left sr1 at the 2 uV bring-up value)
FAST_DELAY, SLOW_DELAY = 2.4, 3.0              # 8 tau at 24 dB/oct (4 % step residual); slow_delay after the row flyback
I_TRIP = 1e-9
print(f"sr1 sens {sr1.sensitivity()} V (FS {sr1.sensitivity()/10e-9:.0f} Ohm), fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti D = 0: n {N_HI:+.2f} -> {N_LO:+.2f}e12 ({N_N}) x B {B_vec[0]} -> {B_vec[-1]} T ({len(B_vec)} rows, uniform 1/B: "
                  f"0.030 below 1.25 T, 0.010 above); sr1 50 uV, fast_delay 2.4 s (8 tau); cal run 5")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {N_LO} to {N_HI} (1e12 cm^-2, {N_N} pts, fast high->low), B = {B_vec[0]} to {B_vec[-1]} T ({len(B_vec)} rows, '
              f'uniform-1/B: d(1/B) 0.030 for 0.70-1.25 T, 0.010 for 1.25-10 T); tetralayer-stacking-fs-count Step 4, electron side; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'inherits runs 6/7: sr1 50 uV, tau 0.3 s/24 dB')

magnet.field(B_vec[0])                         # blocking ramp 0 -> 0.70 T (~5 min) = the settle (VTI variant step 4)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_rail = {"n": 0}
def guards(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[9])) > 0.95 * SENS:        # clipping is unrecoverable for the FFT: log it, the checkpoint decides
        _rail["n"] += 1
        if _rail["n"] in (1, 10, 100):
            print(f"RAIL #{_rail['n']}: sr1 X = {float(data[9]):.3e} V at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}")
s.register_run_after(guards, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field stays where the fan ended (10 T if complete) — the LK mass split rides it down; never re-traverse.
    print(f"done: B = {magnet.field():+.3f} T, gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample {T_sample():.3f} K, rails {_rail['n']}")
