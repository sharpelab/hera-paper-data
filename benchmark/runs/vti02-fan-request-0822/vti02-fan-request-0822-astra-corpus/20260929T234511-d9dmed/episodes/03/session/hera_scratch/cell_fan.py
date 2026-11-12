# landau-fan-vti: electron-side frequency trajectories, run-5 calibration.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# Read-only preconditions before any instrument write; SAFETIES are never changed.
for _p, _expected in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
                      (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                      (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                      (heater.vaporizer_setpoint,(0.,100.))]:
    _actual = (float(_p.vals._min_value),float(_p.vals._max_value))
    print('validator',_p.full_name,'expected',_expected,'actual',_actual)
    assert _actual == _expected
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
for _name in ['T_sample','T_vaporizer']:
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv,_B = T_sample(),T_vaporizer(),magnet.field()
print('Expected base T 1.0..1.5 K, vaporizer <1.6 K, B near 0; actual',_Ts,_Tv,_B)
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Ts-_Tv)<.6 and abs(_B)<.05
_ranges=(heater.sample_range(),heater.vaporizer_range())
_ps=(magnet.persistent_switch_on(),magnet.output_enabled())
_si=(dc205.voltage_range(),dc205.output(),k_si(),dc205.ramp_rate)
print('Expected heaters (0,0), magnet (True,True), Si (2,1,0,.5); actual',_ranges,_ps,_si)
assert _ranges == (0,0) and all(_ps)
assert _si[:2] == (2,1) and abs(_si[2])<.01 and _si[3]==.5
print('Expected gate steps .005 V and NPLC 1; actual',k_tg.volt.step,k_bg.volt.step,k_tg.nplci(),k_bg.nplci())
assert k_tg.volt.step == .005 and k_bg.volt.step == .005
assert k_tg.nplci()==1 and k_bg.nplci()==1
print('Actual initial gates',k_tg.volt(),k_bg.volt(),'; fan sets its own gates')
_drive=(sr1.amplitude(),sr1.frequency())
print('Expected drive 1 V / 13.777 Hz; actual',_drive)
assert abs(_drive[0]-1)<1e-6 and abs(_drive[1]-13.777)<.01
for _li in [sr0,sr1]:
    print('Expected tau .3 s, slope 24 dB/oct; actual',_li.name,_li.time_constant(),_li.filter_slope())
    assert _li.time_constant()==.3 and _li.filter_slope()==24
assert WIRING == {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                  'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'
assert sr0.sensitivity()==.02

# Exactly the rounded run-6 calibration, preserving the shared n=3.2 anchor.
_fan_cal = dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
_fan_ns = np.linspace(3.2,2.8,11)
_fan_tg,_fan_bg = calc_gate_voltages(_fan_ns,np.zeros(11),**_fan_cal)
_fan_B = field_invB(1.017617880804576,6.5,250)
assert np.all(np.diff(_fan_B)>0) and max(_fan_B)<=B_SESSION_CAP
assert np.max(np.abs(np.diff(1/_fan_B))) <= 1/(2*150)
assert np.max(np.abs(np.diff(_fan_ns))) <= _fan_B[0]/(cst.h/(4*cst.e)*1e16)/2/1.2
for _param,_values in [(k_tg.volt,_fan_tg),(k_bg.volt,_fan_bg),(magnet.field,_fan_B)]:
    for _value in _values: _param.validate(float(_value))
_ncheck,_Dcheck = calc_nD(_fan_tg,_fan_bg,**_fan_cal)
assert np.allclose(_ncheck,_fan_ns) and np.max(np.abs(_Dcheck))<1e-10
print('Fan grid',len(_fan_B),'x',len(_fan_ns),'TG',min(_fan_tg),max(_fan_tg),'BG',min(_fan_bg),max(_fan_bg))

# Fixed ranges, 10 tau gate dwell, no changes to pacing/validators/heaters/Si.
sr1.sensitivity(50e-6)
assert sr1.sensitivity()==50e-6
_fan_mc=dict(meas_config)
_fan_mc.update({'Si (V)':_si[2],'sample_temperature:':_Ts,
                'calibration':_fan_cal,'sr1_gain':1.0,
                'comments':'landau-fan-vti; B_1-B_2; n 3.2 to 2.8e12 cm^-2, D=0; B 1.01761788 to 6.5 T, 250 uniform-1/B x 11 n; run-5 cal; Si=0; 10 nA; sr1 50uV; fast_delay 3 s'})
s=sweep.AsyncStation(_fan_mc)
s.add_comment('landau-fan-vti')
s.add_comment(_fan_mc['comments'])
s.add_comment('First 3 rows and every 30 min checkpoints; raw then FFT; no harmonic/pocket labels assumed; leave final B and gates for follow-up')
s.ramp(k_bg.volt,float(_fan_bg[0])); s.ramp(k_tg.volt,float(_fan_tg[0]))
interruptible_sleep(3)
# First slow-axis set positions from measured ~0 T to 1.0176 T; total traverse to 6.5 T is 47.45 min bare.
# Data: time,B,TG,BG,Ts,Tv,Itg,Ibg,sr0_X,sr0_P,sr1_X,sr1_P.
for _p in [T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P]:
    s.fp(_p)
    s.plot('time',_p)
_fan_count=0
_fan_stop=[]
def _fan_guard(station,data):
    global _fan_count
    _fan_count+=1
    _reasons=[]
    if not np.all(np.isfinite(data)): _reasons.append('nonfinite data')
    if not 1.0<=data[4]<=1.5 or not 0<data[5]<1.6: _reasons.append('temperature outside base window')
    if max(abs(data[6]),abs(data[7]))>1e-9: _reasons.append('gate leakage exceeds existing 1 nA trip')
    if not 8e-9 < data[8]/-1e6 < 12e-9: _reasons.append('drain-current anomaly')
    if abs(data[8])>.9*.02 or abs(data[10])>.9*50e-6: _reasons.append('lock-in near rail')
    if (_fan_count-1)%11==0:
        try:
            for _name in ['T_sample','T_vaporizer']:
                assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
            _actual_B=magnet.field()
            if abs(_actual_B-data[1])>.03: _reasons.append(f'field readback {_actual_B} differs from {data[1]}')
        except Exception as _error: _reasons.append(str(_error))
    if _reasons:
        _fan_stop.extend(_reasons)
        print('FAN STOP:',_reasons,'B target',data[1])
        station.interrupt_requested=True
s.register_run_after(_fan_guard,())
_fan_result=s.multimegasweep([magnet.field],[_fan_B],[k_tg.volt,k_bg.volt],
                           [_fan_tg,_fan_bg],slow_delay=1,fast_delay=3)
print('Fan returned; stop reasons:',_fan_stop)
print('Actual held state B,TG,BG,Si,T:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample())
# No automatic recovery move on an abort. On VTI an interrupt DOES NOT stop an in-progress magnet ramp.
