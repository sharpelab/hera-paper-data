# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +1.00 -> +3.24e12 (49 pts) x B 1 -> 10 T uniform-1/B (121 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0                                          # V/nm
n_vec = np.linspace(1.00, 3.24, 49)               # 1e12 cm^-2, ascending each row; dn = 0.0467e12
Vtgs, Vbgs = calc_gate_voltages(n_vec, np.full_like(n_vec, D0), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtgs, Vbgs = np.asarray(Vtgs, float), np.asarray(Vbgs, float)
assert Vtgs.min() >= TG_MIN and Vtgs.max() <= TG_MAX and Vbgs.min() >= BG_MIN and Vbgs.max() <= BG_MAX, (Vtgs.min(), Vtgs.max(), Vbgs.min(), Vbgs.max())
_nchk, _Dchk = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_nchk, n_vec, atol=1e-6) and np.allclose(_Dchk, D0, atol=1e-6)
print(f"fast axis: n = {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, dn {n_vec[1]-n_vec[0]:.4f}e12) at D = {D0:+.2f} V/nm -> "
      f"Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f} V, Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f} V (limits TG [{TG_MIN},{TG_MAX}], BG [{BG_MIN},{BG_MAX}])")

# --- slow axis: uniform in 1/B (per-column SdH-FFT fan). B_lo = sdh_onset(run 6, B >= 1 T).onset_b = 1.00 T (censored -> lower bound).
B_LO, B_HI, DINVB = 1.0, 10.0, 0.0075             # T, T, 1/T
N_B = int(round((1 / B_LO - 1 / B_HI) / DINVB)) + 1
B_vec = 1.0 / np.linspace(1 / B_LO, 1 / B_HI, N_B)   # == field_invB(B_LO, B_HI, N_B); ascending: starts where the magnet will sit
assert N_B == 121 and np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP
F_L = n_vec * 1e16 * cst.h / (4 * cst.e)          # Luttinger frequency per column, T
nyq = 1 / (2 * DINVB); dn_ray = 4 * cst.e / cst.h * B_LO / 1e16
print(f"slow axis: {N_B} rows, B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T uniform-1/B, d(1/B) {DINVB} 1/T; dB {B_vec[1]-B_vec[0]:.4f} T at 1 T, {B_vec[-1]-B_vec[-2]:.3f} T at 10 T")
print(f"design checks: F_L {F_L.min():.1f}..{F_L.max():.1f} T; Nyquist {nyq:.1f} T = {nyq/F_L.max():.2f} F_L(n_max) [rule: >= 1, prefer 1.5]; "
      f"ray spacing at {B_LO} T {dn_ray:.4f}e12 -> {dn_ray/(n_vec[1]-n_vec[0]):.2f} pts/ray [floor 2]; dF {1/(1/B_LO-1/B_HI):.2f} T; "
      f">=5-period partner window f >= {5/(1/B_LO-1/B_HI):.1f} T")

FAST_DELAY, SLOW_DELAY = 1.5, 1.0                 # 5 tau (tau 0.3 s, 24 dB/oct); slow_delay on top of the driver's 3 s field settle
I_TRIP = 1e-9
t_est = N_B * (len(n_vec) * 1.6 + 6.5) + (B_HI - B_LO) / 0.137 * 60 + B_LO / 0.137 * 60
print(f"cost model: {N_B} x ({len(n_vec)} x 1.6 s + 6.5 s) + traverse + positioning = {t_est/3600:.2f} h computed (run 5: 1.10 s/pt @ fast_delay 1.0; run 6: +3.1 s/pt field overhead)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: handoff left 0 T; the cell positions to {B_LO} T itself), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1 (per-point time)"

# --- lock-in: fixed sensitivity for the whole fan (dynamic-range corner n = 1.0 x 10 T; see markdown). 100 uV = 10 kOhm FS at 10 nA.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: D = {D0:+.2f} V/nm, n = {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts) fast, "
                  f"B {B_LO} -> {B_HI} T uniform-1/B ({N_B} rows, d(1/B) {DINVB}) slow; fast_delay {FAST_DELAY}, slow_delay {SLOW_DELAY}; sr1 100 uV; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = {D0:+.2f} V/nm, n = {n_vec[0]:+.2f} to {n_vec[-1]:+.2f}e12 cm^-2 ({len(n_vec)} pts, electron side), '
              f'B = {B_LO} to {B_HI} T uniform-1/B ({N_B} rows, d(1/B) = {DINVB} 1/T); Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f}; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; B_lo from sdh_onset(run 6) = 1.00 T censored')

# gates to the first fast point, then position the magnet at the fan start (blocking ramp, ~7 min from 0 T; the set call is the settle)
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
print(f"positioning magnet {magnet.field():+.3f} -> {B_LO} T ...", flush=True)
magnet.field(B_LO)
print(f"at B = {magnet.field():+.4f} T, gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample {T_sample():.3f} K", flush=True)
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot(magnet.field, sr1.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_rail = {"n": 0}
def guards(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if abs(float(data[9])) > 0.95 * 100e-6:      # sr1 near full scale: flag only (a railed corner costs that column's high-B end, not the fan)
        _rail["n"] += 1
        if _rail["n"] <= 20 or _rail["n"] % 50 == 0:
            print(f"RAIL sr1 at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: X={float(data[9])*1e6:+.1f} uV (count {_rail['n']})")
s.register_run_after(guards, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # park gates; the field stays at the fan's end (10 T) for the next step to ride down — no blind field move here
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T, gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample {T_sample():.3f} K, sr1 rail flags {_rail['n']}")
