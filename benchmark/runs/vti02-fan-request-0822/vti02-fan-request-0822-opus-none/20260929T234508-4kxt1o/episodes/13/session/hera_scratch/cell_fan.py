# === Step 4: Landau fan at D = 0 (`landau-fan`) ===
# slow: B 0 -> 10 T (41 rows, 0.25 T) | fast: (Vtg, Vbg) co-swept along the run-5
# D = 0 line, 261 pts, n = -1.280 -> +3.257e12 cm^-2 (TG -0.300 -> +1.000 V, 5.00 mV)
from sharpelab_nb.gates import calc_nD, calc_gate_voltages

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)  # run 5
N_FAST, N_ROWS = 261, 41
B_vec = np.linspace(0.0, 10.0, N_ROWS)                       # slow, 0.25 T
# Fast axis parametrised by n on the D = 0 line (calc_gate_voltages is the documented
# inverse, so D = 0 holds by construction); the n endpoints are the ones whose Vtg
# lands exactly on the TG operating limits, so the line is TG-limited at both ends.
N_LO, N_HI = -1.27982, +3.25687                              # 1e12 cm^-2 (0.1 mV inside the TG limits)
n_vec = np.linspace(N_LO, N_HI, N_FAST)
_gv = np.array([calc_gate_voltages(nn, 0.0, CAL["c_tg"], CAL["c_bg"],
                                   CAL["n_offset"], CAL["D_offset"]) for nn in n_vec])
Vtg_vec, Vbg_vec = _gv[:, 0], _gv[:, 1]                      # fast, 5.00 mV = k_tg.volt.step
_n_rt, D_vec = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.max(np.abs(D_vec)) < 1e-9, f"fast axis is not D = 0: max|D| = {np.max(np.abs(D_vec)):.2e}"
assert np.allclose(_n_rt, n_vec, atol=1e-9), "n round-trip failed"
assert abs(Vtg_vec[1] - Vtg_vec[0] - 0.005) < 2e-5, f"TG step {Vtg_vec[1]-Vtg_vec[0]:.6f} V != 5.00 mV"

# --- envelope: every setpoint inside the committed validators (backstop is the validator itself) ---
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
assert B_vec.min() >= 0 and B_vec.max() <= B_SESSION_CAP, (B_vec.min(), B_vec.max())
assert len(Vtg_vec) == len(Vbg_vec) == N_FAST

# --- preconditions (assumed by this cell, not set by it) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05, fan starts at 0), "
      f"V_si = {k_si():+.3f} V (0), V_tg = {k_tg.volt():+.4f}, V_bg = {k_bg.volt():+.4f} V, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), step tg/bg = {k_2400_tg.volt.step}/{k_2400_bg.volt.step} V (0.005/0.005), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert k_2400_tg.volt.step == 0.005 and k_2400_bg.volt.step == 0.005, "gate ramp pacing changed"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- lock-in settling: tau 0.3 -> 0.1 s so the 1.0 s dwell is 10*tau (~1 % settled)
#     instead of run 5's 3.3*tau (~40 %). Filter slope untouched (24 dB/oct).
#     Noise cost ~sqrt(3) -> ~0.5 Ohm at 10 nA, negligible vs 10-500 Ohm features.
#     LEFT AT 0.1 s AFTER THIS RUN — later cells must re-read, not assume 0.3 s.
print(f"tau before: sr0 {sr0.time_constant()} s / {sr0.filter_slope()} dB, sr1 {sr1.time_constant()} s / {sr1.filter_slope()} dB")
sr0.time_constant(0.1); sr1.time_constant(0.1)
# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm FS at 10 nA.
sr1.sensitivity(100e-6)
FS_V = sr1.sensitivity()
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9
print(f"tau after:  sr0 {sr0.time_constant()} s, sr1 {sr1.time_constant()} s -> dwell {FAST_DELAY} s = {FAST_DELAY/sr1.time_constant():.0f} tau")
print(f"drive {sr1.amplitude()} V / {sr1.frequency():.3f} Hz -> I_bias {sr1.amplitude()/100e6*1e9:.2f} nA; "
      f"sr1 sens {FS_V} V ({FS_V/(sr1.amplitude()/100e6)/1e3:.1f} kOhm FS); sr0 sens {sr0.sensitivity()} V; "
      f"magnet settle_s {magnet.settle_s} s")
print(f"fan: {N_ROWS} rows x {N_FAST} pts = {N_ROWS*N_FAST} pts; B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T ({B_vec[1]-B_vec[0]:.2f} T); "
      f"n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f}e12 ({n_vec[1]-n_vec[0]:.4f}e12/pt); "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: B {B_vec[0]:.2f}->{B_vec[-1]:.2f} T slow ({N_ROWS} rows, 0.25 T) x "
                  f"(Vtg,Vbg) co-swept on the run-5 D=0 line fast ({N_FAST} pts, 5 mV TG), "
                  f"n {n_vec[0]:+.3f}->{n_vec[-1]:+.3f}e12; sr1 100 uV, tau 0.1 s, fast_delay 1 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan, region-A calibration (run 5: c_tg {CAL["c_tg"]:.4e} F/m2 [9.5 nm geometry prior], '
              f'c_bg/c_tg {CAL["c_bg"]/CAL["c_tg"]:.3f} [data], n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm); '
              f'slow magnet.field {B_vec[0]:.2f}->{B_vec[-1]:.2f} T, {N_ROWS} rows at 0.25 T; '
              f'fast (k_tg.volt, k_bg.volt) co-swept {N_FAST} pts, Vtg {Vtg_vec[0]:+.4f}->{Vtg_vec[-1]:+.4f} V (5.00 mV), '
              f'Vbg {Vbg_vec[0]:+.4f}->{Vbg_vec[-1]:+.4f} V, n {n_vec[0]:+.3f}->{n_vec[-1]:+.3f}e12 cm^-2 (dn {n_vec[1]-n_vec[0]:.4f}e12); '
              f'V_si = 0; sr1 sens 100 uV (10 kOhm FS), sr0/sr1 tau 0.1 s / 24 dB (dwell 10 tau); '
              f'region-B CNP expected at n ~ -0.43e12 on this axis (run-5 ridge offset)')

s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
I_B, I_VTG, I_ITG, I_IBG, I_SR1X = 1, 2, 5, 6, 9
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_clip = {"n": 0, "first": None}

def fan_guard(station, data):
    """Leak trip -> interrupt (device safety). Soft-clip -> count + report, never abort:
    a rail is expected only in the CNP column at high B and is itself a read."""
    if len(data) != 11:
        return
    i_tg, i_bg = abs(float(data[I_ITG])), abs(float(data[I_IBG]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[I_B]):+.3f} T, Vtg={float(data[I_VTG]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[I_SR1X])) >= 0.95 * FS_V:
        _clip["n"] += 1
        if _clip["first"] is None:
            _clip["first"] = (float(data[I_B]), float(data[I_VTG]))
            print(f"SOFT CLIP (sr1 >= 95 % of {FS_V} V FS) first at B={_clip['first'][0]:+.3f} T, "
                  f"Vtg={_clip['first'][1]:+.4f} V — continuing; clipped samples flagged in ana")

s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates parked at 0 V (inside the window, n ~ -0.09e12); field LEFT where the sweep
    # ended — the ride-down is the next step's, never a free re-traverse.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, "
          f"T_sample = {T_sample():.3f} K, soft-clipped samples = {_clip['n']}")
