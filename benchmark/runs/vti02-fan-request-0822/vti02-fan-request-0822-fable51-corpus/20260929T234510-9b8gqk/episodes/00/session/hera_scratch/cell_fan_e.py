# === Landau fan, electron side (`landau-fan-vti`): D = 0, n = +1.0 -> +3.2e12 paired n-line (fast, 67 pts) x B 0.75 -> 10 T uniform in 1/B (slow, 166 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = 9.5 nm geometry prior) — same CAL as runs 6/7 ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0                                          # V/nm
n_lo, n_hi, N_n = 1.0, 3.2, 67                    # 1e12 cm^-2; n_hi = run-6 spot density (shared-density column); 3.27 is the TG limit
ns = np.linspace(n_lo, n_hi, N_n)                 # ascending each row: low n -> high n
Vtgs, Vbgs = calc_gate_voltages(ns, np.full(N_n, D0), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
_tg_ok, _bg_ok = sanitize_tg_bg(Vtgs, Vbgs, tg_lims, bg_lims)
assert len(_tg_ok) == N_n, f"n-line leaves the validators: {N_n - len(_tg_ok)} pts outside"
_n_chk, _D_chk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"n-line: n = {n_lo:+.2f} .. {n_hi:+.2f}e12 ({N_n} pts, dn = {ns[1]-ns[0]:.4f}e12) at D = {D0:+.2f} V/nm -> "
      f"Vtg {Vtgs.min():+.4f} .. {Vtgs.max():+.4f} V, Vbg {Vbgs.min():+.4f} .. {Vbgs.max():+.4f} V; roundtrip |D| max {np.abs(np.asarray(_D_chk)).max():.1e}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), T_vaporizer = {T_vaporizer():.3f} K, B = {_B0:+.4f} T (|B|<0.05: fan ascends from 0.75 T), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"

# --- slow field axis: uniform in 1/B (per-column SdH FFT), d(1/B) = 0.0075 /T -> Nyquist 67 T (>= 2x the 60 T 2nd harmonic seen in run 6)
B_lo, B_hi, N_B = 0.75, 10.0, 166
B_vec = 1.0 / np.linspace(1.0 / B_lo, 1.0 / B_hi, N_B)
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
FAST_DELAY, SLOW_DELAY = 1.2, 3.0                 # 4 tau at tau = 0.3 s / 24 dB (per-column FFT runs along B: the n-lag is a uniform column shift); 10 tau after each row flyback
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA. Worst corner is low n x high B (n = 1.0, 10 T, nu ~ 4):
# anchors R(0) = 117 Ohm (run 5) x MR/QH factor; run 7 (|n| = 1.2, nu ~ 5 at 10 T) peaked at 587 Ohm -> 10 kOhm is > 10x headroom.
# Digitization at 100 uV: 0.37 Ohm/LSB (run 5 measured step) vs >= 5 Ohm SdH amplitude at 1 T (run 6) — resolved.
sr1.sensitivity(100e-6)
print(f"B grid: {N_B} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.2f} T, d(1/B) = {abs(np.diff(1/B_vec)).mean():.5f} /T (first dB {B_vec[1]-B_vec[0]:.4f}, last dB {B_vec[-1]-B_vec[-2]:.3f} T); "
      f"sr1 sens {sr1.sensitivity()} V, sr0 sens {sr0.sensitivity()} V, tau {sr1.time_constant()} s / {sr1.filter_slope()} dB, settle_s {magnet.settle_s} s; "
      f"{N_B * N_n} pts, fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = {D0:+.2f} V/nm, n = {n_lo:+.2f} .. {n_hi:+.2f}e12 ({N_n} pts) fast, "
                  f"B {B_lo} -> {B_hi} T uniform 1/B ({N_B} rows) slow; run-5 cal; sr1 100 uV; fast_delay {FAST_DELAY}, slow_delay {SLOW_DELAY}")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {n_lo:+.2f} to {n_hi:+.2f}e12 cm^-2 ({N_n} pts, electron side, paired (Vtg, Vbg) line), '
              f'B = {B_lo} to {B_hi} T uniform in 1/B ({N_B} rows, d(1/B) = 0.0075 /T); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'sr1 100 uV (10 kOhm FS); fast_delay {FAST_DELAY} s (4 tau), slow_delay {SLOW_DELAY} s; Vsi = 0')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

# field slow (one monotonic 0.75 -> 10 T traverse), paired n-line fast; init_delay applies slow_delay after the first field set.
s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# ends at 10 T with the gates at the last n-point (n = +3.2); no park — the next step (LK mass split / ride-down) starts where the magnet sits.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
