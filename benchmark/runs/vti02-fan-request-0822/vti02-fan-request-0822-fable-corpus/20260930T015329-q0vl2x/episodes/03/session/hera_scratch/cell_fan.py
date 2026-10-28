# === Landau fan (`landau-fan-vti`): electron side, n = 3.2 -> 1.6e12 (51 pts) at D = 0, B 1 -> 10 T uniform 1/B (91 rows) ===
from sharpelab_nb.gates import calc_gate_voltages

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)  # run 5
ns = np.linspace(3.2, 1.6, 51)          # 1e12 cm^-2; dn = 0.032e12 -> 3.0 pts per ray period at B_lo = 1 T
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs), np.asarray(Vbgs)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, \
    (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
print(f"n-line: {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({len(ns)} pts), D = 0; Vtg [{Vtgs.min():+.4f}, {Vtgs.max():+.4f}], "
      f"Vbg [{Vbgs.min():+.4f}, {Vbgs.max():+.4f}] V")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (0.9-1.1: fan starts at 1.0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and 0.9 <= _B0 <= 1.1 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- slow field axis: uniform 1/B ascending, d(1/B) = 0.01 (inherits run 6's fine-leg spacing at its
#     binding low edge; Nyquist ceiling 50 T; 1/3-rule to 33 T = F_L(n_max) at scale 1).
B_vec = field_invB(1.0, 10.0, 91)
assert B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9
FAST_DELAY, SLOW_DELAY = 1.8, 1.0        # 6*tau (tau = 0.3 s) per landau-fan step 7 per-column-FFT discipline;
                                         # field step adds blocking ramp + 3 s driver settle on top of SLOW_DELAY
sr1.sensitivity(50e-6)                   # 5 kOhm FS: worst corner (n = 1.6e12, 10 T) bracketed by run 7's 576 Ohm max
print(f"B rows: {len(B_vec)}, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T uniform 1/B; sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan-vti electron side: n = +3.2 -> +1.6e12 (51 pts) at D = 0 (run-5 cal), "
                  "B 1 -> 10 T uniform 1/B (91 rows, d(1/B) = 0.01), sr1 50 uV, fast_delay 1.8 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0 V/nm, n = +1.6 to +3.2e12 cm^-2 (51 pts, fast, descending), B = 1 -> 10 T uniform 1/B '
              f'(91 rows, d(1/B) = 0.01); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f}; per-column SdH-FFT fan for the stacking call (tetralayer-stacking-fs-count step 4)')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

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
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # park gates; field stays at 10 T (next leg rides down)
print(f"done: B = {magnet.field():+.3f} T, gates parked at 0")
