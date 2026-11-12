# === Landau fan, electron side (`landau-fan-vti`): D = 0, n = +3.24 -> +1.00e12 (fast, paired TG/BG), B 0.65 -> 10 T (slow) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_hi, n_lo, N_n, D0 = 3.24, 1.00, 61, 0.0          # 1e12 cm^-2 (n_hi: V_tg = 0.995 V, 5 mV under the TG limit), V/nm
ns = np.linspace(n_hi, n_lo, N_n)                   # fast axis, high -> low n (recipe idiom); dn = 0.037e12
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
print(f"fast axis: n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({N_n} pts, dn {ns[0]-ns[1]:.4f}e12) at D = {D0:+.2f}; "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V; "
      f"roundtrip (n, D) at n_hi = {calc_nD(Vtgs[0], Vbgs[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- slow axis: uniform in 1/B, d(1/B) = 0.010 /T (Nyquist to 50 T; 3 samples/period at F_L(n_hi) = 33.5 T), 0.65 -> 5 T;
#     then 0.25 T steps 5 -> 10 T (keeps the nu = 8/12/16 ladder imaged at low n). Ascending: the magnet sits at 0 T.
D_INVB = 0.010
B_vec = np.unique(np.round(np.hstack((1.0 / np.arange(1 / 0.65, 1 / 5.0 - 1e-9, -D_INVB), np.arange(5.0, 10.0001, 0.25))), 4))
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"slow axis: {len(B_vec)} rows, B {B_vec[0]} -> {B_vec[-1]} T; max d(1/B) = {np.max(np.abs(np.diff(1/B_vec))):.4f} /T; "
      f"rows below 1.5 T: {(B_vec < 1.5).sum()}, below 3 T: {(B_vec < 3.0).sum()}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (expect ~0: handoff left the magnet at 0 T; fan ramps up to {B_vec[0]} T first), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1 and magnet.persistent_switch_on() and magnet.output_enabled()

# --- lock-in: fixed sensitivity for the whole fan (no autorange). 100 uV = 10 kOhm FS at 10 nA: worst corner is n = 1.0 x 10 T
#     (nu ~ 4); the spot checks peaked at 530 Ohm (run 6, 8.7 T) / 590 Ohm (run 7, CNP side, 10 T) -> 17x headroom over that.
FAST_DELAY, SLOW_DELAY = 1.2, 2.0     # 4 tau at tau = 0.3 s / 24 dB: a constant sub-step lag along n, identical for every row
I_TRIP = 1e-9
sr1.sensitivity(100e-6)
R_FS = sr1.sensitivity() / (sr1.amplitude() / 100e6)
print(f"drive {sr1.amplitude()} V -> {sr1.amplitude()/100e6*1e9:.1f} nA; sr1 sens {sr1.sensitivity()} V ({R_FS/1e3:.0f} kOhm FS), tau {sr1.time_constant()} s, "
      f"slope {sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = {D0:+.2f} V/nm, n = {n_hi:+.2f} -> {n_lo:+.2f}e12 ({N_n} pts), B = {B_vec[0]} -> {B_vec[-1]} T "
                  f"({len(B_vec)} rows, uniform 1/B d(1/B)={D_INVB} to 5 T then 0.25 T), sr1 100 uV, fast_delay {FAST_DELAY} s; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {n_hi:+.2f} to {n_lo:+.2f}e12 cm^-2 ({N_n} pts, paired TG/BG), B = {B_vec[0]} to {B_vec[-1]} T '
              f'({len(B_vec)} rows: uniform-1/B d(1/B) = {D_INVB} /T to 5 T, 0.25 T steps above); electron side per spot checks runs 6/7; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_rail = {"n": 0, "last_B": None}
def guards(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[9])) >= 0.95 * 100e-6:          # sr1 soft-clip flag: report per row, do not abort (low-n x high-B corner is not the claim)
        _rail["n"] += 1
        if _rail["last_B"] != data[1]:
            _rail["last_B"] = data[1]; print(f"RAIL sr1 >= 95% FS at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f} (row flagged; {_rail['n']} pts so far)")
s.register_run_after(guards, ())

s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)      # park gates; field stays at 10 T for the next step to ride down
print(f"done: B = {magnet.field():+.3f} T (left at the top for the ride-down), gates parked (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}); rail pts {_rail['n']}")
