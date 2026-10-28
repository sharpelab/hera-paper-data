# sdh-spot-check: fine low-field extension, run-6 shared density.
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB
import numpy as np

def _expect(label, actual, ok, expected):
    print(f'{label}: expected {expected}; actual {actual}')
    assert ok, label
for p, limits in [(k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),
                  (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                  (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                  (heater.vaporizer_setpoint,(0.,100.))]:
    actual=(float(p.vals._min_value),float(p.vals._max_value))
    _expect(p.full_name+' validators',actual,actual==limits,limits)
for name in ['T_sample','T_vaporizer']:
    assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
_ts,_tv,_b,_si=T_sample(),T_vaporizer(),magnet.field(),k_si()
_expect('T sample',_ts,1<=_ts<=1.5,'1..1.5 K')
_expect('T vaporizer',_tv,_tv<1.6 and abs(_tv-_ts)<.6,'base, within .6 K of sample')
_expect('field',_b,abs(_b)<.02,'0 +/- .02 T')
_expect('Si',_si,abs(_si)<.01,'0 V')
for name,p in [('sample range',heater.sample_range),('vaporizer range',heater.vaporizer_range)]:
    value=p(); _expect(name,value,value==0,0)
for name,p in [('PS',magnet.persistent_switch_on),('output',magnet.output_enabled)]:
    value=p(); _expect(name,value,bool(value),True)
for lia in [sr0,sr1]:
    tau,slope=lia.time_constant(),lia.filter_slope()
    _expect(lia.name+' filter',(tau,slope),tau==.3 and slope==24,'.3 s / 24 dB')
_expect('magnet settle',magnet.settle_s,magnet.settle_s>=3.,'>=3 s')
_expect('drive',(sr1.amplitude(),sr1.frequency()),abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<.01,'1 V / 13.777 Hz')
for gate in [k_tg,k_bg]:
    _expect(gate.name+' pacing',gate.volt.step,gate.volt.step==.005,'.005 V')
    value=gate.nplci(); _expect(gate.name+' NPLC',value,value==1,1)
CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
_vt,_vb=calc_gate_voltages(3.2,0.,**CAL)
k_tg.volt.validate(float(_vt)); k_bg.volt.validate(float(_vb))
B_vec=field_invB(1.5,.4,222)
assert np.max(np.abs(np.diff(1/B_vec)))<1/(3*1.2*33.09)
sr1.sensitivity(5e-6)
mc=dict(meas_config); mc.update({'Si (V)':_si,'sample_temperature:':_ts,'comments':'fine onset repeat n=3.2e12 D=0; B 1.5 -> 0.4 T uniform inverse B 222; sr1 5uV; run-6 calibration'})
s=sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(mc['comments'])
s.ramp(k_bg.volt,float(_vb)); s.ramp(k_tg.volt,float(_vt))
interruptible_sleep(3)
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr).fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
for p in [T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P]: s.plot('time',p)
# [time,B,Ts,Tv,Itg,Ibg,I_X,I_P,V_X,V_P]
def onset_guard(station,data):
    reasons=[]
    if not np.all(np.isfinite(data)): reasons.append('nonfinite data')
    if max(abs(data[4]),abs(data[5]))>1e-9: reasons.append('gate current >1nA')
    if not 1<=data[2]<=1.5: reasons.append('off base T')
    if abs(data[8])>=.9*5e-6: reasons.append('sr1 near full scale')
    if abs(data[6]/-1e6)<8e-9: reasons.append('drain current lost')
    if reasons:
        print('STOP:',reasons); station.interrupt_requested=True
s.register_run_after(onset_guard,())
s.sweep(magnet.field,B_vec,delay=0)
print('ONSET REPEAT END: actual field',magnet.field(),'gates',k_tg.volt(),k_bg.volt())
