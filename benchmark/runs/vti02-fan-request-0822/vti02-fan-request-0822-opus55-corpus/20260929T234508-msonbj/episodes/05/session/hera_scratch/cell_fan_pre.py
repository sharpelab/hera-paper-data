# === Fan step A — low-field onset extension at the fan's top density (`sdh-spot-check`): n = +3.2e12, D = 0, B 0.30 -> 1.0 T uniform in 1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
# --- session calibration, run 5 (cnp-and-dline-calibration): ratio data-calibrated, scale = geometry prior ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
# Shared 1/B lattice with the fan (step B): 1/B = 0.1 + k*DINVB, DINVB = 0.9/101 T^-1 (Nyquist 56 T = 3 pts/period on the
# fastest observed fundamental, ~37 T in run 6). k = 362..102 -> B 0.3007 -> 0.9912 T (261 pts); the fan continues at k = 101 (1.0 T).
DINVB = 0.9 / 101
B_pre = 1.0 / (0.1 + np.arange(362, 101, -1) * DINVB)
assert np.all(np.diff(B_pre) > 0) and B_pre.max() < 1.01 and B_pre.min() > 0.3
n_top, D0 = 3.2, 0.0
Vtg_top, Vbg_top = calc_gate_voltages(n_top, D0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_top <= TG_MAX and BG_MIN <= Vbg_top <= BG_MAX, (Vtg_top, Vbg_top)
print(f"spot: n = {n_top:+.2f}e12, D = {D0:+.2f} -> (Vtg, Vbg) = ({Vtg_top:+.4f}, {Vbg_top:+.4f}) V (same point as run 6)")
# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0, _Vsi = T_sample(), magnet.field(), k_si()
_hs, _hv = heater.sample_range(), heater.vaporizer_range()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05, handoff left 0 T), V_si = {_Vsi:+.3f} V (0), "
      f"heater ranges {_hs}/{_hv} (0/0), PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(_Vsi) < 0.01 and _hs == 0 and _hv == 0
assert magnet.persistent_switch_on() and magnet.output_enabled() and k_tg.nplci() == 1 and k_bg.nplci() == 1
print(f"lock-in: tau sr0/sr1 = {sr0.time_constant()}/{sr1.time_constant()} s, slope {sr0.filter_slope()}/{sr1.filter_slope()} dB (0.3 s / 24 dB), drive {sr1.amplitude()} V")
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24 and sr0.time_constant() == 0.3 and abs(sr1.amplitude() - 1.0) < 1e-6
# Fixed sensitivity 50 uV = 5 kOhm FS at 10 nA — identical to run 6, so this record differs from run 6 only in its grid
# (uniform-1/B vs uniform-B): the grid-change reproduction check. R(B <= 1 T) <= 60 Ohm at this n (run 6).
sr1.sensitivity(50e-6)
I_TRIP, T_TRIP = 1e-9, 1.7
mc = dict(meas_config); mc["Si (V)"] = _Vsi; mc["sample_temperature:"] = _T0
mc["comments"] = (f"fan step A, low-field onset extension: n = {n_top:+.2f}e12, D = 0 (run-5 cal), (Vtg, Vbg) = ({Vtg_top:+.4f}, {Vbg_top:+.4f}), "
                  f"B 0.3007 -> 0.9912 T uniform 1/B (DINVB = 0.9/101, shared lattice with the fan), sr1 50 uV")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'fan step A (onset pin for landau-fan-vti B_lo): electron n = {n_top:+.2f}e12 cm^-2, D = 0 V/nm; (Vtg, Vbg) = ({Vtg_top:+.4f}, {Vbg_top:+.4f}); '
              f'B 0.3007 -> 0.9912 T, 261 pts uniform in 1/B, DINVB = {DINVB:.6f} 1/T; cal run 5: ratio 0.773, n_offset -0.089e12, D_offset -0.013 V/nm')
s.ramp(k_bg.volt, Vbg_top); s.ramp(k_tg.volt, Vtg_top)
interruptible_sleep(10)
# row layout: [time, B, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X); s.plot(magnet.field, sr1.P); s.plot(magnet.field, sr0.P)
s.plot('time', T_sample); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
def guard(station, data):
    T, i_tg, i_bg = float(data[2]), abs(float(data[3])), abs(float(data[4]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.4f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A"); station.interrupt_requested = True
    if T > T_TRIP:
        print(f"T TRIP at B={float(data[1]):+.4f} T: T_sample = {T:.3f} K > {T_TRIP} K"); station.interrupt_requested = True
s.register_run_after(guard, ())
s.sweep(magnet.field, B_pre, delay=0)
# gates stay at the spot, field stays at 0.9912 T: the fan (step B) starts here.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
