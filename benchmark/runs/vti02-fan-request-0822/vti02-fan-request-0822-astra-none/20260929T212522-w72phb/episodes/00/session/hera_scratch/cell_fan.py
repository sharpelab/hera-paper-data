# Plan step 4: Landau fan, run-5 empirical gate line, geometry-anchored density.
# Preconditions are read-only; fail before any set if inherited state mismatches.
import json
from pathlib import Path

def fan_expect(label, actual, expected, ok):
    print(f'{label}: actual={actual}, expected={expected}')
    assert ok, f'FAN PRECONDITION FAIL: {label}'

for _p, _limits in [(k_tg.volt,(-0.3,1.0)), (k_bg.volt,(-1.3,2.0)),
                    (dc205.smart_voltage,(-25.,25.)), (dc205.voltage,(-25.,25.)),
                    (magnet.field,(-10.,10.)), (heater.sample_setpoint,(0.,100.)),
                    (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    fan_expect(_p.full_name+' validator',_actual,_limits,_actual==_limits)
fan_expect('session caps',(B_SESSION_CAP,T_SESSION_CAP),(10.,100.),B_SESSION_CAP==10. and T_SESSION_CAP==100.)
_card_wiring={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
              'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
fan_expect('wiring',WIRING,_card_wiring,WIRING==_card_wiring)
fan_expect('gate aliases',(k_tg.name,k_bg.name,k_si.full_name),'card role bindings',
           k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage)
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv,_B0=T_sample(),T_vaporizer(),magnet.field()
fan_expect('sample T',_Ts,'1.0..1.5 K',1.0<=_Ts<=1.5)
fan_expect('vaporizer T',_Tv,'0<T<1.6 K, within 0.6 K of sample',0<_Tv<1.6 and abs(_Ts-_Tv)<0.6)
_hr=(heater.sample_range(),heater.vaporizer_range())
fan_expect('heater ranges',_hr,(0,0),_hr==(0,0))
fan_expect('handoff B',_B0,'0 T +/-0.02 T',abs(_B0)<0.02)
_ps=(magnet.persistent_switch_on(),magnet.output_enabled())
fan_expect('magnet switch/output',_ps,(True,True),all(_ps))
_si=(dc205.voltage_range(),dc205.output(),k_si(),dc205.ramp_rate)
fan_expect('Si range/output/voltage/rate',_si,'2 / on / 0 V / 0.5 V/s',_si[0]==2 and _si[1]==1 and abs(_si[2])<0.01 and _si[3]==0.5)
_steps=(k_tg.volt.step,k_bg.volt.step)
fan_expect('gate steps',_steps,(0.005,0.005),_steps==(0.005,0.005))
print('gate start readback',k_tg.volt(),k_bg.volt(),'V; cell will set both gates')
assert_keithley_state(k_tg,rangei=1.05e-6)
assert_keithley_state(k_bg,rangei=1.05e-6)
_nplc=(k_tg.nplci(),k_bg.nplci())
fan_expect('NPLC',_nplc,(1.,1.),_nplc==(1.,1.))
_drive=(sr1.amplitude(),sr1.frequency())
fan_expect('drive amplitude/frequency',_drive,'1 V / 13.777 Hz',abs(_drive[0]-1.)<1e-6 and abs(_drive[1]-13.777)<0.01)
_taus=(sr0.time_constant(),sr1.time_constant())
_slopes=(sr0.filter_slope(),sr1.filter_slope())
fan_expect('lock-in tau',_taus,(0.3,0.3),_taus==(0.3,0.3))
fan_expect('lock-in filter slopes',_slopes,(24,24),_slopes==(24,24))
_sens0=sr0.sensitivity()
fan_expect('current sensitivity',_sens0,0.02,_sens0==0.02)
fan_expect('channel metadata',(meas_config['sr0_gain'],meas_config['bias_resistor'],meas_config['bias_channel']),
           'gain -1e6 / 100 Mohm / sr1',meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1')

# SI conversion, avoiding mixed units in gate helpers. JSON offsets are e12/cm2 and V/nm.
_fan_cal=json.loads(Path('hera_scratch/cal_run5.json').read_text())
assert _fan_cal['run']==5
_nvec=np.linspace(-1.2,3.2,111)
_charge=cst.e*(_nvec-_fan_cal['n_offset'])*1e16
_diff=2*cst.epsilon_0*(0.-_fan_cal['D_offset'])*1e9
_vtg=(_charge+_diff)/(2*_fan_cal['c_tg'])
_vbg=(_charge-_diff)/(2*_fan_cal['c_bg'])
_Bvec=np.r_[0.,field_invB(2.,10.,65)]
for _p,_v in [(k_tg.volt,_vtg),(k_bg.volt,_vbg),(magnet.field,_Bvec)]:
    for _x in _v: _p.validate(float(_x))
assert np.all(np.diff(_Bvec)>0)
print('FAN grid:',len(_Bvec),'rows x',len(_nvec),'points;',
      'TG endpoints',_vtg[[0,-1]],'BG endpoints',_vbg[[0,-1]],'B endpoints',_Bvec[[0,-1]])

# Sensitivity is acquisition state, not a safety limit; no pacing/validators touched.
sr1.sensitivity(100e-6)
_sens1=sr1.sensitivity()
assert _sens1==100e-6
mc=dict(meas_config)
mc.update({'Si (V)':_si[2],'sample_temperature:':_Ts,'sr1_gain':1.,
           'gate_calibration_run5':_fan_cal,'density_units':'1e12 cm^-2; geometry-anchored',
           'nominal_density_vector':_nvec.tolist(),'nominal_D_V_per_nm':0.,
           'lockin_tau_s':list(_taus),'lockin_filter_dB_oct':list(_slopes),
           'tg_nplci':_nplc[0],'bg_nplci':_nplc[1],
           'comments':'landau-fan: B1-B2, D nominal 0, n -1.2..3.2e12 in .04; B=0 then 65 uniform inverse-B rows 2..10 T; Si 0; 3s dwell; sr1 100uV; cal run5'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('Plan step 4; B_1-B_2; nominal D=0 V/nm, n=-1.2..+3.2e12 cm^-2 (111); B=0 plus 2..10 T (65 uniform-in-1/B); TG/BG co-swept; Si=0 V; base T; run-5 ratio, geometry absolute scale; 3s dwell, 3s row settle; sr1=100uV')
s.ramp(k_tg.volt,float(_vtg[0])); s.ramp(k_bg.volt,float(_vbg[0]))
interruptible_sleep(10)
# Layout: time,Bset,TGset,BGset,Ts,Tv,Itg,Ibg,X0,P0,X1,P1,Bread,TGread,BGread.
_follow=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,
         magnet.field,k_tg.volt,k_bg.volt]
for _p in _follow:
    s.fp(_p)
    s.plot('time',_p)
s.plot(k_tg.volt,magnet.field,sr1.X)
_fan_counter=[0]
_fan_trip=[]

def fan_guard(station,data):
    _a=np.asarray(data,dtype=float)
    _reasons=[]
    if not np.all(np.isfinite(_a)): _reasons.append('nonfinite readback')
    if not (1.0<=_a[4]<=1.5 and 0<_a[5]<1.6 and abs(_a[4]-_a[5])<0.6): _reasons.append('base temperature')
    if max(abs(_a[6]),abs(_a[7]))>1e-9: _reasons.append('existing 1nA leakage trip')
    _I=_a[8]/mc['sr0_gain']
    if not 0.5e-8<_I<1.5e-8: _reasons.append('drain current outside 5..15nA')
    if abs(_a[8])>=0.9*_sens0 or abs(_a[10])>=0.9*_sens1: _reasons.append('lock-in headroom <10%')
    if abs(_a[12]-_a[1])>0.03: _reasons.append('field tracking >30mT')
    if abs(_a[13]-_a[2])>0.01 or abs(_a[14]-_a[3])>0.01: _reasons.append('gate tracking >10mV')
    if _fan_counter[0]%len(_nvec)==0:
        try:
            for _name in ('T_sample','T_vaporizer'):
                assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
        except Exception as _e: _reasons.append('thermometry stale: '+str(_e))
    _fan_counter[0]+=1
    if _fan_counter[0] in (5,len(_nvec)) or _reasons:
        print('FAN CHECK',_fan_counter[0],'B',_a[12],'I_nA',_I*1e9,'sr1_X_uV',_a[10]*1e6,'issues',_reasons,flush=True)
    if _reasons:
        _fan_trip.extend(_reasons)
        station.interrupt_requested=True
        print('FAN STOP: inspect actual state; no automatic recovery. CAEN can continue last commanded ramp.',flush=True)
s.register_run_after(fan_guard,())
_fan_result=s.multimegasweep([magnet.field],[_Bvec],[k_tg.volt,k_bg.volt],[_vtg,_vbg],
                            slow_delay=3.,fast_delay=3.)
print('FAN COMPLETE run',_fan_result.id,'B',magnet.field(),'TG',k_tg.volt(),'BG',k_bg.volt(),
      'Si',k_si(),'Ts',T_sample(),'Tv',T_vaporizer())
