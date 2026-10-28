# landau-fan-vti: limited hole-side density-dispersion test, run-7 anchor.
import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions: all reads before any write. Same-kernel SAFETIES cell 18 is committed.
def _fan_expect(label, actual, expected, ok):
    print(f'{label}: expected {expected}; actual {actual}')
    assert ok, f'fan precondition failed: {label}'
for _p,_lim in ((k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),
                (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                (heater.vaporizer_setpoint,(0.,100.))):
    _got=(float(_p.vals._min_value),float(_p.vals._max_value))
    _fan_expect(_p.full_name+' validator',_got,_lim,_got==_lim)
_fan_expect('session caps',(B_SESSION_CAP,T_SESSION_CAP),(10,100),B_SESSION_CAP==10 and T_SESSION_CAP==100)
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_ts,_tv=T_sample(),T_vaporizer()
_fan_expect('sample T',_ts,'1.0..1.5 K',1.0<=_ts<=1.5)
_fan_expect('vaporizer T',_tv,'<1.6 K, within 0.6 K of sample',0<_tv<1.6 and abs(_tv-_ts)<.6)
_hr=(heater.sample_range(),heater.vaporizer_range())
_fan_expect('heater ranges',_hr,(0,0),_hr==(0,0))
_b=magnet.field(); _ps=magnet.persistent_switch_on(); _out=magnet.output_enabled()
_fan_expect('field',_b,'handoff 0 T, tolerance 0.05 T',abs(_b)<.05)
_fan_expect('PS/output',(_ps,_out),(True,True),_ps and _out)
_si=(dc205.voltage_range(),dc205.output(),k_si())
_fan_expect('Si range/output/V',_si,'2 / 1 / 0 V',_si[0]==2 and _si[1]==1 and abs(_si[2])<.01)
_fan_expect('pacing',(k_tg.volt.step,k_bg.volt.step,dc205.ramp_rate),(.005,.005,.5),k_tg.volt.step==.005 and k_bg.volt.step==.005 and dc205.ramp_rate==.5)
_fan_expect('NPLC',(k_tg.nplci(),k_bg.nplci()),(1,1),k_tg.nplci()==1 and k_bg.nplci()==1)
_fan_expect('aliases',(k_tg is k_2400_tg,k_bg is k_2400_bg,k_si is dc205.smart_voltage),(True,True,True),k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage)
_wc={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
_fan_expect('hardwired contacts',WIRING,_wc,WIRING==_wc and 'mux' not in globals())
_fan_expect('bias gain/config',(meas_config['sr0_gain'],meas_config['bias_channel'],meas_config['bias_resistor']),(-1e6,'sr1',1e8),meas_config['sr0_gain']==-1e6 and meas_config['bias_channel']=='sr1' and meas_config['bias_resistor']==1e8)
for _li in (sr0,sr1):
    _tc,_slope=_li.time_constant(),_li.filter_slope()
    _fan_expect(_li.name+' tau/slope',(_tc,_slope),(.3,24),_tc==.3 and _slope==24)
_drive,_freq=sr1.amplitude(),sr1.frequency()
_fan_expect('drive',(_drive,_freq),'1 V / 13.777 Hz',abs(_drive-1)<.001 and abs(_freq-13.777)<.01)
_fan_expect('sr0 sensitivity',sr0.sensitivity(),.02,sr0.sensitivity()==.02)
print('Actual initial gates:',k_tg.volt(),k_bg.volt(),'; field:',_b)

_fan_cal=dict(c_tg=.0027960593093052633,c_bg=.002160696465377614,n_offset=-.08937933224099137,D_offset=-.013)
_fan_ns=np.linspace(-1.2,-.95,9)
_fan_vt,_fan_vb=calc_gate_voltages(_fan_ns,np.zeros(9),**_fan_cal)
_fan_B=1/np.linspace(1/.7138767261704282,1/6.,66)
for _p,_vs in ((k_tg.volt,_fan_vt),(k_bg.volt,_fan_vb),(magnet.field,_fan_B)):
    for _v in _vs: _p.validate(float(_v))
_nn,_dd=calc_nD(_fan_vt,_fan_vb,**_fan_cal)
assert np.allclose(_nn,_fan_ns) and np.max(np.abs(_dd))<1e-10
assert np.max(np.abs(np.diff(1/_fan_B)))<=1/(2*26.3)
assert np.max(np.abs(np.diff(_fan_ns)))<.034522924881

sr1.sensitivity(50e-6)
_fan_expect('sr1 acquisition sensitivity',sr1.sensitivity(),50e-6,sr1.sensitivity()==50e-6)
mc=dict(meas_config)
mc.update({'Si (V)':_si[2],'sample_temperature:':_ts,'gate_calibration':_fan_cal,
           'comments':'hole density-dispersion fan; n=-1.20..-0.95e12 D=0; B=.7138767..6T 66 uniform-invB x 9 n; limited pair resolution; sr1 50uV, 3s dwell; run7 shared-density anchor'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('B_1-B_2; n=-1.20..-0.95e12 cm^-2, D=0 V/nm (run5 cal), Si=0V; B=.713876726..6T, 66 inverse-B rows x 9 paired gate points; fast_delay=3s, slow_delay=1s; base T; no unique pocket count promised')
s.ramp(k_bg.volt,float(_fan_vb[0])); s.ramp(k_tg.volt,float(_fan_vt[0]))
interruptible_sleep(10)
# row: time,B,Vtg,Vbg,Ts,Tv,Itg,Ibg,sr0X,sr0P,sr1X,sr1P
_fan_follow=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P]
for _p in _fan_follow:
    s.fp(_p)
    s.plot('time',_p)
_fan_q={'count':0,'reason':None}
def _fan_guard(station,data):
    _fan_q['count']+=1
    vals=np.asarray(data,dtype=float)
    reason=None
    if not np.all(np.isfinite(vals)): reason='nonfinite readback'
    elif max(abs(vals[6]),abs(vals[7]))>1e-9: reason='existing 1 nA gate-current trip'
    elif not (1.0<=vals[4]<=1.5 and 0<vals[5]<1.6 and abs(vals[4]-vals[5])<.6): reason='base thermometry mismatch'
    elif abs(vals[10])>=.9*50e-6 or abs(vals[8])>=.9*.02: reason='lock-in rail approach'
    elif not 8e-9<vals[8]/-1e6<12e-9: reason='drain-current loss'
    if reason:
        _fan_q['reason']=reason
        print('FAN STOP:',reason,'B/gates',vals[1:4])
        station.interrupt_requested=True
    if _fan_q['count']%90==0 and reason is None:
        for name in ('T_sample','T_vaporizer'):
            assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
s.register_run_after(_fan_guard,())
s.multimegasweep([magnet.field],[_fan_B],[k_tg.volt,k_bg.volt],[_fan_vt,_fan_vb],slow_delay=1.,fast_delay=3.)
# No automatic parking after a stop; read actual state before any next move.
print('FAN END: points',_fan_q['count'],'stop',_fan_q['reason'],'actual B',magnet.field(),'TG/BG',k_tg.volt(),k_bg.volt())
