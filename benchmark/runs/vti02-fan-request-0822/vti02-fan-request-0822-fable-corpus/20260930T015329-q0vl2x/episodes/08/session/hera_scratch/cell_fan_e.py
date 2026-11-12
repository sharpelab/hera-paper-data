# === Landau fan, electron side (`landau-fan-vti`): n = +1.2 -> +3.2e12 at D = 0, B 0.7 -> 10 T uniform-1/B ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# --- session calibration (run 5, cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

# --- fast axis: paired n-line at D = 0, ray-Nyquist floor at B_lo = 0.7 T (n-step 0.033e12 <= 0.034e12) ---
N_N = 61
ns = np.linspace(1.2, 3.2, N_N)                  # 1e12 cm^-2
Ds = np.zeros(N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtgs.min() and Vtgs.max() <= TG_MAX, (Vtgs.min(), Vtgs.max())
assert BG_MIN <= Vbgs.min() and Vbgs.max() <= BG_MAX, (Vbgs.min(), Vbgs.max())
print(f"n-line: {N_N} pts, n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 at D = 0; "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")

# --- slow axis: uniform 1/B, Delta(1/B) = 0.0101 = 1/(3*F_L(n_max)) (3 samples/period at F = 33.1 T) ---
N_B = 133
B_vec = field_invB(0.7, 10.0, N_B)               # ascending: starts near the magnet (0 T), ends at 10 T
assert B_vec.max() <= B_SESSION_CAP

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan ascends from 0.7), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# Fixed sensitivity 100 uV = 10 kOhm FS at 10 nA: worst corner is low-n x 10 T (run 7 anchor 587 Ohm at
# |n|=1.2e12, 10 T -> ~6% FS; headroom over QH spikes beats resolution — clipping corrupts a whole column FFT).
sr1.sensitivity(100e-6)
I_TRIP = 1e-9
print(f"B rows: {N_B}, {B_vec[0]:.2f} -> {B_vec[-1]:.1f} T (dB 5 mT -> 0.9 T); sr1 sens {sr1.sensitivity()} V, "
      f"tau {sr1.time_constant()} s; fast_delay 1.8 s = 6 tau")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan electron side: n = +1.20 to +3.20e12 ({N_N} pts), D = 0 (run-5 cal), "
                  f"B 0.7 -> 10 T uniform-1/B ({N_B} rows), sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side: n = +1.20 to +3.20e12 cm^-2 ({N_N} pts, D = 0), B = 0.70 -> 10.00 T uniform-1/B '
              f'({N_B} rows, d(1/B) = 0.0101); Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f}; '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; '
              f'design from runs 6/7: scale 0.90, tones 7.1/22.1 (e) 4.7/6.6 (h)')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

# blocking magnet: the first slow set (0 -> 0.7 T, ~5 min) is the positioning; slow_delay covers gate
# flyback settle, fast_delay = 6 tau (per-column-FFT fan, base recipe step 7)
s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=2, fast_delay=1.8)
# ends at 10 T with gates at n = +3.2e12; next step (LK ladder / follow-ups) rides the field down — no park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
