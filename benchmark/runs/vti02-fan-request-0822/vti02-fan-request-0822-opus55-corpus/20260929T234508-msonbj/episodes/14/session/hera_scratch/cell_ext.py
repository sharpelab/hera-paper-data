# === Low-field onset pin (`sdh-spot-check` extension; landau-fan step 1): n = +3.2e12, D = 0, B 0.3 -> 1.5 T uniform in 1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_spot, D_spot = 3.2, 0.0                       # 1e12 cm^-2, V/nm — same point as run 6
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V (run 6: +0.9836, +1.1661)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, drive {sr1.amplitude()} V (1.0), "
      f"nplci tg/bg {k_tg.nplci()}/{k_bg.nplci()} (1/1), gates now ({k_tg.volt():+.3f}, {k_bg.volt():+.3f})")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(sr1.amplitude() - 1.0) < 1e-3, "drive not 1.0 V (10 nA)"

# --- field grid: uniform in 1/B, dinv = 0.01 T^-1 (the fan's row grid; Nyquist 1/3 on F_L = 33 T), 0.3 -> 1.5 T ascending ---
B_LO, B_HI, DINV = 0.3, 1.5, 0.01
N_B = int(round((1/B_LO - 1/B_HI) / DINV)) + 1
B_vec = 1.0 / np.linspace(1/B_LO, 1/B_HI, N_B)
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP
I_TRIP, T_TRIP = 1e-9, 1.8
sr1.sensitivity(50e-6)   # 5 kOhm FS at 10 nA — the fan's sensitivity (restore left it at 2 uV)
print(f"B grid: {N_B} pts, {B_vec[0]:.4f} -> {B_vec[-1]:.4f} T, dinv {1/B_vec[0]-1/B_vec[1]:.5f}, max dB {np.diff(B_vec).max()*1e3:.1f} mT; "
      f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s / {sr1.filter_slope()} dB (settle_s {magnet.settle_s} s = dwell)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"sdh-spot-check low-field extension (landau-fan B_lo pin): n = {n_spot:+.2f}e12, D = 0 (run-5 cal), "
                  f"(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0.3 -> 1.5 T uniform 1/B dinv 0.01, sr1 50 uV")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field extension of run 6 for the landau-fan B_lo: n = {n_spot:+.2f}e12 cm^-2, D = 0; (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); '
              f'B {B_LO} -> {B_HI} T uniform in 1/B, dinv {DINV} T^-1, {N_B} pts; delay 0 (3 s settle); sr1 50 uV; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
interruptible_sleep(10)

# row layout: [time, B, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr1.P); s.plot(magnet.field, sr0.X); s.plot(magnet.field, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def guard(station, data):
    T, i_tg, i_bg = float(data[2]), abs(float(data[3])), abs(float(data[4]))
    if i_tg > I_TRIP or i_bg > I_TRIP or T > T_TRIP:
        print(f"GUARD TRIP at B={float(data[1]):+.3f} T: T={T:.3f} K, |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(guard, ())

s.sweep(magnet.field, B_vec, delay=0)
# gates stay at the n = 3.2 spot; field ends at 1.5 T — the fan ramps down to its B_lo from here.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
