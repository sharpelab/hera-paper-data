# Plan step 4: constant nominal-D two-carrier Landau fan; all preflight reads precede writes.
import json
from pathlib import Path

# Committed safety surfaces: verify only, never replace or widen.
for _p, _limits in [(k_tg.volt, (-0.3, 1.0)), (k_bg.volt, (-1.3, 2.0)),
                    (dc205.smart_voltage, (-25.0, 25.0)), (dc205.voltage, (-25.0, 25.0)),
                    (magnet.field, (-10.0, 10.0)), (heater.sample_setpoint, (0.0, 100.0)),
                    (heater.vaporizer_setpoint, (0.0, 100.0))]:
    _actual = (float(_p.vals._min_value), float(_p.vals._max_value))
    print(f'{_p.full_name}: expected validator {_limits}, actual {_actual}')
    assert _actual == _limits, f'Validator mismatch: {_p.full_name}'
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert k_tg.volt.step == k_bg.volt.step == 0.005
assert dc205.ramp_rate == 0.5
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_Vsi, _rng, _out = k_si(), dc205.voltage_range(), dc205.output()
_hr = (heater.sample_range(), heater.vaporizer_range())
_ps, _output = magnet.persistent_switch_on(), magnet.output_enabled()
print(f'Expected base T 1.0..1.5 K, vaporizer <1.6 K within 0.6 K; actual {_Ts:.3f}, {_Tv:.3f}')
print(f'Expected handoff |B|<0.02 T, heaters (0,0), PS/output on; actual {_B:+.5f}, {_hr}, {_ps}/{_output}')
print(f'Expected Si 0 V, range 2, output 1; actual {_Vsi:+.4f}, {_rng}, {_out}; TG/BG readback {k_tg.volt():+.4f}/{k_bg.volt():+.4f} V')
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Tv-_Ts) < 0.6
assert abs(_B) < 0.02 and _hr == (0,0) and _ps and _output
assert abs(_Vsi) < 0.01 and _rng == 2 and _out == 1
_expected_wiring = {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                    'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('Expected hardwired T_0 -> B_3, sr1 B_1-B_2; actual', WIRING)
assert WIRING == _expected_wiring
_drive, _freq = sr1.amplitude(), sr1.frequency()
_acq = [(x.name,x.time_constant(),x.filter_slope()) for x in (sr0,sr1)]
_nplc = (k_tg.nplci(), k_bg.nplci())
print(f'Expected drive 1 V/13.777 Hz, tau 0.3 s/24 dB, NPLC 1/1; actual {_drive}/{_freq}, {_acq}, {_nplc}')
assert abs(_drive-1.0)<1e-6 and abs(_freq-13.777)<0.01
assert all(abs(tau-0.3)<1e-9 and slope==24 for _,tau,slope in _acq)
assert _nplc == (1.0,1.0)
assert meas_config['sr0_gain'] == -1e6 and meas_config['bias_resistor'] == 100e6 and meas_config['bias_channel'] == 'sr1'

# Pure gate conversion, SI throughout; values frozen from this session's run-5 fit.
fan_cal = GateCalibration(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
                          n_offset=-0.08937933224099137e16, D_offset=-0.013e9)
n_nominal = np.linspace(-1.2, 3.2, 111)*1e16
_q = (n_nominal-fan_cal.n_offset)*cst.e
_d = (0.0-fan_cal.D_offset)*2*cst.epsilon_0
Vtg_fan = (_q+_d)/(2*fan_cal.c_tg)
Vbg_fan = (_q-_d)/(2*fan_cal.c_bg)
B_fan = np.r_[0.0, 1/np.linspace(1/1.5, 1/4.0, 51), np.round(np.arange(4.1,10.0001,0.1), 4)]
assert len(B_fan)==112 and np.all(np.diff(B_fan)>0)
for _p, _vec in [(k_tg.volt,Vtg_fan),(k_bg.volt,Vbg_fan),(magnet.field,B_fan)]:
    for _v in _vec: _p.validate(float(_v))
assert np.allclose(fan_cal.density(Vtg_fan,Vbg_fan),n_nominal)
assert np.max(np.abs(fan_cal.displacement_field(Vtg_fan,Vbg_fan))) < 1.0
print(f'Fan: {len(B_fan)} x {len(n_nominal)}; TG {Vtg_fan[0]:+.6f}..{Vtg_fan[-1]:+.6f}, BG {Vbg_fan[0]:+.6f}..{Vbg_fan[-1]:+.6f} V')
print('Field ramp floor: 10/0.137 = 73.0 min. Estimated total 14 h including margin; endpoint 10 T.')

# Sensitivity changes only; acquisition time constants and all gate pacing stay committed.
sr0.sensitivity(0.02)
sr1.sensitivity(100e-6)
mc = dict(meas_config)
mc.update({'Si (V)':_Vsi, 'sample_temperature:':_Ts, 'sr1_gain':1.0,
           'sr0_sensitivity':sr0.sensitivity(), 'sr1_sensitivity':sr1.sensitivity(),
           'lockin_settling_readback':_acq, 'gate_nplci':list(_nplc),
           'gate_calibration':dict(c_tg=fan_cal.c_tg,c_bg=fan_cal.c_bg,
                                   n_offset_m2=fan_cal.n_offset,D_offset_Vm=fan_cal.D_offset,
                                   reference_run=5,absolute_scale='geometry prior; ratio and offsets session fitted'),
           'comments':'landau-fan; B_1-B_2; nominal D=0; n=-1.2..3.2e12 cm^-2; Si=0; base T; 3 s dwell'})
s = sweep.AsyncStation(mc, basedir=str(Path(main_dir)/'data'))
s.add_comment('landau-fan')
s.add_comment('B=0 baseline then 1.5..4 T (51 inverse-B points), 4.1..10 T (0.1 T); '
              'n_nom=-1.2..3.2e12 cm^-2 (111), D_nom=0; TG=-0.277033..0.983594 V, '
              'BG=-0.465040..1.166281 V; Si=0 V; calibration run 5 provisional absolute scale; '
              'T base; 10 nA nominal; sr1 100 uV; tau 0.3 s/24 dB; dwell 3 s; slow settle 3 s')
s.ramp(k_tg.volt,float(Vtg_fan[0]))
s.ramp(k_bg.volt,float(Vbg_fan[0]))
interruptible_sleep(10)
# Follow raw X; gains applied once by the analysis helpers. Disconnected sr2/3 excluded.
_follow = [T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,magnet.field]
for _p in _follow:
    s.fp(_p)
    s.plot('time',_p)
# Row: time, B_set, TG_set, BG_set, Ts, Tv, Itg, Ibg, X0, P0, X1, P1, B_read.
_fan_count = 0
_fan_stop = []
def fan_guard(station, data):
    global _fan_count
    _fan_count += 1
    _, b, vt, vb, ts, tv, itg, ibg, x0, p0, x1, p1, bread = data
    reasons = []
    if not np.all(np.isfinite(data)): reasons.append('nonfinite channel')
    if abs(itg)>1e-9 or abs(ibg)>1e-9: reasons.append('gate leakage >1 nA')
    if abs(x0)>=0.9*0.02 or abs(x1)>=0.9*100e-6: reasons.append('lock-in >=90% full scale')
    if not 5e-9 < x0/(-1e6) < 15e-9: reasons.append('drain current outside 5..15 nA')
    if not (1.0<=ts<=1.5 and 0<tv<1.6 and abs(tv-ts)<0.6): reasons.append('base T mismatch')
    if abs(bread-b)>0.03: reasons.append('measured field differs >30 mT')
    if (_fan_count-1)%len(n_nominal)==0:
        try:
            for name in ('T_sample','T_vaporizer'):
                assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
        except Exception as exc: reasons.append(f'thermometry freshness: {exc}')
    if reasons:
        _fan_stop.extend(reasons)
        print(f'FAN STOP at point {_fan_count}, B={bread:+.4f} T: {reasons}',flush=True)
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())
fan_result = s.multimegasweep([magnet.field],[B_fan],[k_tg.volt,k_bg.volt],[Vtg_fan,Vbg_fan],
                              slow_delay=3.0,fast_delay=3.0)
print('FAN RETURN',fan_result.id,'interrupted',fan_result.metadata.get('interrupted'),'guard reasons',_fan_stop)
print(f'Actual endpoint B={magnet.field():+.5f} T, TG={k_tg.volt():+.6f}, BG={k_bg.volt():+.6f}, Si={k_si():+.4f} V, Ts={T_sample():.3f}, Tv={T_vaporizer():.3f} K')
# Hold actual endpoint. Any interruption requires a new state read before another move.
