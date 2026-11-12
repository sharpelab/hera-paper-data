# Plan step 4: near-zero-D Landau fan; all hardware access stays in measure.
import json
from pathlib import Path
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Read-only preflight. Exact deployed validators must still match the card.
for _p, _limits in ((k_tg.volt, (-0.3, 1.0)), (k_bg.volt, (-1.3, 2.0)),
                    (dc205.smart_voltage, (-25.0, 25.0)), (dc205.voltage, (-25.0, 25.0)),
                    (magnet.field, (-10.0, 10.0)), (heater.sample_setpoint, (0.0, 100.0)),
                    (heater.vaporizer_setpoint, (0.0, 100.0))):
    _actual = (float(_p.vals._min_value), float(_p.vals._max_value))
    print(f'validator {_p.full_name}: expected {_limits}; actual {_actual}')
    assert _actual == _limits, f'Validator mismatch: {_p.full_name}'
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_Ts, _Tv, _B, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_Hs, _Hv = heater.sample_range(), heater.vaporizer_range()
_PS, _out = magnet.persistent_switch_on(), magnet.output_enabled()
print(f'Expected base Ts 1.0..1.5 K, Tv<1.6 K and |Tv-Ts|<0.6 K; actual {_Ts}, {_Tv}')
print(f'Expected B=0 +/-0.02 T, Si=0 +/-0.01 V, heater ranges 0/0, PS/output on; actual {_B}, {_Si}, {_Hs}/{_Hv}, {_PS}/{_out}')
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Ts-_Tv) < 0.6
assert abs(_B) < 0.02 and abs(_Si) < 0.01 and _Hs == _Hv == 0 and _PS and _out
print('Starting gates (will set both):', k_tg.volt(), k_bg.volt())
assert WIRING == {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                  'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert dc205.voltage_range() == 2 and dc205.output() == 1 and dc205.ramp_rate == 0.5
print('Expected TG/BG step 0.005 V, NPLC 1; actual', k_tg.volt.step, k_bg.volt.step, k_tg.nplci(), k_bg.nplci())
assert k_tg.volt.step == k_bg.volt.step == 0.005
assert k_tg.nplci() == k_bg.nplci() == 1
_amp, _freq = sr1.amplitude(), sr1.frequency()
_tau0, _tau1, _slope0, _slope1 = sr0.time_constant(), sr1.time_constant(), sr0.filter_slope(), sr1.filter_slope()
print('Expected drive 1 V/13.777 Hz; tau 0.3/0.3 s, slopes 24/24; actual', _amp, _freq, _tau0, _tau1, _slope0, _slope1)
assert abs(_amp-1.0)<1e-6 and abs(_freq-13.777)<0.01
assert _tau0 == _tau1 == 0.3 and _slope0 == _slope1 == 24
assert meas_config['sr0_gain'] == -1e6 and meas_config['bias_resistor'] == 100e6
assert meas_config['bias_channel'] == 'sr1' and sr0.sensitivity() == 0.02

# Plan in provisional coordinates; direct voltage bounds are authoritative.
fan_cal = json.loads(Path('hera_scratch/cal_run5.json').read_text())
assert np.isclose(fan_cal['ratio'], 0.7727648902821315)
n_fan = np.linspace(-1.2, 3.2, 177)
Vt_fan, Vb_fan = calc_gate_voltages(n_fan, np.zeros_like(n_fan), fan_cal['c_tg'], fan_cal['c_bg'], fan_cal['n_offset'], fan_cal['D_offset'])
B_fan = np.concatenate(([0.0, 1.0, 1.5], field_invB(2.0, 10.0, 57)))
assert len(B_fan) == 60 and np.all(np.diff(B_fan)>0)
assert np.all((Vt_fan >= -0.3) & (Vt_fan <= 1.0))
assert np.all((Vb_fan >= -1.3) & (Vb_fan <= 2.0))
for _p, _vec in ((k_tg.volt,Vt_fan),(k_bg.volt,Vb_fan),(magnet.field,B_fan)):
    for _v in _vec: _p.validate(float(_v))
print(f'Fan: {len(B_fan)} x {len(n_fan)}; TG {Vt_fan.min():+.6f}..{Vt_fan.max():+.6f} V; BG {Vb_fan.min():+.6f}..{Vb_fan.max():+.6f} V')
print('Ramp floor: 10 T x 7.3 min/T = 73 min; planned total 12h15m including settling/readout and contingency.')

sr1.sensitivity(100e-6)
assert sr1.sensitivity() == 100e-6
_mc = dict(meas_config)
_mc.update({'sr1_gain':1.0, 'Si (V)':_Si, 'sample_temperature:':_Ts,
            'gate_calibration':fan_cal, 'density_scale_status':'geometry-anchored; ratio from run 5',
            'D_zero_status':'provisional CNP resistance-minimum proxy',
            'n_nominal_1e12_cm2':n_fan.tolist(), 'D_nominal_V_nm':0.0,
            'sr0_tau_s':_tau0,'sr1_tau_s':_tau1,'filter_slope_db_oct':24,
            'comments':'landau-fan; B1-B2; Si 0; nominal n -1.2..3.2e12, D~0; B 0,1,1.5 then 2..10 T inverse-B; 3 s dwell; 100 uV sr1'})
s = sweep.AsyncStation(_mc)
s.add_comment('landau-fan')
s.add_comment('plan step 4; source T_0 drain B_3; voltage B_1-B_2; nominal n=-1.2..+3.2e12 cm^-2 step .025; provisional D=0 from run 5; B=0,1,1.5 then 57 inverse-B points 2..10 T; base T; Si=0 V; sr1 sensitivity 100 uV; fast/slow dwell 3/3 s; gates stay at final point, B stays 10 T')
s.ramp(k_bg.volt, float(Vb_fan[0])); s.ramp(k_tg.volt, float(Vt_fan[0]))
interruptible_sleep(10)
_followed = (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P)
for _p in _followed:
    s.fp(_p)
    s.plot('time', _p)
s.plot(k_tg.volt, sr1.X, magnet.field)
# time, B, TG, BG, Ts, Tv, Itg, Ibg, X0, P0, X1, P1.
# Trip checks add no validator/operating-limit changes and do not move hardware.
_fan_count = 0
_fan_bad_signal = 0
_fan_stop_reasons = []
_fan_field_readbacks = []
def fan_guard(station, data, writer):
    global _fan_count, _fan_bad_signal
    _fan_count += 1
    a = np.asarray(data, dtype=float)
    reasons = []
    if not np.all(np.isfinite(a)): reasons.append('nonfinite read')
    if abs(a[6]) > 1e-9 or abs(a[7]) > 1e-9: reasons.append('gate leakage >1 nA')
    if not (1.0<=a[4]<=1.5 and 0<a[5]<1.6 and abs(a[4]-a[5])<0.6): reasons.append('temperature outside base window')
    _current = a[8]/_mc['sr0_gain']
    _bad = abs(a[10]) >= 0.9*100e-6 or abs(a[8]) >= 0.9*0.02 or not (0.5e-8 <= _current <= 1.5e-8)
    _fan_bad_signal = _fan_bad_signal+1 if _bad else 0
    if _fan_bad_signal >= 3: reasons.append('3 points clipping or drain current outside 5..15 nA')
    if (_fan_count-1) % len(n_fan) == 0:
        _bread = magnet.field()
        _fan_field_readbacks.append({'row':(_fan_count-1)//len(n_fan), 'target_T':float(a[1]), 'actual_T':float(_bread)})
        writer.metadata['field_readbacks'] = list(_fan_field_readbacks)
        print('ROW PREFLIGHT', _fan_field_readbacks[-1], 'Ts/Tv', a[4:6].tolist())
        if abs(_bread-a[1]) > 0.03: reasons.append('field readback mismatch >30 mT')
        try:
            for _name in ('T_sample','T_vaporizer'):
                assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
        except Exception as exc: reasons.append('thermometry freshness: '+str(exc))
    if _fan_count == 10:
        print('FIRST 10 POINTS: I nA=',_current*1e9,'X1 uV=',a[10]*1e6,'leak pA=',a[6:8]*1e12,'T=',a[4:6])
    if reasons:
        _fan_stop_reasons.extend(reasons)
        writer.metadata['stop_reasons'] = list(_fan_stop_reasons)
        print('FAN STOP:', reasons, 'point',_fan_count,'B/TG/BG',a[1:4])
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())
fan_result = s.multimegasweep([magnet.field],[B_fan],[k_tg.volt,k_bg.volt],[Vt_fan,Vb_fan],slow_delay=3.0,fast_delay=3.0)
print('FAN END: run',fan_result.id,'interrupted',fan_result.metadata.get('interrupted'),'stop reasons',_fan_stop_reasons)
print('ACTUAL STATE: B',magnet.field(),'TG/BG/Si',k_tg.volt(),k_bg.volt(),k_si(),'Ts/Tv',T_sample(),T_vaporizer())
# No automatic return traverse; any abort requires fresh state and review.
