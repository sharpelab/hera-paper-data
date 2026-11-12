# Plan step 4: landau-fan, B_1-B_2, provisional D=0, both carrier signs.
# Preconditions are read-only; no instrument writes occur before all pass.
import numpy as np
from hera.analysis import GateCalibration, field_invB
_need = ['magnet','heater','sr0','sr1','k_tg','k_bg','dc205','k_si',
         'T_sample','T_vaporizer','meas_config','WIRING','B_SESSION_CAP',
         'T_SESSION_CAP','assert_thermometry_live','VTI','sweep','interruptible_sleep']
_missing = [name for name in _need if name not in globals()]
print('fan kernel bindings: missing', _missing, '(expected [])')
assert not _missing, 'instrument-carrying kernel required'
for _param, _expected in [
    (k_tg.volt,(-0.3,1.0)), (k_bg.volt,(-1.3,2.0)),
    (dc205.smart_voltage,(-25.0,25.0)),(dc205.voltage,(-25.0,25.0)),
    (magnet.field,(-10.0,10.0)),(heater.sample_setpoint,(0.0,100.0)),
    (heater.vaporizer_setpoint,(0.0,100.0))]:
    _actual=(float(_param.vals._min_value),float(_param.vals._max_value))
    print(_param.full_name, 'validator actual', _actual, 'expected', _expected)
    assert _actual == _expected
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv,_B0,_Si = T_sample(),T_vaporizer(),magnet.field(),k_si()
_hr=(heater.sample_range(),heater.vaporizer_range())
_ps=(magnet.persistent_switch_on(),magnet.output_enabled())
print('actual T_sample,T_vap,B,Si,heaters,PS/output:',_Ts,_Tv,_B0,_Si,_hr,_ps)
print('expected: sample 1.0..1.5 K, vaporizer 0.7..1.6 K within 0.6 K of sample; |B|<0.02 T; Si=0; heaters0; PS/output on')
assert 1.0 <= _Ts <= 1.5 and 0.7 <= _Tv <= 1.6 and abs(_Ts-_Tv)<0.6
assert abs(_B0)<0.02 and abs(_Si)<0.01 and _hr==(0,0) and all(_ps)
print('gate starts (will set):', k_tg.volt(), k_bg.volt())
print('DC205 range/output/rate actual:',dc205.voltage_range(),dc205.output(),dc205.ramp_rate,'expected 2/1/0.5')
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==0.5
print('TG/BG step,NPLC:',k_tg.volt.step,k_bg.volt.step,k_tg.nplci(),k_bg.nplci(),'expected .005,.005,1,1')
assert k_tg.volt.step==0.005 and k_bg.volt.step==0.005
assert k_tg.nplci()==1 and k_bg.nplci()==1
_want_wiring={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
              'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('wiring actual:',WIRING,'expected:',_want_wiring)
assert WIRING==_want_wiring and 'mux' not in globals()
_drive,_freq=sr1.amplitude(),sr1.frequency()
_tau0,_tau1=sr0.time_constant(),sr1.time_constant()
_slope0,_slope1=sr0.filter_slope(),sr1.filter_slope()
_sens0=sr0.sensitivity()
print('drive V/Hz, tau s, slopes dB/oct, sr0 sensitivity:',_drive,_freq,_tau0,_tau1,_slope0,_slope1,_sens0)
print('expected 1 V/13.777 Hz; 0.3s both; 24dB/oct both; sr0 20mV')
assert abs(_drive-1.0)<1e-6 and abs(_freq-13.777)<0.01
assert _tau0==0.3 and _tau1==0.3 and _slope0==24 and _slope1==24 and abs(_sens0-0.02)<1e-9
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'

# Session run5 ratio and offsets. Absolute scale remains a geometry prior.
_fcal=GateCalibration(0.0027960593093052633,0.002160696465377614,
                      n_offset=-0.08937933224099137e16,D_offset=-0.013e9)
_nvec=np.linspace(-1.2,3.2,111)*1e16
# Invert the documented SI GateCalibration equations directly.
from scipy.constants import e, epsilon_0
_Vt=(e*(_nvec-_fcal.n_offset)/2 + epsilon_0*(0-_fcal.D_offset))/_fcal.c_tg
_Vb=(e*(_nvec-_fcal.n_offset)/2 - epsilon_0*(0-_fcal.D_offset))/_fcal.c_bg
_Bvec=np.concatenate(([0.0],field_invB(1.5,6.0,61),np.linspace(6.25,10.0,16)))
assert len(_Bvec)==78 and len(_nvec)==111
assert np.allclose(_fcal.density(_Vt,_Vb),_nvec,rtol=1e-12,atol=10)
assert np.max(np.abs(_fcal.displacement_field(_Vt,_Vb)))<1e-6
for _param,_values in [(k_tg.volt,_Vt),(k_bg.volt,_Vb),(magnet.field,_Bvec)]:
    for _value in _values: _param.validate(float(_value))
print('fan voltage bounds TG:',_Vt.min(),_Vt.max(),'BG:',_Vb.min(),_Vb.max())
print('fan grid:',len(_Bvec),'x',len(_nvec),'= 8658 points; dwell 3s, B ramp floor 73 min, estimated 10h')

# First write: sensitivity only; no limit or pacing changes.
sr1.sensitivity(100e-6)
_sens1=sr1.sensitivity()
assert abs(_sens1-100e-6)<1e-12
_mc=dict(meas_config)
_mc.update({'sr1_gain':1.0,'Si (V)':_Si,'sample_temperature:':_Ts,
            'comments':'landau-fan B1-B2: B0 then 1.5-6T inverse-B 61 rows, 6.25-10T 0.25T; nominal nA -1.2..3.2e12/0.04, provisional D0, Si0; run5 ratio, absolute geometry prior',
            'gate_calibration':{'source_run':5,'c_tg':_fcal.c_tg,'c_bg':_fcal.c_bg,'n_offset_m-2':_fcal.n_offset,'D_offset_V/m':_fcal.D_offset,'absolute_scale':'geometry prior'},
            'acquisition':{'sr0_tau_s':_tau0,'sr1_tau_s':_tau1,'filter_slope_db_oct':24,'sr0_sensitivity_V':_sens0,'sr1_sensitivity_V':_sens1,'drive_V':_drive,'drive_Hz':_freq,'fast_delay_s':3.0}})
s=sweep.AsyncStation(_mc)
s.add_comment('landau-fan')
s.add_comment(_mc['comments'])
s.ramp(k_tg.volt,float(_Vt[0])); s.ramp(k_bg.volt,float(_Vb[0]))
interruptible_sleep(10)
# Columns: time,Bset,TGset,BGset,Tsample,Tvap,Itg,Ibg,X0,P0,X1,P1,Bread
_follow=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,magnet.field]
for _p in _follow:
    s.fp(_p)
    s.plot('time',_p)
s.plot(k_tg.volt,sr1.X)

_fan_guard={'points':0,'reason':None}
def _fan_after(station,data):
    _fan_guard['points']+=1
    _j=_fan_guard['points']
    _b,_ts,_tv,_itg,_ibg,_x0,_x1,_br=map(float,[data[1],data[4],data[5],data[6],data[7],data[8],data[10],data[12]])
    _reasons=[]
    if not np.all(np.isfinite(np.asarray(data,dtype=float))): _reasons.append('nonfinite data')
    if abs(_itg)>1e-9 or abs(_ibg)>1e-9: _reasons.append('gate current >1nA (existing session trip)')
    if not (1.0<=_ts<=1.5 and 0.7<=_tv<=1.6): _reasons.append('temperature outside base window')
    if abs(_br-_b)>0.03: _reasons.append('field readback mismatch >30mT')
    if abs(_x0)>=0.9*_sens0 or abs(_x1)>=0.9*_sens1: _reasons.append('lock-in headroom <10%')
    if not 8e-9<=_x0/_mc['sr0_gain']<=12e-9: _reasons.append('drain current outside 8..12nA')
    if _j==10 or _j%len(_nvec)==0:
        print(f'FAN CHECK point {_j}/8658: B={_br:.4f} T, T={_ts:.3f} K, I={_x0/_mc["sr0_gain"]*1e9:.3f} nA, gates I={_itg*1e12:.1f}/{_ibg*1e12:.1f} pA')
    if _j%len(_nvec)==0:
        try:
            for _name in ('T_sample','T_vaporizer'):
                assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
        except Exception as _err: _reasons.append(str(_err))
    if _reasons:
        _fan_guard['reason']='; '.join(_reasons)
        print('FAN STOP:',_fan_guard['reason'])
        station.interrupt_requested=True
s.register_run_after(_fan_after,())
_fan_result=s.multimegasweep([magnet.field],[_Bvec],[k_tg.volt,k_bg.volt],[_Vt,_Vb],slow_delay=3.0,fast_delay=3.0)
print('FAN END:', 'INTERRUPTED' if _fan_result.metadata.get('interrupted') else 'COMPLETE','run',_fan_result.id,'guard',_fan_guard)
print('actual endpoint B,TG,BG,Si,Tsample,Tvap:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample(),T_vaporizer())
# Hold endpoint for analysis. No automatic field return or retry after any stop.
