# Read-only preconditions; no safety values are changed.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB
for _p, _expected in [(k_tg.volt,(-.3,1.)), (k_bg.volt,(-1.3,2.)),
                      (dc205.smart_voltage,(-25.,25.)), (dc205.voltage,(-25.,25.)),
                      (magnet.field,(-10.,10.)), (heater.sample_setpoint,(0.,100.)),
                      (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(_p.full_name, 'validator expected',_expected,'actual',_actual)
    assert _actual==_expected
assert B_SESSION_CAP==10. and T_SESSION_CAP==100.
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv=T_sample(),T_vaporizer()
_B=magnet.field(); _Vsi=k_si()
print('Expected base T 1–1.5 K, vaporizer <1.6 K tracking within .6 K, Si 0 V; actual',_Ts,_Tv,_Vsi,'B',_B)
assert 1.0<=_Ts<=1.5 and _Tv<1.6 and abs(_Tv-_Ts)<.6 and abs(_Vsi)<.01
print('Expected heaters off, PS/output on:',heater.sample_range(),heater.vaporizer_range(),magnet.persistent_switch_on(),magnet.output_enabled())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
print('Expected drive 1 V / 13.777 Hz, lock-ins .3 s / 24 dB:',sr1.amplitude(),sr1.frequency(),sr0.time_constant(),sr1.time_constant(),sr0.filter_slope(),sr1.filter_slope())
assert abs(sr1.amplitude()-1.)<1e-6 and abs(sr1.frequency()-13.777)<.01
assert sr0.time_constant()==.3 and sr1.time_constant()==.3
assert sr0.filter_slope()==24 and sr1.filter_slope()==24
assert k_tg.volt.step==.005 and k_bg.volt.step==.005
assert k_tg.nplci()==1. and k_bg.nplci()==1.
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==.5
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'
CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
print('Expected handoff field 0 T; actual',_B)
assert abs(_B)<.05
_vtg,_vbg=calc_gate_voltages(3.2,0.,**CAL)
assert -.3<=_vtg<=1. and -1.3<=_vbg<=2.
B_vec=field_invB(.3,1.5,361)
assert np.max(np.abs(B_vec))<=B_SESSION_CAP
assert magnet.settle_s>=3.
sr1.sensitivity(50e-6)  # restore run-6 range; no acquisition scale change across overlap
mc=dict(meas_config); mc['Si (V)']=_Vsi; mc['sample_temperature:']=_Ts
mc['comments']='SdH onset extension: n=+3.2e12 cm^-2 D=0; calibration run 5; B .3→1.5 T uniform inverse B 361 points; 10 nA; sr1 50 uV; .3 s/24 dB; run-6 overlap'
s=sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check'); s.add_comment(mc['comments'])
s.ramp(k_bg.volt,_vbg); s.ramp(k_tg.volt,_vtg)
interruptible_sleep(10)
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr).fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
for _p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P): s.plot(magnet.field,_p)
# Row [time,B,Ts,Tv,Itg,Ibg,Ix,Ip,Vx,Vp]
def onset_guard(station,data):
    if not np.all(np.isfinite(data)) or not 1.0<=data[2]<=1.5 or data[3]>=1.6 or max(abs(data[4]),abs(data[5]))>1e-9:
        print('STOP: onset acquisition guard',data); station.interrupt_requested=True
s.register_run_after(onset_guard,())
s.sweep(magnet.field,B_vec,delay=0.)
print('END actual B/TG/BG/Si/T:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample())
