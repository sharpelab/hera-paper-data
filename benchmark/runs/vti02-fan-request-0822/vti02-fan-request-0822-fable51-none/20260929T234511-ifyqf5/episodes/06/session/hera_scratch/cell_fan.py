# === Landau fan at D = 0 (`landau-fan`): n fast (co-swept TG/BG along the calibrated D = 0 line), B slow 1 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, c_tg = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.2, 3.2001, 0.05), 3)          # 1e12 cm^-2, 89 pts, hole -> electron every row
D_fan = 0.0                                                   # V/nm
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.full_like(n_vec, D_fan), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.asarray(Vtg_vec, float), np.asarray(Vbg_vec, float)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_nchk, n_vec, atol=1e-6) and np.allclose(_Dchk, D_fan, atol=1e-6)
print(f"fast axis: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, dn 0.05e12) at D = {D_fan:+.2f} V/nm; "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V")

# --- field grid: uniform in B, ascending from where the magnet sits (0 T). 0.1 T rows: 1/B Nyquist F > 31 T above 2.5 T.
B_vec = np.round(np.arange(1.0, 10.0001, 0.1), 3)             # 91 rows
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0

# --- preconditions (state this cell assumes but does not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 1 T from 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()
print(f"gate pacing (operator-owned, read only): k_tg.volt.step = {getattr(k_tg.volt, 'step', None)}, k_bg.volt.step = {getattr(k_bg.volt, 'step', None)}, "
      f"inter_delay = {getattr(k_tg.volt, 'inter_delay', None)}/{getattr(k_bg.volt, 'inter_delay', None)}")

FAST_DELAY, SLOW_DELAY = 1.0, 3.0     # fast: same dwell as gatemap run 5 (tau 0.3 s / 24 dB -> ~1-pt lag, uniform since every row runs hole -> electron)
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no mid-row autorange): 200 uV = 20 kOhm FS at 10 nA. Spot checks peaked at 590 Ohm (50 uV, fs 0.12);
# the nu = 0 CNP column at high B may exceed 20 kOhm and rail on a few points - accepted, stated in the markdown.
sr1.sensitivity(200e-6)
print(f"drive {sr1.amplitude()} V @ {sr1.frequency()} Hz -> 10 nA; sr1 sens {sr1.sensitivity()} V (20 kOhm FS), tau {sr1.time_constant()} s, slope {sr1.filter_slope()}; "
      f"sr0 sens {sr0.sensitivity()} V; magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D = 0: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 fast ({len(n_vec)} pts, co-swept TG/BG, run-5 cal), "
                  f"B {B_vec[0]}..{B_vec[-1]} T slow ({len(B_vec)} rows, 0.1 T), sr1 200 uV, fast_delay {FAST_DELAY} s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_fan:+.2f} V/nm; fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2, {len(n_vec)} pts (dn 0.05e12), TG {Vtg_vec[0]:+.4f}->{Vtg_vec[-1]:+.4f} V co-swept with BG {Vbg_vec[0]:+.4f}->{Vbg_vec[-1]:+.4f} V; '
              f'slow: B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows (0.1 T), ascending; T base; Vsi = 0; '
              f'cal run 5: c_tg {CAL["c_tg"]:.3e}, c_bg {CAL["c_bg"]:.3e} F/m2, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm')

# park the gates at the first fast point before the first field ramp (the ramp to 1 T takes ~7.5 min)
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, magnet.field, sr1.X)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates back to the CNP-side start of the line (cheap, inside validators); field stays where the sweep left it - the next step rides it down.
    s.ramp(k_tg.volt, Vtg_vec[0]); s.ramp(k_bg.volt, Vbg_vec[0])
    print(f"end state: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
