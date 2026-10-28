# === Landau fan, electron side, D = 0 (`landau-fan-vti`): B slow 1 -> 10 T uniform in 1/B (101 rows), n fast 1.6 -> 3.27e12 (61 pts) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run-5 calibration (ana)
D0 = 0.0
ns = np.linspace(3.25, 1.60, 61)           # high n first on each row (fast axis retraces every row anyway)
Vtgs, Vbgs = calc_gate_voltages(ns, D0 * np.ones_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
ok = (Vtgs >= TG_MIN) & (Vtgs <= TG_MAX) & (Vbgs >= BG_MIN) & (Vbgs <= BG_MAX)
assert ok.all(), f"{(~ok).sum()} n-points outside the validators — clip by dropping, not clamping"
B_LO, B_HI, N_B = 1.0, 10.0, 101
B_vec = field_invB(B_LO, B_HI, N_B)        # uniform in 1/B, ascending
assert B_vec.max() <= B_SESSION_CAP
dinvB = 1 / B_LO - 1 / B_vec[1]
print(f"fast axis: n = {ns[0]:.2f} -> {ns[-1]:.2f}e12 ({len(ns)} pts, dn = {abs(ns[1]-ns[0]):.3f}e12), Vtg {Vtgs.min():+.3f}..{Vtgs.max():+.3f}, Vbg {Vbgs.min():+.3f}..{Vbgs.max():+.3f}")
print(f"slow axis: B = {B_LO} -> {B_HI} T, {N_B} rows uniform in 1/B, d(1/B) = {dinvB:.4f} 1/T (Nyquist on F_L(3.27e12) = 33.8 T needs <= {1/(2*33.8):.4f}; 1/3: {1/(3*33.8):.4f})")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (expect <= {B_LO}: the ride-down ended at 0.3 T), V_si = {k_si():+.3f} V (0)")
assert 1.0 <= _T0 <= 1.5 and _B0 < B_LO + 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

I_TRIP = 1e-9
sr1.sensitivity(100e-6)    # 10 kOhm FS: worst corner n = 1.6e12 x 10 T (QH regime, nu ~ 6-8; run 6 reached 530 Ohm at 3.2e12)
FAST_DELAY, SLOW_DELAY = 1.2, 3.0   # 4 tau at tau = 0.3 s; per-column FFT is along B (slow), so the fast-axis lag only shifts n uniformly
print(f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s, fast_delay {FAST_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = f"landau-fan-vti electron D = 0: n {ns[-1]:.2f}..{ns[0]:.2f}e12 ({len(ns)} pts fast), B {B_LO}->{B_HI} T uniform-1/B {N_B} rows, run-5 cal, sr1 100 uV"
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {ns[-1]:.2f} to {ns[0]:.2f} e12 cm^-2 ({len(ns)} pts), B = {B_LO} to {B_HI} T ({N_B} rows uniform in 1/B); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; spot checks runs 6 (e) / 7 (h)')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
magnet.field(B_LO)                          # blocking ramp to the fan start (the set call is the settle)
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY, init_delay=False)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
print(f"done: B = {magnet.field():+.3f} T (left at the fan top for the LK ladder), gates parked at 0")
