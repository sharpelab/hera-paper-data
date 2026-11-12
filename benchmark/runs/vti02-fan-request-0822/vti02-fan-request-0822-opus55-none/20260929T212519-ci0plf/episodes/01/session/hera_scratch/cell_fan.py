# === Landau fan along D = 0 (`landau-fan`): B slow 1 -> 10 T (uniform 1/B to 3.1 T, then 0.1 T), n fast -1.25 .. +3.25e12 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (ratio data-calibrated; absolute n scale = geometry prior, x0.907 per run 6's 30 T tone) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.linspace(-1.25, 3.25, 181), 4)          # nominal 1e12 cm^-2, 0.025 step
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.round(Vtg_vec, 5), np.round(Vbg_vec, 5)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_nD = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast: {len(n_vec)} pts, n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f}e12 (D max|{np.abs(_nD[1]).max():.1e}| V/nm); "
      f"Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f} V, Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V")

# --- field grid: uniform in 1/B (d(1/B) = 0.01 /T) from 1.0 T until dB reaches 0.1 T (3.1 T), then 0.1 T steps to 10 T
_Bl = 1.0 / np.arange(1.0, 1 / 3.16, -0.01)
B_vec = np.concatenate([_Bl, np.arange(_Bl[-1] + 0.1, 10.0001, 0.1)])
B_vec = np.round(B_vec, 4)
if B_vec[-1] < 10.0 - 1e-6:
    B_vec = np.append(B_vec, 10.0)
assert np.all(np.diff(B_vec) > 0) and B_vec.max() <= B_SESSION_CAP
print(f"slow: {len(B_vec)} rows, B {B_vec[0]} -> {B_vec[-1]} T, max dB {np.diff(B_vec).max():.3f} T, max d(1/B) {np.max(-np.diff(1/B_vec)):.4f} /T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan ramps 0 -> 1 T first), "
      f"V_si = {k_si():+.3f} V (0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, heater ranges {heater.sample_range()}/{heater.vaporizer_range()} (0/0)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert abs(_B0) < 0.05, f"magnet not at ~0: {_B0} T"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0, "a heater range is on"
assert abs(sr1.amplitude() - 1.0) < 1e-3 and abs(sr1.frequency() - 13.777) < 0.01, "drive not 1 V / 13.777 Hz (10 nA)"

# Fixed sensitivity for the whole fan (state0 left sr1 at 2 uV): 100 uV = 10 kOhm FS at 10 nA.
# Noise floor ~3 Ohm at both 50 and 100 uV (runs 5-7); run 6/7 max 590 Ohm at 10 T; the high-B CNP may rail (accepted).
sr1.sensitivity(100e-6)
FAST_DELAY, SLOW_DELAY = 0.6, 3.0   # 2 tau at tau = 0.3 s / 24 dB (forward-only sweeps: lag is a constant n-shift); 10 tau after flyback
I_TRIP, T_TRIP = 1e-9, 2.5
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS), sr0 sens {sr0.sensitivity()} V, tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; "
      f"fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s, settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan D=0: n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 nominal (181), B 1->10 T (uniform 1/B to 3.1 T, 0.1 T above; {len(B_vec)} rows), "
                  f"Vsi 0, sr1 100 uV, fast_delay {FAST_DELAY}, cal run 5")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; '
              f'nominal n scale, x0.907 per run-6 30 T tone); fast (Vtg, Vbg) co-swept n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f}e12, 181 pts; '
              f'slow B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows, d(1/B) = 0.01 /T to 3.1 T then 0.1 T; Vsi = 0; T base')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(set), Vtg, Vbg, T_sample, B(read), k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(magnet.field).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample); s.plot('time', magnet.field)

def guard(station, data):
    i_tg, i_bg, T = abs(float(data[6])), abs(float(data[7])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
    if T > T_TRIP:
        print(f"T TRIP at B={float(data[1]):.3f} T: T_sample = {T:.3f} K > {T_TRIP} K")
        station.interrupt_requested = True
s.register_run_after(guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # gates park at 0; field holds where the fan ends (10 T) — next step rides it
    print(f"end: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T_sample = {T_sample():.3f} K")
