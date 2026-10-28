# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +1.2 -> +3.2e12, B 0.8 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(1.2, 3.2, 51)                  # 1e12 cm^-2, dn = 4.0e10 (>=2 pts/ray at 0.8 T)
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
print(f"n-line: {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = 0, {len(ns)} pts; "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")

# --- B rows: two uniform-1/B segments, ascending from where the magnet sits (0 T -> start 0.8 T) ---
# seg A 0.8 -> 1.3 T, d(1/B) = 0.0209 (Nyquist to 24 T; only the light tone f~7 T lives below 1.3 T)
# seg B 1.3 -> 10 T,  d(1/B) = 0.00735 (3 pts/period at 45 T, Nyquist to 68 T; heavy tones onset 1.4-1.9 T)
invB = np.unique(np.round(np.hstack((np.linspace(1/0.8, 1/1.3, 24),
                                     np.linspace(1/1.3, 1/10.0, 92))), 8))[::-1]
B_vec = np.round(1.0/invB, 4)
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"B rows: {len(B_vec)} pts, {B_vec[0]} -> {B_vec[-1]} T; dF(full record) = {1/(1/B_vec[0]-1/B_vec[-1]):.2f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
assert abs(_tau - 0.3) < 0.01 and _slope == 24, (_tau, _slope)   # dwell below is priced on tau = 0.3 s / 24 dB

# --- lock-in: fixed sensitivity for the whole fan (worst corner n=1.2e12 x 10 T: ~100 Ohm x MR ~4-6 -> <1 kOhm on 5 kOhm FS) ---
sr1.sensitivity(50e-6)
FAST_DELAY, SLOW_DELAY = 2.1, 1.0               # 7*tau = 24 dB settling floor; magnet set blocks + 3 s driver settle
I_TRIP = 1e-9
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS at 10 nA), tau {_tau} s / {_slope} dB; "
      f"fast_delay {FAST_DELAY} s (7 tau), drive {sr1.amplitude()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron: n = +1.2..+3.2e12, D = 0 (run-5 cal), B 0.8 -> 10 T "
                  f"115 rows uniform-1/B (2 seg), 51-pt n-line, sr1 50 uV, fast_delay 2.1 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = 0.00 V/nm: n = +1.20 to +3.20e12 cm^-2 (51 pts); '
              f'B = 0.8 -> 10 T, 115 rows uniform-1/B (d(1/B) 0.0209 to 1.3 T, 0.00735 above); '
              f'inherits run-6 spot check (tones 7.1/22.1/29.5 T, sens 50 uV); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')

s.ramp(k_tg.volt, Vtgs[0]); s.ramp(k_bg.volt, Vbgs[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f} V: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# End state: field at 10 T, gates at the top of the n-line (n = +3.2e12) — the likely LK-mass spot;
# the next step (LK ladder / ride-down) decides the field endpoint. No blind park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
