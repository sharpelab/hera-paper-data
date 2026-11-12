# === Landau fan, electron side at D = 0 (`landau-fan-vti`): n = +0.6 -> +3.2e12 (66 cols, 0.04 step) x B 0.65 -> 10 T uniform-1/B (190 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0                                                    # V/nm
ns = np.round(np.arange(0.60, 3.2001, 0.04), 3)             # 1e12 cm^-2, ascending along each row
Vtgs, Vbgs = calc_gate_voltages(ns, np.full_like(ns, D0), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert len(ns) == 66 and Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
_n_chk, _D_chk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_n_chk - ns).max() < 1e-6 and np.abs(_D_chk - D0).max() < 1e-6
print(f"fast axis: n = {ns[0]:+.2f} .. {ns[-1]:+.2f}e12 ({len(ns)} pts, 0.04 step) at D = {D0:+.2f} V/nm -> "
      f"Vtg {Vtgs[0]:+.4f} .. {Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f} .. {Vbgs[-1]:+.4f} V")

# --- slow axis: uniform in 1/B, ascending, start where the magnet sits (0 T) ---
B_vec = field_invB(0.65, 10.0, 190)                        # d(1/B) = 0.00761 1/T = Nyquist at 66 T = 2 F_L(n_max)
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"slow axis: {len(B_vec)} rows, B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {abs(1/B_vec[1]-1/B_vec[0]):.5f} 1/T, "
      f"dB first/last = {1e3*(B_vec[1]-B_vec[0]):.1f} mT / {B_vec[-1]-B_vec[-2]:.3f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0.65 T from 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 1.8, 1.0        # 6 tau at tau = 0.3 s / 24 dB; slow_delay on top of the driver's 3 s magnet settle
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange): 100 uV = 10 kOhm FS at 10 nA, sized for the n = 0.6 x 10 T corner.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB; "
      f"sr0 sens {sr0.sensitivity()} V; magnet settle_s {magnet.settle_s} s; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = {D0:+.2f} V/nm, n = {ns[0]:+.2f} .. {ns[-1]:+.2f}e12 ({len(ns)} cols), "
                  f"B {B_vec[0]:.2f} -> {B_vec[-1]:.1f} T uniform-1/B ({len(B_vec)} rows), sr1 100 uV, fast_delay {FAST_DELAY}; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 cm^-2 ({len(ns)} pts, 0.04 step), '
              f'B = {B_vec[0]:.2f} to {B_vec[-1]:.1f} T uniform-1/B ({len(B_vec)} rows, d(1/B) = 0.00761 1/T); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'follows sdh-spot-check runs 6 (electron) / 7 (hole)')

# position gates at the row start, then the magnet at B_lo (blocking ramp, ~5 min from 0 T)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
magnet.field(float(B_vec[0]))
print(f"positioned: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V")
interruptible_sleep(10)

# row layout: [time, magnet_field(slow), k_tg_volt, k_bg_volt (fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    # field is left where the fan ends (10 T on completion) — the next step's decision, never restored blind.
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
