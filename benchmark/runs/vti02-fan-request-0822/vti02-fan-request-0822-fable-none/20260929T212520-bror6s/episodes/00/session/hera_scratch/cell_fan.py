# === Landau fan at D = 0 (`landau-fan`): n fast -1.25 -> +3.24e12 (151 pts, co-swept TG/BG) x B slow 0 -> 10 T (132 rows, uniform-1/B above 1 T) ===
from sharpelab_nb.gates import calc_gate_voltages

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.25, 3.24, 151)          # 1e12 cm^-2 along D = 0; dn = 2.99e10 (hole side validator-limited)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())

# --- slow axis: 4 coarse rows 0..0.75 T, then 128 rows uniform in 1/B from 1 -> 10 T
#     (max d(1/B) = 7.15e-3 -> per-column FFT Nyquist F_max = 70 T; already-even 1/B record for sdh_fft)
B_rows = np.concatenate(([0.0, 0.25, 0.5, 0.75], np.round(1.0 / np.linspace(1.0, 0.1, 128), 4)))
assert np.all(np.diff(B_rows) > 0) and B_rows.max() <= B_SESSION_CAP, (B_rows.max(),)

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"

FAST_DELAY, SLOW_DELAY = 0.9, 3.0    # 0.9 s = 3 tau (tau 0.3 s / 24 dB) — knowing bend; run 5 clean at 1.0 s
I_TRIP = 1e-9
# Fixed sensitivity: 100 uV = 10 kOhm FS at 10 nA (run-4 lesson). Accepts a possible
# narrow rail on the CNP columns at high B (nu = 0); the SdH evidence lives at |n| > 0.
sr1.sensitivity(100e-6)
print(f"grid {len(B_rows)} x {len(n_vec)} = {len(B_rows)*len(n_vec)} pts; sr1 sens {sr1.sensitivity()} V, "
      f"tau {sr1.time_constant()} s; drive {sr1.amplitude()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan: D=0 line (run-5 cal), n -1.25..+3.24e12 fast 151 pts co-swept (Vtg,Vbg); "
                  "B slow 0..10 T, 132 rows (0,0.25,0.5,0.75 + 128 uniform-1/B 1..10 T); sr1 100 uV; base T")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 (run-5 cal: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, '
              f'D_offset {CAL["D_offset"]:+.3f}); n fast {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 cm^-2, 151 pts '
              f'(Vtg {Vtg_vec[0]:+.4f}..{Vtg_vec[-1]:+.4f}, Vbg {Vbg_vec[0]:+.4f}..{Vbg_vec[-1]:+.4f}); '
              f'B slow 0 -> 10 T, 132 rows, uniform-1/B above 1 T; T = {_T0:.2f} K')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, k_tg.curr); s.plot(k_tg.volt, k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_rows], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end state: B = {magnet.field():+.3f} T (left at field — never re-traverse), "
          f"gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V, T = {T_sample():.3f} K")
