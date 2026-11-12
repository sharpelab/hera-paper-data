# === Landau fan at D = 0 (`landau-fan`): n fast along the calibrated D = 0 line, B slow 0 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.round(np.arange(-1.25, 3.2501, 0.02), 4)          # 1e12 cm^-2, 226 pts along D = 0
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, \
    (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
B_vec = np.round(np.arange(0.0, 10.0001, 0.05), 4)         # 201 rows, 50 mT
assert B_vec.max() <= B_SESSION_CAP
print(f"fan: n {ns[0]:+.2f} .. {ns[-1]:+.2f} e12 x {len(ns)} pts; Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, "
      f"Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f}; B {B_vec[0]} -> {B_vec[-1]} T x {len(B_vec)} rows")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- speed/sizing: gate-current reads to NPLC 1 (leakage established runs 0-3 + per-run guards; rig-card timing note),
#     sr1 to 200 uV = 20 kOhm FS at ~10 nA (0.7 Ohm quantization; the nu=0 ridge may clip at high B - accepted, position still reads)
print(f"NPLC before: tg {k_2400_tg.nplci()}, bg {k_2400_bg.nplci()}")
k_2400_tg.nplci(1); k_2400_bg.nplci(1)
sr1.sensitivity(200e-6)
print(f"NPLC after: tg {k_2400_tg.nplci()}, bg {k_2400_bg.nplci()}; sr1 sens {sr1.sensitivity()} V, "
      f"tau {sr1.time_constant()} s / slope {sr1.filter_slope()} dB")

I_TRIP = 2e-9   # sustained-leak trip, ~20x the observed ~100 pA scale, above NPLC-1 read noise
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: n {ns[0]:+.2f}..{ns[-1]:+.2f}e12 x {len(ns)} (0.02e12), B 0->10 T x {len(B_vec)} (50 mT), "
                  f"sr1 200 uV, NPLC 1, run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f}): fast n = {ns[0]:+.2f} .. {ns[-1]:+.2f}e12 ({len(ns)} pts, 0.02e12) '
              f'co-swept (Vtg, Vbg) = ({Vtgs[0]:+.4f},{Vbgs[0]:+.4f}) .. ({Vtgs[-1]:+.4f},{Vbgs[-1]:+.4f}); '
              f'slow B = 0 -> 10 T (201 rows, 50 mT); Vsi = 0, base T; sr1 200 uV, Keithley NPLC 1')

# park gates at the row start before the sweep (paced by volt.step)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr1.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=3, fast_delay=0.35)
# ends at 10 T with gates at the electron end of the D = 0 line - next step rides the field down (never re-traverse)
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
