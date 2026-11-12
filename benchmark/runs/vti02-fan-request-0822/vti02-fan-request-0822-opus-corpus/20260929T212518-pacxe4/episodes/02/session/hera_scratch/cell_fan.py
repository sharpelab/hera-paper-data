# === Landau fan (`landau-fan-vti`): electron side, D = 0, n 2.2 -> 3.2e12, B 0.65 -> 10 T uniform-1/B ===
# Investigation Step 4 (tetralayer-stacking-fs-count). Design numbers computed in
# hera_scratch/fan_final.py from runs 5/6/7 + hera/models/tetralayer_fs_count; every
# lever at its floor (landau-fan step 1 cost-floor rule) -> exactly one fan.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration (run 5, cnp-and-dline-calibration) -------------------
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
SCALE = 0.907          # measured global density rescale: run-6 tone sum 30.0 T / F_L(3.2e12) 33.09 T

# --- committed design ---------------------------------------------------------
N_MIN, N_MAX, N_N = 2.2, 3.2, 33          # 1e12 cm^-2, D = 0; dn = 0.03125e12
B_LO, B_MAX, N_BROWS = 0.65, 10.0, 144    # T, uniform in 1/B; d(1/B) = 0.01006 1/T
TAU_EXPECT, K_SETTLE = 0.3, 7             # sr1 tau (s) and the 24 dB/oct settling-floor factor
FAST_DELAY = K_SETTLE * TAU_EXPECT        # 2.1 s -- STYLE rule 12 settling floor, not a round number
SLOW_DELAY = 1.0                          # magnet.field() already dwells settle_s = 3 s per row
SENS = 50e-6                              # inherited from run 6; 5 kOhm full scale at 10 nA
I_TRIP = 1e-9                             # gate-leakage trip (run 5/6/7 saw <= 220 pA transients)
T_TRIP = 1.6                              # fridge-event trip over a ~4.7 h unattended run
CLIP_TRIP = 5                             # consecutive soft-clipped points -> abort (clipping is unrecoverable)

# --- fast axis: paired (Vtg, Vbg) n-line at D = 0 -----------------------------
ns = np.linspace(N_MIN, N_MAX, N_N)
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
_n_rt, _D_rt = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_D_rt).max() < 1e-9, np.abs(_D_rt).max()
print(f"fast axis: n {ns[0]:+.3f} -> {ns[-1]:+.3f}e12, {N_N} pts, dn = {ns[1]-ns[0]:.5f}e12 "
      f"(ray-Nyquist floor at B_lo {4*2.417989e14*B_LO/1e16/2:.5f}e12)")
print(f"  Vtg {Vtgs.min():+.4f} -> {Vtgs.max():+.4f} V (limit {TG_MIN}/{TG_MAX}, margin {TG_MAX-Vtgs.max():+.4f}); "
      f"Vbg {Vbgs.min():+.4f} -> {Vbgs.max():+.4f} V (margin {BG_MAX-Vbgs.max():+.4f})")

# --- slow axis: uniform in 1/B (per-column SdH-FFT fan, landau-fan step 4) ----
B_vec = field_invB(B_LO, B_MAX, N_BROWS)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
assert np.all(np.diff(B_vec) > 0), "slow axis must be monotonic (never re-traverse)"
_d_invB = np.abs(np.diff(1.0 / B_vec)).max()
_F_L_max = cst.h / (4 * cst.e) * N_MAX * 1e16          # Luttinger freq at n_max, T
assert _d_invB <= 1.0 / (2 * _F_L_max), (_d_invB, 1.0 / (2 * _F_L_max))   # Nyquist on the fastest tone
print(f"slow axis: B {B_vec[0]:.4f} -> {B_vec[-1]:.4f} T, {N_BROWS} rows, "
      f"d(1/B) = {_d_invB:.5f} 1/T (Nyquist {1/(2*_F_L_max):.5f}, preferred 1/3 {1/(3*_F_L_max):.5f})")
print(f"  F_L(n_max) = {_F_L_max:.2f} T; 1/B record {1/B_LO - 1/B_MAX:.4f} 1/T -> dF = {1/(1/B_LO-1/B_MAX):.2f} T; "
      f"max single-row dB = {np.diff(B_vec).max():.3f} T ({np.diff(B_vec).max()/0.137:.1f} min)")
print(f"  total points {N_BROWS*N_N}")

# --- preconditions: state this cell ASSUMES but does not set ------------------
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_tau, _slope, _amp = sr1.time_constant(), sr1.filter_slope(), sr1.amplitude()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: state0), "
      f"V_si = {k_si():+.3f} V (0), Vtg = {k_tg.volt():+.4f}, Vbg = {k_bg.volt():+.4f} V (0: state0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
print(f"  sr1 tau = {_tau} s, filter_slope = {_slope} dB/oct, amplitude = {_amp} V "
      f"-> I_bias = {_amp/1e8*1e9:.2f} nA; fast_delay {FAST_DELAY} s = {FAST_DELAY/_tau:.1f} tau")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(_tau - TAU_EXPECT) < 1e-9 and int(_slope) == 24, (_tau, _slope)  # the dwell derivation rests on these
assert abs(_amp - 1.0) < 1e-6, _amp                         # I_bias = 10 nA; R scale rests on it

# --- fixed lock-in scale for the whole fan (landau-fan step 3) ----------------
sr1.sensitivity(SENS)
print(f"sr1 sensitivity {sr1.sensitivity()} V -> full scale {SENS/(_amp/1e8):.0f} Ohm; "
      f"worst corner (n=2.2e12, B=10 T) expected ~700 Ohm (run 5 R(B=0) 68 Ohm x run-6 MR 10.5x)")

# --- run metadata -------------------------------------------------------------
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side, D = 0: n {N_MIN}->{N_MAX}e12 ({N_N} pts) x "
                  f"B {B_LO}->{B_MAX} T uniform-1/B ({N_BROWS} rows), fast_delay {FAST_DELAY} s (7 tau), "
                  f"sr1 {SENS*1e6:.0f} uV; run-5 cal, tetralayer FS-count Step 4")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0.000 V/nm, n = {N_MIN} to {N_MAX} e12 cm^-2 ({N_N} pts, dn {ns[1]-ns[0]:.5f}e12), '
              f'B = {B_LO} to {B_MAX} T uniform in 1/B ({N_BROWS} rows, d(1/B) {_d_invB:.5f} 1/T)')
s.add_comment(f'per-column SdH-FFT fan: F_L(n_max) {_F_L_max:.2f} T, dF {1/(1/B_LO-1/B_MAX):.2f} T; '
              f'fast_delay {FAST_DELAY} s = {K_SETTLE} tau at tau {_tau} s / {_slope} dB/oct; sr1 sens {SENS} V')
s.add_comment(f'cal run 5: c_tg {CAL["c_tg"]:.4e}, c_bg {CAL["c_bg"]:.4e}, n_offset {CAL["n_offset"]:+.4f}e12, '
              f'D_offset {CAL["D_offset"]:+.4f} V/nm; onset/settling/sensitivity inherited from run 6 (sdh-spot-check)')

# --- position: gates to the n-line start, then the magnet (blocking = settle) -
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
print(f"gates positioned: Vtg {k_tg.volt():+.4f}, Vbg {k_bg.volt():+.4f} V; ramping magnet to {B_LO} T "
      f"(~{(B_LO-abs(_B0))/0.137:.1f} min, blocking)")
magnet.field(B_LO)                      # landau-fan-vti step 4: the set call IS the settle
print(f"magnet at {magnet.field():+.4f} T, T_sample {T_sample():.3f} K -- starting fan")

# row layout: [time, magnet_field, k_tg_volt, k_bg_volt, T_sample, k_tg_curr, k_bg_curr, sr0_X, sr0_P, sr1_X, sr1_P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', sr1.X); s.plot('time', sr1.P); s.plot('time', sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_g = {"clip": 0}


def fan_guard(station, data):
    """Unattended-run guards: gate leakage, fridge event, and soft-clipping of sr1.

    Clipping matters more than a rail warning: a flat-topped column is harmonically
    corrupted across its WHOLE FFT and is not recoverable by any B-window, so it
    aborts rather than burning the rest of the fan (landau-fan step 1 / Next).
    """
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    t_now = float(data[4])
    if t_now > T_TRIP:
        print(f"TEMPERATURE TRIP at B={float(data[1]):+.3f} T: T_sample = {t_now:.3f} K > {T_TRIP} K")
        station.interrupt_requested = True
    if abs(float(data[9])) > 0.95 * SENS:
        _g["clip"] += 1
        if _g["clip"] == 1:
            print(f"CLIP WARNING at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
                  f"sr1.X = {float(data[9]):.3e} V > 0.95 x {SENS} V")
        if _g["clip"] >= CLIP_TRIP:
            print(f"CLIP TRIP: {_g['clip']} points at >= 0.95 full scale -- sensitivity under-ranged "
                  f"the low-n x high-B corner; aborting (re-size and re-run)")
            station.interrupt_requested = True
    else:
        _g["clip"] = 0


s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)

# park gates; leave the field at 10 T -- the follow-up (LK mass split / firming fan)
# rides it down rather than re-traversing (rig card: never re-traverse).
k_tg.volt(0.0); k_bg.volt(0.0)
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, "
      f"T_sample = {T_sample():.3f} K, clip points = {_g['clip']}")
