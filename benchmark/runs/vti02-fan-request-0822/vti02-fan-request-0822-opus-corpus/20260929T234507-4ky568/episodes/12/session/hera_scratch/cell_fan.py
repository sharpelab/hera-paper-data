# === Landau fan (`landau-fan-vti`), electron side, D = 0: n 2.00 -> 3.20e12 x B 0.65 -> 10 T (uniform 1/B) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_N = 2.00, 3.20, 40      # 1e12 cm^-2; top column == run-6 spot density (grid-change reproduction)
B_LO, B_HI, N_B = 0.65, 10.0, 145     # T; d(1/B) = 0.00999 1/T = Nyquist/3 on F_L(3.20e12) = 33.1 T
FAST_DELAY, SLOW_DELAY = 2.1, 1.0     # fast = 7*tau settling floor at 24 dB/oct; field set blocks (no pre-sleep)
I_TRIP = 1e-9                         # 2 consecutive points over trip (flyback transient peaks ~200 pA, run 5)

ns = np.linspace(N_LO, N_HI, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, 0.0, **CAL)
B_vec = field_invB(B_LO, B_HI, N_B)

# --- design asserts: validators, session caps, both-axis Nyquist ---
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
_vr = lambda v: (float(v._min_value), float(v._max_value))
assert _vr(k_2400_tg.volt.vals) == (TG_MIN, TG_MAX) and _vr(k_2400_bg.volt.vals) == (BG_MIN, BG_MAX), "gate validators moved"
assert _vr(magnet.field.vals) == (-B_SESSION_CAP, B_SESSION_CAP), "field cap moved"
_FL = lambda n12: abs(n12) * 1e16 * cst.h / (4 * cst.e)          # Luttinger frequency, T
_dinvB = float(np.diff(1 / B_vec)[0])
_dn_ray = 4 * (cst.e / cst.h) * B_LO / 1e16                      # LL ray spacing in n at B_LO, 1e12 cm^-2
_dn = (N_HI - N_LO) / (N_N - 1)
assert _dinvB <= 1 / (2 * _FL(N_HI)), f"B-axis Nyquist: d(1/B)={_dinvB:.5f} > {1/(2*_FL(N_HI)):.5f}"
assert _dn <= _dn_ray / 2, f"n-axis ray Nyquist at {B_LO} T: dn={_dn:.4f} > {_dn_ray/2:.4f}"
print(f"F_L({N_HI:.2f}e12) = {_FL(N_HI):.2f} T; d(1/B) = {_dinvB:.5f} 1/T = {1/(_dinvB*_FL(N_HI)):.2f} samples/period at F_L")
print(f"n-axis: dn = {_dn:.4f}e12 vs ray/2 = {_dn_ray/2:.4f}e12 at B_LO; "
      f"resolution dF = {1/(1/B_LO - 1/B_HI):.2f} T; ABAB partner at n_lo = 3.55 T -> {(1/B_LO-1/B_HI)*3.55:.1f} periods")
print(f"n-line: {ns[0]:.2f} -> {ns[-1]:.2f}e12, Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f} V "
      f"(TG margin {TG_MAX - Vtgs.max():.4f} V)")
print(f"B grid: {N_B} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, dB {np.diff(B_vec)[0]*1e3:.1f} -> {np.diff(B_vec)[-1]*1e3:.0f} mT, "
      f"{(B_vec < 2).sum()} rows below 2 T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
_floor = (7.0 if _slope >= 24 else 5.0) * _tau
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05 -> ramp up to B_LO), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, settle_s {magnet.settle_s} s")
print(f"lock-in: tau {_tau} s, filter_slope {_slope} dB/oct -> settling floor {_floor:.2f} s vs fast_delay {FAST_DELAY} s")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert FAST_DELAY >= _floor - 1e-9, f"fast_delay {FAST_DELAY} s under the {_floor:.2f} s settling floor"

# Fixed sensitivity for the whole fan, inherited from the run 6/7 spot checks: 50 uV = 5 kOhm FS at 10 nA.
# Worst corner is low-n x high-B: R(n=2.0e12, B=0) = 72 Ohm (run 5) x MR 6.5 (run 6, measured) ~ 470 Ohm = 9% FS;
# even at MR 20 it is 38% FS. Headroom over precision -- clipping is the unrecoverable failure (landau-fan step 1).
sr1.sensitivity(50e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (5 kOhm FS); sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti: D = 0, n {N_LO}..{N_HI}e12 ({N_N} cols), B {B_LO}..{B_HI} T uniform 1/B ({N_B} rows), "
                  f"fast_delay {FAST_DELAY} s, sr1 50 uV, run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0.00 V/nm, n = {N_LO:.2f} to {N_HI:.2f}e12 cm^-2 ({N_N} cols, dn {_dn:.4f}e12); '
              f'B = {B_LO} to {B_HI} T uniform in 1/B ({N_B} rows, d(1/B) {_dinvB:.5f} 1/T); '
              f'electron side (run 6 onset 0.30 T censored vs run 7 hole 0.71 T); '
              f'fast_delay {FAST_DELAY} s = 7 tau, slow_delay {SLOW_DELAY} s, sr1 50 uV; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'per-column SdH FFT for tetralayer-stacking-fs-count Step 4/5')

# position: gates to the n-line start, then the magnet to B_LO (blocking ramp ~4.7 min)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
magnet.field(B_LO)
print(f"positioned: B = {magnet.field():+.4f} T (target {B_LO}), (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', T_sample); s.plot('time', sr1.P); s.plot('time', sr0.P)

_strikes = [0]
def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        _strikes[0] += 1
        print(f"LEAK over-trip #{_strikes[0]} at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        if _strikes[0] >= 2:
            print("LEAK TRIP: two consecutive points over 1 nA -- stopping")
            station.interrupt_requested = True
    else:
        _strikes[0] = 0
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # park the gates; leave the field at 10 T for the LK mass series (Verify: LK mass split), which rides it back down
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
          f"T_sample = {T_sample():.3f} K")
