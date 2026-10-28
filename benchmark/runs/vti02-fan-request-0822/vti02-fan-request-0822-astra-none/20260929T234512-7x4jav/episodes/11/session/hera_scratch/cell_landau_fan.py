# Plan step 4: D*=0 Landau fan, both signs; calibration remains provisional.
# All preconditions and every planned setpoint are checked before any write.
import json
from pathlib import Path

for _label, _param, _limits in [
    ('TG', k_tg.volt, (-0.3, 1.0)), ('BG', k_bg.volt, (-1.3, 2.0)),
    ('Si ramped', dc205.smart_voltage, (-25., 25.)),
    ('Si raw', dc205.voltage, (-25., 25.)),
    ('field', magnet.field, (-10., 10.)),
    ('sample setpoint', heater.sample_setpoint, (0., 100.)),
    ('vaporizer setpoint', heater.vaporizer_setpoint, (0., 100.))]:
    _actual = (float(_param.vals._min_value), float(_param.vals._max_value))
    print(f'validator {_label}: expected {_limits}, actual {_actual}')
    assert _actual == _limits, f'SAFETIES mismatch: {_label}'
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_T0, _Tv0, _B0 = T_sample(), T_vaporizer(), magnet.field()
_Si0 = k_si()
_ranges = (heater.sample_range(), heater.vaporizer_range())
print(f'expected Ts 1.0..1.5 K, Tv 0.6..1.6 K, |B|<0.02 T, Si 0 V, heaters off; '
      f'actual {_T0:.3f}, {_Tv0:.3f} K, {_B0:+.5f} T, {_Si0:+.4f} V, {_ranges}')
assert 1.0 <= _T0 <= 1.5 and 0.6 <= _Tv0 <= 1.6 and abs(_Tv0-_T0)<0.6
assert abs(_B0)<0.02 and abs(_Si0)<0.01 and _ranges == (0,0)
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
print(f'magnet PS/output expected True/True; actual {_ps}/{_out}')
assert _ps and _out
print(f'DC205 expected RNGE2/output1/rate0.5; actual {dc205.voltage_range()}/{dc205.output()}/{dc205.ramp_rate}')
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==0.5
print(f'gate step expected 0.005/0.005 V; actual {k_tg.volt.step}/{k_bg.volt.step}; '
      f'NPLC expected 1/1, actual {k_tg.nplci()}/{k_bg.nplci()}')
assert k_tg.volt.step==0.005 and k_bg.volt.step==0.005
assert k_tg.nplci()==1 and k_bg.nplci()==1
_expected_wiring = {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                    'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print(f'hardwired expected {_expected_wiring}; actual {WIRING}')
assert WIRING==_expected_wiring and 'mux' not in globals()
assert meas_config['sr0_gain']==-1e6 and meas_config.get('sr1_gain',1)==1
assert meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'
_amp, _freq = sr1.amplitude(), sr1.frequency()
print(f'drive expected 1 V / 13.777 Hz; actual {_amp}/{_freq}')
assert abs(_amp-1.0)<0.001 and abs(_freq-13.777)<0.01
for _li in (sr0,sr1):
    _tau, _slope = _li.time_constant(), _li.filter_slope()
    print(f'{_li.name} expected tau 0.3 s / slope 24 dB; actual {_tau}/{_slope}')
    assert _tau==0.3 and _slope==24
print(f'sr0 sensitivity expected 0.020 V; actual {sr0.sensitivity()}')
assert sr0.sensitivity()==0.020
print(f'gate starting readbacks (will be set): TG={k_tg.volt():+.5f}, BG={k_bg.volt():+.5f} V')

# Explicit immutable copy of the run-5 coordinate convention. n in SI internally.
_FCAL = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
             n_offset=-0.08937933224099137e16, D_offset=-0.013e9)
_fan_cal = GateCalibration(**_FCAL)
fan_n = np.linspace(-1.2,3.2,111)*1e16
fan_D = 0.0
_qsum = cst.e*(fan_n-_FCAL['n_offset'])
_qdiff = 2*cst.epsilon_0*(fan_D-_FCAL['D_offset'])
fan_tg = (_qsum+_qdiff)/(2*_FCAL['c_tg'])
fan_bg = (_qsum-_qdiff)/(2*_FCAL['c_bg'])
fan_B = np.r_[0.,1.,1.5,field_invB(2.,5.,31),np.arange(5.25,10.001,0.25)]
assert len(fan_B)==54 and len(fan_n)==111 and np.all(np.diff(fan_B)>0)
assert np.allclose(_fan_cal.density(fan_tg,fan_bg),fan_n)
assert np.allclose(_fan_cal.displacement_field(fan_tg,fan_bg),fan_D,atol=1e-6)
for _p,_vs in ((k_tg.volt,fan_tg),(k_bg.volt,fan_bg),(magnet.field,fan_B)):
    for _v in _vs: _p.validate(float(_v))
print(f'54 x 111 = 5994 points; TG {fan_tg.min():+.6f}..{fan_tg.max():+.6f} V; '
      f'BG {fan_bg.min():+.6f}..{fan_bg.max():+.6f} V; B 0..10 T; D*=0, n* -1.2..3.2e12')
print(f'field ramp floor from {_B0:.4f} T to 10 T: {(abs(_B0)+10)*7.3:.1f} min; total budget 7h30m')

# No changes to gate pacing, limits, excitation, time constants or Si.
sr1.sensitivity(100e-6)
_fan_sens = sr1.sensitivity()
assert _fan_sens == 100e-6
fan_B_readback = qcodes.Parameter('fan_B_readback',get_cmd=magnet.field,unit='T')
fan_TG_readback = qcodes.Parameter('fan_TG_readback',get_cmd=k_tg.volt,unit='V')
fan_BG_readback = qcodes.Parameter('fan_BG_readback',get_cmd=k_bg.volt,unit='V')
mc = dict(meas_config)
mc.update({'Si (V)':_Si0,'sample_temperature:':_T0,'sr1_gain':1.0,
           'gate_calibration_SI':_FCAL,'calibration_status':'ratio/CNP from run5; absolute scale geometry prior; D-zero inferred',
           'lockin_settling':{'sr0_tau_s':0.3,'sr1_tau_s':0.3,'slope_dB':24,'point_dwell_s':3.0},
           'comments':'landau-fan D*=0; n* -1.2..3.2e12; B 0,1,1.5, inverse-B 2..5, 5.25..10 T; base; Si0'})
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('plan step 4; B_1-B_2; source T_0 drain B_3; base T; Si=0 V; D*=0; '
              'n*=-1.2..3.2e12 cm^-2 in 0.04 steps; 54 B rows x 111 gate pairs; '
              'run5 calibration provisional; sr1 100uV; 3s dwell; B end 10T; gates end high-density point')
# Column order: time, B set, TG set, BG set, followed channels below.
_fan_follow = [T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,
               fan_B_readback,fan_TG_readback,fan_BG_readback]
for _p in _fan_follow:
    s.fp(_p) # raw X stored; analysis applies metadata gains once
    s.plot('time',_p)

_fan_count = [0]
_fan_guard_failures = []
def fan_prepoint(station):
    # Freshness checked before each row's first measurement; temperatures checked every point below.
    if _fan_count[0] % len(fan_n) == 0:
        for _name in ('T_sample','T_vaporizer'):
            assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)

def fan_guard(station,data):
    # Guard runs after a completed point, before any next field command.
    a=np.asarray(data,dtype=float)
    _, b, tg, bg, ts, tv, itg, ibg, x0, p0, x1, p1, br, tgr, bgr = a
    current=x0/mc['sr0_gain']
    problems=[]
    if not np.all(np.isfinite(a)): problems.append('nonfinite data')
    if abs(itg)>1e-9 or abs(ibg)>1e-9: problems.append('gate-current >1nA')
    if not (1.0<=ts<=1.5 and 0.6<=tv<=1.6): problems.append('temperature off base')
    if not 8e-9<=current<=12e-9: problems.append('drain-current outside 8..12nA')
    if abs(x1)>=0.90*_fan_sens or abs(x0)>=0.90*0.020: problems.append('lock-in near full scale')
    if abs(br-b)>0.03: problems.append('field tracking >30mT')
    if abs(tgr-tg)>0.002 or abs(bgr-bg)>0.002: problems.append('gate tracking >2mV')
    _fan_count[0]+=1
    if problems:
        _fan_guard_failures.append((_fan_count[0],problems))
        print(f'FAN STOP point {_fan_count[0]}, B={br:.5f}: {problems}',flush=True)
        station.interrupt_requested=True
    if _fan_count[0] in (1,5,20) or _fan_count[0]%len(fan_n)==0:
        print(f'FAN CHECK point {_fan_count[0]}/5994 B={br:.5f} T '
              f'T={ts:.3f}/{tv:.3f} K I={current*1e9:.3f}nA '
              f'gate I={itg*1e12:+.1f}/{ibg*1e12:+.1f}pA X1={x1*1e6:+.3f}uV',flush=True)
s.register_run_before(fan_prepoint,())
s.register_run_after(fan_guard,())
s.ramp(k_bg.volt,float(fan_bg[0])); s.ramp(k_tg.volt,float(fan_tg[0]))
interruptible_sleep(10)
fan_result=s.multimegasweep([magnet.field],[fan_B], [k_tg.volt,k_bg.volt],[fan_tg,fan_bg],
                            slow_delay=3.,fast_delay=3.)
print(f'FAN COMPLETE file_id={fan_result.id}; interrupted={fan_result.metadata.get("interrupted")}')
print(f'actual end B={magnet.field():+.5f} T, TG={k_tg.volt():+.5f} V, '
      f'BG={k_bg.volt():+.5f} V, Si={k_si():+.4f} V; Ts/Tv={T_sample():.3f}/{T_vaporizer():.3f} K')
# Hold endpoint for analysis / possible return scan. No automatic closeout or recovery moves.
