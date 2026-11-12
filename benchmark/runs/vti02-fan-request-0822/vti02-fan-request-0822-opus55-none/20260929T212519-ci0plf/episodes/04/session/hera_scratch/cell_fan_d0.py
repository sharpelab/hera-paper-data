# === Landau fan at D = 0 (`landau-fan`): B slow 0.6 -> 10 T ascending x n fast -1.25 -> +3.20e12 along D = 0 (co-swept Vtg/Vbg) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, c_tg = 9.5 nm geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D_FAN = 0.0                                            # V/nm
n_vec = np.round(np.arange(-1.25, 3.2001, 0.05), 4)   # 1e12 cm^-2, 90 pts (D = 0 line reaches -1.28 .. +3.26 inside the validators)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.full_like(n_vec, D_FAN), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.round(Vtg_vec, 5), np.round(Vbg_vec, 5)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, "fast vector outside validators"
_n_chk, _D_chk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_n_chk, n_vec, atol=1e-3) and np.allclose(_D_chk, D_FAN, atol=1e-4)
print(f"fast: {len(n_vec)} pts n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 at D = {D_FAN}; Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f}, "
      f"Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V")

# --- slow: field, ascending from where the magnet sits (0 T). Uniform in 1/B at low B (FFT-ready), uniform in B above:
#     0.6 -> 1.25 T at d(1/B) = 0.03 (Nyquist 16.7 T; only light tones alive there), 1.25 -> 2.76 T at d(1/B) = 0.0125
#     (Nyquist 40 T > F_L max 33 T), 2.8 -> 10 T at 0.1 T.
B_vec = np.unique(np.round(np.hstack((1 / np.arange(1 / 0.6, 0.8 - 1e-9, -0.03),
                                      1 / np.arange(0.8, 0.35355 - 1e-9, -0.0125),
                                      np.arange(2.8, 10.0 + 1e-9, 0.1))), 4))
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"slow: {len(B_vec)} rows B {B_vec[0]} -> {B_vec[-1]} T; max d(1/B) {np.max(-np.diff(1/B_vec)):.4f}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_pre = dict(T_sample=_T0, B=_B0, V_si=k_si(), nplci=(k_tg.nplci(), k_bg.nplci()), PS=magnet.persistent_switch_on(),
            out=magnet.output_enabled(), heater_ranges=(int(heater.sample_range()), int(heater.vaporizer_range())),
            drive=(sr1.amplitude(), sr1.frequency()), sr1_tau=(sr1.time_constant(), sr1.filter_slope()), sr0_sens=sr0.sensitivity())
print("precondition expected: T 1.0-1.5 K, |B| < 0.05 T, V_si 0, nplci (1,1), PS on, output on, heaters (0,0), drive (1.0 V, 13.777 Hz), "
      "sr1 tau (0.3 s, 24 dB), sr0 sens 0.02")
print("precondition actual:  ", _pre)
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} off base"
assert abs(_B0) < 0.05, f"magnet not at 0: {_B0}"
assert abs(_pre["V_si"]) < 0.01, "Si gate not at 0"
assert _pre["nplci"] == (1, 1), "gate-current nplci not 1"
assert _pre["PS"] and _pre["out"], "magnet PS heater / output"
assert _pre["heater_ranges"] == (0, 0), "a heater range is on"
assert abs(_pre["drive"][0] - 1.0) < 1e-3 and abs(_pre["drive"][1] - 13.777) < 0.01, "drive not 1.0 V / 13.777 Hz (I_bias 10 nA)"
assert _pre["sr1_tau"] == (0.3, 24), "sr1 tau/slope changed — fast_delay is priced on 0.3 s / 24 dB"
assert abs(_pre["sr0_sens"] - 0.02) < 1e-9, "sr0 sensitivity not 20 mV (20 nA FS)"

# Fixed sensitivity for the whole fan (state0 restore left sr1 at 2 uV): 100 uV = 10 kOhm FS at 10 nA.
# Runs 6-7 peaked at 590 Ohm at 10 T; the CNP stripe at high B may rail — accepted (not needed for F(n)).
sr1.sensitivity(100e-6)
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP, N_TRIP = 1e-9, 2          # A; consecutive points over threshold before abort (single flyback glitch is not a leak)
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS); fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: B slow {B_vec[0]} -> {B_vec[-1]} T ({len(B_vec)} rows, 1/B-uniform below 2.8 T), "
                  f"n fast {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, 0.05e12) along D = 0, Vsi 0, sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_FAN} V/nm (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}); '
              f'n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 step 0.05 (co-swept Vtg/Vbg); B {B_vec[0]} -> {B_vec[-1]} T ascending, '
              f'd(1/B) 0.03 to 1.25 T, 0.0125 to 2.76 T, then 0.1 T; fast_delay {FAST_DELAY} s; plan step 4')

s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
s.ramp(magnet.field, B_vec[0])        # 0 -> 0.6 T, blocking ~4.5 min
print(f"at start: B = {magnet.field():+.4f} T, Vtg {k_tg.volt():+.4f}, Vbg {k_bg.volt():+.4f}")
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, magnet.field, sr1.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)
s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)

_over = {"n": 0}
def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    _over["n"] = _over["n"] + 1 if (i_tg > I_TRIP or i_bg > I_TRIP) else 0
    if _over["n"] >= N_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A ({N_TRIP} consecutive)")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates park at 0 (safe unattended end / abort); field stays where the fan left it (10 T at completion) —
    # the next step (finite-D fan) rides it down, never re-traversing.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.4f} T, Vtg {k_tg.volt():+.4f}, Vbg {k_bg.volt():+.4f}, T_sample {T_sample():.3f} K")
