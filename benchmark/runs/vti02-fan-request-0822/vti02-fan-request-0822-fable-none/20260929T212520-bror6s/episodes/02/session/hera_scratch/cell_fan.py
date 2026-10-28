# === Landau fan at D = 0 (`landau-fan`, plan step 4): n fast (co-swept gate line), B slow 0.35 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.24, 3.24, 181)                    # 1e12 cm^-2; dn = 0.025e12
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX, (Vtg_vec.min(), Vtg_vec.max())
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, (Vbg_vec.min(), Vbg_vec.max())
B_vec = np.round(np.arange(0.35, 10.0001, 0.05), 4)      # 194 rows, ascending from where the magnet sits
assert B_vec.max() <= B_SESSION_CAP
print(f"fast line: n {n_vec[0]:+.2f} .. {n_vec[-1]:+.2f}e12 x{len(n_vec)} -> Vtg [{Vtg_vec.min():+.4f}, {Vtg_vec.max():+.4f}], "
      f"Vbg [{Vbg_vec.min():+.4f}, {Vbg_vec.max():+.4f}]; slow B {B_vec[0]} .. {B_vec[-1]} T x{len(B_vec)} (50 mT)")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.05: fan starts at 0.35 T), "
      f"V_si = {k_si():+.3f} V (0), PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()

I_TRIP = 1e-9
# 100 uV = 10 kOhm FS at ~10 nA (run-5 ridge sizing). The nu=0 CNP stripe will clip at high B - accepted, see md.
sr1.sensitivity(100e-6)
print(f"sr1 sens {sr1.sensitivity()} V, tau {sr1.time_constant()} s, slope {sr1.filter_slope()} dB/oct")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan D=0 (run-5 cal): fast co-swept (Vtg,Vbg), n -1.24..+3.24e12 x181; "
                  "slow B 0.35..10.00 T x194 (50 mT); fast_delay 1.0, slow_delay 3.0; sr1 100 uV")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = 0 fan, region-A cal (run 5: ratio 0.773, n_offset -0.089e12, D_offset -0.013 V/nm): '
              f'fast co-swept (Vtg, Vbg) along D = 0, n = -1.24 .. +3.24e12 in 181 pts (dn 0.025e12); '
              f'slow B = 0.35 .. 10.00 T in 50 mT steps (194 rows); fast_delay 1.0 s, slow_delay 3.0 s; sr1 100 uV')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, B, Vtg, Vbg, T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                 slow_delay=3.0, fast_delay=1.0)
# ends at 10 T, gates at the n = +3.24e12 end of the line - follow-ups ride the field down; no park.
print(f"done: B = {magnet.field():+.3f} T, (Vtg, Vbg) = ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), T = {T_sample():.3f} K")
