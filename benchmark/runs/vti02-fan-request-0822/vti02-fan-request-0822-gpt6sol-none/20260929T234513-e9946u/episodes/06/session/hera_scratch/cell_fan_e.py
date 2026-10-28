# Plan step 5 — electron Landau fan: B=0 baseline, then 1.5→10 T; calibrated D_A=0 density line.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Actual state and silent preconditions, before any write.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
_t, _tv, _b = T_sample(), T_vaporizer(), magnet.field()
_vsi, _si_range, _si_out = k_si(), dc205.voltage_range(), dc205.output()
_hr1, _hr2 = heater.sample_range(), heater.vaporizer_range()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_nt, _nb = k_tg.nplci(), k_bg.nplci()
print(f'PRECONDITION: T_sample={_t:.3f} K [1.0,1.5], T_vaporizer={_tv:.3f} K [0.7,1.5]; '
      f'B={_b:+.4f} T [±0.05], Vsi={_vsi:+.4f} V [±0.01], Si range/output={_si_range}/{_si_out} [2/1]; '
      f'heater ranges={_hr1}/{_hr2} [0/0], PS/output={_ps}/{_out} [True/True], '
      f'TG/BG NPLC={_nt}/{_nb} [1/1]')
assert 1.0 <= _t <= 1.5 and 0.7 <= _tv <= 1.5 and abs(_b) < 0.05
assert abs(_vsi) < 0.01 and _si_range == 2 and _si_out == 1
assert _hr1 == 0 and _hr2 == 0 and _ps and _out
assert _nt == 1 and _nb == 1
assert not magnet.is_ramping(), 'magnet still ramping'
assert sr0.time_constant() == 0.3 and sr1.time_constant() == 0.3
assert sr0.filter_slope() == 24 and sr1.filter_slope() == 24

# Run-5 calibration: measured Cbg/Ctg ratio and CNP/D offsets; absolute Ctg from 9.5 nm prior.
_ct, _cb, _n0, _d0 = 2.7960593093052633e-3, 2.160696465377614e-3, -0.08937933224099137, -0.013
_n = np.linspace(0.35, 3.20, 72)  # 1e12 cm^-2
_v_tg, _v_bg = calc_gate_voltages(_n, np.zeros_like(_n), _ct, _cb, n_offset=_n0, D_offset=_d0)
_n_check, _d_check = calc_nD(_v_tg, _v_bg, _ct, _cb, n_offset=_n0, D_offset=_d0)
_B = np.r_[0.0, np.round(np.arange(1.5, 10.0001, 0.1), 4)]
assert np.all(np.diff(_n) > 0) and np.all(np.diff(_B) > 0)
assert np.all((_v_tg >= TG_MIN) & (_v_tg <= TG_MAX)) and np.all((_v_bg >= BG_MIN) & (_v_bg <= BG_MAX))
assert abs(_d_check).max() < 1e-6 and abs(_n_check - _n).max() < 1e-6
assert _B[-1] <= B_SESSION_CAP and len(_B) == 87 and len(_n) == 72
print(f'GRID: {len(_B)} B rows ({_B[0]:.1f}, then {_B[1]:.1f}→{_B[-1]:.1f} T by 0.1) × {len(_n)} n points '
      f'({_n[0]:.2f}→{_n[-1]:.2f}e12, Δn={_n[1]-_n[0]:.4f}e12); '
      f'Vtg={_v_tg[0]:+.4f}→{_v_tg[-1]:+.4f} V, Vbg={_v_bg[0]:+.4f}→{_v_bg[-1]:+.4f} V')

_drive = sr1.amplitude()
assert abs(_drive - 1.0) < 0.02, f'drive changed: {_drive} V'
sr1.sensitivity(200e-6)  # 20 kΩ nominal R headroom at ~10 nA; fixed throughout the fan
assert sr1.sensitivity() == 200e-6 and sr0.sensitivity() >= 20e-3
print(f'BIAS/RANGES: {_drive:.3f} V / 100 MΩ = {_drive/100e6*1e9:.2f} nA; '
      f'sr1={sr1.sensitivity()*1e6:.0f} µV, sr0={sr0.sensitivity()*1e3:.1f} mV; '
      f'fast dwell 2.2 s ≥7τ at 24 dB/oct')

_mc = dict(meas_config)
_mc['Si (V)'] = _vsi
_mc['sample_temperature:'] = _t
_mc['comments'] = 'landau-fan: B 0 baseline, 1.5..10 T step 0.1; n_A +0.35..+3.20e12 step 0.0401, D_A=0; run-5 calibration; Vsi=0; sr1 200uV, dwell 2.2s'
s = sweep.AsyncStation(_mc)
s.add_comment('landau-fan')
s.add_comment('electron side B1-B2: B slow [0,1.5..10] T 87 rows; (TG,BG) fast co-swept 72 points for calibrated ridge-A n +0.35..+3.20e12 cm^-2 at D=0; run-5 c_bg/c_tg=0.773, n0=-0.089e12, D0=-0.013 V/nm; Si=0; 200uV sr1, 2.2s dwell')
s.ramp(k_bg.volt, float(_v_bg[0]))
s.ramp(k_tg.volt, float(_v_tg[0]))
interruptible_sleep(10)

# Row layout: time, B, Vtg, Vbg, T_sample, I_tg, I_bg, sr0_X, sr1_X.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr).fp(sr0.X).fp(sr1.X)
s.plot('time', T_sample)
s.plot('time', k_tg.curr)
s.plot('time', k_bg.curr)
s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, sr1.X)

def fan_guard(station, data):
    i_tg, i_bg, i_x, v_x = (float(data[j]) for j in (5, 6, 7, 8))
    if abs(i_tg) > 1e-9 or abs(i_bg) > 1e-9 or abs(i_x) > 0.9*sr0.sensitivity() or abs(v_x) > 0.85*sr1.sensitivity():
        print(f'FAN TRIP B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f} V: '
              f'Itg={i_tg*1e12:+.0f} pA, Ibg={i_bg*1e12:+.0f} pA, '
              f'sr0X={i_x*1e3:+.2f} mV, sr1X={v_x*1e6:+.2f} µV')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

_result = s.multimegasweep([magnet.field], [_B], [k_tg.volt, k_bg.volt], [_v_tg, _v_bg],
                           slow_delay=0.0, fast_delay=2.2)
print(f'FAN FINISHED: file_id={_result.id}; B readback={magnet.field():+.4f} T; '
      f'Vtg={k_tg.volt():+.4f} V, Vbg={k_bg.volt():+.4f} V; interrupted={_result.metadata.get("interrupted")}')
