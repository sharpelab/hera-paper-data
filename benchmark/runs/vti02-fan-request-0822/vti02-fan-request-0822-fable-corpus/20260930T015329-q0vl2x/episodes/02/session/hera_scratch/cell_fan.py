# === Landau fan (`landau-fan-vti`): electron side, D = 0, n = +2.1 -> +3.2e12, B 0.7 -> 10 T uniform-1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D0 = 0.0
ns = np.linspace(3.2, 2.1, 37)                  # 1e12 cm^-2, descending; step 0.031 <= half ray spacing at 0.7 T (0.034)
Ds = np.full_like(ns, D0)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtgs.min() and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert BG_MIN <= Vbgs.min() and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
print(f"n-line: n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({len(ns)} pts), Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")

# --- field axis: uniform in 1/B (per-column SdH-FFT fan); d(1/B) = 0.01006 = 1/3-Nyquist on F_L(3.2e12) = 33.1 T ---
B_vec = field_invB(0.7, 10.0, 133)
assert B_vec.max() <= B_SESSION_CAP
print(f"B: {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {len(B_vec)} rows uniform-1/B, d(1/B) = {abs(np.diff(1/B_vec)).max():.5f} /T")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left 0 T), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
_tau = sr1.time_constant()
FAST_DELAY, SLOW_DELAY = 2.1, 1.0               # 7*tau settling floor at tau = 0.3 s / 24 dB/oct (per-column FFT read)
print(f"sr1 tau {_tau} s, slope {sr1.filter_slope()} dB/oct -> fast_delay {FAST_DELAY} s (7 tau)")
assert _tau <= 0.301, _tau

I_TRIP = 1e-9
sr1.sensitivity(50e-6)                          # inherited from runs 6/7: 5 kOhm FS at 10 nA; worst corner (n=2.1, 10 T) anchor: run 7 peak 576 Ohm
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS); sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron: D = {D0:+.2f} V/nm, n = +2.1 to +3.2e12 (37 pts), B 0.7 -> 10 T uniform-1/B (133 rows), "
                  f"sr1 50 uV, fast_delay {FAST_DELAY} s (run-5 cal)")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = {D0:+.2f} V/nm, n = +2.1 to +3.2e12 cm^-2 (37 pts, descending), '
              f'B = 0.7 -> 10 T uniform-1/B (133 rows, d(1/B) = 0.01006 = 1/3-Nyquist on F_L = 33.1 T); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'follows sdh-spot-checks runs 6/7 (onset <= 0.7 T, sens/settling inherited)')

# position: blocking ramp to B_lo (~5 min from 0 T), then gates to the line start
magnet.field(float(B_vec[0]))
s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)

# row layout: [time, magnet_field, k_tg_volt, k_bg_volt, T_sample, k_tg_curr, k_bg_curr, sr0_X, sr0_P, sr1_X, sr1_P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B = {float(data[1]):+.3f} T, Vtg = {float(data[2]):+.4f} V: |I_tg| = {i_tg:.3e}, |I_bg| = {i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# ends at 10 T, gates at the n-line end (n = +2.1e12) — follow-ups ride the magnet down; no park here.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
