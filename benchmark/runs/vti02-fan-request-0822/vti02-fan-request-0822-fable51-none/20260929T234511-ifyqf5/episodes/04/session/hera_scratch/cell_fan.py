# === Landau fan at D = 0 (`landau-fan`): B slow 1.0 -> 10.0 T (0.1 T, 91 rows) x n fast -1.25 -> +3.30e12 (92 pts, co-swept Vtg/Vbg) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.25, 3.30, 92)                       # 1e12 cm^-2, dn = 0.05
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), **CAL)
Vtg_vec, Vbg_vec = np.round(np.asarray(Vtg_vec), 5), np.round(np.asarray(Vbg_vec), 5)
assert TG_MIN <= Vtg_vec.min() and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert BG_MIN <= Vbg_vec.min() and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
B_vec = np.round(np.arange(1.0, 10.0001, 0.1), 3)
assert B_vec.max() <= B_SESSION_CAP and len(B_vec) == 91
_n_chk, _D_chk = calc_nD(Vtg_vec, Vbg_vec, **CAL)
print(f"fast axis: {len(n_vec)} pts, n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 (dn {n_vec[1]-n_vec[0]:.3f}); "
      f"Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}] (step {abs(Vtg_vec[1]-Vtg_vec[0])*1e3:.1f} mV), "
      f"Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}] (step {abs(Vbg_vec[1]-Vbg_vec[0])*1e3:.1f} mV); max |D| on line {np.abs(_D_chk).max():.4f} V/nm")
print(f"slow axis: {len(B_vec)} rows, B {B_vec[0]} -> {B_vec[-1]} T, step {B_vec[1]-B_vec[0]:.2f} T; validators tg {k_tg.volt.vals}, bg {k_bg.volt.vals}, field {magnet.field.vals}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: the fan ramps up from where the magnet sits), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()

I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 200 uV = 20 kOhm FS at 10 nA (0.6 Ohm LSB; nu = 0 core at high B may soft-clip -- accepted).
sr1.sensitivity(200e-6)
print(f"drive {sr1.amplitude()} V @ {sr1.frequency()} Hz -> 10 nA; sr1 sens {sr1.sensitivity()} V (20 kOhm FS), tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; "
      f"sr0 sens {sr0.sensitivity()} V; magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: B slow {B_vec[0]}-{B_vec[-1]} T step 0.1 ({len(B_vec)} rows), n fast {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({len(n_vec)} pts) "
                  f"co-swept Vtg/Vbg on the run-5 D = 0 line; sr1 200 uV; fast_delay 1.0, slow_delay 2.0")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e} F/m2 prior, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm); '
              f'slow magnet.field {B_vec[0]} -> {B_vec[-1]} T x 0.1 T ({len(B_vec)} rows); fast n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12, {len(n_vec)} pts (dn 0.05e12): '
              f'Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V; T_sample {_T0:.3f} K; Vsi 0')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(5)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, magnet.field, sr1.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B = {float(data[1]):+.3f} T, Vtg = {float(data[2]):+.4f}, Vbg = {float(data[3]):+.4f}: |I_tg| = {i_tg:.3e}, |I_bg| = {i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec], slow_delay=2.0, fast_delay=1.0)
finally:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
# field stays at 10 T (the next measurement rides it down) -- no field move here.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
