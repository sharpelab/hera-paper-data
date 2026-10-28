# === Low-field extension of the electron-side spot check (`sdh-spot-check`, landau-fan step-1 lever 1): n = +3.2e12, D = 0, B 0.3 -> 1.6 T at 3 mT ===
# Purpose: run 6's carrying tone (7.3 T) is CENSORED at the Nyquist-valid record edge (1.0 T; the sub-1 T leg was 50 mT
# steps, aliased for a 7 T tone) -> the fan's B_lo is unpinned. This pins the onset, positions the magnet at the fan start,
# and tests the fan's fixed sensitivity (100 uV = 10 kOhm FS) on the smallest-amplitude end of the record.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run-5 calibration (ana)
n_spot, D_spot = 3.2, 0.0                       # 1e12 cm^-2, V/nm — same point as run 6
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left it at 0), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, T_vap = {T_vaporizer():.3f} K")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- field grid: uniform in B, 3 mT from 0.3 to 1.6 T. Nyquist at the 0.3 T edge: d(1/B) = 0.003/0.09 = 0.033 1/T -> F < 15 T
#     (the 7.3 T tone and its 2nd harmonic). Onset read: sdh_onset on this record + run 6 above 1 T.
B_vec = np.unique(np.round(np.arange(0.3, 1.6001, 0.003), 4))
assert B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9
sr1.sensitivity(100e-6)   # fan sensitivity under test: 10 kOhm FS at 10 nA (run 6/7 ran at 50 uV; R here is 20-60 Ohm)
print(f"B grid: {len(B_vec)} pts, {B_vec[0]} -> {B_vec[-1]} T; sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s, "
      f"slope {sr1.filter_slope()} dB/oct (settle_s {magnet.settle_s} s = dwell = 10 tau)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"sdh-spot-check low-field extension (electron): n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm (run-5 cal), "
                  f"(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0.3 -> 1.6 T, 3 mT, sr1 100 uV; pins the fan's B_lo")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field extension of run 6 (electron side): n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; '
              f'(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B 0.3 -> 1.6 T uniform-B 3 mT; sr1 100 uV (fan sensitivity check); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
print("positioning magnet 0 -> 0.3 T (blocking, ~2.5 min)"); magnet.field(0.3)
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
# gates stay at the spot; field ends at 1.6 T — the fan starts from here (its B_lo is this record's onset). No park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
