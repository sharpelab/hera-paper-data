# === Landau fan (`landau-fan-vti`), Step 4 of tetralayer-stacking-fs-count ===
# D = 0 electron n-line 0.8 -> 3.2e12 cm^-2 (61 pts, fast) x B 1 -> 10 T uniform in 1/B (122 rows, slow).
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run 5 (cnp-and-dline-calibration)
D_FAN = 0.0                       # V/nm
N_LO, N_HI, N_N = 0.8, 3.2, 61    # 1e12 cm^-2
B_LO, B_MAX, N_B = 1.0, 10.0, 122 # T
FAST_DELAY, SLOW_DELAY = 1.8, 3.0 # 6 tau at tau = 0.3 s / 24 dB (per-column-FFT fan, base step 7)
SENS = 100e-6                     # V -> 10.1 kOhm full scale at 10 nA (low-n x high-B corner)
I_TRIP = 1e-9

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS {magnet.persistent_switch_on()}, out {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24, (sr1.time_constant(), sr1.filter_slope())

# --- axes ---
ns = np.linspace(N_LO, N_HI, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
B_vec = field_invB(B_LO, B_MAX, N_B)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP

# --- design checks on the page (landau-fan step 1: both-axis Nyquist + record resolution) ---
FL_hi = cst.h * (N_HI * 1e16) / (4 * cst.e)              # Luttinger frequency at n_max, T
d_inv = float(np.abs(np.diff(1 / B_vec)).max())
dn_ray = 4 * cst.e / cst.h * B_LO * 1e-16                 # 1e12 cm^-2 per LL ray at B_lo
step_n = (N_HI - N_LO) / (N_N - 1)
dF = 1 / (1 / B_LO - 1 / B_MAX)
print(f"B-axis   : max d(1/B) = {d_inv:.5f} 1/T -> f_Nyq = {1/(2*d_inv):.1f} T = {1/(2*d_inv)/FL_hi:.2f} F_L "
      f"(F_L(n_max) = {FL_hi:.2f} T); {N_B} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T")
print(f"n-axis   : ray {dn_ray:.4f}e12 at {B_LO} T / step {step_n:.4f}e12 = {dn_ray/step_n:.2f} pts/ray (floor 2)")
print(f"record   : dF = {dF:.2f} T, 2dF = {2*dF:.2f} T vs tones to split at n_max 25.8 / 29.2 / 33.1 T (min gap 3.4 T)")
print(f"gates    : V_tg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f} V, V_bg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V; "
      f"roundtrip ends {calc_nD(Vtgs[0], Vbgs[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])} "
      f"{calc_nD(Vtgs[-1], Vbgs[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- fixed sensitivity for the whole fan (no autorange mid-row) ---
sr1.sensitivity(SENS)
assert sr0.sensitivity() == 0.02
print(f"lock-ins : sr1 sens {sr1.sensitivity()} V = {sr1.sensitivity()/1e-8:.0f} Ohm FS at 10 nA; sr0 sens {sr0.sensitivity()} V; "
      f"tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; fast_delay {FAST_DELAY} s = {FAST_DELAY/sr1.time_constant():.0f} tau")

# --- position the magnet at the fan start (FastBi1K5 set blocks through the ramp; no pre-settle sleep) ---
print(f"positioning magnet {_B0:+.4f} -> {B_vec[0]:.3f} T, blocking ~{abs(B_vec[0]-_B0)/0.137:.0f} min ...")
magnet.field(float(B_vec[0]))
print(f"magnet at {magnet.field():+.4f} T")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan electron: D = {D_FAN} V/nm, n = {N_LO} to {N_HI} e12 cm^-2 ({N_N} pts), "
                  f"B = {B_LO} to {B_MAX} T ({N_B} rows, uniform 1/B), run-5 cal, sr1 100 uV, fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D_FAN} V/nm, n = {N_LO} to {N_HI} e12 cm^-2 ({N_N} pts, step {step_n:.4f}e12), '
              f'B = {B_LO} to {B_MAX} T ({N_B} rows, uniform 1/B, max d(1/B) {d_inv:.5f} -> f_Nyq {1/(2*d_inv):.1f} T); '
              f'fast_delay {FAST_DELAY} s = 6 tau (tau 0.3 s / 24 dB), sr1 sens {SENS} V; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'step 4 of tetralayer-stacking-fs-count; onset from spot check run 6 censored at 1.0 T')

s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

IDX_B, IDX_ITG, IDX_IBG, IDX_SR1X = 1, 5, 6, 9
_warned = {"cols": False, "clip": False}

def fan_guard(station, data):
    if len(data) != 11:
        if not _warned["cols"]:
            print(f"GUARD: unexpected row width {len(data)} (expected 11) - leak/clip guard indices unverified")
            _warned["cols"] = True
        return
    i_tg, i_bg = abs(float(data[IDX_ITG])), abs(float(data[IDX_IBG]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[IDX_B]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[IDX_SR1X])) > 0.95 * SENS and not _warned["clip"]:
        print(f"CLIP WARNING at B={float(data[IDX_B]):+.3f} T: |sr1.X|={abs(float(data[IDX_SR1X])):.3e} V "
              f"> 95% of {SENS} V full scale - low-n/high-B corner is railing")
        _warned["clip"] = True
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)

# End state is deliberate: B = 10 T, gates at n = +3.2e12 (D = 0) - where the Verify LK mass
# split starts. No park here (rig card: never re-traverse the magnet).
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) -> "
      f"n, D = {calc_nD(k_tg.volt(), k_bg.volt(), CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}, "
      f"T_sample = {T_sample():.3f} K")
