# === Landau fan (`landau-fan-vti`), electron side, D = 0: n = +1.5 -> +3.25e12 (fast, paired TG/BG line), B = B_LO -> 10 T uniform in 1/B (slow) ===
# Investigation Step 4 (tetralayer-stacking-fs-count): per-column SdH FFT -> peak set vs F_L(n), Luttinger partition, n-dependence
# of every tone (harmonics track k*f exactly; a real pocket follows its own Onsager curve). Design numbers from the spot checks (runs 6/8).
from hera.analysis import field_invB, luttinger_frequency
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run-5 calibration (ana); scale = geometry prior
n_hi, n_lo, N_n = 3.25, 1.5, 81           # 1e12 cm^-2; dn = 0.0219e12 -> 3.1 pts per LL ray (dn_ray = 0.0967e12/T * B_LO) at B_LO = 0.7 T
D0 = 0.0
B_LO, B_HI = 0.7, 10.0                    # B_LO: run-8 onset read (see markdown); B_HI = session cap
ns = np.linspace(n_hi, n_lo, N_n); Ds = D0 * np.ones(N_n)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.all((Vtgs >= TG_MIN) & (Vtgs <= TG_MAX) & (Vbgs >= BG_MIN) & (Vbgs <= BG_MAX)), (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
n_chk, D_chk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(n_chk, ns) and np.allclose(D_chk, D0, atol=1e-6)
print(f"fast axis: n {n_hi:+.2f} -> {n_lo:+.2f}e12 ({N_n} pts, dn {abs(ns[1]-ns[0]):.4f}e12) at D = {D0:+.2f}; "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")

# slow axis: uniform in 1/B, Nyquist on F_L(n_hi) with margin 3 (spec of the design: Delta(1/B) <= 1/(3 F_L))
F_L_max = luttinger_frequency(n_hi * 1e16)
dinvB = 1.0 / (3.0 * F_L_max)
N_B = int(np.ceil((1 / B_LO - 1 / B_HI) / dinvB)) + 1
B_vec = field_invB(B_LO, B_HI, N_B)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
print(f"slow axis: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows uniform in 1/B (dInvB {dinvB:.5f}/T, Nyquist {1/(2*dinvB):.1f} T vs F_L(n_hi) {F_L_max:.1f} T); "
      f"dB {B_vec[1]-B_vec[0]:.4f} T at the bottom, {B_vec[-1]-B_vec[-2]:.3f} T at the top")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (run 8 ended at ~1.05 T; the ramp to B_LO is in-cell), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(k_si()) < 0.01 and abs(_B0) < 1.5
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- lock-in: fixed for the whole fan. 100 uV = 10 kOhm FS at 10 nA: worst corner (n = 1.5, 10 T) anchored on run 7's 587 Ohm at |n| = 1.2 -> ~x10 headroom;
#     low-B signal (~15 Ohm, oscillation +-10 Ohm) sits at 0.1-0.2 % FS, which the spot checks showed is not digitization-limited (SNR ~100 at 0.3 % FS).
sr1.sensitivity(100e-6)
tau, slope = sr1.time_constant(), sr1.filter_slope()
FAST_DELAY, SLOW_DELAY = 1.8, 1.0        # 6 tau at tau = 0.3 s (base recipe step 7: per-column-FFT fan); B is the slow axis, its dwell is the driver's 3 s settle
assert abs(tau - 0.3) < 1e-6 and slope == 24, (tau, slope)
print(f"sr1 sens {sr1.sensitivity()} V (FS {sr1.sensitivity()/10e-9:.0f} Ohm at 10 nA), tau {tau} s, {slope} dB/oct; fast_delay {FAST_DELAY} s = {FAST_DELAY/tau:.0f} tau; "
      f"priced: {N_B} x {N_n} x ~2.05 s + 9.3 T bare traverse (68 min) + row turnaround ~5 s -> ~7.5 h")

I_TRIP = 1e-9
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side D = {D0:+.2f}: n {n_hi:+.2f} -> {n_lo:+.2f}e12 ({N_n} pts) fast paired TG/BG (run-5 cal), "
                  f"B {B_LO} -> {B_HI} T uniform-1/B ({N_B} rows, dInvB {dinvB:.5f}/T) slow, sr1 100 uV, fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {n_lo:+.2f} to {n_hi:+.2f}e12 cm^-2 ({N_n} pts, electron side), B = {B_LO} to {B_HI} T ({N_B} rows uniform in 1/B); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; onset from run 8; sr1 100 uV, tau 0.3 s')

# position: gates to the first fast point, magnet to B_LO (blocking ramp; ~2.5 min from 1.05 T)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
magnet.field(B_LO)
interruptible_sleep(10)
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# end state: field at 10 T (the LK / temperature-dependence step and the ride-home both start from here); gates parked at 0.
k_tg.volt(0.0); k_bg.volt(0.0)
print(f"done: B = {magnet.field():+.3f} T, gates ({k_tg.volt():+.3f}, {k_bg.volt():+.3f}) V, T_sample = {T_sample():.3f} K")
