# === Landau fan at D = 0 (`landau-fan`): B slow 1.0 -> 10.0 T (0.1 T, 91 rows) x (Vtg, Vbg) co-swept along D = 0, n = -1.26..+3.24e12 (130 pts) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.26, 3.24, 130)                    # 1e12 cm^-2, D = 0; TG-limited both ends
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_Dchk).max() < 1e-6 and abs(_nchk[0] - n_vec[0]) < 1e-6
print(f"fast axis: n = {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, {n_vec[1]-n_vec[0]:.4f}e12/pt) at D = 0 -> "
      f"Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}] V, Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}] V")

# --- field grid: uniform 0.1 T, ascending from where the magnet sits (0 T) ---
B_vec = np.round(np.arange(1.0, 10.0001, 0.1), 3)
assert B_vec.max() <= B_SESSION_CAP and len(B_vec) == 91

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: fan starts by ramping to 1 T), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"volt.step tg/bg = {k_tg.volt.step}/{k_bg.volt.step} (0.005)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1 and k_tg.volt.step == 0.005 and k_bg.volt.step == 0.005

FAST_DELAY, SLOW_DELAY = 1.0, 2.0
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 200 uV = 20 kOhm full scale at 10 nA (CNP at 10 T may rail — accepted; SdH minima keep ~1 Ohm resolution).
sr1.sensitivity(200e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (20 kOhm FS), tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V")
print(f"B grid: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T; est. {len(B_vec) * (len(n_vec) * 1.17 + 6 + 0.1 / 0.137 * 60 + 3) / 3600:.1f} h + 7 min to 1 T")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: B slow 1.0 -> 10.0 T 0.1 T (91 rows); (Vtg, Vbg) co-swept along D = 0, n = {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 (130 pts); "
                  f"run-5 cal ratio {CAL['c_bg']/CAL['c_tg']:.3f}, n_offset {CAL['n_offset']:+.4f}e12, D_offset {CAL['D_offset']:+.3f}; sr1 200 uV; Vsi = 0")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: B slow [1.0, 10.0] T 0.1 T (91 rows) ascending; fast (k_tg.volt, k_bg.volt) co-swept along D = 0, '
              f'n = {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 cm^-2 ({len(n_vec)} pts), Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}], Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}]; '
              f'cal run 5: c_tg {CAL["c_tg"]:.3e} (geometry prior), c_bg {CAL["c_bg"]:.3e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; '
              f'fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, sr1 200 uV; T = {_T0:.3f} K; Vsi = 0')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(5)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, magnet.field, sr1.X)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # park the gates at (n, D) = (0, 0); the field stays where the sweep left it (10 T if complete) — the next step rides it down
    _Vt0, _Vb0 = calc_gate_voltages(0.0, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
    s.ramp(k_tg.volt, float(_Vt0)); s.ramp(k_bg.volt, float(_Vb0))
    print(f"done: B = {magnet.field():+.3f} T, gates parked at (n, D) = (0, 0): (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
