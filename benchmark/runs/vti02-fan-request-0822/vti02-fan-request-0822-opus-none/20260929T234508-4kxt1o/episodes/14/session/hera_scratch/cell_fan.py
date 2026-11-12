# === Landau fan (`landau-fan`): R_xx(B, n) at D = 0 — the stacking discriminator (plan step 5) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-fit, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 1: fan starts low), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 1.0 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()
# validators still the committed ones (gate B contract; read, never write)
_vr = lambda v: (float(v._min_value), float(v._max_value))
assert _vr(k_2400_tg.volt.vals) == (TG_MIN, TG_MAX), _vr(k_2400_tg.volt.vals)
assert _vr(k_2400_bg.volt.vals) == (BG_MIN, BG_MAX), _vr(k_2400_bg.volt.vals)
assert _vr(magnet.field.vals) == (-B_SESSION_CAP, B_SESSION_CAP), _vr(magnet.field.vals)

# --- fast axis: the D = 0 line, n = -1.24 ... +3.24e12 (TG-limited at both ends, >= 5 mV inside the validators) ---
N_FAST = 91
n_vec = np.linspace(-1.24, +3.24, N_FAST)                      # 1e12 cm^-2
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = sanitize_tg_bg(Vtg_vec, Vbg_vec, tg_lims, bg_lims)
assert len(Vtg_vec) == len(Vbg_vec) == N_FAST, (len(Vtg_vec), len(Vbg_vec))   # nothing clipped out
assert Vtg_vec.min() > TG_MIN + 0.004 and Vtg_vec.max() < TG_MAX - 0.004
assert Vbg_vec.min() > BG_MIN + 0.004 and Vbg_vec.max() < BG_MAX - 0.004
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_Dchk).max() < 1e-6, _Dchk
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 in {N_FAST} pts ({(n_vec[1]-n_vec[0])*1e3:.1f}e9 step) at D = 0; "
      f"Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f}, Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V")

# --- slow axis: uniform in 1/B (SdH is periodic in 1/B) with a 0.40 T cap on dB so the
#     high-field end stays readable as a fan. d(1/B) = 0.0105 -> F_Nyquist = 48 T (F_L ~ 33.5 T). ---
B_LO, B_HI, D_INV, DB_MAX = 0.7, 10.0, 0.0105, 0.40
_b = [B_LO]
while _b[-1] < B_HI - 1e-9:
    _nxt = 1.0 / (1.0 / _b[-1] - D_INV) if (1.0 / _b[-1] - D_INV) > 0 else B_HI
    _b.append(min(_nxt, _b[-1] + DB_MAX, B_HI))
B_vec = np.round(np.array(_b), 4)
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP
_dinv = -np.diff(1.0 / B_vec)
print(f"slow: {len(B_vec)} B rows {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T; dB {np.diff(B_vec).min():.4f}..{np.diff(B_vec).max():.3f} T; "
      f"F_Nyquist {1/(2*_dinv.max()):.0f} T; dF = {1/(1/B_vec.min()-1/B_vec.max()):.2f} T")

FAST_DELAY, SLOW_DELAY = 1.0, 3.0   # tau = 0.3 s @ 24 dB/oct -> 1.0 s is ~1 fast-point of lag/smoothing (= 0.05e12 in n)
I_TRIP = 1e-9                       # gate-leak trip; observed flyback transients peak ~0.2 nA
assert sr1.time_constant() == 0.3 and sr1.filter_slope() == 24, (sr1.time_constant(), sr1.filter_slope())

# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm FS at 10 nA.
# Spot checks peaked at 590 Ohm (5.8 % FS); the headroom is for the CNP columns at high B.
sr1.sensitivity(100e-6)
_I = abs(sr1.amplitude() / meas_config["bias_resistor"])
print(f"drive {sr1.amplitude()} V / {meas_config['bias_resistor']:.0e} Ohm = {_I*1e9:.2f} nA; "
      f"sr1 sens {sr1.sensitivity()} V = {sr1.sensitivity()/_I:.0f} Ohm FS; tau {sr1.time_constant()} s @ {sr1.filter_slope()} dB/oct; "
      f"sr0 sens {sr0.sensitivity()} V")
print(f"priced: {len(B_vec)} rows x ({N_FAST} x {FAST_DELAY+0.17:.2f} s + {SLOW_DELAY+3.5:.1f} s) + "
      f"{(B_HI-abs(_B0))/0.137/60:.2f} h ramp = {(len(B_vec)*(N_FAST*(FAST_DELAY+0.17)+SLOW_DELAY+3.5+3)+(B_HI-abs(_B0))/0.137*60)/3600:.2f} h nominal")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan: B slow {B_vec[0]}-{B_vec[-1]} T ({len(B_vec)} rows, uniform 1/B d=0.0105, dB cap 0.40 T); "
                  f"(Vtg,Vbg) fast along D = 0, n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 ({N_FAST}); sr1 sens 100 uV; run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: fast (Vtg, Vbg) along D = 0, n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2 ({N_FAST} pts, '
              f'{(n_vec[1]-n_vec[0])*1e3:.1f}e9 step), Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} / Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f}; '
              f'slow B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T, {len(B_vec)} rows uniform in 1/B (d(1/B) = {D_INV}, dB capped {DB_MAX} T), '
              f'F_Nyquist {1/(2*_dinv.max()):.0f} T, dF {1/(1/B_vec.min()-1/B_vec.max()):.2f} T; sr1 100 uV (10 kOhm FS); '
              f'fast_delay {FAST_DELAY} s (tau 0.3 s / 24 dB); T_sample {_T0:.3f} K; Vsi = 0; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', T_sample); s.plot('time', sr1.P); s.plot('time', sr0.P)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates parked; field left where the fan ended (next step rides it down, never re-traverses).
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
