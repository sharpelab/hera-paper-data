# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +3.2 -> +1.0e12 (fast), B 1.0 -> 10 T uniform in 1/B (slow) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
import scipy.constants as cst

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0
# fast axis: paired (Vtg, Vbg) n-line at D = 0, n_hi -> n_lo each row (step 0.04e12)
ns = np.linspace(3.2, 1.0, 56)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.all((Vtgs >= TG_MIN) & (Vtgs <= TG_MAX)) and np.all((Vbgs >= BG_MIN) & (Vbgs <= BG_MAX)), (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
# slow axis: uniform in 1/B, d(1/B) = 0.010 /T (3.0 samples per period of F_L(3.2e12) = 33.1 T)
B_LO, B_HI, N_B = 1.0, 10.0, 91
B_vec = np.round(1.0 / np.linspace(1.0 / B_LO, 1.0 / B_HI, N_B), 5)
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
dinvB = (1 / B_LO - 1 / B_HI) / (N_B - 1)
F_L = ns.max() * 1e16 * cst.h / (4 * cst.e)                      # T, g = 4
dn_ray = 4 * cst.e * B_LO / cst.h / 1e16                          # LL ray spacing at B_lo, 1e12 cm^-2
print(f"fast n-line: n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({len(ns)} pts, step {abs(ns[1]-ns[0]):.3f}e12) at D = {D0:+.2f}; "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V; "
      f"roundtrip n,D at ends = {calc_nD(Vtgs[0], Vbgs[0], **CAL)}, {calc_nD(Vtgs[-1], Vbgs[-1], **CAL)}")
print(f"slow B: {N_B} rows {B_vec[0]} -> {B_vec[-1]} T uniform 1/B, d(1/B) = {dinvB:.4f} /T -> {1/(dinvB*F_L):.2f} samples/period at F_L(n_max) = {F_L:.1f} T; "
      f"dB first/last step {B_vec[1]-B_vec[0]:.3f}/{B_vec[-1]-B_vec[-2]:.3f} T; delta_F = {1/(1/B_LO-1/B_HI):.2f} T; "
      f"ray Nyquist at B_lo: dn = {dn_ray:.3f}e12 -> {dn_ray/abs(ns[1]-ns[0]):.1f} pts/period")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left 0 T; cell positions to {B_LO} T), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
# lock-in state the dwell is priced against (front-panel set; design assumes tau 0.3 s / 24 dB)
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
assert _tau == 0.3 and _slope == 24, (_tau, _slope)
sr1.sensitivity(50e-6)   # fixed for the whole fan: 5 kOhm FS at 10 nA, inherited from spot checks 6/7 (peaks 522/576 Ohm = 10-12 % FS)
FAST_DELAY, SLOW_DELAY = 1.5, 3.0   # 5 tau along n (uniform ~4 tau lag = 1 column); 10 tau after each flyback (on top of the magnet's 3 s settle_s)
print(f"sr1 sens {sr1.sensitivity()} V, tau {_tau} s, slope {_slope} dB/oct; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = {D0:+.2f} V/nm, n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({len(ns)} pts, fast), "
                  f"B = {B_LO} -> {B_HI} T uniform 1/B ({N_B} rows, d(1/B) = {dinvB:.4f}), fast_delay {FAST_DELAY}, slow_delay {SLOW_DELAY}, sr1 50 uV; cal run 5")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {ns[-1]:+.2f} to {ns[0]:+.2f}e12 cm^-2 ({len(ns)} pts, fast axis n_hi -> n_lo, paired Vtg/Vbg), '
              f'B = {B_LO} to {B_HI} T uniform in 1/B ({N_B} rows, d(1/B) = {dinvB:.4f} /T); fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; '
              f'sr1 50 uV, tau {_tau} s / {_slope} dB; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'design from spot checks 6 (electron, onset < 1 T, tones 7.1/14.1/22.1/29.5 T) and 7 (hole)')

# gates to the first fast point, then position the magnet (blocking ramp 0 -> 1 T, ~7.5 min; the set call is the settle)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
print(f"positioning magnet -> {B_LO} T (blocking, ~{(B_LO-_B0)/0.137:.1f} min) ...")
magnet.field(B_vec[0])
print(f"at B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")

# row layout: [time, magnet_field, k_tg_volt, k_bg_volt, T_sample, k_tg_curr, k_bg_curr, sr0_X, sr0_P, sr1_X, sr1_P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

I_TRIP = 1e-9
_rail = {"n": 0}
def guards(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[9])) >= 0.95 * 50e-6:          # soft-clip watch on sr1 (report only; a railed low-n/high-B corner is a column loss, not a stop)
        _rail["n"] += 1
        if _rail["n"] <= 20: print(f"RAIL sr1 at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: X={float(data[9])*1e6:.1f} uV")
s.register_run_after(guards, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)

# park gates; the field stays at 10 T (next steps — firming spot check / LK ladder — ride it down, never re-traverse)
s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
print(f"done: B = {magnet.field():+.3f} T (left at B_HI), (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), rail hits {_rail['n']}, T_sample = {T_sample():.3f} K")
