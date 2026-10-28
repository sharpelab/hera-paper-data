# === Landau fan at D = 0 (`landau-fan`) — Rxx(n, B), B slow 0 -> 10 T, n fast along the D = 0 line ===
# Plan step 4. Decides the number of independent Fermi surfaces (fan families) and the
# density partition between them — the stacking read that the 1D FFT of runs 6/7 cannot give.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: n along D = 0, hole edge -> electron edge of the realized window ---
n_vec = np.linspace(-1.25, +3.25, 113)                      # 1e12 cm^-2, step 0.0402e12
D_fan = 0.0                                                 # V/nm
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.full_like(n_vec, D_fan),
                                      CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
# validator-equivalent check in-cell (the validators are the backstop; this stops before any hardware moves)
_tg_ok, _bg_ok = sanitize_tg_bg(Vtg_vec, Vbg_vec, tg_lims, bg_lims)
assert len(_tg_ok) == len(Vtg_vec) == len(_bg_ok), (
    f"fast axis leaves the operating box: {len(Vtg_vec) - len(_tg_ok)} of {len(Vtg_vec)} pts dropped")
_nrt, _Drt = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_nrt, n_vec, atol=1e-6) and np.allclose(_Drt, D_fan, atol=1e-6)
print(f"fast axis: n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, dn {n_vec[1]-n_vec[0]:.4f}e12) at D = {D_fan:+.2f} V/nm")
print(f"           Vtg {Vtg_vec[0]:+.4f} .. {Vtg_vec[-1]:+.4f} V (step {Vtg_vec[1]-Vtg_vec[0]:+.4f} V), "
      f"margin to TG limits {Vtg_vec[0]-TG_MIN:+.4f} / {TG_MAX-Vtg_vec[-1]:+.4f} V")
print(f"           Vbg {Vbg_vec[0]:+.4f} .. {Vbg_vec[-1]:+.4f} V (step {Vbg_vec[1]-Vbg_vec[0]:+.4f} V), "
      f"margin to BG limits {Vbg_vec[0]-BG_MIN:+.4f} / {BG_MAX-Vbg_vec[-1]:+.4f} V")

# --- slow axis: field, uniform in B (fan lines are read in (n, B), not 1/B) ---
B_vec = np.round(np.arange(0.0, 10.0001, 0.25), 4)          # 41 rows, 0 -> 10 T
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() >= 0.0
print(f"slow axis: B {B_vec[0]:.2f} .. {B_vec[-1]:.2f} T, {len(B_vec)} rows, dB {B_vec[1]-B_vec[0]:.2f} T "
      f"(ramp floor {(B_vec[-1]-B_vec[0])/0.137:.0f} min)")

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0, _Vsi = T_sample(), magnet.field(), k_si()
_Vtg0, _Vbg0 = k_tg.volt(), k_bg.volt()
print(f"precondition  T_sample = {_T0:.3f} K (exp 1.0-1.5) | B = {_B0:+.4f} T (exp |B| < 0.05, sweep starts at 0) | "
      f"V_si = {_Vsi:+.3f} V (exp 0) | gates ({_Vtg0:+.4f}, {_Vbg0:+.4f}) V | "
      f"PS {magnet.persistent_switch_on()} output {magnet.output_enabled()} (exp True/True) | "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (exp 0/0)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0}"
assert abs(_B0) < 0.05, f"B {_B0} — the fan starts at 0 T"
assert abs(_Vsi) < 0.01, f"V_si {_Vsi}"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "heaters must be off for a base-T fan"

# --- sensitivity: worst-corner sizing (run-4 lesson). R_max over runs 5/6/7 is 3.1 kOhm (gapped CNP at
#     D = +0.3) / 0.59 kOhm (spot at 10 T); the unknown here is the CNP column at 10 T, which can be
#     insulating. 500 uV = 50 kOhm FS at 10 nA. Costs nothing in resolution: the measured point noise is
#     ~27 nV (2.7 Ohm) and is INDEPENDENT of the range (2.59 Ohm at 100 uV run 5, 2.79 Ohm at 50 uV run 6),
#     against 20-100 Ohm pk-pk SdH — so buy the headroom rather than the range.
sr1.sensitivity(500e-6)
_fs_ohm = sr1.sensitivity() / 9.9e-9
print(f"sr1 sens {sr1.sensitivity()} V = {_fs_ohm/1e3:.0f} kOhm FS at 10 nA; tau {sr1.time_constant()} s, "
      f"slope {sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V (I FS {sr0.sensitivity()/1e6*1e9:.1f} nA)")

mc = dict(meas_config); mc["Si (V)"] = _Vsi; mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan at D = {D_fan:+.2f} V/nm (run-5 cal): n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 fast "
                  f"({len(n_vec)} pts), B {B_vec[0]:.2f}..{B_vec[-1]:.2f} T slow ({len(B_vec)} rows, {B_vec[1]-B_vec[0]:.2f} T), "
                  f"sr1 500 uV, fast_delay 1.0 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_fan:+.2f} V/nm line, n fast {n_vec[0]:+.3f} .. {n_vec[-1]:+.3f}e12 cm^-2 in {len(n_vec)} pts '
              f'(Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f}); '
              f'B slow {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T uniform {B_vec[1]-B_vec[0]:.2f} T, {len(B_vec)} rows; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.4e} (9.5 nm geometry prior), '
              f'n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.4f}; sr1 500 uV')

# park on the first fast point before the sweep so row 0 is not measured mid-move
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B_set, Vtg_set, Vbg_set, B_meas, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(magnet.field)          # MEASURED field per point — the setpoint column is not the field (rig card)
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', sr1.P); s.plot('time', sr0.P)
s.plot('time', T_sample); s.plot('time', magnet.field)

# leak guard: 1 nA either gate. Debounced to 2 consecutive points — the gatemap flyback
# charging transient reaches a few hundred pA at a row's first point (session_notes TOOLING),
# and a 3 h fan should not die on one transient sample.
I_TRIP, _trip = 1e-9, {'n': 0}
def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[6])), abs(float(data[7]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        _trip['n'] += 1
        print(f"LEAK {_trip['n']} at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        if _trip['n'] >= 2:
            print("LEAK TRIP (2 consecutive) — interrupting")
            station.interrupt_requested = True
    else:
        _trip['n'] = 0
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=2.0, fast_delay=1.0, init_delay=True)
# ends at 10 T with the gates at the electron edge of the D = 0 line — the next step decides the ride down.
print(f"done: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
      f"T_sample = {T_sample():.3f} K, leak trips = {_trip['n']}")
