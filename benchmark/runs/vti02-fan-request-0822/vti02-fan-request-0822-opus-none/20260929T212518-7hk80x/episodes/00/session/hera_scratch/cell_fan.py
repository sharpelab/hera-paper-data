# === Landau fan (`landau-fan`): B slow (uniform in 1/B, 0 -> 10 T) x n fast along D = 0 ===
# Plan step 4. Decides the stacking call: F vs n per tone (lines through the origin = subbands;
# equal-slope offset lines = the run-5 A/B mosaic; integer ratios = harmonics), plus the LL gap
# slopes dn/dB = nu*e/h, which give the absolute n scale independent of the 9.5 nm geometry prior.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: D = 0 line, n = -1.20 ... +3.20e12 (the realized D = 0 window inside the
#     validators is -1.27 ... +3.27; the ends are pulled in to land exactly on the run 6 / run 7
#     spot densities, so the fan's first and last columns reproduce those runs).
n_vec = np.round(np.arange(-1.20, 3.2001, 0.040), 4)        # 111 pts, 0.040e12 step
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_Dchk).max() < 1e-9 and np.abs(_nchk - n_vec).max() < 1e-9, "D = 0 line roundtrip failed"
print(f"fast axis: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 at D = 0, {len(n_vec)} pts ({np.diff(n_vec)[0]*1e3:.0f}e9 step); "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} ({np.diff(Vtg_vec)[0]*1e3:.1f} mV/pt), "
      f"Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} ({np.diff(Vbg_vec)[0]*1e3:.1f} mV/pt)")

# --- slow axis: 5 low-field context rows (incl. B = 0, the run-5 cross-check) + 145 rows
#     uniform in 1/B from 1 to 10 T. The 1/B-uniform block is what sdh_fft consumes with
#     b_range=(1, 10): dF = 1/(1/1 - 1/10) = 1.11 T, Nyquist (144)/(2*0.9) = 80 T -- above
#     2*F_L(3.2e12) = 66 T, so the second harmonic cannot alias onto the fundamental.
B_vec = np.round(np.concatenate(([0.0, 0.2, 0.4, 0.6, 0.8], 1.0 / np.linspace(1.0, 0.1, 145))), 5)
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP
print(f"slow axis: {len(B_vec)} rows, B {B_vec[0]} -> {B_vec[-1]} T; 1/B-uniform block "
      f"{np.sum(B_vec >= 1.0)} rows, dF {1/(1/1.0 - 1/10.0):.2f} T, Nyquist {(np.sum(B_vec >= 1.0)-1)/(2*0.9):.0f} T; "
      f"total ramp {B_vec[-1]/0.137:.0f} min")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.02: fan starts at 0), "
      f"V_si = {k_si():+.3f} V (0), Vtg/Vbg = {k_tg.volt():+.4f}/{k_bg.volt():+.4f} V (0/0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, "
      f"output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.02 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 0.5, 2.0
I_TRIP = 1e-9          # gate leak -> interrupt (run-5 flyback transients peak ~200 pA)
# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm FS at 10 nA.
# Observed maxima: 530 Ohm (run 6, n = +3.2e12 @ 10 T), 587 Ohm (run 7, n = -1.2e12 @ 10 T),
# 240 Ohm (run 5, CNP at B = 0, D = 0) -> ~17x headroom. The unknown is R_CNP at high B;
# the CNP column sits 28 % into every row, so R_CNP(B) is watchable from the first rows on.
sr1.sensitivity(100e-6)
R_FS = sr1.sensitivity() / (sr1.amplitude() / 100e6)
print(f"drive {sr1.amplitude()} V -> {sr1.amplitude()/100e6*1e9:.1f} nA; sr1 sens {sr1.sensitivity()} V "
      f"({R_FS/1e3:.1f} kOhm FS); sr0 sens {sr0.sensitivity()} V; tau {sr1.time_constant()} s "
      f"slope {sr1.filter_slope()} dB/oct; fast_delay {FAST_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan: B slow {B_vec[0]}->{B_vec[-1]} T ({len(B_vec)} rows, uniform in 1/B above 1 T) x "
                  f"n fast {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 at D = 0 ({len(n_vec)} pts, 0.040e12), "
                  f"Vsi = 0, sr1 100 uV, fast_delay {FAST_DELAY} s; cal run 5")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'B slow {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows (5 low-field context rows + 145 uniform in 1/B from 1 T); '
              f'n fast {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2 at D = 0, {len(n_vec)} pts (0.040e12); '
              f'(Vtg, Vbg) {Vtg_vec[0]:+.4f},{Vbg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f},{Vbg_vec[-1]:+.4f}; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_tg.volt, Vtg_vec[0]); s.ramp(k_bg.volt, Vbg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', sr1.P); s.plot('time', sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_rail = {"n": 0, "row": None}

def leak_and_rail_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    # soft rail watch: warn once per row, never abort (a railed CNP column costs the CNP read,
    # not the F-vs-n read that carries the call)
    if abs(float(data[9])) > 0.9 * sr1.sensitivity():
        b = round(float(data[1]), 4)
        if _rail["row"] != b:
            _rail["row"] = b; _rail["n"] += 1
            _i = abs(float(data[7])) / abs(meas_config["sr0_gain"])   # sr0_X is stored raw; gain divides here
            _r = abs(float(data[9])) / _i if _i > 0 else float("inf")
            print(f"RAIL WATCH: sr1 > 90 % FS at B={b:+.3f} T, Vtg={float(data[2]):+.4f} "
                  f"(R ~ {_r:.0f} Ohm); rows flagged so far: {_rail['n']}")

s.register_run_after(leak_and_rail_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY, init_delay=True)

# Park: gates left at the n = +3.2e12 end, field left at 10 T -- the next step (Lifshitz / D-scan
# or an LK ladder) wants high field, and the magnet's fixed 0.137 T/min makes a return traverse
# 73 min. No re-traverse here; close-out does it at the end of the session.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
      f"T_sample = {T_sample():.3f} K, rail-flagged rows: {_rail['n']}")
