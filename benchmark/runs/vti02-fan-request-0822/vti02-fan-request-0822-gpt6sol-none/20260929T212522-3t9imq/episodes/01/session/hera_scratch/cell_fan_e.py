# === calibrated D=0 electron Landau fan; plan step 4 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions assumed, not set by this cell: live base thermometry, zero field,
# zero Si, magnet output/switch state, lock-in drive and filtering, committed fences.
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
assert_thermometry_live("T_vaporizer", VTI.temp_logfile_candidates["T_vaporizer"], max_age=15, max_period=12)
_Ts, _Tv, _B, _Vsi = T_sample(), T_vaporizer(), magnet.field(), k_si()
_amp, _freq, _tau, _slope = sr1.amplitude(), sr1.frequency(), sr1.time_constant(), sr1.filter_slope()
print(f"precondition T_sample={_Ts:.3f} K (1.0–1.5), T_vaporizer={_Tv:.3f} K (<1.6), "
      f"B={_B:+.4f} T (|B|<0.02), Si={_Vsi:+.4f} V (0), "
      f"PS={magnet.persistent_switch_on()}, output={magnet.output_enabled()}, "
      f"drive={_amp:.3f} V at {_freq:.3f} Hz (~{_amp/100e6*1e9:.2f} nA), "
      f"tau={_tau:.3f} s, slope={_slope} dB/oct; heaters={heater.sample_range()}/{heater.vaporizer_range()}, "
      f"DC205 range/output={dc205.voltage_range()}/{dc205.output()}")
assert 1.0 <= _Ts <= 1.5 and _Tv < 1.6 and abs(_B) < 0.02 and abs(_Vsi) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(_amp-1.0) < 0.01 and abs(_freq-13.777) < 0.01 and _tau <= 0.3 and _slope == 24
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert dc205.voltage_range() == 2 and dc205.output() == 1
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert [_vr(p.vals) for p in (k_tg.volt, k_bg.volt, dc205.smart_voltage, magnet.field)] == [(-0.3,1.0),(-1.3,2.0),(-25.0,25.0),(-10.0,10.0)]

# Run-5 CNP-line calibration. c_tg is geometry anchored; c_bg/c_tg and offsets are session-measured.
CAL = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
           n_offset=-0.08937933224099137, D_offset=-0.013)
n_vec = np.round(np.linspace(0.8, 3.2, 49), 4)  # 1e12 cm^-2; 0.05e12 spacing
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), **CAL)
B_vec = np.round(np.r_[np.linspace(0, 4, 41), np.linspace(4.2, 10, 30)], 4)
assert len(B_vec) == 71 and len(Vtg_vec) == len(Vbg_vec) == 49
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX
assert Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
assert np.max(np.abs(B_vec)) <= B_SESSION_CAP
_nr, _Dr = calc_nD(Vtg_vec, Vbg_vec, **CAL)
assert np.max(np.abs(_nr-n_vec)) < 1e-9 and np.max(np.abs(_Dr)) < 1e-9
print(f"fan: B {B_vec[0]:.1f}→{B_vec[-1]:.1f} T ({len(B_vec)} rows); "
      f"n {n_vec[0]:.2f}→{n_vec[-1]:.2f}e12 ({len(n_vec)} pts); "
      f"TG {Vtg_vec[0]:+.4f}→{Vtg_vec[-1]:+.4f} V, BG {Vbg_vec[0]:+.4f}→{Vbg_vec[-1]:+.4f} V")

FAST_DELAY, I_TRIP = 2.4, 1e-9
sr1.sensitivity(100e-6)  # ~10 kohm full scale at 10 nA
_sens = sr1.sensitivity()
print(f"sr1 sensitivity {_sens*1e6:.0f} uV, estimated R full scale {_sens/(_amp/100e6):.0f} ohm; fast dwell {FAST_DELAY:.1f} s = {FAST_DELAY/_tau:.1f} tau")

mc = dict(meas_config); mc["Si (V)"] = _Vsi; mc["sample_temperature:"] = _Ts
mc["comments"] = ("landau-fan electron D=0, run-5 cal; n +0.8..+3.2e12/0.05e12, "
                  "B 0..4/0.1 then 4.2..10/0.2 T, sr1 100uV, fast_delay 2.4s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('electron D=0; run-5 cal ratio 0.772765, n_offset -0.08938e12, D_offset -0.013 V/nm; '
              'n +0.8..+3.2e12 cm^-2 (49 x 0.05e12), B 0..10 T (71 rows: 0.1 T to 4, 0.2 T above); '
              'TG +0.296..+0.984 V, BG +0.276..+1.166 V; Si 0 V, base T; sr1 sens 100uV, delay 2.4s')
s.ramp(k_bg.volt, float(Vbg_vec[0])); s.ramp(k_tg.volt, float(Vtg_vec[0]))
interruptible_sleep(10)

# multimegasweep row: time, B, TG, BG, T, I_tg, I_bg, sr0.X/P, sr1.X/P
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot('time', T_sample); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)

def fan_guard(station, data):
    _bt, _it, _ib, _v = map(float, (data[1], data[5], data[6], data[9]))
    if abs(_it) > I_TRIP or abs(_ib) > I_TRIP:
        print(f"LEAK TRIP B={_bt:.3f} T, |I_tg|={abs(_it):.3e}, |I_bg|={abs(_ib):.3e} A")
        station.interrupt_requested = True
    if abs(_v) > 0.90*_sens:
        print(f"RAIL TRIP B={_bt:.3f} T, |sr1.X|={abs(_v):.3e} V vs sens={_sens:.3e} V")
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    _fan_result = s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt],
                                   [Vtg_vec, Vbg_vec], slow_delay=0, fast_delay=FAST_DELAY)
finally:
    # The run ends at its actual B; gate sources return to the committed 0 V park.
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
print(f"done: interrupted={_fan_result.metadata.get('interrupted')}, B readback={magnet.field():+.4f} T, "
      f"TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V")
