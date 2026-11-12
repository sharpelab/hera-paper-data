# === Landau fan (`landau-fan-vti`), D = 0 electron side: n = +3.2 -> +0.6e12 (fast, 53 cols) x B = 0.7 -> 10 T (slow, 133 rows, uniform 1/B) ===
# E1 auto cell: in-envelope (gates inside the committed validators, |B| <= B_SESSION_CAP, no T move).
import time as _time
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0                                              # V/nm
ns = np.round(np.arange(3.2, 0.6 - 1e-9, -0.05), 3)    # 1e12 cm^-2, high n first each row (53 cols, 0.05e12)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert len(Vtgs) == len(ns) == 53
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
_nchk, _Dchk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast axis: n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({len(ns)} cols, 0.05e12) at D = {D0:+.2f} V/nm; "
      f"Vtg [{Vtgs.min():+.4f}, {Vtgs.max():+.4f}] V, Vbg [{Vbgs.min():+.4f}, {Vbgs.max():+.4f}] V; roundtrip max|dn| = {np.abs(_nchk - ns).max():.1e}, max|D| = {np.abs(_Dchk).max():.1e}")

# --- slow axis: uniform in 1/B, 0.7 -> 10 T. Nyquist 1/3 on F_L(n_max = 3.2e12) = 33.1 T -> d(1/B) <= 0.01007 /T.
B_LO, B_HI = 0.7, 10.0
F_L_MAX = 33.09                                       # T, (h/4e)*3.2e12 cm^-2
N_B = int(np.ceil((1 / B_LO - 1 / B_HI) * 3 * F_L_MAX)) + 1     # 133
B_vec = 1.0 / np.linspace(1 / B_LO, 1 / B_HI, N_B)
d_invB = (1 / B_LO - 1 / B_HI) / (N_B - 1)
assert B_vec.max() <= B_SESSION_CAP and d_invB <= 1 / (3 * F_L_MAX)
print(f"slow axis: {N_B} rows, B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {d_invB:.5f} /T ({1/(d_invB*F_L_MAX):.2f} rows/period at F_L = {F_L_MAX} T); "
      f"dB {B_vec[1]-B_vec[0]:.4f} T (first) .. {B_vec[-1]-B_vec[-2]:.3f} T (last); dF = {1/(1/B_LO-1/B_HI):.2f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vap = {T_vaporizer():.3f} K, B = {_B0:+.4f} T (|B| < 0.05: fan positions 0 -> 0.7 T), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

# --- lock-in: fixed sensitivity for the whole fan (no autorange). 100 uV = 10 kOhm FS at 10 nA:
# worst corner is low n x high B (n = 0.6e12 at 10 T is nu ~ 2.5); spot checks (50 uV) peaked at 590 Ohm at nu ~ 5.
sr1.sensitivity(100e-6)
FAST_DELAY, SLOW_DELAY = 1.0, 3.0                     # fast 1.0 s = 3.3 tau (tau 0.3 s / 24 dB) as in gatemap run 5 (1.10 s/pt measured)
I_TRIP = 1e-9
print(f"drive {sr1.amplitude()} V / 100 MOhm -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB; "
      f"sr0 sens {sr0.sensitivity()} V; magnet settle_s {magnet.settle_s} s; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side D = 0 (run-5 cal): n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 fast ({len(ns)} cols), "
                  f"B {B_LO} -> {B_HI} T slow ({N_B} rows, uniform 1/B, d(1/B) {d_invB:.5f}), sr1 100 uV, fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {ns[-1]:+.2f} to {ns[0]:+.2f}e12 cm^-2 (fast, {len(ns)} cols, 0.05e12, high n first), '
              f'B = {B_LO} to {B_HI} T (slow, {N_B} rows, uniform 1/B, d(1/B) = {d_invB:.5f} /T = 1/3 Nyquist on F_L(3.2e12) = {F_L_MAX} T); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'sr1 100 uV, tau 0.3 s; B_lo from spot checks (run 7 onset 0.71 T, run 6 censored at 1 T)')

# gates to the row start (n_hi), then position the magnet at B_lo (blocking ramp ~5 min from 0 T; this set is the settle)
s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)
_t = _time.time(); magnet.field(float(B_vec[0]))
print(f"positioned: B = {magnet.field():+.4f} T in {(_time.time()-_t)/60:.1f} min; gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V; T_sample {T_sample():.3f} K")

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

_t = _time.time()
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # park gates at 0; leave the field where the fan ends (10 T) for the next step -- stated in the proposal
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done in {(_time.time()-_t)/3600:.2f} h: B = {magnet.field():+.3f} T (left there), gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample {T_sample():.3f} K")
