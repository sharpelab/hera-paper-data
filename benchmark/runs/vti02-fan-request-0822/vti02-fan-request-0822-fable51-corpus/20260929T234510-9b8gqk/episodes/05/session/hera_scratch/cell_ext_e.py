# === SdH low-field extension (`sdh-spot-check`, onset pin for the fan): n = +3.2e12 at D = 0, B 0.3 -> 1.3 T uniform in 1/B ===
# Run 6's 7.3 T tone is censored at the 1.0 T edge of its 10 mT segment (SNR 96 there); the 50 mT leg below 1 T
# under-samples a 7 T tone below ~0.85 T. landau-fan step 1 lever (1): pin the onset cheaply before committing the fan.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run-5 calibration (ana)
n_spot, D_spot = 3.2, 0.0                       # same column as run 6 -> shared-density quality comparison
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left it at 0), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, sample/vap heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0

# --- field grid: uniform in 1/B, 0.3 -> 1.3 T, d(1/B) = 0.020 1/T (Nyquist 25 T; 3.4x the 7.3 T tone), 129 pts ---
B_vec = field_invB(0.3, 1.3, 129)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9
# Sensitivity 20 uV = 2 kOhm FS at 10 nA: R(0.3-1.3 T) <= 60 Ohm (run 6) = 3 % FS, LSB 0.07 Ohm (measured 0.19 Ohm at 50 uV).
sr1.sensitivity(20e-6)
print(f"B grid: {len(B_vec)} pts, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T uniform 1/B; sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s (settle_s {magnet.settle_s} s = dwell)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = f"sdh-spot-check low-field extension (onset pin): n = {n_spot:+.2f}e12, D = {D_spot:+.2f} (run-5 cal), (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0.3 -> 1.3 T uniform 1/B 129 pts, sr1 20 uV"
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field extension of run 6 (onset pin for landau-fan-vti): n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; '
              f'(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B 0.3 -> 1.3 T uniform 1/B, d(1/B) = 0.020, 129 pts; sr1 20 uV; cal run 5')
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
# gates stay at the spot; field stays at 1.3 T — the fan's first slow set ramps it to B_lo. No park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
