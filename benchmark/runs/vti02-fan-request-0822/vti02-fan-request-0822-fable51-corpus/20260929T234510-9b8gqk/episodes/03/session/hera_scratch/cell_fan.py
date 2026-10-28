# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +1.0 -> +3.24e12 (48 pts) fast; B 0.3 -> 10 T two-segment uniform-1/B (159 rows) slow ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_N, N_LO, N_HI, D0 = 48, 1.0, 3.24, 0.0            # 1e12 cm^-2, V/nm; n_max = TG limit (Vtg 0.995 V)
ns = np.linspace(N_LO, N_HI, N_N); Ds = D0 * np.ones_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
print(f"n-line: n = {N_LO:+.2f} -> {N_HI:+.2f}e12 ({N_N} pts, dn {ns[1]-ns[0]:.4f}e12) at D = {D0:+.2f}; "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V; "
      f"roundtrip end n,D = {calc_nD(Vtgs[-1], Vbgs[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0.3 T from rest), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- slow field axis: two-segment uniform-1/B, ascending (magnet at rest at 0 T; ends at 10 T for the next step)
F_MAX = 4.135667e-15 / 4 * N_HI * 1e16                       # F_L at n_max = 33.5 T
def _seg(b0, b1, dinv):
    return field_invB(b0, b1, int(np.ceil(abs(1 / b0 - 1 / b1) / dinv)) + 1)
B_vec = np.unique(np.round(np.hstack((_seg(0.3, 1.2, 0.030), _seg(1.2, 10.0, 1 / (3 * F_MAX)))), 4))
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0 and np.all(np.diff(B_vec) > 0)
FAST_DELAY, SLOW_DELAY = 2.0, 1.0      # 6.7 tau at tau = 0.3 s / 24 dB (90 % settled); magnet set already blocks + 3 s settle
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange mid-fan): 100 uV = 10 kOhm FS at 10 nA; worst corner n = 1.0 x 10 T.
sr1.sensitivity(100e-6)
print(f"B grid: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T (d(1/B) 0.030 to 1.2 T, {1/(3*F_MAX):.4f} above); "
      f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V; drive {sr1.amplitude()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron: D = {D0:+.2f} V/nm, n = {N_LO:+.2f} to {N_HI:+.2f}e12 ({N_N} pts) fast, B {B_vec[0]} to {B_vec[-1]} T "
                  f"two-segment uniform-1/B ({len(B_vec)} rows) slow; run-5 cal; sr1 100 uV; fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {N_LO:+.2f} to {N_HI:+.2f}e12 cm^-2 ({N_N} pts, paired TG/BG n-line), B = {B_vec[0]} to {B_vec[-1]} T '
              f'({len(B_vec)} rows: d(1/B) = 0.030 /T for 0.3-1.2 T, {1/(3*F_MAX):.4f} /T for 1.2-10 T); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; sr1 100 uV')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg (fast pair), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# gates stay at the last n-line point; field stays at 10 T (next step rides it) — no park here.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
