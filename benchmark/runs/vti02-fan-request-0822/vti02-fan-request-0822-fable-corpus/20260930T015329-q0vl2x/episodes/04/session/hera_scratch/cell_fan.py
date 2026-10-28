# === Landau fan, electron side (`landau-fan-vti`): D = 0, n = +1.00 -> +3.25e12, B 1 -> 10 T uniform-1/B ===
from sharpelab_nb.gates import calc_gate_voltages

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_N, N_B = 71, 91
ns = np.linspace(1.00, 3.25, N_N)                 # 1e12 cm^-2; 3x ray-Nyquist at B_lo = 1 T (23.3 periods)
Ds = np.zeros(N_N)                                # D = 0 (the investigation's operating point)
Vtg_vec, Vbg_vec = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
B_vec = field_invB(1.0, 10.0, N_B)                # Delta(1/B) = 0.01 /T -> FFT Nyquist 50 T >= 1.2*F_L(n_max) = 41 T
assert B_vec.max() <= B_SESSION_CAP and B_vec.min() >= 1.0

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan positions to 1 T), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f"sr1 tau = {_tau} s, slope = {_slope} dB/oct  (fast_delay 1.8 s = 6*tau, keyed to 0.3 s / 24 dB)")
assert abs(_tau - 0.3) < 1e-3 and _slope == 24, "lock-in settling changed on the front panel - re-derive the dwell"

# Fixed sensitivity for the whole fan, sized to the global worst corner (low n x high B: nu ~ 4.2 at
# (+1.0e12, 10 T), QH Rxx peaks ~ kOhm): 100 uV = 10 kOhm FS at 10 nA, ~17x the run-7 near-CNP anchor
# (576 Ohm at 10 T). Run-6 max (522 Ohm) sits at 5% FS - lose low-R resolution rather than clip a column.
sr1.sensitivity(100e-6)
I_TRIP = 1e-9
print(f"grid: {N_B} B-rows (uniform 1/B) x {N_N} n-cols; Vtg {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, "
      f"Vbg {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V; sr1 sens {sr1.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti electron side: n = +1.00 -> +3.25e12 ({N_N} cols), D = 0 (run-5 cal), "
                  f"B = 1 -> 10 T uniform-1/B ({N_B} rows, d(1/B) = 0.01 /T), sr1 100 uV, fast_delay 1.8 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side, D = +0.00 V/nm: n = +1.00 -> +3.25e12 cm^-2 ({N_N} cols), B = 1 -> 10 T uniform-1/B '
              f'({N_B} rows, d(1/B) = 0.01 /T); (Vtg, Vbg) = ({Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f}, '
              f'{Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f}) V; sr1 100 uV, tau 0.3 s / 24 dB, fast_delay 1.8 s (6 tau); '
              f'cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f} V: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=1, fast_delay=1.8)

# park gates at 0; field stays at 10 T deliberately (next step - LK ladder or hole-side work - starts high
# and rides down; never re-traverse).
s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
print(f"done: B = {magnet.field():+.3f} T, gates parked at 0 V; T_sample = {T_sample():.3f} K")
