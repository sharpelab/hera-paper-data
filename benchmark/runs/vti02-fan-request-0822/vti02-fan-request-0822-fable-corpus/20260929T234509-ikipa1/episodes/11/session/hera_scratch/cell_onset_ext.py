# === SdH low-field onset extension (`sdh-spot-check`): n = +3.2e12, D = 0, B 0 -> 0.55 T at 1.5 mT ===
# Run 6's carrying tone (7.1 T) is censored at its 0.3 T analysis edge; landau-fan step 1
# (lever 1) requires the measured onset before committing the fan. This pins it.
from sharpelab_nb.gates import calc_gate_voltages

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_spot, D_spot = 3.2, 0.0
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.02: sweep starts at 0), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.02 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

# 1.5 mT uniform: Nyquist-2 on the 7.1 T tone down to B = 0.15 T (dB = B^2/(2*7.1)),
# on the 9.5 T censored tone down to 0.17 T. Below that the record is background.
B_vec = np.round(np.arange(0.0, 0.5501, 0.0015), 5)
assert B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9
sr1.sensitivity(50e-6)   # as run 6: 5 kOhm FS, R(B<0.55) ~ 70-90 Ohm; no MR headroom needed this low
print(f"B grid: {len(B_vec)} pts, {B_vec[0]} -> {B_vec[-1]} T; sr1 sens {sr1.sensitivity()} V, "
      f"tau {sr1.time_constant()} s (settle_s {magnet.settle_s} s = 10 tau dwell)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"sdh-spot-check low-field onset extension: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm "
                  f"(run-5 cal), (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0 -> 0.55 T, 1.5 mT, sr1 50 uV")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field onset extension of run 6: n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; '
              f'(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B 0 -> 0.55 T uniform-B 1.5 mT; '
              f'pins the fan B_lo (run 6 tone censored at 0.3 T)')
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
# ends at 0.55 T with gates at the spot; the fan rides down ~2 min to its B_lo — no park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
