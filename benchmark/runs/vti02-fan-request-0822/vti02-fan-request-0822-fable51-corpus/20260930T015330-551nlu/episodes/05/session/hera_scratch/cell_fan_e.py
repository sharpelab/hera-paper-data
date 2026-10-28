# === Landau fan, electron side (`landau-fan-vti`): D = 0, n = +1.4 -> +3.2e12 (81 pts, fast) x B 0.6 -> 10 T uniform-1/B (160 rows, slow) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- design (investigation Step 4; numbers from the spot-check read of run 6 + the model F(n) table) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run-5 cnp-and-dline-calibration (ana)
N_LO, N_HI, N_N = 1.4, 3.2, 81          # 1e12 cm^-2 at D = 0; dn = 0.0225e12 -> 2.6 pts per LL ray period at 0.6 T (>= 2 floor), 3+ above 0.7 T
B_LO, B_HI, N_B = 0.6, 10.0, 160        # T; uniform in 1/B: d(1/B) = 0.00985 /T -> Nyquist 50.7 T = 1.5 x F_L(3.2e12) (1/3 rule at n_max)
FAST_DELAY, SLOW_DELAY = 1.2, 1.0       # 4 tau at tau = 0.3 s (24 dB/oct); slow_delay sits on top of the driver's 3 s magnet settle
SENS = 100e-6                            # 10 kOhm FS at 10 nA: sized for the low-n x high-B corner (spot-check maxima 530-590 Ohm at 5 kOhm FS never exceeded 12 % FS)
I_TRIP = 1e-9

ns = np.linspace(N_LO, N_HI, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
B_vec = field_invB(B_LO, B_HI, N_B)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
_dinv = float(np.abs(np.diff(1 / B_vec)).mean())
print(f"fast n-line: n {N_LO:+.2f} -> {N_HI:+.2f}e12 ({N_N} pts, dn {ns[1]-ns[0]:.4f}e12); Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V; "
      f"roundtrip (n, D) at the ends: {calc_nD(Vtgs[0], Vbgs[0], **CAL)} / {calc_nD(Vtgs[-1], Vbgs[-1], **CAL)}")
print(f"slow B: {N_B} rows {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T uniform-1/B, d(1/B) = {_dinv:.5f} /T (Nyquist {1/(2*_dinv):.1f} T), dB {B_vec[1]-B_vec[0]:.4f} .. {B_vec[-1]-B_vec[-2]:.3f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: fan starts at 0.6 T), V_si = {k_si():+.3f} V (0), "
      f"gates (Vtg, Vbg) = ({k_tg.volt():+.3f}, {k_bg.volt():+.3f}) V (0, 0 after the handoff), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
sr1.sensitivity(SENS)
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f"sr1 sens {sr1.sensitivity()} V ({SENS/10e-9/1e3:.0f} kOhm FS), tau {_tau} s / {_slope} dB/oct -> fast_delay {FAST_DELAY} s = {FAST_DELAY/_tau:.1f} tau; "
      f"sr0 sens {sr0.sensitivity()} V; drive {sr1.amplitude()} V @ {sr1.frequency()} Hz; magnet settle_s {magnet.settle_s} s")
assert abs(_tau - 0.3) < 1e-6, f"sr1 tau = {_tau} s, fan priced at 4 tau of 0.3 s — stop and re-price"

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron: D = 0, n = {N_LO:+.2f} -> {N_HI:+.2f}e12 ({N_N} pts) fast, B {B_LO} -> {B_HI} T uniform-1/B ({N_B} rows) slow; "
                  f"fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; sr1 100 uV; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0.00 V/nm, n = {N_LO:+.2f} to {N_HI:+.2f} e12 cm^-2 ({N_N} pts, electron side, fast), B = {B_LO} to {B_HI} T ({N_B} rows, uniform 1/B, d(1/B) = {_dinv:.5f} /T, slow); '
              f'fast_delay {FAST_DELAY} s (4 tau), slow_delay {SLOW_DELAY} s; sr1 sens {SENS} V; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'follows sdh-spot-check run 6 (its n = +3.2e12 point is this fan\'s last column)')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B (slow), Vtg, Vbg (fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

_clip_rows = set()
def fan_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    _b = round(float(data[1]), 3)
    if abs(float(data[9])) >= 0.9 * SENS and _b not in _clip_rows:      # soft-clip watch: flag once per row, do not abort
        _clip_rows.add(_b)
        print(f"CLIP WATCH: |sr1.X| = {abs(float(data[9]))*1e6:.1f} uV >= 90 % FS at B={_b:+.3f} T, Vtg={float(data[2]):+.4f} V")
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# gates stay at the line's high-n end, field at 10 T — the next step rides the magnet down; no park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K, clip-flagged rows: {len(_clip_rows)}")
