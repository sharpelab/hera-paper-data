# Plan step 4 — two-carrier Landau fan, B_1-B_2; no safety or pacing edits.
import numpy as np
from scipy.constants import elementary_charge as _e, epsilon_0 as _eps0

# Preconditions: reads first, print actual versus expected; fail before any write.
def _fan_check(label, actual, expected, ok):
    print(f'{label}: actual={actual}; expected={expected}')
    assert ok, f'FAN PRECONDITION FAIL: {label}'

def _fan_bounds(p):
    return (float(p.vals._min_value), float(p.vals._max_value))
for _p, _limits in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
                    (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                    (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                    (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=_fan_bounds(_p)
    _fan_check(_p.full_name+' validator',_actual,_limits,_actual==_limits)
_fan_check('session caps',(B_SESSION_CAP,T_SESSION_CAP),(10.,100.),B_SESSION_CAP==10 and T_SESSION_CAP==100)
for _name in ['T_sample','T_vaporizer']:
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv=T_sample(),T_vaporizer()
_fan_check('temperature K',(_Ts,_Tv),'sample 1.0..1.5; vaporizer 0.7..1.6; difference <0.6',
           1<=_Ts<=1.5 and .7<=_Tv<=1.6 and abs(_Ts-_Tv)<.6)
_ranges=(heater.sample_range(),heater.vaporizer_range())
_fan_check('heater ranges',_ranges,(0,0),_ranges==(0,0))
_Bstart=magnet.field()
_fan_check('start B T',_Bstart,'abs(B)<0.02',abs(_Bstart)<.02)
_mag=(magnet.persistent_switch_on(),magnet.output_enabled(),magnet.is_ramping())
_fan_check('PS/output/ramping',_mag,(True,True,False),bool(_mag[0]) and bool(_mag[1]) and not _mag[2])
_gates=(k_tg.volt(),k_bg.volt(),k_si())
_fan_check('handoff TG/BG/Si V',_gates,'all zero within 1 mV',all(abs(v)<.001 for v in _gates))
_dc=(dc205.voltage_range(),dc205.output(),dc205.ramp_rate)
_fan_check('DC205 range/output/rate',_dc,(2,1,.5),_dc==(2,1,.5))
_pacing=(k_tg.volt.step,k_bg.volt.step)
_fan_check('gate steps V',_pacing,(.005,.005),_pacing==(.005,.005))
for _k in [k_tg,k_bg]:
    _nplc=_k.nplci()
    _fan_check(_k.name+' NPLC',_nplc,1,_nplc==1)
_expected_wiring={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                  'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
_fan_check('hardwired contacts',WIRING,_expected_wiring,WIRING==_expected_wiring)
_fan_check('current gain',meas_config['sr0_gain'],-1e6,meas_config['sr0_gain']==-1e6)
_drive=(sr1.amplitude(),sr1.frequency())
_fan_check('drive V/Hz',_drive,(1.,13.777),abs(_drive[0]-1)<1e-6 and abs(_drive[1]-13.777)<.01)
for _li in [sr0,sr1]:
    _filter=(_li.time_constant(),_li.filter_slope())
    _fan_check(_li.name+' tau/slope',_filter,(.3,24),_filter==(.3,24))
_fan_check('sr0 sensitivity',sr0.sensitivity(),.02,sr0.sensitivity()==.02)

# Explicit run-5 calibration, SI internally. Absolute density scale is a geometry prior.
_fan_cal=dict(c_tg=0.0027960593093052633,c_bg=0.002160696465377614,
              n_offset=-0.08937933224099137e16,D_offset=-0.013e9)
_fan_n=np.linspace(-1.2,3.2,111)*1e16
_fan_q=_e*(_fan_n-_fan_cal['n_offset'])
_fan_delta=2*_eps0*(0.-_fan_cal['D_offset'])
_fan_tg=(_fan_q+_fan_delta)/(2*_fan_cal['c_tg'])
_fan_bg=(_fan_q-_fan_delta)/(2*_fan_cal['c_bg'])
_fan_B=np.r_[0.,1.,1/np.linspace(1/2,1/10,81)]
for _p,_vec in [(k_tg.volt,_fan_tg),(k_bg.volt,_fan_bg),(magnet.field,_fan_B)]:
    for _v in _vec: _p.validate(float(_v))
    print(f'{_p.full_name} path: {_vec.min():+.6f}..{_vec.max():+.6f}; {len(_vec)} points')
assert np.allclose((_fan_cal['c_tg']*_fan_tg+_fan_cal['c_bg']*_fan_bg)/_e+_fan_cal['n_offset'],_fan_n)
assert np.allclose((_fan_cal['c_tg']*_fan_tg-_fan_cal['c_bg']*_fan_bg)/(2*_eps0)+_fan_cal['D_offset'],0,atol=1e-5)

# First instrument write; restore measurement sensitivity after operator's state0 replay.
sr1.sensitivity(100e-6)
_fan_check('sr1 sensitivity',sr1.sensitivity(),100e-6,sr1.sensitivity()==100e-6)
mc=dict(meas_config)
mc.update({'sr1_gain':1.,'Si (V)':_gates[2],'sample_temperature:':_Ts,
           'gate_calibration_SI':_fan_cal,'calibration_source':'run 5; absolute scale geometry prior',
           'nominal_D_V_per_nm':0.,'nominal_density_1e12_cm2':(_fan_n/1e16).tolist(),
           'sr0_sens':.02,'sr1_sens':100e-6,'sr0_tau_s':.3,'sr1_tau_s':.3,
           'filter_slope_dB_oct':24,'comments':'two-carrier D~0 fan; B1-B2; B 0,1,2..10 T (uniform 1/B); Si 0; 3 s dwell'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('Plan step 4: B_1-B_2; nominal n -1.20..+3.20e12 cm^-2 (111); D~0; '
              'TG/BG co-sweep; B 0,1 then 81 points 2..10 T uniform 1/B (83 rows); '
              'T base, Si 0 V; sr1 100 uV; fast delay 3 s; calibration run 5, absolute density geometry prior')
# All values stored raw; gains remain metadata for hera-watch and analysis.
# Unique column names distinguish measured readbacks from planned sweep setpoints.
_fan_B_read=qcodes.Parameter('fan_B_readback',unit='T',get_cmd=magnet.field)
_fan_TG_read=qcodes.Parameter('fan_TG_readback',unit='V',get_cmd=k_tg.volt)
_fan_BG_read=qcodes.Parameter('fan_BG_readback',unit='V',get_cmd=k_bg.volt)
_fan_follow=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,
             _fan_B_read,_fan_TG_read,_fan_BG_read]
for _p in _fan_follow:
    s.fp(_p)
    s.plot('time',_p)  # every followed channel visible, including measured readbacks
s.plot(k_tg.volt,sr1.X)
s.ramp(k_bg.volt,float(_fan_bg[0]));s.ramp(k_tg.volt,float(_fan_tg[0]))
interruptible_sleep(10)

# Layout [time,Bset,TGset,BGset, Ts,Tv,Itg,Ibg,X0,P0,X1,P1,Bread,TGread,BGread].
_fan_guard_state={'count':0,'reason':None}
def _fan_guard(station,data):
    a=np.asarray(data,dtype=float); reasons=[]
    if not np.all(np.isfinite(a)): reasons.append('non-finite readback')
    if max(abs(a[6]),abs(a[7]))>1e-9: reasons.append('gate current >1 nA')
    if not 5e-9<a[8]/mc['sr0_gain']<15e-9: reasons.append('drain current outside 5..15 nA')
    if abs(a[8])>.9*.02 or abs(a[10])>.9*100e-6: reasons.append('lock-in X >90% full scale')
    if not (1<=a[4]<=1.5 and .7<=a[5]<=1.6 and abs(a[4]-a[5])<.6): reasons.append('temperature outside base envelope')
    if abs(a[12]-a[1])>.03: reasons.append('field readback differs >30 mT')
    if max(abs(a[13]-a[2]),abs(a[14]-a[3]))>.003: reasons.append('gate readback differs >3 mV')
    if _fan_guard_state['count']%111==0:
        try:
            for name in ['T_sample','T_vaporizer']:
                assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
        except Exception as err: reasons.append('thermometry freshness: '+str(err))
    _fan_guard_state['count']+=1
    if reasons:
        _fan_guard_state['reason']='; '.join(reasons)
        print('FAN STOP:',_fan_guard_state['reason'],'Bset=',a[1],flush=True)
        station.interrupt_requested=True
s.register_run_after(_fan_guard,())
_fan_result=s.multimegasweep([magnet.field],[_fan_B],[k_tg.volt,k_bg.volt],
                            [_fan_tg,_fan_bg],slow_delay=3.,fast_delay=3.)
print('FAN RESULT',_fan_result.id,'interrupted=',_fan_result.metadata.get('interrupted'),
      'guard=',_fan_guard_state['reason'])
print('READBACK B/TG/BG/Si/Tsample/Tvap:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample(),T_vaporizer())
# Hold endpoint. No automatic field retraverse or safety/pacing changes.
