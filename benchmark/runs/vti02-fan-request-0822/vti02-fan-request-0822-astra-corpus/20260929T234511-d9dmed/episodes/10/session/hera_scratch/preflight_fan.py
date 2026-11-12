# Read-only preflight: compare current state and committed validators to the card.
for _p, _bounds in ((k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
 (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
 (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))):
 _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
 print(_p.full_name,'expected',_bounds,'actual',_actual)
 assert _actual==_bounds
assert B_SESSION_CAP==10. and T_SESSION_CAP==100.
for _name in ('T_sample','T_vaporizer'):
 assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_T0,_Tv0,_B0=T_sample(),T_vaporizer(),magnet.field()
print('Expected base T 1.0-1.5 K, vaporizer <1.6 K within 0.6 K; actual',_T0,_Tv0)
assert 1.0<=_T0<=1.5 and _Tv0<1.6 and abs(_Tv0-_T0)<.6
_ranges=(heater.sample_range(),heater.vaporizer_range())
print('Heater ranges expected (0,0), actual',_ranges); assert _ranges==(0,0)
_ps=(magnet.persistent_switch_on(),magnet.output_enabled())
print('PS/output expected (True,True), actual',_ps); assert all(_ps)
print('Field measured',_B0,'T; gates',k_tg.volt(),k_bg.volt())
_si=(dc205.voltage_range(),dc205.output(),k_si(),dc205.ramp_rate)
print('Si expected (2,1,0 V,0.5 V/s), actual',_si)
assert _si[:2]==(2,1) and abs(_si[2])<.01 and abs(_si[3]-.5)<1e-9
print('Drive expected 1 V,13.777 Hz; actual',sr1.amplitude(),sr1.frequency())
assert abs(sr1.amplitude()-1.)<1e-6 and abs(sr1.frequency()-13.777)<.01
for _li in (sr0,sr1):
 print(_li.name,'tau/slope expected 0.3s/24dB, actual',_li.time_constant(),_li.filter_slope())
 assert _li.time_constant()==.3 and _li.filter_slope()==24
print('Gate pacing expected 5mV; actual',k_tg.volt.step,k_bg.volt.step)
assert k_tg.volt.step==.005 and k_bg.volt.step==.005
print('NPLC expected 1/1; actual',k_tg.nplci(),k_bg.nplci())
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
