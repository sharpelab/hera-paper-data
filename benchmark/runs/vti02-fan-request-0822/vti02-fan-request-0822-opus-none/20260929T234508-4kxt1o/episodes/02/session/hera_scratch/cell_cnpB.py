# === Step 4a, `cnp-vs-field`: R at the CNP (n = 0, D = 0), B 0 -> 10 T ===
# Pre-leg to the Landau fan: the 0 -> 10 T ramp the fan needs anyway, recorded.
# Ends at 10 T with the gates at the CNP; the fan (step 4b) rides the magnet down.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_spot, D_spot = 0.0, 0.0                       # region-A charge neutrality on the D = 0 line
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"CNP spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V; "
      f"roundtrip n,D = {calc_nD(Vtg_spot, Vbg_spot, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: sweep starts at 0), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- field grid: uniform in B, 100 mT, ascending (a smooth envelope, not an oscillation: no 1/B grid needed)
B_vec = np.round(np.arange(0.0, 10.0001, 0.1), 4)
assert B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9
# Deliberately generous: 1 mV = 100 kOhm FS at 10 nA. R_CNP(B = 0) = 240 Ohm (run 5) is 0.24 % FS -- noisy and
# accepted; this leg's job is to find the ceiling that sizes the fan's sensitivity, not to measure 240 Ohm well.
sr1.sensitivity(1e-3)
print(f"B grid: {len(B_vec)} pts, {B_vec[0]} -> {B_vec[-1]} T, 100 mT; sr1 sens {sr1.sensitivity()} V "
      f"(R_FS = {sr1.sensitivity()/10e-9/1e3:.0f} kOhm at 10 nA), tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB "
      f"(settle_s {magnet.settle_s} s = dwell); sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"cnp-vs-field: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm (run-5 cal), "
                  f"(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0 -> 10 T, 100 mT, sr1 1 mV")
s = sweep.AsyncStation(mc)
s.add_comment('cnp-vs-field')
s.add_comment(f'charge neutrality vs field: n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; '
              f'(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B 0 -> 10 T uniform-B 100 mT; '
              f'pre-leg sizing the landau-fan sensitivity at its worst corner (n ~ 0, B = 10 T); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
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
# gates stay at the CNP; field stays at 10 T -- the landau fan rides it down. No park here.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
