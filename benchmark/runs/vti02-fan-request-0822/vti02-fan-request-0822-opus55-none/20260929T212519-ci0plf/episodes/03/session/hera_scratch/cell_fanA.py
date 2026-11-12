# === Fan A (`landau-fan`): Rxx(n, B) along D = 0 — n fast -1.25 -> +3.25e12 (91), B slow 1 -> 10 T (122 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (same CAL as spot runs 6/7; ratio data-calibrated, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D_FAN = 0.0                                                     # V/nm
n_vec = np.round(np.arange(-1.25, 3.25 + 0.025, 0.05), 4)       # 1e12 cm^-2, 91 pts
_v = [calc_gate_voltages(n, D_FAN, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]) for n in n_vec]
Vtg_vec = np.array([float(a) for a, _ in _v]); Vbg_vec = np.array([float(b) for _, b in _v])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
print(f"n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts) at D = {D_FAN} V/nm: "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V; "
      f"roundtrip end = {calc_nD(Vtg_vec[-1], Vbg_vec[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- field grid: uniform in 1/B (d(1/B) = 1/120 T^-1, F_nyq 60 T) from 1 T up to 4.9 T, then uniform 0.2 T steps to 10 T ---
_DINV, _DB = 1 / 120, 0.2
_B1 = 1 / np.arange(1.0, 1 / np.sqrt(_DB / _DINV), -_DINV)
B_vec = np.round(np.hstack((_B1, np.arange(_B1[-1] + _DB, 10.0 + 1e-9, _DB))), 4)
assert (np.diff(B_vec) > 0).all() and B_vec.min() >= 1.0 and B_vec.max() <= min(10.0, B_SESSION_CAP), (B_vec.min(), B_vec.max())
print(f"B grid: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T (1/B-uniform to {_B1[-1]:.2f} T, then {_DB} T steps)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _Tv0, _B0 = T_sample(), T_vaporizer(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {_Tv0:.3f} K, B = {_B0:+.4f} T (|B|<0.05), "
      f"V_si = {k_si():+.3f} V (0), heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), "
      f"PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} off base"
assert abs(_B0) < 0.05, f"magnet not near 0: {_B0}"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "heater range not off"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
_amp, _f, _tau = sr1.amplitude(), sr1.frequency(), sr1.time_constant()
print(f"drive {_amp} V @ {_f} Hz -> I_bias {_amp/100e6*1e9:.1f} nA (10); tau sr1/sr0 = {_tau}/{sr0.time_constant()} s (0.3 — prices fast_delay)")
assert abs(_amp - 1.0) < 1e-6 and abs(_f - 13.777) < 0.01 and _tau == 0.3 and sr0.time_constant() == 0.3

# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm FS at 10 nA
# (runs 6/7 peak 590 Ohm; headroom for the D = 0 CNP going insulating at high B — rails there accepted).
sr1.sensitivity(100e-6)
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V")
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP, T_TRIP = 1e-9, 2.5
_hot = [0]

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan A: D = {D_FAN} V/nm, n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({len(n_vec)}), "
                  f"B 1 -> 10 T ({len(B_vec)} rows, 1/B-uniform to 4.9 T then 0.2 T), sr1 100 uV, run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'fan A: D = {D_FAN:+.2f} V/nm fixed; fast = (Vtg, Vbg) co-swept along D = 0, n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2, '
              f'{len(n_vec)} pts (0.05e12); slow = B 1 -> 10 T, {len(B_vec)} rows, uniform 1/B (d = 1/120 T^-1) to 4.9 T then 0.2 T; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e} (9.5 nm prior), n_offset {CAL["n_offset"]:+.4f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f}; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, tau 0.3 s/24 dB; Vsi 0')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def guard(station, data):
    i_tg, i_bg, t = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    _hot[0] = _hot[0] + 1 if t > T_TRIP else 0
    if _hot[0] >= 3:
        print(f"T TRIP: T_sample {t:.3f} K > {T_TRIP} K on 3 consecutive points at B={float(data[1]):.3f} T")
        station.interrupt_requested = True
s.register_run_after(guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# field stays where the fan ended (10 T on completion) — Fan B rides it down; never re-traverse.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample {T_sample():.3f} K")
