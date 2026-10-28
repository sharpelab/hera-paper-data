# === Landau fan (`landau-fan`): D = 0 line (region-A cal), n fast [-1.24, +3.21]e12 x 179 (0.025), B slow 0 T + 0.6 -> 10.0 T (0.2 T, 49 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration): ratio data-calibrated, ABSOLUTE SCALE = 9.5 nm geometry prior.
# Run 6's high-B tone (29.5 T vs F_L(3.2e12) = 33.1 T) says the scale is likely ~11 % high; the fan-line slopes measure it.
# n labels below are raw-cal; the D = 0 line direction depends only on the ratio + D_offset, so the line itself is right.
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.24, 3.2201, 0.025), 4)          # 1e12 cm^-2 raw cal, 179 pts; TG-limited both ends (~10 mV margin)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
_vt, _vb = sanitize_tg_bg(Vtg_vec, Vbg_vec, tg_lims, bg_lims)
assert len(_vt) == len(Vtg_vec), f"{len(Vtg_vec) - len(_vt)} fast points fall outside the validators"
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
print(f"fast axis: n {n_vec[0]:+.3f} .. {n_vec[-1]:+.3f}e12 ({len(n_vec)} pts, 0.025) along D = 0 -> "
      f"Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V; "
      f"roundtrip D at ends = {calc_nD(Vtg_vec[0], Vbg_vec[0], **CAL)[1]:+.4f}, {calc_nD(Vtg_vec[-1], Vbg_vec[-1], **CAL)[1]:+.4f} V/nm")

# --- field grid: B = 0 baseline row, then 0.6 -> 10.0 T at 0.2 T. Blocking magnet: start where it sits (0 T), end at the cap.
B_vec = np.unique(np.round(np.hstack(([0.0], np.arange(0.6, 10.0001, 0.2))), 4))
assert B_vec.min() >= 0 and B_vec.max() <= B_SESSION_CAP
FAST_DELAY, SLOW_DELAY = 1.0, 3.0     # fast 1.0 s = 3.3 tau at 0.3 s / 24 dB (run-5 calibrated: uniform ~1-pt lag along n)
I_TRIP = 1e-9

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA. Run 5 read 60 Ohm..2.4 kOhm cleanly at this setting;
# the CNP at high B may soft-clip above 10 kOhm -- a localized, informative rail (insulating nu = 0), not a fault.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V; "
      f"tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0 (run-5 cal): n fast {n_vec[0]:+.3f}..{n_vec[-1]:+.3f}e12 x {len(n_vec)} (0.025), "
                  f"B slow 0 + 0.6..10 T x {len(B_vec)} (0.2 T), sr1 100 uV, fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line (region-A cal, run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm); '
              f'n fast [{n_vec[0]:+.3f}, {n_vec[-1]:+.3f}]e12 {len(n_vec)} pts (0.025e12; Vtg {Vtg_vec.min():+.3f}..{Vtg_vec.max():+.3f}, '
              f'Vbg {Vbg_vec.min():+.3f}..{Vbg_vec.max():+.3f} V); B slow 0 T then 0.6 -> 10.0 T at 0.2 T ({len(B_vec)} rows); '
              f'Vsi = 0; T = {_T0:.2f} K; sr1 100 uV; n labels raw-cal (scale check pending from fan slopes)')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
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
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)     # gates parked at 0; field stays where the sweep ended (the next step rides it down)
print(f"done: B = {magnet.field():+.3f} T (held), gates parked (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
