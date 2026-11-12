# === SdH onset extension, electron side (`sdh-spot-check`): n = +3.2e12, D = 0; B 0.25 -> 1.10 T, 2.5 mT ===
# Pins the onset for the landau-fan B_lo (run 6's carrying tone is censored on the aliased 50 mT leg);
# doubles as the grid-change reproduction check on run 6's sub-1 T censored tones (3.0/4.2/5.1/9.5 T).
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run-5 cal
n_spot, D_spot = 3.2, 0.0
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V "
      f"(same point as run 6)")

# --- preconditions (assumed, not set): handoff state0 — gates 0, field 0, base T ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- field grid: uniform B, 2.5 mT, ascending 0.25 -> 1.10 T. At the 0.25 T low edge
# d(1/B) = dB/B^2 = 0.040 -> Nyquist F = 12.5 T > 1.5x the 7.5 T carrying tone (2nd harmonic
# clean above 0.42 T; harmonics are negligible near onset). Ends at 1.10 T, overlapping run 6's
# fine leg by 0.1 T for cross-normalization; fan then starts from the measured onset nearby.
B_vec = np.unique(np.round(np.arange(0.25, 1.10001, 0.0025), 5))
assert B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9
sr1.sensitivity(50e-6)   # inherit run 6 (R <= 120 Ohm below 1.1 T = 2.4% FS of 5 kOhm; headroom fine)
print(f"B grid: {len(B_vec)} pts, {B_vec[0]} -> {B_vec[-1]} T, 2.5 mT; sr1 sens {sr1.sensitivity()} V, "
      f"tau {sr1.time_constant()} s (settle_s {magnet.settle_s} s = dwell, as runs 6/7)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"sdh-spot-check onset extension, electron: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} (run-5 cal), "
                  f"(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0.25 -> 1.10 T 2.5 mT, sr1 50 uV")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'electron onset extension: n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; '
              f'(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B 0.25 -> 1.10 T uniform-B 2.5 mT; '
              f'pins landau-fan B_lo (run 6 carrying tone censored on aliased 50 mT leg); '
              f'grid-change check on run-6 sub-1 T tones; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
interruptible_sleep(10)

# row layout: [time, B, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[3])), abs(float(data[4]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.sweep(magnet.field, B_vec, delay=0)
# gates stay at the spot; field ends at 1.10 T — the fan ramps down to its measured B_lo from here.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
