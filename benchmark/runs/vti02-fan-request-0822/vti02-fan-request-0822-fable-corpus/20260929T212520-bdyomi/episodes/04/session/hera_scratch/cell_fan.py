# === Landau fan, electron side (`landau-fan-vti`): n = +1.2 -> +3.2e12 at D = 0, B 0.5 -> 10 T uniform-1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(3.2, 1.2, 91)            # fast axis, 1e12 cm^-2 — each row starts at the run-6 spot
Ds = np.zeros_like(ns)                    # D = 0 line
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, \
    (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
print(f"n-line: n = {ns[0]:+.2f} -> {ns[-1]:+.2f} e12 (91 cols), Vtg {Vtgs.max():+.4f}..{Vtgs.min():+.4f} V, "
      f"Vbg {Vbgs.max():+.4f}..{Vbgs.min():+.4f} V")

# --- field axis: uniform in 1/B, Delta(1/B) = 0.010 (Nyquist x2.5 on 40 T = 1.2x scale-prior F_L(n_max)) ---
B_vec = 1.0 / np.linspace(1 / 0.5, 1 / 10.0, 191)      # 0.5 -> 10 T ascending, 191 rows
assert B_vec.max() <= B_SESSION_CAP
print(f"B: {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {len(B_vec)} rows, d(1/B) = {(1/B_vec[0]-1/B_vec[-1])/(len(B_vec)-1):.4f} 1/T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, "
      f"output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 1.8, 1.0         # 6*tau per-column-FFT dwell; gates retrace during slow_delay
I_TRIP, T_TRIP = 1e-9, 2.0
sr1.sensitivity(100e-6)                    # 10 kOhm FS at 10 nA: run-7 corner anchor 576 Ohm at |n|=1.2e12, 10 T
_tau = sr1.time_constant()
assert abs(_tau - 0.3) < 1e-3, f"tau changed on the front panel: {_tau} s"
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {_tau} s, slope {sr1.filter_slope()} dB/oct; "
      f"fast_delay {FAST_DELAY} s = 6 tau; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan electron side: n = +1.2..+3.2e12 (91) at D = 0 (run-5 cal), "
                  "B 0.5 -> 10 T uniform-1/B d(1/B)=0.010 (191), sr1 100 uV, fast_delay 1.8 s (6 tau)")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = 0.00 V/nm: n = +1.20 to +3.20e12 cm^-2 (91-col paired n-line), '
              f'B = 0.5 to 10 T uniform-1/B d(1/B)=0.010 (191 rows); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; '
              f'follows sdh-spot-check runs 6 (electron, fan side) / 7 (hole)')

s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def run_guard(station, data):
    i_tg, i_bg, t_s = abs(float(data[5])), abs(float(data[6])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP or t_s > T_TRIP:
        print(f"GUARD TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: "
              f"|I_tg|={i_tg:.3e} A, |I_bg|={i_bg:.3e} A, T={t_s:.2f} K")
        station.interrupt_requested = True
s.register_run_after(run_guard, ())

magnet.field(B_vec[0])                     # blocking positioning ramp 0 -> 0.5 T (~4 min); the set call is the settle
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field left at 10 T deliberately — the next measurement rides it down (never re-traverse)
print(f"done: B = {magnet.field():+.3f} T, gates parked 0/0, T_sample = {T_sample():.3f} K")
