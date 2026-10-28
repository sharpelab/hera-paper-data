# === Landau fan (`landau-fan-vti`): D = 0 electron n-line +1.00 -> +3.20e12, B 1.0 -> 6.0 T slow ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_LO, N_HI, N_N = 1.00, 3.20, 51          # 1e12 cm^-2
B_LO, B_HI, DB = 1.0, 6.0, 0.010          # T (uniform in B: blocking rate-limited magnet)
D0 = 0.0
FAST_DELAY, SLOW_DELAY = 1.0, 1.0         # 10 tau at tau = 0.1 s, 24 dB/oct
TAU = 0.1

# --- fast axis: paired (Vtg, Vbg) n-line at D = 0 ---
ns = np.linspace(N_LO, N_HI, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
_nr, _Dr = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_Dr).max() < 1e-9 and np.abs(_nr - ns).max() < 1e-9, "n-line is not at D = 0"

# --- slow axis: uniform in B, dB = d(1/B) * B_lo^2 (Nyquist held at the low-B edge) ---
B_vec = np.round(np.arange(B_LO, B_HI + DB / 2, DB), 4)
assert B_vec.max() <= B_SESSION_CAP and len(B_vec) == 501, (B_vec.max(), len(B_vec))
_dinvB = 1 / B_vec[0] - 1 / B_vec[1]
_F_L = N_HI * 1e16 * 6.62607015e-34 / (4 * 1.602176634e-19)
print(f"grid: {len(B_vec)} B rows x {N_N} n cols = {len(B_vec)*N_N} pts; dn = {ns[1]-ns[0]:.4f}e12 "
      f"({4*1.602176634e-19*B_vec[0]/6.62607015e-34/1e16/(ns[1]-ns[0]):.2f} pts per LL ray at {B_LO} T)")
print(f"d(1/B) = {_dinvB:.5f} /T -> F_Nyq = {0.5/_dinvB:.1f} T > F_L(n_max) = {_F_L:.1f} T; "
      f"dF = {1/(1/B_vec[0]-1/B_vec[-1]):.2f} T; Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: magnet parked at 0), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- lock-ins: fixed for the whole fan. tau 0.3 -> 0.1 s so fast_delay = 1.0 s is a full 10 tau at 24 dB/oct. ---
print(f"lock-ins before: sr0 tau {sr0.time_constant()} s / {sr0.filter_slope()} dB, "
      f"sr1 tau {sr1.time_constant()} s / {sr1.filter_slope()} dB, sr1 sens {sr1.sensitivity()} V")
sr0.time_constant(TAU); sr1.time_constant(TAU)
sr1.sensitivity(50e-6)
assert sr0.time_constant() == TAU and sr1.time_constant() == TAU
print(f"lock-ins after:  tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct -> fast_delay "
      f"{FAST_DELAY} s = {FAST_DELAY/TAU:.0f} tau; sr1 sens {sr1.sensitivity()} V "
      f"({sr1.sensitivity()/(sr1.amplitude()/1e8):.0f} Ohm FS); drive {sr1.amplitude()} V -> {sr1.amplitude()/1e8*1e9:.1f} nA")

# --- position the magnet at the fan's start (FastBi1K5 set blocks through the ramp; ~7.3 min from 0 T) ---
magnet.field(B_LO)
print(f"positioned: B = {magnet.field():+.4f} T (target {B_LO})")
assert abs(magnet.field() - B_LO) < 0.02

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron D = 0: n {N_LO:+.2f} -> {N_HI:+.2f}e12 ({N_N} cols), "
                  f"B {B_LO} -> {B_HI} T ({len(B_vec)} rows, {DB*1e3:.0f} mT), tau {TAU} s, fast_delay {FAST_DELAY} s, sr1 50 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0} V/nm, n = {N_LO:+.2f} to {N_HI:+.2f}e12 cm^-2 ({N_N} pts, dn = {ns[1]-ns[0]:.4f}e12), '
              f'B = {B_LO} to {B_HI} T ({len(B_vec)} rows, dB = {DB*1e3:.0f} mT, d(1/B) = {_dinvB:.5f}/T, '
              f'F_Nyq = {0.5/_dinvB:.0f} T, dF = {1/(1/B_vec[0]-1/B_vec[-1]):.2f} T); electron side per sdh-spot-check run 6; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'sr1 50 uV, tau {TAU} s / 24 dB, fast_delay {FAST_DELAY} s = 10 tau')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

# Leak guard: trip on two CONSECUTIVE points over 1 nA. A single-point excursion at a row start is the
# gate-flyback charging transient (+-200 pA seen on run 5), not a sustained leak (session_notes TOOLING).
I_TRIP = 1e-9
_leak = {"n": 0}
def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        _leak["n"] += 1
        print(f"leak excursion #{_leak['n']} at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        if _leak["n"] >= 2:
            print("LEAK TRIP (two consecutive points over 1 nA) — interrupting")
            station.interrupt_requested = True
    else:
        _leak["n"] = 0
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# endpoint by design: B = 6 T, gates at n = +3.20e12 — where the LK mass series wants them. No park, no re-traverse.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
      f"T_sample = {T_sample():.3f} K")
