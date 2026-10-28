# === Landau fan at D = 0 (`landau-fan`): n fast along the calibrated D = 0 line, B slow 0.5 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = 9.5 nm prior;
#     runs 6/7 say the scale runs ~10-13 % high — the fan's LL indexing recalibrates it, so n here is "n_geo") ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.25, 3.2001, 0.025), 4)          # 1e12 cm^-2, 179 pts, D = 0
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.asarray(Vtg_vec, float), np.asarray(Vbg_vec, float)
MARGIN = 0.005   # V — every point strictly inside the committed validators (a throw mid-fan would abort the run)
assert Vtg_vec.min() >= TG_MIN + MARGIN and Vtg_vec.max() <= TG_MAX - MARGIN, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN + MARGIN and Vbg_vec.max() <= BG_MAX - MARGIN, (Vbg_vec.min(), Vbg_vec.max())
assert len(Vtg_vec) == len(Vbg_vec) == len(n_vec)
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(np.asarray(_Dchk)).max() < 1e-6 and np.abs(np.asarray(_nchk) - n_vec).max() < 1e-6
print(f"fast axis: n_geo {n_vec[0]:+.3f} .. {n_vec[-1]:+.3f}e12 ({len(n_vec)} pts, 0.025 step) at D = 0 -> "
      f"Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}] V, Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}] V "
      f"(validators TG [{TG_MIN}, {TG_MAX}], BG [{BG_MIN}, {BG_MAX}])")

# --- slow axis: uniform-B rows, denser where the fan converges ---
B_vec = np.unique(np.round(np.hstack((np.arange(0.5, 4.0001, 0.1), np.arange(4.2, 10.0001, 0.2))), 3))   # 66 rows, climbing
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
print(f"slow axis: B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows (0.1 T to 4 T, 0.2 T above)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: fan climbs from 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- lock-in settling: tau 0.3 -> 0.1 s on both lock-ins so fast_delay 1.0 s = 10 tau (24 dB/oct settles to 1 % in ~10 tau);
#     at tau 0.3 s the same dwell leaves ~half of each step unsettled and smears LL minima over ~3 fast points.
#     Acquisition setting, not a safety surface; state0 (close-out restore) holds the operator's 0.3 s.
print(f"tau before: sr0 {sr0.time_constant()} s, sr1 {sr1.time_constant()} s; slope sr1 {sr1.filter_slope()} dB/oct")
sr0.time_constant(0.1); sr1.time_constant(0.1)
# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm FS at 10 nA; CNP at high B may rail (that is a read).
sr1.sensitivity(100e-6)
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9
print(f"tau after: sr0 {sr0.time_constant()} s, sr1 {sr1.time_constant()} s; drive {sr1.amplitude()} V -> 10 nA; "
      f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V; fast_delay {FAST_DELAY} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: n_geo fast {n_vec[0]:+.3f}..{n_vec[-1]:+.3f}e12 ({len(n_vec)} pts) along D = 0 (run-5 cal), "
                  f"B slow {B_vec[0]}->{B_vec[-1]} T ({len(B_vec)} rows: 0.1 T to 4 T, 0.2 T above), Vsi = 0, sr1 100 uV, tau 0.1 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e} prior anchor, n_offset {CAL["n_offset"]:+.4f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f} V/nm); fast (Vtg, Vbg) co-swept, n_geo {n_vec[0]:+.3f}..{n_vec[-1]:+.3f}e12 step 0.025 ({len(n_vec)} pts); '
              f'slow B {B_vec[0]}..{B_vec[-1]} T, {len(B_vec)} rows; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; tau 0.1 s; sr1 100 uV')

# park the gates at the row start, then climb to the first field row (both blocking)
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(5)
s.ramp(magnet.field, B_vec[0])
interruptible_sleep(5)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY, init_delay=False)
# field stays at 10 T (the next step rides it down), gates stay at the last fast point — no park here.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
