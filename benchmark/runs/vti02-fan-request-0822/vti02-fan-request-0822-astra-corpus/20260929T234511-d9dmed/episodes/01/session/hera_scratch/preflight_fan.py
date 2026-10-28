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
