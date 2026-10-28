# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +1.2 -> +3.2e12 (121 pts) x B 0.35 -> 10 T uniform-1/B (277 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(3.2, 1.2, 121)          # 1e12 cm^-2, fast axis (n_hi -> n_lo), D = 0
Ds = np.zeros(len(ns))
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, \
    (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
print(f"n-line: n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = 0; Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, "
      f"Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V (validators [{TG_MIN},{TG_MAX}] / [{BG_MIN},{BG_MAX}])")

# --- slow field axis: uniform in 1/B, ascending 0.35 -> 10 T (magnet sits at 0; fan ends at 10 T, held deliberately) ---
B_LO, B_HI, N_B = 0.35, 10.0, 277
invB = np.linspace(1.0 / B_LO, 1.0 / B_HI, N_B)
B_vec = 1.0 / invB
d_invB = (1.0 / B_LO - 1.0 / B_HI) / (N_B - 1)
assert B_vec.max() <= B_SESSION_CAP
print(f"B: {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows, d(1/B) = {d_invB:.5f} /T "
      f"(Nyquist at F_L=33.1 T: {1/(d_invB*33.1):.2f} samples/period; dF = {1/(1/B_LO-1/B_HI):.3f} T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.02), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.02 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- lock-in: fixed for the whole fan; settling floor tau = 0.3 s / 24 dB -> fast_delay 6*tau ---
sr1.sensitivity(50e-6)   # 5 kOhm FS at 10 nA; worst corner (n=1.2e12, 10 T) measured 576 Ohm = 12% FS (run 7)
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f"sr1 sens {sr1.sensitivity()} V, tau {_tau} s, slope {_slope} dB/oct (expect 0.3 / 24); drive {sr1.amplitude()} V -> 10 nA")
assert _tau == 0.3, f"tau changed: {_tau}"
FAST_DELAY, SLOW_DELAY = 1.8, 1.0        # 6*tau (per-column SdH-FFT fan, landau-fan step 7); gates retrace in slow_delay
I_TRIP = 1e-9

_eta_h = (N_B * (len(ns) * (FAST_DELAY + 0.10) + SLOW_DELAY + 3.0 + 0.7) + (B_HI - B_LO) / 0.137 * 60 + B_LO / 0.137 * 60) / 3600
print(f"predicted wall-clock ~{_eta_h:.1f} h (per-point 1.9 s from run-5 calibration; +5-10% overrun per session evidence)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron: n = +1.2..+3.2e12 (121) at D = 0 (run-5 cal), "
                  f"B 0.35 -> 10 T uniform-1/B (277), sr1 50 uV, fast_delay 1.8 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = 0: n = +1.20 to +3.20e12 cm^-2 (121 pts, paired n-line); '
              f'B = 0.35 -> 10 T uniform-1/B, 277 rows, d(1/B) = 0.0100 /T (inherits run-6 spot check); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'sr1 50 uV, tau 0.3 s / 24 dB, fast_delay 1.8 s (6 tau)')

magnet.field(B_LO)                        # blocking ramp ~2.6 min + 3 s driver settle
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg(fast), T_sample, k_tg.curr(5), k_bg.curr(6), sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"fan done/stopped: B held at {magnet.field():+.3f} T (deliberate — next step decides the descent), gates parked at 0")
