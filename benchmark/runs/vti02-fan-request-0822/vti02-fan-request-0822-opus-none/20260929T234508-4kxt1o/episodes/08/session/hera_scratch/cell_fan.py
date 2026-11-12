# === Landau fan (`landau-fan`): B slow, uniform in 1/B 0.7 -> 10 T (110 rows)
#     x (Vtg, Vbg) co-swept along D = 0, n = -1.20 -> +3.20e12 cm^-2 (89 pts) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_FAST, N_ROWS = 89, 110
B_LO, B_HI = 0.7, 10.0
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9

# fast axis: the D = 0 line. Endpoints are EXACTLY the run 7 / run 6 spot settings,
# so the fan's first and last columns reproduce those runs point-for-point.
n_vec = np.linspace(-1.20, 3.20, N_FAST)                       # 1e12 cm^-2, dn = 0.05
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, **CAL)
Vtg_vec, Vbg_vec = sanitize_tg_bg(Vtg_vec, Vbg_vec, tg_lims, bg_lims)
assert len(Vtg_vec) == N_FAST and len(Vbg_vec) == N_FAST, (len(Vtg_vec), len(Vbg_vec))

# slow axis: uniform in 1/B -> sdh_fft FFTs each column directly, no resample.
B_vec = field_invB(B_LO, B_HI, N_ROWS)
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
_dinv = abs(np.diff(1.0 / B_vec)[0])
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({N_FAST} pts, dn {n_vec[1]-n_vec[0]:.3f}e12) at D = 0; "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V")
print(f"slow: B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T, {N_ROWS} rows uniform in 1/B (d(1/B) = {_dinv:.5f} /T); "
      f"dF = {1/(1/B_LO - 1/B_HI):.2f} T, F_Nyquist = {1/(2*_dinv):.1f} T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at {B_LO} T), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"gates now (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, "
      f"volt.step tg/bg = {k_tg.volt.step}/{k_bg.volt.step} V")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# Fixed sensitivity for the whole fan (no autorange mid-row): 200 uV = 20 kOhm FS at 9.9 nA.
# Runs 6/7 peaked at 530/587 Ohm (10.5 % of the 50 uV scale) with 241 Ohm pk-pk oscillations,
# so 20 kOhm is ~34x the largest R seen and ~60x the B = 0 D = 0 CNP peak (<=330 Ohm, run 5):
# headroom for the CNP column at 10 T, and quantisation is irrelevant at this oscillation size.
sr1.sensitivity(200e-6)
print(f"drive {sr1.amplitude()} V -> ~9.9 nA; sr1 sens {sr1.sensitivity()} V (20 kOhm FS), "
      f"tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan: B slow {B_LO} -> {B_HI} T, {N_ROWS} rows uniform in 1/B; "
                  f"(Vtg, Vbg) fast along D = 0, n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({N_FAST} pts); "
                  f"Vsi = 0, sr1 200 uV, fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: slow B {B_LO} -> {B_HI} T, {N_ROWS} rows uniform in 1/B (dF {1/(1/B_LO-1/B_HI):.2f} T, '
              f'F_Nyq {1/(2*_dinv):.1f} T); fast (k_tg.volt, k_bg.volt) co-swept along D = 0, '
              f'n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2, {N_FAST} pts (dn 0.05e12); '
              f'endpoint columns == run 7 (n -1.20) and run 6 (n +3.20) spot settings; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')

s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', T_sample); s.plot('time', sr1.P); s.plot('time', sr0.P)

_RAIL = 0.95 * sr1.sensitivity()
_flags = {"rail": 0}

def fan_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[9])) > _RAIL:
        _flags["rail"] += 1
        if _flags["rail"] in (1, 10, 100, 1000):
            print(f"RAIL sr1 (>{_RAIL:.2e} V) at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f} "
                  f"(count {_flags['rail']}) - not fatal, logged")

s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"parked gates: (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V; "
          f"B = {magnet.field():+.3f} T (left high for the D-dependence step); rail samples {_flags['rail']}")
