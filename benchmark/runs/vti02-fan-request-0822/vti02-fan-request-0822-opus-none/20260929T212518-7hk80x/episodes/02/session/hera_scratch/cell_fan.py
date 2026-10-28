# === Landau fan (`landau-fan`) at D = 0: n fast along the D = 0 line, B slow uniform in 1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB, luttinger_frequency

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D_FAN = 0.0                                          # V/nm — the fan sits on the D = 0 line
n_vec = np.linspace(-1.25, 3.24, 113)                # 1e12 cm^-2, 0.0401e12 steps (TG-limited both ends)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, D_FAN, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_nchk, n_vec) and np.allclose(_Dchk, D_FAN, atol=1e-9)
print(f"n fast: {len(n_vec)} pts, {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f} e12 cm^-2 (step {n_vec[1]-n_vec[0]:.4f}e12) at D = {D_FAN:+.2f} V/nm")
print(f"  Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V (limits {TG_MIN}, {TG_MAX});  "
      f"Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V (limits {BG_MIN}, {BG_MAX})")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0), "
      f"V_si = {k_si():+.3f} V (0), Vtg/Vbg = {k_tg.volt():+.4f}/{k_bg.volt():+.4f} V (0/0 after the handoff close-out), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- field grid: B = 0 anchor row, then uniform in 1/B from 1.0 to 10 T (ascending: start where the magnet sits) ---
B_FAN_LO, B_FAN_HI, N_B = 1.0, 10.0, 109
B_vec = np.hstack(([0.0], field_invB(B_FAN_LO, B_FAN_HI, N_B)))
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
_dinvB = (1 / B_FAN_LO - 1 / B_FAN_HI) / (N_B - 1)
print(f"B slow: {len(B_vec)} rows = [0 anchor] + {N_B} uniform in 1/B, {B_FAN_LO} -> {B_FAN_HI} T; "
      f"d(1/B) = {_dinvB:.5f} /T -> Nyquist F = {1/(2*_dinvB):.1f} T, FFT resolution df = {1/(1/B_FAN_LO - 1/B_FAN_HI):.2f} T")
print(f"  full-density Onsager F_L at the fan ends: {float(luttinger_frequency(abs(n_vec[0])*1e16)):.1f} T (hole) "
      f"/ {float(luttinger_frequency(n_vec[-1]*1e16)):.1f} T (electron) — both inside Nyquist")

FAST_DELAY, SLOW_DELAY = 0.8, 3.0
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm FS at 10 nA — run-5 gatemap parity.
# Trade stated in the markdown: favours SdH contrast at 1-3 T (noise ~7 Ohm) over headroom at the high-B CNP column.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s, "
      f"slope {sr1.filter_slope()} dB (fast_delay {FAST_DELAY} s = {FAST_DELAY/sr1.time_constant():.1f} tau); sr0 sens {sr0.sensitivity()} V")
print(f"points {len(B_vec)*len(n_vec)}; est {(len(B_vec)*len(n_vec)*(FAST_DELAY+0.12) + (B_FAN_HI)/0.137*60 + len(B_vec)*9.5)/3600:.1f} h")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan at D = 0: n fast {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 cm^-2 ({len(n_vec)} pts) co-swept (Vtg, Vbg), "
                  f"B slow 0 + {B_FAN_LO}..{B_FAN_HI} T uniform in 1/B ({N_B} rows), Vsi = 0, sr1 sens 100 uV, run-5 cal")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: n fast {n_vec[0]:+.3f}..{n_vec[-1]:+.3f}e12 cm^-2, {len(n_vec)} pts (step {n_vec[1]-n_vec[0]:.4f}e12), '
              f'co-swept Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f} / Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f} V; '
              f'B slow {len(B_vec)} rows = B=0 anchor + {N_B} uniform in 1/B {B_FAN_LO}..{B_FAN_HI} T '
              f'(d(1/B) {_dinvB:.5f}/T, Nyquist {1/(2*_dinvB):.1f} T, df {1/(1/B_FAN_LO - 1/B_FAN_HI):.2f} T); '
              f'Vsi = 0; cal run 5: c_tg {CAL["c_tg"]:.4e}, ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm (n scale = 9.5 nm geometry prior)')

s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

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
    # gates to 0; field stays where the fan ended (never re-traverse — the next step starts from there).
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
