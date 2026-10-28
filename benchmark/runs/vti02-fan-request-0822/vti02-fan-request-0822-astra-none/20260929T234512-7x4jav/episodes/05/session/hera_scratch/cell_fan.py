# Plan step 4: fixed provisional D=0 Landau fan, hardwired B_1-B_2.
# Read-only preconditions precede every instrument write.
import json
from pathlib import Path
from scipy.constants import e, epsilon_0

def fan_require(label, actual, expected, ok):
    print(f'{label}: expected {expected}; actual {actual}')
    assert ok, f'PRECONDITION FAIL: {label}'

for p, bounds in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
                  (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                  (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                  (heater.vaporizer_setpoint,(0.,100.))]:
    actual=(float(p.vals._min_value),float(p.vals._max_value))
    fan_require(p.full_name+' validator',actual,bounds,actual==bounds)
fan_require('session caps',(B_SESSION_CAP,T_SESSION_CAP),(10,100),B_SESSION_CAP==10 and T_SESSION_CAP==100)
fan_require('gate aliases',(k_tg.name,k_bg.name,k_si.full_name),'card aliases',
            k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage)
for key in ('T_sample','T_vaporizer'):
    assert_thermometry_live(key,VTI.temp_logfile_candidates[key],max_age=15,max_period=12)
_ts,_tv,_b=T_sample(),T_vaporizer(),magnet.field()
fan_require('sample T',_ts,'1.0..1.5 K',1.0<=_ts<=1.5)
fan_require('vaporizer T',_tv,'<1.6 K and within 0.6 K of sample',0<_tv<1.6 and abs(_tv-_ts)<0.6)
fan_require('initial field',_b,'0 T +/-0.02 T',abs(_b)<0.02)
_hr=(heater.sample_range(),heater.vaporizer_range())
fan_require('heater ranges',_hr,(0,0),_hr==(0,0))
_ms=(magnet.persistent_switch_on(),magnet.output_enabled())
fan_require('magnet PS/output',_ms,(True,True),all(_ms))
_si=(dc205.voltage_range(),dc205.output(),k_si(),dc205.ramp_rate)
fan_require('Si range/output/V/rate',_si,'2 / 1 / 0 V / 0.5 V/s',_si[:2]==(2,1) and abs(_si[2])<0.01 and _si[3]==0.5)
_pacing=(k_tg.volt.step,k_bg.volt.step)
fan_require('Keithley steps',_pacing,(0.005,0.005),_pacing==(0.005,0.005))
_nplc=(k_tg.nplci(),k_bg.nplci())
fan_require('gate NPLC',_nplc,(1,1),_nplc==(1,1))
_w={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
    'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
fan_require('hardwired contacts',WIRING,_w,WIRING==_w and 'mux' not in globals())
_drive=(sr1.amplitude(),sr1.frequency()); _tau=(sr0.time_constant(),sr1.time_constant())
_slopes=(sr0.filter_slope(),sr1.filter_slope())
fan_require('drive V/Hz',_drive,(1.,13.777),abs(_drive[0]-1.)<1e-6 and abs(_drive[1]-13.777)<0.001)
fan_require('lock-in tau/slope',(_tau,_slopes),'0.3 s / 24 dB both',_tau==(0.3,0.3) and _slopes==(24,24))
_s0=sr0.sensitivity(); fan_require('current sensitivity',_s0,0.02,_s0==0.02)
print('actual starting TG/BG:',k_tg.volt(),k_bg.volt(),'; both will be set to first fan point')

# Explicit SI inversion of GateCalibration; density labels remain geometry anchored.
FAN_CAL=json.loads((Path(main_dir)/'hera_scratch'/'cal_run5.json').read_text())
assert FAN_CAL['run']==5
fan_n=np.linspace(-1.2,3.2,177) # 1e12 cm^-2
fan_D=0.0 # V/nm
fan_tg=(e*(fan_n-FAN_CAL['n_offset'])*1e16+2*epsilon_0*(fan_D-FAN_CAL['D_offset'])*1e9)/(2*FAN_CAL['c_tg'])
fan_bg=(e*(fan_n-FAN_CAL['n_offset'])*1e16-2*epsilon_0*(fan_D-FAN_CAL['D_offset'])*1e9)/(2*FAN_CAL['c_bg'])
fan_B=np.r_[0.,field_invB(2.,10.,51)]
_fcal=GateCalibration(FAN_CAL['c_tg'],FAN_CAL['c_bg'],FAN_CAL['n_offset']*1e16,FAN_CAL['D_offset']*1e9)
assert np.allclose(_fcal.density(fan_tg,fan_bg)*1e-16,fan_n)
assert np.max(abs(_fcal.displacement_field(fan_tg,fan_bg)))<1.
for p,vs in ((k_tg.volt,fan_tg),(k_bg.volt,fan_bg),(magnet.field,fan_B)):
    for v in vs: p.validate(float(v))
print('planned TG/BG endpoints:',fan_tg[[0,-1]],fan_bg[[0,-1]],'B rows',len(fan_B),'density points',len(fan_n))

# No change to pacing, validators, bias, heater, or Si.
sr1.sensitivity(100e-6) # 10 kohm nominal FS; run 5 max 2.9 kohm
mc=dict(meas_config)
mc.update({'sr1_gain':1.,'Si (V)':_si[2],'sample_temperature:':_ts,
 'calibration':FAN_CAL,'nominal_n_1e12_cm2':fan_n.tolist(),'nominal_D_V_nm':fan_D,
 'lockin_tau_s':list(_tau),'lockin_slope_dB':list(_slopes),
 'comments':'landau-fan: provisional D=0; n=-1.2..3.2e12, 177 pts; B=0 then 2..10 T uniform 1/B, 51 pts; Si=0; base T; calibration run5'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('plan4; B_1-B_2; n=-1.2..+3.2e12 cm^-2, step0.025e12; D=0 provisional; TG=-0.277033..0.983594 V; BG=-0.465040..1.166281 V; B=0 plus 2..10 T uniform 1/B (51); Si=0 V; dwell3s; sr1=100uV; absolute density geometry anchored')
followed=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P]
for p in followed:
    s.fp(p)
    s.plot('time',p)
# Grid columns [time,B,TG,BG,*followed], raw X retained (gains applied in analysis).
_fan_state={'points':0,'bad_signal':0,'reason':None}
_fan_nf=len(fan_n)
def fan_before(station):
    if _fan_state['points']%_fan_nf==0:
        for key in ('T_sample','T_vaporizer'):
            assert_thermometry_live(key,VTI.temp_logfile_candidates[key],max_age=15,max_period=12)
        actual=magnet.field(); expected=fan_B[_fan_state['points']//_fan_nf]
        print(f'ROW precondition measured B={actual:+.5f} T, expected {expected:+.5f} T')
        if abs(actual-expected)>0.03:
            _fan_state['reason']='field readback mismatch'
            station.interrupt_requested=True

def fan_after(station,data):
    vals=dict(zip([p.full_name for p in followed],map(float,data[4:])))
    ts,tv=vals[T_sample.full_name],vals[T_vaporizer.full_name]
    ig=max(abs(vals[k_tg.curr.full_name]),abs(vals[k_bg.curr.full_name]))
    ix=vals[sr0.X.full_name]/mc['sr0_gain']; vx=vals[sr1.X.full_name]
    bad=(not np.isfinite(ix+vx)) or not (8e-9<ix<12e-9) or abs(vx)>0.9*100e-6
    _fan_state['bad_signal']=_fan_state['bad_signal']+1 if bad else 0
    reason=None
    if not np.all(np.isfinite(data)): reason='nonfinite data'
    elif ig>1e-9: reason='gate leakage >1 nA'
    elif not (1.0<=ts<=1.5 and 0<tv<1.6 and abs(ts-tv)<0.6): reason='temperature outside base envelope'
    elif _fan_state['bad_signal']>=3: reason='three consecutive clipped/current-collapse points'
    _fan_state['points']+=1
    if reason:
        _fan_state['reason']=reason
        print('FAN STOP:',reason,'B/TG/BG',data[1:4],'I',ix,'V',vx,'leak',ig)
        station.interrupt_requested=True
    if _fan_state['points']%_fan_nf==0:
        print('ROW COMPLETE',_fan_state['points']//_fan_nf,'/',len(fan_B),'B',data[1],flush=True)
s.register_run_before(fan_before,())
s.register_run_after(fan_after,())
s.ramp(k_bg.volt,float(fan_bg[0])); s.ramp(k_tg.volt,float(fan_tg[0]))
interruptible_sleep(10)
fan_result=s.multimegasweep([magnet.field],[fan_B],[k_tg.volt,k_bg.volt],[fan_tg,fan_bg],slow_delay=3.,fast_delay=3.)
print('FAN COMPLETE: readbacks B/TG/BG/Si/Ts/Tv',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample(),T_vaporizer())
# Hold the endpoint for an informed down-field follow-up; no automatic retraverse.
