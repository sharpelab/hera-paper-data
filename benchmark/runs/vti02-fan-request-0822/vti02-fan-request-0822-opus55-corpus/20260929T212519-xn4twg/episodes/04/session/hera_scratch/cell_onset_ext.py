# === Step 4a: low-field onset extension (`sdh-spot-check`), n = +2.0e12 at D = 0, B 0.3 -> 3.0 T uniform in 1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_spot, D_spot = 2.0, 0.0                       # 1e12 cm^-2, V/nm
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V; "
      f"roundtrip n,D = {calc_nD(Vtg_spot, Vbg_spot, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left 0 T), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"sr1 tau {sr1.time_constant()} s / {sr1.filter_slope()} dB (0.3 / 24: the 3 s settle = 10 tau)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24, "lock-in settling changed since runs 6/7"
assert abs(sr1.amplitude() - 1.0) < 1e-3, f"drive {sr1.amplitude()} V != 1.0 V (10 nA)"

# --- field grid: uniform in 1/B, dinvB = 0.0125 1/T (Nyquist 40 T; F_L(2.0e12) = 20.7 T), ascending from where the magnet sits
B_vec = field_invB(0.3, 3.0, 241)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
print(f"B grid: {len(B_vec)} pts, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {1/B_vec[0]-1/B_vec[1]:.4f} 1/T")
I_TRIP = 1e-9
sr1.sensitivity(50e-6)   # inherited from runs 6/7: 5 kOhm FS at 10 nA (state0 restore left 2 uV)
print(f"sr1 sens {sr1.sensitivity()} V, sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"sdh-spot-check onset extension: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm (run-5 cal), "
                  f"(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0.3 -> 3.0 T uniform-1/B 241 pts, sr1 50 uV")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'onset extension for landau-fan B_lo + third density for the 7 T tone: n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; '
              f'(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B 0.3 -> 3.0 T uniform-1/B d(1/B)=0.0125; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
interruptible_sleep(10)

# row layout: [time, B, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X); s.plot(magnet.field, sr1.P); s.plot(magnet.field, sr0.P)
s.plot('time', T_sample); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[3])), abs(float(data[4]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.sweep(magnet.field, B_vec, delay=0)
# gates stay at the spot, field stays at 3.0 T — the fan (Step 4) starts from here.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
