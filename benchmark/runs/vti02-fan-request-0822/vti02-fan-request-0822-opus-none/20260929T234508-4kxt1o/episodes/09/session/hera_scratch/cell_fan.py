# === Landau fan at D = 0 (`landau-fan`): n fast (-1.20 -> +3.20e12, 221 pts), B slow (1.5 -> 10 T, 50 rows uniform in 1/B) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = 9.5 nm geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: density along D = 0 (co-swept gates) ---
N_STEP = 0.02                                        # 1e12 cm^-2 per point
n_vec = np.round(np.arange(-1.20, 3.2001, N_STEP), 4)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
_n_rt, _D_rt = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_n_rt, n_vec) and np.allclose(_D_rt, 0.0, atol=1e-9), "n,D roundtrip failed"
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e12 at D = 0, {len(n_vec)} pts ({N_STEP:.3f}e12, "
      f"{np.diff(Vtg_vec)[0]*1e3:.2f} mV TG/pt); Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f} V")

# --- slow axis: 50 field rows uniform in 1/B, ascending (magnet sits at 0 T -> no wasted traverse) ---
B_vec = field_invB(1.5, 10.0, 50)
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
_dinv = abs(np.diff(1.0 / B_vec)[0])
print(f"slow: {len(B_vec)} rows {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {_dinv:.5f} 1/T "
      f"(Nyquist F = {1/(2*_dinv):.1f} T); {len(n_vec)*len(B_vec)} points total")

FAST_DELAY, SLOW_DELAY = 0.8, 5.0     # 0.8 s = 2.7 tau: stated bend, see markdown (13 % amplitude / 1.2-pt lag at the worst row)
I_TRIP, TRIP_STRIKES = 1e-9, 2        # two consecutive points over 1 nA (run-5 flyback reached +-200 pA)

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan ramps up from 0), "
      f"V_tg = {k_tg.volt():+.4f} V (0), V_bg = {k_bg.volt():+.4f} V (0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert abs(k_tg.volt()) < 0.01 and abs(k_bg.volt()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- fixed sensitivity for the whole fan (no autorange mid-row): 200 uV = 20 kOhm FS at 10 nA ---
sr1.sensitivity(200e-6)
print(f"drive {sr1.amplitude()} V / 100 MOhm -> 10 nA; sr1 sens {sr1.sensitivity()} V (20 kOhm FS), "
      f"tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB (fast_delay {FAST_DELAY} s = {FAST_DELAY/sr1.time_constant():.1f} tau); "
      f"sr0 sens {sr0.sensitivity()} V, tau {sr0.time_constant()} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan D = 0: n fast -1.20..+3.20e12 (221 pts, 0.02e12), B slow 1.5..10.0 T "
                  "(50 rows uniform in 1/B), run-5 cal, sr1 200 uV, fast_delay 0.8 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: fast = (Vtg, Vbg) co-swept along D = 0, n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2 '
              f'({len(n_vec)} pts, {N_STEP:.3f}e12); slow = B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {len(B_vec)} rows uniform in 1/B; '
              f'T = base; Vsi = 0; sr1 200 uV (20 kOhm FS); fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.4e} F/m^2 (9.5 nm prior), '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm')

s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow set), Vtg(fast), Vbg(fast), B_meas, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(magnet.field).fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
I_TG, I_BG, NCOL = 6, 7, 12
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample); s.plot('time', magnet.field)

_strikes = [0]
def leak_guard(station, data):
    assert len(data) == NCOL, f"row layout changed ({len(data)} cols, expected {NCOL}) - leak guard indices invalid"
    i_tg, i_bg = abs(float(data[I_TG])), abs(float(data[I_BG]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        _strikes[0] += 1
        print(f"LEAK strike {_strikes[0]}/{TRIP_STRIKES} at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        if _strikes[0] >= TRIP_STRIKES:
            print("LEAK TRIP - interrupting")
            station.interrupt_requested = True
    else:
        _strikes[0] = 0
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
