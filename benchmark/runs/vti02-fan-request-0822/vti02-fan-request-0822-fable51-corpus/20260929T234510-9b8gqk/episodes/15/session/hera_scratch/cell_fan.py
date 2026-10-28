# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +3.25 -> +1.0e12 (fast, paired TG/BG), B 0.8 -> 10 T (slow) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_HI, N_LO, D0, N_N = 3.25, 1.0, 0.0, 61          # 1e12 cm^-2, V/nm; N_HI is TG-limited (3.26 -> Vtg 1.0008 > TG_MAX)
B_LO, B_MID, B_HI = 0.8, 6.0, 10.0                # T; B_LO = sdh_onset lower bound from run 8, floored at 0.8 (see markdown)
F_L_MAX = 33.6                                    # T = (h/4e) n at n = 3.25e12 — the fastest expected tone
D_INVB = 1.0 / (4.0 * F_L_MAX)                    # 0.00744 /T: Nyquist 1/4 on F_L(n_max) -> Nyquist frequency 67 T >= 2 F_L
SLOW_DELAY, FAST_DELAY, TAU_FAN = 1.0, 0.8, 0.1   # s; fast_delay = 8 tau at tau 0.1 s (4-pole: 96 % settled per fast step)
I_TRIP = 1e-9

# --- fast axis: paired (Vtg, Vbg) n-line at D = 0 (landau-fan step 2, VTI variant call form) ---
ns = np.linspace(N_HI, N_LO, N_N); Ds = np.full(N_N, D0)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
_n_chk, _D_chk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_n_chk, ns, atol=2e-3) and np.allclose(_D_chk, D0, atol=2e-3)
print(f"fast axis: n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({N_N} pts, dn {abs(ns[1]-ns[0]):.4f}e12), D = {D0:+.2f}; "
      f"Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V")

# --- slow axis: uniform in 1/B B_LO -> B_MID (per-column SdH FFT), then 0.2 T steps to B_HI (nu-ladder) ---
_n_inv = int(np.ceil((1.0 / B_LO - 1.0 / B_MID) / D_INVB)) + 1
B_vec = np.round(np.hstack((1.0 / np.linspace(1.0 / B_LO, 1.0 / B_MID, _n_inv), np.arange(B_MID + 0.2, B_HI + 1e-6, 0.2))), 4)
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP
print(f"slow axis: {len(B_vec)} rows ({_n_inv} uniform-1/B {B_LO}->{B_MID} T, d(1/B) {D_INVB:.5f} /T = {1e3*D_INVB*B_LO**2:.1f} mT at B_LO; "
      f"{len(B_vec)-_n_inv} rows at 0.2 T to {B_HI} T); grid {len(B_vec)*N_N} pts")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (expect ~1.2 T: run 8 ended there; the fan positions to {B_LO} T itself), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 2.0 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

# --- lock-in: fixed for the whole fan (landau-fan step 3). 100 uV = 10 kOhm FS at 10 nA clears the low-n x 10 T corner
#     (run 7: 590 Ohm at nu ~ 5 and climbing); LSB 0.37 Ohm vs 5-20 Ohm SdH amplitudes (run 6). tau 0.1 s restored in finally.
_tau0 = sr1.time_constant()
sr1.sensitivity(100e-6); sr1.time_constant(TAU_FAN)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s (was {_tau0}), slope {sr1.filter_slope()} dB; "
      f"sr0 sens {sr0.sensitivity()} V tau {sr0.time_constant()} s; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = {D0:+.2f} V/nm, n {N_HI:+.2f} -> {N_LO:+.2f}e12 fast ({N_N} pts, paired TG/BG, run-5 cal), "
                  f"B {B_LO} -> {B_HI} T slow ({len(B_vec)} rows: uniform-1/B to {B_MID} T then 0.2 T), sr1 100 uV tau {TAU_FAN} s, fast_delay {FAST_DELAY}, slow_delay {SLOW_DELAY}")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'landau-fan (VTI variant), per-column SdH-FFT design: D = {D0:+.2f} V/nm, n = {N_HI:+.2f} to {N_LO:+.2f}e12 cm^-2 ({N_N} pts), '
              f'B = {B_LO} to {B_HI} T ({len(B_vec)} rows; d(1/B) = {D_INVB:.5f}/T to {B_MID} T, 0.2 T above); B_LO from run 8 onset (floored 0.8 T); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; Vsi = 0')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]  (guards index from the end)
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_rail_n = [0]
def fan_guard(station, data):
    i_tg, i_bg, v1 = abs(float(data[-6])), abs(float(data[-5])), abs(float(data[-2]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if v1 >= 0.95 * 100e-6 and _rail_n[0] < 20:
        _rail_n[0] += 1
        print(f"RAIL sr1 {v1/100e-6:.2f} fs at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f} V (row point {_rail_n[0]})")
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    sr1.time_constant(_tau0)
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # park gates; field is left at the fan's end (10 T) — the next step rides it down
    print(f"end: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), sr1 tau {sr1.time_constant()} s, "
          f"T_sample = {T_sample():.3f} K, rail points {_rail_n[0]}")
