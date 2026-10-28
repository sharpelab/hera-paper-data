# === Landau fan, electron side, D = 0 (`landau-fan-vti`): n +1.8 -> +3.2e12 (43) x B 0.75 -> 10 T uniform-1/B (165) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0
ns = np.linspace(1.8, 3.2, 43)                                   # 1e12 cm^-2, fast axis (dn = 0.0333e12)
_V = np.array([calc_gate_voltages(n, D0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]) for n in ns])
Vtgs, Vbgs = _V[:, 0], _V[:, 1]
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs, Vbgs)
print(f"n-line: n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = {D0} -> Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V; "
      f"roundtrip ends {calc_nD(Vtgs[0], Vbgs[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}, "
      f"{calc_nD(Vtgs[-1], Vbgs[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

B_vec = field_invB(0.75, 10.0, 165)                               # ascending, d(1/B) = 0.00752 T^-1 (Nyquist 66.5 T)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
print(f"B grid: {len(B_vec)} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {abs(np.diff(1/B_vec)).mean():.5f} T^-1")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.1: ascending fan from 0, priced from 0), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert abs(_B0) < 0.1, f"magnet not near 0 T: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
_tau1, _sl1, _tau0, _sl0 = sr1.time_constant(), sr1.filter_slope(), sr0.time_constant(), sr0.filter_slope()
_amp, _f = sr1.amplitude(), sr1.frequency()
print(f"lock-ins: sr1 tau {_tau1} s / {_sl1} dB, sr0 tau {_tau0} s / {_sl0} dB (expect 0.3 / 24); drive {_amp} V @ {_f:.3f} Hz (expect 1.0 V, 13.777)")
assert _tau1 == 0.3 and _sl1 == 24 and _tau0 == 0.3 and _sl0 == 24, "lock-in tau/slope changed - fast_delay was priced at 6 tau = 1.8 s"
assert abs(_amp - 1.0) < 1e-6 and abs(_f - 13.777) < 0.01, "drive changed"

# --- fixed sensitivity for the whole fan (no autorange): 50 uV = 5 kOhm FS at 10 nA (spot-check setting) ---
SENS1 = 50e-6
sr1.sensitivity(SENS1)
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS), sr0 sens {sr0.sensitivity()} V")
FAST_DELAY, SLOW_DELAY = 1.8, 2.0
I_TRIP, T_TRIP, CLIP = 1e-9, 1.6, 0.95

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron: D = 0, n +1.8 -> +3.2e12 (43), B 0.75 -> 10 T uniform-1/B (165), "
                  f"sr1 50 uV, fast_delay 1.8 s (6 tau), slow_delay 2 s; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = +1.8 to +3.2e12 cm^-2 (43 pts, paired Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f} / Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f}), '
              f'B = 0.75 to 10 T uniform in 1/B (165 rows, d(1/B) 0.00752); tetralayer-stacking-fs-count Step 4; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; spot checks runs 6/7')

# position: gates to the row start, magnet to B_lo (blocking set is the settle)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
s.ramp(magnet.field, B_vec[0])
interruptible_sleep(10)
print(f"positioned: B = {magnet.field():+.4f} T, Vtg = {k_tg.volt():+.4f}, Vbg = {k_bg.volt():+.4f}")

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def fan_guard(station, data):
    B, i_tg, i_bg, T, x1 = float(data[1]), abs(float(data[5])), abs(float(data[6])), float(data[4]), abs(float(data[9]))
    why = []
    if i_tg > I_TRIP or i_bg > I_TRIP: why.append(f"LEAK |I_tg|={i_tg:.3e} |I_bg|={i_bg:.3e} A")
    if x1 > CLIP * SENS1: why.append(f"CLIP |sr1.X|={x1:.3e} V > {CLIP} FS")
    if T > T_TRIP: why.append(f"T_sample={T:.3f} K > {T_TRIP}")
    if why:
        print(f"FAN GUARD TRIP at B={B:+.3f} T, Vtg={float(data[2]):+.4f}: " + "; ".join(why))
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY, init_delay=True)
# field stays at 10 T, gates at n = +3.2e12 — the LK temperature series rides the field down (no re-traverse).
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
