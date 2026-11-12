# === Landau fan at D = 0 (`landau-fan`): B slow 0 -> 10 T (91 rows), (Vtg, Vbg) fast along the run-5 D = 0 line, n = -1.25..+3.25e12 (151 pts) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.25, 3.25001, 0.03), 4)                 # 1e12 cm^-2, 151 pts
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_nchk, _Dchk = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.allclose(_nchk, n_vec, atol=1e-6) and np.all(np.abs(_Dchk) < 1e-6)
print(f"fast axis: n = {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts, step {n_vec[1]-n_vec[0]:.2f}) at D = 0; "
      f"Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V "
      f"(per point dVtg {np.diff(Vtg_vec).mean()*1e3:.1f} mV, dVbg {np.diff(Vbg_vec).mean()*1e3:.1f} mV)")

# --- slow axis: 0, 0.5, 0.75 T; uniform in 1/B 1 -> 5 T (68 rows, d(1/B) = 0.012 /T); 0.25 T steps 5 -> 10 T. Ascending: magnet sits at 0.
B_rows = np.unique(np.round(np.hstack(([0.0, 0.5, 0.75], field_invB(1.0, 5.0, 68), np.arange(5.25, 10.0001, 0.25))), 4))
assert B_rows.max() <= B_SESSION_CAP and np.all(np.diff(B_rows) > 0)
print(f"slow axis: {len(B_rows)} rows, B {B_rows[0]} -> {B_rows[-1]} T; d(1/B) on the 1-5 T leg {np.abs(np.diff(1/B_rows[3:71])).max():.4f} /T; total {len(B_rows)*len(n_vec)} pts")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"gates now (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

FAST_DELAY, SLOW_DELAY = 0.5, 3.0
I_TRIP = 1e-9
TAU_RUN, TAU_RESTORE = 0.1, (sr0.time_constant(), sr1.time_constant())
print(f"lock-in tau before: sr0 {TAU_RESTORE[0]} s, sr1 {TAU_RESTORE[1]} s (slopes {sr0.filter_slope()}/{sr1.filter_slope()} dB/oct) -> set {TAU_RUN} s for this run; fast_delay {FAST_DELAY} s = {FAST_DELAY/TAU_RUN:.0f} tau")
sr0.time_constant(TAU_RUN); sr1.time_constant(TAU_RUN)
# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA (CNP at high B may reach kOhm; low-R oscillations are noise-, not resolution-limited).
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS), sr0 sens {sr0.sensitivity()} V; tau now sr0 {sr0.time_constant()} / sr1 {sr1.time_constant()} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: B slow 0->10 T ({len(B_rows)} rows: 0/0.5/0.75, 1/B-uniform 1-5 T x68, 0.25 T 5-10 T), "
                  f"(Vtg,Vbg) fast along D=0, n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 x{len(n_vec)}; run-5 cal; sr1 100 uV, tau 0.1 s, fast_delay 0.5 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: slow magnet.field 0 -> 10 T, {len(B_rows)} rows (0, 0.5, 0.75; 1/B-uniform 1-5 T d(1/B)=0.012; 0.25 T steps 5-10 T); '
              f'fast (k_tg.volt, k_bg.volt) co-swept along D = 0, n = {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 cm^-2 step 0.03 ({len(n_vec)} pts); '
              f'cal run 5: c_tg {CAL["c_tg"]:.3e} (prior), ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; '
              f'sr1 sens 100 uV, tau 0.1 s, fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(magnet.field, k_tg.volt, sr1.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

_tripped = {"leak": False}
def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        _tripped["leak"] = True
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_rows], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    sr0.time_constant(TAU_RESTORE[0]); sr1.time_constant(TAU_RESTORE[1])
    if _tripped["leak"]:
        s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"done: B = {magnet.field():+.3f} T (fan ends at 10 T; next step rides it down), (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), "
          f"tau restored sr0 {sr0.time_constant()} / sr1 {sr1.time_constant()} s, T_sample {T_sample():.3f} K")
