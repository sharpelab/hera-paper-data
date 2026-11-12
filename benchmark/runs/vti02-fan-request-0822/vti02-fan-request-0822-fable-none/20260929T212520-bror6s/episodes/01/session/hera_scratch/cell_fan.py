# === Landau fan (`landau-fan`): D = 0 line (run-5 cal), n -1.25 -> +3.20e12 (151 pts, co-swept TG+BG fast) x B 1 -> 10 T (100 mT, 91 rows slow) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts with the 0->1 T ramp), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- fast axis: D = 0 line, n = -1.25 .. +3.20e12 in 151 pts (dn ~ 3.0e10; ~8 pts per nu=1 at 10 T) ---
n_vec = np.linspace(-1.25, 3.20, 151)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())

# --- slow axis: B ascending from where the magnet sits ---
B_vec = np.round(np.arange(1.0, 10.0001, 0.1), 4)
assert B_vec.max() <= B_SESSION_CAP
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9

# Fixed sensitivity for the whole fan (no autorange mid-row): 500 uV = 50 kOhm FS at 10 nA.
# The nu=0/CNP stripe at high B may exceed 50 kOhm and rail -- accepted (read qualitatively there);
# 15 nV LSB keeps runs-6/7-scale SdH (0.1-1 uV) quantitative everywhere else.
sr1.sensitivity(500e-6)
print(f"fast: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12, Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, "
      f"Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f} ({len(n_vec)} pts); slow: B {B_vec[0]}..{B_vec[-1]} T ({len(B_vec)} rows)")
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (50 kOhm FS); sr0 sens {sr0.sensitivity()} V; tau {sr1.time_constant()} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan: D=0 line (run-5 cal), n -1.25..+3.20e12 co-swept TG+BG 151 pts fast; "
                  "B 1..10 T 100 mT 91 rows slow; sr1 500 uV; leak trip 1 nA")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f}): n = -1.25..+3.20e12 cm^-2, 151 pts co-swept (Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, '
              f'Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f}); B = 1..10 T, 100 mT, 91 rows ascending; sr1 500 uV, 10 nA')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# ends at B = 10 T, gates at the e-side end (n = +3.2e12) -- next step rides the field down; no park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
