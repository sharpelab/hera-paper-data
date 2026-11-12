# Read-only preconditions; stop before any write on mismatch.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
for _p,_limits in [(k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),(dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),(magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
 _actual=(_p.vals._min_value,_p.vals._max_value)
 print(_p.full_name,'validator expected',_limits,'actual',_actual)
 assert _actual==_limits
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
for _name,_fn in [('T_sample',T_sample),('T_vaporizer',T_vaporizer)]:
 assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_T0,_Tv,_B0,_Si=T_sample(),T_vaporizer(),magnet.field(),k_si()
print('Expected: base 1.0..1.5 K, vaporizer <1.6 K, field near 0 T, Si 0 V. Actual:',_T0,_Tv,_B0,_Si)
assert 1.0<=_T0<=1.5 and .5<_Tv<1.6 and abs(_Tv-_T0)<.6
assert abs(_B0)<.05 and abs(_Si)<.01
print('Expected heaters off, PS/output on:',heater.sample_range(),heater.vaporizer_range(),magnet.persistent_switch_on(),magnet.output_enabled())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
print('Expected DC205 RNGE 2/output 1:',dc205.voltage_range(),dc205.output())
assert dc205.voltage_range()==2 and dc205.output()==1
print('Expected drive 1 V/13.777 Hz, tau .3 s/slope24:',sr1.amplitude(),sr1.frequency(),sr0.time_constant(),sr1.time_constant(),sr0.filter_slope(),sr1.filter_slope())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<.01
assert sr0.time_constant()==.3 and sr1.time_constant()==.3 and sr0.filter_slope()==24 and sr1.filter_slope()==24
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert k_tg.volt.step==.005 and k_bg.volt.step==.005
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
CAL=dict(c_tg=.002796,c_bg=.002161,n_offset=-.0894,D_offset=-.013)
