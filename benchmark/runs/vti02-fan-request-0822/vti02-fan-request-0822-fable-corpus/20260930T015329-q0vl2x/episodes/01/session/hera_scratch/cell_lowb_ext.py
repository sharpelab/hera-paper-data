# === Low-field onset extension (`sdh-spot-check`): n = +3.2e12 at D = 0, B 0.3 -> 1.3 T fine grid ===
# Pins the fan's B_lo: run 6's carrying tone (7.1 T) is censored at the record edge and its
# sub-1 T leg (50 mT) undersamples 7.1 T below ~0.85 T (Nyquist dB <= 0.07*B^2). Grid here:
# 5 mT below 0.6 T (Nyquist at 0.3 T needs <= 6.3 mT), 10 mT above (matches run 6's fine leg).
from sharpelab_nb.gates import calc_gate_voltages

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)  # run 5
n_spot, D_spot = 3.2, 0.0
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V (== run 6)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left field at 0), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

B_vec = np.unique(np.round(np.hstack((np.arange(0.3, 0.6, 0.005), np.arange(0.6, 1.3001, 0.01))), 4))
assert B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9
# Sensitivity sized to the local record, not the 10 T excursion: run 6 below 1.3 T stayed <= 57 Ohm
# (med 6-16). 5 uV = 500 Ohm FS at 10 nA -> 8.8x headroom, ADC step ~15 mOhm (near-onset dR is sub-Ohm;
# at run 6's 50 uV it was ~150 mOhm/count — too coarse for an onset hunt).
sr1.sensitivity(5e-6)
print(f"B grid: {len(B_vec)} pts, {B_vec[0]} -> {B_vec[-1]} T (5 mT < 0.6 T, 10 mT above); "
      f"sr1 sens {sr1.sensitivity()} V (500 Ohm FS), tau {sr1.time_constant()} s (settle_s {magnet.settle_s} s = dwell)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"sdh-spot-check low-field onset extension: n = {n_spot:+.2f}e12, D = 0 (run-5 cal), "
                  f"(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0.3 -> 1.3 T (5/10 mT), sr1 5 uV")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field onset extension of run 6: n = {n_spot:+.2f}e12 cm^-2, D = 0; '
              f'B 0.3 -> 1.3 T, 5 mT below 0.6 T / 10 mT above (7.1 T tone Nyquist); pins landau-fan B_lo')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
interruptible_sleep(10)

# row layout: [time, B, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[3])), abs(float(data[4]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.sweep(magnet.field, B_vec, delay=0)
# ends at 1.3 T, gates at the spot — the fan starts near here (B_lo from this record), no park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
