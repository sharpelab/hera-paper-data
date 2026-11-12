# === Landau fan, electron side (`landau-fan-vti`): D = 0, n = +3.25 -> +1.00e12 paired n-line, B 0.7 -> 8 T uniform in 1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- design (landau-fan step 1, numbers in the markdown) ---
F_MAX = 34.0                  # T — fastest tone to Nyquist: F_L(n = 3.25 nominal) = 33.6 T; region-B (+0.43e12) sum tone <= 34 T
B_LO, B_HI = 0.7, 8.0         # T — B_lo = this device's measured onset floor (run 7: 0.71 T; run 6 light tone censored at its 1.0 T record edge)
N_B = int(np.ceil((1 / B_LO - 1 / B_HI) * 3 * F_MAX)) + 1          # 3 rows per period of F_MAX, uniform in 1/B
B_vec = field_invB(B_LO, B_HI, N_B)                                 # ascending: starts where the magnet sits (0 T), ends at 8 T
n_hi, n_lo, D0 = 3.25, 1.00, 0.0                                    # 1e12 cm^-2, V/nm — electron side of the D = 0 line (validator-limited at +3.27)
dn_ray = 4 * 2.418e10 * B_LO / 1e12                                 # g e B / h at B_lo, 1e12 cm^-2 — ray spacing for a single 4-fold pocket
N_n = int(np.ceil((n_hi - n_lo) / (dn_ray / 2))) + 1                # >= 2 columns per ray spacing at B_lo
ns = np.linspace(n_hi, n_lo, N_n); Ds = np.full_like(ns, D0)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
_ok_tg, _ok_bg = sanitize_tg_bg(Vtgs, Vbgs, tg_lims, bg_lims)
assert len(_ok_tg) == N_n, f"paired n-line leaves the validators: {N_n - len(_ok_tg)} pts dropped"
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
FAST_DELAY, SLOW_DELAY = 1.2, 3.0   # 4 tau at tau = 0.3 s on the paired gate step; 3 s retrace settle before each row's first point
print(f"grid: {N_B} B rows {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T (d(1/B) = {1/B_vec[0]-1/B_vec[1]:.4f} 1/T, first step {B_vec[1]-B_vec[0]*1:.4f} T, last {B_vec[-1]-B_vec[-2]:.3f} T) "
      f"x {N_n} n pts {n_hi:+.2f} -> {n_lo:+.2f}e12 (dn = {(n_hi-n_lo)/(N_n-1):.4f}e12, {dn_ray/((n_hi-n_lo)/(N_n-1)):.2f} per ray at B_lo); "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V; roundtrip ends n,D = "
      f"{np.round(calc_nD(Vtgs[0], Vbgs[0], **CAL), 3)}, {np.round(calc_nD(Vtgs[-1], Vbgs[-1], **CAL), 3)}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (handoff state: 0), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0), "
      f"sr1 tau {_tau} s / slope {_slope} dB (0.3 / 24 inherited from runs 6-7), drive {sr1.amplitude()} V -> 10 nA")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(_tau - 0.3) < 1e-6, f"sr1 tau = {_tau} s, not the 0.3 s the 1.2 s (4 tau) dwell was priced for — stop and re-price"

# Fixed sensitivity for the whole fan (inherited from runs 6-7): 50 uV = 5 kOhm FS at 10 nA. Worst corner n = 1.0e12 x 8 T (nu ~ 5.2):
# run 7 read 587 Ohm at |n| = 1.2e12, 10 T (nu ~ 5) -> ~8.5x headroom; low-B R ~ 10-50 Ohm gave SNR 40-100 tones at this range in run 6.
sr1.sensitivity(50e-6)
I_TRIP = 1e-9
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS); sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s = {FAST_DELAY/_tau:.1f} tau, slow_delay {SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = {D0:+.2f} V/nm, n = {n_hi:+.2f} -> {n_lo:+.2f}e12 ({N_n} pts), "
                  f"B {B_LO} -> {B_HI} T uniform-1/B ({N_B} rows, 3/period at {F_MAX} T), sr1 50 uV, fast_delay {FAST_DELAY}, slow_delay {SLOW_DELAY}; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side: D = {D0:+.2f} V/nm, n = {n_hi:+.2f} to {n_lo:+.2f}e12 cm^-2 ({N_n} pts, paired k_tg/k_bg line), '
              f'B = {B_LO} to {B_HI} T uniform-1/B ({N_B} rows, d(1/B) = {1/(3*F_MAX):.4f} 1/T); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'design from spot checks runs 6 (e, +3.2e12) and 7 (h, -1.2e12)')
# pre-position the gates at the first column so they settle during the 0 -> 0.7 T ramp
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, magnet_field, k_tg_volt, k_bg_volt, T_sample, k_tg_curr, k_bg_curr, sr0_X, sr0_P, sr1_X, sr1_P]
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

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)

# park the gates; the field stays at 8 T deliberately (the next field measurement rides it down — never re-traverse)
s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
print(f"done: B = {magnet.field():+.3f} T (left at B_HI), (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
