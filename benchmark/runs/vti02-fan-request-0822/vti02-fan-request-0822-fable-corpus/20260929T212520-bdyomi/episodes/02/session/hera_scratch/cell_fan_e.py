# === Landau fan, electron side (`landau-fan-vti`): n = +1.8 -> +3.2e12 at D = 0, B 0.4 -> 6 T uniform-1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(1.8, 3.2, 81)              # 1e12 cm^-2, ascending; 2.2 pts per ray period at 0.4 T
Ds = np.zeros_like(ns)                      # D = 0 line
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
print(f"fast axis: n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 (81 pts), Vtg {Vtgs[0]:+.4f} -> {Vtgs[-1]:+.4f}, "
      f"Vbg {Vbgs[0]:+.4f} -> {Vbgs[-1]:+.4f} V")

B_vec = field_invB(0.4, 6.0, 233)           # uniform 1/B, d(1/B) = 0.01006 = Nyquist/3 on F_L(3.2e12) = 33.1 T
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
print(f"slow axis: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {len(B_vec)} rows (dB {abs(B_vec[1]-B_vec[0])*1e3:.1f} mT "
      f"-> {abs(B_vec[-1]-B_vec[-2])*1e3:.0f} mT); est. 11 h (grid 10.0 h + traverse 41 min + row overhead 17 min)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0.4), "
      f"V_si = {k_si():+.3f} V (0), gates ({k_tg.volt():+.3f}, {k_bg.volt():+.3f}) V, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, "
      f"output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()
_tau = sr1.time_constant()
print(f"sr1 tau {_tau} s, slope {sr1.filter_slope()} dB/oct; fast_delay 1.8 s = 6 tau")
assert abs(_tau - 0.3) < 1e-3, "fan dwell keyed on tau = 0.3 s; re-derive fast_delay if tau changed"

I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (spot-check inheritance): 50 uV = 5 kOhm FS at 10 nA.
# Worst corner (n_min x B_max) anchored at run-6 R_max 530 Ohm x <=2 low-n factor -> >=4.7x headroom to soft-clip.
sr1.sensitivity(50e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (5 kOhm FS); sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan-vti electron side: n = +1.80..+3.20e12 (81), D = 0 (run-5 cal), "
                  "B 0.4 -> 6 T uniform-1/B (233), sr1 50 uV, fast_delay 1.8 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron-side D = 0 stacking fan: n = +1.80 to +3.20e12 cm^-2 (81 pts), '
              f'B = 0.4 to 6.0 T uniform-1/B (233 rows, d(1/B) = 0.01006 /T = Nyq/3 on F_L = 33.1 T); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f}; follows spot checks runs 6/7 (light 7.1 + heavy 22.1 T)')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=1, fast_delay=1.8)
finally:
    # park gates; field stays at 6 T (the LK ladder rides it down — no re-traverse)
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end state: B = {magnet.field():+.3f} T, gates ({k_tg.volt():+.3f}, {k_bg.volt():+.3f}) V")
