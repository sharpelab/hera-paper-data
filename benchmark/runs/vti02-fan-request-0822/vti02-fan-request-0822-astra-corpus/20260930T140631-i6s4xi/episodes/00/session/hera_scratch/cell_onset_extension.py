# Read-only preconditions before any instrument write.
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_Ts,_Tv,_B,_Si = T_sample(),T_vaporizer(),magnet.field(),k_si()
print('Expected base T 1.0..1.5 K, vaporizer <1.6 K, B=0 +/-0.02 T, Si=0; actual:',_Ts,_Tv,_B,_Si)
assert 1.0<=_Ts<=1.5 and _Tv<1.6 and abs(_B)<0.02 and abs(_Si)<0.01
print('Expected heaters off, magnet output/PS on:',heater.sample_range(),heater.vaporizer_range(),magnet.output_enabled(),magnet.persistent_switch_on())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.output_enabled() and magnet.persistent_switch_on()
for _p,_limits in [(k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),(dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),(magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value)); print(_p.full_name,'expected',_limits,'actual',_actual); assert _actual==_limits
print('Expected drive 1 V / 13.777 Hz; tau .3 s / slope 24; NPLC 1:',sr1.amplitude(),sr1.frequency(),sr0.time_constant(),sr1.time_constant(),sr0.filter_slope(),sr1.filter_slope(),k_tg.nplci(),k_bg.nplci())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<.01
assert sr0.time_constant()==.3 and sr1.time_constant()==.3 and sr0.filter_slope()==24 and sr1.filter_slope()==24
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert k_tg.volt.step==.005 and k_bg.volt.step==.005
CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
_vt,_vb=calc_gate_voltages(3.2,0.,**CAL)
B_vec=field_invB(.35,2.,283)
for _p,_v in [(k_tg.volt,_vt),(k_bg.volt,_vb)]: _p.validate(float(_v))
for _b in B_vec: magnet.field.validate(float(_b))
assert np.max(np.abs(np.diff(1/B_vec)))<=1/(3*1.2*33.086)
assert magnet.settle_s>=3
sr1.sensitivity(50e-6)
mc=dict(meas_config); mc.update({'comments':'onset extension; n_A=+3.2e12 D_A=0; B .35->2 T, 283 uniform-1/B points; run-6 anchor; 50 uV; 3 s magnet settle','Si (V)':_Si,'sample_temperature:':_Ts})
s=sweep.AsyncStation(mc); s.add_comment('sdh-spot-check'); s.add_comment(mc['comments'])
s.ramp(k_bg.volt,float(_vb)); s.ramp(k_tg.volt,float(_vt)); interruptible_sleep(10)
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr).fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
for _p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P): s.plot(magnet.field,_p)
# time,B,Ts,Tv,Itg,Ibg,Ix,Ip,Vx,Vp
_check_time=[0.]
def _extension_guard(station,data):
    if abs(float(data[4]))>1e-9 or abs(float(data[5]))>1e-9 or not 1.0<=float(data[2])<=1.5 or float(data[3])>=1.6:
        print('STOP: leakage/temperature',data); station.interrupt_requested=True
    if abs(float(data[8]))>=.9*50e-6 or abs(float(data[6]))>=.9*sr0.sensitivity():
        print('STOP: headroom'); station.interrupt_requested=True
    if _time.monotonic()-_check_time[0]>60:
        for _name in ('T_sample','T_vaporizer'): assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
        _check_time[0]=_time.monotonic()
s.register_run_after(_extension_guard,())
s.sweep(magnet.field,B_vec,delay=0)
print('Extension endpoint B,TG,BG:',magnet.field(),k_tg.volt(),k_bg.volt())
