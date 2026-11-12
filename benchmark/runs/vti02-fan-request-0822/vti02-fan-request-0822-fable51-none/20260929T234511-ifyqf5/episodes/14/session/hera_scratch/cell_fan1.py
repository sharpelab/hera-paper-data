# === Fan 1 — D = 0 Landau fan (`landau-fan`): B slow 0.4 -> 10 T (0.2 T), fast = D = 0 gate line n -1.25 .. +3.25e12 (0.03e12) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, absolute scale = 9.5 nm prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_line = np.round(np.arange(-1.25, 3.25 + 1e-9, 0.03), 4)          # 1e12 cm^-2, 151 pts, both carrier signs
D_line = 0.0                                                          # V/nm
Vtg_line, Vbg_line = calc_gate_voltages(n_line, np.full_like(n_line, D_line), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_line, Vbg_line = np.asarray(Vtg_line), np.asarray(Vbg_line)
assert Vtg_line.min() >= TG_MIN and Vtg_line.max() <= TG_MAX and Vbg_line.min() >= BG_MIN and Vbg_line.max() <= BG_MAX, \
    (Vtg_line.min(), Vtg_line.max(), Vbg_line.min(), Vbg_line.max())
print(f"fast line: {len(n_line)} pts, n {n_line[0]:+.2f} .. {n_line[-1]:+.2f}e12 at D = {D_line:+.2f}; "
      f"Vtg {Vtg_line.min():+.4f} .. {Vtg_line.max():+.4f} V, Vbg {Vbg_line.min():+.4f} .. {Vbg_line.max():+.4f} V (inside validators)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left the magnet at 0), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"

# --- slow axis: uniform in B (blocking, rate-limited magnet); start where it sits (0 T), end at 10 T for the down-fan next.
B_vec = np.round(np.arange(0.4, 10.0 + 1e-9, 0.2), 4)                 # 49 rows
assert B_vec.max() <= B_SESSION_CAP
FAST_DELAY, SLOW_DELAY = 1.0, 3.0                                     # run-5 pacing (1.17 s/pt measured incl. turnaround)
I_TRIP = 1e-9

# Fixed sensitivity for the whole fan (no autorange mid-row): 100 uV = 10 kOhm FS at 10 nA.
# Spot checks (runs 6, 7) peaked at 590 Ohm at 10 T; only the nu = 0 gap near n = 0 at high B is expected to exceed FS (rail = gap, accepted).
sr1.sensitivity(100e-6)
print(f"B grid: {len(B_vec)} rows, {B_vec[0]} -> {B_vec[-1]} T (0.2 T); drive {sr1.amplitude()} V -> 10 nA; "
      f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V; tau {sr1.time_constant()} s; settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: B slow 0.4->10 T (0.2 T, {len(B_vec)} rows); fast co-swept (Vtg,Vbg) along D = 0, n -1.25..+3.25e12 "
                  f"(0.03e12, {len(n_line)} pts); run-5 cal; sr1 100 uV; fast_delay 1 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_line:+.2f} V/nm line; n {n_line[0]:+.2f} .. {n_line[-1]:+.2f}e12 step 0.03 ({len(n_line)} pts, fast, co-swept Vtg/Vbg); '
              f'B {B_vec[0]} -> {B_vec[-1]} T step 0.2 ({len(B_vec)} rows, slow); Vsi = 0; T base; '
              f'cal run 5: c_tg {CAL["c_tg"]:.3e}, c_bg {CAL["c_bg"]:.3e}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_line[0]); s.ramp(k_tg.volt, Vtg_line[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, magnet.field, sr1.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}, Vbg={float(data[3]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_line, Vbg_line],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates park at 0; the field stays where the sweep left it (10 T if complete) for the down-fan — no field move here.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
print(f"done: B = {magnet.field():+.3f} T (left as is), (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T_sample = {T_sample():.3f} K")
