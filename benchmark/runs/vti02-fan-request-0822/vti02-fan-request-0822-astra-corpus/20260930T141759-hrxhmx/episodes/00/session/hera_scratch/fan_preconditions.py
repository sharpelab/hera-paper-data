# Read-only preflight: gate B and state inherited from the handoff.
for _p, _expected in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
 (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
 (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
 _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
 print(_p.full_name,'validator expected',_expected,'actual',_actual)
 assert _actual==_expected
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
for _name,_param in [('T_sample',T_sample),('T_vaporizer',T_vaporizer)]:
 assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv=T_sample(),T_vaporizer()
print('expected base sample 1.0-1.5 K, vaporizer <1.6 K; actual',_Ts,_Tv)
assert 1.0<=_Ts<=1.5 and _Tv<1.6 and abs(_Tv-_Ts)<0.6
_ranges=(heater.sample_range(),heater.vaporizer_range());print('heater ranges expected 0,0 actual',_ranges);assert _ranges==(0,0)
_B=magnet.field();print('B expected near 0 T; actual',_B);assert abs(_B)<0.05
assert magnet.persistent_switch_on() and magnet.output_enabled()
_si=dc205.voltage();print('Si expected 0 V, actual',_si);assert abs(_si)<0.01 and dc205.voltage_range()==2 and dc205.output()==1
assert dc205.ramp_rate==0.5 and k_tg.volt.step==0.005 and k_bg.volt.step==0.005
assert k_tg.nplci()==1 and k_bg.nplci()==1
print('drive expected 1 V,13.777 Hz actual',sr1.amplitude(),sr1.frequency())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<0.01
for _li in [sr0,sr1]:
 print(_li.name,'tau/slope expected .3 s/24, actual',_li.time_constant(),_li.filter_slope())
 assert _li.time_constant()==0.3 and _li.filter_slope()==24
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
