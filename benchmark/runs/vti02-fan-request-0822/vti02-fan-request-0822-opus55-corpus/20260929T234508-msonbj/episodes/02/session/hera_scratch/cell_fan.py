# === Step 4 — Landau fan for the stacking call (`landau-fan-vti`; tetralayer-stacking-fs-count Step 4) ===
# Electron side, D = 0 (run-5 cal): n = +1.75 -> +3.24e12 (37 pts, ascending) x B = 1.0 -> 10.0 T uniform in 1/B
# (91 rows, d(1/B) = 0.01 1/T, inherited from spot check run 6). Per-column SdH FFT fan.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration: ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_N, D0 = 1.75, 3.24, 37, 0.0          # 1e12 cm^-2, V/nm
ns = np.linspace(N_LO, N_HI, N_N)                 # ascending: the fan ends at n_hi (the spot-check density)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs, Vbgs)
_nchk, _Dchk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_nchk, ns) and np.allclose(_Dchk, D0, atol=1e-9)
B_LO, B_HI, N_B = 1.0, 10.0, 91
B_vec = field_invB(B_LO, B_HI, N_B)               # ascending, uniform in 1/B
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and abs(np.diff(1 / B_vec).mean() + 0.01) < 1e-9
print(f"fast: n {ns[0]:+.3f}..{ns[-1]:+.3f}e12 ({N_N} pts, dn {ns[1]-ns[0]:.4f}); Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f} V")
print(f"slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows uniform in 1/B (d(1/B) = 0.0100 1/T -> Nyquist 50 T vs F_L(n_hi) = 33.5 T)")

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5) | B = {_B0:+.4f} T (|B|<0.05: fan starts from 0 -> 1 T) | V_si = {k_si():+.3f} V (0) | "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()} | nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1) | "
      f"sr1 tau {_tau} s, slope {_slope} dB (0.3 / 24: the dwell is priced on it) | drive {sr1.amplitude()} V @ {sr1.frequency()} Hz")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert abs(_B0) < 0.05, f"magnet not at ~0 T: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert _tau == 0.3 and _slope == 24, "lock-in settling changed from the priced 0.3 s / 24 dB"
assert abs(sr1.amplitude() - 1.0) < 1e-6 and abs(sr1.frequency() - 13.777) < 0.01, "drive changed from 1 V / 13.777 Hz"

# --- lock-in: fixed sensitivity for the whole fan (inherited from runs 6/7): 50 uV = 5 kOhm FS at 10 nA.
# Worst corner low-n x 10 T: R0(n=1.75) ~ 80 Ohm (run 5) x MR ~10 (run 6: 53 -> 530 Ohm) ~ 0.8-1.2 kOhm = 16-24 % FS.
sr1.sensitivity(50e-6)
SENS = sr1.sensitivity()
FAST_DELAY, SLOW_DELAY = 2.1, 3.0                 # 7 tau at 24 dB/oct (settling floor, rig card); row start 3 s + flyback
I_TRIP, T_TRIP, CLIP_MAX = 1e-9, 2.0, 10
print(f"sr1 sens {SENS} V (5 kOhm FS), sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti (tetralayer-stacking-fs-count step 4): electron side D = 0, n {N_LO:+.2f} -> {N_HI:+.2f}e12 ({N_N}), "
                  f"B {B_LO} -> {B_HI} T uniform 1/B ({N_B}, d(1/B)=0.01), sr1 50 uV, tau 0.3 s/24 dB, fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'tetralayer-stacking-fs-count step 4 | D = {D0} V/nm, n = {N_LO} to {N_HI} e12 cm^-2 ({N_N} pts, ascending), '
              f'B = {B_LO} to {B_HI} T uniform in 1/B ({N_B} rows, d(1/B) = 0.01 1/T); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'c_tg {CAL["c_tg"]:.3e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}; onset 1.0 T (run 6, censored lower bound); '
              f'sr1 50 uV, tau 0.3 s 24 dB, fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s')

# --- position: gates to the first n-point, then the magnet 0 -> 1 T (blocking, ~7.3 min at 0.137 T/min).
# NB: interrupting during the ramp does not stop the supply (rig card) — it completes to 1 T.
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
print(f"ramping magnet {magnet.field():+.3f} -> {B_vec[0]:.3f} T ...")
magnet.field(B_vec[0])
interruptible_sleep(10)
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")

# row layout: [time, magnet_field, k_2400_tg_volt, k_2400_bg_volt, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_g = {"pt": 0, "clip": 0}
def fan_guard(station, data):
    _g["pt"] += 1
    i_tg, i_bg, T, x1 = abs(float(data[5])), abs(float(data[6])), float(data[4]), abs(float(data[9]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if T > T_TRIP:
        print(f"T TRIP: T_sample = {T:.3f} K > {T_TRIP} K at B={float(data[1]):.3f} T")
        station.interrupt_requested = True
    if x1 > 0.9 * SENS:
        _g["clip"] += 1
        if _g["clip"] == 1 or _g["clip"] > CLIP_MAX:
            print(f"CLIP: |sr1.X| = {x1:.3e} V > 0.9 x {SENS} at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f} (count {_g['clip']})")
        if _g["clip"] > CLIP_MAX:
            station.interrupt_requested = True
    if _g["pt"] % N_N == 1:                        # row start: thermometry freshness (>= 2-3 write periods)
        try:
            assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
        except Exception as e:
            print(f"THERMOMETRY STALE at B={float(data[1]):.3f} T: {e}")
            station.interrupt_requested = True
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# Endpoint (deliberate): field stays at 10 T (the LK / next step rides down from there — never re-traverse);
# gates stay at the fan's last point n = +3.24e12, D = 0. No park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K, clipped pts {_g['clip']}")
