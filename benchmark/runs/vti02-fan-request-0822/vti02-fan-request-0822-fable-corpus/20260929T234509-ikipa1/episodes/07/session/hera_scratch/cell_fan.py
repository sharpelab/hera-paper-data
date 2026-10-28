# === Landau fan (`landau-fan-vti`): D = 0 electron side, n +0.6 -> +3.2e12 (91 pts) x B 0.6 -> 10 T uniform-1/B (157 rows) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_N, N_B = 91, 157
ns = np.linspace(0.6, 3.2, N_N)                      # 1e12 cm^-2, ascending (row ends at the n = +3.2 spot)
Ds = np.zeros(N_N)                                   # V/nm
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert (Vtgs >= TG_MIN).all() and (Vtgs <= TG_MAX).all() and (Vbgs >= BG_MIN).all() and (Vbgs <= BG_MAX).all()
B_vec = 1.0 / np.linspace(1 / 0.6, 1 / 10.0, N_B)    # uniform in 1/B, ascending 0.6 -> 10 T
d_invB = (1 / 0.6 - 1 / 10.0) / (N_B - 1)
assert B_vec.max() <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
print(f"fast n-line: {N_N} pts, n +0.60 -> +3.20e12 (dn = {(ns[1]-ns[0]):.4f}e12 <= ray-Nyquist 0.029e12 at 0.6 T); "
      f"Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")
print(f"slow B: {N_B} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T; d(1/B) = {d_invB:.5f} 1/T <= 1/(3*F_L(3.2e12)=33.1 T) = 0.01007")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan opens with a 0 -> 0.6 T ramp), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# --- lock-in: fixed for the whole fan, inherited from spot checks (runs 6/7: no clip at either density extreme) ---
sr1.sensitivity(50e-6)
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f"sr1 sens {sr1.sensitivity()} V (5 kOhm FS at 10 nA), tau {_tau} s, slope {_slope} dB/oct; fast_delay 1.8 s = 6*tau")
assert _tau <= 0.31, f"tau changed ({_tau} s): fast_delay 1.8 s is sized as 6*tau for tau = 0.3 s"

I_TRIP = 1e-9
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = (f"landau-fan-vti: D = 0 electron, n +0.6 -> +3.2e12 ({N_N} pts) x B 0.6 -> 10 T uniform-1/B ({N_B} rows), "
                  f"sr1 50 uV, fast_delay 1.8 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = +0.00 V/nm, n = +0.60 to +3.20e12 cm^-2 ({N_N} pts), B = 0.6 to 10 T uniform-1/B ({N_B} rows, d(1/B) = {d_invB:.5f} 1/T); '
              f'sr1 50 uV, fast_delay 1.8 s (6 tau), slow_delay 1; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}; inherits sdh-spot-check runs 6/7 '
              f'(onset 0.71 T hole / <=1.0 T electron; F_L partition vs harmonic-comb fork to resolve by F(n))')
s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)

# row layout: [time, B, k_tg.volt, k_bg.volt, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=1, fast_delay=1.8)
# end state: B = 10 T, gates at the n = +3.2e12 spot — the LK / firming leg rides the field down from here; no park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
