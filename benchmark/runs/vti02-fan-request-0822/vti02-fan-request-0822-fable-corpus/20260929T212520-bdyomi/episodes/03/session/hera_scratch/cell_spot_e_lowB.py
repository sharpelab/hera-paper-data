# === SdH spot check, electron side — LOW-FIELD EXTENSION (`sdh-spot-check`): n = +3.2e12, D = 0, B 1.05 -> 0.30 T, 3 mT ===
# Pins the fan's B_lo (landau-fan step 1 lever 1): run 6's carrying tone (7.3 T) is censored at the fine
# grid's low edge (1.0 T); the 50 mT leg below 1 T is aliased. Grid-change reproduction retires the
# sub-1 T censored tones (3.0/4.2/5.1/9.5 T) for free.
from sharpelab_nb.gates import calc_gate_voltages

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run-5 calibration
n_spot, D_spot = 3.2, 0.0
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)

# --- preconditions (assumed, not set): handoff state — base T, B = 0, Si 0 ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff state), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- descending grid 1.05 -> 0.30 T, 3 mT uniform (Nyquist covers 2x7.3 T at the 0.3 T bottom edge) ---
B_vec = np.round(np.arange(1.05, 0.2999, -0.003), 4)
assert B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9
# Sensitivity: run 6 has R <= 57 Ohm below 1.1 T at this spot -> 2 uV = 200 Ohm FS at 10 nA (peak ~28 % FS,
# 3.5x headroom); the 50 uV spot-check scale leaves this signal at ~1 % FS (coarse-ADC grainy FFT).
sr1.sensitivity(2e-6)
print(f"B grid: {len(B_vec)} pts, {B_vec[0]} -> {B_vec[-1]} T; sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s (settle_s {magnet.settle_s} s = dwell)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = f"sdh-spot-check electron LOW-B EXTENSION: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm (run-5 cal), (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 1.05 -> 0.30 T, 3 mT, sr1 2 uV"
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'electron side LOW-B extension of run 6: n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; '
              f'(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B 1.05 -> 0.30 T uniform-B 3 mT; pins the fan B_lo; '
              f'cal run 5: ratio 0.773, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
interruptible_sleep(10)
magnet.field(1.05)   # blocking pre-position, ~7.7 min from 0 T (recipe step 4: the set call is the settle)

# row layout: [time, B, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X); s.plot('time', T_sample); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[3])), abs(float(data[4]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.sweep(magnet.field, B_vec, delay=0)
# End state: B = 0.30 T, gates at the spot — the fan starts here. No park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
