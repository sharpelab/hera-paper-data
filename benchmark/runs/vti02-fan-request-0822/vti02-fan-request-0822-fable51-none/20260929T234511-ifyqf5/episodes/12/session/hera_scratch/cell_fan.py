# === Landau fan at D = 0 (`landau-fan`): n fast [-1.25, +3.25]e12 (113 pts) x B slow {0, 0.5, 1.0..10.0 @ 0.1 T} (93 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.25, 3.25, 113)            # 1e12 cm^-2, 0.04e12 step, along D = 0
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.asarray(Vtg_vec), np.asarray(Vbg_vec)
_Vt_s, _Vb_s = sanitize_tg_bg(Vtg_vec, Vbg_vec, tg_lims, bg_lims)
assert len(_Vt_s) == len(Vtg_vec), f"{len(Vtg_vec) - len(_Vt_s)} fan points fall outside the gate limits"
assert TG_MIN <= Vtg_vec.min() and Vtg_vec.max() <= TG_MAX and BG_MIN <= Vbg_vec.min() and Vbg_vec.max() <= BG_MAX
print(f"fast axis: n = {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, {n_vec[1]-n_vec[0]:.3f}e12/pt) at D = 0 -> "
      f"Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V; "
      f"roundtrip n,D at the ends: {calc_nD(Vtg_vec[0], Vbg_vec[0], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}, "
      f"{calc_nD(Vtg_vec[-1], Vbg_vec[-1], CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- slow axis: field rows, ascending from 0 (magnet sits there); 0 and 0.5 T = zero-field reference + background
B_vec = np.unique(np.round(np.hstack(([0.0, 0.5], np.arange(1.0, 10.0001, 0.1))), 4))
assert B_vec.max() <= B_SESSION_CAP and len(B_vec) == 93
print(f"slow axis: {len(B_vec)} field rows, {B_vec[0]} .. {B_vec[-1]} T (0.1 T above 1 T)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0

FAST_DELAY, SLOW_DELAY = 1.0, 3.0     # fast: ~3 tau at tau 0.3 s (lag ~1 pt, blur ~0.5 pt); slow: after the blocking ramp + 3 s settle
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA (SdH 50-200 Ohm; R(10 T) ~ 600 Ohm at n = -1.2; CNP column may rail).
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V; "
      f"tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: n fast {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({len(n_vec)} pts) along D = 0 (run-5 cal), "
                  f"B slow 0, 0.5, 1..10 T @ 0.1 T ({len(B_vec)} rows), sr1 100 uV, fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line; n = {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 cm^-2, {len(n_vec)} pts ({n_vec[1]-n_vec[0]:.3f}e12 step); '
              f'(Vtg, Vbg) co-swept {Vtg_vec[0]:+.4f}->{Vtg_vec[-1]:+.4f} V, {Vbg_vec[0]:+.4f}->{Vbg_vec[-1]:+.4f} V; '
              f'B rows 0, 0.5, 1.0..10.0 T @ 0.1 T ascending ({len(B_vec)} rows); '
              f'cal run 5: c_tg {CAL["c_tg"]:.3e}, c_bg {CAL["c_bg"]:.3e} F/m2, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates park at 0; the field stays where the sweep left it (10 T on completion) — the next step rides it down.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
