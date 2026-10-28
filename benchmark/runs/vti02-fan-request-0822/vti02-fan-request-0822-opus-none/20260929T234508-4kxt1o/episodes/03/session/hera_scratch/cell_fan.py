# === Landau fan (`landau-fan`): B slow (uniform in 1/B) x (Vtg, Vbg) co-swept along D = 0 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB, luttinger_frequency

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: n along D = 0, both carrier signs, 89 pts (dn = 0.05e12 cm^-2) ---
D_FAN = 0.0
n_vec = np.linspace(-1.20, 3.20, 89)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, D_FAN, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
_tg_ok, _bg_ok = sanitize_tg_bg(Vtg_vec, Vbg_vec, tg_lims, bg_lims)
assert len(_tg_ok) == len(Vtg_vec), f"D=0 line leaves the operating box: {len(Vtg_vec) - len(_tg_ok)} pts dropped"
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
_nD0, _nD1 = calc_nD(Vtg_vec[0], Vbg_vec[0], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]), \
             calc_nD(Vtg_vec[-1], Vbg_vec[-1], CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2 at D = {D_FAN:+.2f} V/nm, {len(n_vec)} pts (dn = {n_vec[1]-n_vec[0]:.4f}e12)")
print(f"      Vtg {Vtg_vec.min():+.4f} .. {Vtg_vec.max():+.4f} V (limits {TG_MIN}, {TG_MAX}); "
      f"Vbg {Vbg_vec.min():+.4f} .. {Vbg_vec.max():+.4f} V (limits {BG_MIN}, {BG_MAX})")
print(f"      roundtrip (n, D) ends: {_nD0} , {_nD1}; F_L at |n|max = {luttinger_frequency(n_vec[-1]*1e16):.2f} T")

# --- slow axis: B uniform in 1/B (sdh_fft-native), ascending from the step-3 onset ---
B_vec = np.round(field_invB(0.9, 10.0, 102), 6)   # round: keep the top setpoint off the cap's float edge
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
_dinvB = float(np.mean(np.abs(np.diff(1.0 / B_vec))))
print(f"slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {len(B_vec)} rows uniform in 1/B; "
      f"d(1/B) = {_dinvB:.5f} 1/T -> Nyquist F = {1/(2*_dinvB):.1f} T, dF = {1/(1/B_vec[0]-1/B_vec[-1]):.2f} T")
print(f"      row dB: {np.diff(B_vec)[0]*1e3:.1f} mT at the low end -> {np.diff(B_vec)[-1]*1e3:.0f} mT at 10 T; "
      f"traverse {(B_vec[-1]-B_vec[0])/0.137:.0f} min + start ramp {B_vec[0]/0.137:.0f} min")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0.9 and ramps), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm full scale at 10 nA
# — 17x the largest R seen so far (590 Ohm, run 7 at 10 T), headroom for the unmeasured CNP column at high B.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> {sr1.amplitude()/100e6*1e9:.1f} nA; sr1 sens {sr1.sensitivity()} V "
      f"({sr1.sensitivity()/(sr1.amplitude()/100e6):.0f} Ohm FS), tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; "
      f"sr0 sens {sr0.sensitivity()} V ({sr0.sensitivity()/1e6*1e9:.1f} nA FS)")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan at D = {D_FAN:+.2f} V/nm: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 cm^-2 fast ({len(n_vec)} pts), "
                  f"B {B_vec[0]:.2f}..{B_vec[-1]:.2f} T slow ({len(B_vec)} rows, uniform in 1/B), sr1 100 uV, Vsi = 0")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_FAN:+.2f} V/nm; fast = (k_tg.volt, k_bg.volt) co-swept along the D=0 line, '
              f'n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2, {len(n_vec)} pts (dn {n_vec[1]-n_vec[0]:.4f}e12), '
              f'Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f}; '
              f'slow = B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {len(B_vec)} rows uniform in 1/B (field_invB), '
              f'd(1/B) {_dinvB:.5f} -> Nyquist {1/(2*_dinvB):.1f} T, dF {1/(1/B_vec[0]-1/B_vec[-1]):.2f} T; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, c_tg {CAL["c_tg"]:.4e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}')

s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow set), Vtg, Vbg, T_sample, B(readback), k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(magnet.field).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', T_sample); s.plot('time', magnet.field)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[6])), abs(float(data[7]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates park at 0; field is left where the fan ended (10 T) for a possible measured ride-down.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
