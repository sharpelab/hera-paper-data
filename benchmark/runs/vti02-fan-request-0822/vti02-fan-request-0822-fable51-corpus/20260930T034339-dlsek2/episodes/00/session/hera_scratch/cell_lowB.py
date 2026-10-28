# === Low-field onset extension at the electron spot (`sdh-spot-check` Verify / `landau-fan` step-1 lever 1): n = +3.2e12, D = 0, B 0.2 -> 1.05 T at 5 mT ===
# Run 6's 7.3 T tone is CENSORED at 1.0 T (alive at the edge of the 10 mT leg; the 0-1 T leg was 50 mT-stepped,
# Nyquist-blind to a 7 T tone below ~1 T). This pins the onset with a proper grid before the fan's B_lo is committed,
# and doubles as the grid-change reproduction (5 mT uniform-B vs run 6's 10 mT) for the 7.3 T tone.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run-5 calibration (ana)
n_spot, D_spot = 3.2, 0.0
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V")

# --- preconditions (assumed, not set): base T, magnet at 0 (handoff readback), Si 0, PS/output on ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: sweep starts near 0), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

B_vec = np.round(np.arange(0.2, 1.0501, 0.005), 4)          # 171 pts; dInvB at 0.3 T = 0.056/T (Nyq 9 T), at 0.5 T 0.02/T (Nyq 25 T)
assert B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9
sr1.sensitivity(50e-6)                                        # same as runs 6/7 (5 kOhm FS); R here is 10-60 Ohm
print(f"B grid: {len(B_vec)} pts, {B_vec[0]} -> {B_vec[-1]} T, 5 mT; sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct; dwell = driver settle {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = f"low-field onset extension at the electron spot: n = {n_spot:+.2f}e12, D = 0 (run-5 cal), (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0.2 -> 1.05 T 5 mT, sr1 50 uV; pins run 6's censored onset before the fan"
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field onset extension, electron side: n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); '
              f'B 0.2 -> 1.05 T uniform-B 5 mT; follows run 6 (7.3 T tone censored at 1.0 T); cal run 5')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
interruptible_sleep(10)

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
# gates stay at the spot; field stays at 1.05 T — the fan positions itself from here (B_lo from this run's onset).
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
