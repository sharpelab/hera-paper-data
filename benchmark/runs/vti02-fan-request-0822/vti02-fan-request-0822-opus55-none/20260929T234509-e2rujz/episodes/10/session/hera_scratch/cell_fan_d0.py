# === Landau fan at D = 0 (`landau-fan`): n fast along the calibrated D = 0 line, B slow 0 -> 8 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from sharpelab_nb.autorange import autorange_sr830s

# --- session calibration from run 5 (ratio data-calibrated; n scale confirmed by runs 6/7 F = F_L closure) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
D_FAN = 0.0                                                    # V/nm
n_vec = np.round(np.arange(-1.25, 3.25 + 1e-9, 0.025), 4)      # 1e12 cm^-2, 181 pts
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.full_like(n_vec, D_FAN), **CAL)
B_vec = np.round(np.arange(0.0, 8.0 + 1e-9, 0.1), 4)            # T, 81 rows, uniform in B
assert len(n_vec) == 181 and len(B_vec) == 81
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX, \
    (Vtg_vec.min(), Vtg_vec.max(), Vbg_vec.min(), Vbg_vec.max())
assert np.abs(B_vec).max() <= B_SESSION_CAP
_n_chk, _D_chk = calc_nD(Vtg_vec, Vbg_vec, **CAL)
print(f"fast: n {n_vec[0]:+.3f} -> {n_vec[-1]:+.3f}e12 ({len(n_vec)} pts), Vtg {Vtg_vec[0]:+.4f} -> {Vtg_vec[-1]:+.4f}, "
      f"Vbg {Vbg_vec[0]:+.4f} -> {Vbg_vec[-1]:+.4f} V; roundtrip max|D| {np.abs(_D_chk).max():.1e}")
print(f"slow: B {B_vec[0]} -> {B_vec[-1]} T, {len(B_vec)} rows")

# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
_sr, _vr = heater.sample_range(), heater.vaporizer_range()
_amp, _f = sr1.amplitude(), sr1.frequency()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5) | B = {_B0:+.4f} T (|B|<0.05, fan starts at 0) | V_si = {k_si():+.3f} V (0) | "
      f"heaters {_sr}/{_vr} (0/0) | PS {magnet.persistent_switch_on()}, output {magnet.output_enabled()} | "
      f"nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1) | drive {_amp} V @ {_f:.3f} Hz (1.0 V @ 13.777)")
assert 1.0 <= _T0 <= 1.5, f"T_sample {_T0}"
assert abs(_B0) < 0.05, f"field {_B0}"
assert abs(k_si()) < 0.01 and _sr == 0 and _vr == 0
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert abs(_amp - 1.0) < 1e-3 and abs(_f - 13.777) < 0.01, "drive changed -> I_bias not 10 nA"

# --- readout: sr1 from 10 uV (1 kOhm FS at 10 nA); autorange hook ranges up at the insulating CNP, floor 10 uV ---
SR1_FLOOR = 10e-6
sr1.sensitivity(SR1_FLOOR)
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9
print(f"sr1 sens {sr1.sensitivity()} V (autorange floor {SR1_FLOOR}), sr0 sens {sr0.sensitivity()} V, tau {sr1.time_constant()} s / {sr1.filter_slope()} dB")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = ("landau-fan D=0: n fast -1.25..+3.25e12 (181, 0.025) co-swept Vtg/Vbg on run-5 cal; "
                  "B slow 0..8 T (81, 0.1 T); sr1 autorange floor 10 uV; fast_delay 1 s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f'D = {D_FAN:+.2f} V/nm; n fast {n_vec[0]:+.3f}..{n_vec[-1]:+.3f}e12 cm^-2 ({len(n_vec)} pts, 0.025) as (Vtg, Vbg) co-sweep; '
              f'B slow {B_vec[0]}..{B_vec[-1]} T ({len(B_vec)} rows, 0.1 T); cal run 5: ratio {CAL["c_bg"]/CAL["c_tg"]:.3f}, '
              f'n_offset {CAL["n_offset"]:+.4f}e12, D_offset {CAL["D_offset"]:+.3f} V/nm; sr1 autorange (floor 10 uV)')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, magnet_field(slow), Vtg(fast), Vbg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)
s.register_run_before(autorange_sr830s, (sr0, [sr1], SR1_FLOOR))

_IDX_ITG, _IDX_IBG = 5, 6
def leak_guard(station, data):
    if abs(float(data[_IDX_ITG])) > I_TRIP or abs(float(data[_IDX_IBG])) > I_TRIP:
        print(f"LEAK TRIP at B = {data[1]:.2f} T, Vtg {data[2]:+.4f}, Vbg {data[3]:+.4f}: I_tg {data[_IDX_ITG]:.2e}, I_bg {data[_IDX_IBG]:.2e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtg_vec, Vbg_vec],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f"end: B = {magnet.field():+.4f} T (stays; step 5 rides it down), Vtg {k_tg.volt():+.4f}, Vbg {k_bg.volt():+.4f}, "
          f"T_sample {T_sample():.3f} K, sr1 sens {sr1.sensitivity()}")
