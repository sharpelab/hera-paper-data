# === Step 4 precursor: low-field onset extension (`sdh-spot-check`) — n = +3.2e12, D = 0, B 0.40 -> 1.05 T ===
# Pins the landau-fan B_lo. Run 6's onset_b is censored at the low edge of its well-sampled record
# (1.0 T) and its sub-1 T leg was taken at 50 mT -> d(1/B) ~ 0.5 1/T, aliased for every tone in play.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run 5 (cnp-and-dline-calibration)
n_spot, D_spot = 3.2, 0.0                       # 1e12 cm^-2, V/nm — same spot as run 6
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V "
      f"(run 6 used +0.9836, +1.1661)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"V_tg/V_bg = {k_tg.volt():+.4f}/{k_bg.volt():+.4f} V, tau sr0/sr1 = {sr0.time_constant()}/{sr1.time_constant()} s, "
      f"slope sr0/sr1 = {sr0.filter_slope()}/{sr1.filter_slope()} dB/oct")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert sr1.filter_slope() <= 24 and sr0.filter_slope() <= 24, "settling floor priced at 4-pole; re-price if steeper"

# --- grid: uniform in 1/B, d(1/B) = 0.0101 1/T = run 6's spacing at its 1 T low edge
#     (Nyquist ceiling 50 T, vs F_L = 33.1 T at this density and a tracked tone set topping out at 29.4 T).
B_vec = field_invB(0.40, 1.05, 154)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
I_TRIP = 1e-9
# Sensitivity 20 uV = 808 Ohm full scale at 9.9 nA. R over this window is 8-57 Ohm (measured, run 6)
# -> 7 % FS, 14x rail headroom; run 6's 50 uV put it at 1.1 % FS (digitization-limited) and the onset
# is exactly what this cell measures. tau left at the operator's 0.3 s: delay=0 means the dwell is the
# magnet's blocking ramp + 3 s settle = 10 tau.
sr1.sensitivity(20e-6)
print(f"B grid: {len(B_vec)} pts, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T; d(1/B) = {np.abs(np.diff(1/B_vec)).max():.5f} 1/T "
      f"(Nyquist {1/(2*np.abs(np.diff(1/B_vec)).max()):.0f} T); dB {np.diff(B_vec)[0]*1e3:.1f} -> {np.diff(B_vec)[-1]*1e3:.1f} mT; "
      f"sr1 sens {sr1.sensitivity()} V ({sr1.sensitivity()/(sr1.amplitude()/100e6):.0f} Ohm FS), sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"sdh-spot-check low-field onset extension, electron: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm "
                  f"(run-5 cal), (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0.40 -> 1.05 T uniform-1/B "
                  f"d(1/B) = 0.0101, sr1 20 uV; pins landau-fan B_lo (run 6 onset censored at 1.0 T)")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'low-field onset extension, electron side: n = {n_spot:+.2f}e12 cm^-2, D = {D_spot:+.2f} V/nm; '
              f'(Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B 0.40 -> 1.05 T uniform-1/B, d(1/B) = 0.0101 1/T, 154 pts; '
              f'sr1 sens 20 uV; extends run 6 below its well-sampled edge to pin the landau-fan B_lo; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_spot); s.ramp(k_tg.volt, Vtg_spot)
interruptible_sleep(10)

# row layout: [time, B, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
_FP = ['T_sample', 'k_2400_tg_curr', 'k_2400_bg_curr', 'sr0_X', 'sr0_P', 'sr1_X', 'sr1_P']
assert list(s._col_names()) == _FP, s._col_names()
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[3])), abs(float(data[4]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.sweep(magnet.field, B_vec, delay=0)
# gates stay at the spot, field stays at 1.05 T — the fan re-uses both (it ramps to its B_lo from here).
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
      f"T_sample = {T_sample():.3f} K")
