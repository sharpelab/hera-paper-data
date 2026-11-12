# === Landau fan at D = 0 (`landau-fan`): n fast along the calibrated D = 0 line x B slow 0.4 -> 10 T (plan step 4) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.25, 3.25, 131)            # 1e12 cm^-2, dn = 0.035e12 (~10 mV TG); TG-limited both ends
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.asarray(Vtg_vec), np.asarray(Vbg_vec)
MARGIN = 0.002
assert Vtg_vec.min() >= TG_MIN + MARGIN and Vtg_vec.max() <= TG_MAX - MARGIN, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN + MARGIN and Vbg_vec.max() <= BG_MAX - MARGIN, (Vbg_vec.min(), Vbg_vec.max())
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(np.asarray(_Dchk)).max() < 1e-6
print(f"fast axis: {len(n_vec)} pts, n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 at D = 0; "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V ({(Vtg_vec[1]-Vtg_vec[0])*1e3:.1f} mV), Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V")

# --- field rows: uniform in B (LL lines are straight in (n, B)); blocking magnet, start where it sits (0 T) ---
B_vec = np.round(np.arange(0.4, 10.0001, 0.2), 3)   # 49 rows
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
FAST_DELAY, SLOW_DELAY = 1.0, 3.0                    # run-5 pacing: 1.10 s/pt measured; lag <~ 1 step, uniform per row
I_TRIP, T_TRIP = 1e-9, 2.0                           # A, K — guards (no operator eyes in E1)

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left it at 0), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA (run-5 map read 50 Ohm features at this range;
# the nu = 0 state at high B may exceed it -> flat top at the CNP only, accepted).
sr1.sensitivity(100e-6)
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS), sr0 sens {sr0.sensitivity()} V, tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; "
      f"drive {sr1.amplitude()} V -> {sr1.amplitude()/100e6*1e9:.1f} nA; magnet settle_s {magnet.settle_s} s")
print(f"price: {len(B_vec)} rows x {len(n_vec)} pts x 1.10 s + 10 T / 0.134 T/min + {len(B_vec)} x ~10 s -> "
      f"~{(len(B_vec)*len(n_vec)*1.10 + 10/0.134*60 + len(B_vec)*10)/3600:.2f} h")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, run-5 cal) fast x B {B_vec[0]}..{B_vec[-1]} T "
                  f"({len(B_vec)} rows, 0.2 T) slow; sr1 100 uV; fast_delay 1 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.3e} F/m2 prior-anchored, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm); fast (Vtg, Vbg) co-swept: '
              f'n = {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12, {len(n_vec)} pts (dn {n_vec[1]-n_vec[0]:.4f}e12); '
              f'slow B = {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows (0.2 T); Vsi = 0; T ~ 1.2 K; sr1 sens 100 uV')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def fan_guard(station, data):
    t_s, i_tg, i_bg = float(data[4]), abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if t_s > T_TRIP:
        print(f"T TRIP at B={float(data[1]):+.3f} T: T_sample = {t_s:.3f} K > {T_TRIP} K")
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# field stays at 10 T (the next step rides it down); gates left where the sweep ends — readback:
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
