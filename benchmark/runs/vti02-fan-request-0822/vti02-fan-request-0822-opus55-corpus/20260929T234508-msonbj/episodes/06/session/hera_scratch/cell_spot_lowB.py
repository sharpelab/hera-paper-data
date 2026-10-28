# === SdH low-field extension, electron side (`sdh-spot-check`): n = +3.2e12, D = 0, B 0.4 -> 1.1 T uniform in 1/B ===
# Pins the light-tone onset that run 6 censored at its 1 T record edge; sets the fan's B_lo (and with it n_lo).
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run 5 cnp-and-dline-calibration
n_spot, D_spot = 3.2, 0.0
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V (run 6: +0.9836, +1.1661)")
# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05 after handoff), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
# --- grid: uniform in 1/B, d(1/B) = 0.0125 1/T (Nyquist 40 T > F_L = 33.1 T); ascending so the magnet rides toward the fan ---
B_vec = field_invB(0.4, 1.1, 128)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP and abs(B_vec[0] - 0.4) < 1e-6
d_invB = np.abs(np.diff(1 / B_vec))
print(f"B grid: {len(B_vec)} pts {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {d_invB.mean():.4f} 1/T (Nyquist {1/(2*d_invB.max()):.1f} T)")
I_TRIP = 1e-9
# Fixed sensitivity: 2 uV = 200 Ohm FS at 10 nA; run 6 had R <= 57 Ohm below 1.2 T at this density (3.5x headroom).
sr1.sensitivity(2e-6)
print(f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s / {sr1.filter_slope()} dB (settle_s {magnet.settle_s} s = dwell, 10 tau)")
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"sdh-spot-check low-field extension (electron): n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm (run-5 cal), "
                  f"(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0.4 -> 1.1 T uniform-1/B 128 pts, sr1 2 uV")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field extension of run 6 (onset censored at 1 T): n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; '
              f'(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B 0.4 -> 1.1 T uniform in 1/B, 128 pts, d(1/B) 0.0125; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; sr1 2 uV')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
magnet.field(float(B_vec[0]))          # blocking bare ramp 0 -> 0.4 T (~3 min)
print(f"positioned: B = {magnet.field():+.4f} T")
interruptible_sleep(10)
# row layout: [time, B, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr1.P); s.plot(magnet.field, sr0.X); s.plot(magnet.field, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)
def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[3])), abs(float(data[4]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())
s.sweep(magnet.field, B_vec, delay=0)
# gates stay at n = 3.2 (the fan's first column); field stays at 1.1 T — no park.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
