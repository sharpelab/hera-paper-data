# Plan step 4 — landau-fan; read-only preflight before any instrument write.
import numpy as np
import time
from scipy.constants import e, epsilon_0
from hera.analysis import field_invB

# Gate B: compare every committed validator to the card; do not change any.
for _p, _expected in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
        (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
        (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
        (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print('validator',_p.full_name,'expected',_expected,'actual',_actual)
    assert _actual == _expected, 'SAFETIES mismatch: '+_p.full_name
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
for _name in ['T_sample','T_vaporizer']:
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv,_B,_Si=T_sample(),T_vaporizer(),magnet.field(),k_si()
_ranges=(heater.sample_range(),heater.vaporizer_range())
_ps,_output=magnet.persistent_switch_on(),magnet.output_enabled()
print(f'preflight: sample {_Ts:.3f} K expected 1.0..1.5; vaporizer {_Tv:.3f} K expected <1.6 and within .6 K of sample; B {_B:+.5f} T expected |B|<.02; Si {_Si:+.4f} V expected 0')
print('heater ranges expected (0,0), actual',_ranges,'PS/output expected True/True actual',_ps,_output)
print('starting TG/BG (will be set)',k_tg.volt(),k_bg.volt())
assert 1.0<=_Ts<=1.5 and 0<_Tv<1.6 and abs(_Ts-_Tv)<.6
assert abs(_B)<.02 and abs(_Si)<.01 and _ranges==(0,0) and _ps and _output
print('DC205 range/output expected 2/1 actual',dc205.voltage_range(),dc205.output())
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==.5
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('gate step expected .005/.005 actual',k_tg.volt.step,k_bg.volt.step,'NPLC expected 1/1 actual',k_tg.nplci(),k_bg.nplci())
assert k_tg.volt.step==.005 and k_bg.volt.step==.005
assert k_tg.nplci()==1 and k_bg.nplci()==1
_amp,_freq=sr1.amplitude(),sr1.frequency()
_tau0,_tau1=sr0.time_constant(),sr1.time_constant()
_slope0,_slope1=sr0.filter_slope(),sr1.filter_slope()
_sens0=sr0.sensitivity()
print('drive expected 1 V/13.777 Hz actual',_amp,_freq,'tau expected .3/.3 actual',_tau0,_tau1,'slopes expected 24/24 actual',_slope0,_slope1,'sr0 sensitivity expected .02 actual',_sens0)
assert abs(_amp-1)<1e-6 and abs(_freq-13.777)<.01
assert (_tau0,_tau1)==(.3,.3) and (_slope0,_slope1)==(24,24) and _sens0==.02

# Region-A run-5 calibration: capacitances F/m2, offsets in display units.
# Absolute n and D scale retain geometry uncertainty; voltages are authoritative.
_fcal=dict(c_tg=0.0027960593093052633,c_bg=0.002160696465377614,
           n_offset=-0.08937933224099137,D_offset=-0.013)
_n=np.linspace(-1.20,3.20,111)  # 1e12 cm^-2
_q=e*(_n-_fcal['n_offset'])*1e16
_d=2*epsilon_0*(0-_fcal['D_offset'])*1e9
_vtg=(_q+_d)/(2*_fcal['c_tg']); _vbg=(_q-_d)/(2*_fcal['c_bg'])
_Bvec=np.r_[0.,field_invB(2.,6.,55),np.linspace(6.2,10.,20)]
assert np.all(np.diff(_Bvec)>0) and _Bvec[-1]<=10
assert _vtg.min()>=-.3 and _vtg.max()<=1 and _vbg.min()>=-1.3 and _vbg.max()<=2
for _param,_values in [(k_tg.volt,_vtg),(k_bg.volt,_vbg),(magnet.field,_Bvec)]:
    for _value in _values: _param.validate(float(_value))
print(f'fan: {len(_Bvec)}x{len(_n)}={len(_Bvec)*len(_n)} points; TG {_vtg[0]:+.6f}..{_vtg[-1]:+.6f}, BG {_vbg[0]:+.6f}..{_vbg[-1]:+.6f} V; D nominal 0; field monotonic 0->10 T')
print('bare ramp floor 10 T * 7.3 min/T = 73 min; 3 s dwell = 10 tau; estimate 10 h including read/turnaround overhead and contingency')

# Sole acquisition change: expand Rxx sensitivity after state0 restored 2 uV.
sr1.sensitivity(100e-6)
_sens1=sr1.sensitivity()
assert _sens1==100e-6
_mc=dict(meas_config)
_mc.update({'sr0_gain':-1e6,'sr1_gain':1.0,'Si (V)':_Si,'sample_temperature:':_Ts,
    'calibration_run':5,'calibration':_fcal,'density_units':'1e12 cm^-2',
    'D_units':'V/nm','D_nominal':0.0,'n_nominal':_n.tolist(),
    'density_scale_status':'geometry anchor; ratio and offsets from run 5; D-zero provisional',
    'sr0_sensitivity':_sens0,'sr1_sensitivity':_sens1,'tau_s':[_tau0,_tau1],
    'filter_slope_db_oct':[_slope0,_slope1],
    'comments':'landau-fan B_1-B_2; n -1.20..3.20e12, D nominal 0, Si 0, base; B 0 baseline then 2..10 T; see plan step 4'})
s=sweep.AsyncStation(_mc)
s.add_comment('landau-fan')
s.add_comment('plan step 4; B_1-B_2; n=-1.20..+3.20 x1e12 cm^-2 (111 pts); D=0 nominal; run-5 calibration, geometry absolute scale; B=0 then 2..6 T (55 uniform-1/B) then 6.2..10 T (.2 T); Si=0 V; 3 s dwell; sr1=100 uV; TG/BG pacing unchanged')
_follow=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,
         magnet.field,k_tg.volt,k_bg.volt,k_si]
for _p in _follow:
    s.fp(_p)  # raw signals, gains applied only by analysis
    s.plot('time',_p)
_idx={p.full_name:j+4 for j,p in enumerate(_follow)} # time,Bset,TGset,BGset precede followed channels
_fan_guard={'points':0,'stop':None}

def _fan_before(station):
    # Once per density row: stop before acquiring if thermometry is stale.
    if _fan_guard['points'] % len(_n)==0:
        for name in ['T_sample','T_vaporizer']:
            try:
                assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
            except Exception as exc:
                _fan_guard['stop']='thermometry freshness: '+str(exc)
                print('FAN STOP:',_fan_guard['stop'])
                station.interrupt_requested=True

def _fan_after(station,data):
    a=np.asarray(data,float)
    get=lambda p: float(a[_idx[p.full_name]])
    _fan_guard['points']+=1
    reasons=[]
    if not np.all(np.isfinite(a)): reasons.append('nonfinite readback')
    if max(abs(get(k_tg.curr)),abs(get(k_bg.curr)))>1e-9: reasons.append('gate leakage >1 nA')
    if not 1.0<=get(T_sample)<=1.5: reasons.append('sample off base')
    if not 0<get(T_vaporizer)<1.6 or abs(get(T_sample)-get(T_vaporizer))>=.6: reasons.append('vaporizer off base')
    if abs(get(sr0.X))>.90*_sens0 or abs(get(sr1.X))>.90*_sens1: reasons.append('lock-in >90% full scale')
    if not 8e-9<=get(sr0.X)/-1e6<=11e-9: reasons.append('drain current outside 8..11 nA')
    if abs(get(magnet.field)-a[1])>.02: reasons.append('field readback mismatch >20 mT')
    if abs(get(k_tg.volt)-a[2])>.003 or abs(get(k_bg.volt)-a[3])>.003: reasons.append('gate readback mismatch >3 mV')
    if abs(get(k_si))>.01: reasons.append('Si not zero')
    if reasons:
        _fan_guard['stop']='; '.join(reasons)
        print('FAN STOP after point',_fan_guard['points'],'B',a[1],_fan_guard['stop'])
        station.interrupt_requested=True
s.register_run_before(_fan_before,())
s.register_run_after(_fan_after,())
# s handles every gate set via committed driver pacing, including row flyback.
_fan_result=s.multimegasweep([magnet.field],[_Bvec],[k_tg.volt,k_bg.volt],[_vtg,_vbg],
                            slow_delay=3.,fast_delay=3.)
print('FAN END run',_fan_result.id,'interrupted',_fan_result.metadata.get('interrupted'),
      'guard',_fan_guard,'B actual',magnet.field(),'TG/BG actual',k_tg.volt(),k_bg.volt(),
      'Si',k_si(),'T sample/vaporizer',T_sample(),T_vaporizer())
# Hold endpoint. No automatic flyback, heater change, Si ramp, or field return.
