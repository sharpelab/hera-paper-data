# === Landau fan (`landau-fan`): B slow 0 -> 10 T x (Vtg, Vbg) fast co-swept along D = 0 (run-5 cal), n = -1.26 .. +3.22e12 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = 9.5 nm prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.26, 3.2601, 0.04), 4)                 # 1e12 cm^-2, 0.04 steps (dVtg 11.5 mV, dVbg 14.8 mV per point)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
MARGIN = 0.005                                                        # stay 5 mV inside the validators (the raw grid's last point was 0.8 mV over TG_MAX)
keep = (Vtg_vec >= TG_MIN + MARGIN) & (Vtg_vec <= TG_MAX - MARGIN) & (Vbg_vec >= BG_MIN + MARGIN) & (Vbg_vec <= BG_MAX - MARGIN)
n_vec, Vtg_vec, Vbg_vec = n_vec[keep], Vtg_vec[keep], Vbg_vec[keep]
assert len(n_vec) >= 100
assert TG_MIN <= Vtg_vec.min() and Vtg_vec.max() <= TG_MAX and BG_MIN <= Vbg_vec.min() and Vbg_vec.max() <= BG_MAX, (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_n_chk, _D_chk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_D_chk).max() < 1e-6 and np.allclose(_n_chk, n_vec, atol=1e-6)
print(f"fast axis: {len(n_vec)} pts along D = 0, n = {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f} e12 (0.04 steps); "
      f"Vtg {Vtg_vec.min():+.4f} .. {Vtg_vec.max():+.4f} V, Vbg {Vbg_vec.min():+.4f} .. {Vbg_vec.max():+.4f} V (limits TG [{TG_MIN}, {TG_MAX}], BG [{BG_MIN}, {BG_MAX}])")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"gates now ({k_tg.volt():+.3f}, {k_bg.volt():+.3f}) V")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- slow axis: uniform-B ascending from where the magnet sits: 0 and 0.5 T baseline rows, then 1.0 -> 10.0 T in 0.15 T ---
B_vec = np.unique(np.round(np.hstack(([0.0, 0.5], np.arange(1.0, 10.0001, 0.15))), 4))
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
FAST_DELAY, SLOW_DELAY = 1.0, 5.0      # fast: run-5 calibrated (~1.0 s/pt at tau 0.3 s); slow: flyback settle + 10 tau at each row start
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA. Runs 6/7 features (10-600 Ohm) sit at 0.1-6 % FS;
# the nu = 0 CNP at high B may still rail -- accepted, confined to |n| < ~0.2e12 on the high-B rows (sr0 records the actual current).
sr1.sensitivity(100e-6)
print(f"B grid: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T (0.15 T above 1 T); sr1 sens {sr1.sensitivity()} V (10 kOhm FS), "
      f"sr0 sens {sr0.sensitivity()} V, tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; drive {sr1.amplitude()} V -> 10 nA")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan: B slow 0, 0.5, 1 -> 10 T in 0.15 T ({len(B_vec)} rows) x (Vtg, Vbg) fast co-swept along D = 0, "
                  f"n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f} e12 in 0.04 ({len(n_vec)} pts); run-5 cal; Vsi = 0; sr1 100 uV; fast_delay 1 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm); '
              f'fast (Vtg, Vbg) co-swept hole -> electron, n = {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f} e12 in 0.04e12 ({len(n_vec)} pts); '
              f'slow B = 0, 0.5, 1.0 -> 10.0 T in 0.15 T ({len(B_vec)} rows), ascending; T_sample {_T0:.2f} K; Vsi = 0')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, magnet.field, sr1.X)      # live fan monitor only -- re-form from the TSV for any read

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)       # gates home; the field stays where the fan ended (10 T) -- the next step rides it down
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
