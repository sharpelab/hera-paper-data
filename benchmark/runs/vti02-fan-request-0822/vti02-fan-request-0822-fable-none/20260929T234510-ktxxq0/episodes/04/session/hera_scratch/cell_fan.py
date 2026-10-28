# === Landau fan at D = 0 (`landau-fan`): fast n = -1.2 -> +3.2e12 (co-swept TG/BG, 111 pts), slow B = 0.5 -> 10 T (50 mT, 191 rows) ===
from sharpelab_nb.gates import calc_gate_voltages

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.arange(-1.2, 3.2 + 1e-9, 0.04), 3)          # 1e12 cm^-2, 111 pts
_VV = np.array([calc_gate_voltages(n, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]) for n in n_vec])
Vtg_vec, Vbg_vec = _VV[:, 0], _VV[:, 1]
assert TG_MIN <= Vtg_vec.min() and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert BG_MIN <= Vbg_vec.min() and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
B_vec = np.round(np.arange(0.5, 10.0001, 0.05), 3)              # 191 rows ascending
assert B_vec.max() <= B_SESSION_CAP
print(f"fan: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 ({len(n_vec)} pts) along D = 0; "
      f"(Vtg, Vbg) ({Vtg_vec[0]:+.4f}, {Vbg_vec[0]:+.4f}) -> ({Vtg_vec[-1]:+.4f}, {Vbg_vec[-1]:+.4f}) V; "
      f"B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows; {len(n_vec)*len(B_vec)} pts total")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts with the 0.5 T ramp), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

# Fixed sensitivity for the whole fan: 100 uV = 10 kOhm FS at 10 nA (run-5-proven over the full
# gate window; stated trade — the gapped-CNP/nu=0 stripe may rail at high B, positions still read).
sr1.sensitivity(100e-6)
I_TRIP = 1e-9
print(f"sr1 sens {sr1.sensitivity()} V (10 kOhm FS), tau {sr1.time_constant()} s; "
      f"fast_delay 1.0 s (~3.3 tau), slow_delay 3.0 s; sr0 sens {sr0.sensitivity()} V")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan @ D=0 (run-5 cal): n -1.2 -> +3.2e12 fast (111 pts, dn 0.04, co-swept TG/BG), "
                  "B 0.5 -> 10 T slow (50 mT, 191 rows), sr1 100 uV, fast_delay 1.0, slow_delay 3.0")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan: n {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f}e12 (111 pts, dn 0.04) co-swept '
              f'(Vtg, Vbg) = ({Vtg_vec[0]:+.4f}, {Vbg_vec[0]:+.4f}) -> ({Vtg_vec[-1]:+.4f}, {Vbg_vec[-1]:+.4f}) V; '
              f'B 0.5 -> 10 T, 50 mT, ascending; cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.3f}e12, D_offset {CAL["D_offset"]:+.3f}')
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
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.3f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=3.0, fast_delay=1.0)
# end state: B = 10 T, gates at the n = +3.2e12 point — no park; the post-fan step decides the ride-down.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
