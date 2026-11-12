# === Landau fan (`landau-fan`): D = 0 line, n -1.25 -> +3.25e12 (131 pts) fast x B 0.4 -> 10 T (60 mT, 161 rows) slow ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.25, 3.25, 131)           # 1e12 cm^-2 along D = 0; step 3.46e10
D_fan = 0.0
VV = np.array([calc_gate_voltages(n, D_fan, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]) for n in n_vec])
Vtg_vec, Vbg_vec = VV[:, 0], VV[:, 1]
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
print(f"fast line: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 at D = {D_fan:+.2f} V/nm; "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} (margins {Vtg_vec.min()-TG_MIN:+.4f}/{TG_MAX-Vtg_vec.max():+.4f} V), "
      f"Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f}")

B_vec = np.round(np.arange(0.4, 10.0 + 1e-9, 0.06), 4)   # 161 rows, ascending (magnet at 0)
assert B_vec.max() <= B_SESSION_CAP and len(B_vec) == 161

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.02: fan ascends from 0.4), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.02 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()

I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: sr1 200 uV = 20 kOhm FS at 10 nA (SdH range 10-600 Ohm well resolved;
# the nu=0 CNP stripe may exceed FS at high B - accepted rail, sr0 drain current covers it).
sr1.sensitivity(200e-6)
print(f"sr1 sens {sr1.sensitivity()} V (20 kOhm FS), sr0 sens {sr0.sensitivity()} V, tau {sr1.time_constant()} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan: D = 0 (run-5 cal), n -1.25..+3.25e12 co-swept (Vtg,Vbg) 131 pts fast; "
                  "B 0.4..10 T 60 mT 161 rows slow; sr1 200 uV; fast_delay 1.0, slow_delay 2.0")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 cm^-2, 131 pts (fast, co-swept k_tg+k_bg); '
              f'B {B_vec[0]} -> {B_vec[-1]} T, 60 mT, 161 rows (slow); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'sr1 200 uV; stacking-order fan after spot checks runs 6-7')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg (fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=2.0, fast_delay=1.0)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field stays where the sweep left it (10 T on completion) - never re-traverse without a plan.
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
