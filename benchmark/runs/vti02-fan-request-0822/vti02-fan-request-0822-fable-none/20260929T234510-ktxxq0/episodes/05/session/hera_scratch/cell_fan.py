# === Landau fan at D = 0 (`landau-fan`): n -1.25 -> +3.25e12 (co-swept TG/BG line, run-5 cal), B 1.2 -> 10 T uniform in 1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.25, 3.25, 121)           # 1e12 cm^-2, step 0.0375e12; D = 0 fixed
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
print(f"fast axis: n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f} e12 ({len(n_vec)} pts); "
      f"Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}] V, Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}] V")

# --- slow axis: B uniform in 1/B (SdH-periodic axis; hands sdh_fft an even record), ascending from where the magnet sits ---
B_vec = np.round(1.0 / np.linspace(1.0 / 1.2, 1.0 / 10.0, 97), 4)
assert B_vec.max() <= B_SESSION_CAP
du = abs(np.diff(1.0 / B_vec)).max()
print(f"slow axis: B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows uniform-1/B; d(1/B) = {du:.5f} -> F_Nyq {0.5/du:.0f} T, dF_res {1/(1/B_vec[0]-1/B_vec[-1]):.2f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left 0 T), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

I_TRIP = 1e-9
# Sensitivity 100 uV = 10 kOhm FS at 10 nA: 17x the observed high-B 1D max (run 7: 590 Ohm at 10 T) per the
# run-4 lesson (size >= 10x). The nu=0/CNP stripe at high B may still rail — accepted, excluded from FFT.
sr1.sensitivity(100e-6)
print(f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct; "
      f"fast_delay 1.0 s (3.3 tau, run-5-proven quasi-continuous gate steps), magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan: D = 0 line (run-5 cal), n -1.25 -> +3.25e12 121 pts co-swept TG/BG; "
                  "B 1.2 -> 10 T uniform-1/B 97 rows; Vsi = 0; sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f}e12 cm^-2 (121 pts), fast = [k_tg.volt, k_bg.volt] co-swept; '
              f'B {B_vec[0]} -> {B_vec[-1]} T (97 rows uniform in 1/B, d(1/B) {du:.5f}); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, i_tg, i_bg, sr0_X, sr0_P, sr1_X, sr1_P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=3.0, fast_delay=1.0)
# ends at 10 T with the gates at n = +3.25e12 — no park; the next step decides the ride-down.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
