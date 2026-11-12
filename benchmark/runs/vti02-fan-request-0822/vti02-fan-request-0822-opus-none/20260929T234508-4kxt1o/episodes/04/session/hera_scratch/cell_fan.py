# === Step 4: Landau fan (`landau-fan`): B slow x n fast at D = 0, n = -1.20 .. +3.20e12, B 0.8 -> 9.0 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB, luttinger_frequency

# --- session calibration from run 5 (cnp-and-dline-calibration); absolute scale = geometry prior, which THIS run tests ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: 89 densities along D = 0, endpoints == the run 6 / run 7 spot densities ---
n_vec = np.round(np.linspace(-1.20, 3.20, 89), 6)                  # 1e12 cm^-2, step 0.05
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec),
                                      CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
_iC = int(np.argmin(np.abs(n_vec)))
print(f"fast: n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, dn {n_vec[1]-n_vec[0]:.3f}e12) at D = 0; "
      f"Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} (margin {Vtg_vec.min()-TG_MIN:+.4f}/{TG_MAX-Vtg_vec.max():+.4f} V), "
      f"Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f}; CNP col {_iC} -> (Vtg, Vbg) = ({Vtg_vec[_iC]:+.4f}, {Vbg_vec[_iC]:+.4f})")

# --- slow axis: 111 field rows UNIFORM IN 1/B (sdh_fft takes these un-resampled) ---
B_vec = np.round(field_invB(0.8, 9.0, 111), 5)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
_dinv = np.abs(np.diff(1.0 / B_vec)).mean()
print(f"slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {len(B_vec)} rows uniform in 1/B "
      f"(dB {B_vec[1]-B_vec[0]:.4f} .. {B_vec[-1]-B_vec[-2]:.4f} T); "
      f"FFT dF = {1/(1/B_vec[0]-1/B_vec[-1]):.2f} T, F_Nyquist = {1/(2*_dinv):.1f} T; "
      f"F_L(n_max) = {luttinger_frequency(abs(n_vec).max()*1e16):.1f} T")

# --- preconditions (assumed by this cell, NOT set by it) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_nplc_tg, _nplc_bg = k_tg.nplci(), k_bg.nplci()
print(f"precondition T_sample = {_T0:.3f} K (expect 1.0-1.5), B = {_B0:+.4f} T (expect |B| < 0.05: fan ramps in from 0), "
      f"V_si = {k_si():+.3f} V (expect 0), Vtg/Vbg = {k_tg.volt():+.4f}/{k_bg.volt():+.4f} V (expect 0, set below), "
      f"nplc tg/bg = {_nplc_tg}/{_nplc_bg} (expect 1/1: NPLC 10 would add ~1 s/pt = +3 h), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5, _T0
assert abs(_B0) < 0.05, _B0
assert abs(k_si()) < 0.01, k_si()
assert _nplc_tg == 1.0 and _nplc_bg == 1.0, (_nplc_tg, _nplc_bg)
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- sensitivity: 500 uV = 50 kOhm FS at 10 nA. The CNP at 9 T is the map's worst corner and arrives
#     LAST (run-4 lesson); noise is environment- not range-limited here (sigma_V 20 nV @ 100 uV run 5,
#     37 nV @ 50 uV run 6), so headroom is nearly free. First-rows checkpoint verifies sigma_R directly.
sr1.sensitivity(500e-6)
print(f"sr1 sens {sr1.sensitivity()} V (= {sr1.sensitivity()/10e-9/1e3:.0f} kOhm FS at 10 nA), tau {sr1.time_constant()} s / "
      f"{sr1.filter_slope()} dB, sr0 sens {sr0.sensitivity()} V; drive {sr1.amplitude()} V -> I_bias ~ 10 nA")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan: D = 0, n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 x {len(n_vec)}, "
                  f"B {B_vec[0]:.2f}->{B_vec[-1]:.2f} T x {len(B_vec)} rows uniform in 1/B, sr1 500 uV, fast_delay 1.0 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 cut, region-A calibration: fast = (Vtg, Vbg) co-swept over n = {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 cm^-2 '
              f'({len(n_vec)} pts, dn {n_vec[1]-n_vec[0]:.3f}e12); slow = B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T, {len(B_vec)} rows '
              f'uniform in 1/B (dF {1/(1/B_vec[0]-1/B_vec[-1]):.2f} T, F_Nyq {1/(2*_dinv):.1f} T); '
              f'endpoints = run 6 / run 7 spot densities; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; sr1 500 uV (50 kOhm FS), fast_delay 1.0 s')

# park the fast axis at its first point before the sweep opens (Keithley volt.step paces both)
s.ramp(k_bg.volt, float(Vbg_vec[0])); s.ramp(k_tg.volt, float(Vtg_vec[0]))
interruptible_sleep(10)

# row layout (multimegasweep): [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
#                        idx:    0   1    2     3      4          5           6        7      8      9     10
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, magnet.field, sr1.X)          # the fan itself (live monitor only -- re-form from the TSV to read it)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', T_sample); s.plot('time', sr1.P); s.plot('time', sr0.P)

I_TRIP, _strikes = 1e-9, [0]
def leak_guard(station, data):
    # two CONSECUTIVE over-threshold points required: the fast-axis flyback puts a ~200 pA
    # transient on k_tg.curr at every row start (run 5) -- a single spike must not kill 4+ hours.
    assert len(data) == 11, len(data)
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        _strikes[0] += 1
        if _strikes[0] >= 2:
            print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
            station.interrupt_requested = True
    else:
        _strikes[0] = 0
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec],
                 [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=2.0, fast_delay=1.0)

# ends at B = 9 T with the gates at n = +3.20e12 (run 6's electron spot) -- no park here;
# the next step rides the magnet down rather than re-traversing.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
      f"n = {calc_nD(k_tg.volt(), k_bg.volt(), CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])[0]:+.3f}e12")
