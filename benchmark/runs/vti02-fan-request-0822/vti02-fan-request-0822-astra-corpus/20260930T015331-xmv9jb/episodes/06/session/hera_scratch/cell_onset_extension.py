# sdh-spot-check: resolve the censored electron onset before pricing the fan.
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB
import numpy as np
# Preconditions and gate B: read-only until every check passes.
for p, expected in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
                    (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                    (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                    (heater.vaporizer_setpoint,(0.,100.))]:
    actual=(float(p.vals._min_value),float(p.vals._max_value))
    print(p.full_name,'validator expected',expected,'actual',actual)
    assert actual==expected
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
for name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
_Ts,_Tv,_B=T_sample(),T_vaporizer(),magnet.field()
print('Expected base Ts 1-1.5 K, Tv<1.6 K, B~0; actual',_Ts,_Tv,_B)
assert 1<=_Ts<=1.5 and _Tv<1.6 and abs(_Ts-_Tv)<0.6 and abs(_B)<0.05
print('Expected heaters off; actual',heater.sample_range(),heater.vaporizer_range())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
print('Expected Si 0 V, range 2, output 1; actual',k_si(),dc205.voltage_range(),dc205.output())
assert abs(k_si())<0.01 and dc205.voltage_range()==2 and dc205.output()==1
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('Expected drive 1 V / 13.777 Hz, tau .3 s / 24 dB; actual',sr1.amplitude(),sr1.frequency(),sr1.time_constant(),sr1.filter_slope())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<0.01
assert sr0.time_constant()==sr1.time_constant()==0.3 and sr0.filter_slope()==sr1.filter_slope()==24
assert k_tg.volt.step==k_bg.volt.step==0.005 and dc205.ramp_rate==0.5
assert k_tg.nplci()==k_bg.nplci()==1
assert magnet.settle_s>=3
CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-0.0894,D_offset=-0.013)
_vt,_vb=calc_gate_voltages(3.2,0.,**CAL)
k_tg.volt.validate(float(_vt)); k_bg.volt.validate(float(_vb))
B_vec=field_invB(0.3,1.6,340)
for b in B_vec: magnet.field.validate(float(b))
sr1.sensitivity(5e-6)  # 500 Ohm FS; run 6 <=55 Ohm over this window
mc=dict(meas_config); mc.update({'Si (V)':0.,'sample_temperature:':_Ts,
    'comments':'electron onset extension n=3.2e12 D=0 run-5 cal, B=.3..1.6 T uniform 1/B 340 points; sr1 5 uV; settle >=3 s'})
s=sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment('onset extension: n=+3.2e12 cm^-2 D=0; B .3->1.6 T, 340 uniform-in-1/B points, Vsi=0; run-6 shared density, 5 uV FS')
s.ramp(k_bg.volt,float(_vb)); s.ramp(k_tg.volt,float(_vt)); interruptible_sleep(10)
# [time, B, Ts, Tv, Itg, Ibg, X0, P0, X1, P1]
for p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P):
    s.fp(p); s.plot('time',p)
def onset_guard(station,data):
    a=np.asarray(data,dtype=float)
    if (not np.all(np.isfinite(a)) or not 1<=a[2]<=1.5 or a[3]>=1.6
        or max(abs(a[4]),abs(a[5]))>1e-9 or abs(a[8])>0.9*5e-6):
        print('ONSET CHECK STOP',a); station.interrupt_requested=True
s.register_run_after(onset_guard,())
result_onset=s.sweep(magnet.field,B_vec,delay=0)
print('ONSET EXTENSION END',result_onset.id,'interrupted',result_onset.metadata.get('interrupted'))
print('Actual B/gates',magnet.field(),k_tg.volt(),k_bg.volt())
