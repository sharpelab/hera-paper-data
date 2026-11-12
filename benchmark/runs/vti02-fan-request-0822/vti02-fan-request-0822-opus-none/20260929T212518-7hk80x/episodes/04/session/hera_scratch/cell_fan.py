# === Landau fan (`landau-fan`): D = 0, n = -1.20 -> +3.20e12 cm^-2, B 1 -> 10 T uniform in 1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration); same CAL as runs 6/7 ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_FAST, N_ROWS = 177, 71
n_vec = np.linspace(-1.20, 3.20, N_FAST)                       # 1e12 cm^-2, fast axis, D = 0
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
B_vec = field_invB(1.0, 10.0, N_ROWS)                          # slow axis, ascending, uniform in 1/B

assert len(Vtg_vec) == len(Vbg_vec) == N_FAST
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
_n_rt, _D_rt = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_D_rt).max() < 1e-9, _D_rt
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 cm^-2 (dn {np.diff(n_vec)[0]*1e3:.0f}e9), D = 0; "
      f"Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V (margin {Vtg_vec.min()-TG_MIN:+.3f}/{TG_MAX-Vtg_vec.max():+.3f}), "
      f"Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V")
print(f"slow: B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T, {N_ROWS} rows uniform in 1/B "
      f"(d(1/B) = {np.diff(1/B_vec[::-1])[0]:.5f} -> F_Nyquist {1/(2*abs(np.diff(1/B_vec))).min():.1f} T, "
      f"dF = {1/(1/B_vec.min() - 1/B_vec.max()):.2f} T); dB/row {np.diff(B_vec).min()*1e3:.0f}..{np.diff(B_vec).max()*1e3:.0f} mT")

# --- preconditions (assumed by this cell, not set by it) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: fan starts at 1 T), "
      f"V_si = {k_si():+.3f} V (0), V_tg = {k_tg.volt():+.4f}, V_bg = {k_bg.volt():+.4f} V, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS {magnet.persistent_switch_on()}, out {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"

# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm FS at 10 nA.
SENS, I_TRIP = 100e-6, 1e-9
sr1.sensitivity(SENS)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s "
      f"@ {sr1.filter_slope()} dB/oct; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan: D = 0, n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({N_FAST} pts) fast, "
                  f"B {B_vec[0]:.1f}..{B_vec[-1]:.1f} T uniform-1/B ({N_ROWS} rows) slow, sr1 100 uV, fast_delay 1.0 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line; fast (Vtg, Vbg) co-swept over n = {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2, '
              f'{N_FAST} pts (dn = 25e9); slow B = {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T, {N_ROWS} rows uniform in 1/B '
              f'(F_Nyquist 38.9 T, dF 1.11 T); sr1 sens 100 uV (10 kOhm FS); fast_delay 1.0 s, slow_delay 3.0 s; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')

s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_clip = {'n': 0}
def guards(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[9])) > 0.9 * SENS:
        _clip['n'] += 1
        if _clip['n'] in (1, 10, 100, 1000, 5000):
            print(f"CLIP #{_clip['n']}: |sr1.X| = {abs(float(data[9])):.3e} V > 0.9 FS at "
                  f"B = {float(data[1]):+.3f} T, Vtg = {float(data[2]):+.4f} V")
s.register_run_after(guards, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=3.0, fast_delay=1.0)
finally:
    # gates park at 0; the field stays where the fan ended (10 T) for the step-5 ride-down.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
          f"T_sample = {T_sample():.3f} K, clipped points = {_clip['n']}")
