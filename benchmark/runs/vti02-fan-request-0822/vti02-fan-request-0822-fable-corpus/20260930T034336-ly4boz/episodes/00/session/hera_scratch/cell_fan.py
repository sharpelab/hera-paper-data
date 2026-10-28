# === Landau fan, electron side (`landau-fan-vti`): D = 0, n = +1.2 -> +3.2e12 (101 pts) x B = 0.3 -> 10 T uniform-1/B (321 rows) ===
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB

# --- axes: run-5 calibration (cnp-and-dline-calibration), session cap on B ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(1.2, 3.2, 101)          # 1e12 cm^-2, fast axis, dn = 0.02e12
Ds = np.zeros_like(ns)                   # D = 0 operating point
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
B_vec = field_invB(0.3, 10.0, 321)       # slow axis, ascending, uniform in 1/B (d(1/B) = 0.0101 /T)
assert 0 < B_vec.min() and B_vec.max() <= B_SESSION_CAP

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05; fan ramps 0 -> 0.3 T first), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 1.2, 1.0        # 4 tau at tau = 0.3 s (rationale in markdown); slow_delay covers gate flyback
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange): 50 uV = 5 kOhm FS at 10 nA.
# Worst corner n = 1.2e12 x 10 T anchored by run 7 (0.58 kOhm at same |n|, 10 T) -> ~8x headroom.
sr1.sensitivity(50e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s; "
      f"grid {len(B_vec)} B x {len(ns)} n; Vtg [{Vtgs.min():+.4f}, {Vtgs.max():+.4f}] V, Vbg [{Vbgs.min():+.4f}, {Vbgs.max():+.4f}] V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan-vti electron side: n = +1.2..+3.2e12 (101 pts) at D = 0 (run-5 cal), "
                  "B = 0.3 -> 10 T uniform-1/B (321 rows), sr1 50 uV, fast_delay 1.2 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = 0.00 V/nm: n = +1.20 to +3.20e12 cm^-2 (101 pts, paired TG/BG n-line), '
              f'B = 0.3 -> 10 T uniform-1/B (321 rows, d(1/B) = 0.0101 /T, 3.0 samples/period at F_L(3.2e12) = 33.1 T); '
              f'sr1 50 uV; cal run 5: ratio 0.773, n_offset -0.089e12, D_offset -0.013 V/nm')
s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
magnet.field(float(B_vec[0]))            # blocking ramp 0 -> 0.3 T (~2.2 min); the set call is the settle
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg(fast pair), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f} V: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
# Field endpoint deliberate: stays at 10 T — follow-ups (B-window split / LK ladder) ride it down, never re-traverse.
print(f"done: B = {magnet.field():+.3f} T, gates parked at 0, T_sample = {T_sample():.3f} K")
