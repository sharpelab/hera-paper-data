# Read-only preconditions; no validators, limits, or pacing changed.
for _p,_expected in [(k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),(dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),(magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(_p.full_name,'validator expected',_expected,'actual',_actual)
    assert _actual==_expected
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv=T_sample(),T_vaporizer()
_B=magnet.field(); _Si=k_si()
print('Expected base Ts 1-1.5 K, Tv<1.6 K tracking within .6 K; actual',_Ts,_Tv)
assert 1<=_Ts<=1.5 and _Tv<1.6 and abs(_Tv-_Ts)<.6
print('Expected heaters off; actual',heater.sample_range(),heater.vaporizer_range())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
print('Expected PS/output ON; actual',magnet.persistent_switch_on(),magnet.output_enabled())
assert magnet.persistent_switch_on() and magnet.output_enabled()
print('Expected Si=0, RNGE=2, output=1, ramp=.5; actual',_Si,dc205.voltage_range(),dc205.output(),dc205.ramp_rate)
assert abs(_Si)<.01 and dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==.5
print('Expected drive=1 V at13.777Hz, tau=.3s slope24; actual',sr1.amplitude(),sr1.frequency(),sr1.time_constant(),sr1.filter_slope())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<.01
assert sr1.time_constant()==.3 and sr0.time_constant()==.3 and sr1.filter_slope()==24 and sr0.filter_slope()==24
print('Expected gate steps .005 V, NPLC1; actual',k_tg.volt.step,k_bg.volt.step,k_tg.nplci(),k_bg.nplci())
assert k_tg.volt.step==.005 and k_bg.volt.step==.005 and k_tg.nplci()==1 and k_bg.nplci()==1
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('Expected handoff B=0 within .02T, actual',_B)
assert abs(_B)<.02
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB
CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
_vt,_vb=calc_gate_voltages(3.2,0.,**CAL)
assert -.3<=_vt<=1 and -1.3<=_vb<=2
# 227 points: inverse-field step <= .008 /T, >3 points/F_L even at +20% scale.
B_vec=field_invB(.4,1.5,231)
sr1.sensitivity(50e-6)
mc=dict(meas_config); mc['Si (V)']=_Si; mc['sample_temperature:']=_Ts
mc['comments']='Electron onset overlap n=3.2e12 D=0; B .4 to 1.5 T uniform inverse B; sr1 50uV, tau .3s/24dB; magnet settle>=3s; cal run5'
s=sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check'); s.add_comment(mc['comments'])
s.ramp(k_bg.volt,_vb); s.ramp(k_tg.volt,_vt)
interruptible_sleep(3)
assert magnet.settle_s>=3
for _p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P):
    s.fp(_p); s.plot('time',_p)
# time,B,Ts,Tv,Itg,Ibg,Ix,Ip,Vx,Vp
_last_fresh=[0.]
def onset_guard(station,data):
    import time
    assert np.isfinite(np.asarray(data,dtype=float)).all()
    if abs(data[4])>1e-9 or abs(data[5])>1e-9 or not (1<=data[2]<=1.5) or data[3]>=1.6 or abs(data[8])>=.9*50e-6:
        print('ONSET GUARD STOP',data); station.interrupt_requested=True
    if time.monotonic()-_last_fresh[0]>30:
        for _name in ('T_sample','T_vaporizer'):
            assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
        _last_fresh[0]=time.monotonic()
s.register_run_after(onset_guard,())
s.sweep(magnet.field,B_vec,delay=0)
print('Onset overlap ended; actual B,TG,BG',magnet.field(),k_tg.volt(),k_bg.volt())
