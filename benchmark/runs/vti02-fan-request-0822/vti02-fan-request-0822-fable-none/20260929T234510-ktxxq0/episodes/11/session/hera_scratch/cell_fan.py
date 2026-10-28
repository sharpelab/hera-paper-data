# === Landau fan (`landau-fan`): D = 0 line, n fast -1.25 -> +3.20e12 (179 pts), B slow 1 -> 10 T uniform-1/B (145 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.25, 3.2001, 0.025), 4)         # 1e12 cm^-2; 179 pts
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())

# --- field rows: uniform in 1/B, ascending 1 -> 10 T (magnet sits at ~0; never re-traverse) ---
B_vec = np.round(1.0 / np.linspace(1.0, 0.1, 145), 4)        # d(1/B) = 6.25e-3 -> F_Nyq = 80 T, dF = 1.11 T
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"fan: {len(B_vec)} B rows {B_vec[0]} -> {B_vec[-1]} T (uniform 1/B) x {len(n_vec)} n pts "
      f"[{n_vec[0]:+.3f}, {n_vec[-1]:+.3f}]e12; Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}], "
      f"Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}] V")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()

I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange mid-run): 100 uV = 10 kOhm FS at 10 nA
# (run-5 sizing lesson; D = 0 CNP peak ~330 Ohm at 0 T — headroom for the high-B CNP stripe;
# clipping there, if any, is narrow in n and flagged in analysis via r_full_scale).
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); tau {sr1.time_constant()} s / slope {sr1.filter_slope()} dB")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan: D = 0 (run-5 cal), n fast -1.25..+3.20e12 (179, dn 0.025), "
                  "B slow 1..10 T uniform-1/B (145), sr1 100 uV, fast_delay 1.0")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line: n fast [-1.25, +3.20]e12 cm^-2, 179 pts (dn 0.025e12), co-swept (Vtg, Vbg); '
              f'B slow 1 -> 10 T, 145 rows uniform in 1/B (d(1/B) 6.25e-3 T^-1, F_Nyq 80 T, dF 1.11 T); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'follows sdh-spot-checks runs 6-7 (light tone 7.1 T + ~26-33 T weight: harmonic-vs-band ambiguity -> F(n) slopes)')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec],
                     [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=3.0, fast_delay=1.0)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# field stays at 10 T — the next step rides it down (never re-traverse); gates parked at 0.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
