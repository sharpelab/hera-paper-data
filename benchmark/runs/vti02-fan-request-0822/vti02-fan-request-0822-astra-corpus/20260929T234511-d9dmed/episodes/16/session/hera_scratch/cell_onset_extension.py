from hera.analysis import field_invB
from sharpelab_nb.gates import calc_gate_voltages
# Read-only preflight: committed safety surfaces must still equal the card.
for p,bounds in [(k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),(dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),(magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
    actual=(p.vals._min_value,p.vals._max_value)
    print(p.full_name,'validator expected',bounds,'actual',actual); assert actual == bounds
assert B_SESSION_CAP == 10 and T_SESSION_CAP == 100
assert_thermometry_live('T_sample',VTI.temp_logfile_candidates['T_sample'],max_age=15,max_period=12)
assert_thermometry_live('T_vaporizer',VTI.temp_logfile_candidates['T_vaporizer'],max_age=15,max_period=12)
Ts,Tv,B0,Si=T_sample(),T_vaporizer(),magnet.field(),k_si()
print('Expected base T=1-1.5 K, vaporizer<1.6, B~0, Si=0; actual',Ts,Tv,B0,Si)
assert 1<=Ts<=1.5 and Tv<1.6 and abs(Ts-Tv)<.6 and abs(B0)<.02 and abs(Si)<.01
print('Heater ranges expected 0/0:',heater.sample_range(),heater.vaporizer_range())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==.5
for li in [sr0,sr1]:
    print(li.name,'tau/slope expected .3/24, actual',li.time_constant(),li.filter_slope())
    assert li.time_constant()==.3 and li.filter_slope()==24
print('Drive expected 1 V,13.777 Hz:',sr1.amplitude(),sr1.frequency())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<.01
assert k_tg.volt.step==.005 and k_bg.volt.step==.005
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert WIRING['sr1+']=='B_1' and WIRING['sr1-']=='B_2'
CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
vt,vb=calc_gate_voltages(3.2,0,**CAL)
k_tg.volt.validate(vt);k_bg.volt.validate(vb)
B_vec=field_invB(.3,2.5,295)
for b in B_vec: magnet.field.validate(b)
sr1.sensitivity(20e-6)  # 2 kohm FS; run 6 below 2.5 T is <65 ohm
mc=dict(meas_config);mc.update({'Si (V)':Si,'sample_temperature:':Ts,'comments':'electron onset extension n=3.2e12 D=0, B .3->2.5 T, uniform 1/B 295 points, 3 s dwell; run-5 calibration'})
s=sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment('onset extension and grid-change: n=+3.2e12 cm^-2 D=0; B .3->2.5 T 295 uniform-1/B points; 20 uV sr1; tau=.3 s slope=24 dwell=3 s; Si=0; cal run5')
s.ramp(k_bg.volt,vb);s.ramp(k_tg.volt,vt)
interruptible_sleep(3)
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr).fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
for p in [T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P]: s.plot(magnet.field,p)
def extension_guard(station,data):
    # time,B,Ts,Tv,Itg,Ibg,sr0X,sr0P,sr1X,sr1P
    if not (1<=data[2]<=1.5 and data[3]<1.6 and abs(data[4])<1e-9 and abs(data[5])<1e-9 and abs(data[8])<.9*20e-6):
        print('STOP: extension temperature/leakage/range guard',data);station.interrupt_requested=True
s.register_run_after(extension_guard,())
s.sweep(magnet.field,B_vec,delay=3.)
print('Extension end actual B,TG,BG:',magnet.field(),k_tg.volt(),k_bg.volt())
