# === Landau fan at D = 0 (`landau-fan`): n fast -1.25 -> +3.20e12 (201 pts, TG+BG co-swept); B slow 0 -> 10 T (0.1 T, 101 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; same CAL as runs 6/7) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.25, 3.20, 201)                      # 1e12 cm^-2; dn = 2.2e10
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
B_vec = np.round(np.arange(0.0, 10.0001, 0.1), 4)          # 101 rows, ascending from where the magnet sits
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
assert B_vec.max() <= B_SESSION_CAP
print(f"fast line: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 -> Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}] V, "
      f"Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}] V; slow B {B_vec[0]}..{B_vec[-1]} T x {len(B_vec)}")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not at 1"

FAST_DELAY, SLOW_DELAY = 1.0, 1.0     # run-5 gatemap pacing (known-good at tau 0.3 s)
I_TRIP = 1e-9
# Fixed sensitivity for the whole fan (no autorange mid-row): 200 uV = 20 kOhm FS at 10 nA —
# headroom for the nu=0 CNP ridge at high B; ~50 Ohm SdH proven clean at 0.3% FS in run 6.
# If the nu=0 ridge exceeds 20 kOhm it soft-clips on that column only — accepted (the rail is
# itself gap evidence); everything else has >30x headroom.
sr1.sensitivity(200e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (20 kOhm FS); "
      f"tau {sr1.time_constant()} s / {sr1.filter_slope()} dB/oct")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan at D = 0: fast n = -1.25..+3.20e12 (201 pts, TG+BG co-swept along run-5 D = 0 line), "
                  "slow B = 0..10 T (0.1 T, 101 rows), sr1 200 uV, Vsi = 0")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: fast n -1.25..+3.20e12, 201 pts (dn 2.2e10), Vtg [{Vtg_vec.min():+.3f},{Vtg_vec.max():+.3f}], '
              f'Vbg [{Vbg_vec.min():+.3f},{Vbg_vec.max():+.3f}]; slow B 0..10 T, 0.1 T, 101 rows; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; '
              f'T = {_T0:.2f} K')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
print(f"done: B = {magnet.field():+.3f} T (left at the fan top — the next step rides it down), gates parked at 0")
