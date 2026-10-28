# === Landau fan at D = 0 (`landau-fan`): B slow 1 -> 10 T uniform in 1/B (82 rows) x n fast along D = 0, -1.25 -> +3.25e12 (151 pts) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (ratio data-calibrated; absolute n scale = geometry prior, ~0.89x true per run-6 ladder) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.25, 3.25 + 1e-9, 0.03), 4)          # 1e12 cm^-2 (prior scale), 151 pts
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
Vtg_vec, Vbg_vec = np.asarray(Vtg_vec, float), np.asarray(Vbg_vec, float)
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
_n_rt, _D_rt = calc_nD(Vtg_vec, Vbg_vec, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert np.abs(_D_rt).max() < 1e-6 and np.abs(_n_rt - n_vec).max() < 1e-6
B_vec = field_invB(1.0, 10.0, 82)                                  # ascending, d(1/B) = 0.0111 -> Nyquist 45 T, dF 1.1 T
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() > 0
print(f"fast: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts), Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f}, "
      f"Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V; slow: B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T ({len(B_vec)} rows, uniform 1/B)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_sr, _vrg = heater.sample_range(), heater.vaporizer_range()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05), V_si = {k_si():+.3f} V (0), "
      f"heater ranges {_sr}/{_vrg} (0/0), nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1), "
      f"PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, V_tg/V_bg = {k_tg.volt():+.3f}/{k_bg.volt():+.3f}")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0} K off base"
assert abs(_B0) < 0.05, f"magnet not at 0: {_B0} T"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert _sr == 0 and _vrg == 0, "a heater range is on"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not 1"
assert magnet.persistent_switch_on() and magnet.output_enabled()

I_TRIP = 1e-9
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
# Fixed sensitivity, no autorange mid-map: 100 uV = 10 kOhm FS at 10 nA. SdH/QH away from the CNP is 0-600 Ohm (runs 6-7);
# a rail at the high-B nu = 0 core near n = 0 is accepted (not the discriminator), flagged at the checkpoint.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V @ {sr1.frequency()} Hz -> {sr1.amplitude()/100e6*1e9:.1f} nA; sr1 sens {sr1.sensitivity()} V; "
      f"sr0 sens {sr0.sensitivity()} V; tau {sr1.time_constant()} s / {sr1.filter_slope()} dB; magnet settle_s {magnet.settle_s} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan D=0: B 1->10 T uniform 1/B (82 rows) slow; n -1.25..+3.25e12 prior (151, 0.03e12) along D=0 fast "
                  "(Vtg,Vbg co-swept); run-5 cal; Vsi 0; sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 line (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; '
              f'n on geometry-prior scale, run-6 ladder says true = 0.894 x prior); fast n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12, {len(n_vec)} pts; '
              f'slow B {B_vec[0]:.2f}..{B_vec[-1]:.2f} T, {len(B_vec)} rows uniform in 1/B; Vsi = 0; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s')

# --- move to the start: gates to the first fan point, then the field 0 -> 1 T (unrecorded, ~7.3 min at 0.137 T/min) ---
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
print(f"ramping field {magnet.field():+.3f} -> {B_vec[0]:.3f} T ..."); magnet.field(float(B_vec[0]))
print(f"at start: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T = {T_sample():.3f} K")
interruptible_sleep(10)

# row layout: [time, magnet_field, k_tg.volt, k_bg.volt, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, Vbg={float(data[3]):+.4f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    # gates park at 0; the field stays where the fan left it (10 T on completion) — the next step rides it down.
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.4f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T = {T_sample():.3f} K")
