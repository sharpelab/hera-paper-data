# === Low-field extension (`sdh-spot-check`): n = +2.0e12, D = 0, B 1.5 -> 0.3 T uniform in 1/B — pins the light-tone onset for the fan's B_lo ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from qcodes import Parameter

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_spot, D_spot = 2.0, 0.0                       # 1e12 cm^-2, V/nm — the fan's low-density (binding) column
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.02: handoff left 0 T), V_si = {k_si():+.3f} V (0), "
      f"V_tg/V_bg = {k_tg.volt():+.3f}/{k_bg.volt():+.3f} (0/0), nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.02 and abs(k_si()) < 0.01
assert abs(k_tg.volt()) < 0.01 and abs(k_bg.volt()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f"sr1 tau {_tau} s, slope {_slope} dB/oct (expect 0.3 / 24: the 3 s magnet settle = 10 tau is the dwell)")
assert _tau == 0.3 and _slope == 24

# --- field grid: uniform in 1/B, descending 1.5 -> 0.3 T. Nyquist: F_L(2.0e12) = 20.7 T -> d(1/B) <= 1/(3 F_L) = 0.0161
B_vec = field_invB(1.5, 0.3, 168)
d_invB = abs(np.diff(1 / B_vec)).max()
assert B_vec.max() <= B_SESSION_CAP and d_invB <= 1 / (3 * 20.7) + 1e-6
I_TRIP, T_TRIP = 1e-9, 1.8
sr1.sensitivity(50e-6)   # 5 kOhm FS at 10 nA — spot-check scale (runs 6/7); state0 restore left it at 2 uV
print(f"B grid: {len(B_vec)} pts, {B_vec[0]} -> {B_vec[-1]} T, d(1/B) = {d_invB:.4f} 1/T; sr1 sens {sr1.sensitivity()} V; settle_s {magnet.settle_s} s")

# measured field (FastBi readback = output current x T_per_A; the slow column records the setpoint)
if "B_meas" not in globals():
    B_meas = Parameter("B_meas", label="B readback", unit="T", get_cmd=magnet.field.get)

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"sdh-spot-check low-field extension: n = {n_spot:+.2f}e12, D = 0 (run-5 cal), (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), "
                  f"B 1.5 -> 0.3 T uniform-1/B 168 pts, sr1 50 uV")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field extension for the landau-fan B_lo: n = {n_spot:+.2f}e12 cm^-2, D = 0; (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); '
              f'B 1.5 -> 0.3 T uniform in 1/B (168 pts, d(1/B) = {d_invB:.4f}); cal run 5: ratio 0.773, n_offset -0.089e12, D_offset -0.013')

# positioning: magnet 0 -> 1.5 T (blocking, ~11 min bare), then gates to the spot
magnet.field(B_vec[0])
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
interruptible_sleep(10)

# row layout: [time, B(set), T_sample, B_meas, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(B_meas).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X); s.plot(magnet.field, sr1.P); s.plot(magnet.field, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample); s.plot(magnet.field, B_meas)

def guard(station, data):
    i_tg, i_bg, T = abs(float(data[4])), abs(float(data[5])), float(data[2])
    if i_tg > I_TRIP or i_bg > I_TRIP or T > T_TRIP:
        print(f"GUARD TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A, T={T:.3f} K")
        station.interrupt_requested = True
s.register_run_after(guard, ())

s.sweep(magnet.field, B_vec, delay=0)
# gates stay at n = 2.0 (the fan's first column); field ends at 0.3 T, below the fan's start — no park.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
