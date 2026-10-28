# === Landau fan at D = 0 (`landau-fan`): n fast along the D = 0 line x B slow 0 -> 10 T (plan step 3) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (ratio data-calibrated; c_tg = geometry prior, the fan's QH slopes calibrate it) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.25, 3.20 + 1e-9, 0.025), 4)            # 1e12 cm^-2, 179 pts
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_n_chk, _D_chk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_n_chk, n_vec) and np.abs(_D_chk).max() < 1e-9
print(f"fast: n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f}e12 ({len(n_vec)} pts, 0.025e12) at D = 0; "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V")

# --- slow axis: B up from where the magnet sits. 0.05 T to 2 T (SdH/crossing region), 0.1 T to 6 T, 0.2 T to 10 T.
B_vec = np.round(np.hstack(([0.0, 0.25], np.arange(0.5, 2.0, 0.05), np.arange(2.0, 6.0, 0.1), np.arange(6.0, 10.0001, 0.2))), 4)
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP and B_vec.min() >= 0
print(f"slow: B {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_amp, _f = sr1.amplitude(), sr1.frequency()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5) | B = {_B0:+.4f} T (|B|<0.05: fan starts at 0) | V_si = {k_si():+.3f} V (0) | "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()} | nplci tg/bg {k_tg.nplci()}/{k_bg.nplci()} (1/1) | "
      f"drive {_amp} V @ {_f} Hz (1.0 V @ 13.777 -> 10 nA) | tau {sr1.time_constant()} s / {sr1.filter_slope()} dB (0.3 / 24)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} off base"
assert abs(_B0) < 0.05, f"magnet not at ~0: {_B0} T"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert abs(_amp - 1.0) < 1e-6 and abs(_f - 13.777) < 0.01, "drive not at 1 V / 13.777 Hz"
assert sr1.time_constant() == 0.3 and sr0.time_constant() == 0.3, "lock-in tau not 0.3 s (fast_delay sized for it)"

FAST_DELAY, SLOW_DELAY = 1.0, 3.0      # 3.3 tau per point (as run 5); 10 tau after flyback + field step
I_TRIP, T_TRIP = 1e-9, 2.5             # A on either gate; K sample (magnet-heating guard; runs 6/7 peaked 1.29 K)
# Fixed sensitivity (no autorange mid-map): 100 uV = 10 kOhm FS at 10 nA — runs 6/7 peak 0.6 kOhm, run 5 ridge 3 kOhm;
# headroom for nu = 0 at the CNP at high B (a rail there costs only the CNP amplitude, stated).
sr1.sensitivity(100e-6)
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: n fast {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({len(n_vec)}), B slow 0..10 T ({len(B_vec)} rows: "
                  f"0.05 T to 2, 0.1 to 6, 0.2 to 10), sr1 100 uV, cal run 5")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: n fast {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f}e12 cm^-2 ({len(n_vec)} pts, 0.025e12) co-sweeping (Vtg, Vbg) '
              f'{Vtg_vec[0]:+.4f}->{Vtg_vec[-1]:+.4f} / {Vbg_vec[0]:+.4f}->{Vbg_vec[-1]:+.4f} V; B slow 0 -> 10 T {len(B_vec)} rows '
              f'(0, 0.25, 0.5-1.95 @ 0.05, 2.0-5.9 @ 0.1, 6.0-10.0 @ 0.2); fast_delay 1 s, slow_delay 3 s; Vsi = 0; sr1 100 uV; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg prior, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm')

# row layout: [time, B(set), Vtg, Vbg, T_sample, B(readback), I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(magnet.field).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', T_sample); s.plot('time', magnet.field)

def guard(station, data):
    T, i_tg, i_bg = float(data[4]), abs(float(data[6])), abs(float(data[7]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[5]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if T > T_TRIP:
        print(f"T TRIP at B={float(data[5]):+.3f} T: T_sample = {T:.3f} K > {T_TRIP} K")
        station.interrupt_requested = True
s.register_run_after(guard, ())

s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field stays where the fan left it (10 T on completion) — step 4 works at high B; never re-traverse.
    print(f"end: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
