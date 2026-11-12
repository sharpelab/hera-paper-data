# === Landau fan, electron side (`landau-fan-vti`): n = +1.0 -> +3.2e12 at D = 0, B 1.2 -> 10 T uniform-1/B ===
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(1.0, 3.2, 61)                  # 1e12 cm^-2, electron side
Ds = np.zeros_like(ns)                          # D = 0 line
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert (Vtgs >= TG_MIN).all() and (Vtgs <= TG_MAX).all(), (Vtgs.min(), Vtgs.max())
assert (Vbgs >= BG_MIN).all() and (Vbgs <= BG_MAX).all(), (Vbgs.min(), Vbgs.max())
print(f"n-line: {len(ns)} pts, n = {ns[0]:+.2f} -> {ns[-1]:+.2f} e12 at D = 0; "
      f"Vtg [{Vtgs.min():+.4f}, {Vtgs.max():+.4f}], Vbg [{Vbgs.min():+.4f}, {Vbgs.max():+.4f}] V")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: handoff left field at 0), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- slow field axis: uniform in 1/B, ascending (magnet at 0; fan ends at 10 T for the ride-down follow-up)
B_vec = field_invB(1.2, 10.0, 124)              # d(1/B) = 5.96e-3 /T -> FFT Nyquist 83.9 T > 59.9 T (2x sum tone)
assert B_vec.max() <= B_SESSION_CAP
I_TRIP = 1e-9
sr1.sensitivity(50e-6)                          # 5 kOhm FS (spot-check-inherited; worst corner ~576 Ohm, run 7)
_tau = sr1.time_constant()
assert abs(_tau - 0.3) < 0.01, _tau             # fast_delay = 6*tau below assumes tau = 0.3 s
print(f"B rows: {len(B_vec)}, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T uniform-1/B; sr1 sens {sr1.sensitivity()} V, tau {_tau} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan electron side: n = {ns[0]:+.2f} -> {ns[-1]:+.2f} e12, D = 0 (run-5 cal), "
                  f"B = {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T uniform-1/B {len(B_vec)} rows, sr1 50 uV, fast_delay 1.8")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = 0: n = {ns[0]:+.2f} to {ns[-1]:+.2f} e12 cm^-2 ({len(ns)} pts), '
              f'B = {B_vec[0]:.2f} to {B_vec[-1]:.2f} T uniform-1/B ({len(B_vec)} rows, d(1/B) = 5.96e-3); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'follows sdh-spot-check runs 6/7 (tones 7.05/22.90 + sum 29.94 at scale 0.905)')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg, Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
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
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=1, fast_delay=1.8)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)   # park gates; field endpoint (10 T) left for the ride-down follow-up
print(f"done: B = {magnet.field():+.3f} T, gates parked ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V")
